"""Deep teardown of one Short: measures everything frame by frame (21 Nov 2026).

python3 deep_teardown.py VIDEO.mp4 OUT_DIR [--info INFO.json] [--subs SUBS.json3]

Writes OUT_DIR/<id>/:
  report.json    all numbers (meta, engagement, per-frame series, cuts, text, audio)
  report.md      human summary
  hook.jpg       first 2 s at 10 fps (what the viewer sees before deciding to swipe)
  sheet_NN.jpg   the whole video at 4 fps, 40 frames per sheet, labelled with time
"""
import json, re, subprocess, sys
from pathlib import Path
import cv2
import numpy as np

FPS_SAMPLE = 4


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    p = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    d = json.loads(p.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), {})
    num, den = (v.get("avg_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den) if float(den) else 0
    fmt = d.get("format", {})
    return {"width": v.get("width"), "height": v.get("height"), "fps": round(fps, 2), "vcodec": v.get("codec_name"),
            "duration": round(float(fmt.get("duration", 0) or 0), 2),
            "bitrate_kbps": round(int(fmt.get("bit_rate", 0) or 0) / 1000),
            "acodec": a.get("codec_name"), "audio_hz": a.get("sample_rate")}


def loudness(path):
    p = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    t = p.stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", t)
    lra = re.findall(r"LRA:\s+([\d.]+) LU", t)
    pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", t)
    return {"lufs": float(m[-1]) if m else None, "lra": float(lra[-1]) if lra else None,
            "true_peak_db": float(pk[-1]) if pk else None}


def audio_curve(path, step=0.5):
    """RMS per step (dB) and a crude music/sound-bed share: fraction of steps louder than -35 dB."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True)
    x = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768
    if x.size == 0:
        return {"rms_db": [], "sound_share": 0, "silent_gaps": []}
    n = int(16000 * step)
    rms = [float(20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9)) for i in range(0, len(x), n)]
    # spectral flatness per step (high = noisy/music-like texture, low = tonal speech) - rough indicator only
    flat = []
    for i in range(0, len(x), n):
        seg = x[i:i + n]
        if seg.size < 512:
            continue
        sp = np.abs(np.fft.rfft(seg * np.hanning(seg.size))) + 1e-9
        flat.append(float(np.exp(np.mean(np.log(sp))) / np.mean(sp)))
    gaps = [round(i * step, 1) for i, r in enumerate(rms) if r < -45]
    return {"rms_db": [round(r, 1) for r in rms], "sound_share": round(sum(r > -35 for r in rms) / len(rms), 3),
            "silent_steps_s": gaps[:40], "spectral_flatness_mean": round(float(np.mean(flat)), 3) if flat else None}


def colorfulness(img):
    b, g, r = cv2.split(img.astype(np.float32))
    rg, yb = r - g, 0.5 * (r + g) - b
    return float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))


def ocr(img):
    """Text on screen with vertical band (top/mid/bottom thirds)."""
    h = img.shape[0]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=1.5, fy=1.5)
    import tempfile, os
    fd, tmpn = tempfile.mkstemp(suffix=".png"); os.close(fd); tmp = Path(tmpn)
    cv2.imwrite(str(tmp), g)
    p = sh(["tesseract", str(tmp), "-", "--psm", "11", "tsv"])
    tmp.unlink(missing_ok=True)
    words = []
    for line in p.stdout.splitlines()[1:]:
        c = line.split("\t")
        if len(c) == 12 and c[11].strip() and c[10] not in ("-1",) and float(c[10]) >= 60 and len(c[11].strip()) > 1:
            y = int(c[7]) / 1.5
            band = "top" if y < h / 3 else ("mid" if y < 2 * h / 3 else "bottom")
            words.append((c[11].strip(), band, round(y / h, 2)))
    return words


def label(img, text):
    cv2.rectangle(img, (0, 0), (img.shape[1], 22), (0, 0, 0), -1)
    cv2.putText(img, text, (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def grid(frames, cols, w):
    if not frames:
        return None
    th = [cv2.resize(f, (w, int(f.shape[0] * w / f.shape[1]))) for f in frames]
    h = th[0].shape[0]
    rows = (len(th) + cols - 1) // cols
    out = np.zeros((rows * h, cols * w, 3), np.uint8)
    for i, t in enumerate(th):
        r, c = divmod(i, cols)
        out[r * h:r * h + t.shape[0], c * w:c * w + w] = t[:h]
    return out


def subs_words(path):
    if not path or not Path(path).exists():
        return []
    d = json.loads(Path(path).read_text())
    out = []
    for e in d.get("events", []):
        t0 = e.get("tStartMs", 0) / 1000
        for s in e.get("segs", []) or []:
            w = s.get("utf8", "").strip()
            if w:
                out.append((round(t0 + s.get("tOffsetMs", 0) / 1000, 2), w))
    return out


def main():
    vid, out = Path(sys.argv[1]), Path(sys.argv[2])
    info = subs = None
    if "--info" in sys.argv:
        info = sys.argv[sys.argv.index("--info") + 1]
    if "--subs" in sys.argv:
        subs = sys.argv[sys.argv.index("--subs") + 1]
    vid_id = vid.stem.replace("ref-", "")
    od = out / vid_id
    od.mkdir(parents=True, exist_ok=True)

    meta = probe(vid)
    eng = {}
    if info and Path(info).exists():
        j = json.loads(Path(info).read_text())
        keys = ["title", "channel", "channel_id", "channel_follower_count", "view_count", "like_count", "comment_count",
                "upload_date", "timestamp", "duration", "description", "tags", "categories", "language"]
        eng = {k: j.get(k) for k in keys if k in j}
        if eng.get("view_count"):
            eng["like_rate_%"] = round(100 * (eng.get("like_count") or 0) / eng["view_count"], 2)
            eng["comment_rate_%"] = round(100 * (eng.get("comment_count") or 0) / eng["view_count"], 3)
            if eng.get("channel_follower_count"):
                eng["views_per_sub"] = round(eng["view_count"] / max(1, eng["channel_follower_count"]), 1)

    cap = cv2.VideoCapture(str(vid))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = n / fps if fps else meta["duration"]

    # every frame: scene-change score; sampled frames: quality metrics
    prev_h, prev_g = None, None
    cuts, diffs = [], []
    samples, hook = [], []
    step = max(1, round(fps / FPS_SAMPLE))
    hook_step = max(1, round(fps / 10))
    series = {"t": [], "sharp": [], "bright": [], "sat": [], "color": [], "motion": []}
    text_by_sec = {}
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        t = i / fps
        small = cv2.resize(f, (180, 320))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        if prev_h is not None:
            d = 1 - cv2.compareHist(prev_h, hist, cv2.HISTCMP_CORREL)
            diffs.append(d)
            if d > 0.35 and (not cuts or t - cuts[-1] > 0.25):
                cuts.append(round(t, 2))
        if i % step == 0:
            gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            series["t"].append(round(t, 2))
            series["sharp"].append(round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 1))
            series["bright"].append(round(float(gray.mean()), 1))
            series["sat"].append(round(float(hsv[..., 1].mean()), 1))
            series["color"].append(round(colorfulness(small), 1))
            series["motion"].append(round(float(np.abs(g.astype(int) - prev_g.astype(int)).mean()), 2) if prev_g is not None else 0)
            samples.append(label(cv2.resize(f, (216, int(f.shape[0] * 216 / f.shape[1]))), f"{t:5.2f}s"))
            if i % (step * 2) == 0:
                for w, band, y in ocr(f):
                    text_by_sec.setdefault(round(t, 1), []).append(f"{w}@{band}")
        if t <= 2.0 and i % hook_step == 0:
            hook.append(label(f.copy(), f"{t:4.1f}s"))
        prev_h, prev_g = hist, g
        i += 1
    cap.release()

    shots = [b - a for a, b in zip([0] + cuts, cuts + [dur])]
    lo = loudness(vid)
    au = audio_curve(vid)
    words = subs_words(subs)
    first_word = words[0][0] if words else None
    wpm = round(60 * len(words) / dur, 1) if words and dur else None

    rep = {
        "id": vid_id, "meta": meta, "engagement": eng,
        "cuts": {"times": cuts, "count": len(cuts), "per_10s": round(10 * len(cuts) / dur, 2) if dur else None,
                 "first_cut_s": cuts[0] if cuts else None, "longest_shot_s": round(max(shots), 2) if shots else None,
                 "median_shot_s": round(float(np.median(shots)), 2) if shots else None},
        "quality": {k: {"mean": round(float(np.mean(v)), 1), "min": round(float(np.min(v)), 1)}
                    for k, v in series.items() if k != "t" and v},
        "series": series,
        "on_screen_text": {str(k): v for k, v in sorted(text_by_sec.items())},
        "text_seconds_share": round(len(text_by_sec) / max(1, len(series["t"]) / 2), 2),
        "audio": {**lo, **au},
        "speech": {"words": len(words), "wpm": wpm, "first_word_s": first_word,
                   "transcript": " ".join(w for _, w in words)[:3000]},
        "loop_similarity": None,
    }
    if samples:
        a = cv2.resize(samples[0], (64, 114)).astype(float)
        b = cv2.resize(samples[-1], (64, 114)).astype(float)
        rep["loop_similarity"] = round(1 - float(np.abs(a - b).mean()) / 255, 3)

    if hook:
        cv2.imwrite(str(od / "hook.jpg"), grid(hook, 7, 240), [cv2.IMWRITE_JPEG_QUALITY, 85])
    for k in range(0, len(samples), 40):
        cv2.imwrite(str(od / f"sheet_{k // 40:02d}.jpg"), grid(samples[k:k + 40], 8, 216), [cv2.IMWRITE_JPEG_QUALITY, 80])
    (od / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False))

    e = eng
    md = [f"# {e.get('title', vid_id)}",
          f"- channel {e.get('channel')} ({e.get('channel_follower_count')} subs) · uploaded {e.get('upload_date')}",
          f"- views {e.get('view_count')} · likes {e.get('like_count')} ({e.get('like_rate_%')}%) · comments {e.get('comment_count')} · views/sub {e.get('views_per_sub')}",
          f"- {meta['width']}x{meta['height']} @ {meta['fps']} fps, {meta['bitrate_kbps']} kbps, {meta['duration']} s",
          f"- cuts {len(cuts)} ({rep['cuts']['per_10s']}/10 s), first cut {rep['cuts']['first_cut_s']} s, median shot {rep['cuts']['median_shot_s']} s, longest {rep['cuts']['longest_shot_s']} s",
          f"- sharpness mean {rep['quality'].get('sharp', {}).get('mean')}, saturation {rep['quality'].get('sat', {}).get('mean')}, colourfulness {rep['quality'].get('color', {}).get('mean')}, motion {rep['quality'].get('motion', {}).get('mean')}",
          f"- audio {lo['lufs']} LUFS, LRA {lo['lra']}, sound present {au['sound_share']*100:.0f}% of time, flatness {au.get('spectral_flatness_mean')}",
          f"- speech: {len(words)} words, {wpm} wpm, first word at {first_word} s",
          f"- on-screen text in {rep['text_seconds_share']*100:.0f}% of sampled seconds; loop similarity {rep['loop_similarity']}",
          f"- transcript: {rep['speech']['transcript'][:600]}"]
    (od / "report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:3]))


if __name__ == "__main__":
    main()
