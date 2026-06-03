"""Instagram Graph API publish (Reels), Business/Creator accounts only.

Two-step flow:
  1. POST /{ig_user_id}/media        -> creates a media container (async)
  2. POST /{ig_user_id}/media_publish -> publishes the container

The video must be reachable at a public HTTPS URL (Graph fetches it). On the
VM, serve the rendered MP4 from a temporary public URL, or upload to Supabase
Storage and pass its public URL.

Token: per-account long-lived token at secrets/instagram/<token_ref>.txt
Supports the AI-content label via the (optional) Graph field where available.
"""
from __future__ import annotations
import time
from pathlib import Path
import requests

from config import IG_GRAPH_VERSION, IG_TOKEN_DIR

BASE = "https://graph.facebook.com"


def _token(token_ref: str) -> str:
    p = Path(IG_TOKEN_DIR) / f"{token_ref}.txt"
    if not p.exists():
        raise RuntimeError(f"IG token not found: {p}")
    return p.read_text().strip()


def _g(path: str) -> str:
    return f"{BASE}/{IG_GRAPH_VERSION}/{path}"


def publish_reel(channel: dict, video_url: str, caption: str,
                 ai_generated: bool = True, poll_seconds: int = 5,
                 max_polls: int = 24) -> str:
    """Publish a Reel. Returns the published media id."""
    ig_user_id = channel.get("ig_user_id")
    token_ref = channel.get("ig_token_ref")
    if not ig_user_id or not token_ref:
        raise RuntimeError(f"channel {channel['handle']} missing ig_user_id/ig_token_ref")
    token = _token(token_ref)

    # 1. create container
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption[:2200],
        "access_token": token,
    }
    if ai_generated:
        # Meta's AI-content labelling field (name varies by API version /
        # account eligibility; ignored gracefully if unsupported).
        params["ai_info"] = "AI_GENERATED"
    r = requests.post(_g(f"{ig_user_id}/media"), data=params, timeout=60)
    r.raise_for_status()
    container_id = r.json()["id"]

    # 2. wait for the container to finish processing
    for _ in range(max_polls):
        s = requests.get(
            _g(container_id),
            params={"fields": "status_code", "access_token": token}, timeout=30,
        ).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"IG container processing error: {s}")
        time.sleep(poll_seconds)

    # 3. publish
    pub = requests.post(
        _g(f"{ig_user_id}/media_publish"),
        data={"creation_id": container_id, "access_token": token}, timeout=60,
    )
    pub.raise_for_status()
    return pub.json()["id"]
