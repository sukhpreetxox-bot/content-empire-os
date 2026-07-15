import React from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame,
  useVideoConfig, interpolate, spring,
} from "remotion";
import { NicheVideoProps } from "./style";
import { Decor } from "./components/Decor";
import { Captions } from "./components/Captions";
import { FilmGrain } from "./components/FilmGrain";
import { Vignette } from "./components/Vignette";
import { SceneImages } from "./components/SceneImages";
import { Brand } from "./components/Brand";
import { Outro } from "./components/Outro";

const resolveSrc = (src: string) =>
  /^https?:\/\//.test(src) ? src : staticFile(src);

// Slow Ken Burns zoom/pan on the background for constant gentle motion.
const KenBurns: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [1.12, 1.28],
    { extrapolateRight: "clamp" });
  const x = interpolate(frame, [0, durationInFrames], [-2, 2]);
  const y = interpolate(frame, [0, durationInFrames], [2, -2]);
  return (
    <OffthreadVideo
      src={resolveSrc(src)} muted
      style={{
        position: "absolute", width: "100%", height: "100%", objectFit: "cover",
        transform: `scale(${scale}) translate(${x}%, ${y}%)`, opacity: 0.55,
      }}
    />
  );
};

export const NicheVideo: React.FC<NicheVideoProps> = ({
  style, title, hook, scriptLines, audioSrc, bgVideo, bgImages, words,
  variant = 0, closer,
}) => {
  const { fps, width, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  const portrait = width < 1200;
  const v = ((variant % 3) + 3) % 3;
  const titleTop = [portrait ? "11%" : "9%", portrait ? "14%" : "12%", portrait ? "9%" : "7%"][v];

  // Title: settle almost instantly — the claim must be legible at frame 0
  // (a slow blur-in costs first-second retention on Shorts).
  const tIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 10 });
  const titleBlur = interpolate(tIn, [0, 1], [7, 0]);
  const titleY = interpolate(tIn, [0, 1], [24, 0]);
  const hookIn = spring({ frame: frame - 4, fps, config: { damping: 200 }, durationInFrames: 12 });

  // Progress bar.
  const progress = interpolate(frame, [0, durationInFrames], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: style.bg }}>
      {/* Background: AI scene images (preferred) → b-roll → mood decor */}
      {bgImages && bgImages.length
        ? <SceneImages images={bgImages} />
        : bgVideo ? <KenBurns src={bgVideo} /> : null}
      <Decor style={style} />
      <Vignette strength={style.mood === "eerie" ? 0.7 : 0.5} />

      {/* Title block (top) */}
      <div style={{
        position: "absolute", top: titleTop, left: 0, right: 0,
        padding: "0 8%", textAlign: "center",
        opacity: tIn, transform: `translateY(${titleY}px)`,
        filter: `blur(${titleBlur}px)`,
      }}>
        <div style={{
          fontFamily: style.font, color: style.accent,
          fontSize: portrait ? 78 : 66, fontWeight: 900, lineHeight: 1.05,
          letterSpacing: "-0.5px", textShadow: "0 4px 28px rgba(0,0,0,0.7)",
        }}>
          {title}
        </div>
        <div style={{
          marginTop: 16, fontFamily: style.font, color: "rgba(255,255,255,0.92)",
          fontSize: portrait ? 40 : 34, fontWeight: 500, opacity: hookIn,
          transform: `translateY(${interpolate(hookIn, [0, 1], [16, 0])}px)`,
        }}>
          {hook}
        </div>
      </div>

      {/* Word-by-word captions (lower third) — start almost immediately so the
          spoken hook has synced words in the first second, not after 1.6s. */}
      <Sequence from={Math.round(fps * 0.5)}>
        <Captions lines={scriptLines} style={style} words={words} startSec={0.5} variant={v} />
      </Sequence>

      {/* Progress bar */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 6,
        background: "rgba(255,255,255,0.12)" }}>
        <div style={{ height: "100%", width: `${progress * 100}%`,
          background: style.accent }} />
      </div>

      <Brand accent={style.accent} bg={style.bg} font={style.font} portrait={portrait} />
      <Outro accent={style.accent} bg={style.bg} font={style.font}
        portrait={portrait} closer={closer ?? undefined} />

      <FilmGrain opacity={0.06} />
      {audioSrc ? <Audio src={resolveSrc(audioSrc)} /> : null}
    </AbsoluteFill>
  );
};
