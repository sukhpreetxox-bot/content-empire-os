import { supabaseAdmin } from "@/lib/supabase";
import { BOARD_COLUMNS, STATUS_LABEL, Content } from "@/lib/types";
import ContentCard from "@/components/ContentCard";

export const dynamic = "force-dynamic";

export default async function BoardPage() {
  const sb = supabaseAdmin();
  const { data, error } = await sb
    .from("content")
    .select("*, channels(*, niches(*))")
    .order("updated_at", { ascending: false })
    .limit(300);

  if (error) {
    return <p className="text-rose-400">DB-fout: {error.message}</p>;
  }
  const items = (data ?? []) as Content[];
  const byStatus = (s: string) => items.filter((i) => i.status === s);

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Content-board</h1>
      <div className="grid grid-flow-col auto-cols-[minmax(220px,1fr)] gap-3 overflow-x-auto pb-4">
        {BOARD_COLUMNS.map((col) => {
          const cards = byStatus(col);
          return (
            <div key={col} className="min-w-[220px]">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-medium">{STATUS_LABEL[col]}</h2>
                <span className="pill">{cards.length}</span>
              </div>
              <div className="space-y-3">
                {cards.map((c) => <ContentCard key={c.id} c={c} />)}
                {cards.length === 0 && (
                  <p className="text-xs text-slate-600">leeg</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
