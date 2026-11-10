"""Command line for the story style. See studio/story/__init__.py."""
import argparse, datetime, importlib.util, json, shutil, sys, time
from pathlib import Path

from ..paths import OUT, ensure_fonts, slugify
from . import lib

REQUIRED = ("script.json", "sources.md")  # plus storyboard.json (preferred) or scenes.py


def log(*a):
    print(*a, flush=True)


def load_episode(folder):
    folder = Path(folder)
    missing = [f for f in REQUIRED if not (folder / f).exists()]
    if not (folder / "storyboard.json").exists() and not (folder / "scenes.py").exists():
        missing.append("storyboard.json")
    if missing:
        raise SystemExit(f"{folder}: missing {', '.join(missing)}")
    return folder, json.loads((folder / "script.json").read_text(encoding="utf-8"))


def import_scenes(folder):
    """Shots for an episode: from storyboard.json (data, preferred) or the older scenes.py (code)."""
    if (folder / "storyboard.json").exists():
        from . import board
        return board.build_shots(json.loads((folder / "storyboard.json").read_text(encoding="utf-8")))
    spec = importlib.util.spec_from_file_location(f"episode_{folder.name.replace('-', '_')}", folder / "scenes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SHOTS, getattr(mod, "KEY", set())


# The story-style voice, one place for every episode (new, polished or re-made). Chosen by Franklin on 10 Nov
# (sample "E"): Kokoro's best voice at 1.15x with real but short pauses. The old film voice (am_michael at 1.38x,
# 0.08/0.2 s gaps) rated 5/10: rushed, no breathing room. A script's own voice/speed/pace is ignored on purpose.
STORY_VOICE = {"voice": "af_heart", "speed": 1.15,
               "pace": {"gap_line": 0.22, "gap_beat": 0.42, "lead_in": 0.08, "tail": 0.7, "trim_tail": 0.06}}


def narrate(script, out_dir):
    """Kokoro narration in the story voice (STORY_VOICE); restores the explainer defaults afterwards."""
    from .. import voice
    keep = (voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL)
    script["voice"], script["speed"] = STORY_VOICE["voice"], STORY_VOICE["speed"]
    pace = script["pace"] = dict(STORY_VOICE["pace"])
    try:
        voice.GAP_LINE, voice.GAP_BEAT = pace["gap_line"], pace["gap_beat"]
        voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL = pace["lead_in"], pace["tail"], pace["trim_tail"]
        return voice.narrate(script, out_dir / "narration.wav", out_dir / "timing.json")
    finally:
        voice.GAP_LINE, voice.GAP_BEAT, voice.LEAD_IN, voice.TAIL, voice.TRIM_TAIL = keep


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
    if (folder / "storyboard.json").exists():
        from . import board
        probs += board.validate(json.loads((folder / "storyboard.json").read_text(encoding="utf-8")))
    if probs:
        log("Shot problems:\n  " + "\n  ".join(probs)); return 1
    if (folder / "storyboard.json").exists():
        q = board.quality(json.loads((folder / "storyboard.json").read_text(encoding="utf-8")))
        log("Quality warnings (below benchmark level):\n  " + "\n  ".join(q) if q else "[quality] meets the benchmark rules")
    audio = out / "narration.wav"
    if (folder / "storyboard.json").exists() and script.get("sound", True):
        from . import sound
        audio, cl, track = sound.mix(json.loads((folder / "storyboard.json").read_text(encoding="utf-8")), timing,
                                     out / "narration.wav", out / "mix.wav", track=script.get("music"),
                                     title=script.get("title", folder.name), log=log)
        lib.set_timing(timing)
    log(f"[render] {len(shots)} shots")
    lib.render_video(shots, key, audio, out / "video.mp4", preset=a.preset, log=log)
    from ..qc import contact_sheet
    contact_sheet(out / "video.mp4", out / "contact.png", every=2.0)
    for f in REQUIRED + ("storyboard.json", "scenes.py"):
        if (folder / f).exists():
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


def cmd_review(a):
    """Polish step (POLISH.md, story section): everything the polisher needs on one page, plus a still of every shot."""
    from . import board
    folder, script = load_episode(a.episode)
    ensure_fonts()
    out = OUT / f"review-{folder.name}"; out.mkdir(parents=True, exist_ok=True)
    timing = narrate(script, out)
    lib.set_timing(timing)
    sb = json.loads((folder / "storyboard.json").read_text(encoding="utf-8"))
    shots, key = board.build_shots(sb)
    n, dur = len(timing["words"]), timing["duration"]
    ch = board.picture_changes(shots, dur)
    gaps = [y - x for x, y in zip(ch, ch[1:] + [dur])]
    text = " ".join(l for b in script["beats"] for l in b["lines"])
    sentences = [x for x in __import__("re").split(r"(?<=[.!?])\s+", text) if x.strip()]
    lines = [f"# Review: {script.get('title')}", "",
             f"- Length {dur:.1f}s, {n} words, {n / dur * 60:.0f} words/min (target 200-230), "
             f"{sum(1 for w in timing['words'] if w['start'] < 3)} words in first 3 s",
             f"- Hook: {script['beats'][0]['lines'][0]!r}",
             f"- Sentences: {len(sentences)}, average {sum(len(x.split()) for x in sentences) / max(1, len(sentences)):.1f} words",
             f"- Shots: {len(shots)}; picture changes {len(ch)} (one every {dur / max(1, len(ch)):.2f}s), longest hold {max(gaps):.1f}s",
             "", "## Gate results", ""]
    probs = board.validate(sb) + board.quality(sb)
    lines += [f"- {x}" for x in probs] or ["- all checks pass"]
    lines += ["", "## Script (one line per sentence)", ""] + [f"{i + 1}. {x}" for i, x in enumerate(sentences)]
    lines += ["", "## Shots (start s, name, place, items)", ""]
    starts = [s_[0] for s_ in shots]
    for t0, sh in zip(starts, sb["shots"]):
        bg = sh.get("bg", "gradient"); bg = bg.get("type") if isinstance(bg, dict) else bg
        items = ", ".join(it.get("role") or it.get("name") or it.get("text") or it["type"] for it in sh.get("items", []))
        lines.append(f"- {t0:5.1f}s {sh.get('name', '')} [{bg}] {items}")
    paths = lib.stills(shots, key, [round(t + 0.8, 2) for t in starts], out)
    lines += ["", f"Stills: {out}"]
    (out / "review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


def cmd_write(a):
    """AI writes a new episode (research, script, fact check, narration, storyboard), then optionally renders it."""
    from .writer import write
    from ..paths import ROOT
    ensure_fonts()
    folder = write(a.topic, ROOT / "episodes" / a.channel, log=log)
    print(f"EPISODE={folder.relative_to(ROOT).as_posix()}", flush=True)
    if a.make:
        a.episode, a.preset = str(folder), "veryfast"
        return cmd_make(a)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio.story", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("episode"); m.add_argument("--preset", default="veryfast")
    s = sub.add_parser("stills"); s.add_argument("episode"); s.add_argument("times", nargs="*")
    c = sub.add_parser("check"); c.add_argument("episode")
    r = sub.add_parser("review"); r.add_argument("episode")
    w = sub.add_parser("write"); w.add_argument("--topic", required=True)
    w.add_argument("--channel", default="hidden_reasons"); w.add_argument("--make", action="store_true")
    a = p.parse_args(argv)
    return {"make": cmd_make, "stills": cmd_stills, "check": cmd_check, "review": cmd_review, "write": cmd_write}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
