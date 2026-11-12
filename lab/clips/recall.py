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
        lag, _ = S.estimate_lag(cv["chat_rate"], cv["audio_burst"])
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
    if a.cands_out:
        base = peaks(fams["ALL TOGETHER"], 40)
        strong = [int(m["t"]) for m in sorted(eyes, key=lambda m: -m["score"]) if m["score"] >= 6][:30]
        cands = sorted(set(base) | {t for t in strong if all(abs(t - b) > 45 for b in base)})
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
