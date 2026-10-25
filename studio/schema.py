"""The script format, documented once, used three ways:
  1. shown to Gemini so it writes scripts we can render,
  2. used to validate any script (AI- or human-written) before rendering,
  3. readable by a person writing a script by hand (see scripts/ for examples).
"""
import re
from . import icons

SCENE_DOCS = {
    "hero": "Big icon in a pulsing circle. Best for the HOOK. params: icon, label (optional short text), "
            "reveal {text, at} (optional short punch text that pops when word `at` is spoken).",
    "tags": "Title plus labelled chips that pop in one by one. Good for lists of causes/types/situations. params: "
            "title, icon (optional), items [{text (1-3 words), at, tone: good|bad|neutral}] (2-6 items), "
            "verdict {text, sub, at} (optional full-screen takeaway at the end).",
    "link": "Cause -> effect: icon A sends pulses down to icon B. Good for mechanisms. params: "
            "from {icon, label, at}, to {icon, label, at}, cut {at, label} (optional: the link gets crossed out), "
            "note {text, at} (optional punch text).",
    "number": "A big number counting up. Good for a striking statistic. params: value (number), prefix, suffix, "
              "label (what the number means), at (word when it appears), icon (optional).",
    "compare": "Two cards side by side, A vs B. params: title (optional), left {icon, label, value, at}, "
               "right {icon, label, value, at}, verdict {text, at} (optional).",
    "timeline": "Events appearing down a timeline. params: title (optional), events [{when, label, at}] (2-5).",
    "bars": "Horizontal bar chart. params: title, unit (e.g. ' km/h'), bars [{label, value (number), at}] (2-5).",
    "wave": "A signal/waveform panel. Good for sound, light, signals, rhythms. params: label, icon (optional), "
            "overlay {label, at} (optional: a hidden high-pitched pattern appears inside the wave), "
            "anti {label, at} (optional: an upside-down mirror wave appears), flat {label, at} (optional: the waves "
            "cancel to a flat line), note {text, at} (optional).",
    "meter": "A gauge that fills up. Good for 'how much/how strong'. params: title, low, high, value (0-1), "
             "label (big result text), at.",
    "bubble": "Character with a speech bubble. Best for the PAYOFF. params: icon, prop (optional second icon), "
              "text (2-4 words in the bubble), at.",
    "statement": "Big kinetic words appearing as they're spoken, key words highlighted. Use sparingly. params: "
                 "text (<= 10 words, should match the narration), highlight [words], sub (optional), icon (optional).",
}

REQUIRED = {"hero": ["icon"], "tags": ["items"], "link": ["from", "to"], "number": ["value", "label"],
            "compare": ["left", "right"], "timeline": ["events"], "bars": ["bars"], "wave": ["label"],
            "meter": ["label", "value"], "bubble": ["text"], "statement": ["text"]}

# A few icon names live in nested params.
ICON_PATHS = [("icon",), ("prop",), ("from", "icon"), ("to", "icon"), ("left", "icon"), ("right", "icon")]

WORDS_MIN, WORDS_MAX = 85, 140          # ~35-55 s at Kokoro's pace
MAX_BEATS = 7


def words_of(script):
    return sum(len(l.split()) for b in script.get("beats", []) for l in b.get("lines", []))


def _norm(w):
    return re.sub(r"[^a-z0-9']", "", str(w).lower())


