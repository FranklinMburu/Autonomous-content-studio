"""The story schedule's topic queue: episodes/<channel>/topics.txt (in order), tracked in the channel memory so a
topic is made once. When fewer than 5 remain, the free models suggest new true-story topics in the channel's style.

    python -m studio.story.topics next --channel hidden_reasons --memory used.json   # prints the topic, records it
"""
import argparse, json, re, sys
from pathlib import Path

from ..paths import ROOT
from .filmkit import load_memory

MAX_TRIES = 2   # a topic whose runs failed twice is skipped (it stays listed in the memory for a look)


def key(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def queue(channel):
    f = ROOT / "episodes" / channel / "topics.txt"
    return [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if f.exists() else []


def pending(channel, memory):
    tried = memory.get("topics", {})
    done = {key(e.get("topic", "")) for e in memory.get("episodes", [])}
    return [t for t in queue(channel) + memory.get("ideas", [])
            if key(t) not in done and tried.get(key(t), {}).get("tries", 0) < MAX_TRIES]


def suggest(channel, memory, n=10, log=print):
    """New topic ideas from the free models (true stories, a person doing something strange, a hidden reason)."""
    from ailayer import ask
    have = queue(channel) + memory.get("ideas", []) + [e.get("topic", "") for e in memory.get("episodes", [])]
    prompt = (f"Suggest {n} topics for 1-minute YouTube Shorts on the channel 'Hidden Reasons'. Each is a TRUE, well "
              "documented story (history, science, medicine, engineering) where a real person did something that looked "
              "strange or crazy, and there was a hidden reason. Write each as 'Why <person or group> <did the strange "
              "thing> (<place, year if known>)'. No myths, no legends, no living private people, no gore. "
              "Do not repeat or closely resemble these existing topics:\n" + "\n".join(f"- {t}" for t in have[-80:]) +
              '\nReturn JSON only: {"topics": ["...", ...]}')
    r = ask(prompt, json_out=True, temperature=0.9, max_tokens=1500,
            validate=lambda d: [] if isinstance(d, dict) and isinstance(d.get("topics"), list) else ['need {"topics": [...]}'])
    seen = {key(t) for t in have}
    new = [t.strip() for t in r.data["topics"] if isinstance(t, str) and 20 <= len(t) <= 160 and key(t) not in seen]
    log(f"suggested {len(new)} new topics by {r.ref}")
    return new


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.story.topics")
    ap.add_argument("cmd", choices=["next", "list"])
    ap.add_argument("--channel", default="hidden_reasons"); ap.add_argument("--memory", required=True)
    a = ap.parse_args(argv)
    mem = load_memory(a.memory)
    todo = pending(a.channel, mem)
    if a.cmd == "list":
        print("\n".join(todo)); return 0
    if len(todo) < 5:
        try:
            mem.setdefault("ideas", []).extend(suggest(a.channel, mem, log=lambda *x: print(*x, file=sys.stderr)))
            todo = pending(a.channel, mem)
        except Exception as e:  # noqa: BLE001 - the queue still has topics, or the next run tries again
            print(f"could not get new ideas: {str(e)[:200]}", file=sys.stderr)
    if not todo:
        print("", end=""); return 3
    t = todo[0]
    rec = mem.setdefault("topics", {}).setdefault(key(t), {"topic": t, "tries": 0})
    rec["tries"] += 1
    Path(a.memory).write_text(json.dumps(mem, indent=1, ensure_ascii=False), encoding="utf-8")
    print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
