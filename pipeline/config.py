"""Central configuration for the Content Empire pipeline.

All values come from environment variables (.env at repo root). Secrets use
placeholders in .env.example; fill the real ones in .env on the VM.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the repo root (one level up from pipeline/)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _req(name: str) -> str:
    v = os.getenv(name)
    if not v or v.startswith("YOUR_"):
        raise RuntimeError(
            f"Missing required env var {name!r}. Set it in {ROOT/'.env'}"
        )
    return v


# --- Supabase (service role bypasses RLS; server-side only) -----------------
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# --- LLM: Groq primary, Ollama fallback -------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# --- B-roll -----------------------------------------------------------------
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# --- YouTube / Instagram ----------------------------------------------------
YOUTUBE_OAUTH_DIR = Path(os.getenv("YOUTUBE_OAUTH_DIR", ROOT / "secrets/youtube"))
IG_APP_ID = os.getenv("IG_APP_ID", "")
IG_APP_SECRET = os.getenv("IG_APP_SECRET", "")
IG_TOKEN_DIR = Path(os.getenv("IG_TOKEN_DIR", ROOT / "secrets/instagram"))
IG_GRAPH_VERSION = os.getenv("IG_GRAPH_VERSION", "v21.0")

# --- Voice: Kokoro (primary, free, high quality); edge-tts is the fallback --
MODELS_DIR = Path(os.getenv("MODELS_DIR", ROOT / "models"))
KOKORO_MODEL = MODELS_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES = MODELS_DIR / "voices-v1.0.bin"

# --- Paths ------------------------------------------------------------------
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", ROOT / "assets"))
REMOTION_DIR = Path(os.getenv("REMOTION_DIR", ROOT / "remotion"))
VOICE_DIR = ASSETS_DIR / "voiceover"
VIDEO_DIR = ASSETS_DIR / "video"
THUMB_DIR = ASSETS_DIR / "thumbnails"
BROLL_DIR = ASSETS_DIR / "broll"
for _d in (VOICE_DIR, VIDEO_DIR, THUMB_DIR, BROLL_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- Rate limits (respect free-tier / platform caps) ------------------------
# YouTube Data API v3: 10,000 units/day/project, upload = 1,600 units (~6/day).
YT_MAX_UPLOADS_PER_DAY = 5
# Instagram Graph API: stay well under 25 posts / 24h / account.
IG_MAX_POSTS_PER_DAY = 10
# Seconds to wait between uploads (throttle / spread load).
UPLOAD_THROTTLE_SECONDS = 30
# Default YouTube privacy for auto-published, approved videos.
# Start "unlisted" while tuning; flip to "public" via env when confident.
PUBLISH_PRIVACY = os.getenv("PUBLISH_PRIVACY", "unlisted")  # unlisted|public|private
