"""FFmpeg assembly helpers (ffmpeg is a system binary on the VM).

Two paths are supported:
  - Remotion renders the final MP4 (preferred; see remotion/). FFmpeg is then
    only used for muxing the edge-tts audio and grabbing a thumbnail frame.
  - Fallback: concatenate B-roll + audio directly with FFmpeg when no Remotion
    template applies (e.g. quick Instagram clips).
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path


def _run(args: list[str]) -> None:
    subprocess.run(args, check=True, capture_output=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def mux_audio(video: Path, audio: Path, out: Path) -> Path:
    """Replace/attach audio track, trimming video to the audio length."""
    out = Path(out)
    _run([
        "ffmpeg", "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        str(out),
    ])
    return out


def concat_broll(clips: list[Path], audio: Path, out: Path,
                 width: int = 1080, height: int = 1920) -> Path:
    """Loop/concat B-roll to cover the audio duration, scale to target, mux."""
    out = Path(out)
    dur = probe_duration(audio)
    # Build a concat list that repeats clips until we exceed audio duration.
    listfile = out.with_suffix(".txt")
    total, lines = 0.0, []
    i = 0
    while total < dur and clips:
        clip = clips[i % len(clips)]
        lines.append(f"file '{Path(clip).resolve()}'")
        total += probe_duration(clip)
        i += 1
    listfile.write_text("\n".join(lines))
    _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
        "-i", str(audio),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,"
               f"crop={width}:{height},fps=30",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", "-shortest",
        str(out),
    ])
    listfile.unlink(missing_ok=True)
    return out


def thumbnail(video: Path, out: Path, at_seconds: float = 1.0) -> Path:
    """Grab a single frame as the thumbnail (Remotion @still is preferred)."""
    out = Path(out)
    _run([
        "ffmpeg", "-y", "-ss", str(at_seconds), "-i", str(video),
        "-frames:v", "1", "-q:v", "2", str(out),
    ])
    return out
