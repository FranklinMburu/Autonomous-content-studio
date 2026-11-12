"""Transcription with word times: faster-whisper (MIT; CTranslate2 int8 on CPU).

Runs where the model can be downloaded (GitHub Actions; Hugging Face is blocked in Claude's sandbox), and the
result is saved as <stream>/words.json so it is made once per stream. A 3-6 h stream on a 4-core runner:
`base.en` int8 runs at roughly 10-20x real time on CPU (our measurement goes in docs/CLIPS_ENGINE.md history
once the first real stream runs); `small.en` is better but about 3x slower. Choose with CLIPS_WHISPER.
"""
import json, os
from pathlib import Path


def transcribe(video, out_json, model=None, log=print):
    from faster_whisper import WhisperModel   # imported here: only needed when words.json is missing
    model = model or os.environ.get("CLIPS_WHISPER", "base.en")
    log(f"[transcribe] faster-whisper {model} (int8, CPU)")
    m = WhisperModel(model, device="cpu", compute_type="int8", download_root=os.environ.get("CLIPS_MODEL_CACHE"))
    segs, info = m.transcribe(str(video), word_timestamps=True, vad_filter=True, beam_size=1,
                              condition_on_previous_text=False)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                          "p": round(w.probability, 3)})
    Path(out_json).write_text(json.dumps({"words": words, "source": f"faster-whisper {model}",
                                          "language": info.language}, indent=0), encoding="utf-8")
    log(f"[transcribe] {len(words)} words")
    return words
