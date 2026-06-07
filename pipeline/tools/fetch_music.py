#!/usr/bin/env python3
"""Download royalty-free background music into assets/music/<mood>/.

Source: Kevin MacLeod / incompetech.com (CC BY 4.0) — stable direct MP3 URLs.
Attribution is added automatically to the video description at publish time
(see pipeline/helpers/audio.MUSIC_CREDIT). 404s are skipped silently.

Run once locally, and in CI (cached). Usage: python pipeline/tools/fetch_music.py
"""
from __future__ import annotations
import sys
import urllib.parse
from pathlib import Path
import requests

BASE = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
ROOT = Path(__file__).resolve().parents[2]
MUSIC = ROOT / "assets" / "music"

# mood -> track titles (exact incompetech filenames, minus .mp3)
TRACKS = {
    "calm":      ["Deliberate Thought", "Healing", "Wholesome"],
    "energetic": ["Inspired", "Industrial Music Box", "Itty Bitty 8 Bit"],
    "neutral":   ["Long Note Two", "Thinking Music", "Carefree"],
    "eerie":     ["Anguish", "Ghostpocalypse - 6 Crossing the Threshold", "Long Note Three"],
    "moody":     ["Bittersweet", "Heartbreaking", "Sad Trio"],
    "clinical":  ["Thinking Music", "Wholesome"],
    "bold":      ["Crypto", "Stringed Disco", "Hep Cats"],
    "intimate":  ["Tender Remembrance", "Bittersweet"],
}


def fetch(title: str, dest: Path) -> bool:
    url = BASE + urllib.parse.quote(title + ".mp3")
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and r.content[:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3"):
            dest.write_bytes(r.content)
            return True
        print(f"  skip {title} ({r.status_code})")
    except Exception as e:  # noqa: BLE001
        print(f"  err {title} ({e})")
    return False


def main() -> None:
    total = 0
    for mood, titles in TRACKS.items():
        folder = MUSIC / mood
        folder.mkdir(parents=True, exist_ok=True)
        for t in titles:
            dest = folder / (t.replace(" ", "_") + ".mp3")
            if dest.exists():
                total += 1
                continue
            if fetch(t, dest):
                print(f"  + {mood}/{dest.name}")
                total += 1
    print(f"music ready: {total} tracks across {len(TRACKS)} moods")
    if total == 0:
        sys.exit("no tracks downloaded")


if __name__ == "__main__":
    main()
