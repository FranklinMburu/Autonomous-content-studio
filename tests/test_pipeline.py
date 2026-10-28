"""Offline tests for the trusted pipeline: no keys, no network, no models (fakes stand in for the brain and GitHub).

    python tests/test_pipeline.py
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
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
    from studio.pipeline import gates, polish, store

    script = json.loads((ROOT / "scripts" / "wrinkly_fingers.json").read_text(encoding="utf-8")
                        .replace("Scientists are still arguing", "Researchers keep arguing"))
    narr = " ".join(gates.narration(script))
    source_text = ("Finger wrinkling. " + " ".join(gates.strings_in(script)) + " The response depends on intact nerves; it was described in 1936. "
                   "Researchers think the ridges may improve grip on wet objects. ") * 6
    src_url = script["sources"][0]["url"]
    sources = [{"url": src_url, "title": "Finger wrinkling", "text": source_text}]
    for s in script["sources"]:
        s["url"] = src_url
    icons = sorted(set(gates.icon_names(script)))

    # ---------------------------------------------------------- numbers gate
    check("number words are read as values", gates.numbers("twenty-five cats and 1,500 dogs") == {25.0, 1500.0})
    check("a spoken number matches the same number in digits", gates.new_numbers("forty dogs", ["We studied 40 dogs."]) == [])
    check("a number missing from the sources is caught", gates.new_numbers("forty-seven percent", ["We studied 40 dogs."]) == [47])
    check("small everyday numbers and source years are allowed",
          gates.new_numbers("two cats in 1936", ["described in 1936"]) == [])

    # ---------------------------------------------------------- script gate
    good = gates.check_script(copy.deepcopy(script), sources, icons, stage="draft")
    check("a good script passes the draft gate", good == [])
    bad = copy.deepcopy(script)
    bad["beats"][0]["icon"] = "dragon"
    bad["beats"][0]["lines"] = ["Did you know that wrinkly bath fingers are a clever trick your nerves play on you every day?"]
    bad["sources"].append({"claim": "x", "url": "https://example.com/made-up"})
    bad["beats"][1]["lines"].append("Ninety-three percent of people never notice.")
    probs = " | ".join(gates.check_script(bad, sources, icons, stage="draft"))
    check("unknown icon is an error (never swapped for a look-alike)", "icon 'dragon'" in probs)
    check("hook over 14 words is an error", "hook is" in probs)
    check("banned phrase is an error", "banned phrases" in probs)
    check("cited URL outside the frozen sources is an error", "not in the source list" in probs)
    check("invented number is an error", "93" in probs)
    pol = copy.deepcopy(script)
    pol["beats"][2]["lines"][0] = "In 1936, doctors at Harvard noticed something odd."
    pprobs = " | ".join(gates.check_script(pol, sources, icons, stage="polished", draft=script))
    check("polish may not add names absent from the draft and sources", "Harvard" in pprobs)
    check("a near-copy of an existing script is rejected",
          "too similar" in " | ".join(gates.check_script(copy.deepcopy(script), sources, icons, others=[narr])))

    # ---------------------------------------------------------- store
    item_id, f = store.create("Why do fingers wrinkle in water?", day="20261028")
    check("create makes an item in the queue", store.find(item_id)[0] == "queue")
    try:
        store.create("why do FINGERS wrinkle in water", day="20261029")
        dup = False
    except store.StoreError:
        dup = True
    check("the same topic (different case/punctuation) is refused as a duplicate", dup)
    store.save_sources(f, sources)
    store.write_json(f / "draft.json", script)
    store.write_json(f / "allowed_icons.json", icons)
    store.write_json(f / "draft_check.json", {"fact_check": {"results": [], "counts": {}}})
    try:
        store.move(item_id, "published", "skip ahead")
        illegal = False
    except store.StoreError:
        illegal = True
    check("an illegal move (queue -> published) is refused", illegal and store.find(item_id)[0] == "queue")
    rec = store.read_json(f / "sources" / "01.json")
    rec["text"] += " tampered"
    store.write_json(f / "sources" / "01.json", rec)
    try:
        store.load_sources(f)
        tamper = False
    except store.StoreError:
        tamper = True
    check("a frozen source edited after research is detected", tamper)
    store.save_sources(f, sources)

    # ---------------------------------------------------------- polish CLI (offline)
    check("polish list shows the waiting item", polish.waiting() == [item_id])
    store.write_json(f / "polished.json", script)
    check("polish check passes a good polished script", polish.check(item_id) == [])
    worse = copy.deepcopy(script)
    worse["beats"][-1]["lines"][-1] = "And that is all"
    store.write_json(f / "polished.json", worse)
    check("polish check fails a script without a proper final sentence", any("final line" in p for p in polish.check(item_id)))
    (f / "polished.json").unlink()

    # ---------------------------------------------------------- the PR gate, end to end with fakes
    repo = tmp / "repo"
    os.environ["PIPELINE_DIR"] = str(repo / "pipeline")
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    g = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout
    g("config", "user.email", "t@t"); g("config", "user.name", "t")
    store.ROOT = repo
    from studio.pipeline import run
    run.store.ROOT = repo
    item2, f2 = store.create("Why do fingers wrinkle in water?", day="20261028")
    store.save_sources(f2, sources)
    store.write_json(f2 / "draft.json", script)
    store.write_json(f2 / "allowed_icons.json", icons)
    store.write_json(f2 / "draft_check.json", {})
    item3, f3 = store.create("Why do cats purr?", day="20261028")
    store.save_sources(f3, sources)
    store.write_json(f3 / "draft.json", script)
    store.write_json(f3 / "allowed_icons.json", icons)
    (repo / "topics-done.txt").write_text("", encoding="utf-8")
    g("add", "-A"); g("commit", "-qm", "init")
    g("checkout", "-qb", "claude/polish-x")
    store.write_json(f2 / "polished.json", script)
    store.write_json(f3 / "polished.json", worse)
    g("add", "-A"); g("commit", "-qm", "polish")
    g("checkout", "-q", "main")

    calls = {"comments": [], "closed": [], "dispatched": []}
    fake_gh = types.SimpleNamespace(
        comment=lambda n, t: calls["comments"].append(t), close_pr=lambda n: calls["closed"].append(n),
        delete_branch=lambda b: None, dispatch=lambda w, **k: calls["dispatched"].append(w))
    sys.modules["studio.pipeline.github"] = fake_gh
    import studio.pipeline as pkg
    pkg.github = fake_gh

    def fake_git(*args, check=True):
        if args[:2] == ("fetch", "-q"):
            return ""
        args = tuple(a.replace("pr-7", "claude/polish-x") for a in args)
        r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
        if check and r.returncode:
            raise RuntimeError(r.stderr)
        return r.stdout
    run.git = fake_git
    def fake_commit(msg):
        calls.setdefault("commits", []).append(msg)
        g("add", "-A"); subprocess.run(["git", "-C", str(repo), "commit", "-qm", msg], capture_output=True)
    run.commit_and_push = fake_commit

    def fake_gate_one(iid, polished):
        probs = polish.check(iid, polished)
        rep = {"at": "now", "offline": probs, "score": {"score": 4, "reason": "fine"},
               "fact_check": {"counts": {"supported": 5, "partial": 0, "unsupported": 0}}}
        return (not probs), rep
    run.gate_one = fake_gate_one
    run.cmd_gate_pr(7, author="FranklinMburu", head_ref="claude/polish-x")
    check("gate accepts the good polish and moves it to ready", store.find(item2)[0] == "ready")
    check("gate rejects the bad polish, keeps it queued with the reason",
          store.find(item3)[0] == "queue" and store.read_json(f3 / "feedback.json") and
          store.read_json(f3 / "item.json")["attempts"] == 1)
    check("gate never leaves the PR's polished.json in the queue unaccepted", not (f3 / "polished.json").exists())
    check("gate comments, closes the PR and starts the render", calls["closed"] == [7] and calls["dispatched"]
          and "accepted" in calls["comments"][0])

    calls["closed"].clear()
    run.cmd_gate_pr(8, author="someone-else")
    check("a pull request from anyone but the owner is closed without running anything", calls["closed"] == [8])

    g("checkout", "-qb", "claude/sneaky")
    (repo / "studio_evil.py").write_text("print('x')")
    store.write_json(store.folder("queue", item3) / "polished.json", script)
    g("add", "-A"); g("commit", "-qm", "sneaky")
    g("checkout", "-q", "main")
    run.git = lambda *a, check=True: fake_git(*(x.replace("pr-9", "claude/sneaky") for x in a), check=check)
    calls["closed"].clear(); calls["comments"].clear()
    run.cmd_gate_pr(9, author="FranklinMburu")
    check("a pull request touching any other file is rejected outright",
          calls["closed"] == [9] and "Not allowed" in calls["comments"][0] and store.find(item3)[0] == "queue")

    # ---------------------------------------------------------- status + topics
    md = run.status_markdown()
    check("status shows each stage", "Waiting for polish" in md and "| Ready to render | 1 |" in md)
    (repo / "topics.txt").write_text("Why do cats purr?\nWhy does ice float?\n# comment\n", encoding="utf-8")
    check("topics already in the pipeline are skipped", run.topics_todo() == ["Why does ice float?"])

    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
