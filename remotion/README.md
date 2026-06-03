# Remotion (branded video templates)

One **props-driven** composition renders every niche's visual identity from the
`niches.style_props` + `remotion_template` columns — no per-niche code.

## Compositions

| id | size | use |
|---|---|---|
| `NicheVideoLandscape` | 1920×1080 | YouTube |
| `NicheVideoPortrait` | 1080×1920 | Instagram Reels |

Both accept `NicheVideoProps` (see `src/style.ts`): `template`, `style`
(`bg`/`accent`/`font`/`mood`), `title`, `hook`, `scriptLines`, optional
`audioSrc` / `bgVideo`, and an optional `durationInFrames` (the pipeline sets
this from the voiceover length via `calculateMetadata`).

`mood` drives the decorative layer (`src/components/Decor.tsx`): calm → rising
accent bars, energetic → neon grid, eerie → vignette + drifting fog, etc.

## Develop / preview

```bash
cd remotion && npm install
npm run studio        # interactive preview at localhost:3000
```

## Render (what the pipeline calls)

```bash
# still (thumbnail)
npx remotion still NicheVideoLandscape out/thumb.jpg --frame=60
# video, with content via props
npx remotion render NicheVideoPortrait out/clip.mp4 --props=props.json
```

Local audio / B-roll are loaded via `staticFile` from `public/`; the pipeline
(`pipeline/helpers/remotion.py`) copies them there before rendering. The
pipeline falls back to a plain FFmpeg B-roll assembly if a render fails.

Verified: still renders for the calm (Quiet Capital) and eerie (Lights Off)
styles produce correct, distinct, branded frames.
