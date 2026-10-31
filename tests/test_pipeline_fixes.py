"""Offline tests for the 30 Oct fixes: research filters, retries, the polish-stall alert and backup labelling.

    python tests/test_pipeline_fixes.py
"""
import json
import os
import sys
import tempfile
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
results = []


def check(name, cond):
    results.append(bool(cond))
    print(("PASS  " if cond else "FAIL  ") + name)


def main():
    tmp = Path(tempfile.mkdtemp())
    os.environ["PIPELINE_DIR"] = str(tmp / "pipeline")
    from studio.pipeline import research, run, store

    # research filters
    check("'yourself' is not required in a source", research.keywords("Why can't you tickle yourself?") == ["tickle"])
    check("plural duplicates collapse", research.keywords("Why do you yawn when someone else yawns?") == ["yawn"])
    check("an album article is rejected",
          bool(research.OFF_TOPIC_LEAD.search("Tired of Hanging Around is the second studio album by the band")))
    check("a science article is kept", not research.OFF_TOPIC_LEAD.search("Tickling is the act of touching the body"))

    # retry: attention items that stopped in drafting are re-drafted once
    calls = []
    run.commit_and_push = lambda m: None
    run.draft_one = lambda topic, lane, cfg: calls.append(topic) or ("x", "queue")
    i1, f1 = store.create("Why can't you tickle yourself?")
    store.move(i1, "attention", "drafting failed: only 0 usable source(s) found")
    i2, f2 = store.create("Do fish sleep?")
    store.move(i2, "attention", "render failed technical checks: ['loudness']")
    run.retry_attention(run.config(), None)
    check("a drafting failure is retried", calls == ["Why can't you tickle yourself?"] and not f1.exists()
          and not (store.base() / "attention" / i1).exists())
    check("a non-drafting failure is left alone", store.find(i2)[0] == "attention")
    i3, f3 = store.create("Why can't you tickle yourself?", day="20261031")
    store.move(i3, "attention", "drafting failed: again")
    calls.clear()
    run.retry_attention(run.config(), None)
    check("each topic is retried only once automatically", calls == [])
    run.retry_attention(run.config(), None, force=True)
    check("a forced retry runs anyway", calls == ["Why can't you tickle yourself?"])

    # stall alert
    created, closed = [], []
    gh = types.SimpleNamespace(ensure_label=lambda *a, **k: None, issues=lambda label: [{"number": 9}] if closed == ["open"] else [],
                               create_issue=lambda t, b, l: created.append(t) or {"number": 9},
                               comment=lambda n, t: None, update_issue=lambda n, **k: closed.append(n))
    i4, f4 = store.create("Why does ice float?")
    it = store.read_json(f4 / "item.json")
    old = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(time.time() - 60 * 3600))
    it["history"][-1]["at"] = old
    store.write_json(f4 / "item.json", it)
    store.write_json(f4 / "draft.json", {"beats": []})
    run.stall_check(gh, run.config())
    check("a script waiting 60 h opens a 'polish stalled' issue", created and "stalled" in created[0])
    store.move(i4, "attention", "drafting failed: test")
    closed.append("open")
    run.stall_check(gh, run.config())
    check("the issue closes itself when nothing is stuck", 9 in closed)

    # backup label on the upload issue
    body = run._issue_body({"title": "T", "sources": []}, "id", "https://x/v.mp4", "https://x/r",
                           {"backup": {"model": "groq:openai/gpt-oss-120b"}})
    check("a backup-polished video is labelled on its issue", "Backup polish" in body and "gpt-oss-120b" in body)
    body2 = run._issue_body({"title": "T", "sources": []}, "id", "https://x/v.mp4", "https://x/r", {})
    check("a normal video has no backup label", "Backup polish" not in body2)

    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
