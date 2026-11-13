#!/usr/bin/env python3
"""Voice lab: the same episode script read by several free voice engines, for a BLIND listening test.

    python tools/voice_lab.py kokoro     <script.json> <out_dir>   # the current voice (studio/voice.py)
    python tools/voice_lab.py chatterbox <script.json> <out_dir>   # Resemble AI Chatterbox (MIT)
    python tools/voice_lab.py voxcpm     <script.json> <out_dir>   # OpenBMB VoxCPM2 (Apache-2.0), designed voice
    python tools/voice_lab.py blind      <out_dir>                 # shuffle into sample_A.mp3 ... + blind_key.json
    python tools/voice_lab.py score      <script.json> <out_dir>   # measured scores -> scores.json + scores.md

Only engines whose model WEIGHTS allow commercial use are tested (a monetised channel is commercial use). OmniVoice
(the default engine of "OmniVoice Studio") is CC-BY-NC, so it is not used. Models download from Hugging Face at run
time and are cached by the workflow; nothing is stored in the repo. Each engine runs in its own Python environment
(their packages pin different versions). Every sample is levelled to -14 LUFS and fitted to the current voice's
length (the films are timed to it), so the test compares the voices, not loudness or speed.
"""
import os
import json
import random
import subprocess
import sys
from pathlib import Path

PAUSE = 0.22   # seconds between lines, close to the current narration


def lines_of(script_path):
    s = json.loads(Path(script_path).read_text(encoding="utf-8"))
    return s, [l.strip() for b in s["beats"] for l in b["lines"] if l.strip()]


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *a], check=True)


def seconds(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout
    return float(out or 0)


def join(chunks, sr, out_wav):
    import numpy as np
    import soundfile as sf
    gap = np.zeros(int(PAUSE * sr), np.float32)
    parts = []
    for c in chunks:
        parts += [np.asarray(c, np.float32).reshape(-1), gap]
    sf.write(out_wav, np.concatenate(parts), sr)


def kokoro(script_path, out):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import studio.story.__main__ as story   # the current story voice (STORY_VOICE), the one to beat
    narrate = story.narrate
    if os.environ.get("LAB_KOKORO_VOICE"):    # another channel's locked Kokoro voice, e.g. am_fenrir at speed 1.0
        story.STORY_VOICE = {**story.STORY_VOICE, "voice": os.environ["LAB_KOKORO_VOICE"],
                             "speed": float(os.environ.get("LAB_KOKORO_SPEED", "1.0"))}
    s, _ = lines_of(script_path)
    narrate(s, out)
    (out / "narration.wav").replace(out / "kokoro.wav"); (out / "timing.json").replace(out / "kokoro_timing.json")


def chatterbox(script_path, out):
    import torch
    from chatterbox.tts import ChatterboxTTS
    torch.set_num_threads(4)
    _, lines = lines_of(script_path)
    m = ChatterboxTTS.from_pretrained(device="cpu")
    chunks = []
    for i, l in enumerate(lines):
        torch.manual_seed(7)   # same voice, every line
        chunks.append(m.generate(l, exaggeration=0.6, cfg_weight=0.4).squeeze(0).numpy())
        print(f"chatterbox line {i + 1}/{len(lines)}", flush=True)
    join(chunks, m.sr, out / "chatterbox.wav")


def voxcpm(script_path, out):
    from voxcpm import VoxCPM
    import soundfile as sf
    _, lines = lines_of(script_path)
    m = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)
    sr = m.tts_model.sample_rate
    design = (f"({os.environ['LAB_VOICE_DESIGN']})" if os.environ.get("LAB_VOICE_DESIGN") else None) or ("(A warm, deep male documentary narrator in his forties, calm and gripping, clear British-neutral accent, "
              "measured storytelling pace)")
    first = m.generate(text=design + lines[0], cfg_value=2.0, inference_timesteps=10)
    sf.write(out / "voxcpm_ref.wav", first, sr)
    chunks = [first]
    for i, l in enumerate(lines[1:], 2):   # the designed voice is then cloned, so every line is the same person
        chunks.append(m.generate(text=l, cfg_value=2.0, inference_timesteps=10,
                                 prompt_wav_path=str(out / "voxcpm_ref.wav"), prompt_text=lines[0],
                                 reference_wav_path=str(out / "voxcpm_ref.wav")))
        print(f"voxcpm line {i}/{len(lines)}", flush=True)
    join(chunks, sr, out / "voxcpm.wav")


