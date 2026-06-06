"""AI scene images via Pollinations (free).

Primary visual source: a unique AI image per script beat, styled per niche
(niches.image_style). Avoids Content-ID risk entirely (every frame is new).

Auth: a free token from enter.pollinations.ai (POLLINATIONS_TOKEN) gives the
reliable "seed" tier (~1 req/5s). Without it the keyless tier is heavily
throttled/gated, so the caller falls back to Pexels.
"""
from __future__ import annotations
import time
import urllib.parse
from pathlib import Path
import requests

from config import POLLINATIONS_TOKEN, POLLINATIONS_MODEL

BASE = "https://image.pollinations.ai/prompt/"
_last_call = [0.0]
_MIN_GAP = 5.5 if POLLINATIONS_TOKEN else 16.0  # seconds between requests


def available() -> bool:
    return bool(POLLINATIONS_TOKEN)  # reliable only with a (free) token


def _throttle():
    wait = _MIN_GAP - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def generate_image(prompt: str, out_path: Path, width: int, height: int,
                   seed: int = 0, retries: int = 2) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = BASE + urllib.parse.quote(prompt)
    params = {"width": width, "height": height, "nologo": "true",
              "model": POLLINATIONS_MODEL, "seed": seed, "safe": "true"}
    headers = {"Authorization": f"Bearer {POLLINATIONS_TOKEN}"} if POLLINATIONS_TOKEN else {}
    for attempt in range(retries + 1):
        _throttle()
        r = requests.get(url, params=params, headers=headers, timeout=150)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            out_path.write_bytes(r.content)
            return out_path
        if r.status_code in (402, 429) and attempt < retries:
            time.sleep(_MIN_GAP)  # rate-limited; back off and retry
            continue
        raise RuntimeError(f"pollinations {r.status_code}: {r.text[:120]}")
    raise RuntimeError("pollinations: exhausted retries")


VIDEO_BASE = "https://video.pollinations.ai/prompt/"


def generate_video(prompt: str, out_path: Path, model: str = "seedance",
                   seconds: int = 5) -> Path:
    """Short AI video clip (hero shot for Shorts). Experimental; needs a free
    POLLINATIONS_TOKEN. Caller should fall back to image+Ken Burns on failure."""
    if not POLLINATIONS_TOKEN:
        raise RuntimeError("video needs a free POLLINATIONS_TOKEN")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    url = VIDEO_BASE + urllib.parse.quote(prompt)
    _throttle()
    r = requests.get(url, params={"model": model, "seconds": seconds},
                     headers={"Authorization": f"Bearer {POLLINATIONS_TOKEN}"},
                     timeout=300)
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("video"):
        out_path.write_bytes(r.content)
        return out_path
    raise RuntimeError(f"pollinations video {r.status_code}: {r.text[:120]}")


def generate_scene_images(prompts: list[str], dest_dir: Path, niche_style: str,
                          width: int, height: int) -> list[Path]:
    """One image per prompt (script beat), styled for the niche. Best-effort:
    returns whatever succeeded (may be empty → caller falls back to Pexels)."""
    out: list[Path] = []
    for i, p in enumerate(prompts):
        full = f"{p}. Style: {niche_style}"
        try:
            out.append(generate_image(
                full, Path(dest_dir) / f"scene_{i}.jpg", width, height, seed=1000 + i))
        except Exception as e:  # noqa: BLE001
            print(f"[pollinations] scene {i} failed ({e})")
            break  # stop early on failure (likely rate/gate) — use what we have
    return out
