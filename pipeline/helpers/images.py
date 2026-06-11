"""AI scene-image orchestrator: Cloudflare (reliable) → Pollinations (fallback).

Returns one image per script beat, styled per niche. Empty list → caller uses
Pexels b-roll.
"""
from __future__ import annotations
from pathlib import Path

from helpers import cloudflare, pollinations


def scene_images(prompts: list[str], dest_dir: Path, niche_style: str,
                 width: int, height: int) -> list[Path]:
    dest_dir = Path(dest_dir)
    # 1. Cloudflare Workers AI (free FLUX, reliable from any IP)
    if cloudflare.available():
        out: list[Path] = []
        for i, p in enumerate(prompts):
            try:
                out.append(cloudflare.generate_image(
                    f"{p}. Style: {niche_style}", dest_dir / f"scene_{i}.jpg"))
            except Exception as e:  # noqa: BLE001
                print(f"[images] cloudflare scene {i} failed ({e})")
                break
        if out:
            return out
    # 2. Pollinations (token tier)
    if pollinations.available():
        return pollinations.generate_scene_images(
            prompts, dest_dir, niche_style, width, height)
    return []
