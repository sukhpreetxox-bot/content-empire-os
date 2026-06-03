# Content Empire OS

Self-hosted, free-tier multi-channel content automation for **5 YouTube** + **5 Instagram** faceless channels. No n8n/Make, no paid services.

> **Status:** Foundation layer (repo + database schema + 10-niche seed). Other layers are built incrementally — see [Roadmap](#roadmap).

## Stack (no paid services)

| Concern | Tool | Free tier |
|---|---|---|
| Compute / cron | Oracle Cloud Always Free ARM VM (4 CPU / 24 GB) | forever |
| Database | Supabase (Postgres) | forever (kept awake by analytics-cron) |
| Dashboard | Next.js + Tailwind on Vercel Hobby | forever |
| Scripts | Ollama (Llama 3 / Mistral) → Groq fallback | local / free |
| Voiceover | edge-tts (Microsoft neural voices) | free |
| Video | Remotion (React → MP4) + FFmpeg, B-roll via Pexels | free |

## Architecture (3 + 1 cron jobs)

```
generation-cron (per channel)
  idea → script (Ollama) → EDITORIAL-VALUE GATE → edge-tts → Remotion+FFmpeg
  → thumbnail → write row status='review'
        │
        ▼   (you open the dashboard, preview, click)
human approval gate  →  status='approved' | 'rejected'
        │
        ▼
publication-cron     picks status='approved' & due → YouTube/IG upload
  (throttled, synthetic-disclosure flag) → status='published' → plan next slot

analytics-cron (daily)  pull YT Analytics + IG insights → analytics table
  (also keeps Supabase awake)
```

The **only** human step is approve/reject in the dashboard. Everything else is cron-driven.

## Repository layout

```
db/         schema.sql + seed.sql (10 niches)          ← you are here
pipeline/   Python cron scripts + helpers/             (next)
remotion/   props-driven video templates per niche     (next)
dashboard/  Next.js approval dashboard                 (next)
docs/       non-developer setup guide                  (next)
assets/     generated voiceovers / video / thumbnails  (gitignored)
```

## Quick start (database only, for now)

1. Create a free Supabase project → copy the connection string.
2. `cp .env.example .env` and fill `SUPABASE_DB_URL`.
3. Load the schema + seed:
   ```bash
   psql "$SUPABASE_DB_URL" -f db/schema.sql
   psql "$SUPABASE_DB_URL" -f db/seed.sql      # prints "Seed complete: 10 niches..."
   ```
   (Or paste both files into the Supabase SQL editor.)

See [db/README.md](db/README.md) for the data model.

## The 10 niches

**YouTube:** Quiet Capital (finance) · Leverage Lab (AI tools) · Plain Law (legal) · Coherent (health) · Lights Off (horror)
**Instagram:** @thequietascent · @theprimedbody · @buildquietbrands · @theattachmentlab · @quietcashflow

Each niche is **one row** — add/edit/replace a niche from the dashboard with no code change.

## Policy-safe by design

- **Editorial-value gate**: every script must carry a unique angle/analysis/transformation before it can reach review — blocks bare fact-recaps and templated mass content (YouTube "inauthentic content", Jul 2025+).
- **Synthetic-media disclosure** flag set automatically on realistic AI content.
- **Per-niche disclaimers** (finance/legal/health) injected automatically; "get rich quick" framings blocked.
- **Royalty-free assets only** (Pexels) to avoid Content ID strikes.
- **Throttling**: YouTube ~6 uploads/day/project budget respected; IG <25 posts/24h/account.

> ⚠️ Realistic expectation: large-scale faceless AI channels carry genuine demonetisation/ban risk on YouTube and Meta even with these guardrails. This system minimises risk; it cannot eliminate it.

## Roadmap

- [x] **Layer 0** — repo scaffold + Supabase schema + 10-niche seed *(live in Supabase)*
- [x] **Layer 1** — Python pipeline (3 crons) + helpers (edge-tts, Pexels, FFmpeg, YouTube, IG)
- [x] **Layer 2** — Remotion props-driven templates per niche *(renders verified)*
- [x] **Layer 3** — Next.js dashboard (kanban, approval, analytics, calendar) *(buttons live-tested)*
- [x] **Layer 4** — non-developer setup guide → [docs/SETUP.md](docs/SETUP.md)
- [x] **Layer 5** — compute on **GitHub Actions** (free, no card) instead of an Oracle VM:
  `.github/workflows/` run generate (daily) / publish (hourly) / analytics (daily).
  Dashboard deployed to **Vercel** (Basic-Auth protected). First live run verified.
- [ ] **Go-live remainder** — YouTube OAuth (5×) + Instagram tokens so `publish` can upload.
