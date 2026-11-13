"""Preview a motion episode's frames WITHOUT the voice (for engine work): fake word times at a steady pace.

    python tools/motion_preview.py episodes/tech_education/<ep> out_dir [t1 t2 ...] [--long] [--every 1.5]

Never used to make a real video: the real timing comes from the channel's locked voice (studio.motion make).
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from studio.motion import plan as PL  # noqa: E402
from studio.motion.style import channel, seed_of, style_for  # noqa: E402


def fake_timing(script, wps=2.75):
    t, lines, words = 0.15, [], []
    for bi, b in enumerate(script["beats"]):
        for li, l in enumerate(b["lines"]):
            s = t
            for w in l.split():
                d = (len(w) + 3) / (wps * 7.5)
                words.append({"w": w, "start": round(t, 3), "end": round(t + d, 3), "line": len(lines), "beat": bi}); t += d
            lines.append({"beat": bi, "text": l, "start": round(s, 3), "end": round(t, 3)})
            t += 0.3 if li == len(b["lines"]) - 1 else 0.12
    return {"duration": round(t + 0.4, 3), "lines": lines, "words": words, "exact_word_timing": False}


def main():
    argv = sys.argv[1:]
    if "--every" in argv:
        k = argv.index("--every"); every = float(argv[k + 1]); del argv[k:k + 2]
    else:
        every = 1.5
    a = [x for x in argv if not x.startswith("--")]
    ep, out = Path(a[0]), Path(a[1]); out.mkdir(parents=True, exist_ok=True)
    script = json.loads((ep / "script.json").read_text()); plan = json.loads((ep / "plan.json").read_text())
    if "--long" in sys.argv:
        plan["format"] = "long"
    probs = PL.validate(script, plan)
    if probs:
        print("plan problems:", *probs, sep="\n  ")
    ch = channel("te")
    st = style_for(int(plan.get("seed") or seed_of(ep.name)), ch, plan.get("look"))
    tm = fake_timing(script)
    data = out / "data.json"
    data.write_text(json.dumps({"timing": tm, "script": script, "plan": plan, "style": st}))
    times = [x for x in a[2:]]
    if not times:
        n = int(tm["duration"] / every)
        times = [f"{i * every + 0.5:.2f}" for i in range(n)]
    r = subprocess.run(["node", str(ROOT / "studio/motion/render.js"), str(data), "--stills", ",".join(times), str(out)])
    print("duration", tm["duration"], "stills", len(times), "->", out)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
