#!/usr/bin/env python3
"""Render the Quiet Capital logo (avatar + wordmark) — philosophy: Quiet Conviction.
Supersampled 4x then downscaled for crisp, premium edges."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

NAVY = (10, 31, 60)
GOLD = (212, 175, 55)
GOLD_SOFT = (198, 162, 50)
HERE = Path(__file__).resolve().parent
FONTS = Path("/Users/singh/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/07a0d309-63c8-4411-9365-af898643d393/ef9fba40-45a8-459c-8edc-ba7566d133af/skills/canvas-design/canvas-fonts")
SERIF_BOLD = str(FONTS / "IBMPlexSerif-Bold.ttf")
SERIF_ELEGANT = str(FONTS / "LibreBaskerville-Regular.ttf")
SS = 4  # supersample


def tracked_text(draw, xy, text, font, fill, tracking, anchor_center_x=None):
    """Draw letter-spaced text. If anchor_center_x set, center the block on it."""
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (anchor_center_x - total / 2) if anchor_center_x is not None else xy[0]
    y = xy[1]
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += w + tracking
    return total


def ascending_line(draw, cx, cy, w, h, dot_r, lw):
    """A 4-point ascending trend line centered at (cx, cy)."""
    # monotonic upward — the line of compounding
    pts = [(-0.5, -0.42), (-0.17, -0.12), (0.17, 0.10), (0.5, 0.44)]
    coords = [(cx + px * w, cy - py * h) for px, py in pts]
    draw.line(coords, fill=GOLD, width=lw, joint="curve")
    for (x, y) in coords:
        draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=NAVY,
                     outline=GOLD, width=max(2, lw - 2))


def make_avatar(size=1024):
    S = size * SS
    img = Image.new("RGB", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    cx = cy = S / 2
    # thin disciplined ring
    r = S * 0.43
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=int(3 * SS))
    r2 = S * 0.40
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=GOLD_SOFT, width=int(1 * SS))
    # ascending line above the monogram
    ascending_line(d, cx, S * 0.40, S * 0.34, S * 0.20, int(7 * SS), int(4 * SS))
    # QC monogram, serif gravity, letter-spaced
    f = ImageFont.truetype(SERIF_BOLD, int(S * 0.26))
    asc, desc = f.getmetrics()
    y = cy + S * 0.02
    tracked_text(d, (0, y), "QC", f, GOLD, tracking=int(S * 0.03), anchor_center_x=cx)
    # tiny rule under monogram
    rw = S * 0.13
    ry = y + (asc + desc) + S * 0.015
    d.line([(cx - rw, ry), (cx + rw, ry)], fill=GOLD_SOFT, width=int(2 * SS))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(HERE / "quiet-capital-avatar.png")


def make_wordmark(w=2400, h=720):
    W, H = w * SS, h * SS
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # left emblem: small ring + ascending line
    ecx, ecy = H * 0.5, H * 0.5
    r = H * 0.34
    d.ellipse([ecx - r, ecy - r, ecx + r, ecy + r], outline=GOLD, width=int(3 * SS))
    ascending_line(d, ecx, ecy + H * 0.02, H * 0.42, H * 0.30, int(7 * SS), int(4 * SS))
    # wordmark
    f = ImageFont.truetype(SERIF_ELEGANT, int(H * 0.20))
    asc, desc = f.getmetrics()
    text_x = H * 1.05
    ty = H * 0.30
    tracked_text(d, (text_x, ty), "QUIET CAPITAL", f, GOLD, tracking=int(H * 0.035))
    # thin rule + whispered tagline
    ruley = ty + (asc + desc) + H * 0.04
    d.line([(text_x, ruley), (W - H * 0.25, ruley)], fill=GOLD_SOFT, width=int(2 * SS))
    ft = ImageFont.truetype(SERIF_ELEGANT, int(H * 0.072))
    d.text((text_x, ruley + H * 0.045), "P A T I E N T   W E A L T H", font=ft, fill=GOLD_SOFT)
    img = img.resize((w, h), Image.LANCZOS)
    img.save(HERE / "quiet-capital-wordmark.png")


if __name__ == "__main__":
    make_avatar()
    make_wordmark()
    print("wrote quiet-capital-avatar.png + quiet-capital-wordmark.png")
