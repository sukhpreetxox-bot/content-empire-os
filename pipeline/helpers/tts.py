"""Voiceover.

Primary: Kokoro (kokoro-onnx) — high-quality, free, Apache-2.0, per-niche voice
from the niches table (kokoro_voice / kokoro_speed). Falls back to edge-tts when
the Kokoro model files aren't present (e.g. a minimal local run).
"""
from __future__ import annotations
import asyncio
import subprocess
import tempfile
from pathlib import Path

import edge_tts

from config import KOKORO_MODEL, KOKORO_VOICES

_kokoro = None


def _get_kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    return _kokoro


def _lang_for(voice: str) -> str:
    # bm_/bf_ = British; everything else American.
    return "en-gb" if voice[:1] == "b" else "en-us"


def _to_mp3(wav_path: Path, mp3_path: Path) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
         "-q:a", "2", str(mp3_path)],
        check=True, capture_output=True,
    )
    return mp3_path


def _kokoro_synth(text: str, out_path: Path, voice: str, speed: float) -> Path:
    import soundfile as sf
    k = _get_kokoro()
    samples, sr = k.create(text, voice=voice, speed=speed, lang=_lang_for(voice))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, samples, sr)
        return _to_mp3(Path(tmp.name), out_path)


# --- edge-tts fallback ------------------------------------------------------
async def _edge(text: str, voice: str, rate: str, pitch: str, out: Path) -> None:
    await edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch).save(str(out))


def synthesize(text: str, out_path: Path, voice: str = "en-US-GuyNeural",
               rate: str = "+0%", pitch: str = "+0Hz") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_edge(text, voice, rate, pitch, out_path))
    return out_path


def synthesize_for_niche(text: str, out_path: Path, niche: dict) -> Path:
    """Kokoro with the niche's voice; edge-tts fallback if Kokoro unavailable."""
    voice = niche.get("kokoro_voice")
    if voice and KOKORO_MODEL.exists() and KOKORO_VOICES.exists():
        try:
            return _kokoro_synth(
                text, out_path, voice, float(niche.get("kokoro_speed") or 1.0))
        except Exception as e:  # noqa: BLE001 — degrade gracefully
            print(f"[tts] Kokoro failed ({e}); falling back to edge-tts")
    return synthesize(
        text, out_path,
        voice=niche.get("tts_voice", "en-US-GuyNeural"),
        rate=niche.get("tts_rate", "+0%"),
        pitch=niche.get("tts_pitch", "+0Hz"),
    )
