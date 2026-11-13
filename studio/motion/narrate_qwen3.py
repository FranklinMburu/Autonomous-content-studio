"""The Tech Education voice since 13 Nov 2026 (Franklin): Qwen3-TTS 1.7B (Alibaba, Apache-2.0 code and weights).

One fixed reference recording (channels/te/voice_ref_qwen3.wav, designed once in the voice lab from a description and
chosen by Franklin after the AI listening panel) is cloned for every line, so every episode is the same person.
Never a second voice, never a pitch shift, never echo: the only change is `tempo` (ffmpeg atempo keeps the pitch).

Word times: Qwen3 gives none, so each line is transcribed with faster-whisper (word timestamps) and the heard words
are matched to the script's words; unmatched words get times in proportion to their length between their neighbours.
Lines are cached by text (out_dir/lines/), so a re-run or a second job only makes the missing ones (`only` = a shard).
"""
import difflib, hashlib, json, re, shutil, subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from ..paths import ROOT

SR = 24000


def _spoken(w):
    from ..voice import spoken          # years -> words, the same rule the Kokoro voice uses
    return spoken(w)


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def _lines(script):
    return [(bi, li, l.strip()) for bi, b in enumerate(script["beats"]) for li, l in enumerate(b["lines"]) if l.strip()]


def _key(text, q):
    return hashlib.sha1(json.dumps([text, q["ref_text"], q.get("tempo", 1.0), q.get("model")]).encode()).hexdigest()[:16]


def _trim(a, keep=0.04):
    loud = np.where(np.abs(a) > 0.012)[0]
    if not len(loud):
        return a
    k = int(keep * SR)
    return a[max(0, loud[0] - k):min(len(a), loud[-1] + k)]


def make_lines(script, out_dir, cfg, only=None, log=print):
    """Synthesise every line that is not cached yet (or only those whose index % n == k when only=(k, n))."""
    q = cfg["qwen3"]
    cache = Path(out_dir) / "lines"
    cache.mkdir(parents=True, exist_ok=True)
    todo = [(i, t) for i, (_b, _l, t) in enumerate(_lines(script))
            if not (cache / f"{_key(t, q)}.wav").exists() and (only is None or i % only[1] == only[0])]
    if not todo:
        return
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(int(q.get("threads", 4)))
    m = Qwen3TTSModel.from_pretrained(q.get("model", "Qwen/Qwen3-TTS-12Hz-1.7B-Base"), device_map="cpu", dtype=torch.float32)
    prompt = m.create_voice_clone_prompt(ref_audio=str(ROOT / q["ref_audio"]), ref_text=q["ref_text"], x_vector_only_mode=False)
    for n, (i, text) in enumerate(todo, 1):
        say = " ".join(_spoken(w) for w in text.split())
        w, sr = m.generate_voice_clone(text=say, language="English", voice_clone_prompt=prompt)
        raw = cache / f"raw_{i}.wav"
        sf.write(raw, np.asarray(w[0], np.float32), sr)
        dst = cache / f"{_key(text, q)}.wav"
        af = f"atempo={float(q.get('tempo', 1.0)):.4f},aresample={SR}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ac", "1", str(dst)], check=True)
        raw.unlink()
        a, _ = sf.read(dst, dtype="float32")
        sf.write(dst, _trim(a), SR)
        log(f"  [voice] line {i + 1}: {len(a) / SR:.1f} s ({n}/{len(todo)})")


def _word_times(words, heard, offset, dur):
    """Script words -> (word, start, end). heard = [(word, start, end)] from Whisper, relative to the line."""
    a = [_norm(_spoken(w)) for w in words]
    b = [_norm(h[0]) for h in heard]
    known = [None] * len(words)
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            known[blk.a + k] = (heard[blk.b + k][1], heard[blk.b + k][2])
    exact = sum(k is not None for k in known) >= 0.8 * len(words)
    out, i = [], 0
    while i < len(words):
        if known[i]:
            out.append((words[i], offset + known[i][0], offset + known[i][1])); i += 1
            continue
        j = i
        while j < len(words) and not known[j]:
            j += 1
        lo = known[i - 1][1] if i else 0.0
        hi = known[j][0] if j < len(words) else dur
        hi = max(hi, lo + 0.05 * (j - i))
        wts = [len(w.strip(",.?!")) + 2 for w in words[i:j]]
        t = lo
        for w, wt in zip(words[i:j], wts):
            d = (hi - lo) * wt / sum(wts)
            out.append((w, offset + t, offset + t + d)); t += d
        i = j
    return out, exact


def narrate(script, out_dir, cfg, log=print):
    out_dir = Path(out_dir)
    q, pace = cfg["qwen3"], cfg["pace"]
    make_lines(script, out_dir, cfg, log=log)
    from faster_whisper import WhisperModel
    asr = WhisperModel(q.get("asr", "base.en"), device="cpu", compute_type="int8")
    items = _lines(script)
    chunks = [np.zeros(int(pace["lead_in"] * SR), np.float32)]
    t = pace["lead_in"]
    lines, words, exact_all = [], [], True
    for n, (bi, li, text) in enumerate(items):
        p = out_dir / "lines" / f"{_key(text, q)}.wav"
        a, _ = sf.read(p, dtype="float32")
        dur = len(a) / SR
        from scipy.signal import resample_poly      # hand Whisper the samples (16 kHz): its own file decoder (PyAV)
        a16 = resample_poly(a, 2, 3).astype(np.float32)   # clashes with the av version qwen-tts installs (13 Nov run)
        segs, _info = asr.transcribe(a16, language="en", word_timestamps=True, beam_size=1)
        heard = [(w.word, w.start, w.end) for s in segs for w in (s.words or [])]
        wt, exact = _word_times(text.split(), heard, t, dur)
        exact_all &= exact
        for w, s, e in wt:
            words.append({"w": w, "start": round(s, 3), "end": round(e, 3), "line": len(lines), "beat": bi})
        lines.append({"beat": bi, "text": text, "start": round(t, 3), "end": round(t + dur, 3)})
        chunks.append(a); t += dur
        last_of_beat = n + 1 == len(items) or items[n + 1][0] != bi
        gap = pace["gap_beat"] if last_of_beat else pace["gap_line"]
        chunks.append(np.zeros(int(gap * SR), np.float32)); t += gap
    chunks.append(np.zeros(int(pace["tail"] * SR), np.float32)); t += pace["tail"]
    raw, out = out_dir / "voice_raw.wav", out_dir / "voice.wav"
    sf.write(raw, np.concatenate(chunks), SR)
    timing = {"duration": round(t, 3), "exact_word_timing": exact_all, "lines": lines, "words": words, "voice": "qwen3"}
    (out_dir / "timing.json").write_text(json.dumps(timing, indent=1, ensure_ascii=False), encoding="utf-8")
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "aresample=48000," + cfg["eq"], str(out)], check=True)
        raw.unlink()
    else:
        raw.replace(out)
    return timing
