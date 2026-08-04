#!/usr/bin/env python3
"""Generation cron — one run produces (at most) one piece per active channel.

idea -> script (Groq) -> EDITORIAL GATE -> edge-tts -> video+thumbnail
     -> row written with status 'review' (waits for human approval).

Run per channel or for all:  python gen_cron.py [--platform youtube|instagram]
"""
from __future__ import annotations
import argparse
import random
import sys
import traceback
from pathlib import Path

# allow `python gen_cron.py` from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import VOICE_DIR, VIDEO_DIR, THUMB_DIR, BROLL_DIR
from helpers import db, llm, editorial, tts, pexels, ffmpeg, storage, audio
from helpers import transcribe, trends, images as ai_images
from helpers import remotion as remotion_helper

# Output language for scripts/titles. Niche tones are written in Dutch, which
# made the model drift between languages — pin it here. Switch to "Dutch" (or
# any language) in one place if you target a Dutch-speaking audience.
SCRIPT_LANGUAGE = "English"

SCRIPT_SYS = (
    "You are a faceless-channel scriptwriter. You write tight, original narration "
    "with a clear, specific point of view. You favour a counterintuitive, precise, "
    "almost philosophical insight over generic advice — every script should make "
    "the viewer feel they finally understood something they couldn't put into "
    "words. No clichés, no listicles, no 'in today's world'. "
    "Address the viewer directly ('you'), and CLOSE with one sincere, sharp "
    "question that genuinely invites a reply in the comments — never 'like and "
    "subscribe', a real question tied to the idea that makes them want to answer. "
    "Output strictly the requested JSON."
)


