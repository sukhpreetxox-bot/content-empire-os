"""LLM access: Groq primary, Ollama fallback.

generate() returns plain text. generate_json() parses a JSON object out of the
reply (tolerant of code fences / surrounding prose).
"""
from __future__ import annotations
import json
import re
import requests

from config import (
    GROQ_API_KEY, GROQ_MODEL, OLLAMA_HOST, OLLAMA_MODEL,
)


def _groq(system: str, prompt: str, temperature: float) -> str:
    from groq import Groq  # imported lazily so Ollama-only setups don't need it
    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _ollama(system: str, prompt: str, temperature: float) -> str:
    r = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "options": {"temperature": temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]


def generate(prompt: str, system: str = "", temperature: float = 0.8) -> str:
    """Try Groq first; on any failure fall back to local Ollama."""
    if GROQ_API_KEY and not GROQ_API_KEY.startswith("YOUR_"):
        try:
            return _groq(system, prompt, temperature)
        except Exception as e:  # noqa: BLE001 — fall through to Ollama
            print(f"[llm] Groq failed ({e}); falling back to Ollama")
    return _ollama(system, prompt, temperature)


def generate_json(prompt: str, system: str = "", temperature: float = 0.7) -> dict:
    """Generate and extract the first JSON object from the reply."""
    sys = (system + "\n\nReturn ONLY a single valid JSON object, no prose.").strip()
    raw = generate(prompt, sys, temperature)
    return _extract_json(raw)


def _extract_json(raw: str) -> dict:
    # strip code fences
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise
