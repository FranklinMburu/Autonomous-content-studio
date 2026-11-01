"""Offline tests for the story style (studio/story). No voice model, no network: fake word timings.

    python tests/test_story.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import cairo  # noqa: E402
from studio.story import lib  # noqa: E402
from studio.story.__main__ import import_scenes, load_episode, main  # noqa: E402

fails = 0


def ok(cond, msg):
    global fails
    print(("PASS " if cond else "FAIL ") + msg)
    fails += 0 if cond else 1


def fake_timing(script, step=0.25):
    words, t = [], 0.05
    for bi, b in enumerate(script["beats"]):
        for line in b["lines"]:
            for w in line.split():
                words.append({"w": w, "start": round(t, 3), "end": round(t + step * 0.9, 3), "beat": bi}); t += step
    return {"duration": round(t + 0.7, 3), "words": words}


episodes = sorted(p for p in (ROOT / "episodes").glob("*/*") if (p / "script.json").exists())
ok(len(episodes) >= 1, f"found {len(episodes)} episode(s)")
for ep in episodes:
    ok(main(["check", str(ep)]) == 0, f"{ep.name}: offline check")
    folder, script = load_episode(ep)
    lib.set_timing(fake_timing(script))
    shots, key = import_scenes(folder)
    ok(not lib.check_shots(shots), f"{ep.name}: {len(shots)} shots start at 0 and are in time order")
    if (folder / "storyboard.json").exists():
        from studio.story import board
        probs = board.validate(json.loads((folder / "storyboard.json").read_text(encoding="utf-8")))
        ok(not probs, f"{ep.name}: storyboard passes its checks {probs[:3] if probs else ''}")
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, lib.W, lib.H)
    for s in shots:
        c = cairo.Context(surf)
        try:
            lib.frame(c, s[0] + 0.5, shots, key); good = True
        except Exception as e:  # any drawing error fails the test
            good = False; print("   ", e)
        ok(good, f"{ep.name}: draws shot {s[1].__name__}")

ok(lib.check_shots([(0.5, ok, 0)]) != [], "check_shots catches a first shot not at 0")

# The checks must catch the mistakes an AI writer makes.
from studio.story import board  # noqa: E402
lib.set_timing(fake_timing({"beats": [{"lines": ["A sailor's old scar splits open, years after it healed. You see, time."]}]}))
bad = {"shots": [{"at": 0, "bg": "sea", "items": [{"type": "prop", "name": "dragon"}]},
                 {"at": "unicorn#1", "items": [{"type": "text", "text": "X"}]}]}
probs = board.validate(bad)
ok(any("unicorn" in p for p in probs), "checks catch a trigger word that is never spoken")
bad2 = {"shots": [{"at": 0, "bg": "sea", "items": [{"type": "prop", "name": "dragon"}]}]}
ok(any("dragon" in p for p in board.validate(bad2)), "checks catch an unknown prop")
bad3 = {"shots": [{"at": 0, "items": [{"type": "character", "mood": "furious"}]}]}
ok(any("furious" in p for p in board.validate(bad3)), "checks catch an unknown mood")
from studio.story.writer import catalogue  # noqa: E402
ok("arm_scar" in catalogue() and "vitamin_c" in catalogue(), "the writer's library description is generated from the code")
ok("ward" in catalogue() and "scrub" in catalogue() and "midwife" in catalogue(), "catalogue lists places, poses and cast")

# Cast, places and camera (Phase 1 upgrades).
from studio.story import cast, settings  # noqa: E402
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, lib.W, lib.H)
drawn = True
try:
    for role in cast.ROLES:
        for pose in cast.POSES:
            c = cairo.Context(surf); c.translate(540, 1400); cast.draw(c, role, pose, "calm", 0.5, 1, 0)
    for mood in cast.MOODS:
        c = cairo.Context(surf); c.translate(540, 1400); cast.draw(c, "doctor", "stand", mood, 0.5, -1, 0.3)
    for name in settings.SETTINGS:
        for tone in settings.TONES:
            settings.draw(cairo.Context(surf), name, 1.0, tone)
except Exception as e:  # noqa: BLE001
    drawn = False; print("   ", e)
ok(drawn, f"draws {len(cast.ROLES)} roles x {len(cast.POSES)} poses, {len(cast.MOODS)} moods, "
          f"{len(settings.SETTINGS)} places x {len(settings.TONES)} tones")

ex = json.loads((ROOT / "studio" / "story" / "example_storyboard.json").read_text(encoding="utf-8"))
lib.set_timing(fake_timing({"beats": [{"lines": ex["narration"]}]}, step=0.36))
ok(not board.validate(ex["storyboard"]), "writer's example storyboard passes validate")
ok(not board.quality(ex["storyboard"]), f"writer's example storyboard passes the quality gate {board.quality(ex['storyboard'])[:2]}")
shots, _ = board.build_shots(ex["storyboard"])
ev = board.activity(ex["storyboard"])
end = lib.WORDS[-1]["end"]
gaps = [b - a for a, b in zip(ev, ev[1:] + [end])]
ok(max(gaps) <= 1.6, f"pace comes from things happening: something new every {lib.DUR / len(ev):.2f}s, longest gap {max(gaps):.1f}s")
zooms = []
for t0, fn, fy, cam, *_ in shots:
    if cam:
        zs = [round(cam(t0 + k * 0.05)[2], 3) for k in range(40)]
        zooms.append(all(a == b or abs(a / b - 1) > 0.15 for a, b in zip(zs, zs[1:])))
ok(all(zooms), "camera never zooms in or out within a framing (only clean cuts)")
words_only = {"shots": [{"at": 0, "bg": "street", "items": [{"type": "character", "role": "doctor"}]},
                        {"at": "+2", "items": [{"type": "text", "text": "WORDS"}]}]}
q = board.quality(words_only)
ok(any("only words" in p for p in q), "quality gate catches a words-only shot")
late = {"shots": [{"at": 0, "bg": "gradient", "items": [{"type": "prop", "name": "bed", "in": "+2.5"}]}]}
q = board.quality(late)
ok(any("no picture" in p for p in q) and any("opening shot" in p for p in q) and any("plain colour" in p for p in q),
   "quality gate catches an empty start, a weak opening and plain backgrounds")
arrow = {"shots": [{"at": 0, "bg": "ward", "items": [{"type": "character", "role": "doctor"},
                                                      {"type": "text", "text": "18% \u2192 3%"}]}]}
ok(any("can't draw" in p for p in board.quality(arrow)), "quality gate catches a label the font can't draw (an arrow)")
bars = {"shots": [{"at": 0, "bg": "ward", "items": [{"type": "character", "role": "doctor"}]},
                  {"at": "+2", "bg": "ward", "items": [{"type": "bar", "x": 300, "base_y": 1300, "h": 500, "grow_at": "+2.5"}]}]}
ok(any("no picture" in p for p in board.quality(bars)), "quality gate: a bar that hasn't grown yet is not a picture")
# Sound: effects placed from the storyboard, generated in code, mixed under the narration (no music folder in CI).
import tempfile, wave  # noqa: E402
from studio.story import sound  # noqa: E402
ex = json.loads((ROOT / "studio" / "story" / "example_storyboard.json").read_text(encoding="utf-8"))
tm = fake_timing({"beats": [{"lines": ex["narration"]}]}, step=0.36)
cl = sound.cues(ex["storyboard"], tm)
kinds = {k for _, k, _ in cl}
ok("whoosh" in kinds and "impact" in kinds and "riser" in kinds,
   f"sound: effects placed from the storyboard ({len(cl)}: {sorted(kinds)})")
ok(all(b - a >= 0.25 or kb != ka for (a, ka, _), (b, kb, _) in zip(cl, cl[1:])), "sound: effects never pile up")
d = Path(tempfile.mkdtemp())
n = int(tm["duration"] * 24000)
with wave.open(str(d / "n.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\x00\x00" * n)
out, _, track = sound.mix(ex["storyboard"], tm, d / "n.wav", d / "mix.wav", music_dir=str(d / "none"), log=lambda *a: None)
with wave.open(str(out)) as w:
    secs = w.getnframes() / w.getframerate()
ok(abs(secs - tm["duration"]) < 0.2 and track is None, f"sound: mix is the narration's length ({secs:.1f}s), effects only without music")

# film style (studio/story/film.py): the shot plan, missing assets, effects, and a short render from tiny fake assets
from studio.story import film as F
import cairo as _c
ep2 = Path(__file__).resolve().parents[1] / "episodes/hidden_reasons/002-why-doctors-were-ordered-to-wash-their-h"
fj = json.loads((ep2 / "film.json").read_text(encoding="utf-8"))
tm2 = fake_timing(json.loads((ep2 / "script.json").read_text(encoding="utf-8")))
pl = F.plan(fj, tm2)
ok(pl[0][0] == 0 and all(a[0] < b[0] for a, b in zip(pl, pl[1:])), f"film: 002 has {len(pl)} shots in spoken order")
ok(any("no picture" in x for x in F.problems(fj, tm2, d)), "film: missing pictures are reported")
fc = F.cues(fj, tm2)
ok({"whoosh", "impact", "riser"} <= {k for _, k, _ in fc}, f"film: effects from crossfades, hits and the ending ({len(fc)})")
mini = {"shots": [{"name": "a", "at": 0, "move": "push"}, {"name": "b", "at": 0.6, "clip": True, "xfade": True}]}
for nm, col in (("a", (0.8, 0.3, 0.2)), ("b", (0.2, 0.4, 0.8))):
    s_ = _c.ImageSurface(_c.FORMAT_RGB24, 90, 160); cc = _c.Context(s_); cc.set_source_rgb(*col); cc.paint()
    s_.write_to_png(str(d / f"shot_{nm}.png"))
    g_ = _c.ImageSurface(_c.FORMAT_RGB24, 90, 160); cg = _c.Context(g_); cg.set_source_rgb(0.5, 0.5, 0.5); cg.paint()
    g_.write_to_png(str(d / f"depth_{nm}.png"))
import subprocess as _sp
_sp.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=s=64x112:r=24:d=0.5", str(d / "clip_b.mp4")], check=True)
tm3 = {"duration": 1.2, "words": [{"w": "Hi", "start": 0.1, "end": 0.4}]}
F.render(mini, tm3, d, d / "n.wav", d / "film.mp4", preset="ultrafast", log=lambda *a: None)
ok((d / "film.mp4").stat().st_size > 1000 and not F.problems(mini, tm3, d), "film: renders stills (parallax) and clips with a crossfade")
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
