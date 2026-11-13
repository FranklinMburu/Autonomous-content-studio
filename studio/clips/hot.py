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
BAD_CATEGORY = re.compile(r"slots|casino|gambl|roleplay|\brp\b|grand theft auto|gta|rob run", re.I)
LANE_CATEGORY = re.compile(r"just chatting|irl|chat roulette|pools|hot tubs|music|sports|food|travel", re.I)


def englishish(text):
    letters = [c for c in text if c.isalpha()]
    return not letters or sum(c.isascii() for c in letters) / len(letters) > 0.9 and not re.search(r"\b(que|para|mejor|de la|el|los|na|nie)\b", text.lower())


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


def rss(channel_id):
    """A channel's 15 newest uploads from YouTube's public RSS feed: title, published, views, url. No bot check."""
    raw = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}", as_json=False)
    out = []
    if not raw:
        return out
    ns = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/", "yt": "http://www.youtube.com/xml/schemas/2015"}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return out
    for e in root.findall("a:entry", ns):
        st = e.find("m:group/m:community/m:statistics", ns)
        pub = dt.datetime.fromisoformat(e.findtext("a:published", "", ns).replace("Z", "+00:00"))
        link = e.find("a:link", ns)
        out.append({"title": e.findtext("a:title", "", ns), "ts": pub.timestamp(), "views": int(st.get("views", 0)) if st is not None else 0,
                    "url": link.get("href") if link is not None else None, "channel": root.findtext("a:title", "", ns)})
    return out


_IDS = {}


def channel_id(handle):
    """@handle -> UC... id (yt-dlp list metadata, which works where opening a video hits YouTube's bot check)."""
    if handle.startswith("UC"):
        return handle
    if handle not in _IDS:
        r = subprocess.run(["yt-dlp", "--flat-playlist", "-I", "1", "-J", f"https://www.youtube.com/{handle}/videos"],
                           capture_output=True, text=True, timeout=120)
        try:
            _IDS[handle] = json.loads(r.stdout).get("channel_id")
        except json.JSONDecodeError:
            _IDS[handle] = None
            print(f"  ! could not resolve {handle}: {r.stderr.strip()[-160:]}", file=sys.stderr)
    return _IDS[handle]


def hours_since(ts):
    return max(1.0, (NOW.timestamp() - ts) / 3600) if ts else None


# ---------------------------------------------------------------- streamers lane
def flat(url, n, extra=()):
    """A YouTube list (channel tab, search) as metadata only: this works from GitHub, opening videos does not."""
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-I", f"1:{n}", "-J", "--extractor-args", "youtube:approximate_date", *extra, url],
                       capture_output=True, text=True, timeout=300)
    try:
        return (json.loads(r.stdout) or {}).get("entries") or []
    except json.JSONDecodeError:
        print(f"  ! {url}: {r.stderr.strip()[-200:]}", file=sys.stderr)
        return []


