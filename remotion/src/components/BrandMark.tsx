import React from "react";

const clamp = (x: number) => Math.max(0, Math.min(1, x));

// The Quiet Capital emblem (gold ring + ascending "compounding" line). With
// `progress` 0→1 it DRAWS ITSELF: the ring sweeps in, then the line grows point
// by point. progress=1 (default) renders it fully (used for the corner bug).
export const BrandMark: React.FC<{
  size: number; accent?: string; stroke?: number; progress?: number;
}> = ({ size, accent = "#d4af37", stroke = 2, progress = 1 }) => {
  const s = 100;
  const cx = s / 2;
  const r = 44;
  const C = 2 * Math.PI * r;
  const pts = [[20, 64], [42, 52], [62, 42], [82, 26]] as const;

  const ringP = clamp(progress / 0.55);            // ring draws over first 55%
  const lineP = clamp((progress - 0.45) / 0.55);   // line draws over last 55%

  return (
    <svg width={size} height={size} viewBox={`0 0 ${s} ${s}`} fill="none">
      <circle
        cx={cx} cy={cx} r={r} stroke={accent} strokeWidth={stroke}
        strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - ringP)}
        transform={`rotate(-90 ${cx} ${cx})`}
      />
      <polyline
        points={pts.map((p) => p.join(",")).join(" ")}
        stroke={accent} strokeWidth={stroke * 1.4} fill="none"
        strokeLinecap="round" strokeLinejoin="round"
        pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lineP}
      />
      {pts.map(([x, y], i) => {
        const appear = clamp((lineP - (i / pts.length)) * 6);
        return (
          <circle key={i} cx={x} cy={y} r={2.4 * appear} fill="#0a1f3c"
            stroke={accent} strokeWidth={stroke} opacity={appear} />
        );
      })}
    </svg>
  );
};
