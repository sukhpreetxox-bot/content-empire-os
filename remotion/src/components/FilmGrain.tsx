import React from "react";
import { useCurrentFrame } from "remotion";

// Cheap film grain. Full-screen SVG feTurbulence is far too slow per frame for
// video (it timed out a render), so we compute noise on a SMALL intrinsic
// canvas (160x90) with a STATIC seed and let CSS stretch it to full screen.
// Movement comes from a tiny transform, not from re-seeding (which forces a
// re-rasterise every frame).
export const FilmGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.06 }) => {
  const frame = useCurrentFrame();
  const dx = (frame % 3) - 1; // subtle 1px jitter, transform-only (GPU-cheap)
  const dy = (Math.floor(frame / 2) % 3) - 1;
  return (
    <svg viewBox="0 0 160 90" preserveAspectRatio="none"
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%",
        opacity, pointerEvents: "none", mixBlendMode: "overlay",
        transform: `translate(${dx}px, ${dy}px) scale(1.04)` }}>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={1}
          seed={4} stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="160" height="90" filter="url(#grain)" />
    </svg>
  );
};
