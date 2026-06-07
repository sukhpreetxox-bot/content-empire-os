"""Audio post-production (free, via ffmpeg).

- master(): EBU R128 loudness normalisation + gentle compression so the voice
  sounds broadcast-level instead of raw TTS.
- pick_music(): choose a royalty-free track for the niche mood from
  assets/music/<mood>/ (you drop CC0 tracks there once; see assets/music/README).
- mix_with_music(): duck background music under the voice and mix.
"""
from __future__ import annotations
import random
import subprocess
from pathlib import Path

from config import ASSETS_DIR

MUSIC_DIR = ASSETS_DIR / "music"
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

# Background tracks are Kevin MacLeod / incompetech.com (CC BY 4.0). When a track
# is used, this credit is appended to the video description at publish time.
MUSIC_CREDIT = "Music: Kevin MacLeod (incompetech.com) — licensed under CC BY 4.0"


def _run(args: list[str]) -> None:
    subprocess.run(args, check=True, capture_output=True)


def master(in_path: Path, out_path: Path) -> Path:
    """Loudness-normalise to ~-16 LUFS with light compression (spoken word)."""
    out_path = Path(out_path)
    _run([
        "ffmpeg", "-y", "-i", str(in_path),
        "-af", "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,"
               "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-codec:a", "libmp3lame", "-q:a", "2", str(out_path),
    ])
    return out_path


def pick_music(mood: str) -> Path | None:
    folder = MUSIC_DIR / mood
    if not folder.exists():
        folder = MUSIC_DIR  # fall back to a flat library
    tracks = [p for p in folder.glob("*") if p.suffix.lower() in AUDIO_EXTS]
    return random.choice(tracks) if tracks else None


def mix_with_music(voice: Path, music: Path, out_path: Path,
                   music_gain_db: float = -19.0) -> Path:
    """Duck the music under the voice; trim to the voice length."""
    out_path = Path(out_path)
    _run([
        "ffmpeg", "-y", "-i", str(voice), "-i", str(music),
        "-filter_complex",
        f"[1:a]volume={music_gain_db}dB,aloop=loop=-1:size=2e9[bg];"
        "[bg][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=300[ducked];"
        "[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=0[mix]",
        "-map", "[mix]", "-codec:a", "libmp3lame", "-q:a", "2", str(out_path),
    ])
    return out_path
