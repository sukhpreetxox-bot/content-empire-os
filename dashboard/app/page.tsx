import Link from "next/link";
import { supabaseAdmin } from "@/lib/supabase";
import { Channel } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function Overview() {
  const sb = supabaseAdmin();
  const [{ data: channels }, { count: reviewCount }, { count: pubCount }] =
    await Promise.all([
      sb.from("channels").select("*, niches(*)").order("created_at"),
      sb.from("content").select("id", { count: "exact", head: true }).eq("status", "review"),
      sb.from("content").select("id", { count: "exact", head: true }).eq("status", "published"),
    ]);

  const chs = (channels ?? []) as Channel[];
  const yt = chs.filter((c) => c.platform === "youtube");
  const ig = chs.filter((c) => c.platform === "instagram");

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        <Stat label="Kanalen" value={chs.length} />
        <Stat label="Wacht op review" value={reviewCount ?? 0}
              href="/board" accent />
        <Stat label="Gepubliceerd" value={pubCount ?? 0} />
      </div>

      <Section title={`YouTube (${yt.length})`} channels={yt} />
      <Section title={`Instagram (${ig.length})`} channels={ig} />
    </div>
  );
}

function Stat({ label, value, href, accent }:
  { label: string; value: number; href?: string; accent?: boolean }) {
  const inner = (
    <div className={`card p-4 ${accent ? "border-accent/40" : ""}`}>
      <div className={`text-2xl font-semibold ${accent ? "text-accent" : ""}`}>{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  );
  return href ? <Link href={href}>{inner}</Link> : inner;
}

function Section({ title, channels }: { title: string; channels: Channel[] }) {
  return (
    <div>
      <h2 className="text-sm font-medium mb-2 text-slate-300">{title}</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {channels.map((c) => (
          <div key={c.id} className="card p-3">
            <div className="flex items-center justify-between">
              <span className="font-medium">{c.handle}</span>
              <span className={`pill ${c.is_active ? "" : "opacity-50"}`}>
                {c.is_active ? "actief" : "uit"}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">{c.niches?.category}</p>
            <p className="text-[11px] text-slate-500 mt-1">
              {c.niches?.tone} · RPM ${c.target_rpm_usd ?? 0}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
