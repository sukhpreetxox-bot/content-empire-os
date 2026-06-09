import { supabaseAdmin } from "@/lib/supabase";
import { Idea } from "@/lib/types";
import IdeaForm from "@/components/IdeaForm";

export const dynamic = "force-dynamic";

const STATUS_STYLE: Record<string, string> = {
  new: "text-amber-400", used: "text-emerald-400", dismissed: "text-slate-500 line-through",
};

export default async function IdeasPage() {
  const sb = supabaseAdmin();
  const { data } = await sb.from("ideas").select("*")
    .order("created_at", { ascending: false }).limit(100);
  const ideas = (data ?? []) as Idea[];
  const pending = ideas.filter((i) => i.status === "new").length;

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Ideeën-inbox</h1>
        <span className="pill">{pending} in wachtrij</span>
      </div>
      <p className="text-sm text-slate-400">
        Typ hier ideeën, invalshoeken of losse gedachten. De generatie-cron pakt
        het oudste ongebruikte idee als onderwerp voor de volgende video — vóór
        het terugvalt op trend-onderzoek. Gebruikte ideeën blijven zichtbaar.
      </p>

      <IdeaForm />

      <div className="card divide-y divide-edge">
        {ideas.length === 0 && (
          <p className="p-4 text-sm text-slate-600">Nog geen ideeën. Typ je eerste hierboven.</p>
        )}
        {ideas.map((i) => (
          <div key={i.id} className="p-3 flex items-start justify-between gap-3">
            <div className="text-sm">{i.text}</div>
            <span className={`pill shrink-0 ${STATUS_STYLE[i.status] ?? ""}`}>
              {i.status === "new" ? "wachtrij" : i.status === "used" ? "gebruikt" : "afgewezen"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
