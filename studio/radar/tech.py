"""Tech radar: what Tech Education should make next, from what the market is rewarding right now (13 Nov 2026).

    python -m studio.radar.tech --out tech_radar.json [--model gemini-...]

Free sources only, all readable from GitHub's servers:
  1. reference tech channels on YouTube (Maitis, Griffin Wooldridge and ~20 more): their newest videos, each scored by
     views against that channel's own median ("lift"): what is beating the usual right now;
  2. GitHub: new repositories gaining stars fastest this week (search API);
  3. Hacker News front page (Algolia API);
  4. Hugging Face: trending models;
  5. Google Trends (US): today's searches, kept only when they look like tech.
Then the AI (free Gemini) groups the evidence into topics and, for each, proposes the format that fits (a Short, a
1-minute explainer, or a long walkthrough), the angle, three titles in the winning patterns, and a thumbnail idea.
The output ranks topics by evidence (reference lift weighs most: it is what YouTube rewards), never by the AI alone.
"""
import argparse, base64, datetime as dt, json, os, re, subprocess, sys, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (studio tech radar)"}

# The bar for this lane: channels whose winning videos show what tech viewers click now. Handles are resolved at run
# time; a wrong or renamed handle is skipped and reported, never fatal.
REF_CHANNELS = [
    "@maitis-ai", "@griffinwdesigns", "@Fireship", "@mreflow", "@aiexplained-official", "@t3dotgg", "@ThePrimeTimeagen",
    "@NetworkChuck", "@matthew_berman", "@WesRoth", "@TwoMinutePapers", "@JeffSu", "@futurepedia_io", "@AIJasonZ",
    "@ColeMedin", "@DavidOndrej", "@rileybrownai", "@GregIsenberg", "@TheAIGRID", "@AllAboutAI", "@developedbyed",
    "@AlexFinnOfficial",
]
TECH = re.compile(r"\b(ai|gpt|claude|gemini|openai|anthropic|nvidia|apple|google|microsoft|meta|tesla|iphone|android|chip|robot|"
                  r"app|software|code|coding|github|deepseek|qwen|llm|model|agent|crypto|bitcoin|cyber|hack|data|cloud|"
                  r"startup|samsung|xai|grok|copilot|cursor|python|linux|windows|chatgpt)\b", re.I)


def get(url, as_json=True, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    for wait in (2, 6):
        try:
            raw = urllib.request.urlopen(req, timeout=timeout).read()
            return json.loads(raw) if as_json else raw.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001  one source failing must not stop the radar
            err = e
            time.sleep(wait)
    print(f"  ! {url[:90]}: {err}", file=sys.stderr)
    return None


def flat(url, n):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-I", f"1:{n}", "-J", "--extractor-args", "youtube:approximate_date", url],
                       capture_output=True, text=True, timeout=300)
    try:
        return (json.loads(r.stdout) or {}).get("entries") or []
    except json.JSONDecodeError:
        return []


