"""Command line for the story style. See studio/story/__init__.py."""
import argparse, datetime, importlib.util, json, shutil, sys, time
from pathlib import Path

from ..paths import OUT, ensure_fonts, slugify
from . import lib

REQUIRED = ("script.json", "scenes.py", "sources.md")


def log(*a):
    print(*a, flush=True)


def load_episode(folder):
    folder = Path(folder)
    missing = [f for f in REQUIRED if not (folder / f).exists()]
    if missing:
        raise SystemExit(f"{folder}: missing {', '.join(missing)}")
    return folder, json.loads((folder / "script.json").read_text(encoding="utf-8"))


def import_scenes(folder):
    spec = importlib.util.spec_from_file_location(f"episode_{folder.name.replace('-', '_')}", folder / "scenes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SHOTS, getattr(mod, "KEY", set())


def narrate(script, out_dir):
    """Kokoro narration with this episode's pace; restores the explainer defaults afterwards."""
    from .. import voice
    keep = (voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL)
    pace = script.get("pace", {})
    try:
        voice.GAP_LINE = pace.get("gap_line", 0.08); voice.GAP_BEAT = pace.get("gap_beat", 0.2)
        voice.LEAD_IN = pace.get("lead_in", 0.05); voice.TAIL = pace.get("tail", 0.7)
        return voice.narrate(script, out_dir / "narration.wav", out_dir / "timing.json")
    finally:
        voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL = keep


def cmd_make(a):
    folder, script = load_episode(a.episode)
    ensure_fonts()
    out = OUT / f"{datetime.datetime.now():%Y%m%d-%H%M}-story-{slugify(script.get('title', folder.name))}"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(f"[voice] {script.get('voice')} at speed {script.get('speed')}")
    timing = narrate(script, out)
    n = len(timing["words"])
    log(f"  {timing['duration']:.1f} s, {n} words, {n / timing['duration'] * 60:.0f} words/min, "
        f"{sum(1 for w in timing['words'] if w['start'] < 3)} words in the first 3 s")
    lib.set_timing(timing)
    shots, key = import_scenes(folder)
    probs = lib.check_shots(shots)
    if probs:
        log("Shot problems:\n  " + "\n  ".join(probs)); return 1
    log(f"[render] {len(shots)} shots")
    lib.render_video(shots, key, out / "narration.wav", out / "video.mp4", preset=a.preset, log=log)
    from ..qc import contact_sheet
    contact_sheet(out / "video.mp4", out / "contact.png", every=2.0)
    for f in REQUIRED:
        shutil.copy(folder / f, out / f)
    (out / "narration.wav").unlink(missing_ok=True)
    log(f"[done] {time.time() - t0:.0f} s -> {out / 'video.mp4'}")
    return 0


def cmd_stills(a):
    folder, script = load_episode(a.episode)
    ensure_fonts()
    out = OUT / f"stills-{folder.name}"; out.mkdir(parents=True, exist_ok=True)
    timing = narrate(script, out)
    lib.set_timing(timing)
    shots, key = import_scenes(folder)
    times = [float(x) for x in a.times] if a.times else [round(s[0] + 0.8, 2) for s in shots]
    for p in lib.stills(shots, key, times, out):
        log(p)
    return 0


def cmd_check(a):
    """Offline: files present, script shape, every beat line is text, sources listed."""
    folder, script = load_episode(a.episode)
    problems = []
    if not script.get("beats") or not all(isinstance(l, str) for b in script["beats"] for l in b.get("lines", [])):
        problems.append("script.json needs beats with text lines")
    words = sum(len(l.split()) for b in script.get("beats", []) for l in b["lines"])
    if not 120 <= words <= 260:
        problems.append(f"{words} words; story shorts are 145-235 words")
    if "http" not in (folder / "sources.md").read_text(encoding="utf-8"):
        problems.append("sources.md lists no links")
    log("OK" if not problems else "PROBLEMS:\n  " + "\n  ".join(problems))
    log(f"  {words} words, {len(script['beats'])} beats")
    return 1 if problems else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio.story", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("episode"); m.add_argument("--preset", default="veryfast")
    s = sub.add_parser("stills"); s.add_argument("episode"); s.add_argument("times", nargs="*")
    c = sub.add_parser("check"); c.add_argument("episode")
    a = p.parse_args(argv)
    return {"make": cmd_make, "stills": cmd_stills, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
