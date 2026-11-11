"""Motion engine (Tech Education) checks. Offline: no keys, no network, no models.
The render smoke test runs only where the renderer is installed (npm ci in studio/motion + Chromium).
Run: python tests/test_motion.py
"""
import hashlib, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.motion import plan as PL  # noqa: E402
from studio.motion.style import channel, style_for, seed_of  # noqa: E402

EP = ROOT / "episodes" / "tech_education" / "001-what-is-an-api"
FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def ep():
    return json.loads((EP / "script.json").read_text(encoding="utf-8")), json.loads((EP / "plan.json").read_text(encoding="utf-8"))


def test_engine_knows_every_type():
    html = (ROOT / "studio" / "motion" / "web" / "engine.html").read_text(encoding="utf-8")
    for t in PL.TYPES:
        check(re.search(rf'\b{t}\b', html) is not None, f"engine.html handles scene type {t}")


def test_approved_episode_passes():
    s, p = ep()
    check(PL.validate(s, p) == [], f"episode 001 plan passes the contract {PL.validate(s, p)[:3]}")
    check(PL.variety(p) == [], f"episode 001 has no taste warnings {PL.variety(p)}")
    check(len(PL.lines_of(s)) == len(p["scenes"]), "one scene per line")


def test_validate_catches_mistakes():
    s, p = ep()
    bad = json.loads(json.dumps(p)); bad["scenes"].pop(3)
    check(any("one scene per line" in x for x in PL.validate(s, bad)), "a missing scene is caught")
    bad = json.loads(json.dumps(p)); bad["scenes"][2]["type"] = "explosion"
    check(any("unknown type" in x for x in PL.validate(s, bad)), "an unknown scene type is caught")
    bad = json.loads(json.dumps(p)); bad["scenes"][6]["p"]["word"] = "banana"
    check(any("not a word of line" in x for x in PL.validate(s, bad)), "a word anchor that isn't spoken is caught")
    bad = json.loads(json.dumps(p)); bad["scenes"][5] = {"line": 5, "type": "big_word", "p": {"text": "x"}}
    check(any("needs a diagram_link" in x for x in PL.validate(s, bad)), "scenes that need the diagram first are caught")
    bad = json.loads(json.dumps(p)); bad["scenes"][-1] = {"line": len(p["scenes"]) - 1, "type": "big_word", "p": {"text": "x"}}
    check(any("last scene must be end_card" in x for x in PL.validate(s, bad)), "the end card is required")
    bad = json.loads(json.dumps(p)); bad["scenes"][2]["p"]["value"] = "57"
    check(any("must be a number" in x for x in PL.validate(s, bad)), "a stat value must be a number")


def test_fallback_plan_always_renders():
    s, _ = ep()
    check(PL.validate(s, PL.auto_plan(s)) == [], "auto_plan of episode 001 passes the contract")
    odd = {"title": "x", "beats": [{"lines": ["Hi."]}, {"lines": ["A 3.5 GHz chip, really fast, with 12 cores.", "Then?", "Bye now."]}]}
    check(PL.validate(odd, PL.auto_plan(odd)) == [], "auto_plan of an odd short script passes the contract")


def test_style_is_seeded():
    ch = channel()
    a, b = style_for(27, ch), style_for(27, ch)
    check(a == b, "same seed -> same style")
    styles = {json.dumps(style_for(s, ch), sort_keys=True) for s in range(40)}
    check(len(styles) >= 35, f"different seeds -> different styles ({len(styles)}/40 distinct)")
    check(a["accent"] in ch["look"]["accents"] and a["music"]["key"] in ch["music"]["keys"], "style stays inside the channel look")
    check(seed_of("002-x") == seed_of("002-x") != seed_of("003-y"), "folder-name seeds are stable and differ")


