"""From chosen moments to finished, reviewed Shorts (the first real product, 13 Nov 2026).

    python lab/clips/shorts.py --vod https://www.twitch.tv/videos/2910392998 --streamer "Kai Cenat" --lane SC \
        --stream-title "JAPAN NIGHT LIFE STREAM" --moments moments.json --out shorts/

moments.json: [{"t": 4768, "title": "...", "why": "...", "score": 10}]  (t = a second inside the moment, from the judge)

For each moment:
  1. download ONLY that section in 1080p (t-75 s .. t+45 s; Twitch/Kick work from GitHub);
  2. an AI editor WATCHES the section (low-res copy with sound) and sets the exact start, payoff second and end, and
     writes the on-screen hook and the title (the reference channels' formula, the streamer named);
  3. transcribe the section (faster-whisper small, word times);
  4. the existing engine edits it (dead air out, cold open when the payoff is late, hook, word-by-word captions,
     framing cuts) and renders 1080x1920 at -14 LUFS, then runs the gates;
  5. a reviewer that did not make it WATCHES the finished Short: clipit's 7 pass/fail checks (MIT; hook, tension, real,
     share, minors, honest, layout) + our 10 scores 0-10 (docs/clips/PROMPT.md section 4);
  6. writes post.json: title, description, hashtags, predicted view band (the reviewer's guess, not a measurement),
     and the "before you post" note.
"""
import argparse, base64, json, re, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "lab" / "clips"))
import ai_pass as AI  # noqa: E402
from studio.clips import gates, layout, signals, sources  # noqa: E402
from studio.clips.__main__ import bar  # noqa: E402
from studio.clips.edit import make_clip  # noqa: E402
from studio.clips.render import render  # noqa: E402

PRE, POST = 60, 90   # 13 Nov run 1: 45 s after the moment cut off payoffs and aftermaths; 90 s keeps them

EDITOR = """You are the editor of a top streamer-clip Shorts channel (@Kick_Clippers / Clipatra style). Below is a
{dur:.0f} s piece of {streamer}'s live stream "{stream}" (low quality, with sound). The moment we want is around
{rel:.0f} s into it: "{hint}".

Watch and listen, then decide the Short:
- "peak": the second where the biggest thing happens (the hit, the shock, the punchline, the reveal).
- "start": where the setup a stranger needs begins: at most 25 s before the peak, often less. No dead air, no slow intro.
- "end": just after the reaction lands (laugh, scream, silence after the reveal). Never trail off.
- "hook": the on-screen text for the first seconds, 3-8 words, says the concrete situation with the sound off, names
  {streamer}, teases without spoiling the payoff, no emoji. Good: "Kai Cenat challenges a real sumo wrestler".
- "title": the channel formula: "The moment / No way {streamer} [REALIZED / was SHOCKED / got HUMBLED / EXPOSED] ...",
  under 90 characters, ends with 2-3 emoji like 😳😭💔. Exaggerate the framing, never invent the event.
- "kind": one of encounter, shock, humbled, drama, emotion, money, fight, funny, other.
- "hashtags": 3-5 without #, the streamer's tag first.
- "usable": false if the piece doesn't actually contain a strong moment.
Times are seconds from the start of THIS piece. Answer JSON:
{{"start": 0.0, "peak": 0.0, "end": 0.0, "hook": "", "title": "", "kind": "", "hashtags": [], "usable": true, "why": ""}}"""

CHECKS = {  # clipit (MIT) ai.py CHECKS, adapted
    "hook": "In the first 3 seconds the sound, the action or the on-screen hook makes a stranger want to know what happens. Calm setup fails.",
    "tension": "Real stakes or pull: shock, a hit, a fight, panic, a real argument or callout, someone caught out, money, a celebrity, a doubt left open. Mildly amusing fails.",
    "real": "It is really happening to real people, not a game character or a skit.",
    "share": "A 19 year old would comment on it or send it to a friend.",
    "minors": "Nobody who is or might be under 18 is shown in a sexual or body-focused way. Any doubt fails.",
    "honest": "The on-screen hook and the title match what actually happens in the video.",
    "layout": "The people and the action are visible and big enough on a phone; nothing important is cut off; captions are readable.",
}
SCORES = ["moment", "hook", "title", "framing", "captions", "audio", "pacing", "ending", "originality", "overall"]

