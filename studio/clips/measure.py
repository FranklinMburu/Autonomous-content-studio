"""Measure any short video the same way: our clips, and the real top clips we compare them with.

Everything here is measured from the file (frames, audio, OCR), never by eye. The same numbers feed:
  - the research dataset (docs/clips/reference_measurements.csv),
  - the quality bar (studio/clips/bar.json),
  - the gates on every clip we make (gates.py),
  - the blind judge's "clip cards" (judge.py).
Needs only ffmpeg, numpy and (for captions) the tesseract binary. No models, no network.
"""
import json, re, shutil, subprocess, tempfile
from pathlib import Path


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=kw.pop("text", True), **kw)


def probe(path):
    r = _run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    return {"duration": round(float(d.get("format", {}).get("duration", 0) or 0), 2), "w": int(v.get("width", 0)),
            "h": int(v.get("height", 0)), "fps": round(float(num) / float(den or 1), 2), "has_audio": a is not None}


def loudness(path):
    """Integrated loudness (LUFS), loudness range (LU) and true peak (dBTP), ffmpeg ebur128."""
    r = _run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    g = lambda pat: (float(m.group(1)) if (m := re.search(pat, tail)) else None)  # noqa: E731
    return {"lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra": g(r"LRA:\s+(-?[\d.]+) LU"), "true_peak": g(r"Peak:\s+(-?[\d.]+) dBFS")}


def gray_frames(path, fps=10, w=72, h=128, start=0.0, dur=None):
    import numpy as np
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(path)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float)


