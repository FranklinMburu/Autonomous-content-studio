"""Lab: render one of our own test streams (see streams.py) as a real-looking VOD + chat log + viewer clips.

    ACS_CACHE=<folder with models/kokoro-v1.0.onnx> python lab/clips/make_stream.py neon_dash out/lab_streams

Writes <out>/<name>/: stream.mp4 (1280x720, 30 fps), chat.json (TwitchDownloader format), clips.json (viewer clips),
words.json (the transcript with word times, as Whisper would give it), rights.json (our own work), and truth.json
(where the moments really are: used ONLY to score the moment finder, never read by the engine).
Deterministic: same name -> same stream.
"""
import json, math, random, subprocess, sys
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from streams import STREAMS  # noqa: E402

W, H, FPS, SR = 1280, 720, 30, 24000
FONT = next((str(p) for p in [ROOT / "assets/fonts/Inter-Bold.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")] if p.exists()), None)


def font(size):
    return ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()


def plan_lines(cfg):
    """Filler and moments interleaved, with the long dull stretches a real stream has."""
    rnd = random.Random(cfg["seed"])
    out, filler = [], list(cfg["filler"])
    speakers = list(cfg["voices"])

    def fill(seconds):
        t = 0.0
        while t < seconds:
            f = filler[rnd.randrange(len(filler))]
            spk, text = (f if isinstance(f, tuple) else (speakers[0], f))
            out.append({"speaker": spk, "text": text, "energy": round(rnd.uniform(0.3, 0.45), 2), "event": None,
                        "gap": round(rnd.uniform(1.2, 4.0), 2), "moment": None})
            t += len(text.split()) / 2.6 + out[-1]["gap"]
    fill(rnd.uniform(40, 60))
    for mi, (kind, lines) in enumerate(cfg["moments"]):
        for spk, text, en, ev in lines:
            out.append({"speaker": spk, "text": text, "energy": en, "event": ev, "gap": 0.3, "moment": mi})
        out[-1]["gap"] = 1.5
        fill(rnd.uniform(*cfg["gap_s"]))
    return out


def speak(lines, cfg, voice_mod):
    k = voice_mod.engine()
    chunks, t, words = [], 0.5, []
    chunks.append(np.zeros(int(0.5 * SR), np.float32))
    for i, ln in enumerate(lines):
        v, sp = cfg["voices"][ln["speaker"]]
        speed = sp * (1 + 0.14 * (ln["energy"] - 0.5))
        say = " ".join(voice_mod.spoken(w) for w in ln["text"].split())
        audio, sr, tim = k.create_timed(say, voice=v, speed=speed, lang="en-us")
        loud = np.where(np.abs(audio) > 0.01)[0]
        if len(loud):
            audio = audio[:loud[-1] + int(0.08 * SR)]
        audio = audio * (0.45 + 0.55 * ln["energy"])
        dur = len(audio) / SR
        wt, _ = voice_mod._word_times(k, ln["text"].split(), tim, t, dur)
        ln["start"], ln["end"] = round(t, 3), round(t + dur, 3)
        for w, s, e in wt:
            words.append({"w": w, "start": round(s, 3), "end": round(e, 3), "speaker": ln["speaker"]})
        chunks.append(audio.astype(np.float32))
        t += dur
        chunks.append(np.zeros(int(ln["gap"] * SR), np.float32))
        t += ln["gap"]
        if i % 20 == 0:
            print(f"  voice {i}/{len(lines)} t={t:.0f}s", flush=True)
    chunks.append(np.zeros(int(3 * SR), np.float32))
    return np.concatenate(chunks), words, t + 3


def events_of(lines):
    ev = []
    for ln in lines:
        e = ln["event"]
        if not e:
            continue
        if e.startswith("donation:"):
            _, who, amt, msg = e.split(":", 3)
            ev.append({"t": ln["start"] - 1.0, "type": "donation", "who": who, "amount": amt, "msg": msg})
        else:
            ev.append({"t": ln["start"] - (0.6 if e in ("fail", "clutch") else 0), "type": e})
    return ev


