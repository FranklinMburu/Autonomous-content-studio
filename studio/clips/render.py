"""Draw a clip.json as a finished 1080x1920 Short. Frame by frame in Python (numpy + Pillow), piped to ffmpeg.
No clock and no randomness: the same clip.json and source give the same frames (tests/test_clips.py checks it).

Sound: the stream's own audio for the edit, 8 ms crossfades at every cut, a soft whoosh at the cold-open cut,
then two-pass loudness normalisation to bar.loudness (-14 LUFS, true peak <= -1.5 dBTP: what Shorts plays back at).
"""
import json, math, subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..paths import ROOT

OW, OH, FPS, SR = 1080, 1920, 30, 48000
FONT = ROOT / "assets" / "fonts" / "Poppins-Bold.ttf"
_fonts = {}


def font(px):
    if px not in _fonts:
        _fonts[px] = ImageFont.truetype(str(FONT), px)
    return _fonts[px]


# ---------- frames in ---------------------------------------------------------------------------------------------
def read_segment(video, a, b, w, h):
    n = max(1, int(round((b - a) * FPS)))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", str(video), "-t", f"{b - a + 0.2:.3f}",
                          "-vf", f"fps={FPS},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "2", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8)
    k = len(fr) // (w * h * 3)
    fr = fr[: k * w * h * 3].reshape(k, h, w, 3)
    if k == 0:
        return np.zeros((n, h, w, 3), np.uint8)
    if k < n:
        fr = np.concatenate([fr, np.repeat(fr[-1:], n - k, axis=0)])
    return fr[:n]


def iter_segment(video, a, b, w, h):
    """The same frames as read_segment, one at a time from an ffmpeg pipe: a 45 s 1080p segment held whole is ~8 GB
    and got the renderer killed (13 Nov); streaming keeps memory flat. Same count and padding rule as read_segment."""
    n = max(1, int(round((b - a) * FPS)))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", str(video), "-t", f"{b - a + 0.2:.3f}",
                          "-vf", f"fps={FPS},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "2", "-"],
                         stdout=subprocess.PIPE)
    size, k, last = w * h * 3, 0, None
    while k < n:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        last = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        k += 1
        yield last
    p.stdout.close(); p.kill(); p.wait()
    pad = last if last is not None else np.zeros((h, w, 3), np.uint8)
    for _ in range(n - k):
        yield pad


