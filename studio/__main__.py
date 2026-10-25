"""Autonomous Content Studio - command line.

  python -m studio make   --topic "Why do cats purr?" [--lane "animal behaviour for curious adults"]
  python -m studio render --script scripts/cat_purr.json     (no AI needed: render a hand-written script)
  python -m studio write  --topic "..."                      (script only, to review/edit before rendering)
  python -m studio setup                                     (download free assets, check everything)

Each run writes a folder in out/ with: video.mp4, contact.png, report.md, script.json, timing.json.
"""
import argparse, datetime, json, shutil, sys, time
from pathlib import Path

from .paths import OUT, ensure_fonts, slugify, models_dir, icons_dir


def log(*a):
    print(*a, flush=True)


def _folder(title):
    d = OUT / f"{datetime.datetime.now():%Y%m%d-%H%M}-{slugify(title)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def produce(script, folder, fact=None, warnings=(), preset="veryfast"):
    from . import voice, render, qc
    t0 = time.time()
    (folder / "script.json").write_text(json.dumps(script, indent=1, ensure_ascii=False), encoding="utf-8")
    log("[voice] narrating...")
    timing = voice.narrate(script, folder / "narration.wav", folder / "timing.json")
    log(f"  {timing['duration']:.1f} s of narration; word timing from model: {timing['exact_word_timing']}")
    log("[render] drawing frames and encoding...")
    R = render.Renderer(script, timing)
    log(f"  style: {R.S.name} palette, {R.S.bg} background")
    R.video(folder / "narration.wav", folder / "video.mp4", preset=preset)
    log("[qc] checking...")
    tech = qc.technical(folder / "video.mp4")
    qc.contact_sheet(folder / "video.mp4", folder / "contact.png")
    status = qc.report(folder, script, tech, fact, warnings)
    (folder / "qc.json").write_text(json.dumps({"technical": tech, "fact_check": fact}, indent=1,
                                               ensure_ascii=False), encoding="utf-8")
    (folder / "narration.wav").unlink(missing_ok=True)   # the mp4 has the audio; save space
    log(f"[done] {status} in {time.time() - t0:.0f} s -> {folder}")
    for k, ok in tech["checks"].items():
        if not ok:
            log(f"  ❌ {k}")
    return status


def cmd_setup(a):
    log("Checking setup...")
    ok = True
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        log("  ❌ ffmpeg/ffprobe not found on PATH"); ok = False
    else:
        log("  ✅ ffmpeg")
    try:
        import cairo, cairosvg, kokoro_onnx  # noqa
        log("  ✅ python packages")
    except ImportError as e:
        log(f"  ❌ missing python package: {e}. Run: pip install -r requirements.txt"); ok = False
    ensure_fonts(); log("  ✅ fonts")
    models_dir(); log("  ✅ voice model")
    icons_dir(); log("  ✅ icon set")
    import os
    log("  ✅ GEMINI_API_KEY set" if os.environ.get("GEMINI_API_KEY") else
        "  ⚠️  GEMINI_API_KEY not set (only needed for 'make' and 'write')")
    return 0 if ok else 1


def cmd_write(a):
    from . import writer
    ensure_fonts()
    script, warns, model = writer.write(a.topic, a.lane, log=log)
    out = Path(a.out or (OUT / f"{slugify(script['title'])}.json"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(script, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"script saved to {out}")
    for w in warns:
        log(f"  ⚠️ {w}")
    return 0


def cmd_render(a):
    from . import schema
    ensure_fonts()
    script = json.loads(Path(a.script).read_text(encoding="utf-8"))
    errors, warns = schema.validate(script, fix=True)
    for w in warns:
        log(f"  ⚠️ {w}")
    if errors:
        log("Script problems:\n  " + "\n  ".join(errors))
        if not a.force:
            log("Fix them or pass --force."); return 1
    fact = None
    if a.factcheck:
        from . import factcheck
        log("[fact check] reading sources...")
        fact = factcheck.check(script, log=log)
    produce(script, _folder(script["title"]), fact, warns, preset=a.preset)
    return 0


def cmd_make(a):
    from . import writer, factcheck
    ensure_fonts()
    log(f"[script] writing: {a.topic}")
    script, warns, model = writer.write(a.topic, a.lane, log=log)
    folder = _folder(script["title"])
    fact = None
    if not a.no_factcheck:
        log("[fact check] reading sources...")
        fact = factcheck.check(script, log=log)
    script["_meta"] = {"writer_model": model, "topic": a.topic, "lane": a.lane}
    produce(script, folder, fact, warns, preset=a.preset)
    return 0


def cmd_next(a):
    """Take the first topic in topics.txt that isn't in topics-done.txt, make it, mark it done."""
    from .paths import ROOT
    todo = ROOT / "topics.txt"; done_f = ROOT / "topics-done.txt"
    topics = [l.strip() for l in todo.read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.lstrip().startswith("#")] if todo.exists() else []
    done = set(done_f.read_text(encoding="utf-8").splitlines()) if done_f.exists() else set()
    left = [t for t in topics if t not in done]
    if not left:
        log("No topics left in topics.txt. Add some ideas and run again."); return 1
    a.topic = left[0]
    log(f"Next topic ({len(left)} left): {a.topic}")
    rc = cmd_make(a)
    if rc == 0:
        with open(done_f, "a", encoding="utf-8") as f:
            f.write(a.topic + "\n")
    return rc


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup"); s.set_defaults(fn=cmd_setup)
    s = sub.add_parser("write"); s.add_argument("--topic", required=True); s.add_argument("--lane")
    s.add_argument("--out"); s.set_defaults(fn=cmd_write)
    s = sub.add_parser("render"); s.add_argument("--script", required=True)
    s.add_argument("--factcheck", action="store_true", help="check sources with Gemini (needs key)")
    s.add_argument("--force", action="store_true"); s.add_argument("--preset", default="veryfast")
    s.set_defaults(fn=cmd_render)
    s = sub.add_parser("make"); s.add_argument("--topic", required=True); s.add_argument("--lane")
    s.add_argument("--no-factcheck", action="store_true"); s.add_argument("--preset", default="veryfast")
    s.set_defaults(fn=cmd_make)
    s = sub.add_parser("next"); s.add_argument("--lane")
    s.add_argument("--no-factcheck", action="store_true"); s.add_argument("--preset", default="veryfast")
    s.set_defaults(fn=cmd_next)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except Exception as e:
        log(f"\nFAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
