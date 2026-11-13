"""The Studio Board in Notion, written by the pipeline itself (GitHub secret NOTION_TOKEN; Notion's integration
"Studio Board bot" is connected to the Studio Board only).

    python -m studio.clips.board add --lane SC --title "..." [--who ... --why ... --source URL --video-id SC-... --stage Picked]
    python -m studio.clips.board move --video-id SC-20261113-01 --stage Review [--clip-file URL --score 8.7 --views-band 50K-250K --note "..."]
    python -m studio.clips.board picks --lane SC --file hot_streamers.json [--top 5]
    python -m studio.clips.board picks --lane WC --file hot_world.json [--top 5]
    python -m studio.clips.board test

A card is found again by its Video ID, so re-running never duplicates. The token is read from the environment and never
printed. Everything here only writes to the Studio Board.
"""
import argparse, datetime as dt, json, os, sys, urllib.error, urllib.request
from pathlib import Path

DATABASE = os.environ.get("STUDIO_BOARD_DB", "654c7f0514f0448f8c8e79752c604dbc")
API = "https://api.notion.com/v1"
LANES = ("SC", "WC", "HR", "TE")
STAGES = ("Picked", "Making", "Review", "Approved", "Posted", "Skipped")
BANDS = ("under 10K", "10K-50K", "50K-250K", "250K+")


def call(method, path, body=None):
    tok = os.environ.get("NOTION_TOKEN")
    if not tok:
        sys.exit("NOTION_TOKEN is not set (GitHub secret)")
    req = urllib.request.Request(f"{API}{path}", method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {tok}", "Notion-Version": "2022-06-28",
                                          "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:400]
        hint = (" (is 'Studio Board bot' connected to the Studio Board? ••• → Connections)" if e.code in (403, 404) else "")
        sys.exit(f"Notion error {e.code}: {msg}{hint}")


def text(v):
    return {"rich_text": [{"text": {"content": str(v)[:1900]}}]} if v else {"rich_text": []}


def props(a):
    p = {}
    if getattr(a, "title", None):
        p["Title"] = {"title": [{"text": {"content": a.title[:200]}}]}
    if getattr(a, "lane", None):
        p["Lane"] = {"select": {"name": a.lane}}
    if getattr(a, "stage", None):
        p["Stage"] = {"status": {"name": a.stage}}
    for k, name in (("video_id", "Video ID"), ("who", "Who / topic"), ("why", "Why now"), ("note", "Before you post")):
        if getattr(a, k, None):
            p[name] = text(getattr(a, k))
    for k, name in (("source", "Source"), ("clip_file", "Clip file"), ("youtube", "YouTube link")):
        if getattr(a, k, None):
            p[name] = {"url": getattr(a, k)}
    if getattr(a, "score", None) is not None:
        p["Score"] = {"number": a.score}
    if getattr(a, "views", None) is not None:
        p["Views"] = {"number": a.views}
    if getattr(a, "views_band", None):
        p["Predicted views"] = {"select": {"name": a.views_band}}
    return p


def find(video_id):
    r = call("POST", f"/databases/{DATABASE}/query", {"filter": {"property": "Video ID", "rich_text": {"equals": video_id}}})
    return (r.get("results") or [None])[0]


def find_title(lane, title):
    r = call("POST", f"/databases/{DATABASE}/query", {"filter": {"and": [
        {"property": "Lane", "select": {"equals": lane}}, {"property": "Title", "title": {"equals": title[:200]}}]}})
    return (r.get("results") or [None])[0]


def add(a):
    existing = (find(a.video_id) if a.video_id else None) or find_title(a.lane, a.title)
    p = props(a)
    if existing:
        call("PATCH", f"/pages/{existing['id']}", {"properties": p})
        print(f"updated card: {a.lane} {a.title[:60]}")
        return existing["id"]
    p.setdefault("Stage", {"status": {"name": "Picked"}})
    p["Date"] = {"date": {"start": dt.date.today().isoformat()}}
    page = call("POST", "/pages", {"parent": {"database_id": DATABASE}, "properties": p})
    print(f"new card: {a.lane} {a.title[:60]}")
    return page["id"]


def move(a):
    card = find(a.video_id)
    if not card:
        sys.exit(f"no card with Video ID {a.video_id}")
    call("PATCH", f"/pages/{card['id']}", {"properties": props(a)})
    print(f"moved {a.video_id} -> {a.stage or '(same stage)'}")


def picks(a):
    """Today's who's-hot picks as Picked cards (hot.py output)."""
    d = json.loads(Path(a.file).read_text())
    rows = []
    if a.lane == "SC":
        for r in [r for r in d if r.get("in_our_lane")][: a.top]:
            ev = (r.get("ref_titles") or r.get("kick_top") or r.get("lsf") or [""])[0]
            vod = (r.get("latest_vod") or {}).get("url")
            rows.append((f"{r['login']}: today's stream", f"{r['login']} ({r['site']})", f"who's hot score {r['score']}; {ev}", vod))
    else:
        for e in (d.get("sources") or [])[: a.top]:
            rows.append((f"{e['title'][:120]}", e.get("channel") or e.get("handle"),
                         f"{e['views']:,} views, {e['lift']}x the show's usual" + (f"; trend: {', '.join(e['trend_match'])}" if e.get("trend_match") else ""),
                         e.get("url")))
    for title, who, why, src in rows:
        add(argparse.Namespace(lane=a.lane, title=title, who=who, why=why, source=src, video_id=None, stage=None, note=None,
                               clip_file=None, youtube=None, score=None, views=None, views_band=None))


def test(a):
    cid = add(argparse.Namespace(lane="SC", title="Board connection test (GitHub can write here)", who="pipeline",
                                 why=f"written by GitHub Actions at {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC",
                                 source=None, video_id="TEST-board-connection", stage="Skipped",
                                 note="Safe to delete. Proves the NOTION_TOKEN secret works.", clip_file=None, youtube=None,
                                 score=None, views=None, views_band=None))
    print("board connection works; test card id", cid)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("add", "move"):
        x = sub.add_parser(name)
        x.add_argument("--lane", choices=LANES); x.add_argument("--title"); x.add_argument("--stage", choices=STAGES)
        x.add_argument("--video-id"); x.add_argument("--who"); x.add_argument("--why"); x.add_argument("--source")
        x.add_argument("--clip-file"); x.add_argument("--youtube"); x.add_argument("--score", type=float)
        x.add_argument("--views", type=float); x.add_argument("--views-band", choices=BANDS); x.add_argument("--note")
    pk = sub.add_parser("picks"); pk.add_argument("--lane", choices=("SC", "WC"), required=True)
    pk.add_argument("--file", required=True); pk.add_argument("--top", type=int, default=5)
    sub.add_parser("test")
    a = ap.parse_args()
    if a.cmd == "add" and not (a.lane and a.title):
        sys.exit("add needs --lane and --title")
    {"add": add, "move": move, "picks": picks, "test": test}[a.cmd](a)


if __name__ == "__main__":
    main()
