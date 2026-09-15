import React from "react";
import {
  AbsoluteFill, Img, OffthreadVideo, staticFile, useCurrentFrame,
  useVideoConfig, interpolate,
} from "remotion";

const src = (s: string) => (/^https?:\/\//.test(s) ? s : staticFile(s));

type Seg = { type: "img" | "clip"; src: string };

// Interleave motion clips (hero beats) evenly among AI stills. With no clips
// this reduces to the same still-cycling behaviour as SceneImages.
const buildSegments = (images: string[], clips: string[]): Seg[] => {
  if (!clips.length) return images.map((s) => ({ type: "img", src: s }));
  const total = images.length + clips.length;
  const clipSlots = new Set<number>();
  for (let k = 0; k < clips.length; k++) {
    clipSlots.add(Math.round((k + 0.5) * (total / clips.length)));
  }
  const segs: Seg[] = [];
  let ii = 0, ci = 0;
  for (let s = 0; s < total; s++) {
    if (clipSlots.has(s) && ci < clips.length) segs.push({ type: "clip", src: clips[ci++] });
    else if (ii < images.length) segs.push({ type: "img", src: images[ii++] });
    else if (ci < clips.length) segs.push({ type: "clip", src: clips[ci++] });
  }
  return segs;
};

// Hybrid background: AI stills (Ken Burns) + real motion b-roll clips, each in
// its own time slot with a crossfade — cinematic variety for long-form.
export const SceneVisuals: React.FC<{ images: string[]; clips: string[] }> = ({
  images, clips,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const segs = buildSegments(images || [], clips || []);
  const per = durationInFrames / Math.max(segs.length, 1);
  const fade = Math.min(18, per * 0.25);

  return (
    <AbsoluteFill>
      {segs.map((seg, i) => {
        const start = i * per;
        const local = frame - start;
        if (local < -fade || local > per + fade) return null;
        const opacity = interpolate(
          local, [-fade, 0, per - fade, per], [0, 1, 1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const scale = interpolate(local, [0, per], [1.08, 1.22],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const px = interpolate(local, [0, per], [-1.5, 1.5]);
        const common: React.CSSProperties = {
          position: "absolute", width: "100%", height: "100%",
          objectFit: "cover", opacity,
          transform: `scale(${scale}) translateX(${px}%)`,
        };
        return seg.type === "clip"
          ? <OffthreadVideo key={i} src={src(seg.src)} muted style={common} />
          : <Img key={i} src={src(seg.src)} style={common} />;
      })}
    </AbsoluteFill>
  );
};
