"""Voice test 1: a more expressive free narrator than Kokoro.

Chatterbox (Resemble AI, MIT licence) reads the same lines at several 'exaggeration' (emotion) settings.
Benchmark narrator: fast (~226 words/min), dramatic, storyteller tone. Output: out/*.wav + out/log.txt.
"""
import os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


LINES = ("Ignaz Semmelweis ordered every student to scrub in bleach before touching a mother. "
         "The other doctors were offended. They were gentlemen. How could their hands be dirty? "
         "But in their clinic, mothers were dying of childbed fever. Three times more than in the midwives' clinic. "
         "You see, it's like cutting raw chicken, then making a salad without washing your hands. "
         "The doctor who told everyone to clean their hands died from an infected hand.")
t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "chatterbox-tts"], check=False)
log(f"install {time.time() - t0:.0f}s")
try:
    import torchaudio
    from chatterbox.tts import ChatterboxTTS
    t = time.time()
    model = ChatterboxTTS.from_pretrained(device="cuda")
    log(f"chatterbox load {time.time() - t:.0f}s")
    for ex, cfg in ((0.5, 0.5), (0.8, 0.35), (1.1, 0.3)):
        t = time.time()
        wav = model.generate(LINES, exaggeration=ex, cfg_weight=cfg)
        f = f"{OUT}/chatterbox_ex{ex}_cfg{cfg}.wav"
        torchaudio.save(f, wav, model.sr)
        dur = wav.shape[-1] / model.sr
        log(f"chatterbox ex={ex} cfg={cfg}: {dur:.1f}s audio, {len(LINES.split()) / dur * 60:.0f} wpm, made in {time.time() - t:.0f}s")
except Exception:
    log("CHATTERBOX FAILED", traceback.format_exc()[-2000:])
log(f"total {time.time() - t0:.0f}s")
