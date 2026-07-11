# 🧭 HANDOFF — Content Empire OS / Quiet Capital (resume here)

Self-contained state so a NEW chat (no memory) can continue. Last updated by
the build session. Project lives at `~/Desktop/Diversen/ContentEmpire` (its own
git repo) and on GitHub: **github.com/sukhpreetxox-bot/content-empire-os**.

---

## 0. PASTE THIS INTO A NEW CHAT TO RESUME
> I'm continuing the **Content Empire OS** project at
> `~/Desktop/Diversen/ContentEmpire` (own git repo; remote
> `sukhpreetxox-bot/content-empire-os`). It's a free, fully automated faceless
> YouTube pipeline for ONE channel: **Quiet Capital** — *inner development /
> self-mastery* (NOT finance; "capital" = attention, character, sovereignty).
> Read `docs/HANDOFF.md` first, then `docs/COMMAND-CENTER.md`. Use `git -C
> ~/Desktop/Diversen/ContentEmpire` for git (the home dir is also a git repo —
> never run bare git). Secrets are in `.env` (gitignored) + GitHub Secrets.
> Continue from "Open action items" in the handoff.

---

## 1. WHAT IT IS
Idea → Gemini script → editorial gate → Kokoro voice (am_onyx) + mastering →
Cloudflare FLUX AI scene images → royalty-free music → Whisper word-captions →
animated brand intro/outro → Remotion render → Supabase Storage → YouTube
upload (public) → analytics → self-steers (winners → ideas inbox). 100% free.

Human step = approve/reject on the dashboard. Everything else is automated.

## 2. ACCESS
| What | Where |
|---|---|
| **Dashboard** | https://content-empire-ashy.vercel.app · password **`quietcapital`** (any username) |
| Dashboard pages | Overzicht · 💡 Ideeën (type topics) · Content-board (approve) · Analytics · Kalender |
| **GitHub** | github.com/sukhpreetxox-bot/content-empire-os (gh CLI authed as sukhpreetxox-bot) |
| **Actions** | …/actions — generate (daily Shorts + Mon/Thu deep), publish (hourly), analytics (daily) |
| **Supabase** | project `dfzuiuhzgeizdnppvjvd` (eu-west-2) — MCP available |
| **Vercel** | project `content-empire`, scope `sukhpreetxox-1507s-projects` |
| **YouTube** | channel "Quiet Capital" on account **quietcapital903@gmail.com** |

## 3. KEYS (in `.env` locally + GitHub Secrets) — ⚠️ ROTATE (shared in chat)
GEMINI_API_KEY, GROQ_API_KEY, PEXELS_API_KEY, POLLINATIONS_TOKEN,
CF_ACCOUNT_ID + CF_API_TOKEN (Cloudflare Workers AI = primary free images),
SUPABASE_SERVICE_ROLE_KEY, DASHBOARD_SECRET=quietcapital,
Vercel token (in local `.env` + GitHub Secret `VERCEL_TOKEN` — never inline here),
YouTube OAuth token at `secrets/youtube/quiet-capital.json` (scopes: upload +
youtube manage + yt-analytics.readonly) — also GH secret `YOUTUBE_TOKENS_B64`.

## 4. CURRENT STATE (as of handoff)
- Channel **Quiet Capital**: **0 subs, ~79 views, 23 public videos**, 0 likes (day one, no promotion).
- Winning theme in data: **attention / stillness / avoidance** (top: "The Invisible Labor of Stillness" 22 views). Lean here.
- Voice: **am_onyx** (deep). Identity: Inner Development & Self-Mastery. Only Quiet Capital channel active.
- Formats: `short` (22-35s, hook-first, loopable), `long` (~90s), `deep` (8+ min, mid-roll/revenue, Stoic-anchored).
- Brand: animated logo intro (self-draws) + corner bug + outro CTA on every landscape video; Shorts hook-first.
- Self-steering analytics live (winners → ideas inbox).
- Background batches may have been generating more review items — check the dashboard board.

## 5. HOW TO OPERATE (daily)
1. Dashboard → **Content-board** → approve the 2-3 best → they auto-upload **public** (cap ~5/day, YouTube quota).
2. **💡 Ideeën** page → type topics (the generator uses the oldest unused one first).
3. Cadence runs itself: daily Shorts + Mon/Thu deep.

Commands (terminal):
```bash
gh workflow run generate.yml -f format=short   # or long | deep
gh workflow run publish.yml                    # upload approved
gh run list --workflow=generate.yml --limit 5
# new channel OAuth: .venv/bin/python pipeline/tools/youtube_auth.py <client.json> <ref>
```
Generate locally (any format), uses full premium stack:
`.venv/bin/python -c "import sys;sys.path.insert(0,'pipeline');from helpers import db;import gen_cron;ch=[c for c in db.get_active_channels('youtube') if c['handle']=='Quiet Capital'][0];gen_cron.generate_for_channel(ch, fmt='short')"`

## 6. OPEN ACTION ITEMS (only you can do)
1. **Brand the YouTube channel** — Studio → Customization → avatar = `assets/brand/quiet-capital-avatar.png`, banner, name "Quiet Capital", handle @quietcapital, "About" persona. (HIGHEST priority.)
2. **Enable "YouTube Analytics API"** in GCP project `ce-quiet-capital` → unlocks watch-time/retention.
3. **Repo public** (unlimited free CI): `gh repo edit sukhpreetxox-bot/content-empire-os --visibility public --accept-visibility-change-consequences`
4. **2FA + AdSense** on the Google account (for payout later).
5. Claim @quietcapital on Instagram (optional, later).

## 7. THE HONEST READ
The machine is complete and excellent. The channel is day-one: 0 subs.
Monetization = **1,000 subs + 4,000 watch hours** (or 10M Shorts views/90d),
then ~$5-12 RPM on long-form, payout at $100. Realistic: **6-18 months**
without a breakout. Constraint is NOT content volume — it's subs/engagement +
branding + consistency. Don't bulk-dump; let the daily cadence drip. Lean into
the winning "attention/stillness" vein. Push engagement (scripts now close with
a question).

## 8. DOCS INDEX
`COMMAND-CENTER.md` (controls) · `STRATEGY.md` (cadence/calendar) ·
`MONETIZATION.md` (YPP rules) · `CONTENT-REVIEW.md` (what earns) ·
`TOOL-MAP.md` (free tools) · `SETUP.md` (accounts) · `PROJECTION.md` if present.

## 9. PIPELINE MAP (code)
`pipeline/gen_cron.py` (orchestrator) · `helpers/`: llm (Gemini→Groq→Ollama),
editorial (gate), tts (Kokoro+master), images (Cloudflare→Pollinations→Pexels),
audio (music+master), transcribe (Whisper), trends, storage, remotion, youtube,
instagram · `helpers/cloudflare.py`, `pollinations.py` · `pipeline/tools/`:
youtube_auth, fetch_music, test_upload · `remotion/src/` (Brand, Outro,
BrandMark, Captions, SceneImages, NicheVideo) · `dashboard/` (Next.js, Vercel) ·
DB tables: niches, channels, content, analytics, publish_schedule, ideas.
Local: `.venv` (python), `models/` (Kokoro), ffmpeg via brew.
