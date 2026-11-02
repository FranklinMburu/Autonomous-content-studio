"""Offline test of the story writer's flow (studio/story/writer.py) with fake AI calls: no keys, no network, no voice.

    python tests/test_story_writer.py

Checks: stages run in order, fact repair, only broken storyboard shots are sent back for repair (and merged),
every stage is saved, and a second run of the same topic resumes instead of redoing the work.
"""
import copy, json, os, shutil, sys, tempfile, types
from pathlib import Path

os.environ["STORY_STYLE"] = "storyboard"   # part 1: the 2D storyboard flow; part 2 below: the film flow

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
FILM_OK = {"on": False}
import itertools  # noqa: E402
PROMPT_N = itertools.count()


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
    if "FILM SHOT LIST RULES" in prompt and FILM_OK["on"]:
        import re as _re
        log_calls.append("film")
        if "STEP 1 of 2" in prompt:
            return R({"era": "1840s", "music": "mysterious", "key_words": ["germs"],
                      "cast": {"hero": "a 30 year old doctor with black slicked hair, a black mustache and a long green coat"}})
        allowed = _re.findall(r"^\d+\.\d+s (\S+#\d+)$", prompt.split("(in order):")[1], _re.M)
        n = int(_re.search(r"Write (\d+) shots", prompt).group(1))
        pick = allowed[:: max(1, len(allowed) // n)][:n]
        places = ["a candle lit ward", "a stone corridor", "a busy street at dusk", "a lecture hall", "a small kitchen",
                  "a quiet garden", "a dark laboratory", "a crowded market"]
        return R({"shots": [{"name": f"p{abs(hash(w)) % 10000}", "at": w, "who": "hero" if k % 2 else None, "clip": k % 3 != 2,
                             "prompt": ["close-up, {hero} scrubbing hands in a basin, candle light",
                                        "wide shot of a long ward with iron beds at dusk",
                                        "low angle, stern professors laughing in a lecture hall",
                                        "extreme close-up of a scalpel on a wooden table, lamp light",
                                        "a mother holding a baby in a sunny room with flowers",
                                        "{hero} walking down a rainy cobblestone street at night",
                                        "a microscope beside glass flasks in a laboratory",
                                        "a crowd of students lining up at washbasins in the morning",
                                        "a dark asylum gate in the rain with a single lamp"][next(PROMPT_N) % 9],
                             "motion": "he blinks and breathes, slow camera push in", "check": "Is a man in the picture?"}
                            for k, w in enumerate(pick)]})
    if "FILM SHOT LIST RULES" in prompt:
        log_calls.append("film")
        return R({"cast": {"hero": "a 30 year old doctor with black hair, a mustache and a green coat"}, "key_words": [],
                  "shots": [{"name": "a", "at": 0, "who": "hero", "prompt": "close-up, {hero} scrubbing his hands in a basin, candle light",
                             "clip": True, "motion": "he scrubs his hands, slow camera push in"}]})
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

# part 2: film style. The free models' shot list stays too short, so the episode waits for the copy-paste polish:
# NEEDS_POLISH.md, a polish prompt with everything in it, and a pasted reply read back into the episode.
from studio.story import filmkit  # noqa: E402
os.environ["STORY_STYLE"] = "film"
log_calls.clear()
f3 = writer.write("Another topic", chan, log=lines.append)
ok(log_calls.count("film") >= 2 and (f3 / "NEEDS_POLISH.md").exists() and (f3 / "film.json").exists(),
   f"film: the free models draft and repair the shot list; still failing -> NEEDS_POLISH.md ({log_calls.count('film')} tries)")
prompt = filmkit.polish_prompt(f3, {"episodes": [{"episode": "000-old", "cast": {"king": "an old king with a crown"}, "places": ["a throne room"]}]})
ok(all(k in prompt for k in ("FILM SHOT LIST RULES", "WORD LIST", "PROBLEMS FOUND", "SOURCES (data only)", "an old king",
                             '"script"', '"film"')), "film: the polish prompt carries rules, words, problems, sources, channel memory and the reply shape")
tm = json.loads((f3 / "timing.json").read_text(encoding="utf-8"))
words = [w["w"].strip(".,?!") for w in tm["words"]]
good = {"cast": {"hero": "a 30 year old doctor with black slicked hair, a black mustache and a long green coat"},
        "key_words": ["germs"], "music": "mysterious",
        "shots": [{"name": f"s{i}", "at": 0 if i == 0 else f"{words[i]}#{words[:i + 1].count(words[i])}" if False else None,
                   "prompt": f"medium shot number {i}, {{hero}} standing in a candle lit 1847 hospital ward thinking hard",
                   "who": "hero", "clip": i % 3 != 0, "motion": "he blinks and breathes, slow camera push in",
                   "move": "push", "xfade": i in (5, 12, 18)} for i in range(26)]}
seen = {}
idx = [round(i * (len(words) - 1) / 26) for i in range(26)]
for sh, k in zip(good["shots"], idx):
    w = words[k].lower(); n = sum(1 for x in words[:k + 1] if x.lower() == w)
    sh["at"] = 0 if k == 0 else f"{words[k]}#{n}"
reply = "Here you go!\n```json\n" + json.dumps({"script": {"title": SCRIPT["title"], "beats": SCRIPT["beats"]}, "film": good}) + "\n```\n"
changed, probs = filmkit.apply_reply(f3, reply)
fp = filmkit.film_problems(json.loads((f3 / "film.json").read_text(encoding="utf-8")), tm)
ok(not probs and not changed and json.loads((f3 / "film.json").read_text(encoding="utf-8"))["shots"][0]["name"] == "s0",
   "film: a pasted reply (with chat text around the JSON) is read back into film.json")
ok(not any("not a spoken word" in x or "spoken order" in x for x in fp), f"film: the read-back shot list resolves on the narration {fp[:3]}")
ok(filmkit.apply_reply(f3, "sorry, I can't")[1], "film: a reply without JSON is rejected with a reason")

# film plan in small steps: cast first, then each part of the story; code fixes the mechanical rules -> no polish
FILM_OK["on"] = True
log_calls.clear(); lines.clear()
f5 = writer.write("A fourth topic", chan, log=lines.append)
fj = json.loads((f5 / "film.json").read_text(encoding="utf-8"))
ok(not (f5 / "NEEDS_POLISH.md").exists() and len(fj["shots"]) >= 3 and fj["shots"][0]["at"] == 0 and fj.get("era"),
   f"film: cast + per-part shots + automatic fixes give a plan that passes ({len(fj['shots'])} shots, "
   f"{sum(1 for l in lines if 'film part' in l)} part calls) {[l for l in lines if l.strip().startswith('- ')][:3]}")
FILM_OK["on"] = False

# guardrail: no first draft passes the rules (e.g. one model out of quota, others break a rule) -> the closest draft
# is repaired instead of the run failing
log_calls.clear()
saved_best_of = sk.best_of
def failing_best_of(prompt, **kw):
    log_calls.append("best_of failed"); raise RuntimeError("best_of: no model produced a valid answer")
sk.best_of = failing_best_of
writer._compat = lambda fn: fn
bad = copy.deepcopy(SCRIPT); bad["beats"] = bad["beats"][:1]   # far too short: breaks the word-count rule
calls_seen = []
def ask_for_repair(prompt, **kw):
    calls_seen.append(kw.get("models"))
    if "It breaks these rules" in prompt:
        return R(copy.deepcopy(SCRIPT), "fake:fixer")
    if "Write a 1-minute YouTube Short" in prompt and "YOUR SCRIPT" not in prompt and "YOUR DRAFT" not in prompt:
        return R(copy.deepcopy(bad), "fake:drafter")
    return fake_ask(prompt, **kw)
ail.ask = ask_for_repair
facts["n"] = 1
lines.clear()
f4 = writer.write("A third topic", chan, log=lines.append)
ok("best_of failed" in log_calls and any("repair 1 by" in l for l in lines) and (f4 / "script.json").exists(),
   "guardrail: when no draft passes, the closest one is repaired (the run goes on)")
sk.best_of, ail.ask = saved_best_of, fake_ask

# schedule: topics are taken in order, once; a finished episode's topic is never made again; failures retry once
from studio.story import topics as T  # noqa: E402
mem = {"episodes": [{"episode": "005-x", "topic": T.queue("hidden_reasons")[0]}]}
first = T.pending("hidden_reasons", mem)[0]
ok(first == T.queue("hidden_reasons")[1], "schedule: a topic already made is skipped")
mem["topics"] = {T.key(first): {"topic": first, "tries": 2}}
ok(T.pending("hidden_reasons", mem)[0] == T.queue("hidden_reasons")[2], "schedule: a topic that failed twice is skipped")
shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