def _at_values(beat):
    """All `at` keywords used inside a beat."""
    out = []
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "at" and isinstance(v, str):
                    out.append(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(beat)
    return out


def validate(script, fix=True):
    """Return (errors, warnings). With fix=True, repairs what it safely can (icon names, missing ids)."""
    errors, warns = [], []
    if not script.get("title"):
        errors.append("missing title")
    beats = script.get("beats")
    if not isinstance(beats, list) or not beats:
        return errors + ["no beats"], warns
    if len(beats) > MAX_BEATS:
        errors.append(f"{len(beats)} beats; keep it to {MAX_BEATS} or fewer")
    n = words_of(script)
    if not WORDS_MIN <= n <= WORDS_MAX:
        errors.append(f"narration is {n} words; aim for {WORDS_MIN}-{WORDS_MAX} (about 35-55 seconds)")
    hook = " ".join(beats[0].get("lines", []))
    if len(hook.split()) > 16:
        errors.append(f"hook is {len(hook.split())} words; keep the first beat to 16 words or fewer")
    for i, b in enumerate(beats):
        b.setdefault("id", f"beat{i + 1}")
        sc = b.get("scene")
        if sc not in SCENE_DOCS:
            errors.append(f"beat {i + 1}: unknown scene '{sc}'")
            continue
        if not b.get("lines"):
            errors.append(f"beat {i + 1}: no narration lines")
        for req in REQUIRED[sc]:
            if b.get(req) in (None, "", []):
                errors.append(f"beat {i + 1} ({sc}): missing '{req}'")
        spoken = {_norm(w) for l in b.get("lines", []) for w in l.split()}
        for at in _at_values(b):
            if _norm(at) not in spoken:
                warns.append(f"beat {i + 1}: cue word '{at}' is not in its narration; timing will be estimated")
        for path in ICON_PATHS:
            parent = b
            for k in path[:-1]:
                parent = parent.get(k) if isinstance(parent, dict) else None
            if isinstance(parent, dict) and parent.get(path[-1]):
                name = parent[path[-1]]
                res, exact = icons.resolve(name)
                if not exact:
                    warns.append(f"beat {i + 1}: icon '{name}' not found; using '{res}'")
                    if fix:
                        parent[path[-1]] = res
    if not script.get("sources"):
        errors.append("no sources: every factual claim needs a source URL")
    else:
        for s in script["sources"]:
            if not str(s.get("url", "")).startswith("http"):
                errors.append(f"source without a valid URL: {s}")
    if len({b.get("scene") for b in beats}) < min(3, len(beats)):
        warns.append("few distinct scene types; video may feel repetitive")
    return errors, warns


EXAMPLE = {
    "title": "Your cat's purr is hiding a cry",
    "topic": "Why do cats purr?",
    "voice": "af_heart",
    "beats": [
        {"scene": "hero", "icon": "@cat", "reveal": {"text": "?", "at": "cry"},
         "lines": ["Your cat might be hiding a cry inside its purr."]},
        {"scene": "tags", "title": "Cats purr when...", "icon": "@cat",
         "items": [{"text": "content", "at": "content", "tone": "neutral"},
                   {"text": "hurt", "at": "hurt", "tone": "bad"},
                   {"text": "scared", "at": "scared", "tone": "bad"},
                   {"text": "giving birth", "at": "giving", "tone": "good"}],
         "verdict": {"text": "purr ≠ happy", "sub": "(not always)", "at": "happy"},
         "lines": ["Cats purr when they're content.", "But also when they're hurt, scared, or even giving birth.",
                   "So a purr doesn't always mean happy."]},
        {"scene": "link", "kicker": "The old theory",
         "from": {"icon": "brain", "label": "brain", "at": "brain"},
         "to": {"icon": "activity", "label": "throat muscles", "at": "throat"},
         "note": {"text": "~25× per second", "at": "twenty-five"},
         "lines": ["For decades, scientists thought every purr needed the brain to twitch the throat muscles about twenty-five times a second."]},
        {"scene": "link", "kicker": "2023 · Vienna", "source": "Herbst et al., Current Biology (2023)",
         "from": {"icon": "brain", "label": "brain", "at": "Then"},
         "to": {"icon": "wave-sine", "label": "vocal folds purr alone", "at": "voice"},
         "cut": {"at": "signal", "label": "no brain signal"},
         "lines": ["Then in 2023, researchers in Vienna showed a cat's voice box can purr with no brain signal at all, likely thanks to tiny pads in its vocal folds."]},
        {"scene": "wave", "icon": "bowl", "label": "purr", "source": "McComb et al. (2009), Univ. of Sussex",
         "overlay": {"label": "+ hidden cry ~380 Hz", "at": "cry"},
         "note": {"text": "≈ pitch of a crying baby", "at": "baby"},
         "lines": ["And when your cat wants food?",
                   "Researchers at Sussex found a high-pitched cry hidden in that purr, close to the pitch of a crying baby."]},
        {"scene": "meter", "title": "Listeners rated those purrs", "low": "calm", "high": "urgent",
         "value": 0.85, "label": "MORE URGENT", "at": "urgent",
         "lines": ["People rated those purrs as more urgent."]},
        {"scene": "bubble", "icon": "@cat", "prop": "bowl", "text": "feed me.", "at": "request",
         "lines": ["So the next time your cat purrs at breakfast, listen closely.",
                   "That's not contentment. That's a request."]},
    ],
    "sources": [
        {"claim": "Cats purr when content, hurt, scared, or giving birth", "url": "https://en.wikipedia.org/wiki/Purr"},
        {"claim": "Cat larynges produce purring without neural input; vocal-fold pads (Herbst et al. 2023)",
         "url": "https://medienportal.univie.ac.at/en/media/recent-press-releases/detailansicht-en/artikel/cats-purr-differently-than-previously-thought"},
        {"claim": "Solicitation purrs hide a ~380 Hz cry; rated more urgent (McComb et al. 2009)",
         "url": "https://www.nationalgeographic.com/science/article/cats-manipulate-their-owners-with-a-cry-embedded-in-a-purr"},
    ],
    "youtube": {"title": "Your cat's purr is hiding a cry 🐱", "description": "Why do cats purr? It's not always happiness.",
                "tags": ["cats", "cat facts", "science", "animal behavior"]},
}