def cuts(path, threshold=0.3):
    """Hard cuts: ffmpeg scene score above `threshold` (0.3 = the usual default for hard cuts)."""
    r = _run(["ffmpeg", "-nostats", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    ts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    out = []
    for t in ts:   # merge flashes: two cuts closer than 0.2 s count once
        if not out or t - out[-1] > 0.2:
            out.append(round(t, 2))
    return out


def motion(path):
    import numpy as np
    a = gray_frames(path, fps=10)
    if len(a) < 2:
        return {"motion_mean": 0.0, "still_pct": 100.0, "black_pct": 100.0, "frozen_max_s": 0.0}
    d = np.abs(np.diff(a, axis=0)).mean((1, 2))
    still = d < 0.3
    run = best = 0
    for s in still:
        run = run + 1 if s else 0
        best = max(best, run)
    return {"motion_mean": round(float(d.mean()), 2), "still_pct": round(float(still.mean() * 100), 1),
            "black_pct": round(float((a.mean((1, 2)) < 8).mean() * 100), 1), "frozen_max_s": round(best / 10, 1)}


def layout(path):
    """How the picture uses the 9:16 frame, frame by frame (2 per second).
    letterbox = a landscape band in the middle (bars, or a flat/blurred fill above and below) - the classic
    "stream clip" look; full = picture edge to edge (cropped/reframed); stack = two pictures one above the other
    (facecam over gameplay), seen as a sharp seam that stays at the same height."""
    import numpy as np
    a = gray_frames(path, fps=2, w=90, h=160)
    if not len(a):
        return {"layout": "unknown"}
    H = a.shape[1]
    kinds, bands = [], []
    seam_hist = np.zeros(H)
    for f in a:
        tex = np.abs(np.diff(f, axis=1)).mean(axis=1)           # horizontal texture per row
        rows = np.where(tex > 2.0)[0]
        band = (rows[-1] - rows[0] + 1) / H if len(rows) else 0.0
        jump = np.abs(np.diff(f.mean(axis=1)))
        seam_hist[1:][jump > 25] += 1
        bands.append(band)
        kinds.append("letterbox" if band < 0.72 else "full")
    seam = [r for r in np.where(seam_hist > 0.6 * len(a))[0] if 0.25 * H < r < 0.75 * H]
    n = len(kinds)
    share = {k: round(kinds.count(k) / n, 2) for k in ("letterbox", "full")}
    main = max(share, key=share.get)
    if seam and main == "full":
        main = "stack"
    hook = kinds[: max(1, min(n, 6))]
    return {"layout": main, "letterbox_share": share["letterbox"], "hook_layout": max(set(hook), key=hook.count),
            "content_band": round(float(np.median(bands)), 2), "seam_y": round(seam[0] / H, 2) if seam else None}


def speech_onset(path):
    """First moment the audio is clearly active (RMS above -35 dBFS for 0.15 s): when the hook starts talking."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-t", "8", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    if not len(x):
        return None
    hop = 160
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms)
    act = db > -35
    for i in range(n - 15):
        if act[i:i + 15].all():
            return round(i * hop / 16000, 2)
    return None


def _ocr(png):
    if not shutil.which("tesseract"):
        return []
    r = _run(["tesseract", str(png), "-", "--psm", "11", "tsv"])
    words = []
    for line in r.stdout.splitlines()[1:]:
        p = line.split("\t")
        if len(p) < 12:
            continue
        try:
            conf = float(p[10])
        except ValueError:
            continue
        txt = p[11].strip()
        if conf >= 60 and len(re.sub(r"[^A-Za-z0-9$%]", "", txt)) >= 2:
            words.append({"text": txt, "x": int(p[6]), "y": int(p[7]), "w": int(p[8]), "h": int(p[9]), "conf": conf})
    return words


def captions(path, info=None, every=1.0, hook_every=0.25, max_s=70, min_h=0.018):
    """Burned-in captions read by OCR (only text at least `min_h` of the frame tall: captions, not UI text): when the first words appear, where (fraction of height), how big, how many
    words at once, upper case or not, and the colour of the highlighted word."""
    import numpy as np
    from PIL import Image
    info = info or probe(path)
    dur = min(info["duration"], max_s)
    times = sorted(set([round(t * hook_every, 2) for t in range(int(3 / hook_every))] +
                       [round(3 + i * every, 2) for i in range(int(max(0, dur - 3) / every))]))
    found = []
    with tempfile.TemporaryDirectory() as tmp:
        for t in times:
            png = Path(tmp) / f"f{t:07.2f}.png"
            # 2x upscale helps tesseract on 360-720 px wide sources
            sc = "scale=iw*2:ih*2" if info["w"] < 600 else "scale=iw:ih"
            subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                            "-vf", sc, str(png)], capture_output=True)
            if not png.exists():
                continue
            ws = [w for w in _ocr(png) if w["h"] >= min_h * (2 if info["w"] < 600 else 1) * info["h"]]
            if not ws:
                continue
            im = np.asarray(Image.open(png).convert("RGB")).astype(int)
            H, W = im.shape[:2]
            cols = []
            for w in ws:
                box = im[w["y"]:w["y"] + w["h"], w["x"]:w["x"] + w["w"]].reshape(-1, 3)
                bright = box[box.max(1) > 170]
                if len(bright):
                    r, g, b = np.median(bright, axis=0)
                    cols.append("yellow" if r > 180 and g > 180 and b < 120 else "green" if g > 170 and r < 150 and b < 150
                                else "white" if min(r, g, b) > 180 else "red" if r > 180 and g < 110 else "other")
            found.append({"t": t, "n": len(ws), "y": float(np.median([(w["y"] + w["h"] / 2) / H for w in ws])),
                          "hpx": float(np.median([w["h"] / H for w in ws])),
                          "upper": float(np.mean([w["text"].upper() == w["text"] for w in ws])),
                          "colors": cols, "text": " ".join(w["text"] for w in ws)})
    if not found:
        return {"caption_frames_pct": 0.0, "first_text_s": None}
    from collections import Counter
    c = Counter(x for f in found for x in f["colors"])
    accent = [k for k, _ in c.most_common() if k not in ("white", "other")]
    return {"caption_frames_pct": round(100 * len(found) / len(times), 1),
            "first_text_s": found[0]["t"], "first_text": found[0]["text"][:80],
            "caption_y": round(float(np.median([f["y"] for f in found])), 2),
            "caption_h": round(float(np.median([f["hpx"] for f in found])), 3),
            "words_on_screen": float(np.median([f["n"] for f in found])),
            "upper_pct": round(100 * float(np.mean([f["upper"] for f in found])), 0),
            "accent_color": accent[0] if accent else None,
            "colors": dict(c.most_common(4))}


def measure(path, ocr=True):
    """All the numbers for one short video, as one flat dict."""
    path = Path(path)
    info = probe(path)
    m = {"file": path.name, **info}
    m.update(loudness(path) if info["has_audio"] else {"lufs": None, "lra": None, "true_peak": None})
    c = cuts(path)
    m["cuts"] = len(c)
    m["cuts_per_10s"] = round(10 * len(c) / max(info["duration"], 0.1), 2)
    shots = [b - a for a, b in zip([0.0] + c, c + [info["duration"]])]
    m["median_shot_s"] = round(sorted(shots)[len(shots) // 2], 2) if shots else None
    m["first_cut_s"] = c[0] if c else None
    m.update(motion(path))
    m.update(layout(path))
    m["speech_onset_s"] = speech_onset(path) if info["has_audio"] else None
    if ocr:
        m.update({k: v for k, v in captions(path, info).items() if k != "colors"})
    return m


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(json.dumps(measure(p), ensure_ascii=False))
