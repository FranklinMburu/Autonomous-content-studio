"""The winners-vs-baseline dataset and its statistics (research Phase 1, docs/clips/RESEARCH.md section 6).

1. collect  - YouTube Data API v3 (official, free quota of 10,000 units/day; this uses about 1 unit per 50 videos):
              for each clip channel, its uploads from the last N days -> views, age, views/day, duration, title.
              Within each channel the top quartile by views/day are "winners", the bottom quartile "baseline"
              (same channel = same audience size, so the comparison is fair). Needs YOUTUBE_API_KEY (a free key in the
              studio's Google Cloud project; stored only as a GitHub secret).
2. features - title features from the metadata; picture/sound features (measure.py) ONLY for clip files we are
              allowed to have (Franklin's own saved references, or files from an approved, permitted route).
              YouTube's terms forbid downloading videos without YouTube's permission, so the collector never
              downloads anything.
3. stats    - per feature: winners vs baseline effect size (Cliff's delta) and the views/day ratio with a
              bootstrap 95% CI. Correlation only: a feature that separates winners is a hypothesis to test, not a cause.

    python -m studio.clips.dataset collect channels.txt --days 90 --out docs/clips/dataset.csv
    python -m studio.clips.dataset stats docs/clips/dataset.csv
"""
import csv, json, math, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://www.googleapis.com/youtube/v3/"


def _get(path, **params):
    params["key"] = os.environ["YOUTUBE_API_KEY"]   # read from the environment only; never printed or logged
    with urllib.request.urlopen(API + path + "?" + urllib.parse.urlencode(params), timeout=30) as r:
        return json.loads(r.read())


def iso_seconds(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return None
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


def collect(channels, days=90, now=None, get=_get):
    """channels: channel IDs (UC...) or @handles. Returns rows for every upload <= 180 s from the last `days` days."""
    now = now or datetime.now(timezone.utc)
    rows = []
    for ch in channels:
        q = {"forHandle": ch} if ch.startswith("@") else {"id": ch}
        info = get("channels", part="contentDetails,snippet,statistics", **q)["items"][0]
        uploads = info["contentDetails"]["relatedPlaylists"]["uploads"]
        ids, token = [], None
        while True:
            p = get("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50, **({"pageToken": token} if token else {}))
            for it in p["items"]:
                pub = datetime.fromisoformat(it["contentDetails"]["videoPublishedAt"].replace("Z", "+00:00"))
                if (now - pub).days <= days:
                    ids.append(it["contentDetails"]["videoId"])
            token = p.get("nextPageToken")
            last = p["items"][-1]["contentDetails"]["videoPublishedAt"] if p["items"] else None
            if not token or (last and (now - datetime.fromisoformat(last.replace("Z", "+00:00"))).days > days):
                break
        for i in range(0, len(ids), 50):
            v = get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
            for it in v["items"]:
                dur = iso_seconds(it["contentDetails"]["duration"])
                if dur is None or dur > 180:
                    continue
                pub = datetime.fromisoformat(it["snippet"]["publishedAt"].replace("Z", "+00:00"))
                age = max((now - pub).total_seconds() / 86400, 1.0)
                views = int(it["statistics"].get("viewCount", 0))
                rows.append({"channel": info["snippet"]["title"], "video_id": it["id"], "title": it["snippet"]["title"],
                             "published": it["snippet"]["publishedAt"], "age_days": round(age, 1), "views": views,
                             "views_per_day": round(views / age, 1), "duration_s": dur,
                             "likes": int(it["statistics"].get("likesCount", it["statistics"].get("likeCount", 0)) or 0),
                             "comments": int(it["statistics"].get("commentCount", 0) or 0)})
    return label(rows)


def label(rows, q=0.25, min_age=3):
    """Winners / baseline per channel: top and bottom quartile of views per day (videos at least min_age days old)."""
    by = {}
    for r in rows:
        if r["age_days"] >= min_age:
            by.setdefault(r["channel"], []).append(r)
    for ch, rs in by.items():
        rs.sort(key=lambda r: r["views_per_day"])
        k = max(1, int(len(rs) * q))
        for r in rs[:k]:
            r["group"] = "baseline"
        for r in rs[-k:]:
            r["group"] = "winner"
    for r in rows:
        r.setdefault("group", "middle")
        r.update(title_features(r["title"]))
    return rows


def title_features(t):
    words = t.split()
    return {"t_words": len(words), "t_has_number": int(bool(re.search(r"\d", t))),
            "t_has_question": int("?" in t), "t_has_emoji": int(bool(re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t))),
            "t_caps_share": round(sum(w.isupper() and len(w) > 1 for w in words) / max(len(words), 1), 2),
            "t_has_quote": int('"' in t or "“" in t), "t_hashtags": t.count("#")}


def cliffs_delta(a, b):
    if not a or not b:
        return None
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    return (gt - lt) / (len(a) * len(b))


def bootstrap_ratio(with_x, without_x, n=2000, seed=0):
    """Median views/day with the feature / without it, with a 95% bootstrap CI."""
    import random
    rnd = random.Random(seed)
    med = lambda v: sorted(v)[len(v) // 2]  # noqa: E731
    if len(with_x) < 3 or len(without_x) < 3:
        return None, None, None
    est = med(with_x) / max(med(without_x), 1e-9)
    bs = sorted(med([rnd.choice(with_x) for _ in with_x]) / max(med([rnd.choice(without_x) for _ in without_x]), 1e-9)
                for _ in range(n))
    return round(est, 2), round(bs[int(0.025 * n)], 2), round(bs[int(0.975 * n)], 2)


def stats(rows, features=None):
    rows = [r for r in rows if r.get("group") in ("winner", "baseline")]
    features = features or [k for k in rows[0] if k.startswith(("t_", "m_"))] if rows else []
    out = []
    for f in features:
        win = [float(r[f]) for r in rows if r["group"] == "winner" and r.get(f) not in (None, "")]
        base = [float(r[f]) for r in rows if r["group"] == "baseline" and r.get(f) not in (None, "")]
        d = cliffs_delta(win, base)
        vals = {float(r[f]) for r in rows if r.get(f) not in (None, "")}
        ratio = (None, None, None)
        if vals <= {0.0, 1.0}:
            ratio = bootstrap_ratio([float(r["views_per_day"]) for r in rows if str(r.get(f)) in ("1", "1.0")],
                                    [float(r["views_per_day"]) for r in rows if str(r.get(f)) in ("0", "0.0")])
        out.append({"feature": f, "n_winner": len(win), "n_baseline": len(base), "cliffs_delta": None if d is None else round(d, 2),
                    "winner_median": sorted(win)[len(win) // 2] if win else None,
                    "baseline_median": sorted(base)[len(base) // 2] if base else None,
                    "vpd_ratio": ratio[0], "ci95": [ratio[1], ratio[2]]})
    return sorted(out, key=lambda x: -abs(x["cliffs_delta"] or 0))


def main(argv):
    if argv[:1] == ["collect"]:
        if "YOUTUBE_API_KEY" not in os.environ:
            raise SystemExit("needs YOUTUBE_API_KEY (a GitHub secret; see docs/clips/QUESTIONS_FOR_FRANKLIN.md)")
        chans = [l.strip() for l in open(argv[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
        days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 90
        out = argv[argv.index("--out") + 1] if "--out" in argv else "dataset.csv"
        rows = collect(chans, days)
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} videos from {len(chans)} channels -> {out}")
    elif argv[:1] == ["stats"]:
        rows = list(csv.DictReader(open(argv[1], encoding="utf-8")))
        print(json.dumps(stats(rows), indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
