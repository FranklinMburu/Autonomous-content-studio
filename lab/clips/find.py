"""Find the best moments of a fresh stream (no answer key): the recall-tested chain, pointed at a new stream.

    python lab/clips/find.py resolve --platform kick --slug n3on [--uuid 01a1d1db-...] --out stream.json
    python lab/clips/find.py resolve --platform twitch --url https://www.twitch.tv/videos/2924282282 --out stream.json
    python lab/clips/find.py subs --stream stream.json --out words.json      # Kick's own free subtitles -> word times
    python lab/clips/find.py pick --judged judged.json --top 12 --out moments.json

stream.json has the same shape as an answer key with no clips ({"vod": {...}, "key": []}), so recall.py runs on it
unchanged: its signal families + AI eyes give the candidates (--cands-out), ai_pass.py judge watches each one, and
`pick` keeps the judge's best, at least --gap seconds apart, as the moments file for shorts.py.
"""
import argparse, datetime as dt, json, re, subprocess, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}
GAMBLING = ("slots", "casino", "gambl", "stake.com", "jack.com", "roobet", "rollbit", "jackpot", "bonus buy", "poker", "blackjack", "roulette")


def get(u, raw=False):
    err = None
    for _ in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()
            return b.decode("utf-8", "replace") if raw else json.loads(b)
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(3)
    raise err


def resolve(a):
    if a.platform == "kick":
        vods = []
        for page in range(1, 4):
            d = get(f"https://kick.com/api/v2/channels/{a.slug}/videos?page={page}")
            d = d if isinstance(d, list) else d.get("data", d)
            if not d:
                break
            vods += d
        if not vods:
            sys.exit(f"no Kick VODs for {a.slug}")
        uniq = {}
        for v in vods:                       # Kick ignores ?page= (13 Nov: the same VODs came back on every page)
            uniq.setdefault((v.get("video") or {}).get("uuid") or v.get("id"), v)
        vods = sorted(uniq.values(), key=lambda v: v.get("start_time") or "", reverse=True)

        def cats(v):
            return ", ".join(c.get("name", "") for c in (v.get("categories") or []) if isinstance(c, dict))

        def why_not(v):                      # 13 Nov: "newest" picked a 1.4 h casino-sponsored slots stream
            text = f"{v.get('session_title') or ''} {cats(v)}".lower()
            if any(w in text for w in GAMBLING):
                return "gambling"
            if v["duration"] / 3.6e6 < a.min_hours:
                return f"shorter than {a.min_hours} h"
            return ""
        for v in vods[:8]:
            print(f"  VOD {v.get('start_time')} {v['duration']/3.6e6:.1f} h  {(v.get('video') or {}).get('uuid')}  "
                  f"{(v.get('session_title') or '')[:50]!r} [{cats(v)}] {why_not(v) and 'SKIP: ' + why_not(v)}")
        if a.uuid:
            v = next((v for v in vods if a.uuid in json.dumps(v)), None)
        else:
            v = next((v for v in vods if not why_not(v)), None)
            if not v:
                sys.exit(f"no recent {a.slug} VOD passes the niche filter (no gambling, at least {a.min_hours} h)")
        if not v:
            sys.exit(f"VOD {a.uuid} not in {a.slug}'s list ({len(vods)} VODs)")
        uuid = a.uuid or (v.get("video") or {}).get("uuid") or ""
        start = v["start_time"].replace(" ", "T")
        start = start if ("Z" in start or "+" in start) else start + "Z"
        vod = {"platform": "kick", "slug": a.slug, "id": v["id"], "source": v.get("source"), "start": start,
               "duration": v["duration"] / 1000, "title": v.get("session_title") or "",
               "page": f"https://kick.com/{a.slug}/videos/{uuid}" if uuid else f"https://kick.com/{a.slug}"}
    else:
        d = json.loads(subprocess.run(["yt-dlp", "-J", "--skip-download", a.url], capture_output=True, text=True).stdout)
        vod = {"platform": "twitch", "id": d["id"], "source": a.url, "start": d.get("timestamp"), "duration": d["duration"],
               "title": d.get("title") or "", "page": a.url}
    Path(a.out).write_text(json.dumps({"vod": vod, "key": []}, indent=1))
    print(f"stream: {vod['title'][:80]!r} {vod['duration']/3600:.2f} h, started {vod['start']}\n  page {vod['page']}")


def vtt_cues(text):
    out = []
    for m in re.finditer(r"(\d+:)?(\d+):(\d+\.\d+)\s+-->\s+(\d+:)?(\d+):(\d+\.\d+)[^\n]*\n(.+?)(?:\n\n|\Z)", text, re.S):
        h1, m1, s1, h2, m2, s2, body = m.groups()
        t1 = int((h1 or "0:")[:-1]) * 3600 + int(m1) * 60 + float(s1)
        t2 = int((h2 or "0:")[:-1]) * 3600 + int(m2) * 60 + float(s2)
        body = re.sub(r"<[^>]+>", "", body).strip()
        if body:
            out.append((t1, t2, body))
    return out


