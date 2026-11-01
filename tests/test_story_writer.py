"""Offline test of the story writer's flow (studio/story/writer.py) with fake AI calls: no keys, no network, no voice.

    python tests/test_story_writer.py

Checks: stages run in order, fact repair, only broken storyboard shots are sent back for repair (and merged),
every stage is saved, and a second run of the same topic resumes instead of redoing the work.
"""
import copy, json, shutil, sys, tempfile, types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
fails = 0


def ok(cond, msg):
    global fails
    print(("PASS " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


EX = json.loads((ROOT / "studio" / "story" / "example_storyboard.json").read_text(encoding="utf-8"))
SCRIPT = {"title": "The Doctor Who Scrubbed", "beats": [{"lines": [l]} for l in EX["narration"]],
          "claims": [{"claim": "x", "url": "https://example.org/a"}], "key_words": ["germs"]}
log_calls = []


class R:  # stands in for ailayer.Result
    def __init__(self, data, ref="fake:model"):
        self.data, self.ref, self.attempts = data, ref, [{"ref": ref, "ok": True, "latency_s": 1.0}]


def fake_ask(prompt, **kw):
    if "strict editor" in prompt:
        log_calls.append("logic"); return R({"issues": []})
    if "Rewrite ONLY these shots" in prompt:
        log_calls.append("repair:" + prompt.split("Rewrite ONLY these shots: ")[1].split(".")[0])
        good = [sh for sh in EX["storyboard"]["shots"] if sh["name"] == "cut"]
        return R({"shots": copy.deepcopy(good)})
    if "Design the storyboard" in prompt:
        log_calls.append("storyboard")
        b = copy.deepcopy(EX["storyboard"])
        b["shots"][3]["items"][1]["name"] = "dragon"  # one broken shot ("cut")
        return R(b)
    if "NOT supported" in prompt:
        log_calls.append("fact_repair"); return R(copy.deepcopy(SCRIPT))
    raise AssertionError("unexpected prompt")


facts = {"n": 0}


def fake_fact_check(text, sources, **kw):
    facts["n"] += 1
    bad = facts["n"] == 1  # first check finds one unsupported claim; the repaired script passes
    return {"counts": {"supported": 5, "unsupported": int(bad)}, "model": "fake",
            "results": [{"claim": "c", "verdict": "unsupported" if bad else "supported"}]}


def fake_best_of(prompt, **kw):
    log_calls.append("best_of parallel" if kw.get("parallel") else "best_of serial")
    return R(copy.deepcopy(SCRIPT), "fake:a"), {"candidates": ["fake:a"], "failed": [{"ref": "fake:b", "error": "HTTP 429",
                                                                                     "attempts": []}]}


class Source:
    def __init__(self, url, text, title=""):
        self.url, self.text, self.title = url, text, title


ail = types.ModuleType("ailayer"); ail.ask = fake_ask
sk = types.ModuleType("ailayer.skills")
sk.Source, sk.best_of, sk.fact_check = Source, fake_best_of, fake_fact_check
sk.sources_block = lambda srcs, topic, n=9000: "SOURCES"
sk.new_numbers = lambda text, srcs: []
sys.modules["ailayer"], sys.modules["ailayer.skills"] = ail, sk

from studio.story import writer, __main__ as story_main  # noqa: E402
from studio.pipeline import research as research_mod  # noqa: E402


def fake_research(topic, ask, log=print):
    log_calls.append("research")
    return [{"url": "https://example.org/a", "text": "facts", "title": "A"}], {}


def fake_narrate(script, out_dir):
    words, t = [], 0.05
    for b in script["beats"]:
        for line in b["lines"]:
            for w in line.split():
                words.append({"w": w, "start": round(t, 3), "end": round(t + 0.3, 3)}); t += 0.36
    return {"duration": round(t + 0.7, 3), "words": words}


research_mod.research = fake_research
story_main.narrate = fake_narrate
tmp = Path(tempfile.mkdtemp())
chan = tmp / "hidden_reasons"
lines = []
folder = writer.write("A test topic", chan, log=lines.append)
ok(log_calls[:2] == ["research", "best_of parallel"], f"research, then the script models in parallel {log_calls[:2]}")
ok("fact_repair" in log_calls, "an unsupported claim triggers a repair round")
ok("storyboard" in log_calls and "repair:cut" in log_calls,
   "a storyboard with one broken shot gets only that shot repaired")
sb = json.loads((folder / "storyboard.json").read_text(encoding="utf-8"))
ok(sb["shots"][3]["items"][1]["name"] == "basin" and len(sb["shots"]) == len(EX["storyboard"]["shots"]),
   "the repaired shot is merged back into the full storyboard")
ok(not (folder / "NEEDS_POLISH.md").exists(), "the final storyboard passes every check (no NEEDS_POLISH.md)")
ok(any("call: fake:a 1s ok" in l for l in lines) and any("model failed the script step: fake:b" in l for l in lines),
   "every model call is logged with its time, and failed models are named")
work = chan / "_drafts" / "a-test-topic"
ok(all((work / f).exists() for f in ("research.json", "script.json", "folder.json", "storyboard.json")),
   "every stage is saved as it completes")

log_calls.clear()
(folder / "storyboard.json").unlink()
folder2 = writer.write("A test topic", chan, log=lines.append)
ok(folder2 == folder and log_calls == [], f"a second run resumes: no research, script or storyboard calls redone {log_calls}")
shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
