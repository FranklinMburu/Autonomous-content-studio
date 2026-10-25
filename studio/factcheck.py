"""Stage: fact check. Download every source page and ask Gemini whether the narration is supported by it.

This is a safety net, not a guarantee: it catches dead links, invented sources and claims the sources
don't back up. Anything not clearly supported is flagged in the report for a human to look at.
"""
import html, json, re, urllib.request
from . import gemini

UA = "Mozilla/5.0 (compatible; AutonomousContentStudio/1.0; +https://github.com)"

PROMPT = """You are a strict fact-checker for a short educational video.
Below are the narration sentences and text extracted from the cited source pages.
For EACH narration sentence that states a fact (skip pure questions, jokes and transitions), decide:
- "supported": the sources clearly say this
- "partial": roughly right but the sources say something more cautious or slightly different
- "unsupported": the sources don't say this, or contradict it
Quote a short piece of evidence (max 20 words) from the sources when supported/partial.
Return JSON: {{"results": [{{"claim": "...", "verdict": "...", "url": "...", "evidence": "...", "note": "..."}}]}}

NARRATION:
{narration}

SOURCES:
{sources}
"""


def fetch_text(url, limit=60000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read(2_000_000).decode(r.headers.get_content_charset() or "utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
    txt = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt).strip()[:limit]


def _excerpt(text, narration, size=7000):
    """Keep the parts of a long page that share the most words with the narration."""
    if len(text) <= size:
        return text
    keys = {w for w in re.findall(r"[a-z]{5,}", narration.lower())}
    win, step = 1200, 600
    scored = []
    for i in range(0, len(text), step):
        chunk = text[i:i + win]
        scored.append((sum(chunk.lower().count(k) for k in keys), i))
    keep = sorted(i for _, i in sorted(scored, reverse=True)[: size // win])
    return " … ".join(text[i:i + win] for i in keep)


def check(script, log=print):
    narration = [l for b in script["beats"] for l in b["lines"]]
    results, blocks, dead = [], [], []
    for s in script.get("sources", []):
        url = s.get("url", "")
        try:
            txt = fetch_text(url)
            if len(txt) < 400:
                raise ValueError("page has almost no text")
            blocks.append(f"[{url}]\n{_excerpt(txt, ' '.join(narration))}")
        except Exception as e:
            dead.append(url)
            results.append({"claim": s.get("claim", ""), "verdict": "unreachable", "url": url,
                            "note": f"could not read source ({str(e)[:80]})"})
    if blocks:
        txt, model = gemini.generate(PROMPT.format(narration="\n".join(f"- {n}" for n in narration),
                                                   sources="\n\n".join(blocks)),
                                     temperature=0.1)
        try:
            results += gemini.parse_json(txt).get("results", [])
        except Exception as e:
            results.append({"claim": "(fact-check output unreadable)", "verdict": "unsupported", "note": str(e)})
    else:
        log("  no source could be read; every claim is unverified")
    problems = [r for r in results if r.get("verdict") != "supported"]
    log(f"  fact check: {len(results) - len(problems)} supported, {len(problems)} flagged, {len(dead)} dead links")
    return {"results": results, "problems": problems, "dead_links": dead}
