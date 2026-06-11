import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { BrandMark } from "./BrandMark";

// Recurring outro (last ~3.4s): brand close + subscribe CTA. Consistent across
// every video = a recognizable channel signature (helps brand + retention).
export const Outro: React.FC<{
  accent: string; bg: string; font: string; portrait: boolean; closer?: string;
}> = ({ accent, bg, font, portrait, closer = "Build what cannot be taken." }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const start = durationInFrames - Math.round(fps * 3.4);
  if (frame < start) return null;

  const local = frame - start;
  const fade = interpolate(local, [0, 14], [0, 1], { extrapolateRight: "clamp" });
  const rise = spring({ frame: local, fps, durationInFrames: 18, config: { damping: 200 } });

  return (
    <AbsoluteFill style={{
      background: `${bg}E6`, alignItems: "center", justifyContent: "center",
      opacity: fade, gap: 22,
    }}>
      <div style={{ transform: `translateY(${interpolate(rise, [0, 1], [20, 0])}px)`,
        display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
        <BrandMark size={portrait ? 150 : 120} accent={accent} stroke={2.5} />
        <div style={{ fontFamily: font, color: "white", fontSize: portrait ? 52 : 46,
          fontWeight: 800, textAlign: "center", padding: "0 8%" }}>{closer}</div>
        <div style={{ fontFamily: font, color: accent, letterSpacing: 4,
          fontSize: portrait ? 32 : 26, fontWeight: 600 }}>
          ▸ SUBSCRIBE · QUIET CAPITAL
        </div>
      </div>
    </AbsoluteFill>
  );
};
