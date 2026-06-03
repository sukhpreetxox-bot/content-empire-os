import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { StyleProps } from "../style";

// Sequentially reveals narration lines, evenly spread across the video.
export const Captions: React.FC<{ lines: string[]; style: StyleProps }> = ({
  lines, style,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width } = useVideoConfig();
  const per = durationInFrames / Math.max(lines.length, 1);
  const idx = Math.min(lines.length - 1, Math.floor(frame / per));
  const local = frame - idx * per;
  const enter = spring({ frame: local, fps, config: { damping: 200 }, durationInFrames: 15 });
  const y = interpolate(enter, [0, 1], [30, 0]);

  return (
    <div style={{
      position: "absolute", left: 0, right: 0, bottom: "12%",
      padding: "0 8%", textAlign: "center",
    }}>
      <div style={{
        opacity: enter, transform: `translateY(${y}px)`,
        fontFamily: style.font, fontSize: width > 1200 ? 52 : 60,
        lineHeight: 1.25, color: "white", fontWeight: 600,
        textShadow: "0 2px 18px rgba(0,0,0,0.7)",
      }}>
        {lines[idx]}
      </div>
    </div>
  );
};
