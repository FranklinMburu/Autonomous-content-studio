"""Make the clip's data file (clip.json) from a ranked candidate. The renderer draws exactly this file, nothing else,
so the same clip.json always gives the same video.

What goes in (each rule cites docs/clips/RESEARCH.md via bar.json):
  - an edit list: the moment, minus dead air (pauses > bar.max_pause_s, never next to the payoff), and when the payoff
    comes late a short cold open (the payoff line shown first, then the story from its start: same moment, so honest);
  - the hook text on screen from frame 0;
  - word-by-word captions (1-3 words on screen, the spoken word highlighted);
  - framing changes: a slightly tighter frame on every other sentence (a hard "zoom cut") and punch-ins on loud,
    emphatic words;
  - title, description (with where it is from and why we may use it), why it was chosen, and the scores.
"""
import hashlib, json, re

from .signals import CUES


def _words_in(words, a, b):
    return [w for w in words if w["start"] >= a - 0.05 and w["end"] <= b + 0.05]


def edit_list(words, start, end, peak, bar, audio_burst=None):
    """[(src_a, src_b)]: the window with long silences cut out, keeping the 3 s around the payoff intact."""
    maxp = bar.get("max_pause_s", 0.6)
    ws = _words_in(words, start, end)
    segs, a = [], start
    for w0, w1 in zip(ws, ws[1:]):
        gap = w1["start"] - w0["end"]
        near_peak = (peak - 4) <= w0["end"] <= (peak + 3) or (peak - 4) <= w1["start"] <= (peak + 3)
        loud = audio_burst is not None and any(audio_burst[int(t)] > 6 for t in range(int(w0["end"]), int(w1["start"]) + 1)
                                               if 0 <= t < len(audio_burst))
        if gap > maxp and not near_peak and not loud:
            segs.append((round(a, 3), round(w0["end"] + 0.12, 3)))
            a = w1["start"] - 0.08
    segs.append((round(a, 3), round(end, 3)))
    return [s for s in segs if s[1] - s[0] > 0.25]


def cold_open(words, segs, peak, bar):
    """When the payoff lands late, show its first words first (max bar.cold_open_s) - the hook a viewer can't scroll past."""
    first = segs[0][0]
    if peak - first < bar.get("cold_open_after_s", 9):
        return segs, None
    ws = [w for w in words if w["start"] >= peak - 1.0 and w["start"] <= peak + 3]
    if not ws:
        return segs, None
    a = ws[0]["start"] - 0.1
    b = a
    for w in ws:
        if w["end"] - a > bar.get("cold_open_s", 2.4):
            break
        b = w["end"] + 0.12
        if re.search(r"[.?!]$", w["w"]):
            break
    if b - a < 0.8:
        return segs, None
    return [(round(a, 3), round(b, 3))] + segs, {"src": [round(a, 3), round(b, 3)]}


def timeline(segs):
    out, T = [], 0.0
    for a, b in segs:
        out.append({"src": [a, b], "at": round(T, 3)})
        T += b - a
    return out, round(T, 3)


def to_timeline(edl, s):
    """Every timeline time at which source time s is shown (a cold open can show it twice)."""
    return [e["at"] + (s - e["src"][0]) for e in edl if e["src"][0] - 1e-6 <= s <= e["src"][1] + 1e-6]


def captions(words, edl, max_words=3):
    """Caption chunks on the timeline: words in order of the edit, at most max_words, broken at punctuation."""
    out = []
    for e in edl:
        ws = _words_in(words, *e["src"])
        chunk = []
        for w in ws:
            t0 = e["at"] + w["start"] - e["src"][0]
            t1 = e["at"] + w["end"] - e["src"][0]
            chunk.append({"w": re.sub(r"[^\w'$%?!-]", "", w["w"]).upper(), "start": round(t0, 3), "end": round(t1, 3)})
            if len(chunk) >= max_words or re.search(r"[.?!,]$", w["w"]):
                out.append(chunk)
                chunk = []
        if chunk:
            out.append(chunk)
    for i, c in enumerate(out):   # hold each chunk until the next one starts (no flicker in short pauses)
        nxt = out[i + 1][0]["start"] if i + 1 < len(out) else c[-1]["end"] + 0.4
        c[-1]["hold"] = round(min(nxt, c[-1]["end"] + 0.6), 3)
    return [{"words": [w for w in c if w["w"]], "start": c[0]["start"], "end": c[-1]["hold"]} for c in out if any(w["w"] for w in c)]


