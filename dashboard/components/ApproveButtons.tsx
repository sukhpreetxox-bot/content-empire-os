"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ApproveButtons({ id }: { id: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState<"approve" | "reject" | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function act(action: "approve" | "reject") {
    setBusy(action);
    setErr(null);
    try {
      const reason =
        action === "reject" ? window.prompt("Reden van afkeuren?") || "" : "";
      const res = await fetch("/api/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, action, reason }),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.error || `HTTP ${res.status}`);
      }
      router.refresh();
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        className="btn btn-approve disabled:opacity-50"
        disabled={busy !== null}
        onClick={() => act("approve")}
        data-testid="approve"
      >
        {busy === "approve" ? "..." : "Goedkeuren"}
      </button>
      <button
        className="btn btn-reject disabled:opacity-50"
        disabled={busy !== null}
        onClick={() => act("reject")}
        data-testid="reject"
      >
        {busy === "reject" ? "..." : "Afkeuren"}
      </button>
      {err && <span className="text-xs text-rose-400">{err}</span>}
    </div>
  );
}
