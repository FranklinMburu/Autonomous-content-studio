"""Storyboard renderer: draws a video from storyboard.json (data), not from per-episode code.

A storyboard is a list of shots. Each shot starts on a spoken word and lists a background and items.
Every item type and background comes from the shared library below, so a new video needs no new code,
only a new storyboard. The library grows by adding item types here (reused by every later video).

Timing references ("triggers"):
  "word#n"  the n-th time the word is spoken (case-insensitive, punctuation ignored); "word" = "word#1"
  "+0.4"    seconds after the shot starts
  0         the very start (only for the first shot)
Colours: a palette name (navy, orange, lemon, cream, red, skin, sea, wood, wood2, white, ink, ...),
"#rrggbb", or [r, g, b] with values 0..1.
"""
import math
import cairo

from . import lib as L
from .lib import (W, H, ease, pop, rgb, rect, rrect, circle, vgrad, glow, text, bean, orange, lemon,
                  sea_bg, ship, arm_scar, calendar, ropes, vit_c)

PALETTE = {
    "navy": L.NAVY, "navy2": L.NAVY2, "orange": L.ORANGE, "lemon": L.LEMON, "cream": L.CREAM, "red": L.RED,
    "skin": L.SKIN, "sea": L.SEA, "wood": L.WOOD, "wood2": L.WOOD2, "white": L.WHITE, "ink": L.INK,
    "grey": (0.6, 0.6, 0.65), "steel": (0.25, 0.25, 0.28), "green": (0.6, 0.75, 0.5), "gold": (1, 0.8, 0.3),
    "warm": (1, 0.85, 0.5), "pale": (0.98, 0.88, 0.85),
}
ROLES = {  # character presets: body colour and outfit
    "sailor": {"body": "navy2", "hat": "bandana"},
    "surgeon": {"body": "ink", "hat": "wig"},
    "official": {"body": "navy", "hat": "wig"},
    "person": {"body": "navy2", "hat": None},
}
MOODS = {"calm", "happy", "sick", "doubt", "shock", "gums"}


class BoardError(ValueError):
    pass


def col(v, default="white"):
    v = default if v is None else v
    if isinstance(v, (list, tuple)):
        return tuple(float(x) for x in v[:3])
    if isinstance(v, str) and v.startswith("#") and len(v) == 7:
        return tuple(int(v[i:i + 2], 16) / 255 for i in (1, 3, 5))
    if v in PALETTE:
        return PALETTE[v]
    raise BoardError(f"unknown colour {v!r}")


def when(trigger, shot_t0):
    """Seconds for a trigger. Raises BoardError for words that are not spoken."""
    if trigger is None:
        return shot_t0
    if isinstance(trigger, (int, float)):
        return float(trigger)
    s = str(trigger).strip()
    if s.startswith("+"):
        return shot_t0 + float(s[1:])
    word, _, n = s.partition("#")
    try:
        return L.wt(word, int(n) if n else 1)
    except KeyError as e:
        raise BoardError(str(e).strip('"'))


# ---------- animation helpers ----------
def appear(it, T, t0):
    """0..1 visibility of an item, from its 'in' trigger and 'anim' (pop | drop | fade | grow | none)."""
    a = it.get("anim", "pop" if "in" in it else "none")
    tin = when(it.get("in"), t0) + float(it.get("delay", 0))
    if "out" in it and T >= when(it["out"], t0):
        return 0.0
    if a == "none":
        return 1.0 if T >= tin - 1e-6 else 0.0
    d = float(it.get("dur", 0.25 if a in ("pop", "drop") else 0.5))
    if a == "pop" or a == "drop":
        return pop(T, tin, d)
    return ease((T - tin) / d)


def placed(c, it, p, fn):
    """Translate to (x, y), apply the appear animation, then draw with fn(c)."""
    a = it.get("anim", "pop" if "in" in it else "none")
    x, y, s = float(it.get("x", 540)), float(it.get("y", 960)), float(it.get("s", 1.0))
    if a == "drop":
        y -= (1 - min(1.0, p)) * float(it.get("drop_from", 500))
    c.save(); c.translate(x, y)
    if a in ("pop", "grow"):
        c.scale(max(0.001, s * p), max(0.001, s * p))
    else:
        c.scale(s, s)
    if a == "fade":
        c.push_group()
    fn(c)
    if a == "fade":
        c.pop_group_to_source(); c.paint_with_alpha(max(0.0, min(1.0, p)))
    c.restore()


# ---------- props (drawn around 0,0) ----------
def _mug(c):
    rrect(c, -75, -105, 150, 210, 20, (0.85, 0.65, 0.3), stroke=L.INK, lw=6)
    c.set_line_width(14); rgb(c, L.INK); c.arc(85, 0, 50, -1.2, 1.2); c.stroke()


