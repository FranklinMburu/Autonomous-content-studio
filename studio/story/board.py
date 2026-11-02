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
from . import cast, settings
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


def _basin(c):
    c.move_to(-150, -40); c.curve_to(-140, 60, 140, 60, 150, -40); c.close_path()
    rgb(c, (0.92, 0.92, 0.95)); c.fill_preserve(); rgb(c, L.INK); c.set_line_width(7); c.stroke()
    c.save(); c.scale(1, 0.25); circle(c, 0, -160, 150, (0.55, 0.78, 0.85), stroke=L.INK, lw=6); c.restore()
    rrect(c, -20, 40, 40, 120, 10, (0.45, 0.35, 0.28), stroke=L.INK, lw=5)


def _bed(c):
    rrect(c, -260, -40, 520, 90, 20, (0.95, 0.95, 0.92), stroke=L.INK, lw=7)
    rrect(c, -230, -80, 140, 60, 25, WHITE_, stroke=L.INK, lw=5)
    rect(c, -270, 50, 540, 30, (0.50, 0.38, 0.30)); rect(c, -270, -140, 30, 250, (0.50, 0.38, 0.30)); rect(c, 240, -60, 30, 170, (0.50, 0.38, 0.30))


def _scalpel(c):
    rrect(c, -120, -12, 150, 24, 10, (0.35, 0.30, 0.28), stroke=L.INK, lw=5)
    c.move_to(30, -12); c.line_to(130, -4); c.line_to(30, 12); c.close_path(); rgb(c, (0.85, 0.88, 0.92)); c.fill_preserve(); rgb(c, L.INK); c.set_line_width(5); c.stroke()


def _paper(c):
    rrect(c, -110, -140, 220, 280, 10, (0.97, 0.94, 0.85), stroke=L.INK, lw=6)
    for k in range(7):
        rect(c, -80, -100 + k * 32, 160 - (k % 3) * 30, 8, (0.55, 0.50, 0.45))


def _book(c):
    rrect(c, -130, -90, 260, 180, 12, (0.50, 0.18, 0.15), stroke=L.INK, lw=7); rect(c, -6, -90, 12, 180, (0.35, 0.10, 0.08))


def _bell(c):
    c.move_to(-90, 60); c.curve_to(-90, -110, 90, -110, 90, 60); c.close_path()
    rgb(c, (0.95, 0.75, 0.25)); c.fill_preserve(); rgb(c, L.INK); c.set_line_width(7); c.stroke(); circle(c, 0, 72, 20, (0.95, 0.75, 0.25), stroke=L.INK, lw=5)


def _candle(c):
    rrect(c, -30, -60, 60, 160, 10, (0.97, 0.95, 0.88), stroke=L.INK, lw=5)
    glow(c, 0, -100, 90, (1, 0.8, 0.4), 0.6); c.move_to(0, -130); c.curve_to(25, -90, 15, -70, 0, -66); c.curve_to(-15, -70, -25, -90, 0, -130)
    rgb(c, (1, 0.7, 0.2)); c.fill()


def _microscope(c):
    rect(c, -90, 80, 180, 30, (0.25, 0.25, 0.28)); rrect(c, -20, -60, 40, 150, 10, (0.30, 0.30, 0.35), stroke=L.INK, lw=5)
    c.save(); c.rotate(-0.4); rrect(c, -18, -170, 36, 130, 12, (0.85, 0.85, 0.88), stroke=L.INK, lw=5); c.restore()
    rect(c, -60, 20, 120, 14, (0.25, 0.25, 0.28))


def _germs(c):
    import math as _m
    for k, (x, y, r) in enumerate(((-60, -20, 34), (40, -50, 26), (70, 30, 30), (-20, 50, 22), (0, -5, 18))):
        rgb(c, (0.40, 0.70, 0.25)); c.arc(x, y, r, 0, 2 * _m.pi); c.fill_preserve(); rgb(c, L.INK); c.set_line_width(4); c.stroke()
        for a in range(6):
            aa = a / 6 * 2 * _m.pi + k
            c.move_to(x + r * _m.cos(aa), y + r * _m.sin(aa)); c.line_to(x + (r + 12) * _m.cos(aa), y + (r + 12) * _m.sin(aa)); c.stroke()
        circle(c, x - r * 0.3, y - r * 0.2, r * 0.18, WHITE_)


def _heart(c):
    c.move_to(0, 90); c.curve_to(-160, -20, -90, -150, 0, -60); c.curve_to(90, -150, 160, -20, 0, 90)
    rgb(c, L.RED); c.fill_preserve(); rgb(c, L.INK); c.set_line_width(7); c.stroke()