def youtube_refs(n=15, keep=5):
    out, missing = [], []
    for h in REF_CHANNELS:
        es = [e for e in flat(f"https://www.youtube.com/{h}/videos", n) if (e.get("duration") or 0) >= 60]
        views = sorted(v for v in (e.get("view_count") or 0 for e in es) if v > 0)
        if not views:
            missing.append(h)
            continue
        med = max(1, views[len(views) // 2])
        for pos, e in enumerate(es[:keep]):
            v = e.get("view_count") or 0
            out.append({"source": "youtube", "channel": e.get("channel") or h, "title": e.get("title") or "", "views": v,
                        "lift": round(v / med, 2), "pos": pos + 1, "minutes": round((e.get("duration") or 0) / 60, 1), "url": e.get("url")})
    if missing:
        print(f"  reference channels not read: {', '.join(missing)}")
    return out


def github_new():
    since = (dt.date.today() - dt.timedelta(days=7)).isoformat()
    h = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        h["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    d = get(f"https://api.github.com/search/repositories?q=created:%3E{since}&sort=stars&order=desc&per_page=25", headers=h) or {}
    return [{"source": "github", "title": f"{r['full_name']}: {(r.get('description') or '')[:140]}", "stars": r.get("stargazers_count", 0),
             "url": r.get("html_url")} for r in d.get("items", [])]


def hacker_news():
    d = get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30") or {}
    return [{"source": "hackernews", "title": h.get("title") or "", "points": h.get("points", 0),
             "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"} for h in d.get("hits", [])]


def huggingface():
    d = get("https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=20") or []
    return [{"source": "huggingface", "title": m.get("id") or m.get("modelId") or "", "likes": m.get("likes", 0),
             "url": f"https://huggingface.co/{m.get('id') or m.get('modelId')}"} for m in d if isinstance(m, dict)]


def google_trends_tech():
    raw = get("https://trends.google.com/trending/rss?geo=US", as_json=False) or ""
    out = []
    try:
        ns = {"ht": "https://trends.google.com/trending/rss"}
        for it in ET.fromstring(raw).iter("item"):
            t = it.findtext("title", "")
            news = " ".join(n.findtext("ht:news_item_title", default="", namespaces=ns) for n in it.findall("ht:news_item", ns))
            if TECH.search(t) or TECH.search(news):
                traffic = (it.findtext("ht:approx_traffic", default="", namespaces=ns) or "").replace("+", "").replace(",", "")
                out.append({"source": "google_trends", "title": t, "traffic": int(traffic) if traffic.isdigit() else 0, "news": news[:200]})
    except ET.ParseError:
        pass
    return out


PROMPT = """You are the head of content for a faceless tech YouTube channel ("Tech Education", series "Build Basics":
real-looking software in a moving 3D world, a calm male voice; it can make a 45-75 s Short, a 2-4 min explainer, or a
10-15 min walkthrough with real screen demos). Our honest angle: a $0 builder who shows real, working tools.

What wins right now on reference channels (measured, not guessed): Maitis' best videos are "FREE alternative to a paid
tool" / "X is dead?" / "China is giving AI away for free" (210K, 100K, 57K); Griffin Wooldridge's are "tool X for
designers" / "Ban the AI look" / "I gave AI 600,000 references" (342K, 285K, 166K).

Below is today's evidence. Group it into the 8 best TOPICS for us to make next. For each:
- "topic": short name; "evidence": which items support it (cite them, with the numbers); "why_now": one line;
- "format": "short" | "explainer" | "walkthrough", whichever fits the topic best (not always the same);
- "angle": the one idea that makes ours different, honest and $0-friendly;
- "titles": 3 titles in the winning patterns above (never invent facts: no fake numbers or claims);
- "thumbnail": one concrete idea (main image + at most 4 words of text);
- "risk": anything that could make it wrong or stale.
Return JSON: {"topics": [ ... ]}. Prefer topics with evidence from more than one source; a reference video with a
high lift counts most."""


def call_gemini(text, model):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4}}
    for m in [model] + [x for x in ("gemini-flash-latest", "gemini-flash-lite-latest") if x != model]:
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                                     data=json.dumps(body).encode(), headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=180).read())
            return json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:  # noqa: BLE001
            print(f"  ! gemini {m}: {str(e)[:160]}", file=sys.stderr)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--model", default=os.environ.get("RADAR_MODEL", "gemini-flash-latest"))
    a = ap.parse_args()
    t0 = time.time()
    yt = youtube_refs()
    rest = github_new() + hacker_news() + huggingface() + google_trends_tech()
    hot_yt = sorted(yt, key=lambda e: -e["lift"])[:40]
    print(f"evidence: {len(yt)} reference videos ({len(set(e['channel'] for e in yt))} channels), "
          + ", ".join(f"{s} {sum(1 for e in rest if e['source'] == s)}" for s in ("github", "hackernews", "huggingface", "google_trends")))
    for e in hot_yt[:10]:
        print(f"  {e['lift']:>5}x  {e['views']:>9,}  {e['channel'][:22]:22s} {e['title'][:80]}")
    lines = [f"[youtube {e['channel']}] {e['title']} | {e['views']:,} views, {e['lift']}x its median, {e['minutes']} min" for e in hot_yt]
    lines += [f"[{e['source']}] {e['title']} | " + ", ".join(f"{k} {e[k]}" for k in ("stars", "points", "likes", "traffic") if k in e) for e in rest]
    r = call_gemini(PROMPT + "\n\nEVIDENCE:\n" + "\n".join(lines), a.model) or {}
    topics = [t for t in r.get("topics", []) if isinstance(t, dict) and t.get("topic")]
    out = {"built": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "topics": topics,
           "evidence": {"youtube": hot_yt, "other": rest}, "seconds": round(time.time() - t0)}
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\n== {len(topics)} TOPICS")
    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t.get('format')}] {t['topic']}: {t.get('why_now', '')}\n   " + "\n   ".join(t.get("titles") or [])
              + f"\n   thumbnail: {t.get('thumbnail')}\n   evidence: {str(t.get('evidence'))[:200]}")


if __name__ == "__main__":
    main()
