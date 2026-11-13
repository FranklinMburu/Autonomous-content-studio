"""World Clips: from today's world picks to moments worth a Short (13 Nov 2026).

    python lab/clips/world.py plan --hot hot_world.json --top 3 --out stories.json
    python lab/clips/world.py find --stories stories.json --dir details/ --per 3 --out moments.json

YouTube blocks cloud servers, so the laptop helper fetches each picked video's public details (kind "info"): YouTube's
own "most replayed" heatmap, chapters and English auto-subtitles. `find` takes the most-replayed peaks (viewers
rewinding = the moments people care about), reads what is said around each, lets the AI judge choose the best and
title them, and writes moments for the laptop to download as sections ([T-60, T+90] s) and for shorts.py to make.
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai_pass as AI  # noqa: E402

VID = re.compile(r"(?:v=|youtu\.be/|shorts/|live/)([A-Za-z0-9_-]{6,20})")


def plan(a):
    d = json.loads(Path(a.hot).read_text())
    out = []
    for e in d.get("sources") or []:
        m = VID.search(e.get("url") or "")
        if not m or any(o["vid"] == m.group(1) for o in out):
            continue
        out.append({"vid": m.group(1), "url": f"https://www.youtube.com/watch?v={m.group(1)}", "title": e.get("title", ""),
                    "who": e.get("channel") or e.get("handle") or "", "why": f"{e.get('views', 0):,} views, {e.get('lift')}x the show's usual"})
        if len(out) >= a.top:
            break
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for o in out:
        print(f"story: {o['title'][:80]} ({o['who']}; {o['why']})")


def subs_text(p):
    """English auto-subtitles (json3) -> [(t_seconds, text)]."""
    if not p.exists():
        return []
    out = []
    for ev in json.loads(p.read_text()).get("events", []):
        t = ev.get("tStartMs", 0) / 1000
        txt = "".join(s.get("utf8", "") for s in ev.get("segs") or []).replace("\n", " ").strip()
        if txt:
            out.append((t, txt))
    return out


def peaks(heat, dur, k, gap=120):
    """Most-replayed peaks: [(t_mid, value)], at least `gap` s apart, not in the first minute or the last 30 s."""
    pts = sorted(((h["start_time"] + h["end_time"]) / 2, h["value"]) for h in heat or [] if "value" in h)
    pts = [p for p in pts if 60 <= p[0] <= dur - 30]
    out = []
    for t, v in sorted(pts, key=lambda p: -p[1]):
        if all(abs(t - o[0]) >= gap for o in out):
            out.append((t, v))
        if len(out) >= k:
            break
    return out


def find(a):
    stories = json.loads(Path(a.stories).read_text())
    d = Path(a.dir)
    model = a.model or AI.pick_model()
    moments = []
    for st in stories:
        f = d / f"{st['vid']}.info.json"
        if not f.exists():
            print(f"[{st['vid']}] no details from the laptop: skipped"); continue
        info = json.loads(f.read_text())
        dur = float(info.get("duration") or 0)
        subs = subs_text(d / f"{st['vid']}.en.json3")
        cands = peaks(info.get("heatmap"), dur, a.per * 3)
        source = "most replayed"
        if not cands and subs:          # no heatmap (new or small video): one candidate per chapter, else every 4 minutes
            ch = info.get("chapters") or [{"start_time": t} for t in range(60, int(dur) - 60, 240)]
            cands, source = [(c["start_time"] + 45, 0) for c in ch][: a.per * 3], "chapters"
        if not cands:
            print(f"[{st['vid']}] no heatmap, chapters or subtitles: skipped"); continue
        blocks = []
        for i, (t, v) in enumerate(cands):
            said = " ".join(x for tt, x in subs if t - 50 <= tt <= t + 40)[:900]
            blocks.append(f"MOMENT i={i} t={int(t)} replay={v:.2f}\nSAID: {said or '-'}")
        prompt = (f"You pick moments for a world-news and culture clip channel (Shorts that do 250K+ views: a famous person "
                  f"says something surprising, controversial, emotional or funny; a reveal; a clash). Video: \"{info.get('title')}\" "
                  f"({info.get('channel')}). These are the moments viewers {source == 'most replayed' and 'replay most' or 'reach at each chapter'}. "
                  f"Choose the best {a.per} (or fewer if weak) and for each give a title in the clip-channel style "
                  "(\"[Name] EXPOSED / ADMITS / was SHOCKED ...\", under 90 characters, 2 emoji at the end), never inventing "
                  "what was said. Return JSON: a list of {\"i\": index, \"score\": 0-10, \"title\": \"\", \"why\": \"one line\"}.\n\n"
                  + "\n\n".join(blocks))
        r = AI.call(model, [{"text": prompt}]) or []
        picks = [x for x in (r if isinstance(r, list) else r.get("moments", [])) if isinstance(x, dict) and isinstance(x.get("i"), int) and 0 <= x["i"] < len(cands)]
        if not picks:   # the judge gave nothing: keep the most-replayed ones
            picks = [{"i": i, "score": 5, "title": "", "why": source} for i in range(min(a.per, len(cands)))]
        for x in sorted(picks, key=lambda x: -float(x.get("score") or 0))[: a.per]:
            T = cands[x["i"]][0]
            sec_id = f"WC-{st['vid']}-{int(T)}"
            moments.append({"story": st["vid"], "url": st["url"], "who": st["who"], "show": info.get("title", ""), "T": round(T, 1),
                            "section": {"id": sec_id, "start": max(0, round(T - 60, 1)), "end": round(min(dur, T + 90), 1)},
                            "t": round(T - max(0, T - 60), 1), "title": x.get("title") or st["title"], "why": f"{source}; {x.get('why', '')}",
                            "score": float(x.get("score") or 0)})
            print(f"[{st['vid']}] @{int(T)//60}:{int(T)%60:02d} [{x.get('score')}] {x.get('title')}")
    Path(a.out).write_text(json.dumps(moments, indent=1, ensure_ascii=False))
    print(f"moments: {len(moments)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan"); p.add_argument("--hot", required=True); p.add_argument("--top", type=int, default=3); p.add_argument("--out", required=True)
    f = sub.add_parser("find"); f.add_argument("--stories", required=True); f.add_argument("--dir", required=True)
    f.add_argument("--per", type=int, default=3); f.add_argument("--out", required=True); f.add_argument("--model")
    a = ap.parse_args()
    {"plan": plan, "find": find}[a.cmd](a)


if __name__ == "__main__":
    main()
