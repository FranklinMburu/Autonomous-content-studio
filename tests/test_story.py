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
ch = board.picture_changes(shots, lib.DUR)
gaps = [b - a for a, b in zip(ch, ch[1:] + [lib.DUR])]
ok(max(gaps) <= 1.5 and lib.DUR / len(ch) <= 1.3, f"auto camera: new picture every {lib.DUR / len(ch):.2f}s, longest hold {max(gaps):.1f}s")
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
print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
