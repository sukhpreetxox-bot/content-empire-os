import React from "react";

// The Quiet Capital emblem (gold ring + ascending "compounding" line), drawn as
// scalable SVG so it stays crisp at any size. Reused for the intro flash and
// the persistent corner brand bug.
export const BrandMark: React.FC<{ size: number; accent?: string; stroke?: number }> = ({
  size, accent = "#d4af37", stroke = 2,
}) => {
  const s = 100;
  const pts = [
    [20, 64], [42, 52], [62, 42], [82, 26],
  ] as const;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${s} ${s}`} fill="none">
      <circle cx={s / 2} cy={s / 2} r={44} stroke={accent} strokeWidth={stroke} />
      <polyline
        points={pts.map((p) => p.join(",")).join(" ")}
        stroke={accent} strokeWidth={stroke * 1.4} fill="none"
        strokeLinecap="round" strokeLinejoin="round"
      />
      {pts.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={2.4} fill="#0a1f3c" stroke={accent}
          strokeWidth={stroke} />
      ))}
    </svg>
  );
};
