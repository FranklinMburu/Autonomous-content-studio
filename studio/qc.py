"""Stage: quality check. Technical checks run automatically; the editorial checks are listed for a human.

A video passing these checks is *technically* fine. Whether it's *worth watching* is the human's call,
using the quality bar at the bottom of the report.
"""
import json, re, subprocess
from pathlib import Path

QUALITY_BAR = [
    "Hook in the first ~2 seconds makes you want the answer",
    "Every factual claim is backed by a source (see fact check)",
    "Each visual matches what is being said at that moment",
    "Narration sounds natural and well paced",
    "Captions are in sync with the voice",
    "There is a real payoff at the end",
    "It does not look mass-produced or repetitive",
    "You would watch it to the end",
]


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def technical(video):
    v = str(video)
    res = {}
    pr = _run(["ffprobe", "-v", "error", "-show_entries",
               "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate:format=duration",
               "-of", "json", v])
    info = json.loads(pr.stdout or "{}")
    streams = info.get("streams", [])
    vs = next((s for s in streams if s.get("codec_type") == "video"), {})
    a = next((s for s in streams if s.get("codec_type") == "audio"), {})
    dur = float(info.get("format", {}).get("duration", 0))
    res["duration_s"] = round(dur, 2)
    res["video"] = f"{vs.get('codec_name')} {vs.get('width')}x{vs.get('height')} {vs.get('r_frame_rate')}"
    res["audio"] = f"{a.get('codec_name')} {a.get('sample_rate')} Hz"
    sil = _run(["ffmpeg", "-nostats", "-i", v, "-af", "silencedetect=n=-40dB:d=1.0", "-f", "null", "-"]).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", sil)]
    res["mid_silences"] = [round(s, 1) for s in starts if s < dur - 1.2]
    blk = _run(["ffmpeg", "-nostats", "-i", v, "-vf", "blackdetect=d=0.3:pix_th=0.05", "-an", "-f", "null", "-"]).stderr
    res["black_segments"] = len(re.findall(r"black_start", blk))
    lou = _run(["ffmpeg", "-nostats", "-i", v, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lou)
    res["loudness_lufs"] = float(m[-1]) if m else None
    err = _run(["ffmpeg", "-v", "error", "-i", v, "-f", "null", "-"]).stderr.strip()
    res["decode_errors"] = len(err.splitlines()) if err else 0
    checks = {
        "vertical 1080x1920": vs.get("width") == 1080 and vs.get("height") == 1920,
        "has audio": bool(a),
        "length 20-60 s (Shorts)": 20 <= dur <= 60,
        "no silence gaps over 1 s": not res["mid_silences"],
        "no black segments": res["black_segments"] == 0,
        "loudness near -14 LUFS": res["loudness_lufs"] is not None and abs(res["loudness_lufs"] + 14) <= 2,
        "no decode errors": res["decode_errors"] == 0,
    }
    res["checks"] = checks
    res["passed"] = all(checks.values())
    return res


def contact_sheet(video, out_png, every=2.5):
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf",
          f"fps=1/{every},scale=216:384,tile=10x2:padding=6:color=white", "-frames:v", "1", str(out_png)])
    return out_png


def report(folder, script, tech, fact=None, warnings=()):
    folder = Path(folder)
    lines = [f"# {script.get('title')}", ""]
    status = "READY FOR REVIEW" if tech["passed"] and not (fact and fact.get("problems")) else "NEEDS ATTENTION"
    lines += [f"**Status:** {status}", ""]
    lines += ["## Technical checks (automatic)", ""]
    for k, ok in tech["checks"].items():
        lines.append(f"- {'✅' if ok else '❌'} {k}")
    lines += ["", f"Duration {tech['duration_s']} s · {tech['video']} · {tech['audio']} · "
                  f"loudness {tech['loudness_lufs']} LUFS", ""]
    if fact is not None:
        lines += ["## Fact check (automatic, verify anything flagged)", ""]
        for r in fact.get("results", []):
            icon = {"supported": "✅", "partial": "⚠️"}.get(r.get("verdict"), "❌")
            lines.append(f"- {icon} **{r.get('verdict')}**: {r.get('claim')}  \n  {r.get('url')}"
                         + (f"  \n  evidence: “{r['evidence']}”" if r.get("evidence") else "")
                         + (f"  \n  note: {r['note']}" if r.get("note") else ""))
        lines.append("")
    if warnings:
        lines += ["## Script warnings", ""] + [f"- {w}" for w in warnings] + [""]
    lines += ["## Your review: the quality bar", "", "Watch it once with sound, then tick:", ""]
    lines += [f"- [ ] {q}" for q in QUALITY_BAR]
    yt = script.get("youtube", {})
    if yt:
        lines += ["", "## Upload details", "", f"**Title:** {yt.get('title', script.get('title'))}", "",
                  f"**Description:**", "", yt.get("description", ""), ""]
        if script.get("sources"):
            lines += ["Sources:"] + [f"- {s['url']}" for s in script["sources"]] + [""]
        lines += [f"**Tags:** {', '.join(yt.get('tags', []))}", ""]
        lines += ["YouTube asks you to disclose realistic altered or synthetic media. These are clearly "
                  "animated explainers with a synthetic voice; check the current guidance when uploading.", ""]
    (folder / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return status
