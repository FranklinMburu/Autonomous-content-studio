#!/usr/bin/env python3
"""Sync check: print the LIVE state of the studio, so an agent (Codex, Claude, anyone) starts from facts, not guesses.

    python tools/sync_check.py            # everything (about 15 public GitHub API calls)
    python tools/sync_check.py --offline  # only the local repo: git state + offline tests

Read-only. Stdlib only. Uses the public GitHub API (no token needed; 60 calls/hour without one). If GH_TOKEN or
GITHUB_TOKEN is set it is sent so the limit is higher, but never printed. Never touches .env.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

REPO = "FranklinMburu/Autonomous-content-studio"
API = f"https://api.github.com/repos/{REPO}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get(path):
    req = urllib.request.Request(API + path, headers={"Accept": "application/vnd.github+json", "User-Agent": "studio-sync-check"})
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def sh(*cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return (p.stdout + p.stderr).strip()


def head(t):
    print(f"\n## {t}")


def ago(iso):
    if not iso:
        return "?"
    h = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds() / 3600
    return f"{h:.0f} h ago" if h >= 1 else f"{h * 60:.0f} min ago"


def local():
    head("Local repo")
    print(sh("git", "status", "-sb").splitlines()[0] if sh("git", "status", "-sb") else "(not a git repo)")
    print("last commits on this checkout:")
    print(sh("git", "log", "--oneline", "-8"))
    head("Offline tests (all must pass)")
    for t in ["tests/test_story.py", "tests/test_story_writer.py", "tests/test_workflows.py",
              "tests/test_pipeline.py", "tests/test_pipeline_fixes.py"]:
        p = subprocess.run([sys.executable, t], cwd=ROOT, capture_output=True, text=True)
        print(f"- {t}: {'PASS' if p.returncode == 0 else 'FAIL (exit %d)' % p.returncode}")


def live():
    head("Open pull requests")
    prs = get("/pulls?state=open&per_page=20")
    for p in prs:
        print(f"- #{p['number']} {p['title']}  ({p['head']['ref']}, {ago(p['created_at'])})")
    if not prs:
        print("- none")

    head("Open issues (by label)")
    for i in get("/issues?state=open&per_page=50"):
        if "pull_request" in i:
            continue
        labels = ",".join(l["name"] for l in i["labels"]) or "-"
        print(f"- #{i['number']} [{labels}] {i['title']}  (updated {ago(i['updated_at'])})")

    head("Workflow runs, last 40 (site feed and tests hidden)")
    bad = 0
    for r in get("/actions/runs?per_page=60")["workflow_runs"]:
        if r["name"].startswith("Site feed") or r["name"] == "Pipeline tests":
            continue
        c = r["conclusion"] or r["status"]
        bad += c == "failure"
        print(f"- {r['created_at'][:16]}Z  {r['name']}  [{r['event']}]  {c}  {r['html_url'] if c == 'failure' else ''}")
    print(f"failures listed: {bad}")

    head("Is the film schedule firing? (Story clock / Story schedule / Make a story video)")
    for wf in ["story-clock.yml", "story-schedule.yml", "make-story.yml"]:
        try:
            runs = get(f"/actions/workflows/{wf}/runs?per_page=5")["workflow_runs"]
            print(f"- {wf}: " + "; ".join(f"{r['created_at'][5:16]} {r['conclusion'] or r['status']}" for r in runs))
        except Exception as e:
            print(f"- {wf}: could not read ({e})")

    head("Website")
    try:
        f = urllib.request.urlopen(f"https://raw.githubusercontent.com/{REPO}/site-data/feed.json", timeout=20)
        print(f"- feed.json built {ago(json.load(f).get('built'))} (site-data branch)")
    except Exception as e:
        print(f"- feed.json not readable ({e})")
    print(f"- site: https://franklinmburu.github.io/{REPO.split('/')[1]}/")

    head("Polish tickets on main (film)")
    try:
        dirs = get("/contents/polish/film?ref=main")
    except Exception:
        dirs = []
        print("- none open (polish/film/ is empty or absent)")
    try:
        for d in dirs:
            if d["type"] == "dir":
                t = json.load(urllib.request.urlopen(f"https://raw.githubusercontent.com/{REPO}/main/polish/film/{d['name']}/ticket.json", timeout=20))
                print(f"- {d['name']}: {t.get('status')}")
    except Exception as e:
        print(f"- could not read ({e})")


if __name__ == "__main__":
    print(f"# Studio sync check, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    local()
    if "--offline" not in sys.argv:
        try:
            live()
        except Exception as e:
            print(f"\n(live part stopped: {e}. Run again later, or set GH_TOKEN for a higher API limit.)")
