"""Sound for story videos: a music bed that ducks under the narrator, plus sound effects placed from the storyboard.

Benchmark (Ricks Clips, "Why the Second Draw Always Wins", measured 1 Nov 2026): the sound is never silent (a music
bed under the voice the whole time) and low "hits" / "whooshes" land every 2-5 s on the big visual moments.

    mix(board, timing, narration_wav, out_wav, music_dir=None, track=None, log=print) -> out_wav

Sound effects are GENERATED here (numpy only: shaped noise and tones), so they are free, unlimited and licence-free.
Music comes from the owner's private YouTube Audio Library folder (STORY_MUSIC_DIR); it is never committed, because
the library's terms don't allow redistributing the files. Without a music folder, the video gets effects only.
"""
import json, os, shutil, subprocess, zlib
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


def mix(board, timing, narration_wav, out_wav, music_dir=None, track=None, title="", log=print, cue_list=None):
    """Narration + ducked music + effects, loudness-matched for YouTube (-14 LUFS). Effects come from the storyboard,
    or from a ready cue_list [(time, kind, gain)] (the film style)."""
    out_wav, dur = Path(out_wav), float(timing["duration"])
    music_dir = music_dir or os.environ.get("STORY_MUSIC_DIR")
    cl = cue_list if cue_list is not None else cues(board, timing)
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


# ---------- film mix (studio/story/film.py) ----------
# Lessons from the owner's review of the 2D episodes: synthetic effects sounded fake, too many effects felt "placed
# everywhere", and audio-driven ducking pumped. So the film mix uses:
#   - a music bed whose level follows the WORD TIMING (not a compressor): steady under speech, a little up in real
#     pauses, smooth 0.4 s ramps, a short musical swell after the last word, then a long fade;
#   - only real recorded effects (sfx.json), at most ~1 every 3 s, and none if the files are missing;
#   - two-pass loudness normalisation (linear), so the whole mix is lifted evenly to -14 LUFS without pumping.
SFX_CATALOG = Path(__file__).parent / "sfx.json"
MOODS = {"tense": ("tense", "tension"), "mysterious": ("myster", "investigation"), "epic": ("epic", "history"),
         "curious": ("curious", "sneaky"), "sad": ("myster", "old times")}


