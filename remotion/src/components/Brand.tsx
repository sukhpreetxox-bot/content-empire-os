import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { BrandMark } from "./BrandMark";

// Recurring brand identity on every video:
//  - a short emblem "flash" at the very start (signature),
//  - then a small persistent corner bug for the rest (like a TV channel logo).
export const Brand: React.FC<{ accent: string; font: string; portrait: boolean }> = ({
  accent, font, portrait,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const introEnd = Math.round(fps * 1.5);

  if (frame < introEnd + fps) {
    // INTRO FLASH (center)
    const inIntro = spring({ frame, fps, durationInFrames: 16, config: { damping: 200 } });
    const out = interpolate(frame, [introEnd, introEnd + fps], [1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: 18,
        opacity: Math.min(inIntro, out),
      }}>
        <BrandMark size={portrait ? 180 : 150} accent={accent} stroke={2.5} />
        <div style={{
          fontFamily: font, color: accent, letterSpacing: 8,
          fontSize: portrait ? 40 : 34, fontWeight: 700,
        }}>QUIET&nbsp;CAPITAL</div>
      </div>
    );
  }

  // PERSISTENT CORNER BUG (top-left)
  return (
    <div style={{
      position: "absolute", top: portrait ? 36 : 28, left: portrait ? 36 : 40,
      display: "flex", alignItems: "center", gap: 10, opacity: 0.62,
    }}>
      <BrandMark size={portrait ? 44 : 38} accent={accent} stroke={3} />
      <span style={{ fontFamily: font, color: accent, letterSpacing: 3,
        fontSize: portrait ? 20 : 17, fontWeight: 600 }}>QUIET CAPITAL</span>
    </div>
  );
};
