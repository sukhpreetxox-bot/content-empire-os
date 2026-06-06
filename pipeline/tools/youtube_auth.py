#!/usr/bin/env python3
"""One-time YouTube OAuth consent → saves a reusable token.

Usage:
    python pipeline/tools/youtube_auth.py CLIENT_SECRET.json TOKEN_REF

- Opens your browser so you approve access for the Google account that owns
  the channel (do this while logged into that account).
- Saves the token to secrets/youtube/TOKEN_REF.json (reused forever after;
  auto-refreshes).
- TOKEN_REF is any short label you set on the channel row (e.g. quiet-capital).
"""
from __future__ import annotations
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    client_secret = Path(sys.argv[1]).expanduser()
    token_ref = sys.argv[2]
    if not client_secret.exists():
        sys.exit(f"client secret not found: {client_secret}")

    out_dir = Path(__file__).resolve().parents[2] / "secrets" / "youtube"
    out_dir.mkdir(parents=True, exist_ok=True)
    token_path = out_dir / f"{token_ref}.json"

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    token_path.write_text(creds.to_json())
    print(f"\n✅ Token saved: {token_path}")
    print(f"   Use oauth_token_ref = '{token_ref}' on the channel row.")


if __name__ == "__main__":
    main()
