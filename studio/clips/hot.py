"""Who and what to clip today. Two lanes, real numbers only, every pick with its evidence.

    python -m studio.clips.hot streamers [--out hot_streamers.json]
    python -m studio.clips.hot world     [--out hot_world.json]

STREAMERS lane. Four signals per streamer, then our niche filter:
  1. what the winning clip channels (REF_CHANNELS) posted in the last days and how fast it's getting views
     (views per hour since upload: the strongest sign of what works on YouTube right now);
  2. the views on their Kick clips of the last 24 h (clipit's signal);
  3. a fresh event: a LivestreamFail.tv clip of today;
  4. they streamed in the last 48 h, so there is something new to clip (latest VOD link given).
  Filter: English, IRL / just chatting / reactions; no slots or casino, no roleplay.

WORLD lane. What the whole world is searching and reading today, then the long videos to clip it from:
  trends from Google Trends (daily RSS, US + UK) and Wikipedia's most-read pages; for each, YouTube's long videos of
  the last days (interviews, podcasts, hearings, press conferences) ranked by views per hour.

Read-only public sources, no keys. Every network call is allowed to fail: a lane still reports what it got.
"""
import argparse, collections, datetime as dt, html, json, re, subprocess, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "third_party"))

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
NOW = dt.datetime.now(dt.timezone.utc)

REF_CHANNELS = {  # the bar (docs/clips/DECISIONS.md); more can be added as we find them
    "Kick_Clippers": "UCIPD8q8n3Vy7Qfz59RTc1Jg",
    "Clipatra": "UCxlQSBBswmNP-wFDkcFrDBw",
}
# streamers our audience follows: name used in titles -> (site, login). Names found in reference titles are matched to it.
ROSTER = {
    "kai cenat": ("twitch", "kaicenat"), "kai": ("twitch", "kaicenat"),
    "ishowspeed": ("youtube", "@IShowSpeed"), "speed": ("youtube", "@IShowSpeed"),
    "n3on": ("kick", "n3on"), "adin ross": ("kick", "adinross"), "adin": ("kick", "adinross"),
    "ddg": ("kick", "ddg"), "blueface": ("kick", "blueface"), "deshae": ("kick", "deshaefrost"),
    "deshae frost": ("kick", "deshaefrost"), "jack doherty": ("kick", "jackdoherty"), "sneako": ("kick", "sneako"),
    "jay cinco": ("kick", "jaycinco"), "duke dennis": ("twitch", "dukedennis"), "fanum": ("twitch", "fanum"),
    "agent 00": ("twitch", "agent00"), "cuffem": ("kick", "cuffem"), "druski": ("youtube", "@Druski"),
    "plaqueboymax": ("twitch", "plaqueboymax"), "lacy": ("twitch", "lacy"), "xqc": ("kick", "xqc"),
    "dub": ("kick", "notquitelikedub"), "bendadonnn": ("kick", "bendadonnn"), "clavicular": ("kick", "clavicular"),
}
BAD_CATEGORY = re.compile(r"slots|casino|gambl|roleplay|\brp\b|grand theft auto|gta", re.I)