def ref_uploads(n=40):
    """Newest Shorts of each reference channel, each scored against its channel's median views: a Short far above the
    median while still new is what works right now. (Upload times aren't readable from GitHub, so order = recency.)"""
    out = []
    for name, cid in REF_CHANNELS.items():
        es = flat(f"https://www.youtube.com/channel/{cid}/shorts", n)
        views = sorted(e.get("view_count") or 0 for e in es)
        med = max(1, views[len(views) // 2]) if views else 1
        print(f"  {name}: {len(es)} Shorts, median {med:,} views, {sum(1 for e in es if e.get('timestamp'))} with a date")
        for pos, e in enumerate(es):
            v = e.get("view_count") or 0
            out.append({"channel": name, "title": e.get("title") or "", "views": v, "pos": pos + 1,
                        "lift": round(v / med, 2), "url": e.get("url")})
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
    """Today's top LivestreamFail posts: (streamer login lowercased, title, upvotes). 13 Nov 2026: livestreamfail.tv
    embeds no clip data any more, so this reads the same community on Reddit (r/LivestreamFail, top of the day): its
    JSON, else its RSS feed. Post titles start with the streamer ("N3on | ...", "xQc - ...", "[Kai Cenat] ...")."""
    out = []
    d = get("https://www.reddit.com/r/LivestreamFail/top.json?t=day&limit=50")
    posts = [c["data"] for c in ((d or {}).get("data") or {}).get("children", []) if isinstance(c, dict) and "data" in c]
    if posts:
        rows = [(p.get("title", ""), int(p.get("score") or 0)) for p in posts]
        print(f"  livestreamfail (reddit json): {len(rows)} posts")
    else:
        rows = []
        page = get("https://www.reddit.com/r/LivestreamFail/top/.rss?t=day&limit=50", as_json=False) or ""
        try:
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for e in ET.fromstring(page).findall("a:entry", ns):
                rows.append(((e.findtext("a:title", "", ns) or ""), 0))
        except ET.ParseError:
            pass
        print(f"  livestreamfail (reddit rss): {len(rows)} posts")
    for title, ups in rows:
        t = html.unescape(title).strip()
        m = re.match(r"^\[([A-Za-z0-9_ .]{2,25})\]\s*(.+)$", t) or re.match(r"^([A-Za-z0-9_ .]{2,25}?)\s*(?:\||-|:|\u2013)\s*(.+)$", t)
        if m:
            out.append((m.group(1).strip().lower().replace(" ", ""), m.group(2).strip(), ups))
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
    print(f"[streamers] {len(ref)} newest reference Shorts read")
    score = collections.defaultdict(lambda: {"ref_vph": 0.0, "ref_titles": [], "kick_views": 0, "kick_top": [], "lsf": [], "category": ""})
    for r in ref:
        for who in names_in(r["title"]):
            s = score[who]
            # newer Shorts count more (their views are still growing); lift above the channel median is the demand
            s["ref_vph"] += 100 * r["lift"] * (1.5 if r["pos"] <= 10 else 1.0)
            s["ref_titles"].append(f"#{r['pos']} newest, {r['views']:,} views ({r['lift']}x median): {r['title'][:90]}")
    kv, kt, kc = kick_day()
    for slug, n in kv.items():
        cat, known = kc.get(slug, ""), ("kick", slug) in ROSTER.values()
        if BAD_CATEGORY.search(cat) or (not known and (not LANE_CATEGORY.search(cat) or not all(englishish(t) for _, t in kt[slug][:3]))):
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
    print(f"\n== STREAMERS LANE, top {a.top} (score = demand on the winning clip channels + Kick clip views/hour + fresh events)")
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
    day = (NOW - dt.timedelta(days=2)).strftime("%Y/%m/%d")
    d = get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{day}")
    skip = re.compile(r"^(Main_Page|Special:|Wikipedia:|Portal:|Help:|File:|Talk:|User:|Cleopatra|XXX|Search)")
    arts = (d or {}).get("items", [{}])[0].get("articles", []) if d else []
    return [{"topic": x["article"].replace("_", " "), "views": x["views"]} for x in arts if not skip.match(x["article"])][:40]


WORLD_CHANNELS = [  # long-form shows whose moments get clipped everywhere; ids resolved at run time, a bad handle is skipped
    "@joerogan", "@flagrant", "@TheoVon", "@TheDiaryOfACEO", "@impaulsive", "@ClubShayShay", "@DrinkChamps",
    "@BreakfastClubPower1051", "@lexfridman", "@PBDPodcast", "@ShawnRyanShow", "@PiersMorganUncensored", "@jubilee",
    "@FirstWeFeast", "@60minutes", "@CNBCtelevision", "@cspan", "@TuckerCarlson", "@allin", "@fullsend",
    "@HotOnes", "@IShowSpeed", "@MrBeast", "@colinandsamir", "@hubermanlab", "@NoJumper", "@ComplexNews",
]


def world_sources(n=12, keep=4):
    """Each show's newest long videos, scored by views against that show's own median (dates aren't readable from
    GitHub; the newest few are what's fresh)."""
    out = []
    for h in WORLD_CHANNELS:
        es = [e for e in flat(f"https://www.youtube.com/{h}/videos", n) if (e.get("duration") or 0) >= 600]
        _IDS[h] = bool(es)
        if not es:
            continue
        views = sorted(v for v in (e.get("view_count") or 0 for e in es) if v > 0)   # members-only/premieres show 0
        if not views:
            continue
        med = max(1, views[len(views) // 2])
        for pos, e in enumerate(es[:keep]):
            v = e.get("view_count") or 0
            out.append({"title": e.get("title") or "", "channel": e.get("channel") or h, "handle": h, "views": v, "pos": pos + 1,
                        "lift": round(v / med, 2), "minutes": round((e.get("duration") or 0) / 60), "url": e.get("url")})
    return out


def topic_videos(topic, n=10):
    """Newest long YouTube videos about a trending topic (interviews, podcasts, hearings), metadata only."""
    es = flat(f"ytsearch{n}:{topic} interview", n)
    return [{"title": e.get("title") or "", "channel": e.get("channel") or "", "views": e.get("view_count") or 0,
             "minutes": round((e.get("duration") or 0) / 60), "url": e.get("url")} for e in es if (e.get("duration") or 0) >= 600 or not e.get("duration")]


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
    hot_words = {w for t in trends for w in re.findall(r"[a-z][a-z0-9']{3,}", t["topic"].lower())}
    hot_words |= {w for t in wk[:25] for w in re.findall(r"[a-z][a-z0-9']{3,}", t["topic"].lower())}
    src = world_sources()
    print(f"[world] {len(src)} new long-form uploads from {sum(1 for h in WORLD_CHANNELS if _IDS.get(h))}/{len(WORLD_CHANNELS)} shows")
    import math
    for e in src:
        e["trend_match"] = sorted(hot_words & set(re.findall(r"[a-z][a-z0-9']{3,}", e["title"].lower())))
        # how far above the show's usual it is, times how big it is, newer first; x1.5 on today's trends
        e["score"] = round(e["lift"] * math.log10(max(10, e["views"])) * (1.3 if e["pos"] == 1 else 1.0) * (1.5 if e["trend_match"] else 1.0), 2)
    src.sort(key=lambda e: -e["score"])
    print(f"\n== WORLD LANE: the long videos to clip right now (lift = views vs the show's usual; #1 = its newest)")
    for i, e in enumerate(src[: a.topics], 1):
        print(f"{i:>2}. {e['lift']:>5}x usual  {e['views']:>10,} views  #{e['pos']} newest  {e['minutes']:>3} min  {e['channel'][:24]:24s} {e['title'][:80]}"
              + (f"  [trend: {', '.join(e['trend_match'])}]" if e["trend_match"] else "") + f"  {e['url']}")
    print("\n== What the world is searching and reading (for spotting a moment before the shows cover it)")
    for t in sorted(trends, key=lambda t: -t["traffic"])[:15]:
        print(f"   Google {t['geo']} {t['traffic']:>7,}+  {t['topic']}" + (f"  ({t['news'][0][:70]})" if t["news"] else ""))
    for w in wk[:15]:
        print(f"   Wikipedia {w['views']:>9,}  {w['topic']}")
    people = [w["topic"] for w in wk[:20] if not re.search(r"\b(list|deaths|season|film|series|part|ss |\.xxx)\b", w["topic"].lower()) and not w["topic"].startswith(".")][:8]
    print("\n== Long videos about today's most-read people and stories (newest first)")
    topics_out = []
    for t in people:
        vids = topic_videos(t)[:3]
        topics_out.append({"topic": t, "videos": vids})
        print(f"   {t}")
        for v in vids:
            print(f"      {v['views']:>10,} views  {v['minutes']:>3} min  {v['channel'][:24]:24s} {v['title'][:80]}  {v['url']}")
    Path(a.out).write_text(json.dumps({"sources": src[:60], "trends": trends, "wikipedia": wk, "topics": topics_out}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lane", required=True)
    s = sub.add_parser("streamers"); s.add_argument("--out", default="hot_streamers.json"); s.add_argument("--top", type=int, default=12)
    w = sub.add_parser("world"); w.add_argument("--out", default="hot_world.json"); w.add_argument("--topics", type=int, default=25)
    a = ap.parse_args()
    {"streamers": streamers, "world": world}[a.lane](a)


if __name__ == "__main__":
    main()
