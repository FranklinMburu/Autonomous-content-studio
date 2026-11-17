#!/usr/bin/env python3
"""PreToolUse guard: Franklin's fixed lines, enforced by the computer instead of remembered in chat.

Blocks (exit code 2, message on stderr):
  1. Opening .env / secrets files (also globbed names like `.e*`, and printing the environment).
  2. Pushing to main/master, force/mirror/delete pushes, merging pull requests, writing to main through the API.
  3. Running or enabling workflows by hand, and YouTube upload / auth commands.
  4. Editing this guard or .claude/settings.json (Franklin changes those).
Everything else passes. Stdlib only.

HONEST LIMITS: this stops accidents and careless phrasing, not a determined bypass (variable indirection,
`cp -r .`, `xargs`, `tar`). The real controls are outside the repo: GitHub branch protection on main and a
token without merge/workflow rights (see PR notes). Ask Franklin first if a blocked action is really needed.
"""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

ENV_PATH = re.compile(r"(^|[/=])\.env(\.(?!example$|sample$|template$)[\w.-]*)?$")
SECRET_DIR = re.compile(r"(^|/)(secrets|\.ssh|\.aws)(/|$)|\.config/gh(/|$)")
GUARD_FILES = re.compile(r"(^|/)\.claude/(hooks/|settings(\.local)?\.json$)")
MAIN = ("main", "master", "refs/heads/main", "refs/heads/master")
API_DANGER = re.compile(r"merge|dispatches|rerun|git/refs|/contents/|branches/[^/]+/protection|actions/workflows|mergePullRequest")
SEPARATORS = set(";&|()")


def block(reason: str) -> None:
    sys.stderr.write(f"BLOCKED by .claude/hooks/guard.py: {reason} Ask Franklin first.\n")
    sys.exit(2)


def current_branch() -> str:
    try:
        return subprocess.check_output(["git", "symbolic-ref", "--short", "HEAD"], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def segments(cmd: str):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.whitespace = " \t\r"
    try:
        toks = list(lex)
    except ValueError:
        block("this command could not be parsed safely.")
    out, seg = [], []
    for t in toks:
        if t == "\n" or (t and set(t) <= SEPARATORS):
            if seg:
                out.append(seg)
                seg = []
        else:
            seg.append(t)
    if seg:
        out.append(seg)
    return out


def check_token(t: str) -> None:
    if ENV_PATH.search(t):
        block("this command touches a .env secrets file.")
    if SECRET_DIR.search(t):
        block("this command touches a secrets folder.")
    base = os.path.basename(t)
    if base.startswith(".") and any(c in base for c in "*?[") and fnmatch.fnmatch(".env", base):
        block("this glob would match .env.")


def check_git(args) -> None:
    while args and args[0].startswith("-"):
        args = args[2:] if args[0] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else args[1:]
    if not args:
        return
    sub, rest = args[0], args[1:]
    if sub == "config" and any(a.startswith("alias.") for a in rest):
        block("git aliases can hide blocked commands.")
    if sub != "push":
        return
    for a in rest:
        if a in ("--force", "--mirror", "--all", "--delete") or a.startswith("--force-with-lease"):
            block(f"`git push {a}` is not allowed.")
        if re.match(r"^-[a-zA-Z]*[fd][a-zA-Z]*$", a):
            block("force or delete pushes are not allowed.")
    pos = [a for a in rest if not a.startswith("-")]
    refs = pos[1:]
    for r in refs:
        if r.startswith("+"):
            block("force-pushing a ref is not allowed.")
        if r.split(":")[-1] in MAIN:
            block("pushing to main/master is not allowed; open a pull request.")
    if (not refs or refs == ["HEAD"]) and current_branch() in ("main", "master"):
        block("pushing while on main is not allowed; work on a branch.")


def check_gh(args) -> None:
    words = [a for a in args if not a.startswith("-")]
    pairs = set(zip(words, words[1:]))
    for bad in (("pr", "merge"), ("workflow", "run"), ("workflow", "enable"), ("run", "rerun"), ("alias", "set")):
        if bad in pairs:
            block(f"`gh {' '.join(bad)}` is not allowed.")
    if "api" in words:
        method = ""
        for i, a in enumerate(args):
            if a in ("-X", "--method") and i + 1 < len(args):
                method = args[i + 1].upper()
        has_fields = any(a in ("-f", "-F", "--field", "--raw-field", "--input") for a in args)
        nonget = method in ("PUT", "PATCH", "POST", "DELETE") or (has_fields and method in ("", "POST"))
        if "mergePullRequest" in " ".join(args) or (nonget and API_DANGER.search(" ".join(args))):
            block("this GitHub API call could merge, rewrite main or start workflows.")


def check_http(t) -> None:
    joined = " ".join(t)
    if "api.github.com" in joined and re.search(r"-X\s*(PUT|PATCH|POST|DELETE)|--request\s+(PUT|PATCH|POST|DELETE)|(^|\s)(-d|--data\S*)\b", joined):
        if API_DANGER.search(joined):
            block("this GitHub API call could merge, rewrite main or start workflows.")


def analyze(tokens, depth=0) -> None:
    i = 0
    while i < len(tokens) and re.match(r"^\w+=", tokens[i]):
        i += 1
    t = tokens[i:]
    if not t or depth > 3:
        return
    for tok in t:
        check_token(tok)
    prog = os.path.basename(t[0])
    if prog in ("bash", "sh", "zsh") and "-c" in t and t.index("-c") + 1 < len(t):
        check_command(t[t.index("-c") + 1], depth + 1)
    elif prog == "eval":
        check_command(" ".join(t[1:]), depth + 1)
    elif prog == "printenv" or (prog == "env" and len(t) == 1):
        block("printing the environment could reveal secrets.")
    elif prog in ("sudo", "nohup", "time", "command", "exec", "env", "xargs"):
        analyze([a for a in t[1:] if not a.startswith("-")], depth + 1)
    elif prog == "git":
        check_git(t[1:])
    elif prog == "gh":
        check_gh(t[1:])
    elif prog in ("curl", "wget"):
        check_http(t)
    joined_prog = " ".join(t[:3])
    if re.search(r"youtube_auth|yt_login|studio[./]pipeline[./]youtube|pipeline/youtube\.py", joined_prog + " " + " ".join(t)):
        block("YouTube upload or auth commands need Franklin's yes.")


def check_command(cmd: str, depth=0) -> None:
    for seg in segments(cmd):
        analyze(seg, depth)


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return
    try:
        data = json.loads(raw)
    except Exception:
        block("the hook input could not be read.")
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    if tool == "Bash":
        check_command(inp.get("command", ""))
        return
    for key in ("file_path", "path", "notebook_path"):
        p = inp.get(key)
        if isinstance(p, str):
            p = p.replace("\\", "/")
            if ENV_PATH.search(p) or SECRET_DIR.search(p):
                block("secrets files must never be opened.")
            if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit") and GUARD_FILES.search(p):
                block("the guard and .claude/settings.json are Franklin's to change.")
    pat = inp.get("glob") or inp.get("pattern")
    if tool in ("Grep", "Glob") and isinstance(pat, str) and re.search(r"(^|/)\.env\b(?!\.example)", pat):
        block("secrets files must never be searched.")


if __name__ == "__main__":
    main()
