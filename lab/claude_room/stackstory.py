"""Stacked F3 story Short: facecam panel on top, game panel below, word-by-word captions on the seam (24 Nov 2026, Clip Room).

spec json: {"src","out","face":[x,y,w,h],"game":[x,y,w,h],
  "segments":[{"a","b","game"(opt per-segment crop),"zoom"(opt game punch-in 1.0-1.3)}],
  "label":"top label text (whole video)", "label2":{"text","at"} (opt, replaces label from out-time at),
  "chips":[{"text","at","dur"}] (yellow asterisk beat labels under the label),
  "keywords":{"word":"&HBBGGRR&"}, "drop_words":[source start times], "replace":{"src word":"shown"},
  "gamma":1.25, "sat":1.15}
Layout 1080x1920: label band 0-300 (text y 190-290), face 300-1120 (820 px = 42.7%), game 1120-1728 (608), black 1728-1920.
Captions: Anton 84 px, 1-3 words per chunk, white, 8 px outline, centred on the seam at y 1120.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from edit import draw_line, text_width, FONT

W, H = 1080, 1920
FACE_Y, FACE_H, GAME_Y, GAME_H = 300, 820, 1120, 608


def label_png(text, path, chip=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = ImageFont.truetype(FONT, 58)
    lines = text.split("\n")
    y = 196 if len(lines) == 1 else 172
    for ln in lines:
        tw = text_width(ln, f, 58)
        draw_line(img, (W - tw) / 2, y, ln, f, 58, (255, 255, 255))
        y += 70
    if chip:
        fc = ImageFont.truetype(FONT, 44)
        tw = text_width(chip, fc, 44)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([(W - tw) / 2 - 18, 318, (W + tw) / 2 + 18, 380], radius=14, fill=(0, 0, 0, 200))
        draw_line(img, (W - tw) / 2, 324, chip, fc, 44, (255, 214, 10))
    img.save(path)


def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main(spec_path):
    s = json.loads(Path(spec_path).read_text())
    tmp = Path(tempfile.mkdtemp())
    words = json.loads(Path(s["src"]).with_suffix(".json").read_text())["words"]
    fx, fy, fw, fh = s["face"]
    g_s, sat = s.get("gamma", 1.25), s.get("sat", 1.15)
    parts, chunks, t_out = [], [], 0.0
    drop, rep, kw = set(s.get("drop_words", [])), s.get("replace", {}), s.get("keywords", {})
    for n, g in enumerate(s["segments"]):
        gx, gy, gw, gh = g.get("game", s["game"])
        z = g.get("zoom", 1.0)
        if z != 1.0:
            nw, nh = round(gw / z / 2) * 2, round(gh / z / 2) * 2
            gx, gy, gw, gh = gx + (gw - nw) // 2, gy + (gh - nh) // 2, nw, nh
        dur = g["b"] - g["a"]
        p = tmp / f"p{n}.mp4"
        vf = (f"[0:v]split[a][b];[a]crop={fw}:{fh}:{fx}:{fy},scale={W}:{FACE_H}:flags=lanczos,eq=gamma=1.1:saturation=1.1[f];"
              f"[b]crop={gw}:{gh}:{gx}:{gy},scale={W}:{GAME_H}:flags=lanczos,eq=gamma={g_s}:saturation={sat}[g];"
              f"color=black:s={W}x{H}:r=30:d={dur}[bg];[bg][f]overlay=0:{FACE_Y}[t];[t][g]overlay=0:{GAME_Y},fps=30,format=yuv420p[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(g["a"]), "-t", str(dur), "-i", s["src"], "-filter_complex", vf,
                        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-ar", "48000",
                        str(p)], check=True)
        parts.append(p)
        seg_words = [w for w in words if g["a"] <= w["s"] < g["b"] - 0.05 and w["s"] not in drop]
        cur = []
        for w in seg_words:
            txt = rep.get(w["w"], w["w"]).upper().strip()
            if not txt:
                continue
            cur.append((w["s"] - g["a"] + t_out, w["e"] - g["a"] + t_out, txt))
            if len(cur) == 3 or txt[-1] in ".?!,":
                chunks.append(cur); cur = []
        if cur:
            chunks.append(cur)
        t_out += dur
    total = t_out
    # captions
    ev = []
    for i, c in enumerate(chunks):
        a = c[0][0]; b = min(c[-1][1] + 0.25, total)
        if i + 1 < len(chunks):
            b = min(b, chunks[i + 1][0][0] - 0.01)
        text = " ".join(t for _, _, t in c)
        for k, col in kw.items():
            text = text.replace(k.upper(), "{\\c" + col + "}" + k.upper() + "{\\c&HFFFFFF&}")
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{text}")
    # merge overlaps: end each at next start
    for i in range(len(ev) - 1):
        pass
    ass = tmp / "c.ass"
    ass.write_text("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
                   "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                   "Style: Cap,Anton,124,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,8,3,5,70,140,0,1\n\n"
                   "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" +
                   "\n".join(e.replace(",Cap,,0,0,0,,", ",Cap,,0,0,0,,{\\pos(500,1120)}") for e in ev) + "\n")
    lst = tmp / "l.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cat = tmp / "cat.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)], check=True)
    # label overlays (label, optional label2 switch, chips)
    pngs, ov = [], ""
    l1 = tmp / "l1.png"; label_png(s["label"], l1); pngs.append((l1, 0, s.get("label2", {}).get("at", total)))
    if "label2" in s:
        l2 = tmp / "l2.png"; label_png(s["label2"]["text"], l2); pngs.append((l2, s["label2"]["at"], total))
    for i, c in enumerate(s.get("chips", [])):
        pc = tmp / f"c{i}.png"; label_png("", pc, chip=c["text"]); pngs.append((pc, c["at"], c["at"] + c["dur"]))
    inputs = []
    chain = "[0:v]"
    for i, (p, a, b) in enumerate(pngs):
        inputs += ["-i", str(p)]
        out = f"[o{i}]"
        ov += f"{chain}[{i + 1}:v]overlay=0:0:enable='between(t,{a},{b})'{out};"
        chain = out
    ov += f"{chain}ass={ass}:fontsdir=/usr/share/fonts/truetype/google-fonts/ofl/anton[v]"
    pre = tmp / "pre.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cat)] + inputs + ["-filter_complex", ov, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "copy", str(pre)], check=True)
    # two-pass loudnorm -14
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(pre), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre), "-af", af, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    s["out"]], check=True)
    Path(s["out"]).with_suffix(".ass").write_text(ass.read_text())
    print("OK", s["out"], round(total, 2), "s,", len(ev), "caption chunks")


if __name__ == "__main__":
    main(sys.argv[1])
