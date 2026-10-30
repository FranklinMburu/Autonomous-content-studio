"""Stage 2: research. Find real sources for a topic, download them once, and freeze them.

Method borrowed from Stanford's STORM: first ask which questions a curious viewer would have, then retrieve
sources for those questions. Retrieval uses free, key-less APIs:
- Wikipedia (search + plain-text extracts)
- OpenAlex (scholarly works with abstracts)

Gate: at least 2 usable sources, at least one of them Wikipedia. The frozen text is all any later stage may use.
"""
import json
import re
import time
import urllib.parse
import urllib.request

UA = "AutonomousContentStudio/1.0 (https://github.com/FranklinMburu/Autonomous-content-studio; educational shorts)"
WIKI_API = "https://en.wikipedia.org/w/api.php"
OPENALEX = "https://api.openalex.org/works"
MIN_WIKI_CHARS = 1500
MIN_ABSTRACT_CHARS = 400
MAX_TEXT = 40000
# Articles about films, shows, books or music that share the topic's words are not sources for the science.
OFF_TOPIC = re.compile(r"\((?:[0-9]{4} )?(?:film|tv series|television series|novel|book series|album|song|band|"
                       r"video game|musical|play|episode|franchise|magazine|comics?)\)|\(disambiguation\)", re.I)
OFF_TOPIC_LEAD = re.compile(r"\b(?:is|was) (?:an?|the) (?:[a-z0-9'-]+ ){0,5}(?:film|movie|television series|tv series|"
                            r"novel|album|ep|single|song|band|video game|horror anthology|book series|musical|"
                            r"soundtrack|mixtape|sitcom|documentary|podcast)\b", re.I)


class ResearchError(Exception):
    pass


def _get(url, params, timeout=30, tries=3):
    q = url + "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(q, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:   # network hiccup: retry with a short pause
            last = e
            time.sleep(2 * (i + 1))
    raise ResearchError(f"request failed: {type(last).__name__}: {str(last)[:120]}")


def plan(topic, ask=None):
    """Viewer questions + Wikipedia titles to look up (one free-model call; falls back to the topic itself)."""
    fallback = {"questions": [topic], "wikipedia": [topic], "scholar": [topic]}
    if ask is None:
        return fallback
    prompt = (f"A short explainer video will answer: {topic}\n"
              "1. List the 4 questions a curious viewer would want answered (short).\n"
              "2. List up to 3 exact English Wikipedia article titles most likely to answer them.\n"
              "3. List 2 short search phrases for scientific papers on the core question.\n"
              'Return JSON only: {"questions": [...], "wikipedia": [...], "scholar": [...]}')

    def v(d):
        if not isinstance(d, dict) or not isinstance(d.get("wikipedia"), list) or not d["wikipedia"]:
            return ['need {"questions": [...], "wikipedia": [...], "scholar": [...]}']
        return []
    try:
        r = ask(prompt, tier="bulk", validate=v, temperature=0.2, max_tokens=600)
        d = r.data
        return {"questions": [str(x) for x in d.get("questions", [])][:6] or [topic],
                "wikipedia": [str(x) for x in d.get("wikipedia", [])][:3] + [topic],
                "scholar": [str(x) for x in d.get("scholar", [])][:2] or [topic], "model": r.ref}
    except Exception:
        return fallback


def wiki_search(query, n=2):
    d = _get(WIKI_API, {"action": "query", "list": "search", "srsearch": query, "srlimit": n, "format": "json"})
    return [h["title"] for h in d.get("query", {}).get("search", [])]


def wiki_text(title):
    d = _get(WIKI_API, {"action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1, "titles": title,
                        "format": "json"})
    pages = d.get("query", {}).get("pages", {})
    for p in pages.values():
        txt = p.get("extract") or ""
        if txt:
            t = p.get("title", title)
            txt = re.sub(r"\n==+ (See also|References|External links|Further reading|Notes|Bibliography) ==+[\s\S]*", "",
                         txt)
            return {"url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_")),
                    "title": t, "text": re.sub(r"\s+\n", "\n", txt).strip()[:MAX_TEXT], "kind": "wikipedia"}
    return None


def _abstract(inv):
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def scholar(query, n=2, must=()):
    d = _get(OPENALEX, {"search": query, "filter": "has_abstract:true", "per-page": 5})
    out = []
    for w in d.get("results", []):
        ab = _abstract(w.get("abstract_inverted_index"))
        if len(ab) < MIN_ABSTRACT_CHARS:
            continue
        low = (str(w.get("title")) + " " + ab).lower()
        if must and sum(1 for m in must if m in low) < min(2, len(must)):
            continue
        url = w.get("doi") or w.get("id")
        yr = w.get("publication_year")
        out.append({"url": url, "title": f"{w.get('title')} ({yr})", "kind": "paper",
                    "text": f"{w.get('title')}. Published {yr}. Abstract: {ab}"[:MAX_TEXT]})
        if len(out) >= n:
            break
    return out


def keywords(topic):
    stop = {"why", "how", "does", "do", "what", "the", "a", "an", "you", "your", "can", "is", "are", "when", "we",
            "our", "of", "to", "in", "and", "happens", "happen", "make", "makes", "yourself", "yourselves", "someone",
            "something", "else", "they", "them", "their", "there", "this", "that", "with", "from", "into", "get",
            "gets", "got", "really", "actually", "people", "things", "thing", "only", "ever", "still", "each", "other"}
    out = []
    for w in re.findall(r"[a-z]+", topic.lower()):
        if w not in stop and len(w) > 2 and w.rstrip("s") not in {o.rstrip("s") for o in out}:
            out.append(w)
    return out


def research(topic, ask=None, log=print):
    """Return (sources, plan). Raises ResearchError when the gate fails."""
    p = plan(topic, ask)
    kw = keywords(topic)
    sources, seen = [], set()

    def relevant(s):
        if OFF_TOPIC.search(s["title"]) or OFF_TOPIC_LEAD.search(s["text"][:600]):
            return False
        low = s["text"][:6000].lower() + " " + s["title"].lower()
        return sum(1 for k in kw if k[:-1] in low) >= min(2, len(kw)) if kw else True
    for title in p["wikipedia"]:
        if len([s for s in sources if s["kind"] == "wikipedia"]) >= 2:
            break
        try:
            for t in [title] + wiki_search(title, 2):
                if t in seen:
                    continue
                seen.add(t)
                s = wiki_text(t)
                if s and len(s["text"]) >= MIN_WIKI_CHARS and relevant(s) and s["url"] not in {x["url"] for x in sources}:
                    sources.append(s)
                    log(f"  source: {s['title']} (Wikipedia, {len(s['text'])} chars)")
                    break
        except ResearchError as e:
            log(f"  wikipedia lookup failed for {title!r}: {e}")
    for q in p["scholar"][:2]:
        try:
            for s in scholar(q, 1, kw):
                if s["url"] not in {x["url"] for x in sources}:
                    sources.append(s)
                    log(f"  source: {s['title'][:80]} (paper abstract)")
        except ResearchError as e:
            log(f"  paper search failed: {e}")
    if len(sources) < 2 or not any(s["kind"] == "wikipedia" for s in sources):
        raise ResearchError(f"only {len(sources)} usable source(s) found; need 2, including Wikipedia")
    return sources, p
