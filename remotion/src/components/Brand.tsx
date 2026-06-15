import React from "react";
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Easing,
} from "remotion";
import { BrandMark } from "./BrandMark";

const WORD = "QUIET CAPITAL";

// Recurring, identical on every video:
//  1) a clean intro CARD where the emblem DRAWS ITSELF and the wordmark reveals
//     letter by letter, then dissolves to reveal the video,
//  2) a small persistent corner bug for the rest.
export const Brand: React.FC<{ accent: string; bg: string; font: string; portrait: boolean }> = ({
  accent, bg, font, portrait,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // Full intro card only on landscape (long/deep). Shorts stay hook-first
  // (no 2s logo card eating retention) — just the corner bug.
  const introDur = portrait ? 0 : Math.round(fps * 2.3);

  if (frame < introDur) {
    // emblem draw 0.15s → 1.5s with smooth easing
    const progress = interpolate(frame, [fps * 0.15, fps * 1.5], [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const fadeOut = interpolate(frame, [introDur - fps * 0.45, introDur], [1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const lineY = interpolate(frame, [fps * 1.4, fps * 1.8], [14, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });

    return (
      <AbsoluteFill style={{
        backgroundColor: bg, alignItems: "center", justifyContent: "center",
        gap: portrait ? 26 : 22, opacity: fadeOut,
      }}>
        <BrandMark size={portrait ? 200 : 168} accent={accent} stroke={2.4} progress={progress} />
        <div style={{ display: "flex", transform: `translateY(${lineY}px)` }}>
          {WORD.split("").map((ch, i) => {
            const t = fps * 1.05 + i * 1.6; // staggered letters
            const o = interpolate(frame, [t, t + 8], [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const y = interpolate(o, [0, 1], [10, 0]);
            return (
              <span key={i} style={{
                fontFamily: font, color: accent, fontWeight: 700,
                fontSize: portrait ? 42 : 36, letterSpacing: portrait ? 8 : 7,
                opacity: o, transform: `translateY(${y}px)`,
                whiteSpace: "pre",
              }}>{ch === " " ? " " : ch}</span>
            );
          })}
        </div>
      </AbsoluteFill>
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
