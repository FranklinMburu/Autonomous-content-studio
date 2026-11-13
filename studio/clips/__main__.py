"""Clipping engine CLI. See docs/CLIPS_ENGINE.md.

  python -m studio.clips find    <stream folder> [--top 6] [--out DIR]   signals -> moments -> ranked clip.json files
  python -m studio.clips make    <stream folder> [--top 6] [--out DIR]   find + render + gates (report.json per clip)
  python -m studio.clips render  <clip.json> [--out video.mp4]           draw one clip.json
  python -m studio.clips check   <clip dir>                              re-run the gates on a made clip
  python -m studio.clips measure <video> [...]                           the numbers for any short (ours or a reference)
  python -m studio.clips judge   <clips dir> <references dir>            blind scorecard (needs the brain for the AI part)

Exit code: 0 = every clip passed every gate; 2 = clips made but at least one needs review; 1 = nothing made.
"""
import argparse, json, sys
from pathlib import Path

from ..paths import OUT
from . import gates, measure, sources

HERE = Path(__file__).resolve().parent


def log(*a):
    print(*a, flush=True)


def bar():
    return json.loads((HERE / "bar.json").read_text(encoding="utf-8"))


def brain_ask():
    try:
        from ailayer import ask   # the brain (private repo, present on GitHub Actions when the workflow fetches it)
        return ask
    except Exception:  # noqa: BLE001
        return None


def find(folder, top, out, log=log, ask=None):
    from . import moments, signals
    from .edit import make_clip
    from .layout import choose
    b = bar()
    src = sources.load(folder)
    if src["words"] is None:
        from .transcribe import transcribe
        src["words"] = transcribe(src["video"], Path(folder) / "words.json", log=log)
    dur = measure.probe(src["video"])["duration"]
    cv, info = signals.curves(src, dur, log=log)
    cands, _ = moments.candidates(cv, src["words"], b, src["rights"].get("title", ""), k=max(top * 2, 8))
    ranked = moments.rank(cands, b, ask=ask if ask is not None else brain_ask(), log=log)
    out.mkdir(parents=True, exist_ok=True)
    import shutil
    for old in out.glob("[0-9][0-9]-*"):   # a new find replaces the last one's clips
        shutil.rmtree(old)
    (out / "candidates.json").write_text(json.dumps({"signals": info, "candidates": ranked}, indent=1), encoding="utf-8")
    clips = []
    for i, c in enumerate(ranked[:top]):
        lay = choose(src["video"], c["start"], c["end"])
        clip = make_clip(c, src, src["words"], cv, b, lay, src["rights"].get("title", ""))
        d = out / f"{i + 1:02d}-{clip['id']}"
        d.mkdir(exist_ok=True)
        (d / "clip.json").write_text(json.dumps(clip, indent=1, ensure_ascii=False), encoding="utf-8")
        log(f"[find] #{i + 1} {c['start']:.0f}-{c['end']:.0f}s score {c['score_ai']:.1f} {lay['kind']}: {clip['hook']['text']!r}")
        clips.append(d)
    return clips, src


def make_one(d, words, b, log=log):
    from .render import render
    clip = json.loads((d / "clip.json").read_text(encoding="utf-8"))
    v = render(clip, d / "video.mp4", log=log)
    rep = gates.check(clip, v, words, b)
    rep.update({"title": clip["title"], "hook": clip["hook"]["text"], "why": clip["why"], "id": clip["id"]})
    (d / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    failed = [k for k, v in rep["gates"].items() if not v]
    log(f"[gates] {d.name}: {'all passed' if not failed else 'REVIEW: ' + ', '.join(failed)}")
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.clips")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("find", "make"):
        p = sub.add_parser(c)
        p.add_argument("stream")
        p.add_argument("--top", type=int, default=6)
        p.add_argument("--out")
    p = sub.add_parser("render"); p.add_argument("clip"); p.add_argument("--out")
    p = sub.add_parser("check"); p.add_argument("clipdir")
    p = sub.add_parser("stills"); p.add_argument("clip"); p.add_argument("--times", default="0.3,1.5,4,8,12,16")
    p = sub.add_parser("measure"); p.add_argument("videos", nargs="+"); p.add_argument("--no-ocr", action="store_true")
    p = sub.add_parser("judge"); p.add_argument("ours"); p.add_argument("refs"); p.add_argument("--out")
    a = ap.parse_args(argv)
    if a.cmd in ("find", "make"):
        out = Path(a.out) if a.out else OUT / "clips" / Path(a.stream).name
        try:
            dirs, src = find(a.stream, a.top, out)
        except sources.RightsError as e:
            log(f"[rights] {e}")
            return 1
        if a.cmd == "find":
            return 0 if dirs else 1
        reps = [make_one(d, src["words"], bar()) for d in dirs]
        return 1 if not reps else (0 if all(r["passed"] for r in reps) else 2)
    if a.cmd == "render":
        from .render import render
        clip = json.loads(Path(a.clip).read_text(encoding="utf-8"))
        render(clip, a.out or Path(a.clip).with_name("video.mp4"))
        return 0
    if a.cmd == "stills":
        from .render import stills
        clip = json.loads(Path(a.clip).read_text(encoding="utf-8"))
        ps = stills(clip, [float(x) for x in a.times.split(",")], Path(a.clip).parent / "stills")
        print("\n".join(map(str, ps)))
        return 0
    if a.cmd == "check":
        d = Path(a.clipdir)
        clip = json.loads((d / "clip.json").read_text(encoding="utf-8"))
        words = sources.words(clip["source"]["folder"]) or []
        rep = gates.check(clip, d / "video.mp4", words, bar())
        print(json.dumps(rep["gates"], indent=1))
        return 0 if rep["passed"] else 2
    if a.cmd == "measure":
        for v in a.videos:
            print(json.dumps(measure.measure(v, ocr=not a.no_ocr), ensure_ascii=False))
        return 0
    if a.cmd == "judge":
        from . import judge
        res = judge.run(Path(a.ours), Path(a.refs), bar(), ask=brain_ask(), log=log)
        out = Path(a.out) if a.out else Path(a.ours) / "judge.json"
        out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        return 0


if __name__ == "__main__":
    sys.exit(main())
