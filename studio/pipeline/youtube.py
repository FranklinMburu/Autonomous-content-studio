"""Upload a finished video to YouTube (standard library only). Used by the "Pipeline 6: upload" workflow.

Needs three repository secrets, created once with `python youtube_auth.py` on your computer:
  YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN (upload scope only)
and the repository variable YOUTUBE_UPLOADS_APPROVED=true, set only after Google's API audit is approved.
Before the audit, YouTube locks API uploads as private for good, so the workflow refuses to upload.
"""
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


class YouTubeError(Exception):
    pass


def _secret(name):
    v = os.environ.get(name, "").strip()
    if not v:
        raise YouTubeError(f"{name} is not set")
    return v


def access_token():
    data = urllib.parse.urlencode({"client_id": _secret("YOUTUBE_CLIENT_ID"),
                                   "client_secret": _secret("YOUTUBE_CLIENT_SECRET"),
                                   "refresh_token": _secret("YOUTUBE_REFRESH_TOKEN"),
                                   "grant_type": "refresh_token"}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data, method="POST"), timeout=30) as r:
            return json.loads(r.read())["access_token"]
    except urllib.error.HTTPError as e:
        raise YouTubeError(f"token refresh failed: HTTP {e.code}") from None


def metadata(script, privacy="public"):
    yt = script.get("youtube", {}) or {}
    srcs = "\n".join(s["url"] for s in script.get("sources", []))
    desc = f"{(yt.get('description') or '').strip()}\n\nSources:\n{srcs}\n\n#Shorts".strip()
    title = (yt.get("title") or script["title"])[:100]
    return {"snippet": {"title": title, "description": desc[:4900], "tags": list(yt.get("tags", []))[:15],
                        "categoryId": "27"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}}


def upload(video_path, script, privacy="public"):
    """Resumable upload. Returns the YouTube video id."""
    tok = access_token()
    body = json.dumps(metadata(script, privacy)).encode()
    size = Path(video_path).stat().st_size
    req = urllib.request.Request(UPLOAD_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            session = r.headers["Location"]
        with open(video_path, "rb") as fh:
            put = urllib.request.Request(session, data=fh.read(), method="PUT",
                                         headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"})
        with urllib.request.urlopen(put, timeout=600) as r:
            return json.loads(r.read())["id"]
    except urllib.error.HTTPError as e:
        raise YouTubeError(f"upload failed: HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None
