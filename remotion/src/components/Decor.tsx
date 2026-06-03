import React from "react";
import { useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import { StyleProps } from "../style";

// Mood-driven decorative layer so each niche has a distinct visual identity,
// all driven by the niche's style_props (no per-niche code paths needed).
export const Decor: React.FC<{ style: StyleProps }> = ({ style }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;

  switch (style.mood) {
    case "energetic": {
      // neon grid drifting upward
      const offset = (frame * 2) % 80;
      return (
        <svg width={width} height={height} style={{ position: "absolute", opacity: 0.25 }}>
          {Array.from({ length: 30 }).map((_, i) => (
            <line key={`h${i}`} x1={0} x2={width} y1={i * 80 - offset} y2={i * 80 - offset}
              stroke={style.accent} strokeWidth={1} />
          ))}
          {Array.from({ length: 30 }).map((_, i) => (
            <line key={`v${i}`} y1={0} y2={height} x1={i * 80} x2={i * 80}
              stroke={style.accent} strokeWidth={1} />
          ))}
        </svg>
      );
    }
    case "eerie": {
      // dark vignette + drifting fog blobs
      const fog = interpolate(Math.sin(frame / 30), [-1, 1], [0.15, 0.4]);
      return (
        <>
          <div style={{
            position: "absolute", inset: 0,
            background: `radial-gradient(circle at 50% 40%, transparent 0%, ${style.bg} 75%)`,
          }} />
          <div style={{
            position: "absolute", inset: 0, opacity: fog,
            background: `radial-gradient(circle at ${30 + 20 * Math.sin(t * 6)}% 60%, ${style.accent}33, transparent 40%)`,
          }} />
        </>
      );
    }
    case "calm":
    case "intimate": {
      // slow rising accent bars (finance-y / soft)
      return (
        <svg width={width} height={height} style={{ position: "absolute", opacity: 0.18 }}>
          {Array.from({ length: 8 }).map((_, i) => {
            const h = interpolate(frame, [0, durationInFrames],
              [40, 120 + i * 30 * (0.5 + (i % 3))], { extrapolateRight: "clamp" });
            return <rect key={i} x={80 + i * (width / 9)} y={height - h}
              width={width / 14} height={h} fill={style.accent} rx={6} />;
          })}
        </svg>
      );
    }
    case "clinical":
    case "neutral": {
      return (
        <div style={{
          position: "absolute", inset: 0, opacity: 0.5,
          background: `linear-gradient(135deg, ${style.bg}, ${style.accent}10)`,
        }} />
      );
    }
    default: {
      // bold / moody: large drifting accent circle
      const x = interpolate(Math.sin(frame / 40), [-1, 1], [width * 0.2, width * 0.8]);
      return (
        <div style={{
          position: "absolute", left: x - 200, top: height * 0.1,
          width: 400, height: 400, borderRadius: 9999,
          background: style.accent, opacity: 0.12, filter: "blur(40px)",
        }} />
      );
    }
  }
};
