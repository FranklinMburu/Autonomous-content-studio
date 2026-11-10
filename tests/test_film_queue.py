"""Offline test: the film queue picks the right ticket, retries failures, recovers dead runs and gives up after 3.

    python tests/test_film_queue.py
"""
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import film_queue as q  # noqa: E402

results = []


def check(name, cond):
    results.append(bool(cond))
    print(("PASS  " if cond else "FAIL  ") + name)


def make(root, name, **t):
    d = root / "polish" / "film" / name
    d.mkdir(parents=True)
    base = {"issue": 1, "draft": f"draft-{name}", "episode": f"episodes/hidden_reasons/{name}"}
    (d / "ticket.json").write_text(json.dumps({**base, **t}))
    return d


def main():
    T0 = dt.datetime(2026, 11, 11, 12, 0, tzinfo=dt.timezone.utc)
    iso = lambda m: (T0 - dt.timedelta(minutes=m)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp)
        check("empty queue picks nothing", q.pick(r, T0) is None)
        make(r, "001-waiting", status="waiting", checked=iso(500))
        make(r, "002-needs-fix", status="needs-fix", checked=iso(500))
        check("tickets still being polished are never made", q.pick(r, T0) is None)
        fresh_fail = make(r, "003-failed-now", status="video-failed", tries=1, checked=iso(5))
        check("a video that just failed waits before its retry", q.pick(r, T0) is None)
        old_fail = make(r, "004-failed-old", status="video-failed", tries=1, checked=iso(30))
        check("a failed video is retried after the wait", q.pick(r, T0) == old_fail)
        a2 = make(r, "005-accepted-new", status="accepted", checked=iso(10))
        a1 = make(r, "006-accepted-old", status="accepted", checked=iso(60))
        check("accepted films go first, oldest first", q.pick(r, T0) == a1)
        for d in (a1, a2, old_fail, fresh_fail):
            (d / "ticket.json").unlink(); d.rmdir()
        make(r, "007-gave-up", status="video-failed", tries=3, checked=iso(600))
        make(r, "008-attention", status="attention", tries=3, checked=iso(600))
        check("after 3 tries the queue stops (a person looks)", q.pick(r, T0) is None)
        busy = make(r, "009-making", status="making", tries=1, started=iso(60), checked=iso(60))
        check("a film being made right now is left alone", q.pick(r, T0) is None)
        busy.joinpath("ticket.json").write_text(json.dumps({**json.loads(busy.joinpath("ticket.json").read_text()),
                                                            "started": iso(400)}))
        check("a run that died mid-film (too long 'making') is picked up again", q.pick(r, T0) == busy)
        t = q.set_status(busy, "making", at=T0)
        check("each try is counted", t["tries"] == 2 and t["started"] == T0.isoformat(timespec="seconds"))
        t = q.set_status(busy, "done", "https://example/v", at=T0)
        check("a finished film records its video", t["status"] == "done" and t["video"] == "https://example/v")
    wf = (ROOT / ".github/workflows/film-queue.yml").read_text()
    check("film queue: one film at a time, never cancelled midway",
          "group: film-queue" in wf and "cancel-in-progress: false" in wf)
    check("film queue: fits inside GitHub's job limit", "timeout-minutes: 330" in wf)
    sh = (ROOT / "tools/polish_continue.sh").read_text()
    check("polish check queues the video instead of making it in the same job",
          "save_ticket accepted" in sh and "gh workflow run film-queue.yml" in sh)
    try:
        sys.path.insert(0, str(ROOT))
        from studio.story.film import read_clip
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp, "clip_x.mp4"); bad.write_bytes(b"")
            check("a broken clip falls back to the still picture (no crash)", read_clip(bad) is None)
    except ImportError:
        print("SKIP  read_clip check (pycairo not installed here)")
    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
