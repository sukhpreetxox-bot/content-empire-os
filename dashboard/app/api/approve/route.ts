import { NextRequest, NextResponse } from "next/server";
import { decideContent } from "@/lib/mutations";

// Programmatic approve/reject endpoint (e.g. scripts). The dashboard UI uses a
// Server Action instead (app/actions.ts) so no secret ships to the browser.
// POST { id, action: "approve" | "reject", reason?, approver? }
export async function POST(req: NextRequest) {
  const secret = process.env.DASHBOARD_SECRET;
  if (secret && req.headers.get("x-dashboard-secret") !== secret) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const b = await req.json().catch(() => null);
  if (!b?.id) return NextResponse.json({ error: "id required" }, { status: 400 });
  try {
    const content = await decideContent(b.id, b.action, b.reason, b.approver);
    return NextResponse.json({ ok: true, content });
  } catch (e: any) {
    const bad = /required/.test(e?.message ?? "");
    return NextResponse.json({ error: e.message }, { status: bad ? 400 : 500 });
  }
}
