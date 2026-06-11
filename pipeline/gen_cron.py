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
    "words. No clichés, no listicles, no 'in today's world'. Output strictly the "
    "requested JSON."
)


def build_prompt(niche: dict, fmt: str = "long", topic: str | None = None) -> str:
    topic = topic or random.choice(
        niche.get("topics") or ["an interesting idea in this niche"])
    base = (
        f"Channel: {niche['display_name']} ({niche['category']}).\n"
        f"Tone: {niche['tone']}. Audience: {niche.get('audience','general')}.\n"
        f"Topic to cover: {topic}.\n\n"
        f"Write the title AND script entirely in {SCRIPT_LANGUAGE}.\n"
    )
    if fmt == "short":
        return base + (
            "Write a YOUTUBE SHORT script: 30-50 seconds, ~90-120 words. ONE "
            "single sharp idea. Open with a curiosity-gap HOOK in the first "
            "sentence that makes someone STOP scrolling. Punchy, fast, "
            "conversational; end on a loop or a one-line takeaway. Must carry a "
            "unique angle, not a bare fact.\n"
            'Return JSON: {"title": "<=60 chars, curiosity-driven", '
            '"hook": "<=8 words, the first line", "angle": "<unique POV>", '
            '"script": "<90-120 words>"}'
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

    # 1. PRIMARY visuals: one unique AI image per script beat (per-niche style).
    #    Cloudflare Workers AI → Pollinations → (Pexels fallback below).
    bg_images: list[Path] = []
    try:
        bg_images = ai_images.scene_images(
            lines, BROLL_DIR / slug, niche.get("image_style") or niche["category"],
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

    thumb_path = THUMB_DIR / f"{slug}.jpg"
    ffmpeg.thumbnail(video_path, thumb_path, at_seconds=1.0)
    return video_path, thumb_path, credits


def generate_for_channel(channel: dict, fmt: str = "long") -> None:
    niche = channel["niches"]
    handle = channel["handle"]
    print(f"[gen] {handle} ({niche['slug']}) [{fmt}] ...")
    portrait = fmt == "short" or niche["platform"] == "instagram"

    # 1. idea + script — prefer YOUR submitted idea, else real search demand
    idea = db.pop_idea(channel["id"])
    if idea:
        topic = idea["text"]
        print(f"[gen] using your idea: {topic}")
    else:
        topic = trends.pick_topic(niche)
        print(f"[gen] topic (trends): {topic}")
    draft = llm.generate_json(build_prompt(niche, fmt, topic), system=SCRIPT_SYS)
    row = db.create_content(
        channel["id"], status="script", format=fmt,
        title=draft.get("title"), hook=draft.get("hook"),
        topic=draft.get("title"), editorial_angle=draft.get("angle"),
        script=draft.get("script"),
    )
    cid = row["id"]
    slug = f"{niche['slug']}_{fmt}_{cid[:8]}"

    # 2. editorial-value gate (lower length bar for Shorts)
    result = editorial.check(niche, draft, min_words=70 if fmt == "short" else 120)
    if not result.passed:
        db.update_content(cid, status="rejected", editorial_passed=False,
                          editorial_notes=result.notes, reject_reason="editorial gate")
        print(f"[gen] {handle} BLOCKED by editorial gate: {result.notes}")
        return
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

    # 5. ready for human review
    db.update_content(cid, status="review")
    print(f"[gen] {handle} -> review  ({result.notes})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=["youtube", "instagram"])
    ap.add_argument("--format", choices=["long", "short"], default="long")
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
