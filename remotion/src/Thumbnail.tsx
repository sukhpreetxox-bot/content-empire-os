import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BrandMark } from "./components/BrandMark";
import { StyleProps, DEFAULT_STYLE } from "./style";

// A deliberate, on-brand 1280x720 thumbnail (packaging = the product). Reuses
// the brand emblem, navy/gold system, and title typography. Rendered via
// `remotion still` so the font + emblem match the video exactly — never a
// random video frame.
export type ThumbnailProps = {
  style: StyleProps;
  title: string;
  bgImage?: string | null; // staticFile name of an AI scene image (optional)
  variant?: number;
};

export const THUMB_DEFAULT: ThumbnailProps = {
  style: DEFAULT_STYLE,
  title: "Your Avoidance Isn't Inaction. It's Control.",
  bgImage: null,
  variant: 0,
};

// Title scales down as it gets longer so it never overflows the safe area.
const titleSize = (title: string): number => {
  const n = title.length;
  if (n > 56) return 64;
  if (n > 40) return 78;
  if (n > 26) return 94;
  return 108;
};

export const Thumbnail: React.FC<ThumbnailProps> = ({
  style = DEFAULT_STYLE, title, bgImage, variant = 0,
}) => {
  const { bg, accent, font } = style;
  const size = titleSize(title || "");

  return (
    <AbsoluteFill style={{ backgroundColor: bg, fontFamily: font }}>
      {bgImage ? (
        <>
          <Img
            src={staticFile(bgImage)}
            style={{ position: "absolute", width: "100%", height: "100%",
              objectFit: "cover", opacity: 0.55 }}
          />
          {/* scrim: darken toward the bottom-left where the title sits */}
          <AbsoluteFill style={{
            background:
              `linear-gradient(105deg, ${bg}F2 0%, ${bg}CC 42%, ${bg}55 100%)`,
          }} />
        </>
      ) : (
        <AbsoluteFill style={{
          background: `radial-gradient(120% 90% at 78% 12%, ${accent}22, ${bg} 60%)`,
        }} />
      )}

      <AbsoluteFill style={{
        padding: "72px 80px", display: "flex", flexDirection: "column",
        justifyContent: "space-between",
      }}>
        {/* brand lockup */}
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <BrandMark size={72} accent={accent} stroke={3} progress={1} />
          <span style={{ color: accent, fontSize: 30, fontWeight: 700,
            letterSpacing: 6 }}>QUIET CAPITAL</span>
        </div>

        {/* headline — lower third, editorial, high contrast */}
        <div style={{ maxWidth: "84%",
          transform: variant === 2 ? "translateY(-24px)" : "none" }}>
          <div style={{ color: "white", fontSize: size, fontWeight: 900,
            lineHeight: 1.02, letterSpacing: -0.5,
            textShadow: "0 4px 28px rgba(0,0,0,0.55)" }}>
            {title}
          </div>
          <div style={{ marginTop: 26, height: 8, width: 148,
            background: accent, borderRadius: 4 }} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
