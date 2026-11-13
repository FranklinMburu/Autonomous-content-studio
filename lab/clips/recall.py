"""Proof stage (docs/clips/PROMPT.md §3.4): does the moment finder catch what really went viral?

    python lab/clips/recall.py --key key.json --audio audio.m4a --video low.mp4 [--words words.json] [--chat chat.json] --top 20

The answer key = the fans' own clips of that stream (views + estimated offset). The finder NEVER sees it. Each signal
family alone, then all together, picks its top-N moments; a real hit counts as found when a pick lands inside
[offset - 120 s, offset + duration + 60 s] (clip offsets are estimated from creation time, so the window is generous).
Prints recall by count and by views, and the combined top picks with what was said there (for the AI judge and Franklin).
"""
import argparse, json, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.clips import signals as S  # noqa: E402


def peaks(score, k, gap=45):
    s, out = score.copy(), []
    for _ in range(k):
        i = int(np.argmax(s))
        if s[i] <= -1e8:
            break
        out.append(i)
        s[max(0, i - gap):i + gap] = -1e9
    return sorted(out)


def zz(x):
    return S.z(np.asarray(x, float))


def load_chat(p):
    if not p or not Path(p).exists():
        return []
    d = json.loads(Path(p).read_text())
    out = []
    for m in d if isinstance(d, list) else d.get("comments", []):
        t = m.get("time_in_seconds", m.get("content_offset_seconds"))
        txt = m.get("message") or (m.get("message", {}) if isinstance(m.get("message"), dict) else "")
        if isinstance(txt, dict):
            txt = txt.get("body", "")
        if t is not None:
            out.append((float(t), "", str(txt)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True); ap.add_argument("--audio", required=True); ap.add_argument("--video")
    ap.add_argument("--words"); ap.add_argument("--chat"); ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--out", default="recall_result.json")
    ap.add_argument("--eyes", help="AI eyes moments (lab/clips/ai_pass.py eyes)")
    ap.add_argument("--judged", help="AI judge scores (lab/clips/ai_pass.py judge); adds the final finder")
    ap.add_argument("--cands-out", help="write the candidates for the AI judge here (ALL top 40 + strong eyes moments)")
    a = ap.parse_args()
    K = json.loads(Path(a.key).read_text())
    key = [k for k in K["key"] if k.get("views")]
    n = int(np.ceil(K["vod"]["duration"]))
    cv = {k: np.pad(v, (0, max(0, n - len(v))))[:n] for k, v in S.audio_curves(a.audio).items()}
    if a.video and Path(a.video).exists():
        cv.update(S.video_curves(a.video, n))
    words = json.loads(Path(a.words).read_text())["words"] if a.words and Path(a.words).exists() else []
    cv.update(S.text_curves(words, n))
    chat = load_chat(a.chat)
    if chat:
        cv.update(S.chat_curves(chat, n))
        lag, share = S.estimate_lag(cv["chat_rate"], cv["audio_burst"])
        print(f"chat: {len(chat):,} messages, lag {lag} s (matched {share:.0%} of chat bursts to a loud moment)")
        for k in ("chat_rate", "chat_short", "chat_emote", "chat_dup"):
            cv[k] = S.shift_back(cv[k], lag)
    pic = [k for k in cv if k not in ("audio_db", "audio_burst", "bright_hi", "cues", "speech") and not k.startswith("chat")]
    fams = {
        "audio (loudness, screams, laughter)": zz(cv["audio_burst"]) + 0.6 * zz(cv["bright_hi"]),
        "speech cues (transcript)": zz(cv["cues"]) + 0.3 * zz(cv["speech"]),
    }
    if pic:
        fams["picture change (low quality video)"] = sum(zz(cv[k]) for k in pic)
    if chat:
        fams["chat (speed, emotes, copy-paste waves)"] = zz(cv["chat_rate"]) + zz(cv["chat_emote"]) + 0.5 * zz(cv["chat_dup"])
    eyes = json.loads(Path(a.eyes).read_text())["moments"] if a.eyes and Path(a.eyes).exists() else []
    if eyes:
        ec = np.zeros(n)
        for m in eyes:
            i = int(m["t"])
            if 0 <= i < n:
                ec[max(0, i - 4):i + 5] = np.maximum(ec[max(0, i - 4):i + 5], m["score"])
        fams["AI eyes (vision on low-res frames)"] = ec
    fams["ALL TOGETHER"] = sum(np.clip(v if not k.startswith("AI eyes") else (v - 5), -2, 6) for k, v in fams.items())
    # HighlightMiner's idea (scoring.py): a bonus when independent families fire together (13 Nov 2026, measured here
    # side by side with ALL TOGETHER before it replaces anything)
    fire = []
    for k, v in fams.items():
        if k == "ALL TOGETHER":
            continue
        x = (v - 5) if k.startswith("AI eyes") else v
        hit = (x > (1.5 if not k.startswith("AI eyes") else 2)).astype(float)
        fire.append(np.convolve(hit, np.ones(9), "same") > 0)       # fired within +-4 s
    together = np.sum(fire, axis=0) if fire else np.zeros(n)
    fams["ALL + AGREEMENT BONUS"] = fams["ALL TOGETHER"] + 1.5 * (together >= 2) + 1.5 * (together >= 3)
    if a.cands_out:
        # signals are for RECALL, the judge for PRECISION: the judge sees what ANY signal flags, not only the fused top
        pool = list(peaks(fams["ALL TOGETHER"], 30)) + list(peaks(fams["ALL + AGREEMENT BONUS"], 20))
        for name, sc in fams.items():
            if not name.startswith("ALL"):
                pool += peaks(sc, 12)
        pool += [int(m["t"]) for m in sorted(eyes, key=lambda m: -m["score"]) if m["score"] >= 7][:40]
        cands = []
        for t in pool:                      # first come first kept (fused, then each family, then eyes), 30 s apart
            if all(abs(t - c) > 30 for c in cands):
                cands.append(t)
        cands = sorted(cands)
        Path(a.cands_out).write_text(json.dumps([{"t": t} for t in cands]))
        print(f"candidates for the AI judge: {len(cands)}")
    judged = json.loads(Path(a.judged).read_text())["judged"] if a.judged and Path(a.judged).exists() else []
    if judged:
        jc = np.full(n, -1e9)
        allz = fams["ALL TOGETHER"]
        for m in judged:
            try:
                i, sc = int(float(m["t"])), float(m["score"])
            except (TypeError, ValueError, KeyError):
                continue
            if 0 <= i < n:
                jc[i] = sc * 10 + float(allz[i])
        fams["ALL + AI JUDGE"] = jc
    total_views = sum(k["views"] for k in key)

    def found(pk, k):
        return any(k["offset"] - 120 <= p <= k["offset"] + (k.get("duration") or 30) + 60 for p in pk)

    res = {}
    print(f"\nAnswer key: {len(key)} fan clips of '{K['vod'].get('title')}' ({n/3600:.1f} h). Each finder picks its top {a.top}.\n")
    print(f"{'finder':40s} {'hits found':>11s} {'share of views':>15s}")
    for name, sc in fams.items():
        pk = peaks(sc, a.top)
        hit = [k for k in key if found(pk, k)]
        res[name] = {"found": len(hit), "of": len(key), "view_share": round(sum(k['views'] for k in hit) / max(1, total_views), 3), "picks": pk}
        print(f"{name:40s} {len(hit):>4d} of {len(key):<4d} {res[name]['view_share']:>14.0%}")
    best = "ALL + AI JUDGE" if judged else "ALL TOGETHER"
    allpk = res[best]["picks"]
    # how close each signal came: the percentile of its best second inside each fan clip's window (100 = the stream's peak)
    print("\nHow strongly each signal fired on each fan clip (percentile of its best second in the clip's window):")
    print("  " + " ".join(f"{n.split(' (')[0][:9]:>9s}" for n in fams) + "  clip")
    for k in sorted(key, key=lambda k: -k["views"]):
        lo, hi = max(0, k["offset"] - 30), min(n, k["offset"] + (k.get("duration") or 30) + 15)
        row = []
        for name, sc in fams.items():
            v = sc[lo:hi].max() if hi > lo else -1e9
            row.append(f"{100 * (sc < v).mean():>9.0f}" if v > -1e8 else f"{'-':>9s}")
        print("  " + " ".join(row) + f"  {k['views']:>6,} {k['title'][:40]}")
    if judged:
        print("\nALL + AI JUDGE by number of picks (a 3 h IRL stream can carry 20-40 Shorts):")
        for kk in (10, 20, 30, 40, 60):
            pk = peaks(fams["ALL + AI JUDGE"], kk)
            hit = [k for k in key if found(pk, k)]
            print(f"  top {kk:>2}: {len(hit):>2} of {len(key)} fan clips, {sum(k['views'] for k in hit)/max(1,total_views):.0%} of their views")
        order = sorted(((float(m["score"]), int(float(m["t"]))) for m in judged if isinstance(m.get("score"), (int, float)) and m.get("t") is not None), reverse=True)
        print("\nWhere the judge put each fan clip (its best-scored candidate inside the clip's window):")
        for k in sorted(key, key=lambda k: -k["views"]):
            inwin = [(i + 1, sc, t) for i, (sc, t) in enumerate(order) if k["offset"] - 120 <= t <= k["offset"] + (k.get("duration") or 30) + 60]
            r = f"rank {inwin[0][0]} of {len(order)}, score {inwin[0][1]}" if inwin else "never reached the judge"
            print(f"  {k['views']:>7,}  {k['title'][:45]:45s} {r}")
    print(f"\nPer fan clip (found by {best}?):")
    for k in sorted(key, key=lambda k: -k["views"]):
        print(f"  {'YES' if found(allpk, k) else 'no '}  {k['views']:>7,} views  @{k['offset']//60:>3d}:{k['offset']%60:02d}  {k['title'][:60]}")
    print(f"\nTop picks of {best} with what was said (new finds marked NEW):")
    jmap = {int(float(m["t"])): m for m in judged if m.get("t") is not None}
    picks = []
    for p in allpk:
        said = " ".join(w["w"] for w in words if p - 20 <= w["start"] <= p + 10)[:220]
        new = not any(k["offset"] - 120 <= p <= k["offset"] + (k.get("duration") or 30) + 60 for k in key)
        j = jmap.get(p, {})
        picks.append({"t": p, "new": new, "said": said, "judge": j})
        print(f"  {'NEW' if new else 'hit'} @{p//3600}:{p%3600//60:02d}:{p%60:02d}  " + (f"[{j.get('score')}] {j.get('title')} | " if j else "") + said)
    Path(a.out).write_text(json.dumps({"vod": K["vod"], "results": res, "picks": picks}, indent=1))


if __name__ == "__main__":
    main()
