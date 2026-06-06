-- ============================================================================
-- Content Empire OS  --  Supabase / Postgres schema
-- ----------------------------------------------------------------------------
-- Single source of truth for channels, niches, content pipeline state and
-- ALL analytics. Designed for the Supabase free tier.
--
-- Idempotent: safe to re-run. Run with:
--   psql "$SUPABASE_DB_URL" -f db/schema.sql
-- or paste into the Supabase SQL editor.
-- ============================================================================

-- Needed for gen_random_uuid()
create extension if not exists "pgcrypto";

-- ----------------------------------------------------------------------------
-- ENUMS
-- ----------------------------------------------------------------------------
do $$ begin
  create type platform_t as enum ('youtube', 'instagram');
exception when duplicate_object then null; end $$;

do $$ begin
  -- The content kanban stages. Order matters for the dashboard board.
  create type content_status_t as enum (
    'idea',          -- Idee
    'script',        -- Script
    'voice',         -- Voiceover gerenderd
    'video',         -- Video + thumbnail gerenderd
    'review',        -- Klaar voor review  (wacht op mens)
    'approved',      -- Goedgekeurd        (mag publiceren)
    'rejected',      -- Afgekeurd          (terug naar idee of dood)
    'publishing',    -- Upload bezig
    'published',     -- Gepubliceerd
    'failed'         -- Fout in pipeline / upload
  );
exception when duplicate_object then null; end $$;

