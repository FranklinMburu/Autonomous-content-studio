"""Original music bed + UI sound effects, synthesised in code (no samples, no licences, $0). Deterministic: the noise
generator is seeded from the episode seed. Arrangement follows the plan (sections from web/engine.html):
pad from the start; kick + sub bass from the first stat; hats and the pluck arpeggio from the story; a breakdown with a
riser during a leak; an impact on the wall stat; calmer for the call to action; a held chord to end.
Lab history: the first library track was rejected ("trash"); this bed was accepted in v2/v3 (11 Nov 2026)."""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
KEYS = {"Am": 0, "Cm": 3, "Dm": -7, "Em": -5}
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]      # i - VI - III - VII in A minor
ROOTS = [45, 41, 36, 43]


def _f(kind, x, f):
    return sosfilt(butter(2, f, kind, fs=SR, output="sos"), x)


def _reverb(x, rng, secs=1.2, wet=0.25):
    n = int(secs * SR)
    ir = [_f("low", rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n)), 6000) / np.sqrt(n) * 6 for _ in range(2)]
    if x.ndim == 1: x = np.stack([x, x], 1)
    y = np.stack([fftconvolve(x[:, c], ir[c])[:len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet


def _place(buf, snd, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0: return
    if snd.ndim == 1: snd = np.stack([snd * (1 - max(0, pan)), snd * (1 + min(0, pan))], 1)
    j = min(len(buf), i + len(snd)); buf[i:j] += snd[:j - i] * gain


def _note(m): return 440.0 * 2 ** ((m - 69) / 12)


def _saw(f, n, det=0.0):
    t = np.arange(n) / SR
    return sum(2 * ((f * (1 + d) * t) % 1.0) - 1 for d in (-det, 0, det)) / 3


def music(sections, duration, cfg, seed):
    rng = np.random.default_rng(seed)
    kit = cfg.get("kit", "synth")     # the instruments follow the look: synth (the original), keys, mallet, bright
    dur = duration + 1.2; N = int(dur * SR)
    B = 60 / cfg["bpm"]; BAR = 4 * B; off = KEYS.get(cfg["key"], 0)
    ch = [[m + off for m in c] for c in CHORDS]; roots = [r + off for r in ROOTS]
    g0, k0 = sections["groove_from"], sections["kick_from"]
    br0, br1 = sections.get("break_from"), sections.get("break_to")
    calm, end = sections["calm_from"], sections["end_from"]
    inbreak = lambda t: br0 is not None and br0 <= t < br1  # noqa: E731
    out = np.zeros((N, 2))
    for b in range(int(dur / BAR) + 1):        # pad, one chord per bar
        t0 = b * BAR; n = int(BAR * SR * 1.15)
        if kit == "keys":       # soft electric piano pad: sines with a little second harmonic
            tt = np.arange(n) / SR; x = sum(np.sin(2 * np.pi * _note(m) * tt) + 0.25 * np.sin(4 * np.pi * _note(m) * tt) for m in ch[b % 4]) / 3
        else:
            x = sum(_saw(_note(m), n, 0.004) for m in ch[b % 4]) / 3
        _place(out, _f("low", x, (2600 if kit == "bright" else 700 if kit == "mallet" else 1400) if t0 > g0 else 900) * np.interp(np.arange(n), [0, .5 * SR, BAR * .6 * SR, n], [0, 1, .7, .7]) * 0.22, t0)
    sub = np.zeros(N)
    for b in range(int(dur / BAR) + 1):        # sub bass from the first stat
        t0 = b * BAR
        if t0 + BAR < k0 - 0.5: continue
        n = int(BAR * SR); i = int(t0 * SR); m = max(0, min(n, N - i))
        sub[i:i + m] += np.sin(2 * np.pi * _note(roots[b % 4]) * np.arange(n) / SR)[:m] * 0.5
    pump = np.ones(N)
    for k in range(int(dur / B) + 1):
        i = int(k * B * SR); n = int(B * SR)
        if i >= N: break
        pump[i:i + n] = (1 - 0.75 * np.exp(-np.linspace(0, 1, n) * 9))[:N - i]
    out[:, 0] += sub * pump * 0.3; out[:, 1] += sub * pump * 0.3
    out *= np.stack([pump * 0.6 + 0.4] * 2, 1)
    tk = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(62 + 90 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 9) + 0.15 * _f("high", rng.standard_normal(len(tk)), 3000) * np.exp(-tk * 200)
    th = np.arange(int(0.06 * SR)) / SR; hat = _f("high", rng.standard_normal(len(th)), 7000) * np.exp(-th * 70)
    plucks, drums, arp = {}, np.zeros((N, 2)), np.zeros((N, 2))
    for k in range(int(dur / B * 4) + 1):
        t = k * B / 4
        if t >= dur - 0.5: break
        bar, full = int(t / BAR), (g0 - 0.3 <= t < calm) and not inbreak(t)
        if k % 4 == 0 and k0 - 0.2 <= t < calm and not inbreak(t): _place(drums, kick, t, 0.45)
        if k % 2 == 1 and full and not (kit == "keys" and k % 4 == 1): _place(drums, hat, t, 0.10 + 0.05 * (k % 4 == 2), pan=0.3)
        if g0 - 0.3 <= t < end + 1.2 and not inbreak(t):
            m = ch[bar % 4][[0, 1, 2, 1][k % 4]] + 12 + (12 if k % 8 >= 6 else 0)
            if m not in plucks:
                n = int(0.45 * SR); tt = np.arange(n) / SR
                if kit == "mallet":    # marimba-like: sine + 4x partial, fast decay
                    plucks[m] = (np.sin(2 * np.pi * _note(m) * tt) + 0.35 * np.sin(2 * np.pi * _note(m) * 4 * tt) * np.exp(-tt * 30)) * np.exp(-tt * 12)
                elif kit == "keys":    # bell-like FM tone
                    plucks[m] = np.sin(2 * np.pi * _note(m) * tt + 1.5 * np.exp(-tt * 6) * np.sin(2 * np.pi * _note(m) * 3.5 * tt)) * np.exp(-tt * 7) * 0.8
                else:
                    plucks[m] = _f("low", _saw(_note(m), n, 0.002) * 0.6 + np.sin(2 * np.pi * _note(m) * 2 * tt) * 0.2, 4800 if kit == "bright" else 3200) * np.exp(-tt * 9)
            _place(arp, plucks[m], t, 0.16 if t < calm else 0.12, pan=-0.25 if k % 2 else 0.25)
    if br0 is not None:                        # tension riser through the breakdown
        n = int(max(0.3, br1 - br0) * SR); r = np.linspace(0, 1, n) ** 2
        _place(out, _f("band", rng.standard_normal(n), [400, 6000]) * r * 0.25 + np.sin(2 * np.pi * np.cumsum(np.linspace(110, 440, n)) / SR) * r * 0.12, br0)
    d = int(B * 0.75 * SR); a2 = arp.copy(); a2[d:] += arp[:-d] * 0.35; a2[2 * d:] += arp[:-2 * d] * 0.15
    out += drums + a2[:, ::-1] * 0.9
    out = _reverb(out, rng, 1.6, 0.22)
    e = int((dur - 1.4) * SR); out[e:] *= np.linspace(1, 0, N - e)[:, None]
    out[:int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))[:, None]
    return out / (np.abs(out).max() + 1e-9) * 0.9


def effects(cues, duration, seed):
    rng = np.random.default_rng(seed + 1)
    N = int((duration + 1.2) * SR)
    def env_noise(n, lo, hi): return _f("band", rng.standard_normal(n), [lo, hi])
    def t_(s): return np.arange(int(s * SR)) / SR
    def pop(): t = t_(0.09); return np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t * 18) + 380) / SR) * np.exp(-t * 45) * 0.7
    def tick(): t = t_(0.02); return (np.sin(2 * np.pi * 2400 * t) * 0.6 + _f("high", rng.standard_normal(len(t)), 4000) * 0.3) * np.exp(-t * 300)
    def click(): t = t_(0.03); return (np.sin(2 * np.pi * 1500 * t) * 0.7 + env_noise(len(t), 2000, 8000) * 0.4) * np.exp(-t * 180)
    def key(): t = t_(0.035); f = rng.uniform(0.85, 1.15); return (env_noise(len(t), 1500 * f, 6000) * 0.6 + np.sin(2 * np.pi * 180 * f * t) * 0.4) * np.exp(-t * 140)
    def whoosh(sec=0.5):
        n = int(sec * SR); x = rng.standard_normal(n); e = np.sin(np.linspace(0, np.pi, n)) ** 2; m = np.linspace(0, 1, n)
        y = (_f("low", x, 1200) * (1 - m) + env_noise(n, 1500, 7000) * m) * e * 0.8
        return np.stack([y * (1 - m), y * m], 1) * 1.4
    def zip_(): t = t_(0.28); return (np.sin(2 * np.pi * np.cumsum(np.linspace(300, 1900, len(t))) / SR) * 0.35 + env_noise(len(t), 2000, 8000) * 0.25) * np.sin(np.linspace(0, np.pi, len(t)))
    def blip(): t = t_(0.16); return np.sin(2 * np.pi * np.where(t < 0.07, 660, 990) * t) * np.exp(-(t % 0.07) * 25) * 0.5
    def thump():
        t = t_(0.35); x = np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-t * 25)) / SR) * np.exp(-t * 10); c = click(); x[:len(c)] += c * 0.5; return x
    def ding(): t = t_(1.4); return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in [(1318, .5, 3.5), (1976, .25, 5), (2637, .12, 7), (659, .15, 3)])
    def riser(): t = t_(1.2); m = t / t[-1]; return (env_noise(len(t), 800, 9000) * 0.5 + np.sin(2 * np.pi * np.cumsum(200 + 900 * m ** 2) / SR) * 0.2) * m ** 2.5
    def impact():
        t = t_(1.6); x = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-t * 18)) / SR) * np.exp(-t * 3.2) + _f("low", rng.standard_normal(len(t)), 3000) * np.exp(-t * 14) * 0.6
        return _reverb(x, rng, 1.4, 0.35)
    def slam():
        t = t_(0.6); x = np.sin(2 * np.pi * np.cumsum(90 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 9) + env_noise(len(t), 300, 5000) * np.exp(-t * 40) * 0.7
        return _reverb(x, rng, 0.8, 0.25)
    make = {"pop": pop, "tick": tick, "click": click, "key": key, "whoosh": lambda: whoosh(0.5), "swoosh_big": lambda: whoosh(0.85),
            "zip": zip_, "blip": blip, "thump": thump, "ding": ding, "riser": riser, "impact": impact, "slam": slam}
    level = {"pop": .35, "tick": .18, "click": .3, "key": .22, "whoosh": .32, "swoosh_big": .42, "zip": .3, "blip": .3, "thump": .5,
             "ding": .22, "riser": .35, "impact": .7, "slam": .6}
    out = np.zeros((N, 2))
    for c in cues:
        if c["kind"] not in make: continue
        s = make[c["kind"]]()
        _place(out, s, c["t"], level[c["kind"]] * c.get("gain", 1), pan=float(rng.uniform(-0.3, 0.3)) if s.ndim == 1 else 0)
    out = _reverb(out, rng, 0.7, 0.12)
    return out / (np.abs(out).max() + 1e-9) * 0.9


def make(info, cfg, seed, music_path, sfx_path):
    sf.write(str(music_path), music(info["sections"], info["duration"], cfg, seed).astype(np.float32), SR)
    sf.write(str(sfx_path), effects(info["cues"], info["duration"], seed).astype(np.float32), SR)


MIX = ("[1:a]aresample=48000,acompressor=threshold=0.15:ratio=2:attack=8:release=150,pan=stereo|c0=c0|c1=c0,asplit=2[v][vk];"
       "[2:a]highpass=f=40,equalizer=f=50:t=q:w=1:g=-6,volume=-15dB[m0];[m0][vk]sidechaincompress=threshold=0.04:ratio=4:attack=15:release=300[m];"
       "[3:a]highpass=f=40,volume=-9dB[s];[v][m][s]amix=inputs=3:duration=first:normalize=0,loudnorm=I={lufs}:TP=-1:LRA=7[a]")


def mix(video, voice, music_path, sfx_path, out, lufs=-14):
    """Voice on top, music ducked under the voice, effects under both, -14 LUFS (the reference measured -14.1)."""
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(voice), "-i", str(music_path), "-i", str(sfx_path),
                    "-filter_complex", MIX.format(lufs=lufs), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    str(out)], check=True)
