import { supabaseAdmin } from "@/lib/supabase";
import { Channel, Niche } from "@/lib/types";
import ChannelForm from "@/components/ChannelForm";

export const dynamic = "force-dynamic";

export default async function ChannelsPage() {
  const sb = supabaseAdmin();
  const [{ data: channels }, { data: niches }] = await Promise.all([
    sb.from("channels").select("*, niches(*)").order("created_at"),
    sb.from("niches").select("*").order("display_name"),
  ]);
  const chs = (channels ?? []) as Channel[];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Kanalen</h1>
        <ChannelForm niches={(niches ?? []) as Niche[]} />
      </div>
      <div className="card divide-y divide-edge">
        {chs.map((c) => (
          <div key={c.id} className="p-3 flex items-center justify-between">
            <div>
              <div className="font-medium">{c.handle}
                <span className="pill ml-2">{c.platform}</span>
              </div>
              <div className="text-xs text-slate-400">
                {c.niches?.display_name} · {c.niches?.category}
              </div>
              <div className="text-[11px] text-slate-500">
                stem {c.niches?.tts_voice} · RPM ${c.target_rpm_usd ?? 0}
                {c.oauth_token_ref ? " · YT-token ✓" : ""}
                {c.ig_user_id ? " · IG ✓" : ""}
              </div>
            </div>
            <span className={`pill ${c.is_active ? "text-emerald-400" : "opacity-50"}`}>
              {c.is_active ? "actief" : "uit"}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-500">
        Modulair: een niche bewerken (stem, disclaimers, topics) doe je als rij in
        de <code>niches</code>-tabel; een kanaal toevoegen via de knop hierboven.
      </p>
    </div>
  );
}
