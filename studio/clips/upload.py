"""Upload ONE finished Streamer Clips Short to the SC YouTube channel (19 Nov 2026). Used by "Clips: upload a Short".

Careful by design:
- Franklin starts every upload himself (Actions -> "Clips: upload a Short" -> Run, with the Short's id): one click = his yes.
- Refuses until Google's API audit is approved (repository variable YOUTUBE_UPLOADS_APPROVED=true): before that,
  YouTube locks API uploads as private for good (docs/YOUTUBE_SETUP.md).
- Refuses a Short that is already in posted.json (no double posts), and anything without its .json package.
- Uses the SC channel's own sign-in (secret YOUTUBE_SC_REFRESH_TOKEN; made with `python youtube_auth.py client.json sc`),
  never the Hidden Reasons channel.
- Campaign Shorts (description contains "#ad") are uploaded with YouTube's paid-promotion flag on.

    python -m studio.clips.upload --dir shorts --id kai-D1 --privacy public
"""
import argparse, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path

from studio.pipeline.youtube import YouTubeError, access_token

UPLOAD_URL = ("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable"
              "&part=snippet,status,paidProductPlacementDetails")


def package(d, sid):
    meta, mp4 = d / f"{sid}.json", d / f"{sid}.mp4"
    if not meta.exists() or not mp4.exists():
        sys.exit(f"{sid}: missing {mp4.name} or {meta.name} in {d}")
    m = json.loads(meta.read_text())
    title = (m.get("youtube_title") or m.get("title_box") or "").strip()
    desc = (m.get("description") or title).strip()
    if not title:
        sys.exit(f"{sid}: no title in {meta.name}")
    tags = [t.lstrip("#") for t in (m.get("hashtags") or []) if isinstance(t, str)][:15]
    paid = "#ad" in desc.lower()
    return mp4, {"snippet": {"title": title[:100], "description": desc[:4900], "tags": tags, "categoryId": "20"},
                 "status": {"privacyStatus": None, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False},
                 "paidProductPlacementDetails": {"hasPaidProductPlacement": paid}}


def upload(mp4, body):
    tok = access_token()
    data = json.dumps(body).encode()
    req = urllib.request.Request(UPLOAD_URL, data=data, method="POST", headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(mp4.stat().st_size)})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            session = r.headers["Location"]
        put = urllib.request.Request(session, data=mp4.read_bytes(), method="PUT",
                                     headers={"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4"})
        with urllib.request.urlopen(put, timeout=600) as r:
            return json.loads(r.read())["id"]
    except urllib.error.HTTPError as e:
        raise YouTubeError(f"upload failed: HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--id", required=True)
    ap.add_argument("--privacy", choices=("public", "unlisted", "private"), default="public")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir); posted_f = d / "posted.json"
    posted = json.loads(posted_f.read_text()) if posted_f.exists() else {}
    if a.id in posted:
        sys.exit(f"{a.id} was already uploaded: https://youtube.com/shorts/{posted[a.id]['video']}")
    mp4, body = package(d, a.id)
    body["status"]["privacyStatus"] = a.privacy
    print(json.dumps(body, indent=1, ensure_ascii=False))
    if a.dry_run:
        print("dry run: nothing uploaded"); return
    if os.environ.get("YOUTUBE_UPLOADS_APPROVED", "").lower() != "true":
        sys.exit("Refused: Google's API audit isn't approved yet (variable YOUTUBE_UPLOADS_APPROVED). Uploading now would "
                 "lock the video as private for good. Upload this one by hand; its title and description are above.")
    vid = upload(mp4, body)
    posted[a.id] = {"video": vid, "privacy": a.privacy, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    posted_f.write_text(json.dumps(posted, indent=1))
    print(f"UPLOADED {a.id}: https://youtube.com/shorts/{vid} ({a.privacy})")


if __name__ == "__main__":
    main()
