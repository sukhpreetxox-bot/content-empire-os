// Shared prop types. The pipeline passes these from the niches table:
// niches.style_props -> StyleProps, niches.remotion_template -> template.

export type Mood =
  | "calm" | "energetic" | "neutral" | "eerie"
  | "moody" | "clinical" | "bold" | "intimate";

// Use `type` (not `interface`) so these satisfy Remotion's
// `Record<string, unknown>` props constraint (type aliases get an implicit
// index signature; interfaces do not).
export type StyleProps = {
  bg: string;       // background color
  accent: string;   // accent color
  font: string;     // font family
  mood: Mood;
};

export type Word = { word: string; start: number; end: number }; // seconds

export type NicheVideoProps = {
  template: string;          // e.g. "FinanceTemplate" (informational)
  style: StyleProps;
  title: string;
  hook: string;
  scriptLines: string[];     // narration split into caption lines
  audioSrc?: string | null;  // file path / URL of the voiceover
  bgVideo?: string | null;   // optional B-roll (staticFile path or URL)
  bgImages?: string[] | null;// AI scene images (preferred); cycled w/ Ken Burns
  words?: Word[] | null;     // Whisper word-level timings → exact karaoke
  variant?: number;          // 0-2: subtle layout variation (anti-templated)
  closer?: string | null;    // outro closing line
};

export const DEFAULT_STYLE: StyleProps = {
  bg: "#0a1f3c", accent: "#d4af37", font: "Georgia", mood: "calm",
};

export const DEFAULT_PROPS: NicheVideoProps = {
  template: "FinanceTemplate",
  style: DEFAULT_STYLE,
  title: "Why index funds quietly beat most stock pickers",
  hook: "Most people lose to a fund they've never heard of.",
  scriptLines: [
    "Most people lose to a fund they've never heard of.",
    "It isn't picking winners — it's refusing to pick at all.",
    "An index fund buys the whole market, fees near zero.",
    "Over decades, that quiet discipline compounds.",
    "This is not financial advice. Do your own research.",
  ],
  audioSrc: null,
  bgVideo: null,
};
