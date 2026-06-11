"""Cloudflare Workers AI — free, reliable FLUX.1-schnell image generation.

10,000 neurons/day free, runs from any IP (no shared-IP throttling like the
keyless Pollinations tier). Outputs ~1024x1024; we cover-crop in Remotion.

Setup (free): dash.cloudflare.com → note your Account ID, create an API token
with the "Workers AI" permission → set CF_ACCOUNT_ID / CF_API_TOKEN.
"""
from __future__ import annotations
import base64
from pathlib import Path
import requests

from config import CF_ACCOUNT_ID, CF_API_TOKEN

MODEL = "@cf/black-forest-labs/flux-1-schnell"


def available() -> bool:
    return bool(CF_ACCOUNT_ID and CF_API_TOKEN)


def generate_image(prompt: str, out_path: Path, steps: int = 6) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{MODEL}"
    r = requests.post(
        url, headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
        json={"prompt": prompt[:2000], "steps": max(1, min(steps, 8))}, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"cloudflare {r.status_code}: {r.text[:120]}")
    data = r.json()
    img_b64 = (data.get("result") or {}).get("image")
    if not img_b64:
        raise RuntimeError(f"cloudflare: no image in response {str(data)[:120]}")
    out_path.write_bytes(base64.b64decode(img_b64))
    return out_path