def emphasis(words, edl, audio_db=None, bar=None):
    """Punch-in times: reaction phrases, words shouted (top of this clip's loudness), '!' and ALL CAPS."""
    hits = []
    low = " ".join(re.sub(r"[^a-z' ]", "", w["w"].lower()) for w in words)
    cue_words = {c.split()[0] for c in CUES}
    loud = None
    if audio_db is not None:
        vals = [audio_db[int(w["start"])] for w in words if 0 <= int(w["start"]) < len(audio_db)]
        if vals:
            vals = sorted(vals)
            loud = vals[int(0.85 * (len(vals) - 1))]
    for e in edl:
        for w in _words_in(words, *e["src"]):
            raw = w["w"]
            plain = re.sub(r"[^a-z']", "", raw.lower())
            hot = "!" in raw or (raw.isupper() and len(raw) > 1) or plain in cue_words \
                or (loud is not None and 0 <= int(w["start"]) < len(audio_db) and audio_db[int(w["start"])] >= loud and plain)
            if hot:
                t = e["at"] + w["start"] - e["src"][0]
                if not hits or t - hits[-1] > 1.4:
                    hits.append(round(t, 3))
    _ = low
    return [{"t": t, "amount": 0.14} for t in hits]


def framing(edl, words, layout=None, video=None, peak_t=(), min_shot=1.6):
    """Shots, one per sentence: "wide" (the layout) and "focus" alternate - a hard cut every sentence, the pace
    the references have (2.1 cuts per 10 s). Focus = the facecam big (stack), the person talking full-screen (split2),
    or a tighter frame (letterbox / speaker). The payoff is always on focus: the reaction is what people came for."""
    from .layout import active_person
    shots, k = [], 0
    for e in edl:
        ws = _words_in(words, *e["src"])
        starts = [(e["at"], e["src"][0])] + [(e["at"] + w1["start"] - e["src"][0], w1["start"]) for w0, w1 in zip(ws, ws[1:])
                                             if re.search(r"[.?!,]$", w0["w"]) or w1["start"] - w0["end"] > 0.35]
        for t, src_t in starts:
            if shots and t - shots[-1]["t"] < min_shot:
                continue
            shots.append({"t": round(t, 3), "src": round(src_t, 3)})
    for i, sh in enumerate(shots):
        end_t = shots[i + 1]["t"] if i + 1 < len(shots) else 1e9
        on_payoff = any(sh["t"] - 0.5 <= p < end_t for p in peak_t)
        sh["view"] = "focus" if (on_payoff or k % 2 == 1) else "wide"
        k += 1
        sh["zoom"] = 1.0 if sh["view"] == "wide" else 1.22
        if layout and layout.get("kind") == "split2" and video is not None:
            nxt = shots[i + 1]["src"] if i + 1 < len(shots) else sh["src"] + 2
            sh["who"] = active_person(video, layout["people"], sh["src"], min(nxt, sh["src"] + 3))
    return shots


def make_clip(cand, src, words, cv, bar, layout, stream_title=""):
    segs = edit_list(words, cand["start"], cand["end"], cand["peak"], bar, cv.get("audio_burst"))
    segs, co = cold_open(words, segs, cand["peak"], bar)
    edl, dur = timeline(segs)
    caps = captions(words, edl, bar["captions"]["max_words"])
    hook_until = max(bar["hook"]["min_s"], min(bar["hook"]["max_s"], (edl[1]["at"] if co and len(edl) > 1 else 2.2)))
    r = src["rights"]
    where = r.get("title") or stream_title or "a live stream"
    credit = {"own": "Our own stream.", "program": f"Clipped through {r.get('program')} ({r.get('terms_url')}).",
              "permission": f"Used with permission from {r.get('granted_by')}.", "licence": f"Licence: {r.get('licence')}."}[r["source"]]
    disclose = "\n#ad" if r.get("disclosure_required") else ""
    clip = {
        "version": 1,
        "source": {"folder": str(src["folder"]), "video": src["video"].name, "rights": r},
        "edl": edl, "duration": dur, "cold_open": co, "peak": cand["peak"], "window": [cand["start"], cand["end"]],
        "layout": layout,
        "hook": {"text": cand["hook"], "until": round(hook_until, 2)},
        "captions": caps, "zooms": emphasis(words, edl, cv.get("audio_db")), "framing": framing(edl, words, layout, src["video"], to_timeline(edl, cand["peak"])),
        "style": bar["captions"],
        "title": cand["title"], "description": f"{cand['title']}\n\nFrom: {where}. {credit}{disclose}\n#shorts",
        "why": cand.get("why", ""), "kind": cand.get("kind", "other"), "ranked_by": cand.get("ranked_by"),
        "scores": {"signal": cand["score"], "rank": cand.get("score_ai")}, "signals": cand["signals"],
        "transcript": " ".join(w["w"] for e in edl for w in _words_in(words, *e["src"])),
    }
    clip["id"] = hashlib.sha1(json.dumps([clip["source"]["folder"], segs], sort_keys=True).encode()).hexdigest()[:10]
    return clip
