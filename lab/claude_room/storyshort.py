"""Full-screen 9:16 story Short with word-by-word captions from Whisper words (22 Nov 2026, Clip Room).

spec json: {"src", "out", "segments": [{"a","b","cx","cy"(opt, crop top),"h"(opt crop height),"vf"(opt)}],
  "label": {"text","at","dur"}, "chips": [{"text","at","dur","y"}], "insets": [{"png","at","dur","x","y","w","caption"}],
  "cap_y": default caption centre y, "cap_y_by_seg": {seg_index: y}, "keywords": {"word": "&HBBGGRR&"},
  "drop_words": [source times to skip], "replace": {"buck": "Buck", ...}}
Captions: Anton, 1-3 words per chunk, white with 8 px black outline, keyword colour. Loudness two-pass -14 LUFS.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from edit import draw_line, text_width, FONT

W, H = 1080, 1920
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"


def box_png(text, path, y, size=62, pad=26, bg=(0, 0, 0, 235), fg=(255, 255, 255), font_path=FONT):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = ImageFont.truetype(font_path, size)
    tw = text_width(text, f, size)
    x0 = (W - tw) / 2
    ImageDraw.Draw(img).rounded_rectangle([x0 - pad, y - pad * 0.6, x0 + tw + pad, y + size * 1.25 + pad * 0.6],
                                          radius=22, fill=bg)
    draw_line(img, x0, y, text, f, size, fg)
    img.save(path)


def inset_png(src_png, path, x, y, w, caption):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im = Image.open(src_png).convert("RGBA")
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 10, y - 10, x + w + 10, y + h + 70], radius=18, fill=(0, 0, 0, 230), outline=(255, 214, 10), width=5)
    img.paste(im, (x, y), im)
    f = ImageFont.truetype(FONT, 40)
    tw = text_width(caption, f, 40)
    draw_line(img, x + (w - tw) / 2, y + h + 12, caption, f, 40, (255, 214, 10))
    img.save(path)


def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main(spec_path):
    s = json.loads(Path(spec_path).read_text())
    tmp = Path(tempfile.mkdtemp())
    sw, sh = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                      "-of", "csv=p=0", s["src"]], capture_output=True, text=True).stdout.strip().split(","))
    words = json.loads(Path(s["src"]).with_suffix(".json").read_text())["words"]
    parts, chunks, t_out = [], [], 0.0
    drop = set(s.get("drop_words", []))
    rep = s.get("replace", {})
    for n, g in enumerate(s["segments"]):
        h = g.get("h", sh); w = g.get("w") or round(h * 9 / 16 / 2) * 2
        x = max(0, min(sw - w, g["cx"] - w // 2)); y = max(0, min(sh - h, g.get("cy", 0)))
        if g.get("w"):   # 23 Nov: a wider crop (e.g. to fit the WASTED text), fit to width, thin black bars top/bottom
            vf = (f"crop={w}:{h}:{x}:{y},scale={W}:-2:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
                  "unsharp=5:5:0.5:5:5:0.0,fps=30,format=yuv420p,setsar=1")
        else:
            vf = f"crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.5:5:5:0.0,fps=30,format=yuv420p,setsar=1"
        if g.get("vf"):
            vf += "," + g["vf"]
        p = tmp / f"p{n}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(g["a"]), "-to", str(g["b"]), "-i", s["src"], "-vf", vf,
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-ac", "2", str(p)], check=True)
        parts.append(p)
        cy = s.get("cap_y_by_seg", {}).get(str(n), s.get("cap_y", 1150))
        seg_words = [wd for wd in words if g["a"] - 0.05 <= wd["s"] < g["b"] - 0.1 and round(wd["s"], 1) not in drop]
        cur = []
        for wd in seg_words:
            cur.append(wd)
            txt = wd["w"]
            if len(cur) == 3 or txt.endswith((".", "?", "!", ",")) or wd is seg_words[-1]:
                a = cur[0]["s"] - g["a"] + t_out
                chunks.append({"a": a, "words": [(c["w"], c["s"] - g["a"] + t_out) for c in cur], "y": cy})
                cur = []
        t_out += g["b"] - g["a"]
    total = t_out
    for i, c in enumerate(chunks):
        c["b"] = min(chunks[i + 1]["a"] if i + 1 < len(chunks) else total, c["a"] + 2.2)
    kw = s.get("keywords", {})
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             "Style: C,Anton,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,8,3,5,70,140,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for c in chunks:
        ws = c["words"]
        for k, (wd, ws_t) in enumerate(ws):  # karaoke: words appear as spoken
            a = ws_t if k else c["a"]
            b = ws[k + 1][1] if k + 1 < len(ws) else c["b"]
            if b <= a:
                continue
            out = []
            for j, (w2, _) in enumerate(ws[:k + 1]):
                clean = w2.strip(".,?!").lower()
                for r, v in rep.items():
                    if clean == r:
                        w2 = w2.replace(w2.strip(".,?!"), v)
                col = kw.get(clean)
                t = w2.upper()
                out.append((f"{{\\c{col}}}" + t + "{\\c&H00FFFFFF&}") if col else t)
            lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},C,,0,0,0,,{{\\pos(540,{c['y']})}}" + " ".join(out))
    ass = tmp / "c.ass"; ass.write_text("\n".join(lines))
    lst = tmp / "l.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = tmp / "j.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    ovs = []
    if s.get("label"):
        L = s["label"]; png = tmp / "label.png"; box_png(L["text"], png, L.get("y", 215), L.get("size", 64), fg=tuple(L.get("fg", (255, 255, 255)))); ovs.append((png, L["at"], L["dur"]))
    for i, c in enumerate(s.get("chips", [])):
        png = tmp / f"chip{i}.png"
        box_png(c["text"], png, c["y"], c.get("size", 54), bg=tuple(c.get("bg", (0, 0, 0, 220))), fg=tuple(c.get("fg", (255, 255, 255))))
        ovs.append((png, c["at"], c["dur"]))
    for i, c in enumerate(s.get("insets", [])):
        png = tmp / f"in{i}.png"; inset_png(c["png"], png, c["x"], c["y"], c["w"], c["caption"]); ovs.append((png, c["at"], c["dur"]))
    inputs = ["-i", str(joined)]
    chain, last = f"[0:v]ass={ass}:fontsdir=/usr/share/fonts/truetype/google-fonts/ofl/anton[v0];", "[v0]"
    for i, (png, at, dur) in enumerate(ovs):
        inputs += ["-i", str(png)]
        chain += f"{last}[{i + 1}:v]overlay=0:0:enable='between(t,{at},{at + dur})'[o{i}];"
        last = f"[o{i}]"
    chain = chain.rstrip(";")
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(joined), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", chain, "-map", last, "-map", "0:a",
                    "-af", ln, "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", s["out"]], check=True)
    Path(s["out"]).with_suffix(".ass").write_text(ass.read_text())
    print(s["out"], round(total, 2), "s")


if __name__ == "__main__":
    main(sys.argv[1])
