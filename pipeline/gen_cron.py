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
from helpers import db, llm, editorial, tts, pexels, ffmpeg

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
        "Write a 45-75 second narration script (~130-180 words) with a UNIQUE "
        "angle, analysis, or transformation — not a bare list of facts.\n"
        'Return JSON: {"title": "...", "hook": "<3s opening line>", '
        '"angle": "<the unique POV in one sentence>", "script": "<full narration>"}'
    )


def render_video(niche: dict, audio: Path, slug: str) -> tuple[Path, Path, list[dict]]:
    """Fetch B-roll, assemble video + thumbnail.

    Remotion (Layer 2) is preferred for branded templates; until a template is
    wired we use the FFmpeg fallback so the pipeline is runnable end-to-end.
    """
    orientation = "portrait" if niche["platform"] == "instagram" else "landscape"
    query = random.choice(niche.get("topics") or [niche["category"]])
    clips, credits = pexels.fetch_broll(
        query, BROLL_DIR / slug, count=3, orientation=orientation)
    video_path = VIDEO_DIR / f"{slug}.mp4"
    if orientation == "portrait":
        ffmpeg.concat_broll(clips, audio, video_path, width=1080, height=1920)
    else:
        ffmpeg.concat_broll(clips, audio, video_path, width=1920, height=1080)
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

    # 3. voiceover
    audio = tts.synthesize_for_niche(result.script, VOICE_DIR / f"{slug}.mp3", niche)
    db.update_content(cid, status="voice", voiceover_path=str(audio))

    # 4. video + thumbnail
    video, thumb, credits = render_video(niche, audio, slug)
    db.update_content(cid, status="video", video_path=str(video),
                      thumbnail_path=str(thumb), broll_credits=credits)

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
