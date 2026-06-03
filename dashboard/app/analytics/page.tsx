import { supabaseAdmin } from "@/lib/supabase";

export const dynamic = "force-dynamic";

interface Row {
  channel_id: string; views: number; likes: number;
  estimated_rpm_usd: number | null; estimated_revenue_usd: number | null;
}

export default async function AnalyticsPage() {
  const sb = supabaseAdmin();
  const [{ data: analytics }, { data: channels }] = await Promise.all([
    sb.from("analytics").select("channel_id, views, likes, estimated_rpm_usd, estimated_revenue_usd"),
    sb.from("channels").select("id, handle, platform, niches(display_name, target_rpm_usd)"),
  ]);

  const rows = (analytics ?? []) as Row[];
  const byChannel = new Map<string, { views: number; likes: number; rev: number }>();
  for (const r of rows) {
    const acc = byChannel.get(r.channel_id) ?? { views: 0, likes: 0, rev: 0 };
    acc.views += r.views ?? 0;
    acc.likes += r.likes ?? 0;
    acc.rev += r.estimated_revenue_usd ?? 0;
    byChannel.set(r.channel_id, acc);
  }

  const chs = (channels ?? []) as any[];
  const totalViews = [...byChannel.values()].reduce((s, v) => s + v.views, 0);

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Analytics</h1>
      <div className="grid grid-cols-3 gap-3">
        <div className="card p-4"><div className="text-2xl font-semibold">{totalViews}</div>
          <div className="text-xs text-slate-400">Totale views</div></div>
        <div className="card p-4"><div className="text-2xl font-semibold">{chs.length}</div>
          <div className="text-xs text-slate-400">Kanalen</div></div>
        <div className="card p-4"><div className="text-2xl font-semibold">{rows.length}</div>
          <div className="text-xs text-slate-400">Snapshots</div></div>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-edge/50 text-slate-400 text-xs">
            <tr><th className="text-left p-2">Kanaal</th><th className="p-2">Platform</th>
              <th className="p-2">Views</th><th className="p-2">Likes</th>
              <th className="p-2">Doel-RPM</th><th className="p-2">Geschatte omzet</th></tr>
          </thead>
          <tbody>
            {chs.map((c) => {
              const a = byChannel.get(c.id) ?? { views: 0, likes: 0, rev: 0 };
              return (
                <tr key={c.id} className="border-t border-edge">
                  <td className="p-2">{c.handle}</td>
                  <td className="p-2 text-center">{c.platform}</td>
                  <td className="p-2 text-center">{a.views}</td>
                  <td className="p-2 text-center">{a.likes}</td>
                  <td className="p-2 text-center">${c.niches?.target_rpm_usd ?? 0}</td>
                  <td className="p-2 text-center">${a.rev.toFixed(2)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-500">
        Wordt dagelijks gevuld door <code>analytics_cron.py</code> (houdt Supabase
        ook wakker). Leeg tot de eerste publicaties live staan.
      </p>
    </div>
  );
}
