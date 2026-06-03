import React from "react";
import { Composition } from "remotion";
import { NicheVideo } from "./NicheVideo";
import { DEFAULT_PROPS, NicheVideoProps } from "./style";

const FPS = 30;

// The pipeline may pass an optional durationInFrames (computed from the
// voiceover length) inside --props; otherwise default to 12s.
const calcMeta = ({ props }: { props: NicheVideoProps }) => {
  const dur = Number((props as any).durationInFrames) || FPS * 12;
  return { durationInFrames: Math.round(dur), fps: FPS };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="NicheVideoLandscape"
        component={NicheVideo}
        width={1920}
        height={1080}
        fps={FPS}
        durationInFrames={FPS * 12}
        defaultProps={DEFAULT_PROPS}
        calculateMetadata={calcMeta}
      />
      <Composition
        id="NicheVideoPortrait"
        component={NicheVideo}
        width={1080}
        height={1920}
        fps={FPS}
        durationInFrames={FPS * 12}
        defaultProps={DEFAULT_PROPS}
        calculateMetadata={calcMeta}
      />
    </>
  );
};
