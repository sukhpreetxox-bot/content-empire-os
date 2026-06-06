# 🎛️ Content Empire OS — Command Center

## 🔗 Access
| Wat | Waar |
|---|---|
| **Dashboard** (approve/reject) | https://content-empire-ashy.vercel.app |
| Dashboard login | gebruiker: *willekeurig* · wachtwoord: `ce_8Qz3kRt9vWxL2mNp7sBd4hYf6JcG1aUe` |
| **Code (GitHub)** | https://github.com/sukhpreetxox-bot/content-empire-os |
| **Actions** (de motor) | https://github.com/sukhpreetxox-bot/content-empire-os/actions |
| **Supabase** (database) | project `dfzuiuhzgeizdnppvjvd` (eu-west-2) |
| **Vercel** (dashboard host) | project `content-empire` |

## 🤖 De motor (GitHub Actions, gratis)
| Workflow | Schema | Doet |
|---|---|---|
| `generate` | dagelijks 07:00 UTC | idee → script (Gemini) → gate → Kokoro-stem → render → review |
| `publish` | elk uur 08–20 UTC | uploadt goedgekeurde items (unlisted) |
| `analytics` | dagelijks 23:00 UTC | stats + Supabase wakker |

## ⌨️ Knoppen (terminal-commando's)
```bash
# Nu content genereren (handmatig)
gh workflow run generate.yml -f platform=youtube

# Nu publiceren (goedgekeurde items)
gh workflow run publish.yml

# Status van runs
gh run list --workflow=generate.yml --limit 5

# Nieuw YouTube-kanaal koppelen (na OAuth-client downloaden)
.venv/bin/python pipeline/tools/youtube_auth.py ~/Downloads/client_secret_X.json <ref>

# Logo opnieuw renderen
.venv/bin/python assets/brand/make_logo.py

# Repo public maken (= onbeperkte gratis compute)
gh repo edit sukhpreetxox-bot/content-empire-os --visibility public --accept-visibility-change-consequences
```

## 🎚️ Instellingen (zonder code)
- **Publicatie-privacy**: `PUBLISH_PRIVACY` in `.github/workflows/publish.yml` (`unlisted` → `public`).
- **Stem per niche**: rij in Supabase-tabel `niches` (`kokoro_voice`, `kokoro_speed`).
- **Niche/disclaimers/topics**: rij in `niches`.
- **Schema/cadans**: tabel `publish_schedule`.
- **Muziek**: drop tracks in `assets/music/<mood>/`.

## ✅ Status
- 🎙️ Kokoro-stem + mastering · 🎬 cinematic visuals · ✍️ Gemini-script · 🎨 logo — **live**
- ▶️ YouTube **Quiet Capital** gekoppeld, eerste video unlisted geüpload
- ⏳ Te doen door jou: muziektracks · repo public · extra kanalen (OAuth)

## 🔑 Secrets (waar ze staan)
GitHub Secrets: `SUPABASE_*`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `PEXELS_API_KEY`, `YOUTUBE_TOKENS_B64`.
Lokaal: `.env` (pipeline) · `dashboard/.env.local` (dashboard). **Roteer de keys die in chat gedeeld zijn.**
