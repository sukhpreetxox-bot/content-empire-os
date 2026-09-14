# Long-Form Deep Dive — Free AI Stack + What Actually Works (Sep 2026)

Research to switch Quiet Capital into 10-minute long-form, learning from the
channels that already win. Everything here is achievable **free**.

## The one insight that matters most

**Retention in long-form comes from NARRATIVE TENSION, not visual polish.**
Channels like ColdFusion and MagnatesMedia turn a subject into drama: something
wants X → it grows → a hidden weakness appears → consequences. Documentary
scripts earn retention in the **first 15 seconds** (audio only — the first
sentence), and hold 40–60% to the midpoint through **conflict-and-resolution
pacing**, not production. Pure AI scripts read like AI scripts; the fix is one
concrete vignette/anecdote a generic model wouldn't produce.

Our old `deep` format got ~5% retention because it was a Stoic essay with
"movements" — no tension, no open loops, no payoff. That is now fixed in the
prompt (see gen_cron `build_prompt`).

## The 10-minute beat structure (baked into the deep prompt)

~1500–1900 words at our slow meditative pace = ~10–12 min (must exceed 8 min for
mid-roll ads). Pacing ≈ 130–160 wpm normal, ~120 at our 0.90 speed.

| Beat | Time | Words | Job |
|---|---|---|---|
| Hook | 0:00–0:15 | ~30 | bold claim / question / curiosity gap → open a tension |
| Setup | 0:15–1:30 | ~150 | why it matters; personal stakes |
| Movement 1 | 1:30–4:00 | ~450 | first angle + **open loop** + one concrete vignette/anecdote |
| Re-hook | 4:00–4:15 | ~40 | tease what's next so the midpoint doesn't sag |
| Movements 2–3 | 4:15–8:30 | ~700 | complicate, counter-twist, **resolve the open loop** |
| Payoff | 8:30–9:00 | ~120 | resolve the hook's promise; the transformation lands |
| Close | 9:00–9:15 | ~40 | resonant line + sincere question (drives comments) |

Rules: open loops + re-hooks keep the middle alive; visual variety every 30–60s;
never a list — always building toward one insight.

## The free stack, per dimension (and what we already have)

The honest finding: **our free stack is already ~80% of the winning long-form
stack.** The gap is structure and motion b-roll, not tools.

| Dimension | Best free (2026) | What we run | Verdict |
|---|---|---|---|
| **Denkmotor (LLM/script)** | Claude best for long-form/documentary; open: DeepSeek R1 (logic), Mixtral (prose); ChatGPT free 2–3/wk | Gemini → Groq → Ollama cascade | Keep. The win is the **documentary prompt**, not the model. |
| **Voice** | ElevenLabs (best, limited free), **Fish Audio** (free, YouTube-tuned, cloning), Edge Read Aloud (100% free neural), TTSMaker | Kokoro `am_onyx` @0.90 (free, local, **unlimited**) | Keep Kokoro (unlimited + meditative). Test Fish Audio for a warmer long-form read. |
| **AI video / visuals** | **Veo 3.1** (Google AI Studio, free daily credits, cinematic, least watermark), Kling 2.5, WayinVideo / LlamaGen (no-watermark b-roll) | Cloudflare FLUX **stills** + Ken Burns | Upgrade path: add real **motion b-roll** (Veo free daily) for hero shots; keep FLUX stills for volume. |
| **Sound / music** | Chosic, Bensound, Fesliyan, **Alex-Productions**, **Infraction** (free, no-copyright, cinematic/documentary) | incompetech CC-BY, ducked mix | Add cinematic documentary tracks; deepen the ducked score for 10-min. |
| **Captions / subtitles** | Whisper (open-source), **Phonix** (styled word-highlight), Whisper Web | faster-whisper **word-level** (already) | Best-in-class free, already ours. |
| **Design / render** | Remotion, Canva free | Remotion | Keep; needs a long-form composition (longer pacing, chapters). |
| **Language** | Fish/most TTS = 80+ langs | English | Keep English (widest reach). |

## The switch plan

- **Phase 1 (now, shipped):** `deep` prompt rewritten to the 7-beat documentary
  structure; deep cron RE-ENABLED Mon & Thu (2 flagship 10-min essays/week).
  Shorts stay daily as the discovery engine that feeds long-form.
- **Phase 2 (next):** motion b-roll via Veo 3.1 free daily credits for 3–5 hero
  shots per essay (keep FLUX stills for the rest); richer cinematic score.
- **Phase 3:** once one essay holds ≥40% to the midpoint, scale deep to 3–4/wk.

## Honest framing

Shorts = top of funnel (reach + subs). Long-form = watch-time + the only real ad
money (RPM ~$5–12 vs Shorts' pennies). This switch is the right funnel — but
long-form still needs Shorts (or distribution) to be *discovered*. We are
building the thing that pays; discovery remains the separate, deferred lever.

## Sources
ColdFusion / MagnatesMedia narrative (faceless.my, magnatesmedia.com) · frameo.ai
long-form script structure · HeyGen / Oakgen free stack · Fish Audio, ElevenLabs,
Edge Read Aloud (voice) · Veo 3.1 / Kling / WayinVideo (b-roll) · Chosic /
Alex-Productions / Infraction (music) · Whisper / Phonix (captions).
