"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Niche } from "@/lib/types";

// Add a channel by filling a form — no code change needed (modular).
export default function ChannelForm({ niches }: { niches: Niche[] }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [f, setF] = useState({
    niche_id: niches[0]?.id ?? "", platform: "youtube",
    handle: "", target_rpm_usd: "", oauth_token_ref: "", ig_user_id: "",
  });

  function set(k: string, v: string) { setF((p) => ({ ...p, [k]: v })); }

  async function submit() {
    setBusy(true); setErr(null);
    try {
      const res = await fetch("/api/channels", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...f, target_rpm_usd: f.target_rpm_usd ? Number(f.target_rpm_usd) : null,
        }),
      });
      if (!res.ok) throw new Error((await res.json()).error || `HTTP ${res.status}`);
      setOpen(false); setF({ ...f, handle: "" }); router.refresh();
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  }

  if (!open) {
    return <button className="btn btn-ghost" onClick={() => setOpen(true)}>+ Kanaal toevoegen</button>;
  }

  return (
    <div className="card p-4 space-y-3 max-w-lg">
      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs space-y-1">
          <span className="text-slate-400">Niche</span>
          <select className="w-full bg-edge rounded p-2" value={f.niche_id}
                  onChange={(e) => set("niche_id", e.target.value)}>
            {niches.map((n) => <option key={n.id} value={n.id}>{n.display_name}</option>)}
          </select>
        </label>
        <label className="text-xs space-y-1">
          <span className="text-slate-400">Platform</span>
          <select className="w-full bg-edge rounded p-2" value={f.platform}
                  onChange={(e) => set("platform", e.target.value)}>
            <option value="youtube">youtube</option>
            <option value="instagram">instagram</option>
          </select>
        </label>
        <label className="text-xs space-y-1 col-span-2">
          <span className="text-slate-400">Handle</span>
          <input className="w-full bg-edge rounded p-2" value={f.handle}
                 placeholder="@kanaal of kanaalnaam"
                 onChange={(e) => set("handle", e.target.value)} />
        </label>
        <label className="text-xs space-y-1">
          <span className="text-slate-400">RPM-doel ($)</span>
          <input className="w-full bg-edge rounded p-2" value={f.target_rpm_usd}
                 onChange={(e) => set("target_rpm_usd", e.target.value)} />
        </label>
        <label className="text-xs space-y-1">
          <span className="text-slate-400">OAuth/IG ref</span>
          <input className="w-full bg-edge rounded p-2" value={f.oauth_token_ref}
                 placeholder="token-ref"
                 onChange={(e) => set("oauth_token_ref", e.target.value)} />
        </label>
      </div>
      {err && <p className="text-xs text-rose-400">{err}</p>}
      <div className="flex gap-2">
        <button className="btn btn-approve" disabled={busy || !f.handle} onClick={submit}>
          {busy ? "..." : "Opslaan"}
        </button>
        <button className="btn btn-ghost" onClick={() => setOpen(false)}>Annuleren</button>
      </div>
    </div>
  );
}