def test_voice_is_locked():
    v = channel()["voice"]
    check((v["voice"], v["speed"], v["pace"]["gap_line"], v["pace"]["gap_beat"]) == ("am_fenrir", 1.0, 0.12, 0.3),
          "TE voice = Franklin's locked choice (am_fenrir 1.0, gaps 0.12/0.3)")
    check(v["pace"] == {"gap_line": 0.12, "gap_beat": 0.3, "lead_in": 0.15, "tail": 0.4, "trim_tail": None},
          "every pacing value of the locked voice is set in the channel file (as approved on 11 Nov)")
    src = (ROOT / "studio" / "motion" / "narrate.py").read_text(encoding="utf-8")
    check(all(f'pace["{k}"]' in src for k in v["pace"]) and all(f"voice.{k}" in src for k in ("GAP_LINE", "GAP_BEAT", "LEAD_IN", "TAIL", "TRIM_TAIL")),
          "narrate.py sets all five pacing values itself (shared voice defaults can't change the locked voice)")
    check("rubberband" not in v["eq"] and "aecho" not in v["eq"] and "asetrate" not in v["eq"],
          "no pitch shift or echo in the voice chain (rejected on 11 Nov)")


def test_never_imports_the_story_engine():
    for p in (ROOT / "studio" / "motion").glob("*.py"):
        txt = p.read_text(encoding="utf-8")
        check("from ..story" not in txt and "studio.story" not in txt, f"{p.name} does not import the story engine")


def test_isolated_from_hidden_reasons():
    files = list((ROOT / "studio").rglob("*.py")) + list((ROOT / ".github" / "workflows").glob("*.yml")) + list((ROOT / "tools").glob("*"))
    for sub in ("src", "scripts"):
        files += [p for p in (ROOT / "web" / sub).rglob("*") if p.suffix in (".js", ".mjs", ".ts", ".tsx")]
    files += list((ROOT / "pipeline").rglob("*.py")) if (ROOT / "pipeline").exists() else []
    words = ("studio.motion", "studio/motion", "tech_education", "channels/te")
    hits = [str(p.relative_to(ROOT)) for p in files if p.is_file() and any(w in p.read_text(encoding="utf-8", errors="ignore") for w in words)]
    own = (".github/workflows/make-motion.yml", ".github/workflows/motion-review.yml", ".github/workflows/pipeline-tests.yml")
    hits = [h for h in hits if not h.startswith("studio/motion/") and h not in own]
    check(hits == [], f"nothing outside the motion engine uses it: studio, workflows, tools, website {hits}")


def test_workflows_do_not_share_with_films():
    wf = ROOT / ".github" / "workflows"
    mm, mr = (wf / "make-motion.yml").read_text(encoding="utf-8"), (wf / "motion-review.yml").read_text(encoding="utf-8")
    check("assets-kokoro-v1.1-tabler" not in mm, "make-motion never touches the Hidden Reasons cache key")
    check("--label review-motion" in mm and not re.search(r"--label review(\s|$)", mm, re.M), "motion review issues use their own label")
    check("group: make-motion" in mm and "KAGGLE_" not in mm and "pip install kaggle" not in mm and "release download channel-memory" not in mm,
          "own queue, no Kaggle keys or tool, no channel memory download")
    check("'review-motion'" in mr and "repository_owner" in mr, "motion-review answers only the owner on review-motion issues")
    check("<!-- motion-review: tag=" in mm and "motion-review: tag=" in mr, "the review issue carries the marker the review workflow reads")
    rr = (wf / "review-reply.yml").read_text(encoding="utf-8")
    check("contains(github.event.issue.labels.*.name, 'review')" in rr, "the film review workflow matches the exact label 'review' (not review-motion)")
    check("episodes/tech_education/" in mm and "commit_to_main.sh" in mm, "AI-written episodes are saved to the repo")


class _R:
    def __init__(self, data): self.data, self.attempts = data, []


