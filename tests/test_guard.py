"""The guard must block Franklin's fixed lines and let normal work pass (run: python tests/test_guard.py)."""
import json
import pathlib
import subprocess
import sys

GUARD = pathlib.Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "guard.py"


def run(tool, **inp):
    r = subprocess.run([sys.executable, str(GUARD)], input=json.dumps({"tool_name": tool, "tool_input": inp}),
                       text=True, capture_output=True)
    return r.returncode


BLOCK = [
    ("Bash", {"command": "cat .env"}),
    ("Bash", {"command": "grep KEY ./.env.local"}),
    ("Bash", {"command": "source ~/proj/.env && echo hi"}),
    ("Bash", {"command": "git push origin main"}),
    ("Bash", {"command": "git push origin HEAD:main"}),
    ("Bash", {"command": "git push --force origin feature"}),
    ("Bash", {"command": "git push -f"}),
    ("Bash", {"command": "gh pr merge 131 --squash"}),
    ("Bash", {"command": "gh workflow run film-queue.yml"}),
    ("Bash", {"command": "python youtube_auth.py"}),
    ("Bash", {"command": "echo ok && git push origin main"}),
    ("Read", {"file_path": "/repo/.env"}),
    ("Read", {"file_path": "/repo/sub/.env.production"}),
    ("Write", {"file_path": ".env"}),
    ("Grep", {"pattern": "KEY", "path": "/repo/.env"}),
]
PASS = [
    ("Bash", {"command": "git push -u origin operator/enforced-rules"}),
    ("Bash", {"command": "git push origin polish/008-why-edison-added-a-carbon-button"}),
    ("Bash", {"command": "ls -la && git status"}),
    ("Bash", {"command": "python -m studio.story.filmkit check-answer polish/film/x"}),
    ("Bash", {"command": "cat .env.example"}),
    ("Bash", {"command": "git log main --oneline"}),
    ("Bash", {"command": "gh pr create --title 'Polish: x' --body y"}),
    ("Read", {"file_path": "/repo/.env.example"}),
    ("Read", {"file_path": "/repo/docs/environment.md"}),
    ("Read", {"file_path": "/repo/CLAUDE.md"}),
]


def bare_push_on(branch):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", "-b", branch], cwd=d, check=True)
        r = subprocess.run([sys.executable, str(GUARD)], cwd=d, text=True, capture_output=True,
                           input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push"}}))
        return r.returncode


def main():
    bad = []
    if bare_push_on("main") != 2:
        bad.append("should BLOCK: bare git push while on main")
    if bare_push_on("work") != 0:
        bad.append("should PASS: bare git push while on a work branch")
    for tool, inp in BLOCK:
        if run(tool, **inp) != 2:
            bad.append(f"should BLOCK: {tool} {inp}")
    for tool, inp in PASS:
        if run(tool, **inp) != 0:
            bad.append(f"should PASS: {tool} {inp}")
    if bad:
        print("\n".join(bad))
        sys.exit(1)
    print(f"OK: {len(BLOCK)} blocked, {len(PASS)} allowed, all as expected")


if __name__ == "__main__":
    main()
