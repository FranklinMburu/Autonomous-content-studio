"""Sound for story videos: a music bed that ducks under the narrator, plus sound effects placed from the storyboard.

Benchmark (Ricks Clips, "Why the Second Draw Always Wins", measured 1 Nov 2026): the sound is never silent (a music
bed under the voice the whole time) and low "hits" / "whooshes" land every 2-5 s on the big visual moments.

    mix(board, timing, narration_wav, out_wav, music_dir=None, track=None, log=print) -> out_wav

Sound effects are GENERATED here (numpy only: shaped noise and tones), so they are free, unlimited and licence-free.
Music comes from the owner's private YouTube Audio Library folder (STORY_MUSIC_DIR); it is never committed, because
the library's terms don't allow redistributing the files. Without a music folder, the video gets effects only.
"""
import json, os, subprocess, zlib
from pathlib import Path

import numpy as np

SR = 48000
MUSIC_CATALOG = Path(__file__).parent / "music.json"   # names, moods and safe start points only (no audio)


# ---------- generated sound effects ----------

def _shaped_noise(dur, centre_fn, width_fn, seed=0):
    """Noise whose frequency band follows centre_fn(t)/width_fn(t) (Hz), built frame by frame in the frequency domain."""
    rng = np.random.default_rng(seed)
    n, hop = 2048, 512
    frames = int(dur * SR / hop) + 4
    out = np.zeros(frames * hop + n)
    win = np.hanning(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    for k in range(frames):
        t = k * hop / SR
        c, w = centre_fn(t), max(30.0, width_fn(t))
        mag = np.exp(-0.5 * ((freqs - c) / w) ** 2)
        spec = mag * np.exp(1j * rng.uniform(0, 2 * np.pi, len(freqs)))
        out[k * hop:k * hop + n] += np.fft.irfft(spec, n) * win
    out = out[:int(dur * SR)]
    return out / (np.abs(out).max() + 1e-9)


def _env(n, attack, release, peak=None):
    t = np.linspace(0, 1, n)
    p = peak if peak is not None else attack / (attack + release)
    return np.where(t < p, (t / max(p, 1e-6)) ** 2, np.exp(-((t - p) / max(1 - p, 1e-6)) * 4.0))


def whoosh(dur=0.55, seed=0):
    d = dur
    x = _shaped_noise(d, lambda t: 300 + 2600 * np.sin(np.pi * min(1, t / d)) ** 2, lambda t: 500 + 900 * (t / d), seed)
    x *= _env(len(x), 0.6, 0.4)
    pan = np.linspace(-0.7, 0.7, len(x))           # moves left to right, like something passing
    return np.stack([x * (1 - pan) / 2, x * (1 + pan) / 2], 1)


def impact(dur=1.4, seed=1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 50 * np.exp(-t * 9)                    # pitch drops: the "boom"
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    crack = _shaped_noise(0.25, lambda u: 1800, lambda u: 1500, seed) * np.exp(-np.arange(int(0.25 * SR)) / SR * 30)
    body[:len(crack)] += 0.5 * crack
    body /= np.abs(body).max()
    return np.stack([body, body], 1)


def riser(dur=1.6, seed=2):
    x = _shaped_noise(dur, lambda t: 250 + 5000 * (t / dur) ** 2, lambda t: 300 + 1500 * (t / dur), seed)
    t = np.arange(len(x)) / SR
    tone = np.sin(2 * np.pi * np.cumsum(220 + 600 * (t / dur) ** 2) / SR)
    y = (0.7 * x + 0.3 * tone) * (t / dur) ** 2
    y[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return np.stack([y, y], 1) / (np.abs(y).max() + 1e-9)


def tick(seed=3):
    n = int(0.06 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 120) + 0.4 * np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 90)
    return np.stack([y, y], 1) / np.abs(y).max()


def pop(seed=4):
    n = int(0.12 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(500 + 700 * t / 0.12) / SR) * np.exp(-t * 35)
    return np.stack([y, y], 1) / np.abs(y).max()


# ---------- where effects go (from the storyboard) ----------

def cues(board, timing):
    """(time, kind, gain) for every effect, read from the storyboard: scene changes, labels, crosses, counters,
    falls, the dim before the ending and a riser into the final shot. Spaced so they never pile up."""
    from . import board as B, lib as L
    L.set_timing(timing)
    built, _ = B.build_shots(board)
    shots = board.get("shots", [])
    out = []

    def bg(sh):
        b = sh.get("bg", "gradient")
        return b.get("type") if isinstance(b, dict) else b
    for i, (sh, bs) in enumerate(zip(shots, built)):
        t0 = bs[0]
        if i and bg(sh) != bg(shots[i - 1]):  # a whoosh only when the place changes (not on every cut)
            out.append((t0 - 0.12, "whoosh", 0.4))
        for it in sh.get("items", []):
            try:
                tin = B.when(it["in"], t0) if "in" in it else None
            except Exception:  # noqa: BLE001
                tin = None
            t = it.get("type")
            if t in ("cross", "dim") and tin is not None:      # the story's big beats only
                out.append((tin, "impact", 0.6))
            elif t == "calendar" and isinstance(it.get("count"), dict):
                c = it["count"]; a, b = int(c["from"]), int(c["to"])
                ts, dur = B.when(c.get("at"), t0), float(c.get("dur", 1.0))
                n = max(1, min(abs(b - a), 6))
                for k in range(n):
                    out.append((ts + dur * k / n, "tick", 0.25))
            elif t == "character":
                for st in it.get("states", []):
                    if st.get("pose") == "fall":
                        out.append((B.when(st["at"], t0), "impact", 0.5))
    if len(built) > 2:  # build tension into the last shot (the twist)
        out.append((built[-1][0] - 1.6, "riser", 0.35))
    out.sort()
    spaced, last = [], {}
    for t, k, g in out:  # benchmark: hits every 2-5 s at most; never two big sounds on top of each other
        gap = {"impact": 2.0, "whoosh": 4.5, "riser": 5.0, "tick": 0.1}.get(k, 0.5)
        if t < 0 or t - last.get(k, -99) < gap or (spaced and t - spaced[-1][0] < 0.35 and k != "tick"):
            continue
        spaced.append((t, k, g)); last[k] = t
    return spaced


def effects_track(cue_list, dur):
    track = np.zeros((int(dur * SR) + SR, 2))
    gen = {"whoosh": whoosh, "impact": impact, "riser": riser, "tick": tick, "pop": pop}
    for i, (t, k, g) in enumerate(cue_list):
        s = gen[k](seed=i) if k != "riser" else riser(seed=i)
        a = int(max(0, t) * SR)
        b = min(len(track), a + len(s))
        track[a:b] += s[:b - a] * g
    return track[:int(dur * SR)]


def _write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ---------- music ----------

def pick_track(script_title, music_dir, track=None):
    """The episode's music: the one named in script.json ("music"), else a stable pick from the catalogue."""
    if not music_dir or not Path(music_dir).is_dir():
        return None
    cat = json.loads(MUSIC_CATALOG.read_text(encoding="utf-8")) if MUSIC_CATALOG.exists() else {"tracks": []}
    usable = [t for t in cat["tracks"] if (Path(music_dir) / t["file"]).exists() and not t.get("skip")]
    if track:
        usable = [t for t in usable if track.lower() in t["file"].lower()] or usable
    if not usable:
        return None
    return usable[zlib.crc32(script_title.encode()) % len(usable)]


def mix(board, timing, narration_wav, out_wav, music_dir=None, track=None, title="", log=print):
    """Narration + ducked music + effects, loudness-matched for YouTube (-14 LUFS)."""
    out_wav, dur = Path(out_wav), float(timing["duration"])
    music_dir = music_dir or os.environ.get("STORY_MUSIC_DIR")
    cl = cues(board, timing)
    fx = out_wav.with_name("effects.wav")
    _write_wav(fx, effects_track(cl, dur))
    t = pick_track(title, music_dir, track)
    inputs = ["-i", str(narration_wav), "-i", str(fx)]
    if t:
        gain = -25.0 - float(t.get("lufs", -14))
        inputs += ["-ss", str(t.get("start", 0)), "-i", str(Path(music_dir) / t["file"])]
        graph = (f"[0]aresample={SR},aformat=channel_layouts=stereo,asplit=2[v][key];"
                 f"[2]aresample={SR},atrim=0:{dur:.2f},asetpts=N/SR/TB,volume={gain:.1f}dB,afade=t=in:d=0.6,"
                 f"afade=t=out:st={max(0, dur - 1.8):.2f}:d=1.8[m];"
                 "[m]equalizer=f=2500:t=q:w=1.2:g=-5,equalizer=f=1000:t=q:w=1:g=-3[meq];"   # make room for the voice
                 "[meq][key]sidechaincompress=threshold=0.03:ratio=2.5:attack=80:release=900[md];"  # gentle, no pumping
                 "[v][1][md]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
        log(f"[sound] music: {t['file']} from {t.get('start', 0)}s; {len(cl)} effects")
    else:
        graph = (f"[0]aresample={SR},aformat=channel_layouts=stereo[v];"
                 "[v][1]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
        log(f"[sound] no music folder (STORY_MUSIC_DIR); {len(cl)} effects")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-ar", str(SR), "-t", f"{dur:.2f}", str(out_wav)], check=True)
    return out_wav, cl, (t or {}).get("file")
