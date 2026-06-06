"""Render a branded video with Remotion, driven by the niche's style_props.

Copies the voiceover (and optional B-roll) into remotion/public/ so the
templates can load them via staticFile, writes a props file, and invokes the
Remotion CLI. Falls back is handled by the caller (gen_cron).
"""
from __future__ import annotations
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import REMOTION_DIR

FPS = 30


def _public_dir() -> Path:
    p = Path(REMOTION_DIR) / "public"
    p.mkdir(parents=True, exist_ok=True)
    return p


def render(niche: dict, title: str, hook: str, script_lines: list[str],
           audio_path: Path, out_path: Path, duration_seconds: float,
           portrait: bool, bg_video: Path | None = None,
           bg_images: list[Path] | None = None,
           words: list[dict] | None = None) -> Path:
    pub = _public_dir()
    audio_name = f"{out_path.stem}.mp3"
    shutil.copy(audio_path, pub / audio_name)

    bg_name = None
    if bg_video:
        bg_name = f"{out_path.stem}_bg{Path(bg_video).suffix}"
        shutil.copy(bg_video, pub / bg_name)

    bg_image_names = []
    for i, img in enumerate(bg_images or []):
        name = f"{out_path.stem}_img{i}{Path(img).suffix}"
        shutil.copy(img, pub / name)
        bg_image_names.append(name)

    style = niche.get("style_props") or {}
    props = {
        "template": niche.get("remotion_template", "GenericTemplate"),
        "style": {
            "bg": style.get("bg", "#0a1f3c"),
            "accent": style.get("accent", "#d4af37"),
            "font": style.get("font", "Georgia"),
            "mood": style.get("mood", "calm"),
        },
        "title": title,
        "hook": hook,
        "scriptLines": script_lines,
        "audioSrc": audio_name,
        "bgVideo": bg_name,
        "bgImages": bg_image_names or None,
        "words": words or None,
        "durationInFrames": max(int(duration_seconds * FPS), FPS * 3),
    }

    composition = "NicheVideoPortrait" if portrait else "NicheVideoLandscape"
    out_path = Path(out_path).resolve()
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(props, f)
        props_file = f.name

    subprocess.run(
        ["npx", "remotion", "render", composition, str(out_path),
         f"--props={props_file}"],
        cwd=str(REMOTION_DIR), check=True,
    )
    return out_path
