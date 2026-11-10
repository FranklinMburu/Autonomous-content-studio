"""Offline test: the pipeline can save its state when another commit landed first, on a machine with NO git
identity (like a GitHub runner). On 7 Nov the rebase after a rejected push failed with "Committer identity unknown".

    python tests/test_git_identity.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
results = []


def check(name, cond):
    results.append(bool(cond))
    print(("PASS  " if cond else "FAIL  ") + name)


def sh(*a, cwd, env):
    return subprocess.run(list(a), cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout


def main():
    tmp = Path(tempfile.mkdtemp())
    # no global/system git config at all, so git has no name or email unless the pipeline gives one
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "EMAIL"))}
    env.update(HOME=str(tmp), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    ident = ["-c", "user.name=t", "-c", "user.email=t@example.com"]   # only for setting up the test repos

    remote, a, b = tmp / "remote.git", tmp / "a", tmp / "b"
    sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp, env=env)
    sh("git", "clone", "-q", str(remote), str(a), cwd=tmp, env=env)
    (a / "pipeline").mkdir()
    (a / "pipeline" / "state.json").write_text("{}\n")
    sh("git", "add", "-A", cwd=a, env=env)
    sh("git", *ident, "commit", "-q", "-m", "start", cwd=a, env=env)
    sh("git", "push", "-q", "origin", "HEAD:main", cwd=a, env=env)
    sh("git", "clone", "-q", str(remote), str(b), cwd=tmp, env=env)

    # another run lands a commit first (a different file, like a polish ticket)
    (b / "other.txt").write_text("other run\n")
    sh("git", "add", "-A", cwd=b, env=env)
    sh("git", *ident, "commit", "-q", "-m", "other run", cwd=b, env=env)
    sh("git", "push", "-q", "origin", "HEAD:main", cwd=b, env=env)

    # this run changes its state and saves through the real commit_and_push, with the identity-free environment
    (a / "pipeline" / "state.json").write_text('{"moved": "attention"}\n')
    os.environ.clear(); os.environ.update(env)
    from studio.pipeline import run, store
    store.ROOT = a
    run.time.sleep = lambda s: None
    try:
        ok, err = run.commit_and_push("pipeline: save state"), ""
    except Exception as e:  # noqa: BLE001
        ok, err = False, str(e)
    check(f"state is saved after a rejected push, with no git identity set {err[:120]}", ok)
    log = sh("git", "log", "--format=%s|%an", "origin/main", cwd=a, env=env).splitlines()
    check("both runs' commits are on main (nothing overwritten)",
          any(l.startswith("other run|") for l in log) and any(l.startswith("pipeline: save state|") for l in log))
    check("the state commit is signed with the repo's no-reply identity",
          any(l == "pipeline: save state|Franklin Mburu" for l in log))

    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