def _brain(c):
    for x, y, r in ((-50, -20, 70), (40, -30, 75), (0, 30, 70), (-70, 40, 50), (70, 40, 55)):
        circle(c, x, y, r, (0.95, 0.65, 0.70), stroke=L.INK, lw=6)


WHITE_ = (1, 1, 1)

PROPS = {"basin": _basin, "bed": _bed, "scalpel": _scalpel, "paper": _paper, "book": _book, "bell": _bell,
         "candle": _candle, "microscope": _microscope, "germs": _germs, "heart": _heart, "brain": _brain,
         "mug": _mug, "bottle": _bottle, "bucket": _bucket, "cannon": _cannon, "plate": _plate, "crate": _crate,
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
    if p and _PAINT and name not in ("germs",):  # inside a painting: lit by the scene, moving with the floor
        from .depth_scene import draw_lit, scene_light
        sc, k, mv, am = _PAINT
        x, y = float(it.get("x", 540)), float(it.get("y", 960))
        px, py, ps = sc.place(x, y, k, mv, am)
        sz = float(it.get("s", 1.0)) * ps * (p if it.get("anim", "pop" if "in" in it else "none") in ("pop", "grow") else 1.0)
        draw_lit(c, PROPS[name], px, py, max(0.01, sz), scene_light(sc, x, y))
    elif p:
        if _PAINT:  # floating things (germs) still drift with the camera
            sc, k, mv, am = _PAINT
            px, py, ps = sc.place(float(it.get("x", 540)), float(it.get("y", 960)), k, mv, am)
            it = {**it, "x": px, "y": py, "s": float(it.get("s", 1.0)) * ps}
        placed(c, it, p, PROPS[name])


def i_character(c, it, T, t0, lt):
    if it.get("role") in cast.ROLES:
        return _cast_member(c, it, T, t0)
    role = ROLES.get(it.get("role", "person"))
    if role is None:
        raise BoardError(f"unknown role {it.get('role')!r}; known: {', '.join(list(cast.ROLES) + list(ROLES))}")
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


STILL_POSES = ("sit", "lie", "kneel", "beg", "fall")


def _cast_member(c, it, T, t0):
    """A cast member (studio/story/cast.py), animated: walks in from the side on its "in" word (anim "enter",
    the default for standing characters), moves smoothly between poses, hops a little when its mood changes,
    blinks and breathes. "states" change pose/mood/facing/position on spoken words.
    "outfit": {"top": COLOUR, "legs": COLOUR, "extras": [...]} gives a story's hero a look of their own;
    "name_tag": "SEMMELWEIS" shows the name above the head for 2.5 s after they appear."""
    pose, mood, face = it.get("pose", "stand"), it.get("mood", "calm"), int(it.get("face", 1))
    x, y = float(it.get("x", 540)), float(it.get("y", 1500))
    prev_pose, t_pose, t_mood = None, -99.0, -99.0
    for st in it.get("states", []):  # e.g. [{"at": "ran#1", "pose": "run", "mood": "scared", "to_x": 900}]
        ts = when(st["at"], t0)
        if T >= ts:
            if st.get("pose", pose) != pose:
                prev_pose, t_pose = pose, ts
            if st.get("mood", mood) != mood:
                t_mood = ts
            pose, mood, face = st.get("pose", pose), st.get("mood", mood), int(st.get("face", face))
            k = ease((T - ts) / float(st.get("dur", 0.8)))
            moving = ("to_x" in st or "to_y" in st) and k < 1
            x += (float(st["to_x"]) - x) * k if "to_x" in st else 0
            y += (float(st["to_y"]) - y) * k if "to_y" in st else 0
            if moving and pose in ("stand", "point", "hold", "wave", "think"):
                prev_pose, pose, t_pose = None, "walk", ts
    for name, known in ((pose, cast.POSES), (mood, cast.MOODS)):
        if name not in known:
            raise BoardError(f"unknown {'pose' if known is cast.POSES else 'mood'} {name!r}; known: {', '.join(known)}")
    hold = it.get("hold")
    if hold and hold not in PROPS:
        raise BoardError(f"unknown prop {hold!r} to hold; known: {', '.join(sorted(PROPS))}")
    outfit = {}
    for k_, v in (it.get("outfit") or {}).items():
        outfit[k_] = col(v) if k_ in ("top", "legs") else v
    seed = (x * 0.013 + y * 0.007) % 6.28
    anim = it.get("anim", ("enter" if pose not in STILL_POSES else "pop") if "in" in it else "none")
    tin = when(it.get("in"), t0) + float(it.get("delay", 0)) if "in" in it else -99.0
    if T < tin - 1e-6:
        return
    draw_pose, draw_face = pose, face
    if anim == "enter" and T < tin + 0.7:  # walk in from the nearer side of the frame
        k = ease((T - tin) / 0.7)
        side = -1 if x < 540 else 1
        start = x + side * 520
        x = start + (x - start) * k
        draw_pose, draw_face, prev_pose = "walk", -side, None
        it2 = {**it, "anim": "none"}
    else:
        it2 = {**it, "anim": anim if anim != "enter" else "none"}
    p = appear(it2, T, t0) if "in" in it else 1.0
    if not p:
        return
    blend = min(1.0, (T - t_pose) / 0.35) if prev_pose else 1.0
    hop = (T - t_mood) / 0.3 if 0 <= T - t_mood < 0.3 else 0.0
    if _PAINT:
        from .depth_scene import draw_lit, scene_light
        sc, k, mv, am = _PAINT
        px, py, ps = sc.place(x, y, k, mv, am)
        light = scene_light(sc, float(it.get("x", 540)), float(it.get("y", 1500)))
        sz = float(it.get("s", 1.0)) * ps * (p if anim == "pop" else 1.0)
        draw_lit(c, lambda c: cast.draw(c, it["role"], draw_pose, mood, T + float(it.get("phase", 0)), draw_face,
                                        float(it.get("look", 0)), hold_fn=PROPS.get(hold), prev_pose=prev_pose,
                                        blend=blend, outfit=outfit, seed=seed, hop=hop), px, py, max(0.01, sz), light)
        _tag(c, it, T, t0, tin, px, py)
        return
    placed(c, {**it2, "x": x, "y": y}, p,
           lambda c: cast.draw(c, it["role"], draw_pose, mood, T + float(it.get("phase", 0)), draw_face,
                               float(it.get("look", 0)), hold_fn=PROPS.get(hold), prev_pose=prev_pose, blend=blend,
                               outfit=outfit, seed=seed, hop=hop))
    _tag(c, it, T, t0, tin, x, y)


def _tag(c, it, T, t0, tin, x, y):
    tag = it.get("name_tag")
    if tag and T < max(tin, t0) + 2.5:
        h = 380 * float(it.get("s", 1.0)) * cast.ROLES[it["role"]].get("scale", 1.0)
        a_ = min(1.0, (T - max(tin, t0)) / 0.25) * min(1.0, (max(tin, t0) + 2.5 - T) / 0.3)
        c.save(); c.push_group()
        _name_tag(c, str(tag), x, y - h - 40)
        c.pop_group_to_source(); c.paint_with_alpha(max(0.0, a_)); c.restore()


def _name_tag(c, text, x, y):
    """A small dark label with the person's name (first appearance of a story's hero)."""
    c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(50)
    e = c.text_extents(text)
    w, h = e.width + 48, 74
    rrect(c, x - w / 2, y - h, w, h, 20, col("ink"))
    c.set_source_rgb(*col("lemon")); c.move_to(x - e.width / 2 - e.x_bearing, y - h / 2 - e.height / 2 - e.y_bearing)
    c.show_text(text)


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


def i_hands(c, it, T, t0, lt):
    """Close-up of two hands: dirty (germs) and/or washing (bubbles) from triggers."""
    import math as _m
    x, y, s = float(it.get("x", 540)), float(it.get("y", 1000)), float(it.get("s", 1.0))
    wash = ease((T - when(it["wash_at"], t0)) / 1.2) if "wash_at" in it else 0.0
    dirty = (1.0 if it.get("dirty") else 0.0) * (1 - wash)
    skin = col(it.get("skin"), "skin")
    c.save(); c.translate(x, y); c.scale(s, s)
    for sx in (-1, 1):
        c.save(); c.translate(sx * 120, 0); c.rotate(sx * 0.25 + _m.sin(T * 8) * 0.05 * wash)
        rrect(c, -95, -150, 190, 300, 90, skin, stroke=L.INK, lw=8)
        for k in range(4):
            rrect(c, -85 + k * 45, -260, 40, 140, 20, skin, stroke=L.INK, lw=6)
        rrect(c, sx * 70 - 22, -120, 44, 120, 22, skin, stroke=L.INK, lw=6)
        c.restore()
    if dirty > 0:
        for k in range(7):
            c.save(); c.translate(-200 + k * 65, -60 + (k % 3) * 70); c.scale(0.45, 0.45)
            c.push_group(); _germs(c); c.pop_group_to_source(); c.paint_with_alpha(dirty); c.restore()
    if wash > 0:
        for k in range(14):
            a = T * 3 + k
            circle(c, -230 + (k * 37) % 460, -200 + ((k * 53 + T * 80) % 380), 14 + (k % 4) * 6, (1, 1, 1), 0.75 * min(1, wash * 2),
                   stroke=(0.6, 0.75, 0.85), lw=3)
    c.restore()


ITEMS = {"hands": i_hands, "text": i_text, "prop": i_prop, "character": i_character, "bar": i_bar, "calendar": i_calendar,
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
    elif t in settings.SETTINGS:
        tone = bg.get("tone", "day")
        if tone not in settings.TONES:
            raise BoardError(f"unknown tone {tone!r}; known: {', '.join(settings.TONES)}")
        settings.draw(c, t, T, tone)
    else:
        raise BoardError(f"unknown background {t!r}; known: gradient, sea, none, {', '.join(settings.SETTINGS)}")


# ---------- shots ----------
OVERLAY = {"text", "calendar", "cross", "dim"}       # drawn on top of the camera (never cropped)
FOCUSABLE = {"character", "prop", "card", "hands", "bar", "ship", "finger", "group"}


def _target(it):
    """Where to point the camera for an item, and how close."""
    x, y, s = float(it.get("x", 540)), float(it.get("y", 960)), float(it.get("s", 1.0))
    if it.get("type") == "character":
        h = 380 * s * (cast.ROLES[it["role"]].get("scale", 1.0) if it.get("role") in cast.ROLES else 0.9)
        return x, y - h * 0.55, max(1.0, min(1.55, 1100 / max(h, 1)))  # whole head and body stay in frame
    if it.get("type") == "group":
        g = it["grid"]
        return g["x"] + (g["cols"] - 1) * g["dx"] / 2, g["y"] + (g.get("rows", 1) - 1) * g.get("dy", 0) / 2, 1.15
    if it.get("type") == "hands":
        return x, y - 60, 1.25
    if it.get("type") == "card":  # whole panel stays in frame
        return x, y, max(1.0, min(1.35, 1.1 / max(s, 0.5)))
    if it.get("type") == "prop":
        return x, y, max(1.0, min(1.6, 1.5 / max(s, 0.5)))
    return x, y, max(1.0, min(1.8, 1.4 / max(s, 0.5)))


def _clamp(cx, cy, z):
    hw, hh = 540 / z, 960 / z
    return min(max(cx, hw), 1080 - hw), min(max(cy, hh), 1920 - hh), z


def _fit(sh, t0, t1):
    """The tightest steady framing that keeps everything the shot shows (people, props, bars; labels excluded)
    in view for the whole shot, with a margin. None if there's nothing to frame."""
    xs0, ys0, xs1, ys1 = [], [], [], []
    for it in sh.get("items", []):
        t = it.get("type")
        sc = float(it.get("s", 1.0))
        x, y = float(it.get("x", 540)), float(it.get("y", 960))
        boxes = []
        if t == "character":
            for T in (t0 + 0.05, (t0 + t1) / 2, t1 - 0.05):
                boxes += [_boxes(it, t0, T).get("body")]
        elif t == "prop":
            boxes = [(x - 140 * sc, y - 220 * sc, x + 140 * sc, y + 40 * sc)]
        elif t == "hands":
            boxes = [(x - 260 * sc, y - 300 * sc, x + 260 * sc, y + 180 * sc)]
        elif t == "bar":
            boxes = [(float(it["x"]) - 100, float(it["base_y"]) - float(it["h"]), float(it["x"]) + 100, float(it["base_y"]))]
        elif t == "group":
            g = it["grid"]; cols, rows = int(g.get("cols", 1)), int(g.get("rows", 1))
            boxes = [(g["x"] - 160, g["y"] - 420, g["x"] + (cols - 1) * g.get("dx", 0) + 160, g["y"] + (rows - 1) * g.get("dy", 0) + 40)]
        elif t in ("finger", "arm_scar", "ship", "ropes", "card"):
            return None  # drawn for the full frame
        for b_ in boxes:
            if b_:
                xs0.append(b_[0]); ys0.append(b_[1]); xs1.append(b_[2]); ys1.append(b_[3])
    if not xs0:
        return None
    x0, y0, x1, y1 = min(xs0), min(ys0), max(xs1), max(ys1)
    w, h = (x1 - x0) * 1.25, (y1 - y0) * 1.3 + 260  # margin, plus room for the caption band below
    z = max(1.0, min(1.6, W / max(w, 1), H / max(h, 1)))
    return ((x0 + x1) / 2, (y0 + y1) / 2 + 90 / z, z)


def make_camera(sh, t0, t1, beat=1.0):
    """The camera, like an editor would use it (not a zoom template): each shot opens on one framing ("camera":
    "wide" (default) | "medium" | "close", close = on the first character) and holds it with a slow sideways drift.
    It cuts (instantly, no zooming) to a close-up only when something important appears ("in") and the cut shows a
    clearly different picture, at most once every 0.8 s. "camera": "static" = no drift and no cuts."""
    if sh.get("camera") == "static":
        return None
    fy = float(sh.get("focus", 900))
    items = [it for it in sh.get("items", []) if it.get("type") in FOCUSABLE]
    mode = sh.get("camera", "fit")
    chars = [it for it in items if it.get("type") in ("character", "hands")]
    if mode == "close" and chars:
        x, y, z = _target(chars[0]); first = (x, y, max(1.25, z))
    elif mode == "medium":
        first = (540, fy + 60, 1.18)
    elif mode == "wide":
        first = (540, fy, 1.0)
    else:  # "fit" (default): frame the shot's people and things tightly, like a camera operator would
        first = _fit(sh, t0, t1) or (540, fy, 1.0)
    def clean(fr, T):
        """True if no head is half in, half out of this framing at time T (and labels don't land on faces)."""
        cx, cy, z = _clamp(*fr)
        for it in sh.get("items", []):
            if it.get("type") != "character" or not _on_screen(it, t0, T + 0.3):
                continue
            hd = _boxes(it, t0, T + 0.3).get("head")
            if not hd:
                continue
            v = ((hd[0] - cx) * z + 540, (hd[1] - cy) * z + 960, (hd[2] - cx) * z + 540, (hd[3] - cy) * z + 960)
            visible = v[2] > 0 and v[0] < W and v[3] > 0 and v[1] < H
            if visible and not (v[0] >= 0 and v[2] <= W and v[1] >= 0):
                return False
        return True

    if not clean(first, t0):
        first = next((f for f in ((first[0], first[1], 1.0), (540, fy, 1.0)) if clean(f, t0)), (540, fy, 1.0))
    beats = [(t0, first)]
    for it in sorted((i for i in items if "in" in i), key=lambda i: when(i["in"], t0)):
        te = when(it["in"], t0)
        tx, ty, tz = _target(it)
        if not (t0 + 0.3 < te < t1 - 0.8 and te - beats[-1][0] >= 0.8 and it.get("cut", True)):
            continue
        cur = _clamp(*beats[-1][1])
        for fr in ((tx, ty, max(1.2, tz)), (tx, ty, 1.35), (tx, ty, 1.2)):
            new = _clamp(*fr)
            big_change = abs(new[2] / cur[2] - 1) >= 0.18 or abs(new[0] - cur[0]) >= 200 or abs(new[1] - cur[1]) >= 200
            if big_change and clean(fr, te):
                beats.append((te, fr))
                break
    drift = 1 if int(t0 * 10) % 2 else -1

    def cam(T):
        tb, (x, y, z) = beats[0]
        for b_ in beats:
            if b_[0] <= T + 1e-6:
                tb, (x, y, z) = b_
        nxt = next((b_[0] for b_ in beats if b_[0] > tb), t1)
        k = (T - tb) / max(0.5, nxt - tb)
        return _clamp(x + drift * 24 * (k - 0.5), y, z)  # slow sideways drift, no zoom
    cam.beats = beats
    return cam


def activity(board):
    """Times (s) when something new happens on screen: a new shot, something appears, a character changes
    pose/mood/place, a bar grows, a count runs, an action trigger fires. Camera moves are NOT counted:
    pace must come from things happening, not from zooming."""
    built, _ = build_shots(board)
    out = []
    for sh, (t0, *_r) in zip(board.get("shots", []), built):
        out.append(t0)

        def add(trig):
            try:
                out.append(when(trig, t0))
            except (BoardError, KeyError, ValueError):
                pass
        for it in sh.get("items", []):
            src = [it] + ([it["item"]] if isinstance(it.get("item"), dict) else [])
            for x in src:
                if "in" in x and x is it:
                    add(x["in"])
                for st in x.get("states", []):
                    add(st["at"])
                for k_, v in x.items():
                    if k_.endswith("_at") and isinstance(v, (str, int, float)):
                        add(v)
                if isinstance(x.get("regroup"), dict):
                    add(x["regroup"].get("at"))
                if isinstance(x.get("count"), dict):
                    add(x["count"].get("at"))
    return sorted(set(round(t, 2) for t in out))


def picture_changes(shots, dur, fps=10):
    """Times (s) when the picture changes: a new shot, or the camera cuts (moves > 40 px or zooms > 12%)."""
    out, prev = [], None
    for i in range(int(dur * fps)):
        T = i / fps
        idx = max(k for k, s in enumerate(shots) if s[0] <= T + 1e-6)
        cam = shots[idx][3] if len(shots[idx]) > 3 else None
        v = (idx,) + (tuple(cam(T)) if cam else (540, 960, 1.0))
        if prev is None or v[0] != prev[0] or abs(v[1] - prev[1]) > 40 or abs(v[2] - prev[2]) > 40 or abs(v[3] / prev[3] - 1) > 0.12:
            out.append(T)
        prev = v
    return out


# ---- painted 2.5D backgrounds (studio/story/depth_scene.py) ----
PAINT_DIR = None          # folder with bg_<id>.png + depth_<id>.png (set by the caller, e.g. the episode's paint/ folder)
_SCENES = {}
_PAINT = None             # (scene, k, move, amount) while a painted shot is being drawn


def paint_scene(pid):
    import os
    from pathlib import Path
    d = Path(PAINT_DIR or os.environ.get("STORY_PAINT_DIR", "") or ".")
    key = (str(d), pid)
    if key not in _SCENES:
        bg, dp = d / f"bg_{pid}.png", d / f"depth_{pid}.png"
        if not bg.exists() or not dp.exists():
            raise BoardError(f"painted background {pid!r} not found in {d} (bg_{pid}.png + depth_{pid}.png)")
        from .depth_scene import DepthScene
        _SCENES[key] = DepthScene(bg, dp)
    return _SCENES[key]


def build_shots(board):
    """Turn storyboard.json into shots for lib.frame: (t0, scene_fn, focus_y, camera_fn, overlay_fn)."""
    starts = []
    for i, sh in enumerate(board["shots"]):
        starts.append(0.0 if i == 0 else when(sh["at"], 0.0))
    shots = []
    for i, sh in enumerate(board["shots"]):
        t0 = starts[i]
        t1 = starts[i + 1] if i + 1 < len(starts) else max(L.DUR, t0 + 0.5)
        auto = board.get("camera", "auto") == "auto"

        def draw(c, lt, T, sh=sh, t0=t0, t1=t1, auto=auto):
            global _PAINT
            bg = sh.get("bg", "gradient")
            if isinstance(bg, dict) and bg.get("type") == "paint":
                sc = paint_scene(bg["id"])
                k = (T - t0) / max(0.3, t1 - t0)
                mv, am = bg.get("move", "push"), float(bg.get("amount", 1.0))
                sc.draw(c, k, mv, am)
                _PAINT = (sc, k, mv, am)
            else:
                background(c, bg, T)
            try:
                for it in sh.get("items", []):
                    if not (auto and it.get("type") in OVERLAY):
                        draw_item(c, it, T, t0, lt)
            finally:
                _PAINT = None

        def over(c, lt, T, sh=sh, t0=t0):
            for it in sh.get("items", []):
                if it.get("type") in OVERLAY:
                    draw_item(c, it, T, t0, lt)
        draw.__name__ = sh.get("name", f"shot{i + 1}")
        painted = isinstance(sh.get("bg"), dict) and sh["bg"].get("type") == "paint"
        cam = make_camera(sh, t0, t1) if auto and not painted else None
        shots.append((t0, draw, float(sh.get("focus", 900)), cam, over if auto else None))
    return shots, {w.lower() for w in board.get("key_words", [])}


DECOR = {"text", "dim", "glow", "rays", "floor", "cross"}  # these alone are not a picture


def _on_screen(it, t0, T):
    if it.get("type") == "bar" and when(it.get("grow_at"), t0) > T + 0.05:
        return False  # a bar is nothing until it grows
    for k in ("in", "from"):
        if k in it and when(it[k], t0) > T + 0.05:
            return False
    return not ("until" in it and when(it["until"], t0) <= T)


def _pos(it, t0, T):
    """Where a character stands at time T (follows its states' to_x / to_y)."""
    x, y = float(it.get("x", 540)), float(it.get("y", 1500))
    pose = it.get("pose", "stand")
    for st in it.get("states", []):
        ts = when(st["at"], t0)
        if T >= ts:
            k = ease((T - ts) / float(st.get("dur", 0.8)))
            x += (float(st["to_x"]) - x) * k if "to_x" in st else 0
            y += (float(st["to_y"]) - y) * k if "to_y" in st else 0
            pose = st.get("pose", pose)
    return x, y, pose


def _boxes(it, t0, T):
    """Screen boxes (x0, y0, x1, y1) of an item at time T: {"head": ..., "body": ...} or {"label": ...}."""
    t = it.get("type")
    s = float(it.get("s", 1.0))
    if t == "character" and it.get("role") in cast.ROLES:
        x, y, pose = _pos(it, t0, T)
        h = 380 * s * cast.ROLES[it["role"]].get("scale", 1.0)
        if pose == "lie":
            return {"body": (x - h * 0.5, y - h * 0.45, x + h * 0.5, y)}
        y += {"sit": 95, "kneel": 70, "beg": 70}.get(pose, 0) * s
        return {"head": (x - 0.24 * h, y - h, x + 0.24 * h, y - 0.6 * h), "body": (x - 0.3 * h, y - h, x + 0.3 * h, y)}
    if t == "text":
        size, n = float(it.get("size", 90)) * s, len(str(it.get("text", "")))
        x, y = float(it.get("x", 540)), float(it.get("y", 960))
        return {"label": (x - 0.31 * size * n, y - 0.78 * size, x + 0.31 * size * n, y + 0.12 * size)}
    if t == "calendar":
        x, y = float(it.get("x", 540)), float(it.get("y", 960))
        return {"label": (x - 150 * s, y - 170 * s, x + 150 * s, y + 170 * s)}
    if t == "card":
        x, y = float(it.get("x", 540)), float(it.get("y", 960))
        return {"label": (x - 380 * s, y - 190 * s, x + 380 * s, y + 190 * s)}
    if t == "bar" and when(it.get("grow_at"), t0) <= T:
        x, base, w, h = float(it["x"]), float(it["base_y"]), float(it.get("w", 140)), float(it["h"])
        return {"bar": (x - w / 2, base - h, x + w / 2, base)}
    return {}


def _overlap(a, b):
    """Overlap area as a share of the smaller box."""
    w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    return w * h / max(1.0, min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])))