REVIEW = """You watch YouTube Shorts all day and you review clips for a top streamer-clip channel. Someone else made this
Short. Watch the whole video (with sound) and judge it against the best clips on @Kick_Clippers and Clipatra, harshly:
a raw, chaotic clip with something real beats a tidy calm one.

Title: {title}
On-screen hook: {hook}
Words spoken: {spoken}

1. Answer each check from what you SEE and HEAR, never from what the title promises:
{checks}
2. Score 0-10 each: {scores}. "overall" = your honest chance that this reaches 250K+ views on a channel like
@Kick_Clippers (10 = certain, 5 = maybe 20K). Most clips are 5-7; give 9+ only to what you'd bet on.
3. "fix": the single change that would most raise "overall".
Answer JSON: {{"checks": [{{"name": "hook", "passed": true, "evidence": "one line"}}], "scores": {{"moment": 0}}, "fix": ""}}"""


def sh(*a, **k):
    return subprocess.run(a, check=True, capture_output=True, text=True, **k)


def lowres(src, dst, scale="284:160", fps=2):
    sh("ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"fps={fps},scale={scale}", "-c:v", "libx264", "-crf", "33",
       "-preset", "veryfast", "-ac", "1", "-ar", "16000", "-c:a", "aac", "-b:a", "32k", str(dst))
    return dst


def video_part(p):
    return {"inline_data": {"mime_type": "video/mp4", "data": base64.b64encode(Path(p).read_bytes()).decode()}}


def band(overall):
    return "250K+" if overall >= 9 else "50K-250K" if overall >= 8 else "10K-50K" if overall >= 6.5 else "under 10K"


