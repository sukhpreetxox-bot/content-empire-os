"""Voiceover via edge-tts (free Microsoft neural voices).

Each niche supplies its own voice / rate / pitch (from the niches table).
"""
from __future__ import annotations
import asyncio
from pathlib import Path
import edge_tts


async def _synth(text: str, voice: str, rate: str, pitch: str, out: Path) -> None:
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(out))


def synthesize(text: str, out_path: Path, voice: str = "en-US-GuyNeural",
               rate: str = "+0%", pitch: str = "+0Hz") -> Path:
    """Render `text` to an MP3 at out_path. Returns the path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_synth(text, voice, rate, pitch, out_path))
    return out_path


def synthesize_for_niche(text: str, out_path: Path, niche: dict) -> Path:
    return synthesize(
        text, out_path,
        voice=niche.get("tts_voice", "en-US-GuyNeural"),
        rate=niche.get("tts_rate", "+0%"),
        pitch=niche.get("tts_pitch", "+0Hz"),
    )
