"""Checks every clip must pass before it can be called finished. A clip that fails any gate is still made, but it
becomes a REVIEW pre-release plus an issue (never a finished release). Numbers come from bar.json."""
from . import measure as M
from .sources import ALLOWED_RIGHTS


def _inside(box, W, H, tol=0.02):
    x, y, w, h = box
    return x >= -tol * W and y >= -tol * H and x + w <= W * (1 + tol) and y + h <= H * (1 + tol)


def subject_in_frame(clip):
    lay = clip["layout"]
    W, H = lay["src"]
    if lay["kind"] == "stack":
        return _inside(lay["cam"], W, H) and (lay.get("face") is None or _inside(lay["face"], W, H))
    if lay["kind"] in ("split2", "speaker"):
        return all(_inside(p, W, H) for p in lay["people"])
    return True   # letterbox shows the whole picture


def text_in_safe_zone(clip, bar):
    st, z = clip["style"], bar["ui_safe"]
    y = st.get("y_by_layout", {}).get(clip["layout"]["kind"], st["y"])
    cap_ok = z["top"] <= y <= z["bottom"] and z["top"] <= st.get("y_focus", y) <= z["bottom"] and st["safe_x"][0] >= z["left"] and st["safe_x"][1] <= z["right"]
    hook_ok = z["top"] <= st.get("hook_y_by_layout", {}).get(clip["layout"]["kind"], st.get("hook_y", 0.17)) <= z["bottom"]
    return cap_ok and hook_ok


def captions_in_sync(clip, words):
    """Every caption word sits exactly where that word is spoken in the edit (within one frame)."""
    from .edit import to_timeline
    spoken = set()
    for w in words:
        for t in to_timeline(clip["edl"], w["start"]):
            spoken.add(round(t * 30))
    caps = [w for c in clip["captions"] for w in c["words"]]
    bad = [w for w in caps if not any(round(w["start"] * 30) + d in spoken for d in (-1, 0, 1))]
    return len(caps) > 0 and not bad, len(bad)


def check(clip, video, words, bar, m=None):
    m = m or M.measure(video, ocr=True)
    g = {}
    r = clip["source"]["rights"]
    g["rights_recorded"] = r.get("source") in ALLOWED_RIGHTS
    hook_t = min([x for x in (m.get("first_text_s"), m.get("speech_onset_s")) if x is not None] or [99])
    g["hook_in_first_second"] = bool(clip["hook"]["text"]) and hook_t <= bar["hook"]["by_s"]
    g["duration_in_range"] = bar["duration_s"]["min"] <= m["duration"] <= bar["duration_s"]["max"]
    ok, nbad = captions_in_sync(clip, words)
    g["captions_in_sync"] = ok
    g["captions_visible"] = (m.get("caption_frames_pct") or 0) >= bar["captions"]["min_visible_pct"]
    g["no_black_or_frozen"] = m["black_pct"] <= 1.0 and m["frozen_max_s"] <= bar["max_frozen_s"]
    g["loudness_in_range"] = m["lufs"] is not None and abs(m["lufs"] - bar["loudness"]["lufs"]) <= bar["loudness"]["tol"] \
        and (m["true_peak"] is None or m["true_peak"] <= bar["loudness"]["max_true_peak"])
    g["subject_in_frame"] = subject_in_frame(clip)
    g["text_outside_ui_zones"] = text_in_safe_zone(clip, bar)
    views = [(f.get("view"), f.get("who"), f.get("zoom")) for f in clip.get("framing", [])]
    shot_cuts = sum(1 for a_, b_ in zip(views, views[1:]) if a_ != b_)
    pace = (len(clip["edl"]) - 1 + shot_cuts) / max(m["duration"], 1) * 10
    g["pace_at_least_bar"] = pace >= bar["pace"]["min_cuts_per_10s"]
    return {"gates": g, "passed": all(g.values()), "measures": m, "edit_cuts_per_10s": round(pace, 2),
            "caption_words_out_of_sync": nbad}
