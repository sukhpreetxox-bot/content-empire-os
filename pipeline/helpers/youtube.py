"""YouTube Data API v3 upload, one OAuth client per channel.

Token layout (per channel, referenced by channels.oauth_token_ref):
  secrets/youtube/<token_ref>.json   -> stored OAuth user credentials
  secrets/youtube/client_secret_<gcp_project>.json -> OAuth client (download
    from Google Cloud Console > Credentials).

IMPORTANT — synthetic-media disclosure:
  As of now the Data API does NOT expose a settable field for the
  "Altered or synthetic content" disclosure; it is confirmed in YouTube
  Studio. We therefore (a) record the disclosure in the description, and
  (b) leave a clear hook so it can be set the moment the API supports it.
  Do not claim the API sets it automatically — it does not yet.
"""
from __future__ import annotations
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import YOUTUBE_OAUTH_DIR

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SYNTH_NOTICE = (
    "\n\nDisclosure: This video contains realistic content that was created "
    "or altered with the help of AI tools."
)


def _credentials(token_ref: str, client_secret_file: str) -> Credentials:
    token_path = Path(YOUTUBE_OAUTH_DIR) / f"{token_ref}.json"
    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # One-time interactive consent (run during setup, not in cron).
            flow = InstalledAppFlow.from_client_secrets_file(
                str(Path(YOUTUBE_OAUTH_DIR) / client_secret_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
    return creds


def upload(channel: dict, video_path: Path, title: str, description: str,
           tags: list[str] | None = None, synthetic: bool = True,
           privacy: str = "unlisted", made_for_kids: bool = False) -> str:
    """Upload a video for `channel`. Returns the YouTube video id."""
    token_ref = channel.get("oauth_token_ref")
    if not token_ref:
        raise RuntimeError(f"channel {channel['handle']} has no oauth_token_ref")
    client_secret = f"client_secret_{channel.get('gcp_project_id','default')}.json"
    creds = _credentials(token_ref, client_secret)
    youtube = build("youtube", "v3", credentials=creds)

    if synthetic:
        description = description + SYNTH_NOTICE

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": (tags or [])[:30],
            "categoryId": "27",  # Education
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
            # NOTE: altered/synthetic disclosure is not yet a Data API field;
            # see module docstring. Hook kept here for when it lands:
            # "containsSyntheticMedia": synthetic,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _status, response = request.next_chunk()
    return response["id"]
