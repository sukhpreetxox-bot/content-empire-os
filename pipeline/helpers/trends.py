"""Topic selection driven by real YouTube search demand (free, keyless).

Uses Google/YouTube autocomplete (ds=yt) — what people actually type into the
YouTube search bar — to turn a niche seed into a high-intent, long-tail topic.
Falls back to the niche's own topic pool if the request fails.
"""
from __future__ import annotations
import random
import requests

SUGGEST = "https://suggestqueries.google.com/complete/search"


def youtube_suggestions(seed: str) -> list[str]:
    try:
        r = requests.get(SUGGEST, params={"client": "firefox", "ds": "yt", "q": seed},
                         timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        return [s for s in data[1] if isinstance(s, str)]
    except Exception as e:  # noqa: BLE001
        print(f"[trends] suggest failed ({e})")
        return []


def pick_topic(niche: dict) -> str:
    """A trending, high-intent topic for this niche (else a pool topic)."""
    pool = niche.get("topics") or [niche.get("category", "an idea")]
    seed = random.choice(pool)
    sugg = youtube_suggestions(seed)
    # prefer multi-word, specific suggestions (long-tail = less competition)
    cands = [s for s in sugg if len(s.split()) >= 2 and s.lower() != seed.lower()]
    return random.choice(cands) if cands else seed
