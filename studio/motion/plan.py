"""The visual plan: one scene per spoken line, from a fixed list of scene types (TYPES). This is the contract between
the writer (an AI model or a person) and the engine (web/engine.html). The engine only draws what is described here,
so a plan that passes validate() always renders.

plan.json = {"seed": 17, "scenes": [{"line": 0, "type": "hook_orbit", "p": {...}}, ...]}
- "line" is the index of the spoken line (all beats' lines in order, starting at 0). Every line needs a scene, in order.
- "p" holds the scene's own text: labels, numbers, rows. Word anchors ("word") name a word in that line; the animation
  lands on it (captions and visuals stay in sync with the voice, never with fixed seconds).
"""
import re

S, N, L, B = "text", "number", "list", "bool"
# type -> {param: (kind, required)}. Kinds: text, number, list, bool. Keep in step with BUILD/RENDER in web/engine.html.
TYPES = {
    "hook_orbit":     {"core": (S, True), "sub": (S, False), "items": (L, True)},
    "settings_field": {"title": (S, False), "label": (S, True), "placeholder": (S, True), "glow_word": (S, False), "button": (S, False)},
    "stat_floor":     {"value": (N, True), "suffix": (S, False), "caption": (S, True), "sub": (S, False), "source": (S, True)},
    "laptop_prompt":  {"prompt": (S, True), "result": (S, False), "title": (S, False)},
    "app_window":     {"title": (S, True), "subtitle": (S, False), "rows": (L, False), "slot": (S, False), "unknown": (B, False), "unknown_word": (S, False), "url": (S, False)},
    "diagram_link":   {"label": (S, True), "icon": (S, False), "door": (S, False)},
    "door":           {"word": (S, False)},
    "packet":         {"dir": (S, True), "label": (S, False)},
    "code_card":      {"text": (S, True), "marks": (L, False)},
    "data_card":      {"title": (S, False), "pairs": (L, True), "fill": (S, False)},
    "question":       {"word": (S, False), "label": (S, False)},
    "key_fly":        {"word": (S, False), "append": (S, False)},
    "compare":        {"a_label": (S, True), "a_value": (S, True), "b_label": (S, True), "b_value": (S, True), "sign": (S, False)},
    "leak":           {"word": (S, False), "meter_label": (S, False), "meter_word": (S, False)},
    "stat_wall":      {"value": (N, True), "suffix": (S, False), "caption": (S, True), "sub": (S, False), "source": (S, True), "rows": (L, False), "wall_title": (S, False)},
    "badges_intro":   {},
    "badge":          {"code": (S, True), "label": (S, True), "tone": (S, False)},
    "cta_terminal":   {"prompt": (S, True), "result": (S, False), "title": (S, False)},
    "file_tree":      {"files": (L, True), "code": (L, False), "title": (S, False)},
    "end_card":       {"series": (S, False), "title": (S, True), "next": (S, False)},
    "big_word":       {"text": (S, True), "sub": (S, False)},
    "bullets":        {"items": (L, True)},
    # worlds: one picture that fits the topic; consecutive lines of the same type keep adding to it
    "table_grid":     {"columns": (L, False), "rows": (L, True), "title": (S, False), "highlight_word": (S, False), "highlight_row": (N, False)},
    "timeline":       {"items": (L, True)},
    "flow_steps":     {"steps": (L, True)},
    "browser_page":   {"url": (S, False), "title": (S, False), "blocks": (L, True), "button": (S, False)},
    "chat_thread":    {"messages": (L, True), "title": (S, False)},
    "bar_chart":      {"bars": (L, True), "title": (S, True), "unit": (S, False), "source": (S, False)},
    "phone_screen":   {"app": (S, False), "title": (S, False), "rows": (L, True), "notify": (S, False), "notify_word": (S, False)},
    "stack_layers":   {"layers": (L, True)},
}
LOOKS = ["studio", "paper", "blueprint", "neon", "glass", "bold"]          # design families, one per episode (plan.look)
WORLDS = ["story", "table_grid", "timeline", "flow_steps", "browser_page", "chat_thread", "bar_chart", "phone_screen", "stack_layers"]
# Scenes that need the story set's pieces drawn first (the engine draws nothing for them otherwise).
NEEDS = {"compare": "app_window", "door": "diagram_link", "packet": "diagram_link", "question": "diagram_link", "key_fly": "question",
         "leak": "question", "badges_intro": "diagram_link", "badge": "diagram_link", "data_card": "diagram_link"}
