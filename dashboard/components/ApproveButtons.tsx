"use client";
import { useState, useTransition } from "react";
import { decideAction } from "@/app/actions";

export default function ApproveButtons({ id }: { id: string }) {
  const [pending, startTransition] = useTransition();
  const [busy, setBusy] = useState<"approve" | "reject" | null>(null);
  const [err, setErr] = useState<string | null>(null);

  function act(action: "approve" | "reject") {
    const reason =
      action === "reject" ? window.prompt("Reden van afkeuren?") || "" : "";
    setBusy(action);
    setErr(null);
    startTransition(async () => {
      try {
        await decideAction(id, action, reason);
        // revalidatePath in the action refreshes the board automatically.
      } catch (e: any) {
        setErr(e?.message ?? "fout");
      } finally {
        setBusy(null);
      }
    });
  }

  return (
    <div className="flex items-center gap-2">
      <button className="btn btn-approve disabled:opacity-50" data-testid="approve"
              disabled={pending} onClick={() => act("approve")}>
        {busy === "approve" ? "..." : "Goedkeuren"}
      </button>
      <button className="btn btn-reject disabled:opacity-50" data-testid="reject"
              disabled={pending} onClick={() => act("reject")}>
        {busy === "reject" ? "..." : "Afkeuren"}
      </button>
      {err && <span className="text-xs text-rose-400">{err}</span>}
    </div>
  );
}
