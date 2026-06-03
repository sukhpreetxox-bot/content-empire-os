import { supabaseAdmin } from "@/lib/supabase";

export const dynamic = "force-dynamic";

export default async function CalendarPage() {
  const sb = supabaseAdmin();
  const [{ data: schedules }, { data: upcoming }] = await Promise.all([
    sb.from("publish_schedule").select("*, channels(handle, platform)").order("cron_expr"),
    sb.from("content").select("title, scheduled_for, status, channels(handle)")
      .in("status", ["approved", "review"]).not("scheduled_for", "is", null)
      .order("scheduled_for").limit(50),
  ]);

  const sch = (schedules ?? []) as any[];
  const up = (upcoming ?? []) as any[];

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Kalender</h1>

      <div>
        <h2 className="text-sm font-medium mb-2 text-slate-300">Herhalende schema's</h2>
        <div className="card divide-y divide-edge">
          {sch.map((s) => (
            <div key={s.id} className="p-3 flex items-center justify-between text-sm">
              <span>{s.channels?.handle}
                <span className="pill ml-2">{s.channels?.platform}</span></span>
              <span className="text-slate-400">
                <code>{s.cron_expr}</code> {s.timezone} · max {s.daily_cap}/dag
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-sm font-medium mb-2 text-slate-300">Gepland / in afwachting</h2>
        <div className="card divide-y divide-edge">
          {up.length === 0 && <p className="p-3 text-xs text-slate-600">niets gepland</p>}
          {up.map((c, i) => (
            <div key={i} className="p-3 flex items-center justify-between text-sm">
              <span>{c.title || "(geen titel)"}
                <span className="pill ml-2">{c.channels?.handle}</span></span>
              <span className="text-slate-400">
                {c.scheduled_for ? new Date(c.scheduled_for).toLocaleString("nl-NL") : "—"}
                <span className="pill ml-2">{c.status}</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
