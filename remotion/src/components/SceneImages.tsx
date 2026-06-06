import React from "react";
import {
  AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate,
} from "remotion";

const src = (s: string) => (/^https?:\/\//.test(s) ? s : staticFile(s));

// Cycle AI scene images across the video, each with a Ken Burns push and a
// crossfade into the next — gives constant cinematic motion from stills.
export const SceneImages: React.FC<{ images: string[] }> = ({ images }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const per = durationInFrames / Math.max(images.length, 1);
  const fade = Math.min(18, per * 0.25);

  return (
    <AbsoluteFill>
      {images.map((im, i) => {
        const start = i * per;
        const local = frame - start;
        if (local < -fade || local > per + fade) return null;
        const opacity = interpolate(
          local, [-fade, 0, per - fade, per], [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const scale = interpolate(local, [0, per], [1.08, 1.24],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const px = interpolate(local, [0, per], [-1.5, 1.5]);
        return (
          <Img key={i} src={src(im)}
            style={{
              position: "absolute", width: "100%", height: "100%",
              objectFit: "cover", opacity,
              transform: `scale(${scale}) translateX(${px}%)`,
            }} />
        );
      })}
    </AbsoluteFill>
  );
};
