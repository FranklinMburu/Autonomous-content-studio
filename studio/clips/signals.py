"""Understand: turn a stream into per-second signal curves. Streams are long (3-6 h), so audio and video are read in
one streaming pass each and reduced right away (memory stays small).

Curves (one value per second of the stream):
  audio_db     loudness (RMS dBFS)            audio_burst  how much louder than the 10 s before (dB)
  bright_hi    share of energy above 2 kHz (screams, laughs, hype)
  scene        picture change (0-1)           chat_rate    messages/s (commands like !enter removed)
  chat_short   share of short messages        chat_emote   share of emote / ALL-CAPS messages
  chat_dup     share of the commonest message (copy-paste waves)   clips  viewer-clip coverage (log views)
  cues         reaction words in the transcript ("no way", "are you serious", "clip it", laughter)
  speech       words spoken per second

Evidence for the choice (docs/clips/RESEARCH.md): chat message count, message length and message similarity
predict highlights (Lightor, ICDE 2020); chat reacts AFTER the moment, so the chat curve is shifted back by a
lag that is estimated per stream (cross-correlation with the audio bursts), not assumed.
"""
import re, subprocess
from collections import Counter

import numpy as np

EMOTES = set("""kekw omegalul lul lol lmao lmaoo lmaooo lmaoooo pog pogchamp poggers pogu w l ww www wwww ll lll kappa
monkas pepega sadge copium aware ez gg clip lulw icant <3 xd xdd 5head ratio based kek""".split())
CUES = ["no way", "are you serious", "what the", "oh my god", "oh my gosh", "clip it", "clip that", "i can't believe",
        "let's go", "lets go", "no no no", "bro", "wait wait", "you're kidding", "are you kidding", "what did",
        "haha", "hahaha", "i'm leaving", "never told anyone", "i need to tell you", "the whole time", "insane",
        "oh no", "encore", "i will find you"]


def _ffmpeg_pcm(video, sr=16000):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                            stdout=subprocess.PIPE)


