import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { StyleProps, Word } from "../style";

const CHUNK = 5; // words shown at once when using real timings

// Karaoke captions. With Whisper `words` (real timings) we show a sliding chunk
// of words and highlight the spoken one frame-accurately; otherwise we fall
// back to evenly distributing `lines` across the duration.
export const Captions: React.FC<{
  lines: string[]; style: StyleProps; words?: Word[] | null; startSec?: number;
}> = ({ lines, style, words, startSec = 0 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width } = useVideoConfig();
  const portrait = width < 1200;
  const t = startSec + frame / fps;

  let display: { text: string; active: number };
  if (words && words.length) {
    let active = 0;
    for (let i = 0; i < words.length; i++) {
      if (words[i].start <= t) active = i; else break;
    }
    const chunkStart = Math.floor(active / CHUNK) * CHUNK;
    const chunk = words.slice(chunkStart, chunkStart + CHUNK);
    display = { text: chunk.map((w) => w.word).join(" "), active: active - chunkStart };
  } else {
    const per = durationInFrames / Math.max(lines.length, 1);
    const idx = Math.min(lines.length - 1, Math.floor(frame / per));
    const localWords = (lines[idx] || "").split(/\s+/).filter(Boolean);
    const active = Math.floor((frame - idx * per) / (per / Math.max(localWords.length, 1)));
    display = { text: localWords.join(" "), active };
  }

  const tokens = display.text.split(/\s+/).filter(Boolean);
  const blockIn = spring({ frame: frame % 12, fps, config: { damping: 200 }, durationInFrames: 8 });
  const y = interpolate(blockIn, [0, 1], [16, 0]);

  return (
    <div style={{
      position: "absolute", left: 0, right: 0, bottom: portrait ? "18%" : "12%",
      padding: portrait ? "0 8%" : "0 14%", textAlign: "center",
      transform: `translateY(${y}px)`,
    }}>
      <div style={{
        display: "inline-block", padding: "14px 28px", borderRadius: 18,
        background: "rgba(0,0,0,0.36)", backdropFilter: "blur(6px)",
        fontFamily: style.font, fontWeight: 800,
        fontSize: portrait ? 62 : 52, lineHeight: 1.22,
        textShadow: "0 2px 16px rgba(0,0,0,0.85)",
      }}>
        {tokens.map((w, i) => {
          const isActive = i === display.active;
          return (
            <span key={i} style={{
              color: isActive ? style.accent : "white",
              opacity: i <= display.active ? 1 : 0.45,
              transform: isActive ? "scale(1.07)" : "scale(1)",
              display: "inline-block", margin: "0 0.16em",
            }}>{w}</span>
          );
        })}
      </div>
    </div>
  );
};