def read_audio(video, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", str(video), "-t", f"{b - a:.3f}", "-vn",
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = max(1, int(round((b - a) * FPS))) * SR // FPS   # exactly as long as the frames of this segment
    if len(x) < n:
        x = np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
    return x[:n]   # (-shortest is racy with piped frames; exact lengths keep renders identical)


# ---------- zoom curves -------------------------------------------------------------------------------------------
def shot_at(t, clip):
    cur = {"view": "wide", "zoom": 1.0}
    for f in clip.get("framing", []):
        if f["t"] <= t:
            cur = f
    return cur


def zoom_at(t, clip):
    base = 1.0
    for f in clip.get("framing", []):
        if f["t"] <= t:
            base = f["zoom"] if clip["layout"]["kind"] in ("letterbox", "speaker") else 1.0
    p = 0.0
    for z in clip.get("zooms", []):
        d = t - z["t"]
        if 0 <= d < 1.2:   # snap in over 0.08 s, ease back out over the next second
            p = max(p, z["amount"] * (d / 0.08 if d < 0.08 else math.exp(-(d - 0.08) * 2.6)))
    return base * (1 + p)


# ---------- picture -----------------------------------------------------------------------------------------------
def crop_cover(img, box, out_w, out_h, zoom=1.0):
    """Crop `box` (x, y, w, h, in img pixels) to the out aspect around its centre, zoom in, resize to out size."""
    H, W = img.shape[:2]
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    ar = out_w / out_h
    if w / h > ar:
        w = h * ar
    else:
        h = w / ar
    w, h = w / zoom, h / zoom
    x0 = int(round(min(max(0, cx - w / 2), W - w)))
    y0 = int(round(min(max(0, cy - h / 2), H - h)))
    sub = img[y0:y0 + int(round(h)), x0:x0 + int(round(w))]
    return Image.fromarray(sub).resize((out_w, out_h), Image.BILINEAR)


def compose_picture(fr, clip, t, scale):
    lay = clip["layout"]
    z = zoom_at(t, clip)
    H, W = fr.shape[:2]
    S = lambda b: [v * scale for v in b]  # noqa: E731
    canvas = Image.new("RGB", (OW, OH))
    kind = lay["kind"]
    shot = shot_at(t, clip)
    if kind == "split2" and shot.get("view") == "focus":   # the person talking, full screen
        p = S(lay["people"][shot.get("who", 0)])
        h = min(H, max(p[3] * 3.2, 0.8 * H))           # never a tiny, blurry crop
        w = h * OW / OH
        canvas.paste(crop_cover(fr, [p[0] + p[2] / 2 - w / 2, p[1] + p[3] * 0.5 - h * 0.36, w, h], OW, OH, z), (0, 0))
        return canvas
    if kind == "stack":
        cam = S(lay["cam"])
        top_h = int(OH * (0.62 if shot.get("view") == "focus" else 0.40))   # focus: the facecam takes most of it
        face = S(lay["face"]) if lay.get("face") else None
        cb = cam if not face else [face[0] + face[2] / 2 - cam[2] / 2, face[1] + face[3] / 2 - cam[3] / 2, cam[2], cam[3]]
        canvas.paste(crop_cover(fr, cb, OW, top_h, 1.0 + (z - 1) * 0.5), (0, 0))
        gh = OH - top_h
        gw_src = W / 1.3                                   # keep most of the game: 77% of the width, centred on the action
        ax = lay.get("action_x", W / 2) * scale
        cx = min(max(gw_src / 2, ax), W - gw_src / 2)
        gimg = crop_cover(fr, [cx - gw_src / 2, 0, gw_src, H], OW, int(OW * H / gw_src), z)
        bg = gimg.resize((OW // 12, gh // 12), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).resize((OW, gh), Image.BILINEAR)
        canvas.paste(Image.fromarray((np.asarray(bg) * 0.45).astype(np.uint8)), (0, top_h))
        canvas.paste(gimg, (0, top_h + (gh - gimg.height) // 2))
        ImageDraw.Draw(canvas).rectangle([0, top_h - 3, OW, top_h + 3], fill=(0, 0, 0))
    elif kind == "split2":
        half = OH // 2
        for i, p in enumerate(lay["people"][:2]):
            p = S(p)
            h = min(H, p[3] * 3.4)
            w = h * OW / half
            box = [p[0] + p[2] / 2 - w / 2, p[1] + p[3] * 0.4 - h * 0.38, w, h]   # face a little below the middle
            canvas.paste(crop_cover(fr, box, OW, half, z), (0, i * half))
        ImageDraw.Draw(canvas).rectangle([0, half - 3, OW, half + 3], fill=(0, 0, 0))
    elif kind == "speaker":
        p = S(lay["people"][0])
        h = H
        w = h * OW / OH
        canvas.paste(crop_cover(fr, [p[0] + p[2] / 2 - w / 2, 0, w, h], OW, OH, z), (0, 0))
    elif kind == "band":
        # The reference look (measured 13 Nov on Kick_Clippers' 32M / 28M / 9.7M Shorts): the 16:9 picture cropped at
        # the sides and zoomed ~1.6x into a big band that fills about half the screen, on a blurred copy of itself,
        # with the title in a white box above it for the whole clip. Crop centred on the people when we know where.
        zf = clip["style"].get("band_zoom", 1.6)
        cw = W / zf
        ax = lay.get("action_x", W / 2) * scale
        cx = min(max(cw / 2, ax), W - cw / 2)
        bg = crop_cover(fr, [0, 0, W, H], OW // 10, OH // 10).filter(ImageFilter.GaussianBlur(3)).resize((OW, OH), Image.BILINEAR)
        bg = Image.fromarray((np.asarray(bg) * 0.80).astype(np.uint8))
        canvas.paste(bg, (0, 0))
        fh = int(OW * H / cw)
        canvas.paste(crop_cover(fr, [cx - cw / 2, 0, cw, H], OW, fh, z), (0, int(OH * clip["style"].get("band_y", 0.47) - fh / 2)))
    else:   # letterbox on a blurred, darkened copy of itself
        bg = crop_cover(fr, [0, 0, W, H], OW // 10, OH // 10).filter(ImageFilter.GaussianBlur(3)).resize((OW, OH), Image.BILINEAR)
        bg = Image.fromarray((np.asarray(bg) * 0.42).astype(np.uint8))
        canvas.paste(bg, (0, 0))
        fh = int(OW * H / W)
        canvas.paste(crop_cover(fr, [0, 0, W, H], OW, fh, z), (0, int(OH * clip["style"].get("letterbox_y", 0.5) - fh / 2)))
    return canvas


# ---------- text --------------------------------------------------------------------------------------------------
def caption_y(clip, t=0.0):
    """Captions sit where the picture lets them: on the seam of two-panel layouts (it moves with the shot), under the
    face on a focus shot, else at the measured height."""
    st, kind = clip["style"], clip["layout"]["kind"]
    if shot_at(t, clip).get("view") == "focus" and kind in ("stack", "split2"):
        return st.get("y_focus", 0.64)
    return st.get("y_by_layout", {}).get(kind, st["y"])


def draw_captions(canvas, clip, t):
    st = clip["style"]
    chunk = next((c for c in clip["captions"] if c["start"] <= t < c["end"]), None)
    if not chunk:
        return
    d = ImageDraw.Draw(canvas)
    px = st["font_px"]
    pop = 1 + 0.12 * max(0.0, 1 - (t - chunk["start"]) / 0.09)
    f = font(int(px * pop))
    words = chunk["words"]
    active = max([i for i, w in enumerate(words) if w["start"] <= t] or [0])
    widths = [d.textlength(w["w"] + " ", font=f) for w in words]
    total = sum(widths) - d.textlength(" ", font=f)
    maxw = OW * (st["safe_x"][1] - st["safe_x"][0])
    lines = [[0]]
    if total > maxw:   # wrap to two lines
        acc = 0
        lines = [[]]
        for i, wd in enumerate(widths):
            if acc + wd > maxw and lines[-1]:
                lines.append([])
                acc = 0
            lines[-1].append(i)
            acc += wd
    else:
        lines = [list(range(len(words)))]
    y = OH * caption_y(clip, t) - len(lines) * px * 0.6
    for ln in lines:
        lw = sum(widths[i] for i in ln) - d.textlength(" ", font=f)
        x = OW * (st["safe_x"][0] + st["safe_x"][1]) / 2 - lw / 2
        for i in ln:
            col = tuple(st["accent_rgb"]) if i == active else (255, 255, 255)
            d.text((x + 4, y + 6), words[i]["w"], font=f, fill=(0, 0, 0))   # drop shadow
            d.text((x, y), words[i]["w"], font=f, fill=col, stroke_width=st["stroke_px"], stroke_fill=(0, 0, 0))
            x += widths[i]
        y += px * 1.15


EMOJI_FONT = Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")   # apt: fonts-noto-color-emoji
_EMOJI = None
_EMOJI_RE = None


def _is_emoji_char(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0x200D, 0xFE0F) or 0x1F1E6 <= o <= 0x1F1FF


def _runs(text):
    """[(is_emoji, str)]: emoji sequences are drawn from the colour emoji font, the rest in Poppins."""
    out = []
    for ch in text:
        e = _is_emoji_char(ch)
        if out and out[-1][0] == e:
            out[-1] = (e, out[-1][1] + ch)
        else:
            out.append((e, ch))
    return out


def _emoji_img(seq, px):
    """One emoji (or ZWJ sequence) as an RGBA image px tall; None when no emoji font is installed."""
    global _EMOJI
    if not EMOJI_FONT.exists():
        return None
    if _EMOJI is None:
        _EMOJI = ImageFont.truetype(str(EMOJI_FONT), 109)   # the only size this bitmap font has
    im = Image.new("RGBA", (160, 136), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 4), seq, font=_EMOJI, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb)
    return im.resize((max(1, int(im.width * px / im.height)), px), Image.LANCZOS)


def _emoji_units(s):
    """Split an emoji run into single emoji (keeping ZWJ / variation selectors with their base)."""
    units, cur = [], ""
    for ch in s:
        if ch in ("\u200d", "\ufe0f") or (cur.endswith("\u200d")):
            cur += ch
        else:
            if cur:
                units.append(cur)
            cur = ch
    if cur:
        units.append(cur)
    return units


def _line_width(d, line, f, px):
    w = 0
    for e, s in _runs(line):
        w += sum(int(px * 1.05) for _ in _emoji_units(s)) if e else d.textlength(s, font=f)
    return w


def _draw_line(canvas, d, x, y, line, f, px, fill):
    for e, s in _runs(line):
        if e:
            for u in _emoji_units(s):
                im = _emoji_img(u, int(px * 0.92))
                if im is not None:
                    canvas.paste(im, (int(x), int(y + px * 0.12)), im)
                x += int(px * 1.05)
        else:
            d.text((x, y), s, font=f, fill=fill)
            x += d.textlength(s, font=f)


def draw_hook(canvas, clip, t):
    h = clip["hook"]
    if not h["text"] or t >= h["until"]:
        return
    d = ImageDraw.Draw(canvas)
    st = clip["style"]
    px = st.get("hook_px", 62)
    f = font(px)
    words, lines = h["text"].split(), [""]
    for w in words:
        trial = (lines[-1] + " " + w).strip()
        if _line_width(d, trial, f, px) > OW * 0.78 and lines[-1]:
            lines.append(w)
        else:
            lines[-1] = trial
    pad = 26
    bw = max(_line_width(d, l, f, px) for l in lines) + 2 * pad
    bh = len(lines) * px * 1.18 + 2 * pad - px * 0.18
    s = min(1.0, 0.85 + t / 0.12 * 0.15)
    x0 = OW / 2 - bw * s / 2
    y0 = OH * st.get("hook_y_by_layout", {}).get(clip["layout"]["kind"], st.get("hook_y", 0.17))
    d.rounded_rectangle([x0, y0, x0 + bw * s, y0 + bh * s], radius=22, fill=(255, 255, 255))
    ff = font(int(px * s))
    for i, l in enumerate(lines):
        lw = _line_width(d, l, ff, int(px * s))
        _draw_line(canvas, d, OW / 2 - lw / 2, y0 + pad * s + i * px * 1.18 * s, l, ff, int(px * s), (10, 10, 10))


# ---------- sound -------------------------------------------------------------------------------------------------
def whoosh(n):
    x = np.arange(n) / SR
    rng = np.random.default_rng(0)
    noise = rng.standard_normal(n).astype(np.float32)
    k = np.exp(-((x - 0.18) / 0.09) ** 2)
    sweep = np.convolve(noise, np.ones(8) / 8, "same") * k * 0.10
    return np.stack([sweep, sweep], 1).astype(np.float32)


PRE = "acompressor=threshold=-20dB:ratio=3:attack=5:release=150:makeup=2,alimiter=limit=0.5:level=false"


def loudnorm(wav_in, wav_out, target=-14.0, tp=-1.5):
    """Tame the peaks first (a stream has screams and crash sounds), then two-pass linear loudnorm hits the target."""
    pre = str(wav_out) + ".pre.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav_in), "-af", PRE, str(pre)], check=True)
    wav_in = pre
    r = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", str(wav_in), "-af",
                        f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav_in), "-af",
                    f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
                    f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
                    "-ar", str(SR), str(wav_out)], check=True)
    Path(pre).unlink(missing_ok=True)


def render(clip, out_mp4, log=print, threads=2):
    # sliced threads: x264's frame threads gave different bytes on 1 run in 3 here (12 Nov); slices never did
    out_mp4 = Path(out_mp4)
    video = Path(clip["source"]["folder"]) / clip["source"]["video"]
    W0, H0 = clip["layout"]["src"]
    scale = min(1.0, 1920 / W0)
    w, h = int(W0 * scale) // 2 * 2, int(H0 * scale) // 2 * 2
    import soundfile as sf
    aud = []
    for i, e in enumerate(clip["edl"]):
        x = read_audio(video, *e["src"])
        f = min(len(x), int(0.008 * SR))
        if f:
            ramp = np.linspace(0, 1, f, dtype=np.float32)[:, None]
            x[:f] *= ramp
            x[-f:] *= ramp[::-1]
        aud.append(x)
    mix = np.concatenate(aud)
    if clip.get("cold_open") and len(clip["edl"]) > 1:
        s = int(clip["edl"][1]["at"] * SR) - int(0.18 * SR)
        wsh = whoosh(int(0.4 * SR))
        s = max(0, s)
        mix[s:s + len(wsh)] += wsh[: len(mix) - s]
    tmp = out_mp4.with_suffix("")
    sf.write(str(tmp) + ".mix.wav", np.clip(mix, -1, 1), SR)
    loudnorm(str(tmp) + ".mix.wav", str(tmp) + ".norm.wav", clip["style"].get("lufs", -14), clip["style"].get("true_peak", -1.5))
    total = sum(max(1, int(round((e["src"][1] - e["src"][0]) * FPS))) for e in clip["edl"])
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-i", str(tmp) + ".norm.wav", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "18", "-threads", str(threads), "-x264-params", "sliced-threads=1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                           "-movflags", "+faststart", "-frames:v", str(total), str(out_mp4)], stdin=subprocess.PIPE)
    fi = 0
    for e in clip["edl"]:
        for fr in iter_segment(video, *e["src"], w, h):
            t = fi / FPS
            cv = compose_picture(fr, clip, t, scale)
            draw_captions(cv, clip, t)
            draw_hook(cv, clip, t)
            ff.stdin.write(cv.tobytes())
            fi += 1
    ff.stdin.close()
    ff.wait()
    for s in (".mix.wav", ".norm.wav"):
        Path(str(tmp) + s).unlink(missing_ok=True)
    log(f"[render] {out_mp4.name}: {fi} frames, {fi / FPS:.1f} s")
    return out_mp4


def stills(clip, times, out_dir):
    """A few finished frames (PNG) without encoding the video: for quick looks and the contact sheet."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    video = Path(clip["source"]["folder"]) / clip["source"]["video"]
    W0, H0 = clip["layout"]["src"]
    scale = min(1.0, 1920 / W0)
    w, h = int(W0 * scale) // 2 * 2, int(H0 * scale) // 2 * 2
    paths = []
    for t in times:
        e = max([e for e in clip["edl"] if e["at"] <= t] or clip["edl"][:1], key=lambda e: e["at"])
        s = e["src"][0] + (t - e["at"])
        fr = read_segment(video, s, s + 1 / FPS, w, h)[0]
        cv = compose_picture(fr, clip, t, scale)
        draw_captions(cv, clip, t)
        draw_hook(cv, clip, t)
        p = out_dir / f"t{t:06.2f}.png"
        cv.save(p)
        paths.append(p)
    return paths
