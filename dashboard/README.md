# Dashboard (Next.js)

The only human surface: review content and click **Goedkeuren / Afkeuren**.
Everything else is cron-driven. Deployable to Vercel Hobby (free).

## Pages

| Route | What |
|---|---|
| `/` | Overview: channels (YT/IG), counts (waiting for review, published). |
| `/board` | Kanban per status; **approve/reject buttons on `review` cards** with preview (title, hook, editorial angle). |
| `/channels` | Channel list + **add-channel form** (modular: no code change). |
| `/analytics` | Per-channel views/likes/RPM/revenue (filled by analytics-cron). |
| `/calendar` | Repeating schedules + upcoming/planned items. |

## API routes

- `POST /api/approve` — `{ id, action: "approve"|"reject", reason? }` → writes
  the decision to Supabase. The publication-cron only picks `approved` rows.
- `POST/PATCH /api/channels` — create / update channels.

Both honour an optional `x-dashboard-secret` header (`DASHBOARD_SECRET`).

## Data access

Server-side only via the **service_role** key (`lib/supabase.ts`), which
bypasses RLS. The key is never shipped to the browser. Swap the simple secret
gate for Supabase Auth before exposing publicly.

## Run locally

```bash
cd dashboard
npm install
cp .env.local.example .env.local     # fill SUPABASE_SERVICE_ROLE_KEY
npm run dev                          # http://localhost:3000
```

Get the service_role key at: Supabase → Project Settings → API → `service_role`.

## Deploy to Vercel

1. Import the repo, set **Root Directory** to `dashboard`.
2. Add env vars `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DASHBOARD_SECRET`.
3. Deploy. (Free Hobby tier.)
