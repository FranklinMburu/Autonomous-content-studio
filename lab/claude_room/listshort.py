"""List Short in the proven COLETHEMAN format, built from narration timings (20 Nov 2026).

python3 listshort.py spec.json
spec: {
  "narr_wav", "narr_json"            # Kokoro output (studio/voice.py): words with start/end, lines with beat
  "out",
  "title": {"text", "at", "dur"},    # opening on-screen title (PNG box, emoji ok)
  "beats": [ {"beat": i, "header": "1. ALLIGATOR ATTACK 🐊" | null,
              "shots": [ {"src", "a", "b", "cx", "y0", "h", "zoom": 1.06, "vf": "", "game_vol": 0.25} ] } ],
  "keywords": {"word": "&H00FFFF&"},  # ASS BGR colours for keyword highlighting
  "game_vol": 0.22, "tail": 0.0
}
Every beat's footage window runs from its first spoken line to the next beat's first line, so the cuts land on the
narration. Shots share the window in proportion to their source length and each gets a slow push-in so nothing is
static. Captions are word-by-word (current word yellow, keywords coloured) in ASS, burned with libass. Headers and the
title are PNG boxes from edit.py. Audio: narration on top of ducked game audio, two-pass loudnorm to -14 LUFS.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
from edit import title_png, W, H, FONT, wrap, text_width, draw_line
from PIL import Image, ImageFont

FONT_NAME = "Inter Black"


def header_png(text, path, y_top=250):
    """COLETHEMAN-style item header: big white heavy text, thick black outline, no box (max 2 lines)."""
    for size in (92, 86, 80, 74, 68):
        font = ImageFont.truetype(FONT, size)
        lines = wrap(text.replace("*", "\u2009") if False else text, font, size, 1000)
        if len(lines) <= 2:
            break
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lh = int(size * 1.15)
    sp = font.getlength(" ")
    for i, l in enumerate(lines):
        lw = text_width(l.replace("*", ""), font, size); x = (W - lw) / 2
        for wd in l.split(" "):
            col = "#2BE04A" if wd.startswith("*") else "white"; wd = wd.replace("*", "")
            draw_line(img, x, y_top + i * lh, wd, font, size, col, stroke=9, stroke_fill="black")
            x += text_width(wd, font, size) + sp
    img.save(path)


def ffrun(cmd):
    subprocess.run(cmd, check=True)


def probe_res(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", src],
                       capture_output=True, text=True).stdout.strip().split(",")
    return int(o[0]), int(o[1])


def windows(tm, beats_used):
    starts = {}
    for ln in tm["lines"]:
        starts.setdefault(ln["beat"], ln["start"])
    order = sorted(beats_used)
    win = {}
    for i, b in enumerate(order):
        a = 0.0 if i == 0 else starts[b]
        e = starts[order[i + 1]] if i + 1 < len(order) else tm["duration"]
        win[b] = (a, e)
    return win


def render_shot(sh, dur, path):
    sw, shh = probe_res(sh["src"])
    h = sh.get("h", shh); w = round(h * 9 / 16 / 2) * 2
    x = max(0, min(sw - w, int(sh["cx"] - w / 2))); y = max(0, min(shh - h, int(sh.get("y0", 0))))
    z = sh.get("zoom", 1.06)
    # crop, upscale, then a slow push-in (zoom from 1.0 to z across the shot)
    vf = (f"crop={w}:{h}:{x}:{y},scale={W * 2}:{H * 2}:flags=lanczos,"
          f"zoompan=z='1+({z}-1)*on/({max(int(dur * 30), 1)})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30,"
          f"unsharp=5:5:0.5:5:5:0.0,setsar=1,format=yuv420p")
    if sh.get("vf"):
        vf += "," + sh["vf"]
    ffrun(["ffmpeg", "-v", "error", "-y", "-ss", str(sh["a"]), "-t", f"{dur:.3f}", "-i", sh["src"], "-vf", vf,
           "-af", f"volume={sh.get('game_vol', 1.0)},aresample=48000,aformat=channel_layouts=stereo",
           "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "pcm_s16le", "-t", f"{dur:.3f}", str(path)])


def ass_time(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def captions_ass(tm, keywords, path, y=1180, max_words=3):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT_NAME},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    words = tm["words"]; ev = []
    # chunks: up to max_words, break at line ends and sentence punctuation
    cf = ImageFont.truetype(FONT, 96)
    fits = lambda ws: cf.getlength(" ".join(x["w"].upper() for x in ws)) * 1.1 <= 900
    chunks, cur = [], []
    for i, w in enumerate(words):
        if cur and not fits(cur + [w]):
            chunks.append(cur); cur = []
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        short_next = nxt is not None and len(nxt["w"].strip(".,?!")) <= 2 and nxt["line"] == w["line"] and fits(cur + [nxt])
        if (len(cur) >= max_words and not short_next) or nxt is None or nxt["line"] != w["line"] or re.search(r"[.?!,]$", w["w"]):
            chunks.append(cur); cur = []
    for ci, c in enumerate(chunks):
        nxt_start = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else 1e9
        for j, w in enumerate(c):
            st = w["start"]; en = c[j + 1]["start"] if j + 1 < len(c) else min(w["end"] + 0.12, nxt_start)
            parts = []
            for k, x in enumerate(c):
                t = x["w"].upper().replace("{", "").replace("}", "")
                key = re.sub(r"[^a-z0-9$,]", "", x["w"].lower())
                col = keywords.get(key)
                if k == j:
                    parts.append(r"{\c&H00E6FF&\fscx108\fscy108}" + t + r"{\r}")
                elif col:
                    parts.append(r"{\c" + col + "}" + t + r"{\r}")
                else:
                    parts.append(t)
            ev.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W // 2},{y})}}" + " ".join(parts))
    Path(path).write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def main(spec_path):
    s = json.loads(Path(spec_path).read_text()); tmp = Path(tempfile.mkdtemp())
    tm = json.loads(Path(s["narr_json"]).read_text())
    win = windows(tm, [b["beat"] for b in s["beats"]])
    parts, cursor, labels = [], 0.0, []
    for b in s["beats"]:
        a, e = win[b["beat"]]
        if b is s["beats"][-1]:
            e += s.get("tail", 0.0)
        W_ = e - a; fixed = sum(sh["d"] for sh in b["shots"] if "d" in sh)
        lens = [sh["b"] - sh["a"] for sh in b["shots"]]; tot = sum(l for l, sh in zip(lens, b["shots"]) if "d" not in sh) or 1
        for i, sh in enumerate(b["shots"]):
            d = sh["d"] if "d" in sh else (W_ - fixed) * lens[i] / tot
            p = tmp / f"s{len(parts):03d}.mov"; render_shot(sh, d, p); parts.append(p)
            if sh.get("label"):
                labels.append((sh["label"], cursor + 0.1, cursor + d))
            cursor += d
        b["_win"] = (a, e)
    lst = tmp / "l.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = tmp / "j.mov"
    ffrun(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    ass = tmp / "cap.ass"; captions_ass(tm, s.get("keywords", {}), ass)
    # overlays: title + headers
    inputs, chain, last, n = ["-i", str(joined), "-i", s["narr_wav"]], "", "[0:v]", 2
    ovs = []
    if s.get("title"):
        ovs.append((s["title"]["text"], s["title"]["at"], s["title"]["at"] + s["title"]["dur"], "header"))
    for b in s["beats"]:
        if b.get("header"):
            ovs.append((b["header"], b["_win"][0], b["_win"][1], "header"))
    for lb in labels:
        ovs.append((lb[0], lb[1], lb[2], "label"))
    for i, (txt, t0, t1, kind) in enumerate(ovs):
        png = tmp / f"o{i}.png"
        if kind == "label":
            header_png(txt, png, y_top=760)
        else:
            header_png(txt, png)
        inputs += ["-i", str(png)]
        chain += f"{last}[{n}:v]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[v{i}];"; last = f"[v{i}]"; n += 1
    chain += f"{last}ass={ass}[vout];"
    chain += "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=1.0[nar];[0:a][nar]amix=inputs=2:duration=first:normalize=0[mix]"
    mixed = tmp / "m.mov"
    ffrun(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[vout]", "-map", "[mix]",
           "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "pcm_s16le", str(mixed)])
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mixed), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    ffrun(["ffmpeg", "-v", "error", "-y", "-i", str(mixed), "-af", ln, "-c:v", "libx264", "-preset", "slow", "-crf", "16",
           "-tune", "film", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", s["out"]])
    print("made", s["out"])


if __name__ == "__main__":
    main(sys.argv[1])
