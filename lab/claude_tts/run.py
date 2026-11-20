"""Narrate lab/claude_tts/script.json with Kokoro (studio/voice.py) in several voices -> out/<voice>.wav + .json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from studio import voice
s = json.loads(Path("lab/claude_tts/script.json").read_text())
out = Path("out"); out.mkdir(exist_ok=True)
for v in s["voices"]:
    sc = {"voice": v, "speed": s["speed"], "beats": s["beats"]}
    t = voice.narrate(sc, str(out / f"{v}.wav"), str(out / f"{v}.json"))
    print(v, t["duration"], "exact" if t["exact_word_timing"] else "approx")
