"""Raw-footage fetcher for hand-made Claude clips (19 Nov 2026, Franklin: "don't use my pipeline, use Claude fully").
No AI here: it only finds where fans clipped a stream (proof of demand), downloads ~2 min of 1080p around each moment
and writes a word-level transcript. Claude picks, cuts and edits in its own workspace.

  python fetch.py twitch --vod https://www.twitch.tv/videos/<id> --channel kaicenat --from-s 0 --to-s 14400 --top 14 --out out
  python fetch.py kick --slug n3on --uuid <vod uuid> --top 8 --out out
"""
import argparse, datetime as dt, json, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read())


def ytj(u):
    return json.loads(subprocess.run(["yt-dlp", "-J", "--skip-download", u], capture_output=True, text=True).stdout or "{}")


def ts(s):
    s = s.replace(" ", "T").replace("Z", "+00:00")
    d = dt.datetime.fromisoformat(s)
    return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).timestamp()


def twitch_clips(a):
    v = ytj(a.vod); t0, dur = v["timestamp"], v["duration"]
    urls = subprocess.run(["yt-dlp", "--flat-playlist", "--playlist-end", "150", "--print", "%(url)s",
                           f"https://www.twitch.tv/{a.channel}/clips?filter=clips&range=7d"], capture_output=True, text=True).stdout.split()
    with ThreadPoolExecutor(12) as ex:
        ds = list(ex.map(ytj, urls))
    out = []
    for u, d in zip(urls, ds):
        if d.get("timestamp") and t0 <= d["timestamp"] <= t0 + dur + 600:
            out.append({"views": d.get("view_count") or 0, "off": d["timestamp"] - t0 - (d.get("duration") or 30),
                        "len": d.get("duration") or 30, "title": d.get("title") or "", "url": u})
    return {"source": a.vod, "page": a.vod, "title": v.get("title"), "fmt": "1080p60/1080p/best"}, out


def kick_clips(a):
    vids = get(f"https://kick.com/api/v2/channels/{a.slug}/videos")
    v = next(x for x in vids if a.uuid in json.dumps(x))
    t0, dur = ts(v["start_time"]), v["duration"] / 1000
    raw = []
    for rng in ("day", "week"):
        try:
            d = get(f"https://kick.com/api/v2/channels/{a.slug}/clips?sort=view&time={rng}")
            raw += d.get("clips", d) if isinstance(d, dict) else d
        except Exception as e:
            print("kick clips", rng, e)
    if raw:
        print("kick clip keys:", sorted(raw[0].keys()))
    seen, out = set(), []
    for c in raw:
        if c.get("id") in seen:
            continue
        seen.add(c.get("id"))
        created = c.get("created_at") or c.get("started_at")
        if not created:
            continue
        ln = float(c.get("duration") or 30)
        vsa = c.get("vod_starts_at")             # Kick returns 0 here (19 Nov): fall back to creation time minus length
        off = float(vsa) if isinstance(vsa, (int, float)) and vsa > 0 else ts(created) - t0 - ln
        if 0 <= off <= dur and str(c.get("livestream_id", v.get("id"))) == str(v.get("id")):
            out.append({"views": c.get("view_count") or c.get("views") or 0, "off": off, "len": ln,
                        "title": c.get("title") or "", "url": c.get("clip_url") or c.get("video_url") or ""})
    return {"source": v["source"], "page": f"https://kick.com/{a.slug}/videos/{a.uuid}", "title": v.get("session_title"),
            "fmt": "b[height<=1080]/b"}, out


def moments(clips, lo, hi, top):
    clips = sorted([c for c in clips if lo <= c["off"] <= hi], key=lambda c: -c["views"])
    ms = []
    for c in clips:                                  # fans clip the same moment many times: merge within 60 s
        m = next((m for m in ms if abs(m["off"] - c["off"]) < 60), None)
        if m:
            m["views"] += c["views"]; m["fan_titles"].append(f'{c["views"]}: {c["title"]}')
            m["a"] = min(m["a"], c["off"]); m["b"] = max(m["b"], c["off"] + c["len"])
        else:
            ms.append({"off": c["off"], "a": c["off"], "b": c["off"] + c["len"], "views": c["views"],
                       "fan_titles": [f'{c["views"]}: {c["title"]}'], "fan_clip": c["url"]})
    ms.sort(key=lambda m: -m["views"])
    return ms[:top]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("platform"); ap.add_argument("--vod"); ap.add_argument("--channel")
    ap.add_argument("--slug"); ap.add_argument("--uuid"); ap.add_argument("--from-s", type=float, default=0)
    ap.add_argument("--to-s", type=float, default=1e9); ap.add_argument("--top", type=int, default=10); ap.add_argument("--out", default="out")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    src, clips = twitch_clips(a) if a.platform == "twitch" else kick_clips(a)
    print(f"{len(clips)} fan clips in the stream")
    ms = moments(clips, a.from_s, a.to_s, a.top)
    from faster_whisper import WhisperModel
    wm = WhisperModel("small.en", device="cpu", compute_type="int8")
    for i, m in enumerate(ms, 1):
        s0, s1 = max(0, m["a"] - 50), m["b"] + 40
        s1 = min(s1, s0 + 160)
        name = f"{a.channel or a.slug}-{i:02d}"
        f = out / f"{name}.mp4"
        subprocess.run(["yt-dlp", "-q", "--no-warnings", "-N", "8", "-f", src["fmt"], "--download-sections", f"*{s0:.0f}-{s1:.0f}",
                        "--force-keyframes-at-cuts", "-o", str(out / f"{name}.raw.mp4"), src["source"]])
        raw = out / f"{name}.raw.mp4"
        if not raw.exists():
            print("FAILED download", name); continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", "fps=30", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "20", "-c:a", "aac", "-b:a", "160k", str(f)]); raw.unlink()
        import numpy as np                       # decode with ffmpeg (19 Nov: faster-whisper's own decoder broke on a new PyAV)
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
        segs, _ = wm.transcribe(np.frombuffer(pcm, np.int16).astype(np.float32) / 32768, word_timestamps=True, vad_filter=True)
        words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for sg in segs for w in (sg.words or [])]
        meta = {**m, "file": f.name, "section_start_in_vod": round(s0, 1), "section_end_in_vod": round(s1, 1),
                "fan_moment_in_section": round(m["a"] - s0, 1), "vod_page": src["page"], "stream_title": src["title"],
                "streamer_channel": a.channel or a.slug, "words": words}
        (out / f"{name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        print(f"OK {name} {m['views']} views @{m['off']/3600:.2f}h  {m['fan_titles'][0][:70]}  ({f.stat().st_size>>20} MB, {len(words)} words)")


if __name__ == "__main__":
    main()
