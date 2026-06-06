# Background music library (royalty-free)

Drop **royalty-free, commercial-use, no-attribution** tracks here and the
pipeline will automatically duck them under the voice per niche **mood**.

## Layout

```
assets/music/<mood>/*.mp3      # mood-specific (preferred)
assets/music/*.mp3             # flat fallback (used if a mood folder is empty)
```

Moods used by the niches: `calm`, `energetic`, `neutral`, `eerie`, `moody`,
`clinical`, `bold`, `intimate`.

## Where to get free tracks (no copyright claims)
- **Pixabay Music** — https://pixabay.com/music/ (free, commercial, no attribution)
- **YouTube Audio Library** (in YouTube Studio) — free tracks
- **Freesound** (CC0 filter) — https://freesound.org

Download a handful per mood and drop them in the matching folder. The pipeline
loops/ducks them automatically — no code change. Keep files reasonably sized.

> On GitHub Actions: commit a few small tracks here (they're not gitignored), or
> have the workflow fetch them from a public URL you control.