def _bottle(c, colour=(0.6, 0.75, 0.5)):
    rrect(c, -50, -60, 100, 170, 20, colour, stroke=L.INK, lw=6); rect(c, -25, -130, 50, 80, colour)


def _bucket(c):
    rrect(c, -90, -80, 180, 180, 20, (0.55, 0.42, 0.28), stroke=L.INK, lw=6); rect(c, -75, -60, 150, 40, L.SEA)


def _cannon(c):
    rrect(c, -150, -60, 260, 110, 50, (0.25, 0.25, 0.28), stroke=L.INK, lw=7); circle(c, -60, 70, 55, L.WOOD, stroke=L.INK, lw=6)


def _plate(c):
    c.save(); c.scale(1, 0.32); circle(c, 0, 0, 420, L.CREAM, stroke=L.INK, lw=10); c.restore()


def _crate(c):
    rrect(c, -300, -165, 600, 330, 30, L.WOOD, stroke=L.INK, lw=8)


def _lantern(c):
    rect(c, -10, -200, 20, 160, L.INK); circle(c, 0, 0, 40, (1, 0.85, 0.45))


def _hammock(c):
    c.set_line_width(8); rgb(c, L.CREAM)
    c.move_to(-160, -60); c.curve_to(-60, 40, 60, 40, 160, -60); c.stroke()


def _medicine_crossed(c):
    rrect(c, -60, 0, 120, 220, 20, (0.75, 0.80, 0.85), 0.9, stroke=L.INK, lw=5)
    c.set_line_width(14); rgb(c, L.RED); c.move_to(-80, -20); c.line_to(80, 240); c.stroke()


PROPS = {"mug": _mug, "bottle": _bottle, "bucket": _bucket, "cannon": _cannon, "plate": _plate, "crate": _crate,
         "lantern": _lantern, "hammock": _hammock, "medicine_crossed": _medicine_crossed,
         "orange": lambda c: orange(c, 0, 0, 130), "lemon": lambda c: lemon(c, 0, 0, 95),
         "vitamin_c": lambda c: vit_c(c, 0, 0, 60)}


# ---------- item types ----------
def i_text(c, it, T, t0, lt):
    p = appear(it, T, t0)
    if p:
        placed(c, it, p, lambda c: text(c, str(it["text"]), 0, 0, float(it.get("size", 90)), col(it.get("color"), "white"),
                                           None if it.get("stroke") is False else col(it.get("stroke"), "ink"),
                                           float(it.get("stroke_w", 12))))


def i_prop(c, it, T, t0, lt):
    name = it["name"]
    if name not in PROPS:
        raise BoardError(f"unknown prop {name!r}; known: {', '.join(sorted(PROPS))}")
    p = appear(it, T, t0)
    if p:
        placed(c, it, p, PROPS[name])


def i_character(c, it, T, t0, lt):
    role = ROLES.get(it.get("role", "person"))
    if role is None:
        raise BoardError(f"unknown role {it.get('role')!r}; known: {', '.join(ROLES)}")
    mood, arm = it.get("mood", "calm"), 0.0
    for st in it.get("states", []):  # e.g. [{"at": "already#1", "mood": "happy", "arm": 1.6}]
        k = ease((T - when(st["at"], t0)) / float(st.get("dur", 0.5)))
        if k > 0.5:
            mood = st.get("mood", mood)
        arm += k * float(st.get("arm", 0))
    if mood not in MOODS:
        raise BoardError(f"unknown mood {mood!r}; known: {', '.join(sorted(MOODS))}")
    p = appear(it, T, t0)
    if not p:
        return
    hat = it.get("hat", role["hat"])
    body = col(it.get("body", role["body"]))
    placed(c, {**it, "s": it.get("s", 1.0)}, p, lambda c: bean(c, 0, 0, 1.0, body, mood, hat, T + float(it.get("phase", 0)),
                                                            look=float(it.get("look", 0)), arm=arm,
                                                            lie=bool(it.get("lie", False))))


def i_bar(c, it, T, t0, lt):
    h = float(it["h"]) * ease((T - when(it.get("grow_at"), t0) - float(it.get("delay", 0))) / float(it.get("dur", 0.6)))
    x, base, w = float(it["x"]), float(it["base_y"]), float(it.get("w", 140))
    rrect(c, x - w / 2, base - h, w, h + 1, 20, col(it.get("color"), "red"))


def i_calendar(c, it, T, t0, lt):
    p = appear(it, T, t0)
    if not p:
        return
    val = it.get("value", "")
    if "count" in it:
        cnt = it["count"]
        a, b = int(cnt["from"]), int(cnt["to"])
        k = ease((T - when(cnt.get("at"), t0)) / float(cnt.get("dur", 1.0))) if cnt.get("ease") else \
            max(0.0, min(1.0, (T - when(cnt.get("at"), t0)) / float(cnt.get("dur", 1.0))))
        val = str(a + int(round((b - a) * k)))
    placed(c, it, p, lambda c: calendar(c, 0, 0, 1.0, str(it.get("top", "")), str(val), col(it.get("color"), "red")))