def qwen3(script_path, out):
    """Qwen3-TTS 1.7B (Alibaba, Apache-2.0 code and weights): a voice designed from a description for the first line,
    then that voice cloned for every other line (Base model), so the whole script is one person. CPU: float32, no
    FlashAttention (GPU only). Usage from the qwen-tts 0.1.1 model card."""
    import gc, torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(4)
    _, lines = lines_of(script_path)
    design = os.environ.get("LAB_VOICE_DESIGN", "A calm, deep male narrator in his thirties, clear neutral American accent, "
                            "confident and friendly, measured explainer pace, like a good tech teacher.")
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    wavs, sr = m.generate_voice_design(text=lines[0], language="English", instruct=design)
    sf.write(out / "qwen3_ref.wav", wavs[0], sr)
    chunks = [wavs[0]]
    del m; gc.collect()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
    prompt = m.create_voice_clone_prompt(ref_audio=str(out / "qwen3_ref.wav"), ref_text=lines[0], x_vector_only_mode=False)
    for i, l in enumerate(lines[1:], 2):     # always the ORIGINAL reference (never the previous line): no drift
        w, sr = m.generate_voice_clone(text=l, language="English", voice_clone_prompt=prompt)
        chunks.append(w[0])
        print(f"qwen3 line {i}/{len(lines)}", flush=True)
    join(chunks, sr, out / "qwen3.wav")


def blind(out):
    target = seconds(out / "kokoro.wav")
    made = [p.stem for p in sorted(out.glob("*.wav")) if p.stem in ("kokoro", "chatterbox", "voxcpm", "qwen3")]
    random.shuffle(made)
    key = {}
    for letter, eng in zip("ABCDEF", made):
        src = out / f"{eng}.wav"
        tempo = max(0.75, min(1.5, seconds(src) / target)) if target else 1.0
        ff("-i", str(src), "-af", f"atempo={tempo:.4f},loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100",
           "-b:a", "192k", str(out / f"sample_{letter}.mp3"))
        key[letter] = {"engine": eng, "original_seconds": round(seconds(src), 1), "tempo": round(tempo, 3)}
    (out / "blind_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"blind samples: {', '.join(key)} (key saved separately; don't open it before rating)")


def score(script_path, out):
    """Measure each voice the way a listener would judge it, so an agent that can't listen can still choose:
    - naturalness: UTMOS22 (predicted 1-5 listener score, the standard automatic MOS model);
    - clarity: Whisper word error rate against the script (did every word come out right?);
    - liveliness: pitch range (semitones, 10th-90th percentile) and how much it varies line to line; flat = boring;
    - pace: words per second before any speed fitting."""
    import re
    import numpy as np
    import librosa
    import torch
    from faster_whisper import WhisperModel
    _, lines = lines_of(script_path)
    ref = re.sub(r"[^a-z0-9' ]+", " ", " ".join(lines).lower()).split()
    mos = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
    asr = WhisperModel("small.en", device="cpu", compute_type="int8")
    res = {}
    for eng in ("kokoro", "chatterbox", "voxcpm", "qwen3"):
        w = out / f"{eng}.wav"
        if not w.exists():
            continue
        y16, _ = librosa.load(w, sr=16000)
        with torch.no_grad():
            m = float(mos(torch.from_numpy(y16).unsqueeze(0), 16000).mean())
        segs, _ = asr.transcribe(y16, beam_size=5, language="en")   # array, not a path: the old "av" can't decode
        hyp = re.sub(r"[^a-z0-9' ]+", " ", " ".join(x.text for x in segs).lower()).split()
        d = list(range(len(hyp) + 1))   # word-level edit distance
        for i, r in enumerate(ref, 1):
            prev, d[0] = d[0], i
            for j, h in enumerate(hyp, 1):
                prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
        f0, _, _ = librosa.pyin(y16, fmin=60, fmax=400, sr=16000)
        f0 = f0[~np.isnan(f0)]
        st = 12 * np.log2(f0 / np.median(f0)) if len(f0) else np.array([0.0])
        dur = len(y16) / 16000
        res[eng] = {"naturalness_mos": round(m, 2), "word_error_rate": round(d[-1] / max(1, len(ref)), 3),
                    "pitch_range_semitones": round(float(np.percentile(st, 90) - np.percentile(st, 10)), 1),
                    "words_per_second": round(len(ref) / dur, 2), "seconds": round(dur, 1)}
        print(eng, res[eng], flush=True)
    (out / "scores.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    rows = ["| Engine | Naturalness (MOS 1-5) | Word errors | Pitch range (semitones) | Words/s |", "|---|---|---|---|---|"]
    rows += [f"| {e} | {r['naturalness_mos']} | {r['word_error_rate']:.1%} | {r['pitch_range_semitones']} | {r['words_per_second']} |"
             for e, r in sorted(res.items(), key=lambda kv: -kv[1]["naturalness_mos"])]
    (out / "scores.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "blind":
        blind(Path(sys.argv[2]))
    elif cmd == "score":
        score(sys.argv[2], Path(sys.argv[3]))
    else:
        o = Path(sys.argv[3]); o.mkdir(parents=True, exist_ok=True)
        {"kokoro": kokoro, "chatterbox": chatterbox, "voxcpm": voxcpm, "qwen3": qwen3}[cmd](sys.argv[2], o)