def layout_problems(board):
    """Composition mistakes a viewer notices: a label or calendar over a face, a bar over a person, two heads on
    top of each other, a person cut off by the frame edge. Checked through every shot, every 0.25 s."""
    built, _ = build_shots(board)
    starts = [b_[0] for b_ in built] + [L.DUR]
    out = []
    for sh, bs, a, b in zip(board.get("shots", []), built, starts, starts[1:]):
        name, found = sh.get("name", "a shot"), set()
        items = sh.get("items", [])
        cam = bs[3] if len(bs) > 3 else None
        T = a
        while T < b:
            cx, cy, z = cam(T) if cam else (540, 960, 1.0)

            def view(it, bx):  # what the viewer sees: overlays stay put, everything else moves with the camera
                if it.get("type") in OVERLAY:
                    return bx
                return {k: ((v[0] - cx) * z + 540, (v[1] - cy) * z + 960, (v[2] - cx) * z + 540, (v[3] - cy) * z + 960)
                        for k, v in bx.items()}
            vis = [(it, view(it, _boxes(it, a, T))) for it in items if _on_screen(it, a, T)]
            people = [(it, bx) for it, bx in vis if "head" in bx or ("body" in bx and it.get("type") == "character")]
            for it, bx in vis:
                for key in ("label", "bar"):
                    if key in bx:
                        for p_, pb in people:
                            if "head" in pb and _overlap(bx[key], pb["head"]) > 0.15:
                                found.add(f"{name}: a {it['type']} covers the {p_['role']}'s face; move one of them")
                            elif key == "bar" and _overlap(bx[key], pb["body"]) > 0.25:
                                found.add(f"{name}: a bar stands on top of the {p_['role']}; move one of them")
            for i, (p1, b1) in enumerate(people):
                for p2, b2 in people[i + 1:]:
                    if "head" in b1 and "head" in b2 and _overlap(b1["head"], b2["head"]) > 0.25:
                        found.add(f"{name}: the {p1['role']}'s and {p2['role']}'s heads overlap; space them apart")
                hd = b1.get("head") or b1["body"]
                inside = hd[0] >= 0 and hd[2] <= W and hd[1] >= 0
                visible = hd[2] > 0 and hd[0] < W and hd[3] > 0
                if visible and not inside:
                    found.add(f"{name}: the {p1['role']}'s head is cut by the frame edge; move them inward")
            T += 0.25
        out += sorted(found)
    return out


