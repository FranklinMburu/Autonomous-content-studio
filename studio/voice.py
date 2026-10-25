"""Stage: narration. Script -> narration.wav + timing.json with a start/end time for every word.

Uses Kokoro (open-source TTS, Apache-2.0 weights) via kokoro-onnx (MIT). The v1.1 model export
reports phoneme durations, so word times come from the model itself, not from guesses.
"""
import json, re
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from .paths import models_dir

GAP_LINE, GAP_BEAT, LEAD_IN, TAIL = 0.22, 0.45, 0.15, 0.4
_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen " \
        "sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
_engine = None


def engine():
    global _engine
    if _engine is None:
        d = models_dir()
        _engine = Kokoro(str(d / "kokoro-v1.0.onnx"), str(d / "voices-v1.0.bin"))
    return _engine


def _two(n):
    if n < 20:
        return _ONES[n]
    return _TENS[n // 10] + ("" if n % 10 == 0 else "-" + _ONES[n % 10])


def spoken(word):
    """How a written word should be said. Years like 2023 -> 'twenty twenty-three'."""
    m = re.fullmatch(r"([^\d]*)(1[1-9]\d\d|20\d\d)([^\d]*)", word)
    if m:
        y = int(m.group(2)); hi, lo = divmod(y, 100)
        if 2000 <= y <= 2009:
            say = "two thousand" + ("" if lo == 0 else " " + _ONES[lo])
        else:
            say = _two(hi) + " " + ("hundred" if lo == 0 else ("oh " + _ONES[lo] if lo < 10 else _two(lo)))
        return m.group(1) + say + m.group(3)
    return word


def _groups(timings):
    """Split phoneme timings into word groups at spaces; drop pure-punctuation groups."""
    groups, cur = [], []
    for tm in timings:
        if tm.phoneme == " ":
            if cur:
                groups.append(cur); cur = []
        else:
            cur.append(tm)
    if cur:
        groups.append(cur)
    return [g for g in groups if any(re.search(r"\w", x.phoneme) for x in g)]


def _plen(s):
    return max(1, len(re.sub(r"[^\w]", "", s.replace("ˈ", "").replace("ˌ", ""))))


def _align(exp, groups):
    """Monotonic alignment of words (expected phoneme lengths) to spoken phoneme groups.
    Moves: 1 word:1 group, 2 words:1 group (merged in speech), 1 word:2-3 groups (split).
    Returns list of (word_indices, group_indices) or None."""
    act = [_plen("".join(x.phoneme for x in g)) for g in groups]
    n, m = len(exp), len(act)
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    prev = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    moves = [(1, 1, 0), (2, 1, 1.5), (1, 2, 1.5), (1, 3, 3), (3, 1, 3)]
    for i in range(n + 1):
        for j in range(m + 1):
            if cost[i][j] == INF:
                continue
            for di, dj, pen in moves:
                a, b = i + di, j + dj
                if a > n or b > m:
                    continue
                c = cost[i][j] + pen + abs(sum(exp[i:a]) - sum(act[j:b])) / max(1, sum(act[j:b]))
                if c < cost[a][b]:
                    cost[a][b] = c; prev[a][b] = (i, j)
    if cost[n][m] == INF:
        return None
    path, a, b = [], n, m
    while (a, b) != (0, 0):
        i, j = prev[a][b]; path.append((list(range(i, a)), list(range(j, b)))); a, b = i, j
    return path[::-1]


def _word_times(k, words, timings, offset, dur):
    """Map each written word to (start, end) using phoneme groups; fall back to estimates on mismatch."""
    groups = _groups(timings)
    exp = []
    for w in words:
        ph = k.tokenizer.phonemize(spoken(w), "en-us").strip()
        exp.append(_plen(ph))
    path = _align(exp, groups) if timings and groups else None
    if path:
        out = [None] * len(words)
        for wi, gi in path:
            s = groups[gi[0]][0].start; e = groups[gi[-1]][-1].end
            tot = sum(exp[i] for i in wi); t = s
            for i in wi:  # several words in one sound group: split by expected length
                d = (e - s) * exp[i] / tot
                out[i] = (words[i], offset + t, offset + t + d); t += d
        return out, True
    # fallback: proportional to word length, with pauses after punctuation
    wts = [len(w.strip(",.?!")) + 2 + (4 if w[-1] in ",.?!" else 0) for w in words]
    tot = sum(wts); t = offset; out = []
    for w, wt in zip(words, wts):
        d = dur * wt / tot; out.append((w, t, t + d)); t += d
    return out, False


def narrate(script, wav_path, timing_path):
    k = engine()
    voice = script.get("voice", "af_heart")
    speed = float(script.get("speed", 1.0))
    sr = 24000
    chunks = [np.zeros(int(LEAD_IN * sr), np.float32)]
    t = LEAD_IN
    lines, words, exact_all = [], [], True
    for bi, beat in enumerate(script["beats"]):
        for li, line in enumerate(beat["lines"]):
            say = " ".join(spoken(w) for w in line.split())
            audio, sr, timings = k.create_timed(say, voice=voice, speed=speed, lang="en-us")
            dur = len(audio) / sr
            wt, exact = _word_times(k, line.split(), timings, t, dur)
            exact_all &= exact
            for w, s, e in wt:
                words.append({"w": w, "start": round(s, 3), "end": round(e, 3), "line": len(lines), "beat": bi})
            lines.append({"beat": bi, "text": line, "start": round(t, 3), "end": round(t + dur, 3)})
            chunks.append(audio.astype(np.float32)); t += dur
            gap = GAP_BEAT if li == len(beat["lines"]) - 1 else GAP_LINE
            chunks.append(np.zeros(int(gap * sr), np.float32)); t += gap
    chunks.append(np.zeros(int(TAIL * sr), np.float32)); t += TAIL
    sf.write(str(wav_path), np.concatenate(chunks), sr)
    timing = {"duration": round(t, 3), "exact_word_timing": exact_all, "lines": lines, "words": words}
    json.dump(timing, open(timing_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return timing
