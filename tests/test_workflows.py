"""Checks on the GitHub workflows and the polish tickets that run before anything reaches the schedule.

Added 6 Nov 2026 after every "Story schedule" run failed for 4 days: its "Pick the topic" step installed
requirements.txt (pycairo) without the cairo library. Nothing ran that step before the merge, so no test saw it.
Run: python tests/test_workflows.py
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
WF = ROOT / ".github" / "workflows"
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def jobs_of(path):
    """{job name: text of that job} without a YAML library (the runner's tests install nothing extra)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^jobs:\n(.*)", text, re.S | re.M)
    body = m.group(1) if m else ""
    parts = re.split(r"^  ([A-Za-z0-9_-]+):\s*$", body, flags=re.M)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def test_requirements_need_cairo():
    for wf in sorted(WF.glob("*.yml")):
        for job, text in jobs_of(wf).items():
            i = text.find("-r requirements.txt")
            if i < 0:
                continue
            check("libcairo2-dev" in text[:i], f"{wf.name}/{job}: installs the cairo library before requirements.txt")


def test_workflow_syntax():
    try:
        import yaml
    except ImportError:
        print("skip YAML parse (PyYAML not installed)")
        return
    for wf in sorted(WF.glob("*.yml")):
        try:
            d = yaml.safe_load(wf.read_text(encoding="utf-8"))
            check(isinstance(d, dict) and "jobs" in d, f"{wf.name}: valid YAML with jobs")
        except Exception as e:  # noqa: BLE001
            check(False, f"{wf.name}: YAML error {e}")


def test_schedule_slots_match():
    s = (WF / "story-schedule.yml").read_text(encoding="utf-8")
    slots = re.search(r'SLOTS="([0-9 ]+)"', s)
    check(bool(slots), "story-schedule: has the SLOTS list")
    hours = [int(h) for h in slots.group(1).split()] if slots else []
    check(len(hours) == 5, "story-schedule: 5 slots a day (agreed with Franklin)")
    head = re.search(r"Slots \(UTC\): ([0-9:, ]+)", s)
    check(bool(head) and [int(x.split(":")[0]) for x in head.group(1).split(",")] == hours,
          "story-schedule: the slot comment and the SLOTS list agree")
    check('cron: "23 * * * *"' in s, "story-schedule: wakes hourly (catches up dropped runs)")


def test_shell_scripts():
    for sh in ["tools/polish_continue.sh", "tools/commit_to_main.sh", "tools/film_produce.sh", "tools/ready_issue.sh"]:
        p = ROOT / sh
        if not p.exists():
            continue
        r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
        check(r.returncode == 0, f"{sh}: bash syntax ok {r.stderr.strip()}")


def test_polish_return_triggers():
    s = (WF / "polish-return.yml").read_text(encoding="utf-8")
    for t in ["issue_comment:", "push:", "pull_request_target:"]:
        check(t in s, f"polish-return: listens to {t[:-1]}")
    check("ref: main" in s, "polish-return: runs trusted code from main (never PR code)")
    check("head.repo.full_name == github.repository" in s, "polish-return: ignores pull requests from forks")
    check("repository_owner" in s, "polish-return: comments are read only from the owner")


def test_ticket_and_offline_check():
    """A real draft (Lister, 003) + its real polished answer must pass the offline check; a broken answer must not."""
    from studio.story import filmkit as F
    arch = ROOT / "polish" / "archive" / "draft-003-why-joseph-lister-sprayed-carbolic-acid--run10"
    final = ROOT / "episodes" / "hidden_reasons" / "003-why-joseph-lister-sprayed-carbolic-acid-"
    if not arch.exists() or not (final / "film.json").exists():
        print("skip ticket test (archive not present)")
        return
    with tempfile.TemporaryDirectory() as tmp:
        ep = Path(tmp) / "episodes" / "hidden_reasons" / final.name
        shutil.copytree(arch, ep)
        t = F.make_ticket(ep, "draft-test", 99, root=Path(tmp) / "polish" / "film")
        check((t / "PROMPT.md").read_text(encoding="utf-8").startswith("You are the polish step"), "ticket: PROMPT.md written")
        check(json.loads((t / "ticket.json").read_text())["issue"] == 99, "ticket: ticket.json links the issue")
        check(not any(p.suffix in {".wav", ".mp4"} for p in (t / "files").iterdir()), "ticket: text files only")
        script = json.loads((final / "script.json").read_text(encoding="utf-8"))
        film = json.loads((final / "film.json").read_text(encoding="utf-8"))
        (t / "answer.json").write_text(json.dumps({"script": {k: script[k] for k in ("title", "beats", "key_words", "claims") if k in script},
                                                   "film": film}), encoding="utf-8")
        probs = F.check_answer(t, log=lambda *a: None)
        check(not [p for p in probs if not p.startswith("script:")], f"check-answer: the real polished Lister film passes the film checks {probs[:3]}")
        (t / "answer.json").write_text('{"script": {"title": "x"}}', encoding="utf-8")
        check(bool(F.check_answer(t, log=lambda *a: None)), "check-answer: a broken answer is refused")
        tm = F.estimate_timing(script)
        check(len(tm["words"]) == sum(len(l.split()) for b in script["beats"] for l in b["lines"]),
              "estimate_timing: one entry per spoken word")


def test_open_tickets_are_well_formed():
    for tj in (ROOT / "polish" / "film").glob("*/ticket.json"):
        t = json.loads(tj.read_text(encoding="utf-8"))
        ok = re.fullmatch(r"episodes/[a-z0-9_]+/[0-9]{3}-[a-z0-9-]+", t.get("episode", "")) and t.get("draft") and t.get("issue")
        check(bool(ok), f"{tj.parent.name}: ticket.json has episode, draft and issue")
        check((tj.parent / "PROMPT.md").exists() and (tj.parent / "files" / "script.json").exists(),
              f"{tj.parent.name}: PROMPT.md and files/script.json present")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall workflow checks pass")
    sys.exit(1 if FAILS else 0)
