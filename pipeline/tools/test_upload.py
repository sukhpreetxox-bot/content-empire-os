#!/usr/bin/env python3
"""One-off: generate a fresh Quiet Capital video and upload it UNLISTED.

Proves the end-to-end YouTube upload works with the stored token, without
publishing publicly. Run from repo root with the venv python.
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pipeline/

from helpers import db, youtube
import gen_cron


def main() -> None:
    channels = db.get_active_channels("youtube")
    qc = next((c for c in channels if c["handle"] == "Quiet Capital"), None)
    if not qc:
        sys.exit("Quiet Capital channel not found")

    # Generate until one piece passes the editorial gate (max 3 tries).
    for attempt in range(1, 4):
        print(f"[test] generation attempt {attempt} ...", flush=True)
        gen_cron.generate_for_channel(qc)
        rows = (
            db.db().table("content").select("*")
            .eq("channel_id", qc["id"]).eq("status", "review")
            .order("created_at", desc=True).limit(1).execute().data
        )
        if rows and rows[0].get("video_path"):
            content = rows[0]
            break
    else:
        sys.exit("No piece passed the gate after 3 attempts")

    niche = qc["niches"]
    title = content.get("title") or "Quiet Capital"
    desc_parts = [content.get("hook") or "", "", content.get("editorial_angle") or ""]
    for d in (niche.get("required_disclaimers") or []):
        desc_parts += ["", d]
    description = "\n".join(p for p in desc_parts if p is not None).strip()

    print(f"[test] uploading UNLISTED: {title}", flush=True)
    video_id = youtube.upload(
        qc, Path(content["video_path"]), title=title, description=description,
        tags=(niche.get("topics") or [])[:10], synthetic=True,
        privacy="unlisted",
    )
    url = f"https://youtube.com/watch?v={video_id}"

    db.update_content(
        content["id"], status="published", published_url=url,
        published_at=datetime.now(timezone.utc).isoformat(),
        meta={**(content.get("meta") or {}), "test_upload": True, "privacy": "unlisted"},
    )
    print(f"\n✅ UPLOADED (unlisted): {url}", flush=True)


if __name__ == "__main__":
    main()
