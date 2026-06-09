// Shared server-side mutation logic. Used by both the Server Actions (UI) and
// the API route handlers (programmatic callers). Runs only on the server with
// the service_role key — never imported into a client component.
import { supabaseAdmin } from "@/lib/supabase";

export async function decideContent(
  id: string,
  action: "approve" | "reject",
  reason?: string,
  approver = "dashboard",
) {
  if (!id || !["approve", "reject"].includes(action)) {
    throw new Error("id and valid action required");
  }
  const update =
    action === "approve"
      ? {
          status: "approved",
          approved_by: approver,
          approved_at: new Date().toISOString(),
          scheduled_for: new Date().toISOString(),
          reject_reason: null,
        }
      : { status: "rejected", reject_reason: reason || "rejected via dashboard" };

  const { data, error } = await supabaseAdmin()
    .from("content").update(update).eq("id", id)
    .select("id, status").single();
  if (error) throw new Error(error.message);
  return data;
}

export async function createIdea(text: string, channelId?: string | null) {
  const clean = (text || "").trim();
  if (!clean) throw new Error("idea text required");
  const { data, error } = await supabaseAdmin()
    .from("ideas").insert({ text: clean, channel_id: channelId ?? null })
    .select("*").single();
  if (error) throw new Error(error.message);
  return data;
}

export async function setIdeaStatus(id: string, status: "new" | "dismissed") {
  const { error } = await supabaseAdmin()
    .from("ideas").update({ status }).eq("id", id);
  if (error) throw new Error(error.message);
}

export interface NewChannel {
  niche_id: string; platform: string; handle: string;
  target_rpm_usd?: number | null;
  gcp_project_id?: string | null; oauth_token_ref?: string | null;
  ig_user_id?: string | null; ig_token_ref?: string | null;
}

export async function createChannel(c: NewChannel) {
  if (!c.niche_id || !c.platform || !c.handle) {
    throw new Error("niche_id, platform, handle required");
  }
  const { data, error } = await supabaseAdmin()
    .from("channels").insert({
      niche_id: c.niche_id, platform: c.platform, handle: c.handle,
      target_rpm_usd: c.target_rpm_usd ?? null,
      gcp_project_id: c.gcp_project_id ?? null,
      oauth_token_ref: c.oauth_token_ref ?? null,
      ig_user_id: c.ig_user_id ?? null, ig_token_ref: c.ig_token_ref ?? null,
    }).select("*").single();
  if (error) throw new Error(error.message);
  return data;
}
