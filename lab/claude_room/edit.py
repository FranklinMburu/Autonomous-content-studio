"""Claude's hand editor for GTA 6 streamer Shorts (19 Nov 2026). Follows the 10/10 spec:
1080x1920; title box static at frame 0 inside the safe zone (x 90-990, y 210-390); stack layout = facecam band
(y 400-1000) over gameplay band (y 1000-1608) on a blurred, darkened game background; optional hard switch to a full
facecam (y 400-1440) at the peak; one punchline caption (<= 6 words) on the seam; -14 LUFS, -1 dBTP; no music.

  python edit.py spec.json            spec: {"src","start","end","face":[x,y,w,h],"game":[x,y,w,h]|null,
                                             "face_at":sec|null,"bg":[x,y,w,h]|null (blurred-background source crop; default full frame),"title","punch":{"text","at","dur"}|null,"out"}
  optional: "game_h" (band height, default 608), "full_h" (full-face height, default 1040), "game_eq" (ffmpeg filter on
            the game band), "captions"/"punches" [{"text","at","dur","y"}] extra timed captions (wrap to 2 lines if wide)
  python edit.py spec.json --sheet    also writes <out>.sheet.jpg (frames at 0, 0.5 s, 25/50/75 %, end) for review
"""
import json, subprocess, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)


def runs(text):
    out, cur, emo = [], "", None
    for ch in text:
        e = is_emoji(ch)
        if emo is None or e == emo:
            cur += ch
        else:
            out.append((cur, emo)); cur = ch
        emo = e
    if cur:
        out.append((cur, emo))
    return out


def text_width(text, font, size):
    w = 0
    for chunk, emo in runs(text):
        if emo:
            w += sum(int(size * 1.15) for c in chunk if c not in "️‍")
        else:
            w += font.getlength(chunk)
    return w