-- ----------------------------------------------------------------------------
-- updated_at trigger helper
-- ----------------------------------------------------------------------------
create or replace function set_updated_at() returns trigger
  language plpgsql
  set search_path = ''   -- pin search_path (prevents hijacking; advisor 0011)
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ============================================================================
-- NICHES  --  one row per niche. Editing a niche = no code change (modular).
-- ============================================================================
create table if not exists niches (
  id              uuid primary key default gen_random_uuid(),
  slug            text unique not null,              -- e.g. 'quiet-capital'
  display_name    text not null,                     -- 'Quiet Capital'
  platform        platform_t not null,
  category        text not null,                     -- 'Personal Finance & Investing'
  -- Editorial / brand identity
  tone            text not null,                     -- 'kalme autoritaire stem'
  audience        text,                              -- target audience description
  visual_style    text,                              -- 'Donker navy + goud, animated charts'
  -- Voice: Kokoro is primary (kokoro_voice/speed); edge-tts is the fallback.
  kokoro_voice    text,                              -- e.g. 'am_michael'
  kokoro_speed    numeric(4,2) not null default 1.0,
  image_style     text,                              -- per-niche AI image prompt style
  tts_voice       text not null default 'en-US-GuyNeural',  -- edge-tts fallback
  tts_rate        text not null default '+0%',
  tts_pitch       text not null default '+0Hz',
  -- Remotion: which visual template + a free-form props blob (colors, fonts...)
  remotion_template text not null default 'GenericTemplate',
  style_props     jsonb not null default '{}'::jsonb,
  -- Economics & policy
  target_rpm_usd  numeric(6,2),                      -- expected RPM, for analytics
  cadence         text not null default 'daily',     -- 'daily' | 'weekly' | cron-ish
  -- Guardrails the editorial-value step must enforce for this niche
  required_disclaimers text[] not null default '{}', -- e.g. {'Not financial advice'}
  banned_framings text[] not null default '{}',      -- e.g. {'get rich quick'}
  topics          text[] not null default '{}',      -- seed topic pool
  is_active        boolean not null default true,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
drop trigger if exists trg_niches_updated on niches;
create trigger trg_niches_updated before update on niches
  for each row execute function set_updated_at();

-- ============================================================================
-- CHANNELS  --  a concrete account on a platform, bound to a niche.
--   Add/edit a channel = one form row in the dashboard, no code change.
-- ============================================================================
create table if not exists channels (
  id                uuid primary key default gen_random_uuid(),
  niche_id          uuid not null references niches(id) on delete restrict,
  platform          platform_t not null,
  handle            text not null,                   -- '@thequietascent' / channel name
  -- Per-channel overrides (fall back to niche defaults when null)
  tone_override     text,
  cadence_override  text,
  target_rpm_usd    numeric(6,2),
  -- Credentials live in secrets / per-channel rows. We store only references,
  -- never raw tokens in plaintext app code. (RLS + Supabase Vault recommended.)
  gcp_project_id    text,                            -- YouTube: own GCP project
  youtube_channel_id text,
  oauth_token_ref   text,                            -- key into secrets store
  ig_user_id        text,                            -- Instagram Graph API user id
  ig_token_ref      text,
  is_active          boolean not null default true,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now(),
  unique (platform, handle)
);
drop trigger if exists trg_channels_updated on channels;
create trigger trg_channels_updated before update on channels
  for each row execute function set_updated_at();

create index if not exists idx_channels_niche on channels(niche_id);
create index if not exists idx_channels_active on channels(is_active);

-- ============================================================================
-- CONTENT  --  one row per piece of content moving through the pipeline.
-- ============================================================================
create table if not exists content (
  id              uuid primary key default gen_random_uuid(),
  channel_id      uuid not null references channels(id) on delete cascade,
  status          content_status_t not null default 'idea',
  format          text not null default 'long',      -- 'long' (16:9) | 'short' (9:16)
  -- Generated artefacts
  title           text,
  hook            text,                              -- opening line / hook
  script          text,                              -- full narration script
  topic           text,
  -- Editorial-value gate (policy-safe). Must pass before reaching 'review'.
  editorial_angle text,                              -- the unique POV/analysis
  editorial_passed boolean not null default false,
  editorial_notes text,
  -- Asset paths (on the Oracle VM filesystem) and/or remote URLs
  voiceover_path  text,
  video_path      text,
  thumbnail_path  text,
  broll_credits   jsonb not null default '[]'::jsonb,-- Pexels attribution
  -- Synthetic-media disclosure (YouTube "Altered or Synthetic")
  synthetic_disclosure boolean not null default true,
  -- Human approval gate
  approved_by     text,
  approved_at     timestamptz,
  reject_reason   text,
  -- Publication
  published_url   text,
  published_at    timestamptz,
  scheduled_for   timestamptz,                       -- next slot in repeating calendar
  -- Diagnostics
  error_message   text,
  meta            jsonb not null default '{}'::jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
drop trigger if exists trg_content_updated on content;
create trigger trg_content_updated before update on content
  for each row execute function set_updated_at();

create index if not exists idx_content_channel on content(channel_id);
create index if not exists idx_content_status on content(status);
create index if not exists idx_content_scheduled on content(scheduled_for);
-- Fast lookup for the publication-cron: approved + due
create index if not exists idx_content_publishable
  on content(status, scheduled_for) where status = 'approved';

-- ============================================================================
-- ANALYTICS  --  daily snapshots per content item. The analytics-cron also
--   keeps the Supabase free-tier project awake by writing here every day.
-- ============================================================================
create table if not exists analytics (
  id              uuid primary key default gen_random_uuid(),
  content_id      uuid not null references content(id) on delete cascade,
  channel_id      uuid not null references channels(id) on delete cascade,
  snapshot_date   date not null default current_date,
  views           bigint not null default 0,
  likes           bigint not null default 0,
  comments        bigint not null default 0,
  shares          bigint not null default 0,
  -- YouTube specifics
  avg_view_duration_s numeric,
  retention_pct   numeric(5,2),
  ctr_pct         numeric(5,2),
  estimated_rpm_usd numeric(6,2),
  estimated_revenue_usd numeric(10,2),
  raw             jsonb not null default '{}'::jsonb,
  created_at      timestamptz not null default now(),
  unique (content_id, snapshot_date)
);
create index if not exists idx_analytics_channel_date on analytics(channel_id, snapshot_date);

-- ============================================================================
-- PUBLISH_SCHEDULE  --  the repeating publication calendar per channel.
-- ============================================================================
create table if not exists publish_schedule (
  id              uuid primary key default gen_random_uuid(),
  channel_id      uuid not null references channels(id) on delete cascade,
  -- Cron-style recurrence; pipeline reads this to plan the next slot.
  cron_expr       text not null default '0 14 * * *', -- daily 14:00 UTC
  timezone        text not null default 'UTC',
  daily_cap       int not null default 1,             -- throttle: max posts/day
  is_active        boolean not null default true,
  last_planned_at timestamptz,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
drop trigger if exists trg_schedule_updated on publish_schedule;
create trigger trg_schedule_updated before update on publish_schedule
  for each row execute function set_updated_at();
create index if not exists idx_schedule_channel on publish_schedule(channel_id);

-- ============================================================================
-- Convenience view: full kanban join for the dashboard.
-- ============================================================================
create or replace view v_content_board as
select
  c.id,
  c.status,
  c.title,
  c.hook,
  c.scheduled_for,
  c.editorial_passed,
  c.thumbnail_path,
  c.video_path,
  ch.handle      as channel_handle,
  ch.platform,
  n.display_name as niche,
  n.slug         as niche_slug,
  c.updated_at
from content c
join channels ch on ch.id = c.channel_id
join niches  n  on n.id  = ch.niche_id;

-- ============================================================================
-- SECURITY HARDENING
--   RLS enabled on every table with NO policies = deny-all for anon/public.
--   The Python pipeline and Next.js API routes use the service_role key,
--   which bypasses RLS. Add granular policies only if you expose the anon key.
-- ============================================================================
alter table niches            enable row level security;
alter table channels          enable row level security;
alter table content           enable row level security;
alter table analytics         enable row level security;
alter table publish_schedule  enable row level security;

-- View runs with the querying user's permissions (not the creator's).
alter view v_content_board set (security_invoker = on);

-- ============================================================================
-- DONE. Run db/seed.sql next to load the 10 niches + channels.
-- ============================================================================
