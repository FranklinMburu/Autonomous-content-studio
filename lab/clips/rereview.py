"""Review Shorts again that are already made (13 Nov 2026: the free Gemini quota ran out mid-run and 6 Shorts were never
reviewed). Reads a shorts-* release's posts.json and videos, runs the same reviewer as shorts.py on the ones that were
not reviewed (or all, with --all), and writes the updated posts.json.

    python lab/clips/rereview.py --dir rel/ [--all]       # rel/ = posts.json + <id>.mp4 downloaded from the release
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shorts as S  # noqa: E402
AI = S.AI


def unreviewed(p):
    sc = p.get("scores") or {}
    return p.get("reviewed") is False or not p.get("checks") or sc.get("overall") in (None, 0, 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--all", action="store_true"); ap.add_argument("--model")
    a = ap.parse_args()
    d = Path(a.dir)
    posts = json.loads((d / "posts.json").read_text())
    model = a.model or AI.pick_model()
    done = 0
    for p in posts:
        if not (a.all or unreviewed(p)):
            continue
        video = d / f"{p['id']}.mp4"
        if not video.exists():
            print(f"[{p['id']}] no video file: skipped"); continue
        small = S.lowres(video, d / f"{p['id']}_low.mp4", scale="360:640", fps=2)
        rv = AI.call(model, [{"text": S.REVIEW.format(title=p["title"], hook=p.get("hook", ""), spoken="(listen to the video)",
                                                      checks="\n".join(f"- {k}: {v}" for k, v in S.CHECKS.items()),
                                                      scores=", ".join(S.SCORES))}, S.video_part(small)]) or {}
        if isinstance(rv, list):
            rv = rv[0] if rv else {}
        ok = bool(rv.get("scores")) and bool(rv.get("checks"))
        if not ok:
            print(f"[{p['id']}] the reviewer gave no answer again (quota?)"); continue
        checks = {c.get("name"): bool(c.get("passed") is True) for c in rv.get("checks", []) if isinstance(c, dict)}
        passed = [k for k in S.CHECKS if checks.get(k)]
        sc = {k: float((rv.get("scores") or {}).get(k, 0) or 0) for k in S.SCORES}
        note = p.get("before_you_post", "").split(" NOT REVIEWED")[0]
        note = note.split("Checks failed:")[0].rstrip() + (" Checks failed: " + ", ".join(k for k in S.CHECKS if k not in passed) + "." if len(passed) < len(S.CHECKS) else "")
        p.update({"checks": rv.get("checks", []), "checks_passed": f"{len(passed)}/{len(S.CHECKS)}", "scores": sc, "reviewed": True,
                  "fix": rv.get("fix", ""), "predicted_views": S.band(sc["overall"]), "before_you_post": note, "rereviewed": True})
        done += 1
        print(f"[{p['id']}] reviewed: overall {sc['overall']}, checks {len(passed)}/{len(S.CHECKS)}; fix: {p['fix'][:100]}")
    (d / "posts.json").write_text(json.dumps(posts, indent=1, ensure_ascii=False))
    print(f"reviewed {done} Short(s)")


if __name__ == "__main__":
    main()
