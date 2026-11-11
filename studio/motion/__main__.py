"""Command line for the motion engine (Tech Education style). See studio/motion/__init__.py and docs/MOTION_ENGINE.md."""
import argparse, datetime, json, re, shutil, subprocess, sys, time
from pathlib import Path

from ..paths import OUT, ROOT, slugify
from . import plan as PL
from .style import channel, seed_of, style_for

HERE = Path(__file__).resolve().parent


def log(*a):
    print(*a, flush=True)


def load(folder):
    folder = Path(folder)
    missing = [f for f in ("script.json", "plan.json", "sources.md") if not (folder / f).exists()]
    if missing:
        raise SystemExit(f"{folder}: missing {', '.join(missing)}")
    rd = lambda f: json.loads((folder / f).read_text(encoding="utf-8"))  # noqa: E731
    return folder, rd("script.json"), rd("plan.json")


def node_ready():
    if not (HERE / "node_modules" / "playwright").exists():
        raise SystemExit("The renderer is not installed: run `npm ci` in studio/motion (and `npx playwright install chromium` once).")


def node(*args, timeout=3600):
    node_ready()
    r = subprocess.run(["node", str(HERE / "render.js"), *map(str, args)], timeout=timeout)
    if r.returncode:
        raise SystemExit(f"renderer failed ({r.returncode})")


def prepare(folder, script, plan, out, ch, log=log):
    """Voice + timing + the data file the engine reads. Returns (data_path, plan_used, problems)."""
    probs = PL.validate(script, plan)
    if probs:   # guardrail: never stop the line here; draw the plain fallback plan and flag the video for review
        log("[plan] problems, using the fallback plan (video flagged for review):\n  " + "\n  ".join(probs[:12]))
        plan = PL.auto_plan(script, script.get("title"), ch.get("series", ""))
    seed = int(plan.get("seed") or seed_of(folder.name))
    st = style_for(seed, ch)
    log(f"[style] seed {seed}: accent {st['accent']}, {st['music']['key']} at {st['music']['bpm']} BPM")
    from .narrate import narrate
    timing = narrate(script, out, ch["voice"])
    n = len(timing["words"])
    log(f"[voice] {ch['voice']['voice']}: {timing['duration']:.1f} s, {n} words, {n / timing['duration'] * 60:.0f} words/min")
    data = out / "data.json"
    data.write_text(json.dumps({"timing": timing, "script": script, "plan": plan, "style": st}, ensure_ascii=False), encoding="utf-8")
    return data, plan, st, probs


def measure(video):
    """Numbers for the quality bar: loudness and how much of the video stands still (reference: -14.1 LUFS, 8% still)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(video), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", "fps=10,scale=90:160,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(float)
    d = np.abs(np.diff(a, axis=0)).mean((1, 2))
    return {"lufs": float(m[-1]) if m else None, "still_pct": round(float((d < 0.3).mean() * 100), 1),
            "motion_mean": round(float(d.mean()), 2), "brightness": round(float(a.mean()), 1)}


def cmd_make(a):
    folder, script, plan = load(a.episode)
    ch = channel(a.channel)
    out = Path(a.out) if a.out else OUT / f"{datetime.datetime.now():%Y%m%d-%H%M}-motion-{slugify(script.get('title', folder.name))}"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    data, used, st, probs = prepare(folder, script, plan, out, ch)
    node(data, "--cues", out / "info.json")
    info = json.loads((out / "info.json").read_text())
    from . import sound
    sound.make(info, st["music"], st["seed"], out / "music.wav", out / "sfx.wav")
    log("[render] frames (about 0.25 s each)")
    node(data, out / "silent.mp4", a.fps)
    sound.mix(out / "silent.mp4", out / "voice.wav", out / "music.wav", out / "sfx.wav", out / "video.mp4", ch.get("loudness_lufs", -14))
    try:
        from ..qc import contact_sheet
        contact_sheet(out / "video.mp4", out / "contact.png", every=2.0)
    except Exception as e:  # noqa: BLE001 - the sheet is a convenience, not a gate
        log(f"  contact sheet skipped: {e}")
    m = measure(out / "video.mp4")
    gates = {"plan_valid": not probs, "loudness_ok": m["lufs"] is not None and abs(m["lufs"] - ch.get("loudness_lufs", -14)) <= 1.0,
             "moves_enough": m["still_pct"] <= 10}
    report = {"episode": folder.as_posix(), "title": script.get("title"), "seed": st["seed"], "style": st, "measures": m,
              "gates": gates, "plan_problems": probs, "plan_warnings": PL.variety(used), "fallback_plan": bool(used.get("auto"))}
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for f in ("script.json", "plan.json", "sources.md"):
        shutil.copy(folder / f, out / f)
    for f in ("silent.mp4", "voice.wav", "music.wav", "sfx.wav", "data.json"):
        (out / f).unlink(missing_ok=True)
    log(f"[check] {m} gates {gates}")
    log(f"[done] {time.time() - t0:.0f} s -> {out / 'video.mp4'}")
    print(f"MOTION_OUT={out}", flush=True)
    return 0 if all(gates.values()) else 2      # 2 = made, but held for review


def cmd_stills(a):
    folder, script, plan = load(a.episode)
    ch = channel(a.channel)
    out = OUT / f"stills-{folder.name}"; out.mkdir(parents=True, exist_ok=True)
    data, used, _st, _p = prepare(folder, script, plan, out, ch)
    timing = json.loads((out / "timing.json").read_text())
    starts = [timing["lines"][s["line"]]["start"] for s in used["scenes"]]
    times = [float(x) for x in a.times] if a.times else [round(x + 0.9, 2) for x in starts]
    node(data, "--stills", ",".join(map(str, times)), out)
    log(f"stills -> {out}")
    return 0


def cmd_check(a):
    """Offline: plan contract, taste warnings, script length, sources."""
    folder, script, plan = load(a.episode)
    probs = PL.validate(script, plan)
    words = sum(len(l.split()) for l in PL.lines_of(script))
    if not 110 <= words <= 200:
        probs.append(f"{words} words; Tech Education shorts are 120-190 words (about 45-75 s)")
    if "http" not in (folder / "sources.md").read_text(encoding="utf-8"):
        probs.append("sources.md lists no links")
    log("OK" if not probs else "PROBLEMS:\n  " + "\n  ".join(probs))
    for w in PL.variety(plan):
        log(f"  warning: {w}")
    log(f"  {words} words, {len(PL.lines_of(script))} lines, {len(plan.get('scenes', []))} scenes")
    return 1 if probs else 0


def cmd_write(a):
    from .writer import write
    ch = channel(a.channel)
    folder = write(a.topic, ROOT / ch["episodes"], ch, log=log)
    print(f"EPISODE={folder.relative_to(ROOT).as_posix()}", flush=True)
    if a.make:
        a.episode = str(folder)
        return cmd_make(a)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio.motion", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("episode"); m.add_argument("--fps", type=int, default=30); m.add_argument("--out")
    s = sub.add_parser("stills"); s.add_argument("episode"); s.add_argument("times", nargs="*")
    c = sub.add_parser("check"); c.add_argument("episode")
    w = sub.add_parser("write"); w.add_argument("--topic", required=True); w.add_argument("--make", action="store_true")
    w.add_argument("--fps", type=int, default=30); w.add_argument("--out")
    for x in (m, s, c, w):
        x.add_argument("--channel", default="te")
    a = p.parse_args(argv)
    return {"make": cmd_make, "stills": cmd_stills, "check": cmd_check, "write": cmd_write}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
