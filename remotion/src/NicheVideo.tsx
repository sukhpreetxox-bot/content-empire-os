import React from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame,
  useVideoConfig, interpolate, spring,
} from "remotion";
import { NicheVideoProps } from "./style";
import { Decor } from "./components/Decor";
import { Captions } from "./components/Captions";

// Remote URLs are used as-is; bare filenames are resolved from public/ (the
// pipeline copies the voiceover / B-roll there before rendering).
const resolveSrc = (src: string) =>
  /^https?:\/\//.test(src) ? src : staticFile(src);

// One props-driven composition that renders every niche's identity from
// style_props + template. The pipeline passes content via --props.
export const NicheVideo: React.FC<NicheVideoProps> = ({
  style, title, hook, scriptLines, audioSrc, bgVideo,
}) => {
  const { fps, width } = useVideoConfig();
  const frame = useCurrentFrame();
  const titleIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 20 });
  const titleY = interpolate(titleIn, [0, 1], [40, 0]);
  const portrait = width < 1200;

  return (
    <AbsoluteFill style={{ backgroundColor: style.bg }}>
      {bgVideo ? (
        <OffthreadVideo src={resolveSrc(bgVideo)} muted
          style={{ position: "absolute", width: "100%", height: "100%", objectFit: "cover", opacity: 0.35 }} />
      ) : null}

      <Decor style={style} />

      {/* Title card for the first ~2.5s, then it stays as a small header */}
      <div style={{
        position: "absolute", top: portrait ? "12%" : "10%", left: 0, right: 0,
        padding: "0 8%", textAlign: "center",
        opacity: titleIn, transform: `translateY(${titleY}px)`,
      }}>
        <div style={{
          fontFamily: style.font, color: style.accent,
          fontSize: portrait ? 72 : 64, fontWeight: 800, lineHeight: 1.1,
          textShadow: "0 2px 20px rgba(0,0,0,0.6)",
        }}>
          {title}
        </div>
        <div style={{
          marginTop: 18, fontFamily: style.font, color: "white",
          fontSize: portrait ? 40 : 34, opacity: 0.9,
        }}>
          {hook}
        </div>
      </div>

      <Sequence from={Math.round(fps * 1.5)}>
        <Captions lines={scriptLines} style={style} />
      </Sequence>

      {audioSrc ? <Audio src={resolveSrc(audioSrc)} /> : null}

      {/* Accent baseline */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0, height: 8,
        background: style.accent, opacity: 0.8,
      }} />
    </AbsoluteFill>
  );
};
