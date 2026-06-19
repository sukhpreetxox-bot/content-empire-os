#!/usr/bin/env python3
"""Analytics cron — pull real per-video stats, fill the dashboard, steer content.

- Reads the channel's videos (YouTube Data API) → views/likes/comments.
- Upserts a daily snapshot per matching content row (dashboard Analytics page).
- Logs the top performers.
- Auto-steer: seeds ONE idea echoing the best video's angle so the channel
  leans into what works (skipped if already seeded today).
- Keeps the Supabase free-tier project awake.

Watch-time / retention need the YouTube Analytics API enabled in the GCP
project; this runs fine without it (views/likes/comments are real-time).
"""
from __future__ import annotations
import sys
import re
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import YOUTUBE_OAUTH_DIR
from helpers import db


def _video_id(url: str) -> str | None:
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", url or "")
    return m.group(1) if m else None


def _channel_stats(token_ref: str) -> dict[str, dict]:
    """video_id -> {views, likes, comments, title} for the whole channel."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(
        str(Path(YOUTUBE_OAUTH_DIR) / f"{token_ref}.json"))
    yt = build("youtube", "v3", credentials=creds)
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=up,
                                    maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    out: dict[str, dict] = {}
    for j in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,statistics",
                                  id=",".join(ids[j:j + 50])).execute()["items"]:
            s = v["statistics"]
            out[v["id"]] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
                "title": v["snippet"]["title"],
            }
    return out


def collect() -> None:
    today = date.today().isoformat()
    channels = db.get_active_channels("youtube")
    for ch in channels:
        ref = ch.get("oauth_token_ref")
        if not ref:
            continue
        try:
            stats = _channel_stats(ref)
        except Exception as e:  # noqa: BLE001
            print(f"[analytics] {ch['handle']} stats failed: {e}")
            continue

        published = db.get_published_content(ch["id"])
        ranked = []
        for c in published:
            vid = _video_id(c.get("published_url") or "")
            s = stats.get(vid) if vid else None
            if not s:
                continue
            db.upsert_analytics({
                "content_id": c["id"], "channel_id": ch["id"],
                "snapshot_date": today, "views": s["views"],
                "likes": s["likes"], "comments": s["comments"],
            })
            ranked.append((s["views"], s["title"], c))

        ranked.sort(reverse=True)
        print(f"[analytics] {ch['handle']}: {len(ranked)} videos tracked")
        for v, t, _ in ranked[:5]:
            print(f"   {v:>5} views  {t[:50]}")

        # auto-steer: echo the top performer into the idea inbox (once/day)
        if ranked and ranked[0][0] >= 5:
            top_title, top_c = ranked[0][1], ranked[0][2]
            already = (db.db().table("ideas").select("id")
                       .eq("status", "new").ilike("text", f"%{top_title[:24]}%")
                       .execute().data)
            if not already:
                db.create_idea(
                    f"Make another angle in the vein of the winner '{top_title}' "
                    f"(it is pulling the most views) — go deeper on that theme.",
                    ch["id"])
                print(f"   ↳ seeded a winner-echo idea from: {top_title[:40]}")


def main() -> None:
    try:
        collect()
    finally:
        db.touch_keepalive()
        print("[analytics] keep-alive done")


if __name__ == "__main__":
    main()