def subs(a):
    """Kick VODs carry auto subtitles in the HLS master playlist. Each cue's words get evenly spread times (good enough
    for the speech-cue signal and the judge's 'what was said'; shorts.py re-transcribes each section with Whisper)."""
    vod = json.loads(Path(a.stream).read_text())["vod"]
    master = get(vod["source"], raw=True)
    tracks = [dict(re.findall(r'([A-Z-]+)="?([^",]*)"?', ln)) for ln in master.splitlines() if ln.startswith("#EXT-X-MEDIA:TYPE=SUBTITLES")]
    print("subtitle tracks:", [(t.get("LANGUAGE"), t.get("NAME")) for t in tracks])
    tr = next((t for t in tracks if (t.get("LANGUAGE") or "").startswith("en")), None)
    if not tr:
        sys.exit("no English subtitles in this stream's playlist")
    pl_url = urllib.parse.urljoin(vod["source"], tr["URI"])
    segs = [urllib.parse.urljoin(pl_url, ln.strip()) for ln in get(pl_url, raw=True).splitlines() if ln.strip() and not ln.startswith("#")]
    with ThreadPoolExecutor(16) as ex:
        texts = list(ex.map(lambda u: get(u, raw=True), segs))
    cues, seen = [], set()
    for t in texts:
        for c in vtt_cues(t):
            if (round(c[0], 1), c[2]) not in seen:
                seen.add((round(c[0], 1), c[2]))
                cues.append(c)
    cues.sort()
    words = []
    for t1, t2, body in cues:
        ws = body.split()
        step = max(0.05, (t2 - t1) / max(1, len(ws)))
        words += [{"w": w, "start": round(t1 + i * step, 2), "end": round(t1 + (i + 1) * step, 2)} for i, w in enumerate(ws)]
    if len(words) < 200:
        sys.exit(f"subtitles too thin ({len(words)} words): use Whisper")
    Path(a.out).write_text(json.dumps({"words": words, "language": "en", "from": "kick subtitles"}))
    print(f"subtitles: {len(segs)} files, {len(cues)} cues, {len(words)} words, last at {words[-1]['start']/3600:.2f} h")


STOP = set("the a an and of on in at to his her after was got by with for moment n3on kai cenat shocked realized humbled exposed no way live stream".split())


def same_story(t1, t2):
    """13 Nov: three of twelve picks were the same 'won an award' moment. Titles sharing most of their content words
    tell the same story: keep only the best one."""
    w = lambda t: {x.rstrip("s") for x in re.findall(r"[a-z0-9$]+", t.lower()) if x not in STOP and len(x) > 2}  # noqa: E731
    a_, b_ = w(t1), w(t2)
    return bool(a_ and b_) and len(a_ & b_) / min(len(a_), len(b_)) >= 0.5


def pick(a):
    judged = json.loads(Path(a.judged).read_text())["judged"]
    ok = []
    for m in judged:
        try:
            ok.append((float(m["score"]), float(m["t"]), m))
        except (TypeError, ValueError, KeyError):
            pass
    ok.sort(key=lambda x: (-x[0], x[1]))
    keep = []
    for sc, t, m in ok:
        if sc < a.min_score or len(keep) >= a.top:
            break
        if all(abs(t - k["t"]) >= a.gap for k in keep) and not any(same_story(m.get("title") or "", k["title"]) for k in keep):
            keep.append({"t": int(t), "title": m.get("title") or "", "why": f"judge {m.get('score_alone', sc)}; {m.get('kind') or ''}: {(m.get('why') or '')[:200]}",
                         "score": round(sc, 2)})
    Path(a.out).write_text(json.dumps(keep, indent=1, ensure_ascii=False))
    print(f"moments chosen: {len(keep)}")
    for k in keep:
        print(f"  [{k['score']:>5}] @{k['t']//3600}:{k['t']%3600//60:02d}:{k['t']%60:02d}  {k['title']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve"); r.add_argument("--platform", choices=("kick", "twitch"), required=True)
    r.add_argument("--slug"); r.add_argument("--uuid"); r.add_argument("--url"); r.add_argument("--min-hours", type=float, default=1.5); r.add_argument("--out", required=True)
    s = sub.add_parser("subs"); s.add_argument("--stream", required=True); s.add_argument("--out", required=True)
    p = sub.add_parser("pick"); p.add_argument("--judged", required=True); p.add_argument("--out", required=True)
    p.add_argument("--top", type=int, default=12); p.add_argument("--gap", type=float, default=60); p.add_argument("--min-score", type=float, default=0)
    a = ap.parse_args()
    {"resolve": resolve, "subs": subs, "pick": pick}[a.cmd](a)


if __name__ == "__main__":
    main()
