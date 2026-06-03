# Database

Single source of truth on Supabase (Postgres). Two files, run in order:

1. `schema.sql` — tables, enums, triggers, indexes, dashboard view. Idempotent.
2. `seed.sql` — the 10 niches + one starter channel each + a daily schedule. Idempotent (upserts).

## Tables

| Table | Purpose |
|---|---|
| `niches` | One row per niche. Brand identity, edge-tts voice, Remotion template + `style_props`, RPM target, **disclaimers & banned framings** (policy), topic pool. Modular: edit a row, no code change. |
| `channels` | A concrete account on a platform, bound to a niche. Holds credential **references** (GCP project, OAuth/IG token refs) — never raw tokens. |
| `content` | One row per piece moving through the kanban (`idea → … → published`). Holds script, **editorial gate** fields, asset paths, synthetic-disclosure flag, approval + publication state. |
| `analytics` | Daily snapshot per content item (views, retention, CTR, RPM, revenue). The analytics-cron writes here daily — also keeps Supabase awake. |
| `publish_schedule` | Repeating publication calendar per channel (cron expr, daily cap, timezone). |
| `v_content_board` | View joining content+channel+niche for the dashboard kanban. |

## Status flow (`content_status_t`)

```
idea → script → voice → video → review → approved → publishing → published
                                    └──→ rejected
   (any stage) → failed
```

The publication-cron only ever reads `status = 'approved'` rows (covered by a partial index).

## Notes

- `gen_random_uuid()` needs `pgcrypto` (schema enables it).
- `updated_at` is auto-maintained by triggers.
- Credentials: store tokens in Supabase Vault or `secrets/` on the VM; tables hold only `*_ref` pointers. Add RLS before exposing anything client-side.
- Re-running either file is safe.

## Verify a load

`seed.sql` ends with a `RAISE NOTICE` — expect:
```
NOTICE:  Seed complete: 10 niches, 10 channels, 10 schedules
```
