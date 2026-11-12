"""Keeps Tech Education videos from looking alike.

YouTube's monetisation policy (since 15 July 2025) targets "inauthentic", mass-produced content: videos that look like
one template with the words swapped. Franklin (11 Nov 2026): "even if you're producing 40 videos, we should not have a
pattern whereby they look the same."

Every episode's plan.json already says what it looks like, so the history is simply the episodes folder (no extra state):
  look    one of six design families (plan.look; chosen here, least recently used, never by the model)
  world   the main picture the story is told with (the app/server diagram, a table filling up, a timeline, a phone...)
  opener  the first scene type
  types   every scene type used
check() compares a new plan with the recent episodes; a plan that repeats them is held for review (gate unique_enough).
"""
import json
from collections import Counter
from pathlib import Path

from . import plan as PL

STORY = {"laptop_prompt", "app_window", "diagram_link", "door", "packet", "code_card", "data_card", "question", "key_fly",
         "compare", "leak", "badges_intro", "badge"}
RECENT = 6          # how many earlier episodes a new one is compared with


def world_of(t):
    return "story" if t in STORY else t if t in PL.WORLDS else None


def fingerprint(plan):
    sc = plan.get("scenes", []) if isinstance(plan, dict) else []
    types = [s.get("type") for s in sc]
    worlds = Counter(w for w in map(world_of, types) if w)
    return {"look": plan.get("look") or "studio", "world": worlds.most_common(1)[0][0] if worlds else None,
            "worlds": sorted(worlds), "opener": types[0] if types else None, "types": sorted(set(types))}


def history(channel_dir, before=None):
    """Fingerprints of the episodes in channel_dir, oldest first; only folders sorting before `before` if given."""
    out = []
    for d in sorted(Path(channel_dir).glob("[0-9][0-9][0-9]-*")):
        if before and d.name >= before:
            continue
        try:
            out.append({"episode": d.name, **fingerprint(json.loads((d / "plan.json").read_text(encoding="utf-8")))})
        except (OSError, ValueError):
            continue
    return out


def choose_look(hist, seed=0):
    """The least recently used look (ties broken by the seed), so six episodes in a row never share a look."""
    last = {}
    for i, h in enumerate(hist):
        last[h["look"]] = i
    order = sorted(PL.LOOKS, key=lambda lk: (last.get(lk, -1), (PL.LOOKS.index(lk) + seed) % len(PL.LOOKS)))
    return order[0]


def _jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(1, len(a | b))


def check(plan, hist):
    """Problems if this plan repeats the recent episodes. Empty list = different enough."""
    fp, recent, probs = fingerprint(plan), hist[-RECENT:], []
    if not recent:
        return probs
    if fp["look"] in [h["look"] for h in recent[-2:]]:
        probs.append(f"look '{fp['look']}' was used by one of the last 2 episodes")
    if fp["world"] and fp["world"] in [h["world"] for h in recent[-2:]]:
        probs.append(f"main picture '{fp['world']}' was used by one of the last 2 episodes")
    if fp["opener"] and fp["opener"] == recent[-1]["opener"]:
        probs.append(f"opens with '{fp['opener']}' like the previous episode")
    for h in recent:
        j = _jac(fp["types"], h["types"])
        if j > 0.7:
            probs.append(f"uses {j:.0%} the same scene types as {h['episode']}")
            break
    return probs


def brief(hist):
    """What the writer must avoid, in plain words (goes into the model prompt)."""
    recent = hist[-RECENT:]
    if not recent:
        return "This is the first episode: any world fits."
    worlds = [h["world"] for h in recent[-2:] if h["world"]]
    openers = [h["opener"] for h in recent[-1:] if h["opener"]]
    return (f"VARIETY (the channel must never look like a template): the last episodes were told with "
            f"{', '.join(dict.fromkeys(worlds)) or 'nothing yet'} as the main picture and opened with {', '.join(openers) or '-'}. "
            f"Tell this one with a DIFFERENT main picture and a different opening scene type, chosen because it fits the topic.")