def draw_line(img, x, y, text, font, size, fill, stroke=0, stroke_fill=None):
    d = ImageDraw.Draw(img)
    for chunk, emo in runs(text):
        if emo:
            ef = ImageFont.truetype(EMOJI, 109)
            for c in chunk:
                if c in "️‍":
                    continue
                g = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((0, 0), c, font=ef, embedded_color=True)
                g = g.crop(g.getbbox() or (0, 0, 1, 1)).resize((int(size * 1.05), int(size * 1.05)), Image.LANCZOS)
                img.alpha_composite(g, (int(x), int(y + size * 0.08)))
                x += int(size * 1.15)
        else:
            d.text((x, y), chunk, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += font.getlength(chunk)


def wrap(text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, font, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + ([cur] if cur else [])


def title_png(title, path):
    """White rounded box, black heavy text, centred in the band y 210-390, max 2 lines."""
    for size in (60, 56, 52, 48, 44):
        font = ImageFont.truetype(FONT, size)
        lines = wrap(title, font, size, 900 - 56)
        if len(lines) <= 2:
            break
    lh = int(size * 1.18)
    bw = int(max(text_width(l, font, size) for l in lines)) + 56
    bh = lh * len(lines) + 36
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0 = (W - bw) // 2, 210 + (180 - bh) // 2
    ImageDraw.Draw(img).rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=24, fill="white")
    for i, l in enumerate(lines):
        lw = text_width(l, font, size)
        draw_line(img, (W - lw) / 2, y0 + 18 + i * lh - size * 0.06, l, font, size, "black")
    img.save(path)
    return y0, y0 + bh


def punch_png(text, path, y_center, size=64):
    """Bold white caption, black outline, centred on y_center; wraps to 2 lines if wider than 960 px."""
    font = ImageFont.truetype(FONT, size)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lines = wrap(text, font, size, 960)
    lh = int(size * 1.12)
    y0 = y_center - size * 0.6 - (len(lines) - 1) * lh / 2
    for i, l in enumerate(lines):
        lw = text_width(l, font, size)
        draw_line(img, (W - lw) / 2, y0 + i * lh, l, font, size, "white", stroke=7, stroke_fill="black")
    img.save(path)


def render(spec, sheet=False):
    s = spec
    out = Path(s["out"]); out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix("")
    title_png(s["title"], f"{tmp}.title.png")
    dur = s["end"] - s["start"]
    fx, fy, fw, fh = s["face"]
    gx, gy, gw, gh = s.get("game") or [0, 0, 1920, 1080]
    face_at = s.get("face_at")
    GH = s.get("game_h", 608)   # game band height (y 1000 .. 1000+GH); 608 = old template
    FH = s.get("full_h", 1040)  # full-facecam height (y 400 .. 400+FH)
    geq = ("," + s["game_eq"]) if s.get("game_eq") else ""  # e.g. "eq=brightness=0.08:gamma=1.25"
    inputs = ["-ss", str(s["start"]), "-t", str(dur), "-i", s["src"], "-i", f"{tmp}.title.png"]
    n = 4 if face_at is not None else 3
    g = (f"[0:v]split={n}[bg][fa][ga]" + ("[ff];" if n == 4 else ";") +
         (f"[bg]crop={s['bg'][2]}:{s['bg'][3]}:{s['bg'][0]}:{s['bg'][1]}," if s.get("bg") else "[bg]") + f"scale=-2:{H},crop={W}:{H},gblur=sigma=28,eq=brightness=-0.22:saturation=0.8[bgo];"
         f"[fa]crop={fw}:{fh}:{fx}:{fy},scale={W}:600:force_original_aspect_ratio=increase:flags=lanczos,hqdn3d=1.2:1.2:4:4,unsharp=5:5:0.9:5:5:0.0,crop={W}:600[fac];"
         f"[ga]crop={gw}:{gh}:{gx}:{gy},scale={W}:{GH}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{GH}{geq}[gam];" +
         (f"[ff]crop={fw}:{fh}:{fx}:{fy},scale={W}:{FH}:force_original_aspect_ratio=increase:flags=lanczos,hqdn3d=1.2:1.2:4:4,unsharp=5:5:0.9:5:5:0.0,crop={W}:{FH}[ful];" if n == 4 else "") +
         (f"[bgo][fac]overlay=0:400[v1];[v1][gam]overlay=0:1000[v2];" if face_at != 0 else
          "[fac]nullsink;[gam]nullsink;[bgo]null[v2];"))  # face_at 0: full facecam only, no game strip under it
    if face_at is not None:
        g += f"[v2][ful]overlay=0:400:enable='gte(t,{face_at})'[v3];"
    else:
        g += "[v2]null[v3];"
    g += "[v3][1:v]overlay=0:0[v4];"
    last = "v4"
    if s.get("punch"):
        p = s["punch"]
        yc = p.get("y") or (1390 if (face_at is not None and p["at"] >= face_at) else 1000)  # optional explicit centre y
        punch_png(p["text"], f"{tmp}.punch.png", yc)
        inputs += ["-i", f"{tmp}.punch.png"]
        g += f"[v4][2:v]overlay=0:0:enable='between(t,{p['at']},{p['at'] + p.get('dur', 1.6)})'[v5];"
        last = "v5"
    for k, p in enumerate((s.get("punches") or []) + (s.get("captions") or [])):  # optional extra captions, e.g. a counter: [{"text","at","dur","y"}]
        punch_png(p["text"], f"{tmp}.punch{k}.png", p.get("y", 1000))
        inputs += ["-i", f"{tmp}.punch{k}.png"]
        g += f"[{last}][{sum(1 for x in inputs if x == '-i') - 1}:v]overlay=0:0:enable='between(t,{p['at']},{p['at'] + p.get('dur', 1.6)})'[vp{k}];"
        last = f"vp{k}"
    # two-pass loudness (19 Nov review: one pass left C3 at -11.4 LUFS)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(s["start"]), "-t", str(dur), "-i", s["src"], "-af",
                        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    g += f"[{last}]format=yuv420p[vout];[0:a]{ln},alimiter=limit=0.891:level=false,aresample=48000[aout]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", g, "-map", "[vout]", "-map", "[aout]",
           "-r", str(s.get("fps", 30)), "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-tune", "film", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    if sheet:
        ts = [0.0, 0.5, dur * 0.25, dur * 0.5, dur * 0.75, max(0, dur - 0.2)]
        ims = []
        for t in ts:
            f = f"{tmp}.f.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", "-vf", "scale=270:480", f])
            ims.append(Image.open(f).convert("RGB"))
        sh = Image.new("RGB", (270 * len(ims), 480))
        for i, im in enumerate(ims):
            sh.paste(im, (270 * i, 0))
        sh.save(f"{tmp}.sheet.jpg", quality=85)
    return out


if __name__ == "__main__":
    spec = json.loads(Path(sys.argv[1]).read_text())
    for sp in (spec if isinstance(spec, list) else [spec]):
        print("made", render(sp, "--sheet" in sys.argv))
