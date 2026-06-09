"use server";
// Server Actions for the dashboard UI. These run on the server (service_role,
// CSRF-protected by Next) so no secret is ever shipped to the browser.
import { revalidatePath } from "next/cache";
import * as m from "@/lib/mutations";

export async function decideAction(
  id: string, action: "approve" | "reject", reason?: string,
) {
  const r = await m.decideContent(id, action, reason);
  revalidatePath("/board");
  revalidatePath("/");
  return r;
}

export async function createChannelAction(input: m.NewChannel) {
  const r = await m.createChannel(input);
  revalidatePath("/channels");
  revalidatePath("/");
  return r;
}

export async function createIdeaAction(text: string, channelId?: string | null) {
  const r = await m.createIdea(text, channelId);
  revalidatePath("/ideas");
  revalidatePath("/");
  return r;
}

export async function dismissIdeaAction(id: string) {
  await m.setIdeaStatus(id, "dismissed");
  revalidatePath("/ideas");
}
