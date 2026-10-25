"""Stage: visuals + captions + encode. script + narration + timing -> video.mp4 (1080x1920, 30 fps)."""
import math, re, subprocess
import cairo
from . import draw
from .draw import W, H, FPS, CAPTION_Y, Style, pick_style, appear, back, text, set_font, ease
from .scenes import SCENES, decorations


def _norm(w):
    return re.sub(r"[^a-z0-9']", "", str(w).lower())


class Timeline:
    def __init__(self, script, timing):
        self.script, self.duration = script, timing["duration"]
        self.words, self.lines = timing["words"], timing["lines"]
        nb = len(script["beats"])
        self.beats = []
        for bi in range(nb):
            ls = [l for l in self.lines if l["beat"] == bi]
            self.beats.append({"i": bi, "speech_start": ls[0]["start"], "speech_end": ls[-1]["end"]})
        for bi, b in enumerate(self.beats):
            b["start"] = 0.0 if bi == 0 else b["speech_start"] - .25   # cut just before the words
        for bi, b in enumerate(self.beats):
            b["end"] = self.beats[bi + 1]["start"] if bi + 1 < nb else self.duration

    def beat_at(self, t):
        for b in self.beats:
            if b["start"] <= t < b["end"]:
                return b
        return self.beats[-1]

    def keyfn(self, b):
        """K(word, frac): seconds into beat `b` when `word` is first spoken; else frac of the beat."""
        ws = [w for w in self.words if w["beat"] == b["i"]]
        dur = b["end"] - b["start"]
        def K(word, frac=0.5):
            if isinstance(word, (int, float)) and not isinstance(word, bool):
                return float(word)
            if word:
                key = _norm(str(word).split()[0])
                for w in ws:
                    if _norm(w["w"]) == key or (len(key) > 3 and _norm(w["w"]).startswith(key)):
                        # never so late that the viewer barely sees it
                        return min(w["start"] - b["start"], .8 * dur)
            return (frac if frac is not None else .5) * dur
        K.dur = dur
        return K


def caption_chunks(words):
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        nxt_line = i + 1 < len(words) and words[i + 1]["line"] != w["line"]
        if (len(cur) >= 4 or sum(len(words[j]["w"]) for j in cur) > 17 or w["w"][-1] in ",.?!"
                or nxt_line or i == len(words) - 1):
            chunks.append(cur); cur = []
    out = []
    for k, ch in enumerate(chunks):
        s = words[ch[0]]["start"]; e = words[ch[-1]]["end"]
        if k + 1 < len(chunks):
            e = max(e, min(words[chunks[k + 1][0]]["start"], e + .35))
        out.append((ch, s, e))
    return out


def draw_captions(ctx, t, words, chunks, S):
    for ch, s, e in chunks:
        if s - .05 <= t < e:
            ws = [words[j] for j in ch]
            size = 78
            set_font(ctx, size)
            space = ctx.text_extents(" ").x_advance
            widths = [ctx.text_extents(w["w"]).x_advance for w in ws]
            total = sum(widths) + space * (len(ws) - 1)
            scale = min(1, 960 / total)
            p = back((t - s) / .18)
            ctx.save(); ctx.translate(W / 2, CAPTION_Y); ctx.scale(scale * (.9 + .1 * p), scale * (.9 + .1 * p))
            x = -total / 2
            for w, wd in zip(ws, widths):
                active = w["start"] <= t < w["end"] + .04
                text(ctx, w["w"], x, 0, size, S.accent if active else S.text, align="left", stroke=14)
                x += wd + space
            ctx.restore()
            return


class Renderer:
    def __init__(self, script, timing):
        draw_pal, draw_bg = pick_style(script)
        self.S = Style(draw_pal, draw_bg)
        self.script, self.T = script, Timeline(script, timing)
        self.chunks = caption_chunks(self.T.words)
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ctx = cairo.Context(self.surf)
        self.ctx.set_antialias(cairo.ANTIALIAS_BEST)
        self.keys = [self.T.keyfn(b) for b in self.T.beats]

    def frame(self, t):
        ctx, S = self.ctx, self.S
        ctx.new_path(); ctx.save()
        draw.background(ctx, t, S)
        b = self.T.beat_at(min(t, self.T.duration - 1e-3))
        beat = self.script["beats"][b["i"]]
        lt = t - b["start"]; dur = b["end"] - b["start"]
        # slow camera push-in on every beat
        z = 1 + .05 * ease(lt / max(dur, 1))
        ctx.save(); ctx.translate(W / 2, 760); ctx.scale(z, z); ctx.translate(-W / 2, -760)
        SCENES[beat["scene"]](ctx, lt, beat, self.keys[b["i"]], S)
        ctx.restore()
        decorations(ctx, lt, beat, S)
        if lt < .18 and b["i"] > 0:          # quick dip at each cut
            ctx.set_source_rgba(*S.bg1, 1 - lt / .18); ctx.paint()
        draw_captions(ctx, t, self.T.words, self.chunks, S)
        ctx.restore(); self.surf.flush()

    def stills(self, times, prefix):
        out = []
        for i, t in enumerate(times):
            self.frame(t); p = f"{prefix}_{i:02d}.png"; self.surf.write_to_png(p); out.append(p)
        return out

    def video(self, audio_path, out_path, preset="veryfast"):
        n = int(math.ceil(self.T.duration * FPS))
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(audio_path), "-c:v", "libx264", "-preset", preset, "-crf", "20",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest", "-movflags", "+faststart", str(out_path)],
            stdin=subprocess.PIPE)
        stride = self.surf.get_stride()
        for i in range(n):
            self.frame(i / FPS)
            data = self.surf.get_data()
            if stride == W * 4:
                ff.stdin.write(data)
            else:  # some platforms pad rows; strip the padding
                mv = memoryview(data)
                for r in range(H):
                    ff.stdin.write(mv[r * stride: r * stride + W * 4])
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg encode failed")
        return out_path