def i_glow(c, it, T, t0, lt):
    k = ease(lt / float(it["fade_in"])) if it.get("fade_in") else 1.0
    glow(c, float(it.get("x", 540)), float(it.get("y", 900)), float(it.get("r", 600)), col(it.get("color"), "warm"),
         float(it.get("alpha", 0.5)) * k)


def i_rays(c, it, T, t0, lt):
    x, y = float(it.get("x", 540)), float(it.get("y", 900))
    for i in range(int(it.get("count", 10))):
        a = i / int(it.get("count", 10)) * 2 * math.pi + T * float(it.get("speed", 0.4))
        rgb(c, col(it.get("color"), "white"), float(it.get("alpha", 0.15)))
        c.move_to(x, y); c.line_to(x + 1600 * math.cos(a), y + 1600 * math.sin(a))
        c.line_to(x + 1600 * math.cos(a + 0.2), y + 1600 * math.sin(a + 0.2)); c.close_path(); c.fill()


def i_floor(c, it, T, t0, lt):
    y = float(it.get("y", 1250))
    rect(c, 0, y, W, H - y + 400, col(it.get("color"), "wood"))
    for k in range(int(it.get("planks", 0))):
        rect(c, 0, y + k * 60, W, 4, col(it.get("line_color"), "wood2"))


def i_dim(c, it, T, t0, lt):
    if T >= when(it.get("in"), t0):
        rect(c, 0, 0, W, H, col(it.get("color"), "ink"), float(it.get("alpha", 0.55)))


def i_cross(c, it, T, t0, lt):
    tin = when(it.get("in"), t0)
    if T < tin:
        return
    p = pop(T, tin)
    x, y, s = float(it.get("x", 540)), float(it.get("y", 720)), float(it.get("size", 400))
    c.set_line_width(float(it.get("width", 36))); rgb(c, col(it.get("color"), "red")); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x - s / 2, y - s / 2); c.line_to(x - s / 2 + s * p, y - s / 2 + s * p)
    c.move_to(x + s / 2, y - s / 2); c.line_to(x + s / 2 - s * p, y - s / 2 + s * p); c.stroke()


def i_finger(c, it, T, t0, lt):
    c.save(); c.translate(float(it.get("x", 540)), float(it.get("y", 1050))); c.rotate(float(it.get("rotate", -0.3)))
    rrect(c, -130, -560, 260, 1100, 130, L.SKIN, stroke=L.INK, lw=10)
    rrect(c, -100, -540, 200, 170, 80, (0.98, 0.88, 0.85), stroke=L.INK, lw=5)
    if "cut_at" in it:
        cut = ease((T - when(it["cut_at"], t0)) / 0.3)
        if cut:
            c.set_line_width(12 * cut); rgb(c, L.RED); c.move_to(-90, -120); c.line_to(90, -150); c.stroke()
    c.restore()


def i_arm_scar(c, it, T, t0, lt):
    opened = ease((T - when(it["open_at"], t0)) / float(it.get("dur", 0.8))) if "open_at" in it else 0.0
    arm_scar(c, T, opened)


def i_ship(c, it, T, t0, lt):
    ship(c, float(it.get("x", 540)), float(it.get("y", 1170)), float(it.get("s", 1.0)), T)


def i_ropes(c, it, T, t0, lt):
    """Collagen ropes across a cut. Each of weave/knots/slip is animated by *_at (+ *_dur) or fixed by a 0..1 value."""
    def k(name, default):
        if name + "_at" in it:
            return ease((T - when(it[name + "_at"], t0)) / float(it.get(name + "_dur", 1.0)))
        return float(it.get(name, default))
    ropes(c, k("weave", 1.0), k("slip", 0.0), T, knots=k("knots", 0.0))


def i_card(c, it, T, t0, lt):
    p = appear(it, T, t0)
    if not p:
        return

    def draw(c):
        rrect(c, -380, -190, 760, 380, 40, col(it.get("color"), [0.25, 0.20, 0.17]), stroke=L.INK, lw=8)
        c.save(); c.translate(-180, 0); PROPS[it["icon"]](c); c.restore()
        text(c, str(it["label"]), 110, 30, float(it.get("size", 92)), col(it.get("label_color"), "cream"), L.INK, 10)
    placed(c, it, p, draw)