def one(m, a, model, b, out):
    t = float(m["t"])
    a0 = max(0.0, t - PRE)
    d = out / f"{m['id']}"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "stream.mp4"
    log = lambda *x: print(f"[{m['id']}]", *x, flush=True)  # noqa: E731
    if not src.exists():
        t0 = time.time()
        # no --force-keyframes-at-cuts (it re-encoded the whole section: ~155 s each on 13 Nov); 30 fps is all a Short uses
        sh("yt-dlp", "-q", "--no-warnings", "-f", "bv*[height<=1080][fps<=30]+ba/bv*[height<=1080]+ba/b[height<=1080]/b",
           "--merge-output-format", "mp4", "--download-sections", f"*{a0:.0f}-{t + POST:.0f}", "-o", str(src), a.vod)
        log(f"section {a0:.0f}-{t + POST:.0f} s downloaded in {time.time() - t0:.0f} s ({src.stat().st_size / 1e6:.0f} MB)")
    dur = float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)).stdout)
    # 2. the AI editor watches the section
    low = lowres(src, d / "low.mp4")
    ed = AI.call(model, [{"text": EDITOR.format(dur=dur, streamer=a.streamer, stream=a.stream_title, rel=t - a0,
                                                hint=m.get("title", ""))}, video_part(low)]) or {}
    if isinstance(ed, list):
        ed = ed[0] if ed else {}
    if not ed or not ed.get("usable", True):
        log("editor: not usable:", ed.get("why") if ed else "no answer")
        return None
    start, peak, end = (float(ed.get(k, v)) for k, v in (("start", t - a0 - 20), ("peak", t - a0), ("end", t - a0 + 10)))
    peak = min(max(peak, 2.0), dur - 2.0)                       # the editor's peak can fall outside the piece (13 Nov)
    if end <= start or end <= peak:                             # an end before the start/peak = a bad answer: rebuild it
        end = peak + 6
    start, end = max(0, min(start, peak - 2)), min(dur - 0.5, max(end, peak + 2))
    if end - start > b["duration_s"]["max"] + 15:
        start = max(start, peak - 25)
    log(f"editor: start {start:.1f} peak {peak:.1f} end {end:.1f} | {ed.get('hook')!r} | {ed.get('title')!r}")
    # 3. words
    words_p = d / "words.json"
    if not words_p.exists():
        from studio.clips.transcribe import transcribe
        transcribe(src, words_p, model="small.en", log=log)
    (d / "rights.json").write_text(json.dumps({"source": "unverified", "streamer": a.streamer, "title": a.stream_title,
                                               "vod": a.vod, "note": "Rights not checked yet: see the before-you-post note."}))
    # 4. edit, render, gates
    S = sources.load(d)
    cv, _ = signals.curves(S, dur, log=lambda *x: None)
    lay = layout.choose(S["video"], start, end)
    cand = {"start": start, "end": end, "peak": peak, "hook": ed.get("hook") or m.get("title", ""), "title": ed.get("title") or m.get("title", ""),
            "why": ed.get("why", ""), "kind": ed.get("kind", "other"), "score": m.get("score", 0), "score_ai": m.get("score", 0),
            "ranked_by": "AI judge (watched)", "signals": {}}
    clip = make_clip(cand, S, S["words"], cv, b, lay, a.stream_title)
    (d / "clip.json").write_text(json.dumps(clip, indent=1, ensure_ascii=False))
    video = render(clip, d / "short.mp4", log=lambda *x: None)
    rep = gates.check(clip, video, S["words"], b)
    failed = [k for k, v in rep["gates"].items() if not v]
    log(f"rendered {clip['duration']:.1f} s, layout {lay['kind']}; gates: {'all passed' if not failed else 'REVIEW ' + ', '.join(failed)}")
    # 5. the reviewer watches the finished Short
    small = lowres(video, d / "short_low.mp4", scale="360:640", fps=2)
    spoken = clip.get("transcript", "")[:1500]
    rv = AI.call(model, [{"text": REVIEW.format(title=clip["title"], hook=clip["hook"]["text"], spoken=spoken,
                                                checks="\n".join(f"- {k}: {v}" for k, v in CHECKS.items()),
                                                scores=", ".join(SCORES))}, video_part(small)]) or {}
    if isinstance(rv, list):
        rv = rv[0] if rv else {}
    checks = {c.get("name"): bool(c.get("passed") is True) for c in rv.get("checks", []) if isinstance(c, dict)}
    passed = [k for k in CHECKS if checks.get(k)]
    sc = {k: float((rv.get("scores") or {}).get(k, 0) or 0) for k in SCORES}
    log(f"review: {len(passed)}/{len(CHECKS)} checks; overall {sc['overall']}; fix: {rv.get('fix', '')[:120]}")
    # 6. the post package
    tags = [re.sub(r"[^A-Za-z0-9_]", "", h) for h in (ed.get("hashtags") or [])][:5] or [a.streamer.replace(" ", "").lower()]
    post = {
        "id": m["id"], "title": clip["title"], "hook": clip["hook"]["text"],
        "description": f"{clip['title']}\n\nFrom {a.streamer}'s stream \"{a.stream_title}\".\n" + " ".join(f"#{h}" for h in tags + ["shorts"]),
        "hashtags": tags, "duration_s": round(clip["duration"], 1), "layout": lay["kind"],
        "gates_failed": failed, "checks": rv.get("checks", []), "checks_passed": f"{len(passed)}/{len(CHECKS)}",
        "scores": sc, "fix": rv.get("fix", ""), "predicted_views": band(sc["overall"]),
        "before_you_post": (f"Rights NOT verified: this is {a.streamer}'s stream ({a.vod}). Check whether {a.streamer} runs a "
                            "clipping program or campaign, and its rules, before posting. The predicted views are the "
                            "reviewer's guess, not a measurement. " + ("Checks failed: " + ", ".join(k for k in CHECKS if k not in passed) + ". " if len(passed) < len(CHECKS) else "")
                            + ("Gates failed: " + ", ".join(failed) + "." if failed else "")),
        "source": {"vod": a.vod, "start": round(a0 + start, 1), "peak": round(a0 + peak, 1), "end": round(a0 + end, 1)},
        "editor": ed,
    }
    (d / "post.json").write_text(json.dumps(post, indent=1, ensure_ascii=False))
    for junk in (src, low, small):
        junk.unlink(missing_ok=True)
    return post


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vod", required=True); ap.add_argument("--streamer", required=True); ap.add_argument("--lane", default="SC")
    ap.add_argument("--stream-title", default=""); ap.add_argument("--moments", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--model"); ap.add_argument("--only", type=int, help="make only moment number N (1-based): one job per Short")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    b = bar()
    model = a.model or AI.pick_model()
    ms = json.loads(Path(a.moments).read_text())
    day = time.strftime("%Y%m%d")
    posts = []
    for i, m in enumerate(ms, 1):
        m["id"] = m.get("id") or f"{a.lane}-{day}-{i:02d}"
        if a.only and i != a.only:
            continue
        try:
            p = one(m, a, model, b, out)
            if p:
                posts.append(p)
        except Exception as e:  # noqa: BLE001  one bad moment must not stop the others
            print(f"[{m['id']}] FAILED: {type(e).__name__}: {str(e)[-300:]}", flush=True)
    (out / "posts.json").write_text(json.dumps(posts, indent=1, ensure_ascii=False))
    print("\n== SHORTS")
    for p in sorted(posts, key=lambda p: -p["scores"]["overall"]):
        print(f"{p['id']}  overall {p['scores']['overall']:.1f}  checks {p['checks_passed']}  {p['duration_s']} s  {p['layout']}  "
              f"band {p['predicted_views']}\n   {p['title']}\n   hook: {p['hook']}\n   scores: "
              + " ".join(f"{k} {v:g}" for k, v in p["scores"].items()) + f"\n   fix: {p['fix'][:160]}")


if __name__ == "__main__":
    main()
