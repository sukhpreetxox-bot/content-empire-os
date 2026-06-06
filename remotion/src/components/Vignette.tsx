import React from "react";

// Cinematic vignette — darkens the edges so the eye lands on the center text.
export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <div style={{
    position: "absolute", inset: 0, pointerEvents: "none",
    background:
      `radial-gradient(120% 90% at 50% 45%, transparent 40%, rgba(0,0,0,${strength}) 100%)`,
  }} />
);