def get(url, as_json=True, timeout=30):
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json" if as_json else "*/*"})
    for wait in (2, 5, 10):
        try:
            raw = urllib.request.urlopen(req, timeout=timeout).read()
            return json.loads(raw) if as_json else raw.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001  one source failing must not stop the lane
            err = e
            time.sleep(wait)
    print(f"  ! {url[:90]}: {err}", file=sys.stderr)
    return None


def ytdlp_json(args, timeout=600):
    r = subprocess.run(["yt-dlp", "-q", "--no-warnings", *args], capture_output=True, text=True, timeout=timeout)
    out = []
    for line in r.stdout.splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def hours_since(ts):
    return max(1.0, (NOW.timestamp() - ts) / 3600) if ts else None


# ---------------------------------------------------------------- streamers lane
def ref_uploads(days=7, n=60):
    """Newest Shorts of each reference channel with views per hour (full metadata, so upload time is known)."""
    out = []
    for name, cid in REF_CHANNELS.items():
        for e in ytdlp_json(["--playlist-end", str(n), "--skip-download", "-j", f"https://www.youtube.com/channel/{cid}/shorts"]):
            ts = e.get("timestamp") or (dt.datetime.strptime(e["upload_date"], "%Y%m%d").replace(tzinfo=dt.timezone.utc).timestamp() if e.get("upload_date") else None)
            h = hours_since(ts)
            if h and h <= days * 24:
                out.append({"channel": name, "title": e.get("title", ""), "views": e.get("view_count") or 0, "hours": round(h, 1),
                            "vph": round((e.get("view_count") or 0) / h, 1), "url": e.get("webpage_url")})
    return out


def names_in(title):
    t = " " + re.sub(r"[^a-z0-9 ]", " ", title.lower()) + " "
    found = {ROSTER[k] for k in sorted(ROSTER, key=len, reverse=True) if f" {k} " in t}
    return found


def kick_day():
    """(slug -> clip views of the last 24 h, top clip titles, category) from Kick's clips feed."""
    from clipit import kick
    views, tops, cats, cursor = collections.Counter(), collections.defaultdict(list), {}, ""
    for _ in range(10):
        try:
            d = kick.get(f"https://kick.com/api/v2/clips?sort=view&time=day{cursor}")
        except Exception as e:  # noqa: BLE001
            print("  ! kick clips:", e, file=sys.stderr)
            break
        for c in d.get("clips") or []:
            s = ((c.get("channel") or {}).get("slug") or "").lower()
            cat = (c.get("category") or {}).get("name") or ""
            views[s] += c.get("views") or 0
            tops[s].append((c.get("views") or 0, c.get("title") or ""))
            cats[s] = cat
        if not d.get("nextCursor"):
            break
        cursor = "&cursor=" + urllib.parse.quote(d["nextCursor"])
    return views, tops, cats


def lsf_today():
    """LivestreamFail.tv's clips of today: (streamer login lowercased, title, views)."""
    page = get("https://livestreamfail.tv/clips/today", as_json=False) or ""
    out = []
    # the page embeds its clips as JSON in a Next.js data script; fall back to nothing if the format changes
    for m in re.finditer(r'"broadcaster(?:_name|Name|Login|_login)"\s*:\s*"([^"]+)".{0,400}?"title"\s*:\s*"([^"]*)".{0,400}?"view(?:_count|Count|s)"\s*:\s*(\d+)', page, re.S):
        out.append((m.group(1).lower(), html.unescape(m.group(2)), int(m.group(3))))
    return out


def latest_vod(site, login):
    try:
        if site == "kick":
            from clipit import kick
            v = kick.latest_vod(login)
            return v and {"url": f"https://kick.com/{login}/videos/{v['id']}", "when": v["publishedAt"], "hours": round(v["lengthSeconds"] / 3600, 1)}
        if site == "twitch":
            e = ytdlp_json(["--flat-playlist", "--playlist-end", "1", "-j", f"https://www.twitch.tv/{login}/videos?filter=archives&sort=time"], 120)
            return e and {"url": e[0].get("url") or e[0].get("webpage_url"), "when": e[0].get("timestamp"), "hours": round((e[0].get("duration") or 0) / 3600, 1)}
        if site == "youtube":
            e = ytdlp_json(["--flat-playlist", "--playlist-end", "1", "-j", f"https://www.youtube.com/{login}/streams"], 120)
            return e and {"url": e[0].get("url"), "when": None, "hours": round((e[0].get("duration") or 0) / 3600, 1)}
    except Exception as e:  # noqa: BLE001
        print(f"  ! latest vod {site}:{login}: {e}", file=sys.stderr)
    return None


def streamers(a):
    ref = ref_uploads()
    print(f"[streamers] {len(ref)} reference Shorts from the last 7 days")
    score = collections.defaultdict(lambda: {"ref_vph": 0.0, "ref_titles": [], "kick_views": 0, "kick_top": [], "lsf": [], "category": ""})
    for r in ref:
        for who in names_in(r["title"]):
            s = score[who]
            s["ref_vph"] += r["vph"]
            s["ref_titles"].append(f"{r['views']:,} views in {r['hours']:.0f} h: {r['title'][:90]}")
    kv, kt, kc = kick_day()
    for slug, n in kv.items():
        if BAD_CATEGORY.search(kc.get(slug, "")):
            continue
        s = score[("kick", slug)]
        s["kick_views"], s["kick_top"], s["category"] = n, [f"{v:,} {t[:70]}" for v, t in sorted(kt[slug], reverse=True)[:2]], kc.get(slug, "")
    for login, title, v in lsf_today():
        s = score.get(("twitch", login)) or score.get(("kick", login))
        if s is None:
            s = score[("twitch", login)]
        s["lsf"].append(f"{v:,} {title[:70]}")
    # one number: reference demand dominates (it is what works on YouTube), platform clips and fresh events add
    rows = []
    for (site, login), s in score.items():
        known = (site, login) in ROSTER.values()
        total = s["ref_vph"] * 1.0 + s["kick_views"] / 24 * (1.0 if known else 0.3) + sum(int(x.split()[0].replace(",", "")) for x in s["lsf"]) / 24
        if total > 0:
            rows.append({"site": site, "login": login, "score": round(total, 1), "in_our_lane": known, **s})
    rows.sort(key=lambda r: -r["score"])
    for r in rows[: a.top]:
        r["latest_vod"] = latest_vod(r["site"], r["login"])
    print(f"\n== STREAMERS LANE, top {a.top} (score = views/hour of reference Shorts + clip views/hour + fresh events)")
    for i, r in enumerate(rows[: a.top], 1):
        print(f"{i:>2}. {r['site']}:{r['login']:<18} score {r['score']:>8.1f}  {'lane' if r['in_our_lane'] else 'new?'}  {r['category']}")
        for t in r["ref_titles"][:3]:
            print(f"      ref  {t}")
        for t in r["kick_top"][:2]:
            print(f"      kick {t}")
        for t in r["lsf"][:2]:
            print(f"      lsf  {t}")
        if r.get("latest_vod"):
            print(f"      clip {r['latest_vod']}")
    Path(a.out).write_text(json.dumps(rows[:50], indent=1, default=str))


# ---------------------------------------------------------------- world lane
def google_trends(geo):
    raw = get(f"https://trends.google.com/trending/rss?geo={geo}", as_json=False)
    out = []
    if not raw:
        return out
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return out
    ns = {"ht": "https://trends.google.com/trending/rss"}
    for it in root.iter("item"):
        traffic = (it.findtext("ht:approx_traffic", default="", namespaces=ns) or "").replace("+", "").replace(",", "")
        news = [n.findtext("ht:news_item_title", default="", namespaces=ns) for n in it.findall("ht:news_item", ns)]
        out.append({"topic": it.findtext("title", ""), "traffic": int(traffic) if traffic.isdigit() else 0, "geo": geo, "news": [x for x in news if x][:2]})
    return out


def wiki_top():
    day = (NOW - dt.timedelta(days=1)).strftime("%Y/%m/%d")
    d = get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{day}")
    skip = re.compile(r"^(Main_Page|Special:|Wikipedia:|Portal:|Help:|File:|Talk:|User:|Cleopatra|XXX|Search)")
    arts = (d or {}).get("items", [{}])[0].get("articles", []) if d else []
    return [{"topic": x["article"].replace("_", " "), "views": x["views"]} for x in arts if not skip.match(x["article"])][:40]


def long_videos(topic, days=4, n=12):
    """YouTube long videos (> 12 min) about topic from the last days, by views per hour (metadata only)."""
    out = []
    for e in ytdlp_json(["--skip-download", "-j", "--match-filter", "duration > 720 & !is_live", f"ytsearchdate{n}:{topic}"], 300):
        ts = e.get("timestamp") or (dt.datetime.strptime(e["upload_date"], "%Y%m%d").replace(tzinfo=dt.timezone.utc).timestamp() if e.get("upload_date") else None)
        h = hours_since(ts)
        if h and h <= days * 24:
            out.append({"title": e.get("title"), "channel": e.get("channel"), "views": e.get("view_count") or 0, "hours": round(h),
                        "vph": round((e.get("view_count") or 0) / h), "minutes": round((e.get("duration") or 0) / 60), "url": e.get("webpage_url")})
    return sorted(out, key=lambda x: -x["vph"])


def world(a):
    trends = google_trends("US") + google_trends("GB")
    wk = wiki_top()
    print(f"[world] {len(trends)} Google trends, {len(wk)} Wikipedia top pages")
    seen, topics = set(), []
    for t in sorted(trends, key=lambda t: -t["traffic"]):
        k = t["topic"].lower()
        if k not in seen:
            seen.add(k)
            topics.append({"topic": t["topic"], "why": f"Google {t['geo']} {t['traffic']:,}+ searches" + (f"; news: {t['news'][0][:80]}" if t["news"] else "")})
    for w in wk:
        k = w["topic"].lower()
        if k not in seen:
            seen.add(k)
            topics.append({"topic": w["topic"], "why": f"Wikipedia {w['views']:,} reads yesterday"})
    topics = topics[: a.topics]
    print(f"\n== WORLD LANE: {len(topics)} trending topics, with the long videos to clip from (views per hour)")
    for i, t in enumerate(topics, 1):
        t["sources"] = long_videos(t["topic"])[:3]
        best = t["sources"][0]["vph"] if t["sources"] else 0
        t["score"] = best
        print(f"{i:>2}. {t['topic']}  ({t['why']})")
        for s in t["sources"]:
            print(f"      {s['vph']:>7,}/h  {s['views']:>9,} views  {s['minutes']:>3} min  {s['channel']}: {(s['title'] or '')[:80]}  {s['url']}")
    Path(a.out).write_text(json.dumps(sorted(topics, key=lambda t: -t["score"]), indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lane", required=True)
    s = sub.add_parser("streamers"); s.add_argument("--out", default="hot_streamers.json"); s.add_argument("--top", type=int, default=12)
    w = sub.add_parser("world"); w.add_argument("--out", default="hot_world.json"); w.add_argument("--topics", type=int, default=25)
    a = ap.parse_args()
    {"streamers": streamers, "world": world}[a.lane](a)


if __name__ == "__main__":
    main()
