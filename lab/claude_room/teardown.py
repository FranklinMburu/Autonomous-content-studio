"""Objective teardown of a Short (20 Nov 2026): what the winners actually do, measured, not guessed.

python3 teardown.py out_dir file1.mp4 file2.mp4 ...
Per file: duration, cuts (ffmpeg scene > 0.3) and cut rate, first cut time, longest shot, on-screen text by second
(tesseract OCR, with vertical position band), loudness (LUFS), share of time with sound above -35 dB,
first-vs-last frame similarity (loop), and a 1 fps contact strip. Writes <id>.json, <id>.strip.jpg and summary.md.
"""
import json, re, subprocess, sys
from pathlib import Path
import cv2
import numpy as np


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(f):
    o = run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
             "-of", "json", str(f)]).stdout
    j = json.loads(o); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return float(j["format"]["duration"]), s["width"], s["height"], round(int(n) / int(d), 2)


def cuts(f):
    e = run(["ffmpeg", "-hide_banner", "-i", str(f), "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"]).stderr
    return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", e)]


def loud(f):
    e = run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    return float(m[-1]) if m else None


def sound_share(f, dur):
    e = run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=n=-35dB:d=0.3", "-f", "null", "-"]).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", e)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", e)]
    sil = sum(b - a for a, b in zip(st, en + [dur] * (len(st) - len(en))))
    return round(1 - sil / dur, 2) if dur else None


def frame(cap, t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read()
    return fr if ok else None


def ocr(fr):
    h = fr.shape[0]; g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=1.5, fy=1.5)
    tsv = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "11", "tsv"], input=cv2.imencode(".png", g)[1].tobytes(),
                         capture_output=True).stdout.decode(errors="ignore")
    words = []
    for line in tsv.splitlines()[1:]:
        p = line.split("\t")
        if len(p) == 12 and p[11].strip() and float(p[10]) > 60 and len(p[11].strip()) > 1:
            y = (int(p[7]) + int(p[9]) / 2) / 1.5 / h
            words.append((p[11].strip(), round(y, 2)))
    if not words:
        return ""
    band = lambda y: "top" if y < 0.33 else ("mid" if y < 0.66 else "bot")
    out = {}
    for w, y in words:
        out.setdefault(band(y), []).append(w)
    return " | ".join(f"{k}: {' '.join(v)}" for k, v in out.items())


def main(od, files):
    od = Path(od); od.mkdir(parents=True, exist_ok=True); rows = []
    for f in map(Path, files):
        dur, w, h, fps = probe(f); c = cuts(f)
        shots = np.diff([0] + c + [dur]) if dur else []
        cap = cv2.VideoCapture(str(f))
        text = {}
        for t in [0, 0.5, 1, 1.5, 2, 3] + list(range(4, int(dur), 2)):
            fr = frame(cap, t)
            if fr is not None:
                tx = ocr(fr)
                if tx:
                    text[str(t)] = tx
        a, b = frame(cap, 0.05), frame(cap, max(dur - 0.15, 0))
        loop = None
        if a is not None and b is not None:
            ha = cv2.calcHist([cv2.resize(a, (64, 64))], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)
            hb = cv2.calcHist([cv2.resize(b, (64, 64))], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)
            loop = round(float(cv2.compareHist(cv2.normalize(ha, ha), cv2.normalize(hb, hb), cv2.HISTCMP_CORREL)), 2)
        r = {"id": f.stem, "dur": round(dur, 1), "res": f"{w}x{h}", "fps": fps, "cuts": len(c),
             "cuts_per_10s": round(len(c) / dur * 10, 1) if dur else 0, "first_cut": c[0] if c else None,
             "longest_shot": round(float(max(shots)), 1) if len(shots) else None, "lufs": loud(f), "sound_share": sound_share(f, dur),
             "loop_sim": loop, "cut_times": c, "text": text}
        (od / f"{f.stem}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
        run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", "fps=1,scale=160:-1,tile=12x6", "-frames:v", "1", str(od / f"{f.stem}.strip.jpg")])
        rows.append(r); print(f.stem, r["dur"], r["cuts_per_10s"], r["first_cut"], r["loop_sim"], flush=True)
    md = ["| id | dur | cuts/10s | first cut | longest shot | LUFS | sound | loop | text @0s | text @1s |", "|" + "---|" * 10]
    for r in rows:
        md.append(f"| {r['id']} | {r['dur']} | {r['cuts_per_10s']} | {r['first_cut']} | {r['longest_shot']} | {r['lufs']} | {r['sound_share']} | "
                  f"{r['loop_sim']} | {r['text'].get('0', '')[:60]} | {r['text'].get('1', '')[:60]} |")
    (od / "summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