def build_prompt(niche: dict, fmt: str = "long", topic: str | None = None) -> str:
    topic = topic or random.choice(
        niche.get("topics") or ["an interesting idea in this niche"])
    base = (
        f"Channel: {niche['display_name']} ({niche['category']}).\n"
        f"Tone: {niche['tone']}. Audience: {niche.get('audience','general')}.\n"
        f"Topic to cover: {topic}.\n\n"
        "PERSONA: You are Quiet Capital — a sharp, calm, unmistakably opinionated "
        "voice on inner development (attention, character, consciousness, sovereignty). "
        "You are NOT a neutral narrator. You take a clear stance, name the "
        "uncomfortable truth, and challenge the viewer's assumptions directly. "
        "Confident, never hedging ('maybe', 'some people think', 'it could be'). "
        "Contrarian where the mainstream is lazy, but always precise and earned — "
        "never a cheap hot-take or fake-guru bait. Address the viewer as 'you'. "
        "Signature register: quiet conviction, not loud hype.\n\n"
        "TITLE — this is the product; it decides whether anyone clicks. Write it "
        "in the PROVEN patterns of this channel's top performers:\n"
        "  • Concrete + second-person + visceral: 'Your Unread Messages Are "
        "Attacking Your Nervous System'\n"
        "  • Contrarian reframe: 'Your Avoidance Isn't Inaction. It's Control.'\n"
        "  • Unexpected pairing: 'The Invisible Labor of Stillness', "
        "'Motivation Is a Wake, Not an Engine'\n"
        "Address 'you' or name a specific, felt tension. BANNED title styles "
        "(these flopped): academic explainers like 'Unpacking Seneca's Timeless "
        "Wisdom', '<Philosopher> on <Topic>', or any 'The Power of <abstract noun>' "
        "cliché. Curiosity or a bold claim over a neutral description, always.\n\n"
        f"Write the title AND script entirely in {SCRIPT_LANGUAGE}.\n"
    )
    if fmt == "short":
        return base + (
            "Write a high-retention YOUTUBE SHORT: 18-28 seconds, ~60-80 words "
            "(shorter holds retention — do not pad; 50-60% of viewers quit in "
            "the first 3 seconds). ONE single sharp idea.\n"
            "HOOK (first line) — spoken in under 2.5s, it decides everything. "
            "Use ONE of these proven formulas, present tense, active verb:\n"
            "  1. PATTERN INTERRUPT — a contradiction that breaks autopilot: "
            "'Motivation doesn't start anything.'\n"
            "  2. DIRECT PROMISE — one concrete payoff up front: 'In 20 seconds, "
            "why your attention isn't yours.'\n"
            "  3. QUESTION — name a specific felt struggle: 'Why does your best "
            "thinking vanish the second you grab your phone?'\n"
            "It must be a COMPLETE, finished thought that flips a common belief — "
            "never a vague tease.\n"
            "  WORKS (retention 100-185%): 'Motivation doesn't start anything.' · "
            "'What if doing nothing is your most vital work?' · "
            "'What you avoid owns you.'\n"
            "  FAILS (retention 0-14%): vague curiosity with no substance "
            "('One strange discipline the titans mastered'), or abstract meta "
            "('Thinking for yourself isn't about thinking'). NEVER write these.\n"
            "BODY — a great hook dies if the body drifts. Every sentence must "
            "ADVANCE with a concrete, specific image or turn — never restate the "
            "hook in abstract terms, never generalise. Build to one felt payoff.\n"
            "The LAST line must LOOP cleanly back into the first so a rewatch "
            "feels seamless (this is how Shorts pass 100% retention).\n"
            'Return JSON: {"title": "<=55 chars, curiosity-driven", '
            '"hook": "<=8 words, a complete counter-intuitive claim", '
            '"angle": "<unique POV>", "script": "<60-80 words, concrete, loopable>"}'
        )
    if fmt == "deep":
        return base + (
            "Write a DEEP long-form narration script: 9-12 minutes, "
            "1900-2400 words (this MUST exceed 8 minutes so YouTube places "
            "mid-roll ads — do not stop early). This is a flagship revenue video.\n"
            "Structure: a gripping cold-open hook; then 3-4 distinct movements "
            "that each deepen the idea from a new angle (use a recognisable "
            "philosophical anchor — e.g. a Stoic like Marcus Aurelius/Seneca/"
            "Epictetus, or a timeless principle — reframed through this niche); "
            "concrete imagery and one or two short stories/analogies; a slow, "
            "resonant close that lands the transformation. Calm, authoritative, "
            "almost meditative. No filler, no listicle padding, no clichés.\n"
            'Return JSON: {"title": "<=70 chars, evergreen-searchable", '
            '"hook": "<one-sentence cold open>", "angle": "<the through-line>", '
            '"script": "<full 1300-1700 word narration>"}'
        )
    return base + (
        "Write a 60-90 second narration script. REQUIRED: at least 170 words "
        "(aim for 170-220). It must carry a UNIQUE angle, analysis, or "
        "transformation — not a bare list of facts.\n"
        'Return JSON: {"title": "...", "hook": "<3s opening line>", '
        '"angle": "<the unique POV in one sentence>", "script": "<full narration, 170+ words>"}'
    )


def _caption_lines(script: str, max_lines: int = 7) -> list[str]:
    """Split narration into short caption lines for the on-screen subtitles."""
    import re
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    return parts[:max_lines] or [script[:120]]


def _scene_prompts(script: str, n: int) -> list[str]:
    """n visual anchors (sentences) spread across the script, for AI scenes."""
    import re
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not sents:
        return [script[:120]]
    if len(sents) <= n:
        return sents
    step = len(sents) / n
    return [sents[min(int(i * step), len(sents) - 1)] for i in range(n)]