def quality(board):
    """Benchmark-level rules (stricter than validate). The AI writer must pass these; older episodes show them as warnings.
    Based on the benchmark research: a real picture from the first frame, a new picture about every second,
    almost no label-only shots, places instead of plain colour."""
    problems = []
    shots = board.get("shots") or []
    try:
        built, _ = build_shots(board)
    except BoardError as e:
        return [f"timing: {e}"]
    starts = [s[0] for s in built] + [L.DUR]
    label_only, plain = 0, 0
    for i, (sh, (a, *_), b) in enumerate(zip(shots, built, starts[1:])):
        pics = [it for it in sh.get("items", []) if it.get("type") not in DECOR]
        name = sh.get("name", f"shot {i + 1}")
        if not pics:
            label_only += 1
            problems.append(f"{name}: only words on screen; add a character, prop or scene")
            continue
        pics = [it for it in pics if not (it.get("type") == "prop" and float(it.get("s", 1.0)) < 0.7)]
        T, empty = a, 0.0
        while T < b:
            empty = 0.0 if any(_on_screen(it, a, T) for it in pics) else empty + 0.25
            if empty > 0.5:
                problems.append(f"{name}: no picture for ~1s at {T:.1f}s (items appear later); show something from the start")
                break
            T += 0.25
        bg = sh.get("bg", "gradient")
        bg = bg.get("type") if isinstance(bg, dict) else bg
        if bg in ("gradient", None, "none") and not any(it.get("type") in ("ship", "arm_scar", "ropes", "hands") for it in pics):
            plain += 1
    for sh in shots:  # the font has letters, digits and common punctuation only: anything else shows as a box
        for it in sh.get("items", []):
            bad = sorted({ch for ch in str(it.get("text", "")) if not (ch.isascii() and ch.isprintable())})
            if it.get("type") == "text" and bad:
                problems.append(f"{sh.get('name', 'a shot')}: label {it['text']!r} uses {bad}, which the font can't draw; "
                                "use plain words (e.g. TO instead of an arrow)")
    first = shots[0] if shots else {}
    lead = [it for it in first.get("items", []) if it.get("type") in ("character", "hands", "group", "ship", "arm_scar", "finger")
            and _on_screen(it, built[0][0], built[0][0] + 0.3)]
    if not lead:
        problems.append("opening shot: start mid-action with a person or body part on screen in the first 0.3 s")
    elif not (first.get("camera") == "close" or any(it.get("type") in ("hands", "arm_scar", "finger") or
                                                    float(it.get("s", 1.0)) >= 1.6 for it in lead)):
        problems.append('opening shot: show the action up close ("camera": "close", or the person at s 1.6+), '
                        "not a small figure in a big room")
    problems += layout_problems(board)
    if label_only > 0.1 * len(shots):
        problems.append(f"{label_only} of {len(shots)} shots are words only (limit 10%)")
    if plain > len(shots) / 2:
        problems.append(f"{plain} of {len(shots)} shots sit on a plain colour; use a place (bg: ward, street, room, lab, deck)")
    end = L.WORDS[-1]["end"] if L.WORDS else L.DUR  # the silent tail after the last word doesn't count
    ev = [t for t in activity(board) if t < end]
    gaps = [(y - x, x) for x, y in zip(ev, ev[1:] + [end])]
    worst = max(gaps)
    if L.DUR / max(1, len(ev)) > 1.3 or worst[0] > 1.6:
        problems.append(f"pace: something new happens every {L.DUR / max(1, len(ev)):.2f}s, but nothing happens for "
                        f"{worst[0]:.1f}s from {worst[1]:.1f}s; add an action (an entrance, a pose or mood change, "
                        "an object appearing) there (target about 1s, never over 1.6s)")
    return problems


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
    for (a, fn, *_), b in zip(built, starts[1:]):
        if b - a > float(board.get("max_shot_seconds", 4.5)):
            problems.append(f"{fn.__name__} lasts {b - a:.1f}s; keep shots under {board.get('max_shot_seconds', 4.5)}s")
    if sample:  # draw the middle of every shot once: catches unknown props, moods, colours, missing fields
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 108, 192)
        for (a, fn, fy, *rest), b in zip(built, starts[1:]):
            c = cairo.Context(surf); c.scale(0.1, 0.1)
            for T in (a + 0.05, (a + b) / 2, b - 0.05):
                try:
                    fn(c, T - a, T)
                    if rest and rest[0]:
                        rest[0](T)
                    if len(rest) > 1 and rest[1]:
                        rest[1](c, T - a, T)
                except (BoardError, KeyError, TypeError, ValueError) as e:
                    problems.append(f"{fn.__name__}: {e}")
                    break
    return problems
