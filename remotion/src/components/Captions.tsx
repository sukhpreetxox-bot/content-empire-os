import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { StyleProps } from "../style";

// Word-by-word "karaoke" captions: each line gets an equal time slot, words
// reveal in sequence, the active word is highlighted in the accent colour.
// Looks dynamic and modern vs. a static line.
export const Captions: React.FC<{ lines: string[]; style: StyleProps }> = ({
  lines, style,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width } = useVideoConfig();
  const portrait = width < 1200;

  const per = durationInFrames / Math.max(lines.length, 1);
  const idx = Math.min(lines.length - 1, Math.floor(frame / per));
  const local = frame - idx * per;
  const words = (lines[idx] || "").split(/\s+/).filter(Boolean);
  const wordSlot = per / Math.max(words.length, 1);
  const activeWord = Math.floor(local / wordSlot);

  const blockIn = spring({ frame: local, fps, config: { damping: 200 }, durationInFrames: 10 });
  const y = interpolate(blockIn, [0, 1], [24, 0]);

  return (
    <div style={{
      position: "absolute", left: 0, right: 0, bottom: portrait ? "16%" : "11%",
      padding: portrait ? "0 8%" : "0 14%", textAlign: "center",
      transform: `translateY(${y}px)`, opacity: blockIn,
    }}>
      <div style={{
        display: "inline-block", padding: "14px 26px", borderRadius: 18,
        background: "rgba(0,0,0,0.34)", backdropFilter: "blur(6px)",
        fontFamily: style.font, fontWeight: 800,
        fontSize: portrait ? 56 : 50, lineHeight: 1.25,
        textShadow: "0 2px 16px rgba(0,0,0,0.8)",
      }}>
        {words.map((w, i) => {
          const shown = i <= activeWord;
          const isActive = i === activeWord;
          return (
            <span key={i} style={{
              color: isActive ? style.accent : "white",
              opacity: shown ? 1 : 0.25,
              transform: isActive ? "scale(1.06)" : "scale(1)",
              display: "inline-block", margin: "0 0.18em",
              transition: "none",
            }}>
              {w}
            </span>
          );
        })}
      </div>
    </div>
  );
};
