"""Does the viewer panel agree with Franklin? (16 Nov 2026, Clipping Lab #3b)

Runs the reviewer (with the viewer panel, shorts.REVIEW) on Shorts Franklin has already sorted on the Studio Board:
Approved = kept, Skipped = not kept. Prints each Short's viewer score, the six answers and the angle, then how well the
viewer score and the old "overall" score separate kept from not kept (AUC: 1.0 = perfectly, 0.5 = a coin flip).
Read-only: nothing is written to the board or the releases.

    python lab/clips/viewer_calib.py --labels labels.json --dir clips/      # labels: [{"id","label":1|0}], clips/<id>.mp4
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shorts as S  # noqa: E402
AI = S.AI


def auc(pairs):
    pos = [s for s, y in pairs if y == 1 and s is not None]; neg = [s for s, y in pairs if y == 0 and s is not None]
    if not pos or not neg:
        return None
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return round(wins / (len(pos) * len(neg)), 3)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--labels", required=True); ap.add_argument("--dir", required=True)
    ap.add_argument("--model"); a = ap.parse_args()
    labels = json.loads(Path(a.labels).read_text()); d = Path(a.dir)
    model = a.model or AI.pick_model()
    rows = []
    for L in labels:
        v = d / f"{L['id']}.mp4"
        if not v.exists():
            print(f"[{L['id']}] no file"); continue
        small = S.lowres(v, d / f"{L['id']}_low.mp4", scale="360:640", fps=2)
        rv = AI.call(model, [{"text": S.REVIEW.format(title=L.get("title", ""), hook=L.get("title", ""), spoken="(listen to the video)",
                                                      checks="\n".join(f"- {k}: {t}" for k, t in S.CHECKS.items()),
                                                      scores=", ".join(S.SCORES), angles=", ".join(S.ANGLES),
                                                      viewer="\n".join(f"- {k}: {t}" for k, t in S.VIEWER.items()))},
                             S.video_part(small)]) or {}
        if isinstance(rv, list):
            rv = rv[0] if rv else {}
        if not rv.get("scores"):
            print(f"[{L['id']}] no answer (quota?)"); continue
        vp = S.viewer_panel(rv); overall = float((rv.get("scores") or {}).get("overall", 0) or 0)
        rows.append({"id": L["id"], "label": L["label"], "viewer": vp["score"], "overall": overall, "passed": vp["passed"],
                     "angle": vp["angle"], "failed": vp["failed"], "answers": vp["answers"]})
        print(f"[{L['id']}] {'KEPT' if L['label'] else 'skip'}  viewer {vp['score']}  ({vp['passed']} yes; failed {', '.join(vp['failed']) or '-'})"
              f"  angle {vp['angle']}  overall {overall}  | {L.get('title', '')[:60]}", flush=True)
    print("\nRESULT kept vs not kept (AUC, 1.0 = perfect, 0.5 = coin flip):")
    print(f"  viewer score:        {auc([(r['viewer'], r['label']) for r in rows])}")
    print(f"  viewer yes-count:    {auc([(int(r['passed'].split('/')[0]) if r['passed'] else None, r['label']) for r in rows])}")
    print(f"  reviewer overall:    {auc([(r['overall'], r['label']) for r in rows])}")
    print(f"  Shorts judged: {len(rows)} ({sum(r['label'] for r in rows)} kept)")
    Path(d / "viewer_calib.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