def render_video(niche: dict, title: str, hook: str, script: str,
                 audio: Path, slug: str, portrait: bool = False
                 ) -> tuple[Path, Path, list[dict]]:
    """Render: AI scene images (primary) → Pexels b-roll (fallback), with
    Whisper word-accurate captions; FFmpeg assembly as last resort."""
    orientation = "portrait" if portrait else "landscape"
    w, h = (1080, 1920) if portrait else (1920, 1080)
    video_path = VIDEO_DIR / f"{slug}.mp4"
    duration = ffmpeg.probe_duration(audio)
    lines = _caption_lines(script)
    credits: list[dict] = []

    # 1. PRIMARY visuals: AI images spread across the video. Shorts need a
    #    visual reset every ~3-4s (best-practice for retention — a slow ~8s
    #    hold bleeds viewers); long/deep pace ~1 per 55s. Capped to protect the
    #    free Cloudflare daily quota. Cloudflare → Pollinations.
    if duration <= 40:  # Short: fast cadence, one scene ~every 3.5s
        n_scenes = max(5, min(8, round(duration / 3.5)))
    else:               # long/deep: calmer pacing
        n_scenes = max(3, min(10, round(duration / 55)))
    scene_prompts = _scene_prompts(script, n_scenes)
    bg_images: list[Path] = []
    try:
        bg_images = ai_images.scene_images(
            scene_prompts, BROLL_DIR / slug, niche.get("image_style") or niche["category"],
            width=w, height=h)
        if bg_images:
            credits = [{"source": "AI (Cloudflare Workers AI / Pollinations FLUX)"}]
    except Exception as e:  # noqa: BLE001
        print(f"[gen] AI images failed ({e})")

    # 2. FALLBACK visuals: Pexels b-roll if no AI images.
    clips: list[Path] = []
    if not bg_images:
        try:
            query = random.choice(niche.get("topics") or [niche["category"]])
            clips, credits = pexels.fetch_broll(
                query, BROLL_DIR / slug, count=3, orientation=orientation)
        except Exception as e:  # noqa: BLE001
            print(f"[gen] no B-roll ({e}); solid background")

    # 3. Whisper word-level timings for frame-accurate karaoke captions.
    words = transcribe.word_timestamps(audio)

    try:
        remotion_helper.render(
            niche, title, hook, lines, audio, video_path,
            duration_seconds=duration, portrait=portrait,
            bg_video=clips[0] if clips else None,
            bg_images=bg_images or None, words=words or None)
    except Exception as e:  # noqa: BLE001 — last-resort FFmpeg assembly
        print(f"[gen] Remotion render failed ({e}); FFmpeg fallback")
        if not clips:
            raise
        ffmpeg.concat_broll(clips, audio, video_path, width=w, height=h)

    # Thumbnail: deliberate on-brand Remotion still (packaging = product);
    # random-frame grab only as a last-resort fallback.
    thumb_path = THUMB_DIR / f"{slug}.jpg"
    try:
        remotion_helper.render_thumbnail(
            niche, title, thumb_path,
            bg_image=bg_images[0] if bg_images else None)
    except Exception as e:  # noqa: BLE001
        print(f"[gen] branded thumbnail failed ({e}); frame-grab fallback")
        ffmpeg.thumbnail(video_path, thumb_path, at_seconds=1.0)
    return video_path, thumb_path, credits


