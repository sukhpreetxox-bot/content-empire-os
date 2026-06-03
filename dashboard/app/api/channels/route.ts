import { NextRequest, NextResponse } from "next/server";
import { createChannel } from "@/lib/mutations";
import { supabaseAdmin } from "@/lib/supabase";

function auth(req: NextRequest) {
  const secret = process.env.DASHBOARD_SECRET;
  return !secret || req.headers.get("x-dashboard-secret") === secret;
}

// Programmatic channel create. POST { niche_id, platform, handle, ... }
export async function POST(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const b = await req.json().catch(() => null);
  try {
    const channel = await createChannel(b);
    return NextResponse.json({ ok: true, channel });
  } catch (e: any) {
    const bad = /required/.test(e?.message ?? "");
    return NextResponse.json({ error: e.message }, { status: bad ? 400 : 500 });
  }
}

// Update a channel. PATCH { id, ...fields }
export async function PATCH(req: NextRequest) {
  if (!auth(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const b = await req.json().catch(() => null);
  if (!b?.id) return NextResponse.json({ error: "id required" }, { status: 400 });
  const { id, ...fields } = b;
  const { data, error } = await supabaseAdmin()
    .from("channels").update(fields).eq("id", id).select("*").single();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ ok: true, channel: data });
}