def sfx_and_music(total, events, kind, seed):
    rnd = np.random.default_rng(seed)
    n = int(total * SR)
    out = np.zeros(n, np.float32)
    tt = np.arange(n) / SR
    if kind == "gaming":   # a quiet chiptune-ish bed: two square-ish voices on a 120 BPM grid
        notes = [220, 262, 330, 392, 330, 262, 294, 349]
        beat = 0.5
        idx = (tt // beat).astype(int) % len(notes)
        f = np.array(notes)[idx]
        ph = np.cumsum(f / SR) * 2 * np.pi
        env = np.exp(-((tt % beat) / 0.18))
        out += 0.035 * np.tanh(3 * np.sin(ph)) * env
        out += 0.02 * np.sin(np.cumsum(np.array(notes)[(idx // 2) % len(notes)] / 2 / SR) * 2 * np.pi)
    else:                  # room tone
        out += 0.002 * rnd.standard_normal(n).astype(np.float32)
    for e in events:
        s = int(max(0, e["t"]) * SR)
        if e["type"] == "fail":
            m = int(1.2 * SR); x = np.arange(m) / SR
            snd = 0.35 * rnd.standard_normal(m) * np.exp(-x * 3) + 0.25 * np.sin(2 * np.pi * (180 - 80 * x) * x) * np.exp(-x * 2)
        elif e["type"] == "clutch":
            m = int(1.5 * SR); x = np.arange(m) / SR
            snd = sum(0.12 * np.sin(2 * np.pi * f0 * x) * np.exp(-x * 2.5) for f0 in (523, 659, 784, 1047))
        elif e["type"] == "donation":
            m = int(0.8 * SR); x = np.arange(m) / SR
            snd = 0.2 * np.sin(2 * np.pi * 880 * x) * np.exp(-x * 5) + 0.15 * np.sin(2 * np.pi * 1320 * x) * np.exp(-x * 6)
        else:
            continue
        e2 = min(n, s + len(snd))
        out[s:e2] += snd[: e2 - s].astype(np.float32)
    return out


def chat(lines, events, total, cfg):
    """A live chat: steady chatter, then bursts of short emote-heavy messages a few seconds after a real moment.
    Plus one decoy burst that is NOT a moment (a giveaway command spam) to keep the finder honest."""
    rnd = random.Random(cfg["seed"] * 31)
    names = [f"{a}{b}" for a in ("nova", "kekw_", "pix", "lowkey", "zz", "mango", "turbo", "sleepy", "ghost", "raven")
             for b in ("", "77", "_tv", "x", "99", "lol")]
    normal = ["lol", "hi chat", "what game is this", "W stream", "first time here", "how long is stream today",
              "the music slaps", "you got this", "lmao", "bro", "this level looks hard", "what rank are you",
              "hello from Kenya", "gg", "can you say hi to me", "are you going to beat it", "nice", "true",
              "I have school tomorrow", "chat is slow today"]
    hype = {"fail": ["LMAOOO", "KEKW", "KEKW KEKW", "L", "OMEGALUL", "NOOOO", "he pressed it trust", "LUL", "unlucky", "L L L"],
            "clutch": ["NO WAY", "POG", "PogChamp", "CLIP IT", "W", "WWWW", "insane", "CLIP THAT", "GOAT", "POGGERS"],
            "funny": ["KEKW", "LMAO", "Mike LMAO", "OMEGALUL", "lmaooo", "MIKE", "KEKW KEKW"],
            "story": ["awww", "mom W", "soup W", "<3", "wholesome", "mom is goated", "W mom"],
            "reveal": ["LMAOOOO", "KEKW", "MIKE WAS RIGHT", "3 WEEKS", "OMEGALUL", "no shot", "LMAO"],
            "argument": ["LMAO", "KEKW", "its a sandwich", "NOT A SANDWICH", "Dev is right", "Maya W", "OMEGALUL"],
            "shock": ["NOOO", "LMAOOO", "ENCORE", "KEKW", "no way", "the boss W", "OMEGALUL"],
            "wholesome": ["<3", "crying", "W", "this is so sweet", "awww", "<3 <3"]}
    msgs = []
    t = 0.0
    while t < total:
        t += rnd.expovariate(cfg["chat_rate"])
        msgs.append((t, rnd.choice(names), rnd.choice(normal)))
    kinds = [k for k, _ in cfg["moments"]]
    for ln in lines:
        if ln["moment"] is not None and ln["energy"] >= 0.85:
            k = kinds[ln["moment"]]
            t0 = ln["start"] + rnd.uniform(2.0, 4.5)    # stream delay + reaction time
            t = t0
            while t < t0 + rnd.uniform(9, 15):
                t += rnd.expovariate(rnd.uniform(6, 11))
                msgs.append((t, rnd.choice(names), rnd.choice(hype[k])))
    decoy = total * 0.47        # giveaway spam: lots of messages, all the same command, nothing happening on stream
    t = decoy
    while t < decoy + 25:
        t += rnd.expovariate(9)
        msgs.append((t, rnd.choice(names), "!enter"))
    msgs.sort()
    return {"source": "TwitchDownloader-compatible (own test stream)",
            "comments": [{"content_offset_seconds": round(a, 2), "commenter": {"display_name": n}, "message": {"body": b}}
                         for a, n, b in msgs if a < total]}


def draw_avatar(d, cx, cy, s, mouth, energy, blink, hue):
    skin = (236, 188, 150) if hue == 0 else (198, 140, 105)
    d.ellipse([cx - s, cy - s * 1.1, cx + s, cy + s * 1.1], fill=skin)
    hair = [(40, 30, 30), (90, 40, 140), (20, 20, 20)][hue % 3]
    d.chord([cx - s * 1.05, cy - s * 1.25, cx + s * 1.05, cy + s * 0.2], 180, 360, fill=hair)
    eo = s * 0.36
    ey = cy - s * 0.05
    er = s * (0.11 + 0.07 * max(0, energy - 0.6))
    for sx in (-1, 1):
        if blink:
            d.line([cx + sx * eo - er, ey, cx + sx * eo + er, ey], fill=(30, 30, 30), width=max(2, int(s * 0.05)))
        else:
            d.ellipse([cx + sx * eo - er, ey - er, cx + sx * eo + er, ey + er], fill=(255, 255, 255))
            d.ellipse([cx + sx * eo - er * 0.5, ey - er * 0.5, cx + sx * eo + er * 0.5, ey + er * 0.5], fill=(30, 30, 30))
        by = ey - s * (0.25 + 0.15 * max(0, energy - 0.5))
        d.line([cx + sx * eo - er * 1.2, by + sx * 0, cx + sx * eo + er * 1.2, by - s * 0.03 * sx * (energy > 0.9)],
               fill=hair, width=max(3, int(s * 0.07)))
    mw = s * (0.28 + 0.15 * energy)
    mh = s * (0.04 + 0.45 * mouth)
    d.ellipse([cx - mw, cy + s * 0.45 - mh / 2, cx + mw, cy + s * 0.45 + mh / 2], fill=(110, 30, 40))


def render(name, out):
    cfg = STREAMS[name]
    d = Path(out) / name
    d.mkdir(parents=True, exist_ok=True)
    from studio import voice as V
    lines = plan_lines(cfg)
    print(f"[{name}] {len(lines)} lines; voicing", flush=True)
    speech, words, total = speak(lines, cfg, V)
    events = events_of(lines)
    bed = sfx_and_music(total, events, cfg["kind"], cfg["seed"])
    mix = bed[: len(speech)] if len(bed) >= len(speech) else np.pad(bed, (0, len(speech) - len(bed)))
    mix = mix + speech
    mix = np.clip(mix, -1, 1)
    sf.write(str(d / "audio.wav"), mix, SR)
    # per-frame mouth opening per speaker from the speech envelope of their own lines
    nfr = int(total * FPS)
    env = {s: np.zeros(nfr) for s in cfg["voices"]}
    hop = SR // FPS
    for ln in lines:
        a, b = int(ln["start"] * FPS), int(ln["end"] * FPS)
        seg = speech[int(ln["start"] * SR): int(ln["end"] * SR)]
        for f in range(a, min(b, nfr)):
            x = seg[(f - a) * hop:(f - a + 1) * hop]
            env[ln["speaker"]][f] = min(1.0, float(np.sqrt((x ** 2).mean() + 1e-9)) * 9) if len(x) else 0
    en = {s: np.full(nfr, 0.35) for s in cfg["voices"]}
    for ln in lines:
        en[ln["speaker"]][int(ln["start"] * FPS):int(ln["end"] * FPS) + 15] = ln["energy"]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(d / "audio.wav"), "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest",
                           str(d / "stream.mp4")], stdin=subprocess.PIPE)
    f_big, f_mid, f_small = font(64), font(30), font(22)
    rnd = random.Random(cfg["seed"])
    obstacles = [(i * 2.3 + rnd.uniform(0, 1.2), rnd.choice([60, 90, 120])) for i in range(int(total / 2.3) + 5)]
    for fi in range(nfr):
        t = fi / FPS
        im = Image.new("RGB", (W, H))
        dr = ImageDraw.Draw(im)
        recent = [e for e in events if 0 <= t - e["t"] < 6]
        if cfg["kind"] == "gaming":
            for y in range(0, H, 8):   # sky gradient
                c = int(20 + 40 * y / H)
                dr.rectangle([0, y, W, y + 8], fill=(c // 2, 10, c + 30))
            off = (t * 320) % 80
            for x in range(-80, W + 80, 80):
                dr.line([x - off, 520, x - off - 200, H], fill=(255, 0, 200), width=2)
            for k, y in enumerate([520, 560, 610, 670]):
                dr.line([0, y, W, y], fill=(255, 0, 200), width=2)
            for ot, oh in obstacles:   # obstacles scroll past the player at x=300
                x = 300 + (ot - t) * 320
                if -60 < x < W + 60:
                    dr.rectangle([x, 520 - oh, x + 40, 520], fill=(0, 255, 230), outline=(255, 255, 255))
            jump = abs(math.sin(t * math.pi / 1.15)) * 150
            shake = 0
            fail = [e for e in recent if e["type"] == "fail"]
            clutch = [e for e in recent if e["type"] == "clutch"]
            if fail:
                k = t - fail[0]["t"]
                shake = int(18 * math.exp(-k * 3) * math.sin(k * 60))
                jump = max(0, 150 - k * 400) if k < 0.4 else 0
            if clutch:
                k = t - clutch[0]["t"]
                jump = 260 * math.sin(min(1, k / 1.1) * math.pi) if k < 1.1 else 0
            dr.rectangle([280 + shake, 470 - jump, 330 + shake, 520 - jump], fill=(255, 220, 0), outline=(255, 255, 255), width=3)
            score = int(t * 37)
            dr.text((30, 24), f"SCORE {score:,}", font=f_mid, fill=(255, 255, 255))
            dr.text((30, 60), "LEVEL 9" if t > total * 0.15 else "LEVEL 6", font=f_small, fill=(200, 200, 255))
            if fail:
                k = t - fail[0]["t"]
                if k < 0.25:
                    dr.rectangle([0, 0, W, H], fill=(200, 0, 0))
                if 0.3 < k < 4:
                    dr.text((W // 2 - 230, 220), "LEVEL FAILED", font=f_big, fill=(255, 60, 60))
            if clutch:
                k = t - clutch[0]["t"]
                if 1.0 < k < 4.5:
                    dr.text((W // 2 - 160, 200), "PERFECT!", font=f_big, fill=(255, 215, 0))
                    for p in range(40):
                        a = p * 0.9 + k
                        dr.ellipse([W // 2 + math.cos(a) * k * 160 - 5, 260 + math.sin(a) * k * 110 - 5,
                                    W // 2 + math.cos(a) * k * 160 + 5, 260 + math.sin(a) * k * 110 + 5], fill=(255, 215, 0))
            # facecam, bottom right, like most game streams
            cx0, cy0, cw, ch = 900, 440, 360, 260
            dr.rectangle([cx0 - 4, cy0 - 4, cx0 + cw + 4, cy0 + ch + 4], fill=(120, 0, 255))
            dr.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=(55, 60, 80))
            dr.rectangle([cx0 + 20, cy0 + 20, cx0 + 90, cy0 + 110], fill=(240, 200, 120))
            e = en["zed"][fi]
            draw_avatar(dr, cx0 + cw // 2, cy0 + ch // 2 + 25 + int(3 * math.sin(t * 2)), 82, env["zed"][fi], e,
                        (fi % 130) < 4, 0)
        else:
            dr.rectangle([0, 0, W, H], fill=(36, 28, 44))
            dr.rectangle([0, 470, W, H], fill=(70, 40, 60))
            dr.rounded_rectangle([90, 400, W - 90, 640], 40, fill=(150, 70, 60))
            dr.ellipse([W // 2 - 40, 120, W // 2 + 40, 200], fill=(255, 220, 140))
            dr.text((W // 2 - 140, 30), "LATE NIGHT COUCH", font=f_mid, fill=(255, 200, 120))
            for spk, x, hue in (("maya", 360, 1), ("dev", 920, 2)):
                e = en[spk][fi]
                draw_avatar(dr, x, 330 + int(2 * math.sin(t * 1.7 + x)), 110, env[spk][fi], e, ((fi + x) % 150) < 4, hue)
                dr.rectangle([x - 90, 600, x + 90, 640], fill=(0, 0, 0))
                dr.text((x - 40, 605), spk.upper(), font=f_small, fill=(255, 255, 255))
        for e in recent:
            if e["type"] == "donation":
                dr.rounded_rectangle([340, 90, 940, 190], 18, fill=(255, 255, 255))
                dr.text((370, 105), f"{e['who']} donated {e['amount']}!", font=f_mid, fill=(120, 0, 255))
                dr.text((370, 148), e["msg"], font=f_small, fill=(30, 30, 30))
        dr.ellipse([W - 120, 20, W - 104, 36], fill=(255, 0, 0))
        dr.text((W - 98, 14), "LIVE", font=f_small, fill=(255, 255, 255))
        ff.stdin.write(im.tobytes())
        if fi % 3000 == 0:
            print(f"  frame {fi}/{nfr}", flush=True)
    ff.stdin.close()
    ff.wait()
    (d / "audio.wav").unlink()
    json.dump({"words": words, "source": "Kokoro ground truth (stands in for Whisper in the lab)"}, open(d / "words.json", "w"), indent=0)
    json.dump(chat(lines, events, total, cfg), open(d / "chat.json", "w"), indent=0)
    moments = []
    for mi, (kind, _) in enumerate(cfg["moments"]):
        ls = [ln for ln in lines if ln["moment"] == mi]
        moments.append({"kind": kind, "start": ls[0]["start"], "end": ls[-1]["end"]})
    rnd = random.Random(cfg["seed"] + 5)
    vclips = [{"vod_offset": round(m["start"] + rnd.uniform(-5, 5), 1), "duration": 30, "views": rnd.randint(40, 900),
               "title": f"clip {i}"} for i, m in enumerate(moments) if i in (0, 2)]
    vclips.append({"vod_offset": round(total * 0.3, 1), "duration": 30, "views": 3, "title": "test"})
    json.dump({"clips": vclips}, open(d / "clips.json", "w"), indent=1)
    json.dump({"source": "own", "owner": "Autonomous Content Studio (lab)", "licence": "own work, made by the studio",
               "permission": "we made it", "proof": "lab/clips/make_stream.py + lab/clips/streams.py",
               "platform": "local", "title": cfg["title"]}, open(d / "rights.json", "w"), indent=1)
    json.dump({"moments": moments, "duration": total}, open(d / "truth.json", "w"), indent=1)
    print(f"[{name}] done: {total / 60:.1f} min, {len(words)} words", flush=True)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "out" / "lab_streams"))