LIMITS = {"items": 8, "rows": 14, "files": 5, "code": 3, "pairs": 6, "marks": 2, "columns": 4, "steps": 6, "blocks": 5, "messages": 6, "bars": 6, "layers": 5}
TEXT_MAX = 64


def lines_of(script):
    return [l for b in script.get("beats", []) for l in b.get("lines", [])]


def _has_word(line, w):
    n = lambda s: re.sub(r"[^a-z0-9%.']", "", s.lower())  # noqa: E731 - same rule as the engine's norm()
    return any(n(x).startswith(n(w)) for x in line.split()) if w else True


def validate(script, plan):
    """Problems (empty list = the plan renders). Checks the contract, not taste."""
    probs = []
    lines = lines_of(script)
    sc = plan.get("scenes") if isinstance(plan, dict) else None
    if not isinstance(sc, list) or not sc:
        return ["plan has no scenes"]
    if [s.get("line") for s in sc] != list(range(len(lines))):
        probs.append(f"plan must have exactly one scene per line, in order (lines 0..{len(lines) - 1})")
    seen = set()
    for i, s in enumerate(sc):
        t, p = s.get("type"), s.get("p", {}) or {}
        where = f"scene {i} ({t})"
        if t not in TYPES:
            probs.append(f"{where}: unknown type; use one of {', '.join(TYPES)}"); continue
        if not isinstance(p, dict):
            probs.append(f"{where}: p must be an object"); continue
        for k, (kind, req) in TYPES[t].items():
            v = p.get(k)
            if v is None:
                if req: probs.append(f"{where}: missing {k}")
                continue
            if kind == S and not isinstance(v, str): probs.append(f"{where}: {k} must be text")
            if kind == S and isinstance(v, str) and len(v) > (110 if k in ("text", "prompt") else TEXT_MAX): probs.append(f"{where}: {k} too long")
            if kind == N and not isinstance(v, (int, float)): probs.append(f"{where}: {k} must be a number")
            if kind == L and (not isinstance(v, list) or not v): probs.append(f"{where}: {k} must be a non-empty list")
            if kind == L and isinstance(v, list) and len(v) > LIMITS.get(k, 8): probs.append(f"{where}: {k} has more than {LIMITS.get(k, 8)} entries")
            if kind == B and not isinstance(v, bool): probs.append(f"{where}: {k} must be true/false")
        for k in p:
            if k not in TYPES[t]: probs.append(f"{where}: unknown field {k}")
        line = lines[s["line"]] if isinstance(s.get("line"), int) and 0 <= s["line"] < len(lines) else ""
        for k in ("word", "glow_word", "unknown_word", "meter_word", "notify_word", "highlight_word"):
            if isinstance(p.get(k), str) and not _has_word(line, p[k]):
                probs.append(f"{where}: {k} {p[k]!r} is not a word of line {s.get('line')}")
        for m in p.get("marks", []) if isinstance(p.get("marks"), list) else []:
            if not (isinstance(m, dict) and m.get("part") and m.get("label")) or m.get("part") not in p.get("text", ""):
                probs.append(f"{where}: each mark needs part (found in text) and label")
            elif m.get("word") and not _has_word(line, m["word"]):
                probs.append(f"{where}: mark word {m['word']!r} is not in line {s.get('line')}")
        if t == "packet" and p.get("dir") not in ("up", "down"): probs.append(f"{where}: dir must be up or down")
        if t == "badge" and p.get("tone", "ok") not in ("ok", "bad", "warn"): probs.append(f"{where}: tone must be ok, bad or warn")
        if t == "hook_orbit" and any(not isinstance(x, dict) or not x.get("label") for x in p.get("items", [])): probs.append(f"{where}: items need a label (and an optional icon)")
        if t == "data_card" and any(not isinstance(x, list) or len(x) != 2 for x in p.get("pairs", [])): probs.append(f"{where}: pairs are [key, value]")
        if t == "file_tree" and any(not isinstance(x, list) or not 1 <= len(x) <= 3 for x in p.get("files", [])): probs.append(f"{where}: files are [name, note, tone]")
        if t == "stat_wall" and any(not isinstance(x, list) or len(x) > 3 for x in p.get("rows", [])): probs.append(f"{where}: rows are [id, text, tag]")
        shape = {"timeline": ("items", "label"), "flow_steps": ("steps", "label"), "browser_page": ("blocks", "text"), "chat_thread": ("messages", "text"),
                 "phone_screen": ("rows", "text"), "stack_layers": ("layers", "label")}.get(t)
        if shape:   # world items: {label|text, word?, ...}; "word" lands the item on that spoken word
            for x in p.get(shape[0], []) if isinstance(p.get(shape[0]), list) else []:
                if not isinstance(x, dict) or not isinstance(x.get(shape[1]), str) or not x[shape[1]].strip():
                    probs.append(f"{where}: each of {shape[0]} needs {shape[1]}"); break
                if len(x[shape[1]]) > TEXT_MAX + 30: probs.append(f"{where}: {shape[0]} {shape[1]} too long"); break
                if x.get("word") and not _has_word(line, x["word"]): probs.append(f"{where}: item word {x['word']!r} is not in line {s.get('line')}")
            if t == "chat_thread" and any(isinstance(x, dict) and x.get("from", "you") not in ("you", "ai") for x in p.get("messages", [])): probs.append(f"{where}: message from must be you or ai")
        if t in ("browser_page", "phone_screen") and t not in seen and not p.get("title"): probs.append(f"{where}: the first {t} needs a title")
        if t == "table_grid" and "table_grid" not in seen and not p.get("columns"): probs.append(f"{where}: the first table_grid needs columns")
        if t == "table_grid" and any(not isinstance(x, list) or not 1 <= len(x) <= 4 for x in p.get("rows", [])): probs.append(f"{where}: rows are lists of up to 4 cells")
        if t == "bar_chart" and any(not isinstance(x, list) or len(x) != 2 or not isinstance(x[1], (int, float)) for x in p.get("bars", [])): probs.append(f"{where}: bars are [label, number]")
        if t in NEEDS and NEEDS[t] not in seen: probs.append(f"{where}: needs a {NEEDS[t]} scene before it")
        seen.add(t)
    if sc and sc[-1].get("type") != "end_card": probs.append("the last scene must be end_card")
    if isinstance(plan, dict) and plan.get("look") is not None and plan.get("look") not in LOOKS: probs.append(f"look must be one of {', '.join(LOOKS)}")
    return probs


