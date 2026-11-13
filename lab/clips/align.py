"""Exact answer key: find where each fan clip sits in the stream by matching its sound (not by its creation time).

    python lab/clips/align.py --key key.json --audio stream.m4a --clips-dir clipaudio/ [--out key_exact.json]

Each clip's audio (downloaded beside it as <index>.m4a) is turned into a 10 Hz log-energy fingerprint in 8 frequency
bands and slid along the stream's fingerprint (normalised cross-correlation). The best match gives the true offset;
its strength (0-1) says how sure. Offsets estimated from creation time are often minutes off (a clip can be made
long after the moment), which made the first recall test miss the stream's top clip.
"""
import argparse, json, subprocess
from pathlib import Path

import numpy as np

SR, HOP, BANDS = 8000, 800, 8      # 10 frames per second


def fingerprint(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = len(x) // HOP
    if n < 20:
        return None
    fr = x[:n * HOP].reshape(n, HOP) * np.hanning(HOP)
    sp = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    edges = np.geomspace(3, sp.shape[1] - 1, BANDS + 1).astype(int)
    e = np.log1p(np.stack([sp[:, a:b].sum(1) for a, b in zip(edges[:-1], edges[1:])], 1) * 1e3)
    e = np.diff(e, axis=0, prepend=e[:1])                    # changes, not levels: robust to volume differences
    return (e - e.mean(0)) / (e.std(0) + 1e-6)


def locate(stream, clip):
    m, n = len(clip), len(stream)
    L = 1 << int(np.ceil(np.log2(n + m)))
    score = np.zeros(n - m + 1)
    for b in range(BANDS):
        S, C = np.fft.rfft(stream[:, b], L), np.fft.rfft(clip[::-1, b], L)
        score += np.fft.irfft(S * C, L)[m - 1:n]
    # normalise by local energy of the stream window
    cs = np.concatenate([[0], np.cumsum((stream ** 2).sum(1))])
    local = np.sqrt(cs[m:] - cs[:-m]) * np.sqrt((clip ** 2).sum()) + 1e-6
    r = score / local
    i = int(np.argmax(r))
    return i / 10, float(r[i])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True); ap.add_argument("--audio", required=True)
    ap.add_argument("--clips-dir", required=True); ap.add_argument("--out")
    a = ap.parse_args()
    K = json.loads(Path(a.key).read_text())
    st = fingerprint(a.audio)
    print(f"stream fingerprint: {len(st)/36000:.2f} h")
    for i, k in enumerate(K["key"]):
        f = Path(a.clips_dir) / f"{i}.m4a"
        cf = fingerprint(f) if f.exists() else None
        if cf is None:
            print(f"  ?      clip {i} has no audio: keeps estimated offset {k['offset']}")
            continue
        off, conf = locate(st, cf)
        print(f"  {conf:.2f}  estimated {k['offset']:>6}  matched {off:>8.1f}  ({off - k['offset']:+.0f} s)  {k['title'][:50]}")
        k["offset_est"], k["match"] = k["offset"], round(conf, 3)
        if conf >= 0.35:
            k["offset"] = int(round(off))
    Path(a.out or a.key).write_text(json.dumps(K, indent=1))


if __name__ == "__main__":
    main()
