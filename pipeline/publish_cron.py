#!/usr/bin/env python3
"""Publication cron — uploads APPROVED, due content; then schedules the next.

Only ever touches rows with status='approved' and scheduled_for due. Respects
per-platform daily caps and throttles between uploads.
"""
from __future__ import annotations
import re
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    YT_MAX_UPLOADS_PER_DAY, IG_MAX_POSTS_PER_DAY, UPLOAD_THROTTLE_SECONDS,
    VIDEO_DIR, PUBLISH_PRIVACY,
)
from helpers import db, youtube, instagram, storage


def _local_video(content: dict) -> Path:
    """Return a local video path: use the on-disk file if present (same-runner
    case), else download it from Supabase Storage (ephemeral-runner case)."""
    vp = content.get("video_path")
    if vp and Path(vp).exists():
        return Path(vp)
    url = (content.get("meta") or {}).get("public_video_url")
    if not url:
        raise RuntimeError("no local video and no meta.public_video_url to fetch")
    dest = VIDEO_DIR / f"{content['id']}.mp4"
    return storage.download(url, dest)


_STOPWORDS = {
    "the", "and", "for", "not", "but", "this", "that", "its", "are", "was",
    "with", "from", "how", "why", "what", "when", "who", "one", "just", "only",
    "more", "less", "than", "then", "your", "you", "his", "her", "them", "they",
    "isn", "it's", "isn't", "doesn", "does", "been", "being", "into", "about",
    "make", "makes", "made", "will", "would", "could", "should", "every",
}


def _keywords(content: dict, limit: int = 6) -> list[str]:
    """Per-video keywords taken from its OWN title/angle.

    Reusing the same niche topic list on every upload makes all videos look
    identical to the algorithm; per-video terms are a far better signal.
    """
    text = f"{content.get('title') or ''} {content.get('editorial_angle') or ''}"
    out: list[str] = []
    for raw in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", text.lower()):
        w = raw.strip("'-")
        if len(w) < 4 or w in _STOPWORDS or w in out:
            continue
        out.append(w)
        if len(out) >= limit:
            break
    return out


def _hashtags(content: dict) -> str:
    tags = [f"#{w.capitalize()}" for w in _keywords(content, 3)]
    if content.get("format") == "short":
        tags.insert(0, "#Shorts")
    return " ".join(tags)


def _description(content: dict, niche: dict) -> str:
    parts = [content.get("hook") or "", "", content.get("editorial_angle") or ""]
    hashtags = _hashtags(content)
    if hashtags:
        parts += ["", hashtags]
    for d in (niche.get("required_disclaimers") or []):
        parts += ["", d]
    credit = (content.get("meta") or {}).get("music_credit")
    if credit:
        parts += ["", credit]
    return "\n".join(p for p in parts if p is not None).strip()


def _next_slot(channel_id: str) -> datetime:
    """Plan the next occurrence from the channel's repeating schedule."""
    sched = db.get_schedule(channel_id)
    # Minimal cron handling: default to +1 day at the same time.
    base = datetime.now(timezone.utc) + timedelta(days=1)
    if sched and sched.get("cron_expr"):
        try:
            _m, h, *_ = sched["cron_expr"].split()
            base = base.replace(hour=int(h), minute=0, second=0, microsecond=0)
        except Exception:  # noqa: BLE001
            pass
    return base


def publish_one(content: dict) -> None:
    channel = content["channels"]
    niche = channel["niches"]
    platform = channel["platform"]
    cid = content["id"]

    if db.count_published_today(channel["id"]) >= (
        YT_MAX_UPLOADS_PER_DAY if platform == "youtube" else IG_MAX_POSTS_PER_DAY
    ):
        print(f"[pub] {channel['handle']} daily cap reached, skipping")
        return

    db.update_content(cid, status="publishing")
    title = content.get("title") or niche["display_name"]
    desc = _description(content, niche)

    if platform == "youtube":
        vid = youtube.upload(
            channel, _local_video(content), title=title, description=desc,
            tags=(_keywords(content, 8) + (niche.get("topics") or []))[:12],
            synthetic=content.get("synthetic_disclosure", True),
            privacy=PUBLISH_PRIVACY,
        )
        url = f"https://youtube.com/watch?v={vid}"
    else:
        # IG needs a public HTTPS URL; meta.public_video_url is set by the
        # generation step when the asset is uploaded to Supabase Storage.
        public_url = content.get("meta", {}).get("public_video_url")
        if not public_url:
            raise RuntimeError("no public_video_url in content.meta for IG upload")
        caption = f"{content.get('hook','')}\n\n{desc}"
        mid = instagram.publish_reel(
            channel, public_url, caption,
            ai_generated=content.get("synthetic_disclosure", True))
        url = f"https://instagram.com/reel/{mid}"

    db.update_content(
        cid, status="published", published_url=url,
        published_at=datetime.now(timezone.utc).isoformat(),
    )
    print(f"[pub] {channel['handle']} -> {url}")

    # schedule the next piece for this channel (repeating calendar)
    nxt = _next_slot(channel["id"])
    print(f"[pub] next {channel['handle']} slot: {nxt.isoformat()}")


def main() -> None:
    due = db.get_publishable()
    print(f"[pub] {len(due)} approved & due")
    for i, content in enumerate(due):
        try:
            publish_one(content)
        except Exception:  # noqa: BLE001
            db.update_content(content["id"], status="failed",
                              error_message=traceback.format_exc()[-1000:])
            print(f"[pub] ERROR on {content['id']}:\n{traceback.format_exc()}")
        if i < len(due) - 1:
            time.sleep(UPLOAD_THROTTLE_SECONDS)


if __name__ == "__main__":
    main()
