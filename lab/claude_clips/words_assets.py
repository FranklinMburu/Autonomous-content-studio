"""Download yt-sections release assets by name prefix and add Whisper word timestamps (24 Nov 2026, Clip Room).
Writes out/<name>.mp4 + out/<name>.json {"words":[{"w","s","e"}], "source": ...}. No AI beyond Whisper."""
import json, os, subprocess, sys, urllib.request
from pathlib import Path
repo, prefix = os.environ["GITHUB_REPOSITORY"], sys.argv[1]
tok = os.environ["GH_TOKEN"]
def api(u, accept="application/vnd.github+json"):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"Authorization": f"Bearer {tok}", "Accept": accept}))
rel = json.load(api(f"https://api.github.com/repos/{repo}/releases/tags/yt-sections"))
out = Path("out"); out.mkdir(exist_ok=True)
from faster_whisper import WhisperModel
import numpy as np
wm = WhisperModel("small.en", device="cpu", compute_type="int8")
for a in rel["assets"]:
    if not (a["name"].startswith(prefix) and a["name"].endswith(".mp4")):
        continue
    f = out / a["name"]
    f.write_bytes(api(a["url"], "application/octet-stream").read())
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = wm.transcribe(audio, word_timestamps=True, vad_filter=False)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for sg in segs for w in (sg.words or [])]
    f.with_suffix(".json").write_text(json.dumps({"source": a["name"], "words": words}))
    print("OK", a["name"], len(words), "words")
