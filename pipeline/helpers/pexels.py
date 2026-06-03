"""Royalty-free B-roll from the Pexels API (free).

Using only Pexels (or freshly generated AI assets) avoids Content ID strikes.
Returns clips plus attribution credits to store on the content row.
"""
from __future__ import annotations
from pathlib import Path
import requests

from config import PEXELS_API_KEY

API = "https://api.pexels.com/videos/search"


def search_videos(query: str, per_page: int = 5, orientation: str = "portrait") -> list[dict]:
    """Return a list of {url, download, photographer, credit_url, duration}."""
    if not PEXELS_API_KEY or PEXELS_API_KEY.startswith("YOUR_"):
        raise RuntimeError("PEXELS_API_KEY not set in .env")
    r = requests.get(
        API,
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": per_page, "orientation": orientation},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for v in r.json().get("videos", []):
        # pick the highest-res mp4 file under ~1080p
        files = sorted(
            [f for f in v["video_files"] if f.get("file_type") == "video/mp4"],
            key=lambda f: (f.get("height") or 0),
        )
        if not files:
            continue
        best = next((f for f in files if (f.get("height") or 0) <= 1920), files[-1])
        out.append({
            "url": v["url"],
            "download": best["link"],
            "photographer": v.get("user", {}).get("name", "Pexels"),
            "credit_url": v.get("user", {}).get("url", "https://pexels.com"),
            "duration": v.get("duration", 0),
        })
    return out


def download(url: str, out_path: Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)
    return out_path


def fetch_broll(query: str, dest_dir: Path, count: int = 3,
                orientation: str = "portrait") -> tuple[list[Path], list[dict]]:
    """Download up to `count` clips. Returns (paths, credits)."""
    clips = search_videos(query, per_page=count, orientation=orientation)
    paths, credits = [], []
    for i, c in enumerate(clips):
        p = download(c["download"], Path(dest_dir) / f"broll_{i}.mp4")
        paths.append(p)
        credits.append({"source": "Pexels", "by": c["photographer"], "url": c["url"]})
    return paths, credits
