import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

function auth(req: NextRequest) {
  const secret = process.env.DASHBOARD_SECRET;
  return !secret || req.headers.get("x-dashboard-secret") === secret;
}

// Create a channel.  POST { niche_id, platform, handle, target_rpm_usd?, ... }
export async function POST(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const b = await req.json().catch(() => null);
  if (!b?.niche_id || !b?.platform || !b?.handle) {
    return NextResponse.json({ error: "niche_id, platform, handle required" }, { status: 400 });
  }
  const sb = supabaseAdmin();
  const { data, error } = await sb.from("channels").insert({
    niche_id: b.niche_id, platform: b.platform, handle: b.handle,
    target_rpm_usd: b.target_rpm_usd ?? null,
    gcp_project_id: b.gcp_project_id ?? null,
    oauth_token_ref: b.oauth_token_ref ?? null,
    ig_user_id: b.ig_user_id ?? null, ig_token_ref: b.ig_token_ref ?? null,
  }).select("*").single();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, channel: data });
}

// Update a channel.  PATCH { id, ...fields }
export async function PATCH(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const b = await req.json().catch(() => null);
  if (!b?.id) return NextResponse.json({ error: "id required" }, { status: 400 });
  const { id, ...fields } = b;
  const sb = supabaseAdmin();
  const { data, error } = await sb.from("channels").update(fields).eq("id", id)
    .select("*").single();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, channel: data });
}
