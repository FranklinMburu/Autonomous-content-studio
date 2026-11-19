"""Live status for the Notion front door ("Start here — YouTube Creator Studio").

Rewrites ONE block on that page: the callout whose text starts with "Live status". Nothing else on the page (or in
Notion) is touched. Reads the Studio Board, the polish tickets in this checkout and, when GH_TOKEN is set, the open pull
requests. Token: GitHub secret NOTION_TOKEN (integration "Studio Board bot", connected by Franklin on 19 Nov 2026 to the
YouTube Creator Studio page and the Studio Board). The token is never printed.

    python tools/front_door_status.py            # write to Notion
    python tools/front_door_status.py --dry-run  # print the text only
"""
import argparse, collections, datetime as dt, json, os, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.clips.board import LANES, STAGES, all_cards, call  # noqa: E402

PAGE = "41dda224599e8114b120eee8ded4ca75"   # fixed on purpose: no setting can point this at another page
PAGE_UUID = "41dda224-599e-8114-b120-eee8ded4ca75"
MARKER = "Live status"
REPO = os.environ.get("GITHUB_REPOSITORY", "FranklinMburu/Autonomous-content-studio")


def board_counts():
    c = collections.Counter()
    for card in all_cards():
        p = card.get("properties", {})
        lane = ((p.get("Lane") or {}).get("select") or {}).get("name")
        stage = ((p.get("Stage") or {}).get("status") or {}).get("name")
        if lane and stage:
            c[(lane, stage)] += 1
    return c


def polish_tickets():
    c = collections.Counter()
    for t in sorted((ROOT / "polish" / "film").glob("*/ticket.json")):
        try:
            c[json.loads(t.read_text()).get("status", "unknown")] += 1
        except ValueError:
            c["unreadable"] += 1
    return c


def open_prs():
    tok = os.environ.get("GH_TOKEN")
    if not tok:
        return None
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/pulls?state=open&per_page=50",
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
    try:
        return [(p["number"], p["title"]) for p in json.load(urllib.request.urlopen(req, timeout=30))]
    except Exception:  # noqa: BLE001  (status is best-effort; never fail the board for this)
        return None


def compose(now=None):
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
    b, pol, prs = board_counts(), polish_tickets(), open_prs()
    lines = [f"{MARKER} (automatic, {now:%d %b %Y %H:%M} Nairobi; written by GitHub, do not edit by hand)", "",
             "Studio Board:"]
    for lane in LANES:
        parts = [f"{b[(lane, s)]} {s}" for s in STAGES if b[(lane, s)]]
        lines.append(f"• {lane}: " + (" · ".join(parts) if parts else "no cards"))
    posted = sum(b[(l, "Posted")] for l in LANES)
    lines.append(f"Posted to YouTube so far: {posted}")
    total = sum(pol.values())
    lines.append("")
    lines.append(f"Hidden Reasons polish tickets on main: {total}" +
                 (" (" + ", ".join(f"{n} {k}" for k, n in sorted(pol.items())) + ")" if total else ""))
    if prs is not None:
        lines.append(f"Open pull requests waiting for Franklin: {len(prs)}")
        lines += [f"• #{n} {t[:90]}" for n, t in prs[:8]]
    return "\n".join(lines)


def guarded(method, path, body=None):
    """The only door to Notion in this file. Allowed: read the Studio Board, read the front door's top-level blocks,
    update the text of the one Live status box. Never delete, never create, move or archive pages, never another page."""
    ok = ((method == "GET" and path.startswith(f"/blocks/{PAGE}/children")) or
          (method == "GET" and path.startswith("/blocks/") and path.count("/") == 2) or
          (method == "PATCH" and path.startswith("/blocks/") and path.count("/") == 2
           and set(body or {}) == {"callout"} and set(body["callout"]) == {"rich_text"}))
    if not ok:
        sys.exit(f"refused: {method} {path} is outside what this script may do")
    return call(method, path, body)


def find_block():
    cursor = None
    for _ in range(10):
        r = guarded("GET", f"/blocks/{PAGE}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else ""))
        for blk in r.get("results", []):
            if blk.get("type") == "callout":
                txt = "".join(t.get("plain_text", "") for t in blk["callout"].get("rich_text", []))
                if txt.startswith(MARKER):
                    return blk["id"]
        if not r.get("has_more"):
            return None
        cursor = r.get("next_cursor")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    text = compose()
    print(text)
    if a.dry_run:
        return
    blk = find_block()
    if not blk:
        sys.exit(f"No callout starting with '{MARKER}' on the front door; add it back (see the page's Details for AI).")
    # Re-check right before writing: the block must still be our box, directly on the front door.
    b = guarded("GET", f"/blocks/{blk}")
    parent = (b.get("parent") or {}).get("page_id", "").replace("-", "")
    head = "".join(t.get("plain_text", "") for t in (b.get("callout") or {}).get("rich_text", []))
    if b.get("type") != "callout" or parent != PAGE or not head.startswith(MARKER) or b.get("archived"):
        sys.exit("refused: the Live status box is not where it should be; nothing was written")
    guarded("PATCH", f"/blocks/{blk}", {"callout": {"rich_text": [{"type": "text", "text": {"content": text[:1990]}}]}})
    print("front door status updated")


if __name__ == "__main__":
    main()
