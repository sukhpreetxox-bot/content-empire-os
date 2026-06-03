import { Content } from "@/lib/types";
import ApproveButtons from "./ApproveButtons";

export default function ContentCard({ c }: { c: Content }) {
  const niche = c.channels?.niches?.display_name ?? "—";
  return (
    <div className="card p-3 space-y-2" data-testid="content-card">
      <div className="flex items-center justify-between">
        <span className="pill">{niche}</span>
        <span className="text-xs text-slate-500">{c.channels?.platform}</span>
      </div>
      <div className="font-medium text-sm leading-snug">{c.title || "(geen titel)"}</div>
      {c.hook && <p className="text-xs text-slate-400 line-clamp-2">{c.hook}</p>}
      {c.editorial_angle && (
        <p className="text-[11px] text-accent/80 line-clamp-2">
          ⟢ {c.editorial_angle}
        </p>
      )}
      {!c.editorial_passed && c.status !== "idea" && (
        <p className="text-[11px] text-rose-400">gate: {c.editorial_notes}</p>
      )}
      {c.status === "review" && (
        <div className="pt-1">
          <ApproveButtons id={c.id} />
        </div>
      )}
      {c.published_url && (
        <a href={c.published_url} target="_blank" rel="noreferrer"
           className="text-xs text-emerald-400 hover:underline">
          Bekijk gepubliceerd ↗
        </a>
      )}
    </div>
  );
}
