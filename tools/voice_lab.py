#!/usr/bin/env python3
"""Voice lab: the same episode script read by several free voice engines, for a BLIND listening test.

    python tools/voice_lab.py kokoro     <script.json> <out_dir>   # the current voice (studio/voice.py)
    python tools/voice_lab.py chatterbox <script.json> <out_dir>   # Resemble AI Chatterbox (MIT)
    python tools/voice_lab.py voxcpm     <script.json> <out_dir>   # OpenBMB VoxCPM2 (Apache-2.0), designed voice
    python tools/voice_lab.py blind      <out_dir>                 # shuffle into sample_A.mp3 ... + blind_key.json

Only engines whose model WEIGHTS allow commercial use are tested (a monetised channel is commercial use). OmniVoice
(the default engine of "OmniVoice Studio") is CC-BY-NC, so it is not used. Models download from Hugging Face at run
time and are cached by the workflow; nothing is stored in the repo. Each engine runs in its own Python environment
(their packages pin different versions). Every sample is levelled to -14 LUFS and fitted to the current voice's
length (the films are timed to it), so the test compares the voices, not loudness or speed.
"""
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
    from studio.voice import narrate
    s, _ = lines_of(script_path)
    narrate(s, str(out / "kokoro.wav"), str(out / "kokoro_timing.json"))


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
    design = ("(A warm, deep male documentary narrator in his forties, calm and gripping, clear British-neutral accent, "
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


def blind(out):
    target = seconds(out / "kokoro.wav")
    made = [p.stem for p in sorted(out.glob("*.wav")) if p.stem in ("kokoro", "chatterbox", "voxcpm")]
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


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "blind":
        blind(Path(sys.argv[2]))
    else:
        o = Path(sys.argv[3]); o.mkdir(parents=True, exist_ok=True)
        {"kokoro": kokoro, "chatterbox": chatterbox, "voxcpm": voxcpm}[cmd](sys.argv[2], o)