def variety(plan):
    """Taste warnings (do not block): the reference changes picture about every 1-3 s and never repeats itself."""
    sc, warn = plan.get("scenes", []), []
    types = [s.get("type") for s in sc]
    runs = [i for i in range(2, len(types)) if types[i] == types[i - 1] == types[i - 2] and types[i] not in ("badge",)]
    if runs: warn.append(f"same scene type 3 times in a row at scenes {runs}")
    if len(set(types)) < min(8, len(types)): warn.append(f"only {len(set(types))} different scene types")
    if not any(t in ("stat_floor", "stat_wall", "bar_chart") for t in types): warn.append("no stat_floor, stat_wall or bar_chart: the bar wants a real, sourced number")
    return warn


def auto_plan(script, title=None, series="Build Basics"):
    """Guardrail: a valid plan from the script alone, used when no model produced one that passes validate().
    Plainer than a written plan (big words and bullet cards), but it always renders, so the run never dies here."""
    lines = lines_of(script)
    words = lambda l: [w.strip(",.?!:;\"'") for w in l.split() if len(w.strip(",.?!:;\"'")) > 3]  # noqa: E731
    num = lambda l: next((float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", l)), None)  # noqa: E731
    sc = []
    kw = [k for k in script.get("key_words", [])]
    for i, l in enumerate(lines):
        if i == 0:
            core = (kw[0] if kw else (words(l) or ["?"])[-1])[:12]
            sc.append({"line": 0, "type": "hook_orbit", "p": {"core": core, "items": [{"label": w[:14]} for w in (kw[1:6] or words(l)[:5] or ["idea"])]}})
        elif i == len(lines) - 1:
            sc.append({"line": i, "type": "end_card", "p": {"series": series, "title": (title or script.get("title", ""))[:60]}})
        elif num(l) is not None and not any(s["type"].startswith("stat") for s in sc):
            sc.append({"line": i, "type": "stat_floor", "p": {"value": num(l), "caption": " ".join(l.split()[:7])[:60], "source": "see sources"}})
        elif i % 2:
            sc.append({"line": i, "type": "big_word", "p": {"text": max(words(l) or ["…"], key=len)[:14], "sub": l[:60]}})
        else:
            sc.append({"line": i, "type": "bullets", "p": {"items": [" ".join(l.split()[:6])[:60]]}})
    return {"seed": 1, "scenes": sc, "auto": True}
