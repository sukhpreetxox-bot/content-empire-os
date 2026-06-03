#!/usr/bin/env python3
"""Analytics cron (daily) — pull stats per published item, upsert snapshots.

Also performs a cheap keep-alive write so the Supabase free-tier project does
not pause after 7 days of inactivity.

Stats sources:
  YouTube : Data API videos.list (views/likes/comments). Retention/CTR/RPM
            require the YouTube Analytics (reporting) API + revenue scope; left
            as best-effort hooks so the schema is ready when those are wired.
  Instagram: Graph API media insights (reach/likes/comments/shares).
"""
from __future__ import annotations
import sys
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from config import IG_GRAPH_VERSION
from helpers import db
from helpers.instagram import _token, _g  # reuse token + graph url helpers


def _yt_stats(channel: dict, video_id: str) -> dict:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from config import YOUTUBE_OAUTH_DIR
    token_path = Path(YOUTUBE_OAUTH_DIR) / f"{channel['oauth_token_ref']}.json"
    creds = Credentials.from_authorized_user_file(str(token_path))
    yt = build("youtube", "v3", credentials=creds)
    r = yt.videos().list(part="statistics", id=video_id).execute()
    s = (r.get("items") or [{}])[0].get("statistics", {})
    return {
        "views": int(s.get("viewCount", 0)),
        "likes": int(s.get("likeCount", 0)),
        "comments": int(s.get("commentCount", 0)),
        "raw": s,
    }


def _ig_stats(channel: dict, media_id: str) -> dict:
    token = _token(channel["ig_token_ref"])
    r = requests.get(
        _g(f"{media_id}/insights"),
        params={"metric": "reach,likes,comments,shares", "access_token": token},
        timeout=30,
    ).json()
    vals = {d["name"]: d["values"][0]["value"] for d in r.get("data", [])}
    return {
        "views": vals.get("reach", 0),
        "likes": vals.get("likes", 0),
        "comments": vals.get("comments", 0),
        "shares": vals.get("shares", 0),
        "raw": r,
    }


def _media_id_from_url(url: str) -> str:
    return url.rstrip("/").split("/")[-1].split("=")[-1]


def collect() -> None:
    today = date.today().isoformat()
    rows = db.get_published_content()
    print(f"[analytics] {len(rows)} published items")
    for c in rows:
        try:
            channel = db.get_active_channels()  # noqa: F841 (kept simple)
            ch = db.db().table("channels").select("*").eq("id", c["channel_id"]) \
                .limit(1).execute().data[0]
            url = c.get("published_url") or ""
            if ch["platform"] == "youtube":
                stats = _yt_stats(ch, _media_id_from_url(url))
            else:
                stats = _ig_stats(ch, _media_id_from_url(url))
            db.upsert_analytics({
                "content_id": c["id"], "channel_id": c["channel_id"],
                "snapshot_date": today, **stats,
            })
        except Exception:  # noqa: BLE001
            print(f"[analytics] skip {c['id']}: {traceback.format_exc(limit=1)}")


def main() -> None:
    try:
        collect()
    finally:
        db.touch_keepalive()  # keep Supabase awake regardless
        print("[analytics] keep-alive write done")


if __name__ == "__main__":
    main()
