# 📈 Long-term strategy — YouTube first (Quiet Capital)

## The model in one line
**Shorts pull strangers in (reach); long-form keeps them + pays (watch-time & RPM).**
Run both, drip them on a calendar, scale only when the data says so.

## Hard constraints (free, no money)
- **YouTube upload quota: ~6 uploads/day per Google Cloud project.** All channels
  on one project share this. Plenty for a slow, healthy ramp.
- **New-channel risk**: a brand-new channel that dumps 5 AI videos/day looks
  inauthentic → demonetisation/ban risk. We ramp deliberately.
- Compute is free (GitHub Actions; unlimited once the repo is public).

## Automatic upload-on-date (how it works)
Each piece has a `scheduled_for` timestamp. The hourly **publish** cron only
uploads **approved** items whose date is due, then marks them published.
- On **approve**, the system assigns the **next open daily slot** for that
  channel (drip), so videos space out across future dates automatically —
  you approve a batch, they release one per slot.
- Cadence/slot times live in the `publish_schedule` table (per channel, cron +
  daily cap). Change a row → change the calendar. No code.
- Result: you can approve a week of content in one sitting; it auto-releases
  on schedule, looking organic.

## Ramp-up calendar (Quiet Capital)
| Phase | Weeks | Shorts | Long-form | Why |
|---|---|---|---|---|
| **Warm-up** | 1–2 | 3 / week | 1 / week | establish the channel, avoid spam signals |
| **Build** | 3–6 | 5 / week | 2 / week | feed the algorithm, find winners |
| **Scale** | 7–12 | 1 / day | 2–3 / week | push what works; near the ~6/day cap |
| **Expand** | 12+ | — | — | add a 2nd channel (or 2nd GCP project) once monetised |

Set this via `publish_schedule` (daily_cap + cron) — start low, raise the cap as
phases progress.

## Shorts — built for views
- **9:16 portrait, ≤ 55s**, one single idea, **hook in the first second**.
- Big animated word-by-word captions (already built), fast pace, loopable ending.
- Topic = a sharp, curiosity-gap angle from the niche topic pool.
- Strong title + the niche disclaimer still applies.
- Shorts are the **discovery engine**: each should tease the deeper long-form.

## Long-form — built for revenue
- 16:9, 3–8 min, the full editorial angle, calm authoritative Kokoro voice.
- Higher RPM, watch-time, and ad eligibility.

## Quality bar (the 10x stack — already live)
Gemini script → editorial gate → Kokoro voice + mastering → cinematic Remotion
(Ken Burns, vignette, grain, karaoke captions) → branded logo intro.

## What to watch (analytics page)
CTR (thumbnail/title), 30-sec retention, avg view duration, RPM per niche.
Double down on the topics/angles that win; kill the rest. The `niches.topics`
pool is editable — feed winners back in.

## Growth without ad spend (you have no budget)
Paid ads cost money — skip until AdSense revenue exists. Free growth instead:
SEO titles/descriptions, Shorts volume, consistent schedule, strong thumbnails,
and Shorts→long-form funneling. Reinvest a slice of revenue into ads later.

## Sequencing
1. Quiet Capital: warm-up phase (Shorts + 1 long/wk), all dripped by date.
2. Read the analytics after ~2–3 weeks.
3. Scale cadence on winners; only then add channel #2.
