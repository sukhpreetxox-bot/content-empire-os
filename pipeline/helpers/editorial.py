"""Editorial-value gate (policy-safe).

Every script MUST clear this before it can reach 'review'. It enforces the
YouTube "inauthentic content" stance (Jul 2025+): no bare fact-recaps, no
mass-produced templates — there must be a genuine angle/analysis/transformation.

Three layers:
  1. Hard rules   — banned framings (per niche), minimum substance, angle present.
  2. Disclaimers  — required per-niche disclaimers are appended if missing.
  3. LLM judge    — a model rates originality/value and can fail the draft.
"""
from __future__ import annotations
from dataclasses import dataclass

from helpers import llm

MIN_SCRIPT_WORDS = 120
MIN_ANGLE_WORDS = 6


@dataclass
class EditorialResult:
    passed: bool
    notes: str
    script: str          # possibly with disclaimers appended


def _contains_any(text: str, needles: list[str]) -> list[str]:
    low = text.lower()
    return [n for n in needles if n.lower() in low]


def _append_disclaimers(script: str, disclaimers: list[str]) -> str:
    out = script.rstrip()
    for d in disclaimers:
        if d.lower() not in out.lower():
            out += f"\n\n{d}"
    return out


def _llm_judge(niche: dict, draft: dict) -> tuple[bool, str]:
    """Ask a model whether the draft has real editorial value."""
    prompt = (
        f"Niche: {niche['display_name']} — {niche['category']}.\n"
        f"Title: {draft.get('title','')}\n"
        f"Stated angle: {draft.get('angle','')}\n"
        f"Script:\n{draft.get('script','')}\n\n"
        "Judge this as a content-policy reviewer. It must have a UNIQUE point of "
        "view, analysis, or transformation — not a bare recap of facts, not a "
        "generic template. Rate 'value' 0-10 (10 = highly original/useful). "
        'Return JSON: {"value": <int>, "reason": "<short>"}'
    )
    try:
        v = llm.generate_json(prompt, system="You are a strict editorial reviewer.",
                              temperature=0.2)
        score = int(v.get("value", 0))
        return score >= 6, f"value={score}: {v.get('reason','')}"
    except Exception as e:  # noqa: BLE001
        # Fail open would let junk through; fail closed is safer for policy.
        return False, f"judge error ({e}) — blocked for safety"


def check(niche: dict, draft: dict) -> EditorialResult:
    """Run all gates. `draft` has keys: title, hook, angle, script."""
    script = (draft.get("script") or "").strip()
    angle = (draft.get("angle") or "").strip()
    reasons: list[str] = []

    # 1a. angle present & substantive
    if len(angle.split()) < MIN_ANGLE_WORDS:
        reasons.append("missing/weak editorial angle")

    # 1b. minimum substance
    if len(script.split()) < MIN_SCRIPT_WORDS:
        reasons.append(f"script too short (<{MIN_SCRIPT_WORDS} words)")

    # 1c. banned framings (per niche)
    banned = niche.get("banned_framings") or []
    hits = _contains_any(f"{draft.get('title','')} {script}", banned)
    if hits:
        reasons.append(f"banned framing(s): {', '.join(hits)}")

    if reasons:
        return EditorialResult(False, "; ".join(reasons), script)

    # 2. disclaimers (append, never block on these)
    script = _append_disclaimers(script, niche.get("required_disclaimers") or [])

    # 3. LLM originality judge
    ok, note = _llm_judge(niche, {**draft, "script": script})
    if not ok:
        return EditorialResult(False, note, script)

    return EditorialResult(True, note, script)