def i_group(c, it, T, t0, lt):
    """Repeat an item on a grid; optionally regroup into pairs/other grid at a trigger, number the groups."""
    g = it["grid"]
    n = int(it.get("count", g["cols"] * g.get("rows", 1)))
    rg = it.get("regroup")
    k = ease((T - when(rg["at"], t0)) / float(rg.get("dur", 0.9))) if rg else 0.0
    for i in range(n):
        cl, rw = i % g["cols"], i // g["cols"]
        x0 = g["x"] + cl * g["dx"] + (rw % 2) * g.get("stagger", 0)
        y0 = g["y"] + rw * g.get("dy", 0)
        x, y = x0, y0
        if rg:
            size = int(rg.get("size", 2)); grp, member = i // size, i % size
            x1 = rg["x"] + (grp % rg["cols"]) * rg["dx"] + member * rg.get("member_dx", 120)
            y1 = rg["y"] + (grp // rg["cols"]) * rg["dy"]
            x, y = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        child = {**it["item"], "x": x + it["item"].get("x", 0), "y": y + it["item"].get("y", 0),
                 "phase": i, "delay": float(it["item"].get("delay", 0)) + i * float(it.get("stagger_in", 0))}
        draw_item(c, child, T, t0, lt)
    if rg and rg.get("number") and k > 0.9:
        for grp in range(n // int(rg.get("size", 2))):
            text(c, str(grp + 1), rg["x"] + (grp % rg["cols"]) * rg["dx"] + rg.get("number_dx", 60),
                 rg["y"] + (grp // rg["cols"]) * rg["dy"] + rg.get("number_dy", -220), 60, L.ORANGE, L.INK, 8)


ITEMS = {"text": i_text, "prop": i_prop, "character": i_character, "bar": i_bar, "calendar": i_calendar,
         "glow": i_glow, "rays": i_rays, "floor": i_floor, "dim": i_dim, "cross": i_cross, "finger": i_finger,
         "arm_scar": i_arm_scar, "ship": i_ship, "ropes": i_ropes, "card": i_card, "group": i_group}


def draw_item(c, it, T, t0, lt):
    """Draw one item. Any item may have "from" / "until" triggers: shown only between them."""
    fn = ITEMS.get(it.get("type"))
    if fn is None:
        raise BoardError(f"unknown item type {it.get('type')!r}; known: {', '.join(sorted(ITEMS))}")
    if "from" in it and T < when(it["from"], t0):
        return
    if "until" in it and T >= when(it["until"], t0):
        return
    fn(c, it, T, t0, lt)


# ---------- backgrounds ----------
def background(c, bg, T):
    if isinstance(bg, str):
        bg = {"type": bg}
    t = bg.get("type", "gradient")
    if t == "gradient":
        vgrad(c, col(bg.get("top"), "navy2"), col(bg.get("bottom"), "ink"))
    elif t == "sea":
        sea_bg(c, T)
    elif t in ("none", "skin"):  # drawn entirely by items (arm_scar, ropes)
        pass
    else:
        raise BoardError(f"unknown background {t!r}; known: gradient, sea, none")


# ---------- shots ----------
def build_shots(board):
    """Turn storyboard.json into (start_time, draw_fn, focus_y) shots for lib.frame."""
    shots = []
    for i, sh in enumerate(board["shots"]):
        t0 = 0.0 if i == 0 else when(sh["at"], 0.0)

        def draw(c, lt, T, sh=sh, t0=t0):
            background(c, sh.get("bg", "gradient"), T)
            for it in sh.get("items", []):
                draw_item(c, it, T, t0, lt)
        draw.__name__ = sh.get("name", f"shot{i + 1}")
        shots.append((t0, draw, float(sh.get("focus", 900))))
    return shots, {w.lower() for w in board.get("key_words", [])}


def validate(board, sample=True):
    """Problems with a storyboard, as plain sentences. Needs lib.set_timing() first (word triggers)."""
    problems = []
    shots = board.get("shots") or []
    if not shots:
        return ["storyboard has no shots"]
    try:
        built, key = build_shots(board)
    except BoardError as e:
        return [f"timing: {e}"]
    problems += L.check_shots(built)
    starts = [s[0] for s in built] + [L.DUR]
    for (a, fn, _), b in zip(built, starts[1:]):
        if b - a > float(board.get("max_shot_seconds", 4.5)):
            problems.append(f"{fn.__name__} lasts {b - a:.1f}s; keep shots under {board.get('max_shot_seconds', 4.5)}s")
    if sample:  # draw the middle of every shot once: catches unknown props, moods, colours, missing fields
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 108, 192)
        for (a, fn, fy), b in zip(built, starts[1:]):
            c = cairo.Context(surf); c.scale(0.1, 0.1)
            for T in (a + 0.05, (a + b) / 2, b - 0.05):
                try:
                    fn(c, T - a, T)
                except (BoardError, KeyError, TypeError, ValueError) as e:
                    problems.append(f"{fn.__name__}: {e}")
                    break
    return problems
