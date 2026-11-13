"""Laptop helper for the clipping engine: downloads ONLY the short YouTube sections the cloud pipeline asks for.

Why it exists: YouTube blocks video downloads from GitHub's servers. Your laptop is an ordinary home connection,
so the same download works there. No YouTube login and no cookies are used, ever.

What it does each run (Windows Task Scheduler runs it every 10 minutes; one run takes seconds when there's nothing):
  1. reads the public request list: branch `clips-jobs`, file `youtube_requests.json` of this repo
     (each request: id, YouTube URL, start and end second; nothing else);
  2. checks every request strictly (a youtube.com/youtu.be URL, numbers only, at most 10 minutes per section);
  3. downloads just that section with yt-dlp (up to 1080p) into %USERPROFILE%\\.clips_agent\\out;
  4. uploads it to the GitHub release `yt-sections` of this repo, named <id>.mp4, where the cloud pipeline picks it up;
  5. remembers what it finished, so nothing is downloaded twice.

It never runs code from the internet or from the repo: it only reads that small JSON list as data.
The GitHub token (fine-grained: this one repo, "Contents: read and write") is typed by you into setup.ps1 and kept in
%USERPROFILE%\\.clips_agent\\token, readable only by your Windows user. This script reads it and never prints it.

    python agent.py            one run (what the scheduled task does)
    python agent.py --check    show what it would do, download nothing
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

REPO = "FranklinMburu/Autonomous-content-studio"
REQUESTS = f"https://raw.githubusercontent.com/{REPO}/clips-jobs/youtube_requests.json"
RELEASE_TAG = "yt-sections"
HOME = Path(os.environ.get("USERPROFILE") or Path.home()) / ".clips_agent"
OUT, STATE, LOG = HOME / "out", HOME / "done.json", HOME / "agent.log"
URL_OK = re.compile(r"^https://(www\.)?(youtube\.com/(watch\?v=|live/|shorts/)|youtu\.be/)[A-Za-z0-9_-]{6,20}([&?][A-Za-z0-9_=&.-]*)?$")
ID_OK = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
MAX_SECTION = 600


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    print(line)
    HOME.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def token():
    p = HOME / "token"
    if not p.exists():
        sys.exit("No token yet: run setup.ps1 first.")
    return p.read_text(encoding="utf-8").strip()


def api(method, url, data=None, headers=None, raw=False):
    h = {"Authorization": f"Bearer {token()}", "Accept": "application/vnd.github+json", "User-Agent": "clips-agent",
         "X-GitHub-Api-Version": "2022-11-28", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        body = r.read()
    return body if raw else (json.loads(body) if body else {})


def requests_list():
    try:
        req = urllib.request.Request(REQUESTS + f"?t={int(time.time())}", headers={"User-Agent": "clips-agent"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise
    good = []
    for r in d.get("requests", []) if isinstance(d, dict) else []:
        try:
            rid, url, a, b = str(r["id"]), str(r["url"]), float(r["start"]), float(r["end"])
        except (KeyError, TypeError, ValueError):
            log(f"skipped a malformed request: {str(r)[:120]}")
            continue
        if not (ID_OK.match(rid) and URL_OK.match(url) and 0 <= a < b and b - a <= MAX_SECTION):
            log(f"skipped request {rid[:40]!r}: failed the safety checks")
            continue
        good.append({"id": rid, "url": url, "start": a, "end": b})
    return good


def release():
    try:
        return api("GET", f"https://api.github.com/repos/{REPO}/releases/tags/{RELEASE_TAG}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        return api("POST", f"https://api.github.com/repos/{REPO}/releases",
                   json.dumps({"tag_name": RELEASE_TAG, "name": "YouTube sections (laptop helper)", "prerelease": True,
                               "body": "Short sections downloaded by the laptop helper for the clipping pipeline. Not for publishing."}).encode())


def ffmpeg_dir():
    """Where ffmpeg is: on PATH, or winget's links folder (PATH changes don't always reach scheduled tasks)."""
    import shutil
    found = shutil.which("ffmpeg")
    if found:
        return str(Path(found).parent)
    for cand in (Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links",
                 *sorted((Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages").glob("Gyan.FFmpeg*/*/bin"))):
        if (cand / "ffmpeg.exe").exists():
            return str(cand)
    return None


def download(r):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{r['id']}.mp4"
    if f.exists():
        f.unlink()
    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-cookies-from-browser", "-q", "--no-warnings",
           "-f", "bv*[height<=1080]+ba/b[height<=1080]/b", "--merge-output-format", "mp4",
           "--download-sections", f"*{r['start']:.2f}-{r['end']:.2f}", "--force-keyframes-at-cuts",
           "-o", str(f), r["url"]]
    loc = ffmpeg_dir()
    if loc:
        cmd[3:3] = ["--ffmpeg-location", loc]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if p.returncode or not f.exists():
        raise RuntimeError((p.stderr or p.stdout).strip()[-300:])
    return f


def upload(rel, f):
    for a in rel.get("assets", []):
        if a["name"] == f.name:
            api("DELETE", a["url"])
    up = rel["upload_url"].split("{")[0] + f"?name={f.name}"
    api("POST", up, f.read_bytes(), {"Content-Type": "video/mp4"})


def main():
    check = "--check" in sys.argv
    done = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    todo = [r for r in requests_list() if r["id"] not in done]
    if not todo:
        print("nothing to do")
        return
    log(f"{len(todo)} section(s) requested")
    if check:
        for r in todo:
            print(f"  would download {r['id']}: {r['url']} {r['start']:.0f}-{r['end']:.0f} s")
        return
    rel = release()
    for r in todo:
        try:
            t0 = time.time()
            f = download(r)
            upload(rel, f)
            done.add(r["id"])
            STATE.write_text(json.dumps(sorted(done)))
            log(f"done {r['id']}: {f.stat().st_size/1e6:.1f} MB in {time.time()-t0:.0f} s")
            f.unlink()
        except Exception as e:  # noqa: BLE001  one failed section must not stop the others
            log(f"FAILED {r['id']}: {e}")


if __name__ == "__main__":
    main()
