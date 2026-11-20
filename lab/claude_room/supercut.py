"""Supercut helper for edit.py (19 Nov 2026).
  python supercut.py spec.json [--sheet]
spec: {"id","out", "common": {face, game, bg, title, fps, ...edit.py keys}, "pieces": [{src,start,end[,game,punch,face_at,bg]}]}
Each piece is rendered with edit.py (same layout), concatenated (concat demuxer), then re-encoded once:
libx264 crf 15 + aac 192k with a whole-clip two-pass loudnorm to -14 LUFS / -1 dBTP.
"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edit
from PIL import Image


def run(spec, sheet=False):
    out = Path(spec["out"]); tmp = Path("/tmp") / f"sc_{out.stem}"; tmp.mkdir(exist_ok=True)
    parts = []
    for i, p in enumerate(spec["pieces"]):
        sp = {**spec["common"], **p, "out": str(tmp / f"p{i}.mp4")}
        sp.setdefault("punch", None)
        edit.render(sp)
        parts.append(sp["out"])
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{x}'\n" for x in parts))
    cat = tmp / "cat.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)], check=True)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(cat), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cat), "-af", f"{ln},alimiter=limit=0.891:level=false,aresample=48000",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-tune", "film", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    if sheet:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                                   capture_output=True, text=True).stdout)
        ims = []
        for t in [0.0, 0.5, dur * 0.25, dur * 0.5, dur * 0.75, max(0, dur - 0.2)]:
            f = tmp / "f.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(out), "-frames:v", "1", "-vf", "scale=270:480", str(f)])
            ims.append(Image.open(f).convert("RGB"))
        sh = Image.new("RGB", (270 * len(ims), 480))
        for i, im in enumerate(ims):
            sh.paste(im, (270 * i, 0))
        sh.save(out.with_suffix(".sheet.jpg"), quality=85)
    return out


if __name__ == "__main__":
    print("made", run(json.loads(Path(sys.argv[1]).read_text()), "--sheet" in sys.argv))
