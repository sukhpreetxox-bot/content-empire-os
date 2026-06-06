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
from helpers import remotion as remotion_helper

# Output language for scripts/titles. Niche tones are written in Dutch, which
# made the model drift between languages — pin it here. Switch to "Dutch" (or
# any language) in one place if you target a Dutch-speaking audience.
SCRIPT_LANGUAGE = "English"

SCRIPT_SYS = (
    "You are a faceless-channel scriptwriter. You write tight, original short-form "
    "narration with a clear, specific point of view. You never produce generic "
    "fact-recaps. Output strictly the requested JSON."
)


def build_prompt(niche: dict) -> str:
    topic = random.choice(niche.get("topics") or ["an interesting idea in this niche"])
    return (
        f"Channel: {niche['display_name']} ({niche['category']}).\n"
        f"Tone: {niche['tone']}. Audience: {niche.get('audience','general')}.\n"
        f"Topic to cover: {topic}.\n\n"
        f"Write the title AND script entirely in {SCRIPT_LANGUAGE}.\n"
        "Write a 60-90 second narration script. REQUIRED: at least 170 words "
        "(scripts under 120 words are auto-rejected, so aim for 170-220). It "
        "must carry a UNIQUE angle, analysis, or transformation — not a bare "
        "list of facts.\n"
        'Return JSON: {"title": "...", "hook": "<3s opening line>", '
        '"angle": "<the unique POV in one sentence>", "script": "<full narration, 170+ words>"}'
    )


def _caption_lines(script: str, max_lines: int = 7) -> list[str]:
    """Split narration into short caption lines for the on-screen subtitles."""
    import re
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    return parts[:max_lines] or [script[:120]]


def render_video(niche: dict, title: str, hook: str, script: str,
                 audio: Path, slug: str) -> tuple[Path, Path, list[dict]]:
    """Branded Remotion render (preferred) with an FFmpeg B-roll fallback."""
    portrait = niche["platform"] == "instagram"
    orientation = "portrait" if portrait else "landscape"
    video_path = VIDEO_DIR / f"{slug}.mp4"
    duration = ffmpeg.probe_duration(audio)

    # Optional B-roll behind the branded template (and for the fallback).
    query = random.choice(niche.get("topics") or [niche["category"]])
    try:
        clips, credits = pexels.fetch_broll(
            query, BROLL_DIR / slug, count=3, orientation=orientation)
    except Exception as e:  # noqa: BLE001 — B-roll is optional
        print(f"[gen] no B-roll ({e}); rendering on solid background")
        clips, credits = [], []

    try:
        remotion_helper.render(
            niche, title, hook, _caption_lines(script), audio, video_path,
            duration_seconds=duration, portrait=portrait,
            bg_video=clips[0] if clips else None)
    except Exception as e:  # noqa: BLE001 — fall back to plain FFmpeg assembly
        print(f"[gen] Remotion render failed ({e}); FFmpeg fallback")
        if not clips:
            raise
        w, h = (1080, 1920) if portrait else (1920, 1080)
        ffmpeg.concat_broll(clips, audio, video_path, width=w, height=h)

    thumb_path = THUMB_DIR / f"{slug}.jpg"
    ffmpeg.thumbnail(video_path, thumb_path, at_seconds=1.0)
    return video_path, thumb_path, credits


def generate_for_channel(channel: dict) -> None:
    niche = channel["niches"]
    handle = channel["handle"]
    print(f"[gen] {handle} ({niche['slug']}) ...")

    # 1. idea + script
    draft = llm.generate_json(build_prompt(niche), system=SCRIPT_SYS)
    row = db.create_content(
        channel["id"], status="script",
        title=draft.get("title"), hook=draft.get("hook"),
        topic=draft.get("title"), editorial_angle=draft.get("angle"),
        script=draft.get("script"),
    )
    cid = row["id"]
    slug = f"{niche['slug']}_{cid[:8]}"

    # 2. editorial-value gate
    result = editorial.check(niche, draft)
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
    if track:
        try:
            final_audio = audio.mix_with_music(
                final_audio, track, VOICE_DIR / f"{slug}_mixed.mp3")
        except Exception as e:  # noqa: BLE001 — music is optional
            print(f"[gen] music mix failed ({e}); voice-only")
    db.update_content(cid, status="voice", voiceover_path=str(final_audio))

    # 4. video + thumbnail
    video, thumb, credits = render_video(
        niche, draft.get("title") or niche["display_name"],
        draft.get("hook") or "", result.script, final_audio, slug)

    # 4b. persist media to Supabase Storage so a later (ephemeral) publish
    #     runner can fetch it; also gives IG its required public URL.
    meta: dict = {}
    try:
        meta["public_video_url"] = storage.upload(video, f"{slug}/video.mp4")
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
    args = ap.parse_args()

    channels = db.get_active_channels(args.platform)
    print(f"[gen] {len(channels)} active channel(s)")
    for ch in channels:
        try:
            generate_for_channel(ch)
        except Exception:  # noqa: BLE001 — one channel failing must not stop the rest
            print(f"[gen] ERROR on {ch.get('handle')}:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
