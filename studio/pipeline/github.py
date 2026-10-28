"""Tiny GitHub REST client for the workflows (standard library only). Uses GITHUB_TOKEN; never prints it."""
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"


class GitHubError(Exception):
    pass


def repo():
    r = os.environ.get("GITHUB_REPOSITORY")
    if not r:
        raise GitHubError("GITHUB_REPOSITORY is not set (run inside GitHub Actions)")
    return r


def _req(method, url, body=None, data=None, ctype="application/json", ok=(200, 201, 202, 204)):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise GitHubError("GITHUB_TOKEN is not set")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "studio-pipeline"}
    if body is not None:
        data = json.dumps(body).encode()
    if data is not None:
        headers["Content-Type"] = ctype
    req = urllib.request.Request(url if url.startswith("http") else API + url, data=data, method=method,
                                 headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if e.code in ok:
            return {}
        raise GitHubError(f"{method} {url.split('?')[0]} -> HTTP {e.code}: {e.read().decode(errors='replace')[:200]}")


def comment(number, text):
    return _req("POST", f"/repos/{repo()}/issues/{number}/comments", {"body": text[:60000]})


def close_pr(number):
    return _req("PATCH", f"/repos/{repo()}/pulls/{number}", {"state": "closed"})


def delete_branch(branch):
    try:
        return _req("DELETE", f"/repos/{repo()}/git/refs/heads/{urllib.parse.quote(branch)}")
    except GitHubError:
        return None


def ensure_label(name, color, description=""):
    try:
        _req("POST", f"/repos/{repo()}/labels", {"name": name, "color": color, "description": description})
    except GitHubError:
        pass   # already exists


def create_issue(title, body, labels=()):
    return _req("POST", f"/repos/{repo()}/issues", {"title": title[:250], "body": body[:60000], "labels": list(labels)})


def update_issue(number, **fields):
    return _req("PATCH", f"/repos/{repo()}/issues/{number}", fields)


def issues(label, state="open"):
    return _req("GET", f"/repos/{repo()}/issues?labels={urllib.parse.quote(label)}&state={state}&per_page=100")


def get_issue(number):
    return _req("GET", f"/repos/{repo()}/issues/{number}")


def create_release(tag, name, body, files, target="main"):
    rel = _req("POST", f"/repos/{repo()}/releases", {"tag_name": tag, "name": name[:200], "body": body[:60000],
                                                     "target_commitish": target})
    assets = []
    for f in files:
        f = Path(f)
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        up = rel["upload_url"].split("{")[0] + "?name=" + urllib.parse.quote(f.name)
        assets.append(_req("POST", up, data=f.read_bytes(), ctype=ctype))
    return rel, assets


def dispatch(workflow_file, ref="main", inputs=None):
    return _req("POST", f"/repos/{repo()}/actions/workflows/{workflow_file}/dispatches",
                {"ref": ref, "inputs": inputs or {}})
