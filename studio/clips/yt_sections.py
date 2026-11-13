"""Cloud side of the laptop helper (tools/laptop_agent): ask for YouTube sections, then pick them up.

    python -m studio.clips.yt_sections request --id <id> --url <youtube url> --start 120 --end 210   (on GitHub Actions)
    python -m studio.clips.yt_sections fetch --id <id> --out section.mp4 [--wait 1800]

`request` appends to youtube_requests.json on the `clips-jobs` branch (needs a checkout with push rights: the workflow's
GITHUB_TOKEN with contents: write). `fetch` waits for <id>.mp4 on the `yt-sections` release (the laptop uploads it within
~10 minutes while the laptop is on) and downloads it.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "FranklinMburu/Autonomous-content-studio")
URL_OK = re.compile(r"^https://(www\.)?(youtube\.com/(watch\?v=|live/|shorts/)|youtu\.be/)[A-Za-z0-9_-]{6,20}")


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout


def request(a):
    assert URL_OK.match(a.url) and 0 <= a.start < a.end and a.end - a.start <= 600, "bad request"
    tok = os.environ["GITHUB_TOKEN"]
    d = Path(tempfile.mkdtemp())
    remote = f"https://x-access-token:{tok}@github.com/{REPO}.git"
    try:
        sh("git", "clone", "-q", "--depth", "1", "--branch", "clips-jobs", remote, str(d))
    except subprocess.CalledProcessError:   # first time: make the branch with an empty list
        sh("git", "init", "-q", str(d)); sh("git", "checkout", "-q", "-b", "clips-jobs", cwd=d)
        sh("git", "remote", "add", "origin", remote, cwd=d)
    f = d / "youtube_requests.json"
    data = json.loads(f.read_text()) if f.exists() else {"requests": []}
    if not any(r["id"] == a.id for r in data["requests"]):
        data["requests"].append({"id": a.id, "url": a.url, "start": a.start, "end": a.end, "asked": int(time.time())})
    data["requests"] = data["requests"][-200:]
    f.write_text(json.dumps(data, indent=1))
    sh("git", "add", "youtube_requests.json", cwd=d)
    sh("git", "-c", "user.name=clips-bot", "-c", "user.email=clips-bot@users.noreply.github.com", "commit", "-q", "-m", f"request {a.id}", cwd=d)
    sh("git", "push", "-q", "origin", "clips-jobs", cwd=d)
    print(f"requested {a.id}: {a.url} {a.start}-{a.end} s")


def fetch(a):
    url = f"https://github.com/{REPO}/releases/download/yt-sections/{a.id}.mp4"
    t0 = time.time()
    while True:
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "clips"}), timeout=120) as r:
                Path(a.out).write_bytes(r.read())
            print(f"fetched {a.id} after {time.time()-t0:.0f} s")
            return
        except Exception:  # noqa: BLE001  not there yet
            if time.time() - t0 > a.wait:
                sys.exit(f"{a.id} not uploaded within {a.wait} s: is the laptop on? (log: %USERPROFILE%\\.clips_agent\\agent.log)")
            time.sleep(30)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("request"); r.add_argument("--id", required=True); r.add_argument("--url", required=True)
    r.add_argument("--start", type=float, required=True); r.add_argument("--end", type=float, required=True)
    f = sub.add_parser("fetch"); f.add_argument("--id", required=True); f.add_argument("--out", required=True)
    f.add_argument("--wait", type=int, default=1800)
    a = ap.parse_args()
    {"request": request, "fetch": fetch}[a.cmd](a)


if __name__ == "__main__":
    main()
