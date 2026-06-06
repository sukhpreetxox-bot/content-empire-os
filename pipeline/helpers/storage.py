"""Supabase Storage helpers.

On GitHub Actions the runner that renders a video is NOT the runner that later
publishes it (ephemeral). So we persist rendered media to a public Storage
bucket and store the URL on the content row. publish_cron downloads from there.
This also gives Instagram the public HTTPS URL it requires, and lets the
dashboard show real previews.
"""
from __future__ import annotations
from pathlib import Path
import mimetypes
import requests

from helpers.db import db

BUCKET = "media"


def upload(local_path: Path, dest_path: str) -> str:
    """Upload a local file to the bucket and return its public URL."""
    local_path = Path(local_path)
    content_type = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
    with open(local_path, "rb") as f:
        db().storage.from_(BUCKET).upload(
            dest_path, f,
            {"content-type": content_type, "upsert": "true"},
        )
    return public_url(dest_path)


def public_url(dest_path: str) -> str:
    return db().storage.from_(BUCKET).get_public_url(dest_path)


def download(url: str, out_path: Path) -> Path:
    """Download a (public) URL to a local file."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)
    return out_path