def generate_for_channel(channel: dict, fmt: str = "long",
                         topic: str | None = None) -> None:
    niche = channel["niches"]
    handle = channel["handle"]
    print(f"[gen] {handle} ({niche['slug']}) [{fmt}] ...")
    portrait = fmt == "short" or niche["platform"] == "instagram"

    # 1. topic: explicit override → your inbox idea → real search demand
    if topic:
        print(f"[gen] topic (given): {topic}")
    else:
        idea = db.pop_idea(channel["id"])
        if idea:
            topic = idea["text"]
            print(f"[gen] using your idea: {topic}")
        else:
            topic = trends.pick_topic(niche)
            print(f"[gen] topic (trends): {topic}")
    base_prompt = build_prompt(niche, fmt, topic)
    draft = llm.generate_json(base_prompt, system=SCRIPT_SYS)
    row = db.create_content(
        channel["id"], status="script", format=fmt,
        title=draft.get("title"), hook=draft.get("hook"),
        topic=draft.get("title"), editorial_angle=draft.get("angle"),
        script=draft.get("script"),
    )
    cid = row["id"]
    slug = f"{niche['slug']}_{fmt}_{cid[:8]}"

    # 2. editorial-value gate (length bar by format), with ONE corrective retry.
    #    A single bad LLM roll must not cost the whole day's video: feed the
    #    rejection reason back and regenerate before giving up.
    min_words = {"short": 55, "deep": 1500}.get(fmt, 120)
    result = editorial.check(niche, draft, min_words=min_words, fmt=fmt)
    if not result.passed:
        print(f"[gen] {handle} gate rejected attempt 1 ({result.notes}) — retrying")
        retry_prompt = (
            f"{base_prompt}\n\n"
            f"YOUR PREVIOUS ATTEMPT WAS REJECTED: {result.notes}\n"
            f"Fix exactly that. Hard requirements: the script must be at least "
            f"{min_words} words, and 'angle' must state a specific, substantive "
            "point of view — not a vague restatement of the topic."
        )
        draft2 = llm.generate_json(retry_prompt, system=SCRIPT_SYS)
        result2 = editorial.check(niche, draft2, min_words=min_words, fmt=fmt)
        if not result2.passed:
            db.update_content(
                cid, status="rejected", editorial_passed=False,
                editorial_notes=f"attempt1: {result.notes} || attempt2: {result2.notes}",
                reject_reason="editorial gate (2 attempts)")
            print(f"[gen] {handle} BLOCKED after retry: {result2.notes}")
            return
        draft, result = draft2, result2
        db.update_content(cid, title=draft.get("title"), hook=draft.get("hook"),
                          topic=draft.get("title"),
                          editorial_angle=draft.get("angle"))
        print(f"[gen] {handle} retry passed the gate")
    db.update_content(cid, script=result.script, editorial_passed=True,
                      editorial_notes=result.notes)

    # 3. voiceover (Kokoro) → master → optional background music
    raw_voice = tts.synthesize_for_niche(result.script, VOICE_DIR / f"{slug}_raw.mp3", niche)
    final_audio = audio.master(raw_voice, VOICE_DIR / f"{slug}.mp3")
    mood = (niche.get("style_props") or {}).get("mood", "calm")
    track = audio.pick_music(mood)
    music_credit = None
    if track:
        try:
            final_audio = audio.mix_with_music(
                final_audio, track, VOICE_DIR / f"{slug}_mixed.mp3")
            music_credit = audio.MUSIC_CREDIT
        except Exception as e:  # noqa: BLE001 — music is optional
            print(f"[gen] music mix failed ({e}); voice-only")
    db.update_content(cid, status="voice", voiceover_path=str(final_audio))

    # 4. video + thumbnail
    video, thumb, credits = render_video(
        niche, draft.get("title") or niche["display_name"],
        draft.get("hook") or "", result.script, final_audio, slug, portrait=portrait)

    # 4b. persist media to Supabase Storage so a later (ephemeral) publish
    #     runner can fetch it; also gives IG its required public URL.
    meta: dict = {}
    if music_credit:
        meta["music_credit"] = music_credit
    # Stay under Supabase free-tier 50MB/object: shrink if needed before upload.
    upload_src = video
    if video.stat().st_size > 48 * 1024 * 1024:
        upload_src = ffmpeg.shrink(video, VIDEO_DIR / f"{slug}_web.mp4")
    try:
        meta["public_video_url"] = storage.upload(upload_src, f"{slug}/video.mp4")
        meta["thumbnail_url"] = storage.upload(thumb, f"{slug}/thumb.jpg")
    except Exception as e:  # noqa: BLE001 — local runs can still work off disk
        print(f"[gen] storage upload failed ({e}); keeping local paths only")

    db.update_content(cid, status="video", video_path=str(video),
                      thumbnail_path=str(thumb), broll_credits=credits, meta=meta)

    # 5. AUTONOMOUS MODE: the editorial gate already vetted quality, so approve
    #    straight away — the publish cron will pick it up (respects the daily
    #    upload cap). Flip back to status="review" to reinstate a human gate.
    db.update_content(cid, status="approved", scheduled_for=None)
    print(f"[gen] {handle} -> approved (auto)  ({result.notes})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=["youtube", "instagram"])
    # 'long' (60-90s) retired: too long for Shorts reach, too short for
    # watch-time/mid-roll revenue. Funnel = Shorts (reach) + deep (revenue).
    ap.add_argument("--format", choices=["short", "deep"], default="short")
    args = ap.parse_args()

    channels = db.get_active_channels(args.platform)
    print(f"[gen] {len(channels)} active channel(s) — format={args.format}")
    for ch in channels:
        try:
            generate_for_channel(ch, fmt=args.format)
        except Exception:  # noqa: BLE001 — one channel failing must not stop the rest
            print(f"[gen] ERROR on {ch.get('handle')}:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
