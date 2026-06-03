# Content Empire OS — Setup Guide (no coding required)

This walks you, click by click, from nothing to a running system. Budget
**2–4 hours** the first time (most of it is creating accounts and waiting for
approvals). You only ever do this **once**.

Legend: 🟢 = already done for you · ⏱️ = waiting/approval step · 🔑 = produces a secret you paste into `.env`.

## Overview of what you'll set up

| # | Thing | Free tier | Why |
|---|---|---|---|
| 1 | Oracle Cloud VM | Always Free | runs everything 24/7 |
| 2 | Supabase 🟢 | Free | database (already created) |
| 3 | Groq API key 🔑 | Free | writes the scripts |
| 4 | Pexels API key 🔑 | Free | royalty-free B-roll |
| 5 | Google Cloud ×5 🔑 | Free | upload to 5 YouTube channels |
| 6 | Instagram/Meta ×5 🔑 | Free | publish to 5 IG accounts |
| 7 | Vercel | Hobby (free) | hosts the dashboard |

> You can get the system **fully working for YouTube first** and add Instagram
> later — sections 5 and 6 are independent.

---

## 1. Oracle Cloud Always Free VM

This is the always-on computer that runs the cron jobs.

1. Go to <https://www.oracle.com/cloud/free/> → **Start for free**. Sign up
   (needs a card for identity check — **Always Free resources are never
   charged**; do not upgrade to Pay As You Go if you want to stay free).
2. In the console: **Menu → Compute → Instances → Create Instance**.
3. Settings:
   - **Image**: Canonical Ubuntu 22.04
   - **Shape**: **Ampere (ARM) — VM.Standard.A1.Flex**, set **4 OCPU / 24 GB**
     (this is the full Always Free allowance).
   - **Networking**: keep "Assign a public IPv4 address" = yes.
   - **SSH keys**: choose **Generate a key pair for me** and **download both**
     the private and public key. Keep the **private** key safe.
4. Click **Create**. ⏱️ Wait ~2 min until it's **Running**. Note the
   **Public IP address**.
