"use client";
import { useState, useTransition } from "react";
import { createIdeaAction } from "@/app/actions";

// Free-text inbox: type any idea, angle, hook or note. The generator picks the
// oldest unused idea as the next video's topic (before falling back to trends).
export default function IdeaForm() {
  const [text, setText] = useState("");
  const [pending, start] = useTransition();
  const [err, setErr] = useState<string | null>(null);

  function submit() {
    if (!text.trim()) return;
    setErr(null);
    start(async () => {
      try {
        await createIdeaAction(text);
        setText("");
      } catch (e: any) { setErr(e?.message ?? "fout"); }
    });
  }

  return (
    <div className="card p-4 space-y-3">
      <label className="text-sm font-medium">💡 Nieuw idee / voorstel / hook</label>
      <textarea
        className="w-full bg-edge rounded-lg p-3 text-sm min-h-[90px] outline-none focus:ring-1 focus:ring-accent"
        placeholder="Typ hier wat dan ook — een onderwerp, een invalshoek, een hook, een losse gedachte. De pipeline pakt het op als volgende video-topic."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) submit(); }}
      />
      <div className="flex items-center gap-3">
        <button className="btn btn-approve disabled:opacity-50"
                disabled={pending || !text.trim()} onClick={submit}>
          {pending ? "..." : "Toevoegen"}
        </button>
        <span className="text-xs text-slate-500">⌘/Ctrl + Enter</span>
        {err && <span className="text-xs text-rose-400">{err}</span>}
      </div>
    </div>
  );
}
