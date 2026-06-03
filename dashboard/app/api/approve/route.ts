import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

// POST { id, action: "approve" | "reject", reason?, approver? }
// Writes the human decision to Supabase. The publication-cron only ever
// picks rows that reach status 'approved'.
export async function POST(req: NextRequest) {
  const secret = process.env.DASHBOARD_SECRET;
  if (secret && req.headers.get("x-dashboard-secret") !== secret) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  let body: any;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }

  const { id, action, reason, approver } = body ?? {};
  if (!id || !["approve", "reject"].includes(action)) {
    return NextResponse.json({ error: "id and valid action required" }, { status: 400 });
  }

  const sb = supabaseAdmin();
  const update =
    action === "approve"
      ? {
          status: "approved",
          approved_by: approver || "dashboard",
          approved_at: new Date().toISOString(),
          // schedule immediately; publish-cron throttles + caps.
          scheduled_for: new Date().toISOString(),
          reject_reason: null,
        }
      : {
          status: "rejected",
          reject_reason: reason || "rejected via dashboard",
        };

  const { data, error } = await sb
    .from("content")
    .update(update)
    .eq("id", id)
    .select("id, status")
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
  return NextResponse.json({ ok: true, content: data });
}