def test_writer_offline():
    from studio.motion import writer
    s, p = ep()
    good = {**s, "plan": p}
    srcs = [{"url": "https://example.org/a", "text": "57 percent of dynamic internet traffic. 23.8 million secrets. 2024. 200 401 429", "title": "a"}]
    fact = lambda text, sources, **k: {"results": [], "counts": {"supported": 1}}  # noqa: E731
    with tempfile.TemporaryDirectory() as tmp:
        f = writer.write("What is an API?", Path(tmp), channel(), log=lambda *a: None,
                         ask_fn=lambda *a, **k: _R(good), research_fn=lambda t: srcs, fact_fn=fact)
        check(f.name.startswith("001-") and (f / "plan.json").exists() and not (f / "NEEDS_REVIEW.md").exists(),
              "writer: a good draft becomes an episode folder with no review flag")
        check(PL.validate(json.loads((f / "script.json").read_text()), json.loads((f / "plan.json").read_text())) == [], "writer: saved plan passes")
        broken = {**s, "plan": {"scenes": [{"line": 0, "type": "nope"}]}}
        f2 = writer.write("What is an API?", Path(tmp), channel(), log=lambda *a: None,
                          ask_fn=lambda *a, **k: _R(broken), research_fn=lambda t: srcs, fact_fn=fact)
        check(f2.name.startswith("002-") and (f2 / "NEEDS_REVIEW.md").exists(), "writer: a broken plan is flagged for review")
        check(json.loads((f2 / "plan.json").read_text()).get("auto") is True, "writer: a broken plan falls back to the plain plan")


def test_render_smoke():
    motion = ROOT / "studio" / "motion"
    if not (motion / "node_modules" / "playwright").exists() or not shutil.which("node"):
        print("skip render smoke (renderer not installed: npm ci in studio/motion)")
        return
    s, p = ep()
    words, lines, t = [], [], 0.2
    for i, l in enumerate(PL.lines_of(s)):
        st = t
        for w in l.split():
            words.append({"w": w, "start": round(t, 3), "end": round(t + 0.3, 3), "line": i}); t += 0.34
        lines.append({"text": l, "start": st, "end": t}); t += 0.15
    data = {"timing": {"duration": t + 0.5, "lines": lines, "words": words}, "script": s, "plan": p, "style": style_for(p["seed"])}
    with tempfile.TemporaryDirectory() as tmp:
        dp = Path(tmp) / "data.json"; dp.write_text(json.dumps(data))
        times = "1.0,9.0,20.5,33.0,48.0"
        r1 = subprocess.run(["node", str(motion / "render.js"), str(dp), "--stills", times, str(Path(tmp) / "a")], capture_output=True, text=True, timeout=300)
        r2 = subprocess.run(["node", str(motion / "render.js"), str(dp), "--stills", times, str(Path(tmp) / "b")], capture_output=True, text=True, timeout=300)
        check(r1.returncode == 0 and r2.returncode == 0, f"renderer draws without page errors {r1.stderr[-300:]}")
        fa, fb = sorted((Path(tmp) / "a").glob("*.jpg")), sorted((Path(tmp) / "b").glob("*.jpg"))
        same = sum(hashlib.md5(x.read_bytes()).digest() == hashlib.md5(y.read_bytes()).digest() for x, y in zip(fa, fb))
        try:   # Chromium's blur filters can differ by a few pixels between runs; the picture itself must not
            import numpy as np
            from PIL import Image
            worst = max(float((np.abs(np.asarray(Image.open(x), int) - np.asarray(Image.open(y), int)).max(2) > 8).mean()) for x, y in zip(fa, fb))
        except ImportError:
            worst = 0.0 if same == len(fa) else 1.0
        check(len(fa) == 5 and worst < 0.005, f"same inputs -> the same frames ({same}/5 byte-identical, worst {worst * 100:.2f}% pixels differ)")
        r3 = subprocess.run(["node", str(motion / "render.js"), str(dp), "--cues", str(Path(tmp) / "c.json")], capture_output=True, text=True, timeout=300)
        info = json.loads((Path(tmp) / "c.json").read_text()) if r3.returncode == 0 else {}
        check(len(info.get("cues", [])) > 50 and info.get("sections", {}).get("break_from") is not None, "sound cues and music sections come out of the plan")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall motion checks pass")
    sys.exit(1 if FAILS else 0)
