"""The film queue: which accepted polish becomes a video next, and its bookkeeping in ticket.json.

Why: making videos inside the polish check (one long job for a whole batch) hit GitHub's 5-hour limit on 10 Nov
when Kaggle's two GPU slots were busy, and the films after it were simply lost. Now the check only marks a ticket
"accepted"; the Film queue workflow makes ONE video per run, saves the result, and starts itself again.
Nothing is lost if a run dies: a ticket left "making" for too long is retried, at most MAX_TRIES times.

    python tools/film_queue.py next              -> prints the ticket folder to make next (nothing if empty)
    python tools/film_queue.py env <ticket>      -> shell lines: ISSUE= EPISODE= DRAFT= NAME= TRIES=
    python tools/film_queue.py set <ticket> <status> [video-url]
"""
import datetime as dt
import json
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_TRIES = 3
RETRY_AFTER = dt.timedelta(minutes=20)    # a failed video waits a little (Kaggle busy, provider hiccup)
STALE_AFTER = dt.timedelta(hours=6)       # a "making" ticket older than this was killed mid-run: retry it


def now():
    return dt.datetime.now(dt.timezone.utc)


def when(s):
    try:
        return dt.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def tickets(root=ROOT):
    for p in sorted((root / "polish" / "film").glob("*/ticket.json")):
        try:
            yield p.parent, json.loads(p.read_text())
        except (OSError, ValueError):
            continue


def pick(root=ROOT, at=None):
    """The next ticket to make: accepted first (oldest), then failed ones due for a retry, then stale 'making'."""
    at = at or now()
    best = None
    for d, t in tickets(root):
        st, tries, checked = t.get("status"), int(t.get("tries", 0)), when(t.get("checked"))
        if st == "accepted":
            key = (0, checked)
        elif st == "video-failed" and tries < MAX_TRIES and at - checked >= RETRY_AFTER:
            key = (1, checked)
        elif st == "making" and tries < MAX_TRIES and at - when(t.get("started")) >= STALE_AFTER:
            key = (2, checked)
        else:
            continue
        if best is None or key < best[0]:
            best = (key, d)
    return best[1] if best else None


def set_status(tdir, status, video="", at=None):
    p = Path(tdir) / "ticket.json"
    t = json.loads(p.read_text())
    stamp = (at or now()).isoformat(timespec="seconds")
    t["status"], t["checked"] = status, stamp
    if status == "making":
        t["tries"] = int(t.get("tries", 0)) + 1
        t["started"] = stamp
    if status == "accepted":
        t["tries"] = 0
    if video:
        t["video"] = video
    p.write_text(json.dumps(t, indent=1))
    return t


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "next":
        d = pick()
        if d:
            print(d.relative_to(ROOT).as_posix())
        return 0
    if cmd == "env":
        tdir = Path(argv[2])
        t = json.loads((ROOT / tdir / "ticket.json").read_text())
        ok = (re.fullmatch(r"episodes/[a-z0-9_]+/[0-9]{3}-[a-z0-9-]+", t.get("episode", ""))
              and re.fullmatch(r"[A-Za-z0-9._-]+", t.get("draft", "")) and str(t.get("issue", "")).isdigit())
        if not ok:
            print(f"bad ticket {tdir}", file=sys.stderr)
            return 1
        for k, v in {"ISSUE": t["issue"], "EPISODE": t["episode"], "DRAFT": t["draft"],
                     "NAME": tdir.name, "TRIES": int(t.get("tries", 0))}.items():
            print(f"{k}={shlex.quote(str(v))}")
        return 0
    if cmd == "set":
        set_status(ROOT / argv[2], argv[3], argv[4] if len(argv) > 4 else "")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
