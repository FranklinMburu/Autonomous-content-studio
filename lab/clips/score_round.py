"""Lab: score one round of clips made from our own test streams.

    python lab/clips/score_round.py <round dir> <lab streams dir> <reference dir with *.measure.json>

Prints (Markdown):
  1. the moment finder against truth.json (which candidates overlap a real moment);
  2. every clip's measured features next to the reference medians (the "at least the median top clip" rule);
  3. the measured craft scorecard (studio/clips/judge.py measured_scores).
The AI half of the blind judge is not here: it needs the brain (GitHub Actions) - see docs/clips/ITERATIONS.md.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.clips.judge import measured_scores, _median  # noqa: E402

KEYS = [("duration", "s"), ("first_text_s", "s"), ("speech_onset_s", "s"), ("cuts_per_10s", ""), ("lufs", ""),
        ("caption_y", ""), ("words_on_screen", ""), ("caption_frames_pct", "%")]


def overlap(a, b):
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


def main(rnd, streams, refdir):
    bar = json.loads((ROOT / "studio/clips/bar.json").read_text())
    refs = [json.loads(p.read_text()) for p in Path(refdir).glob("*.measure.json")]
    med = {k: _median([r.get(k) for r in refs]) for k, _ in KEYS}
    print("### Moment finder vs truth\n")
    for sd in sorted(Path(rnd).glob("*/")):
        truth = json.loads((Path(streams) / sd.name / "truth.json").read_text())["moments"]
        cands = json.loads((sd / "candidates.json").read_text())["candidates"]
        row = []
        for i, c in enumerate(cands[:6]):
            hit = next((m["kind"] for m in truth if overlap((c["start"], c["end"]), (m["start"], m["end"])) >= 0.5 * (m["end"] - m["start"])), None)
            row.append(f"#{i + 1} {c['start']:.0f}-{c['end']:.0f}s {'= ' + hit if hit else 'miss'}")
        found = {m["kind"] for m in truth if any(overlap((c["start"], c["end"]), (m["start"], m["end"])) >= 0.5 * (m["end"] - m["start"]) for c in cands[:len(truth)])}
        print(f"- **{sd.name}**: {len(found)}/{len(truth)} real moments in the top {len(truth)}. " + "; ".join(row))
    print("\n### Clips: measured vs the 14 references (median)\n")
    print("| clip | " + " | ".join(k for k, _ in KEYS) + " | gates | craft score (hook, pace, captions, sound, duration) |")
    print("|---" * (len(KEYS) + 3) + "|")
    print("| **reference median** | " + " | ".join(str(med[k]) for k, _ in KEYS) + " | | |")
    for rep in sorted(Path(rnd).glob("*/*/report.json")):
        r = json.loads(rep.read_text())
        m = r["measures"]
        sc = measured_scores(m, refs, bar)
        failed = [k for k, v in r["gates"].items() if not v]
        print(f"| {rep.parent.parent.name}/{rep.parent.name[:2]} \"{r['hook']}\" | " + " | ".join(str(m.get(k)) for k, _ in KEYS)
              + f" | {'all pass' if not failed else 'FAIL ' + ', '.join(failed)} | "
              + ", ".join(f"{v:.0f}" for v in sc.values()) + f" (mean {sum(sc.values()) / len(sc):.1f}) |")


if __name__ == "__main__":
    main(*sys.argv[1:4])
