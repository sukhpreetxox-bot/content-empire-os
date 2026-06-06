"""Word-level timestamps of the voiceover (faster-whisper, free, local/CPU).

Feeds frame-accurate karaoke captions in Remotion. Falls back to an empty list
(the captions then use even line distribution) if anything fails.
"""
from __future__ import annotations
from pathlib import Path

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return _model


def word_timestamps(audio_path: Path) -> list[dict]:
    """Return [{word, start, end}] in seconds. Empty on failure."""
    try:
        model = _get_model()
        segments, _info = model.transcribe(str(audio_path), word_timestamps=True)
        words: list[dict] = []
        for seg in segments:
            for w in (seg.words or []):
                token = (w.word or "").strip()
                if token:
                    words.append({"word": token,
                                  "start": round(float(w.start), 3),
                                  "end": round(float(w.end), 3)})
        return words
    except Exception as e:  # noqa: BLE001
        print(f"[transcribe] whisper failed ({e}); using estimated caption timing")
        return []
