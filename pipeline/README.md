# Pipeline (Python)

Pure-Python orchestration, triggered by Linux cron on the Oracle VM. No n8n/Make.

## Modules

| File | Role |
|---|---|
| `config.py` | Loads `.env`, paths, rate limits. |
| `helpers/db.py` | Supabase data-access (service_role, bypasses RLS). |
| `helpers/llm.py` | **Groq primary**, Ollama fallback. `generate` / `generate_json`. |
| `helpers/editorial.py` | **Editorial-value gate**: banned-framing + substance rules, auto-disclaimers, LLM originality judge. Blocks bare recaps. |
| `helpers/tts.py` | edge-tts voiceover, per-niche voice/rate/pitch. |
| `helpers/pexels.py` | Royalty-free B-roll fetch + credits. |
| `helpers/ffmpeg.py` | Assembly: concat B-roll, mux audio, grab thumbnail. |
| `helpers/youtube.py` | YouTube Data API upload, per-channel OAuth, synthetic disclosure. |
| `helpers/instagram.py` | IG Graph API Reels publish (container → publish), AI label. |

## Cron jobs

| Script | When | Does |
|---|---|---|
| `gen_cron.py` | daily AM | idea→script→**gate**→voice→video→thumbnail, writes `status='review'` |
| `publish_cron.py` | hourly 08-20 | picks `approved` & due → upload (throttled, capped) → `published` → plan next |
| `analytics_cron.py` | daily PM | pull YT/IG stats → `analytics`; keep Supabase awake |

`crontab.txt` wires all of it. Install on the VM with `crontab pipeline/crontab.txt`.

## Run locally / on the VM

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
sudo apt-get install -y ffmpeg          # system binary
cp .env.example .env                     # then fill secrets
python pipeline/gen_cron.py --platform youtube
```

## Honest notes

- **Synthetic-media disclosure**: the YouTube Data API does not yet expose a
  settable "altered/synthetic" field — we record it in the description and keep
  a code hook for when it lands. It is *not* auto-set via API. See
  `helpers/youtube.py` docstring.
- **IG publishing** needs the rendered MP4 at a public HTTPS URL
  (`content.meta.public_video_url`) — wire Supabase Storage or a temp host.
- Editorial gate **fails closed**: if the judge errors, the draft is blocked
  rather than published, to protect against policy violations.
- Video currently uses the FFmpeg fallback (B-roll + voiceover). Branded
  per-niche Remotion templates come in Layer 2 and slot into `render_video()`.