def audio_curves(video, sr=16000):
    p = _ffmpeg_pcm(video, sr)
    db, hi = [], []
    while True:
        b = p.stdout.read(sr * 2)
        if not b:
            break
        x = np.frombuffer(b, np.int16).astype(np.float32) / 32768
        fr = x[: len(x) // 1600 * 1600].reshape(-1, 1600)       # 0.1 s frames
        if not len(fr):
            continue
        rms = np.sqrt((fr ** 2).mean(1) + 1e-10)
        db.append(float(20 * np.log10(np.percentile(rms, 90))))
        spec = np.abs(np.fft.rfft(fr * np.hanning(1600), axis=1)) ** 2
        hi.append(float((spec[:, 200:].sum(1) / (spec.sum(1) + 1e-12)).mean()))   # bin 200 = 2 kHz
    p.wait()
    db = np.array(db)
    burst = np.zeros_like(db)
    for i in range(len(db)):
        prev = db[max(0, i - 10):i]
        burst[i] = db[i] - (np.median(prev) if len(prev) else db[i])
    return {"audio_db": db, "audio_burst": burst, "bright_hi": np.array(hi)}


def video_curves(video, n):
    """Picture change per second from a 2 fps, 64x36 grey pass (cheap enough for a 6 h stream)."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-an", "-vf", "fps=2,scale=64:36,format=gray",
                          "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    prev, vals = None, []
    while True:
        b = p.stdout.read(64 * 36)
        if len(b) < 64 * 36:
            break
        f = np.frombuffer(b, np.uint8).astype(np.float32)
        vals.append(0.0 if prev is None else float(np.abs(f - prev).mean() / 255))
        prev = f
    p.wait()
    v = np.array(vals + [0.0])
    sec = np.zeros(n)
    for i in range(n):
        sec[i] = v[2 * i: 2 * i + 2].max() if 2 * i < len(v) else 0
    return {"scene": sec}


def _norm(msg):
    return re.sub(r"\s+", " ", msg.strip().lower())


def chat_curves(chat, n):
    rate, short, emote, dup = (np.zeros(n) for _ in range(4))
    per = [[] for _ in range(n)]
    for t, _, m in chat:
        i = int(t)
        if 0 <= i < n and not m.strip().startswith("!"):     # bot commands (giveaways, !song) are not reactions
            per[i].append(m)
    for i in range(n):
        ms = per[i]
        rate[i] = len(ms)
        if ms:
            short[i] = np.mean([len(m) <= 12 for m in ms])
            emote[i] = np.mean([any(w in EMOTES for w in _norm(m).split()) or (m.isupper() and len(m) > 1) for m in ms])
    for i in range(n):   # similarity over a 5 s window: copy-paste waves
        win = [_norm(m) for j in range(max(0, i - 2), min(n, i + 3)) for m in per[j]]
        if len(win) >= 4:
            dup[i] = Counter(win).most_common(1)[0][1] / len(win)
    return {"chat_rate": rate, "chat_short": short, "chat_emote": emote, "chat_dup": dup}


def clip_curve(clips, n):
    c = np.zeros(n)
    for cl in clips:
        a = int(max(0, cl["vod_offset"]))
        b = int(min(n, a + cl.get("duration", 30)))
        c[a:b] += 1 + np.log1p(cl.get("views", 0))
    return {"clips": c}


def text_curves(words, n):
    cues, speech = np.zeros(n), np.zeros(n)
    if not words:
        return {"cues": cues, "speech": speech}
    for w in words:
        i = int(w["start"])
        if 0 <= i < n:
            speech[i] += 1
    toks = [(re.sub(r"[^a-z' ]", "", w["w"].lower()), w["start"]) for w in words]
    for k in range(len(toks)):
        for L in (1, 2, 3, 4, 5):
            phrase = " ".join(t for t, _ in toks[k:k + L])
            if phrase in CUES:
                i = int(toks[k][1])
                if 0 <= i < n:
                    cues[i] += 1
        if "!" in words[k]["w"] or "?" in words[k]["w"]:
            i = int(words[k]["start"])
            if 0 <= i < n:
                cues[i] += 0.3
    return {"cues": cues, "speech": speech}


def z(x, win=300):
    """Robust z-score against the surrounding 5 minutes (streams drift: a loud hour is not one long highlight)."""
    x = np.asarray(x, float)
    out = np.zeros_like(x)
    for i in range(0, len(x), 10):
        seg = x[max(0, i - win // 2): i + win // 2]
        med = np.median(seg)
        mad = np.median(np.abs(seg - med)) * 1.4826 + 1e-6
        sd = max(mad, seg.std() * 0.5, 1e-6)
        out[i:i + 10] = (x[i:i + 10] - med) / sd
    return out


def _peaks(x, thr, gap=20, k=20):
    idx = [i for i in np.argsort(-x) if x[i] >= thr]
    out = []
    for i in idx:
        if all(abs(i - j) >= gap for j in out):
            out.append(int(i))
        if len(out) >= k:
            break
    return sorted(out)


def estimate_lag(chat_rate, audio_burst, max_lag=30, default=5):
    """Seconds by which chat trails the stream, measured per stream: for each big chat ONSET (rate jumping above its
    own last 5 s) take the nearest loud burst before it (within max_lag s); the median gap is the lag.
    Returns (lag, share of chat onsets that found a burst). Falls back to `default` with fewer than 3 matches."""
    if chat_rate.sum() < 30:
        return default, 0.0
    prev = np.array([chat_rate[max(0, i - 5):i].mean() if i else 0 for i in range(len(chat_rate))])
    onset = z(np.clip(chat_rate - prev, 0, None))
    cp = _peaks(onset, 4.0, k=8)
    ap = _peaks(np.asarray(audio_burst, float), 6.0, gap=8, k=80)
    starts = [min([i for i in range(max(0, c - 10), c + 1) if onset[i] >= 2.0] or [c]) for c in cp]
    # vote: the lag at which the most chat-burst starts have a loud burst right before them (+-1 s); ties -> shorter
    votes = {lag: sum(any(abs((c - a) - lag) <= 1 for a in ap) for c in starts) for lag in range(0, max_lag + 1)}
    best = max(votes, key=lambda k: (votes[k], -k))
    if votes[best] < 3:
        return default, votes[best] / max(len(starts), 1)
    near = [c - a for c in starts for a in ap if abs((c - a) - best) <= 1]
    return int(round(float(np.median(near)))), round(votes[best] / len(starts), 2)


def shift_back(x, lag):
    return np.concatenate([x[lag:], np.zeros(lag)]) if lag else x


def curves(src, duration, log=print):
    n = int(np.ceil(duration))
    cv = {}
    log("[signals] audio")
    a = audio_curves(src["video"])
    for k, v in a.items():
        cv[k] = np.pad(v, (0, max(0, n - len(v))))[:n]
    log("[signals] picture")
    cv.update(video_curves(src["video"], n))
    cv.update(chat_curves(src["chat"], n))
    lag, corr = estimate_lag(cv["chat_rate"], cv["audio_burst"])
    for k in ("chat_rate", "chat_short", "chat_emote", "chat_dup"):
        cv[k] = shift_back(cv[k], lag)
    cv.update(clip_curve(src["viewer_clips"], n))
    cv.update(text_curves(src["words"], n))
    log(f"[signals] {n} s; chat lag {lag} s ({corr:.0%} of chat bursts matched); {len(src['chat'])} chat msgs; "
        f"{len(src['viewer_clips'])} viewer clips; {len(src['words'] or [])} words")
    return cv, {"chat_lag_s": lag, "chat_lag_corr": round(corr, 3), "seconds": n}