5. **Open the firewall for nothing inbound except SSH** (default is fine). The
   pipeline makes only outbound calls, so no extra ports needed. (If you later
   serve IG videos from the VM, you'll open one port — see section 6 note.)

> ⚠️ If the A1 (ARM) shape says "out of capacity", try a different
> Availability Domain or retry later — ARM capacity is in demand. An AMD
> **VM.Standard.E2.1.Micro** (1 CPU / 1 GB, also Always Free) works too but
> renders videos slower.

### Connect and install dependencies

From your computer's terminal (replace the path and IP):

```bash
chmod 600 ~/Downloads/your-private-key.key
ssh -i ~/Downloads/your-private-key.key ubuntu@YOUR_VM_IP
```

Once logged in, paste this block (installs everything the pipeline needs):

```bash
sudo apt-get update && sudo apt-get install -y \
  python3 python3-venv python3-pip ffmpeg git curl
# Node 20 (for Remotion renders, optional on the VM)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
# (Optional) local LLM fallback. Groq is primary, so this is not required:
# curl -fsSL https://ollama.com/install.sh | sh && ollama pull llama3
```

> 💡 **I (Claude) can do this step for you** later via SSH if you give me the
> VM IP + private key — that's "Layer 5: deploy". For now just get the VM
> running.

---

## 2. Supabase 🟢 (already done)

Your project `dfzuiuhzgeizdnppvjvd` is live with the full schema, the 10
niches, RLS security, and a daily keep-alive. You only need two values from it:

- **Project URL**: `https://dfzuiuhzgeizdnppvjvd.supabase.co`
- 🔑 **service_role key**: Supabase → **Project Settings → API → Project API
  keys → `service_role`** → Reveal/Copy. (Keep this secret — it bypasses all
  security. Used only server-side.)

---

## 3. Groq API key 🔑 (script generation)

1. Go to <https://console.groq.com> → sign in (free).
2. **API Keys → Create API Key** → copy it.
3. This is your `GROQ_API_KEY`. Free tier has generous daily limits; the
   pipeline throttles to stay within them.

---

## 4. Pexels API key 🔑 (B-roll)

1. Go to <https://www.pexels.com/api/> → **Get Started** → sign in.
2. Copy **Your API Key**. This is `PEXELS_API_KEY`.

---

## 5. YouTube: 5 × Google Cloud project + OAuth 🔑

YouTube allows ~6 uploads/day per Google Cloud project. **One project per
channel** keeps each channel within its own quota. Repeat 5 times (or start
with 1 and add more later).

**For each YouTube channel:**

1. <https://console.cloud.google.com> → top bar **project dropdown → New
   Project** → name it e.g. `ce-quiet-capital` → Create.
2. **APIs & Services → Library** → search **"YouTube Data API v3"** → **Enable**.
3. **APIs & Services → OAuth consent screen**:
   - User type: **External** → Create.
   - App name, your email, developer email → Save and continue.
   - **Scopes**: add `.../auth/youtube.upload` → Save.
   - **Test users**: add the Google account that owns this YouTube channel.
   - Leave it in **Testing** mode (fine for your own uploads).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app** → Create.
   - **Download JSON**. Rename it to `client_secret_ce-quiet-capital.json`
     (use the project id you chose) and put it in `secrets/youtube/` on the VM.
5. Note the **project id**; you'll set it on the channel row (dashboard →
   Kanalen → the channel's `gcp_project_id`) and pick an `oauth_token_ref`
   (any short label, e.g. `quiet-capital`).

⏱️ **First-time OAuth consent** (once per channel): run the helper on the VM,
which opens a one-time login link:

```bash
cd ~/ContentEmpire && source .venv/bin/activate
python -c "from pipeline.helpers.youtube import _credentials; _credentials('quiet-capital','client_secret_ce-quiet-capital.json')"
```

Approve in the browser; a token file `secrets/youtube/quiet-capital.json` is
saved and reused forever after.

> Repeat 1–5 for: quiet-capital, leverage-lab, plain-law, coherent, lights-off.

---

## 6. Instagram: 5 × Business account + Meta app 🔑

The Instagram Graph API only publishes from **Business/Creator** accounts
linked to a **Facebook Page**.

**One-time Meta app (covers all 5 IG accounts):**

1. Convert each IG account to **Business** or **Creator** (IG app → Settings →
   Account type and tools) and **link it to a Facebook Page** (IG → Settings →
   Linked accounts / Page).
2. <https://developers.facebook.com> → **My Apps → Create App** → type
   **Business** → name it `ContentEmpire`.
3. Add the **Instagram Graph API** product.
4. **App settings → Basic**: copy **App ID** (`IG_APP_ID`) and **App Secret**
   (`IG_APP_SECRET`).
5. Use the **Graph API Explorer** (or the Access Token Tool) to generate a
   **long-lived Page/IG access token** with permissions:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `business_management`. Exchange it for a long-lived token (≈60 days; the
   analytics cron's usage keeps it warm — refresh before expiry).
6. For each IG account, get its **IG user id** (Graph Explorer:
   `GET /me/accounts` → page → `instagram_business_account`).
7. On the VM, save each token to `secrets/instagram/<ref>.txt` (e.g.
   `quiet-ascent.txt`) and set the channel's `ig_user_id` + `ig_token_ref`
   in the dashboard.

> 📝 **Public video URL**: IG fetches the video from a public HTTPS URL. The
> simplest free option is to upload the rendered MP4 to **Supabase Storage**
> (public bucket) and store that URL in `content.meta.public_video_url`. A
> helper for this can be added in a later layer — tell me when you reach IG.

---

## 7. Vercel: deploy the dashboard (free)

1. Push this repo to GitHub (or let me do it).
2. <https://vercel.com> → **Add New → Project** → import the repo.
3. **Root Directory**: set to `dashboard`.
4. **Environment Variables** (Settings → Environment Variables):
   - `SUPABASE_URL` = `https://dfzuiuhzgeizdnppvjvd.supabase.co`
   - `SUPABASE_SERVICE_ROLE_KEY` = (from section 2)
   - `DASHBOARD_SECRET` = a long random string
5. **Deploy**. You'll get a URL like `https://content-empire.vercel.app`.

> 🔒 The dashboard currently has no login. Before using the public Vercel URL,
> enable **Vercel Authentication** (Project → Settings → Deployment Protection)
> or add Supabase Auth, so only you can approve content.

---

## 8. Put the secrets on the VM and schedule the crons

On the VM:

```bash
cd ~ && git clone YOUR_REPO_URL ContentEmpire && cd ContentEmpire
python3 -m venv .venv && source .venv/bin/activate
pip install -r pipeline/requirements.txt
mkdir -p secrets/youtube secrets/instagram logs
cp .env.example .env && nano .env     # paste all the keys from sections 2–6
crontab pipeline/crontab.txt          # schedules generation/publish/analytics
```

`.env` fields and where each came from are documented in `.env.example`.

---

## 9. Daily life (the only thing you do)

1. The **generation cron** runs each morning → new drafts appear on the
   dashboard **Board** in the **"Klaar voor review"** column, already past the
   editorial-value gate.
2. You open the dashboard, read the script + angle, watch the preview, and
   click **Goedkeuren** or **Afkeuren**.
3. The **publication cron** picks up approved items during the day, uploads
   them (throttled, with synthetic-media disclosure), and schedules the next.
4. The **analytics cron** fills the Analytics page nightly.

That's it — one click per piece. Everything else is automatic.

---

## Free-tier guardrails (already enforced in code)

- YouTube: ≤5 uploads/day/project, separate project per channel.
- Instagram: well under 25 posts/24h/account.
- Supabase: daily keep-alive write prevents the 7-day pause.
- Assets: only Pexels (royalty-free) or fresh AI — avoids Content ID strikes.
- Editorial gate blocks bare recaps / banned framings; disclaimers auto-added.

## Honest expectations

- Large-scale faceless AI channels carry **real demonetisation/ban risk** on
  YouTube and Meta even with these safeguards. Start small, watch what gets
  traction, and treat the guardrails as risk-reduction, not a guarantee.
- The first videos use plain B-roll + voiceover; branded per-niche visuals
  come with the Remotion layer.
