"""Deterministic checks (gates). Code decides, models propose: a script moves forward only if these pass.

Self-contained on purpose (standard library + studio only): the polish session runs them with no keys, no
network and no access to the private brain repo.

    problems = check_script(script, sources, allowed_icons, stage="draft"|"polished", draft=None, others=[...])
"""
import re

from .. import schema

UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
        "ninety": 90}
SCALES = {"hundred": 100, "thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
SMALL_OK = {0, 1, 2}           # too common in plain speech ("one study", "two cats") to need a source
ORDINAL_OK = {"first", "second", "third"}

BANNED = ["did you know", "in this video", "subscribe", "like and follow", "smash that", "more research is needed",
          "scientists are still", "the jury is still out", "which brings us back", "...", "…",
          "stay tuned", "let's dive", "buckle up"]

ICON_KEYS = schema.ICON_PATHS
FINAL_PUNCT = (".", "?", "!")


# ---------------------------------------------------------------- numbers

def numbers(text):
    """Every number in `text` as a value: digits ("25", "3.5", "1,500") and spoken words ("twenty-five")."""
    out = set()
    low = str(text).lower()
    for m in re.findall(r"\d[\d,]*(?:\.\d+)?", low):
        try:
            out.add(float(m.replace(",", "")))
        except ValueError:
            pass
    toks = re.findall(r"[a-z]+", low.replace("-", " "))
    cur, total, seen = 0, 0, False
    for t in toks + ["<end>"]:
        if t in UNITS:
            cur += UNITS[t]; seen = True
        elif t in TENS:
            cur += TENS[t]; seen = True
        elif t in SCALES and seen:
            if t == "hundred":
                cur *= 100
            else:
                total += cur * SCALES[t]; cur = 0
        elif t == "and" and seen:
            continue
        else:
            if seen:
                out.add(float(total + cur))
            cur, total, seen = 0, 0, False
    return out


def new_numbers(text, allowed_texts):
    have = set()
    for t in allowed_texts:
        have |= numbers(t)
    years_ok = {v for v in have if 1000 <= v <= 2100}
    extra = []
    for v in sorted(numbers(text)):
        if v in have or v in SMALL_OK or v in years_ok:
            continue
        # tolerate rounding of a source number ("about 40" for 39.5) within 3%
        if any(h and abs(v - h) / h <= 0.03 for h in have):
            continue
        extra.append(int(v) if v == int(v) else v)
    return extra


# ---------------------------------------------------------------- text helpers

def strings_in(data):
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        for k, v in data.items():
            if k in ("sources", "_meta", "youtube", "id", "scene", "voice", "tone"):
                continue
            yield from strings_in(v)
    elif isinstance(data, list):
        for v in data:
            yield from strings_in(v)


def narration(script):
    return [l for b in script.get("beats", []) for l in b.get("lines", [])]


def proper_nouns(text):
    """Capitalised words that are not at the start of a sentence (names, places, institutions)."""
    out = set()
    for sent in re.split(r"(?<=[.!?])\s+", str(text)):
        words = re.findall(r"[A-Za-z][A-Za-z'’-]*", sent)
        for w in words[1:]:
            if w[0].isupper() and w not in {"I", "I'm", "I've"}:
                out.add(w.strip("'’"))
    return out


def trigrams(text):
    w = re.findall(r"[a-z]+", str(text).lower())
    return {" ".join(w[i:i + 3]) for i in range(len(w) - 2)}


def similarity(a, b):
    ta, tb = trigrams(a), trigrams(b)
    return len(ta & tb) / max(1, min(len(ta), len(tb)))


# ---------------------------------------------------------------- icons

def icon_names(script):
    out = []
    for b in script.get("beats", []):
        for path in ICON_KEYS:
            parent = b
            for k in path[:-1]:
                parent = parent.get(k) if isinstance(parent, dict) else None
            if isinstance(parent, dict) and parent.get(path[-1]):
                out.append(str(parent[path[-1]]))
    return out


def icon_ok(name, allowed):
    """Allowed = offered to the writer; every offered name was checked to exist when the list was made."""
    return name in set(allowed)


# ---------------------------------------------------------------- the gate

def check_script(script, sources, allowed_icons, stage="draft", draft=None, others=()):
    """Return a list of problems (empty = pass).

    sources: frozen source records [{url, text, ...}]
    allowed_icons: the exact icon names offered to the writer (unknown icons are an error, never swapped)
    stage: "draft" or "polished" (polished is stricter: cue words must be spoken; no new facts vs the draft)
    others: narration texts of scripts already queued/delivered/published (repetition check)
    """
    problems = []
    if not isinstance(script, dict):
        return ["not a JSON object"]
    errors, warns = schema.validate(script, fix=False, check_icons=False)
    problems += [e for e in errors if not e.startswith("no sources")]
    lines = narration(script)
    text = " ".join(lines)
    if lines and not lines[-1].rstrip().endswith(FINAL_PUNCT):
        problems.append("the final line must be a complete sentence ending with . ? or !")
    hook = " ".join(script.get("beats", [{}])[0].get("lines", [])) if script.get("beats") else ""
    if len(hook.split()) > 14:
        problems.append(f"hook is {len(hook.split())} words; keep it to 14 or fewer")
    if lines and lines[-1].strip().lower() == (script["beats"][0]["lines"][0].strip().lower() if script.get("beats") else ""):
        problems.append("the last line repeats the opening line; end with a new angle")
    bad_phrases = [p for p in BANNED if p in " ".join(strings_in(script)).lower()]
    if bad_phrases:
        problems.append(f"banned phrases: {bad_phrases}")
    for name in icon_names(script):
        if not icon_ok(name, allowed_icons):
            problems.append(f"icon '{name}' is not in the allowed icon list; pick one from the list exactly")
    src_texts = [s["text"] for s in sources]
    extra = new_numbers(" ".join(strings_in(script)), src_texts)
    if extra:
        problems.append(f"numbers not found in the sources: {extra[:8]}")
    urls = {s["url"] for s in sources}
    cited = [str(s.get("url", "")) for s in script.get("sources", []) if isinstance(s, dict)]
    if not cited:
        problems.append("no sources cited: cite the source URLs you used (from the source list)")
    foreign = [u for u in cited if u not in urls]
    if foreign:
        problems.append(f"cited URLs that are not in the source list: {foreign[:3]}")
    if stage == "polished":
        problems += [w for w in warns if "cue word" in w]
        if draft is not None:
            allowed_text = " ".join(src_texts) + " " + " ".join(strings_in(draft))
            more = new_numbers(" ".join(strings_in(script)), [allowed_text])
            if more:
                problems.append(f"numbers added that are in neither the draft nor the sources: {more[:8]}")
            known = proper_nouns(allowed_text) | set(re.findall(r"[A-Za-z][A-Za-z'’-]*", allowed_text))
            new_names = sorted(n for n in proper_nouns(text) if n not in known)
            if new_names:
                problems.append(f"names added that are in neither the draft nor the sources: {new_names[:8]}")
    for o in others:
        if o and similarity(text, o) > 0.35:
            problems.append("too similar to a script already made (repetitive content)")
            break
    return problems
