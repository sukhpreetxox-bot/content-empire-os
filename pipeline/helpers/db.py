"""Supabase data-access layer.

Uses the service_role key, which bypasses RLS — keep this server-side only.
Thin wrappers around the queries the cron jobs actually need, so the crons
stay readable and the table/column names live in one place.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


def client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set in .env")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


_sb: Client | None = None


def db() -> Client:
    global _sb
    if _sb is None:
        _sb = client()
    return _sb


# --- Niches & channels ------------------------------------------------------
def get_active_channels(platform: str | None = None) -> list[dict]:
    q = db().table("channels").select("*, niches(*)").eq("is_active", True)
    if platform:
        q = q.eq("platform", platform)
    return q.execute().data or []


def get_niche(niche_id: str) -> dict | None:
    r = db().table("niches").select("*").eq("id", niche_id).limit(1).execute()
    return (r.data or [None])[0]


# --- Content ----------------------------------------------------------------
def create_content(channel_id: str, **fields) -> dict:
    payload = {"channel_id": channel_id, **fields}
    return db().table("content").insert(payload).execute().data[0]


def update_content(content_id: str, **fields) -> dict:
    return (
        db().table("content").update(fields).eq("id", content_id).execute().data[0]
    )


def get_content(content_id: str) -> dict | None:
    r = db().table("content").select("*").eq("id", content_id).limit(1).execute()
    return (r.data or [None])[0]


def get_publishable(now: datetime | None = None) -> list[dict]:
    """Approved rows whose scheduled_for is due (or null)."""
    now = now or datetime.now(timezone.utc)
    rows = (
        db().table("content").select("*, channels(*, niches(*))")
        .eq("status", "approved").execute().data or []
    )
    due = []
    for r in rows:
        sf = r.get("scheduled_for")
        if not sf or datetime.fromisoformat(sf.replace("Z", "+00:00")) <= now:
            due.append(r)
    return due


def count_published_today(channel_id: str) -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    r = (
        db().table("content").select("id", count="exact")
        .eq("channel_id", channel_id).eq("status", "published")
        .gte("published_at", f"{today}T00:00:00Z").execute()
    )
    return r.count or 0


# --- Analytics --------------------------------------------------------------
def get_published_content(channel_id: str | None = None) -> list[dict]:
    q = db().table("content").select("*").eq("status", "published")
    if channel_id:
        q = q.eq("channel_id", channel_id)
    return q.execute().data or []


def upsert_analytics(row: dict[str, Any]) -> None:
    # unique (content_id, snapshot_date)
    db().table("analytics").upsert(row, on_conflict="content_id,snapshot_date").execute()


# --- Schedule ---------------------------------------------------------------
def get_schedule(channel_id: str) -> dict | None:
    r = (
        db().table("publish_schedule").select("*")
        .eq("channel_id", channel_id).eq("is_active", True).limit(1).execute()
    )
    return (r.data or [None])[0]


def touch_keepalive() -> None:
    """Cheap write to keep the Supabase free-tier project from pausing."""
    db().table("niches").update({"updated_at": datetime.now(timezone.utc).isoformat()}) \
        .eq("slug", "quiet-capital").execute()
