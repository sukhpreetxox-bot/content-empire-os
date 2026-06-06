import React from "react";
import { useCurrentFrame } from "remotion";

// Animated film grain via SVG turbulence — adds a subtle organic texture that
// reads as "cinematic" rather than flat/AI. Cheap to render.
export const FilmGrain: React.FC<{ opacity?: number }> = ({ opacity = 0.06 }) => {
  const frame = useCurrentFrame();
  const seed = frame % 12; // shift the noise each frame
  return (
    <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%",
      opacity, pointerEvents: "none", mixBlendMode: "overlay" }}>
      <filter id="grain">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2}
          seed={seed} stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter="url(#grain)" />
    </svg>
  );
};
