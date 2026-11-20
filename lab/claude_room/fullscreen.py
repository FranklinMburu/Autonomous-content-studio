"""Full-screen 9:16 Short from 16:9 game footage, crop window following the subject (20 Nov 2026).

spec: {"src", "out", "segments": [{"a","b","h","keys":[[t_src, cx, y0], ...]}],
       "overlays": [{"kind":"title"|"punch","text","at","dur","y"}]}
Times in overlays are output-timeline seconds. Crop height h (source px), width h*9/16, centre x and top y
interpolated linearly between keys. Two-pass loudnorm to -14 LUFS.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
from edit import title_png, punch_png, W, H


def lerp_expr(keys, idx):
    """ffmpeg expression in t (segment-local seconds) interpolating keys[i][idx] over keys[i][0]."""
    k = keys
    if len(k) == 1:
        return str(k[0][idx])
    e = str(k[-1][idx])
    for i in range(len(k) - 2, -1, -1):
        t0, t1, v0, v1 = k[i][0], k[i + 1][0], k[i][idx], k[i + 1][idx]
        seg = f"({v0}+({v1}-{v0})*(t-{t0})/{max(t1 - t0, 1e-3)})"
        e = f"if(lt(t,{t1}),{seg},{e})"
    return f"if(lt(t,{k[0][0]}),{k[0][idx]},{e})"


def main(spec_path):
    s = json.loads(Path(spec_path).read_text())
    tmp = Path(tempfile.mkdtemp())
    sw, sh = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                      "stream=width,height", "-of", "csv=p=0", s["src"]], capture_output=True, text=True).stdout.strip().split(","))
    parts = []
    for n, g in enumerate(s["segments"]):
        h = g["h"]; w = round(h * 9 / 16 / 2) * 2
        keys = [[kk[0] - g["a"], kk[1], kk[2]] for kk in g["keys"]]
        cx = lerp_expr(keys, 1); cy = lerp_expr(keys, 2)
        x = f"max(0,min({sw - w},{cx}-{w}/2))"; y = f"max(0,min({sh - h},{cy}))"
        vf = (f"crop=w={w}:h={h}:x='{x}':y='{y}',scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6:5:5:0.0,"
              f"fps=30,format=yuv420p,setsar=1" + (("," + g["vf_extra"]) if g.get("vf_extra") else ""))
        p = tmp / f"p{n}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(g["a"]), "-to", str(g["b"]), "-i", s["src"], "-vf", vf,
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(p)], check=True)
        parts.append(p)
    lst = tmp / "l.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = tmp / "j.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    inputs, chain, last = ["-i", str(joined)], "", "[0:v]"
    for i, o in enumerate(s.get("overlays", [])):
        png = tmp / f"o{i}.png"
        if o["kind"] == "title":
            title_png(o["text"], png)
        else:
            punch_png(o["text"], png, o.get("y", 1500), o.get("size", 64))
        inputs += ["-i", str(png)]
        nxt = f"[v{i}]"
        chain += f"{last}[{i + 1}:v]overlay=0:0:enable='between(t,{o['at']},{o['at'] + o['dur']})'{nxt};"
        last = nxt
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(joined), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs]
    if chain:
        cmd += ["-filter_complex", chain.rstrip(";"), "-map", last]
    else:
        cmd += ["-map", "0:v"]
    cmd += ["-map", "0:a", "-af", ln, "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-tune", "film", "-r", "30",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", s["out"]]
    subprocess.run(cmd, check=True)
    print("made", s["out"])


if __name__ == "__main__":
    main(sys.argv[1])