def _decode(path, start=0.0, dur=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{start:.2f}", "-i", str(path)]
    if dur:
        cmd += ["-t", f"{dur:.2f}"]
    if af:
        cmd += ["-af", af]
    raw = subprocess.run(cmd + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def _rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def pick_film_track(title, music_dir, mood=None, avoid=()):
    """A track for the episode's mood, not one used by the channel's recent videos when there is a choice."""
    if not music_dir or not Path(music_dir).is_dir():
        return None
    cat = json.loads(MUSIC_CATALOG.read_text(encoding="utf-8"))
    usable = [t for t in cat["tracks"] if (Path(music_dir) / t["file"]).exists() and not t.get("skip")]
    if mood:
        keys = MOODS.get(mood, (mood,))
        usable = [t for t in usable if any(k in t["mood"] for k in keys)] or usable
    fresh = [t for t in usable if t["file"] not in set(avoid)]
    usable = fresh or usable
    return usable[zlib.crc32(title.encode()) % len(usable)] if usable else None


def speech_spans(timing, merge=0.55):
    """(start, end) of continuous speech: words closer than `merge` seconds count as one span."""
    spans = []
    for w in timing["words"]:
        if spans and w["start"] - spans[-1][1] < merge:
            spans[-1][1] = w["end"]
        else:
            spans.append([w["start"], w["end"]])
    return spans


def music_gain(timing, n, bed_db, open_db, outro_db, ramp=0.4):
    """Per-sample gain (linear) for the music: bed under speech, open in pauses, swell after the last word."""
    t = np.arange(n) / SR
    g = np.full(n, open_db, float)
    for a, b in speech_spans(timing):
        g[(t >= a - 0.15) & (t <= b + 0.1)] = bed_db
    last = timing["words"][-1]["end"] if timing["words"] else 0
    g[t > last + 0.25] = outro_db
    k = max(1, int(ramp * SR))   # smooth every change (moving average = ramps, no clicks, no pumping)
    c = np.cumsum(np.pad(g, (k, k), mode="edge")); g = (c[2 * k:2 * k + n] - c[:n]) / (2 * k)
    return 10 ** (g / 20)


def mix_film(timing, narration_wav, out_wav, cue_list, music_dir=None, mood=None, title="", avoid=(), outro=1.6,
             log=print):
    """Narration + music bed + real effects -> out_wav (length = narration + outro). Returns (out_wav, track_file)."""
    music_dir = music_dir or os.environ.get("STORY_MUSIC_DIR")
    dur = float(timing["duration"]) + outro
    n = int(dur * SR)
    voice = np.zeros((n, 2)); v = _decode(narration_wav)[:n]; voice[:len(v)] = v
    vdb = _rms_db(v[np.abs(v).max(1) > 0.01]) if len(v) else -20.0     # speech level (pauses excluded)
    out = voice.copy()
    track = pick_film_track(title, music_dir, mood, avoid)
    if track:
        m = _decode(Path(music_dir) / track["file"], float(track.get("start", 0)), dur + 0.5,
                    af="equalizer=f=2500:t=q:w=1.2:g=-4,equalizer=f=1000:t=q:w=1:g=-2,highpass=f=40")[:n]
        mm = np.zeros((n, 2)); mm[:len(m)] = m
        mm *= 10 ** ((vdb - _rms_db(mm[: int(20 * SR)])) / 20)        # music level matched to the voice first
        g = music_gain(timing, n, bed_db=-19, open_db=-15, outro_db=-8)   # benchmark: music ~16-20 dB under the voice
        fade_in, fade_out = int(0.5 * SR), int(min(outro + 0.6, dur) * SR)
        g[:fade_in] *= np.linspace(0, 1, fade_in) ** 2
        g[-fade_out:] *= np.linspace(1, 0, fade_out) ** 1.5
        out += mm * g[:, None]
        log(f"[sound] music: {track['file']} from {track.get('start', 0)}s (bed 19 dB under the voice)")
    else:
        log("[sound] no music folder (STORY_MUSIC_DIR): narration only")
    fx = json.loads(SFX_CATALOG.read_text(encoding="utf-8"))["effects"] if SFX_CATALOG.exists() else {}
    used = 0
    for t, kind, _g in cue_list:
        spec = fx.get({"impact": "hit", "riser": "swell"}.get(kind, kind))
        f = Path(music_dir or "") / spec["file"] if spec else None
        if not f or not f.exists():
            continue
        af = f"lowpass=f={spec['lowpass']}" if spec.get("lowpass") else None
        s = _decode(f, af=af)
        if spec.get("reverse"):
            s = s[::-1]
            s = s[-int(1.6 * SR):]           # the swell's last 1.6 s, ending on the cut
        s = s * 10 ** ((vdb + spec["gain_db"] - _rms_db(s[np.abs(s).max(1) > 0.003])) / 20)
        env = np.convolve(np.abs(s).max(1), np.ones(480) / 480, mode="same")
        peak = int(np.argmax(env)) if not spec.get("reverse") else len(s)
        a = int(t * SR) - peak            # the loudest moment of the sound lands exactly on the cue
        if a < 0:
            s, a = s[-a:], 0
        b = min(n, a + len(s))
        tail = np.ones(b - a); tail[-min(len(tail), 2400):] = np.linspace(1, 0, min(len(tail), 2400))
        out[a:b] += s[:b - a] * tail[:, None]
        used += 1
    log(f"[sound] {used} real effects" + ("" if fx else " (no sfx.json)"))
    tmp = Path(out_wav).with_name("premix.wav")
    _write_wav(tmp, out / max(1.0, np.abs(out).max() / 0.95))
    # two-pass loudness: measure, then apply one linear gain (no pumping)
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(meas[meas.rfind("{"): meas.rfind("}") + 1])
    if "inf" in str(js.get("input_i")):   # silence (tests): nothing to normalise
        shutil.move(str(tmp), str(out_wav))
        return out_wav, (track or {}).get("file")
    lin = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
           f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-af", lin, "-ar", str(SR), str(out_wav)], check=True)
    tmp.unlink(missing_ok=True)
    return out_wav, (track or {}).get("file")
