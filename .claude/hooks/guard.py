#!/usr/bin/env python3
"""PreToolUse guard: Franklin's fixed lines, enforced by the computer instead of remembered in chat.

Blocks (exit code 2, message on stderr):
  1. Reading, printing or copying `.env` files or anything under a secrets path.
  2. Pushing to main/master, force-pushing, merging pull requests.
  3. Running workflows by hand, and YouTube upload / auth commands.
Everything else passes. Stdlib only. Reads the hook JSON from stdin.
Ask Franklin first if a blocked action is really needed.
"""
import json
import re
import subprocess
import sys

ENV_PATH = re.compile(r"(^|/)\.env(\.(?!example|sample|template)[\w.-]*)?$")
ENV_TOKEN = re.compile(r"(?<![\w.-])(?:[\w./~-]*/)?\.env(?:\.(?!example\b|sample\b|template\b)[\w.-]+)?(?![\w.-])")
PUSH = re.compile(r"\bgit\b[^;&|]*\bpush\b")
FORCE = re.compile(r"(\s--force\b|\s--force-with-lease\b|\s-f\b|\s\+\S)")
MAIN_REF = re.compile(r"(^|[\s:/+])(main|master)(\s|$)")
MERGE = re.compile(r"\bgh\b[^;&|]*\b(pr\s+merge|merge)\b|\bgh\s+api\b[^;&|]*\bmerge\b|\bgit\s+merge\b[^;&|]*\b(main|master)\b")
WORKFLOW = re.compile(r"\bgh\s+workflow\s+run\b|\bgh\s+run\s+(rerun|watch\s+--exit)\b|/dispatches")
YOUTUBE = re.compile(r"youtube_auth|studio\.pipeline\.youtube|pipeline[./]upload|videos\(\)\.insert")


def block(reason: str) -> None:
    sys.stderr.write(f"BLOCKED by .claude/hooks/guard.py: {reason} Ask Franklin first.\n")
    sys.exit(2)


def current_branch() -> str:
    try:
        return subprocess.check_output(["git", "symbolic-ref", "--short", "HEAD"], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def check_bash(cmd: str) -> None:
    if ENV_TOKEN.search(cmd):
        block("this command touches a .env secrets file.")
    for seg in re.split(r"[;&|]+", cmd):
        seg = " " + seg.strip()
        if PUSH.search(seg):
            if FORCE.search(seg):
                block("force-push is not allowed.")
            if MAIN_REF.search(seg):
                block("pushing to main/master is not allowed; open a pull request.")
            tail = seg.split("push", 1)[1].split()
            refs = [t for t in tail if not t.startswith("-")]
            if len(refs) <= 1 and current_branch() in ("main", "master"):
                block("a bare push while on main is not allowed; work on a branch.")
    if MERGE.search(cmd):
        block("merging pull requests is Franklin's decision.")
    if WORKFLOW.search(cmd):
        block("running workflows by hand is not allowed.")
    if YOUTUBE.search(cmd):
        block("YouTube upload or auth commands need Franklin's yes.")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    if tool == "Bash":
        check_bash(inp.get("command", ""))
        return
    for key in ("file_path", "path", "notebook_path"):
        p = inp.get(key)
        if isinstance(p, str) and ENV_PATH.search(p.replace("\\", "/")):
            block("secrets files (.env) must never be opened.")
    pat = inp.get("glob") or inp.get("pattern")
    if tool in ("Grep", "Glob") and isinstance(pat, str) and re.search(r"(^|/)\.env\b(?!\.example)", pat):
        block("secrets files (.env) must never be searched.")


if __name__ == "__main__":
    main()
