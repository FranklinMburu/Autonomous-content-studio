"""The cast: original, consistent cartoon people with bendable limbs, poses, actions and expressions.

Style (ours): a big round head, a soft pear-shaped body in an outfit, thick rounded limbs with round hands and
shoes, bold ink outlines. Feet are at (0, 0); s=1 is about 380 px tall. Facing right by default (face=-1 mirrors).

    draw(c, role, pose="stand", mood="calm", t=0.0, face=1, look=0.0, hold=None)

Roles, poses and moods are listed in ROLES, POSES and MOODS; storyboards may only use those names.
"""
import math
import cairo

INK = (0.08, 0.07, 0.10)
WHITE = (1, 1, 1)
SKINS = {"light": (0.98, 0.84, 0.72), "tan": (0.88, 0.68, 0.50), "brown": (0.66, 0.46, 0.31), "dark": (0.45, 0.30, 0.20)}

# role -> look. top: outfit colour; style: coat|dress|shirt|apron|robe|uniform; hair: (style, colour); hat; extras
ROLES = {
    "doctor":    {"skin": "light", "top": (0.16, 0.16, 0.20), "style": "coat", "hair": ("side", (0.30, 0.20, 0.12)), "extras": ["mustache"], "legs": (0.20, 0.20, 0.24)},
    "student":   {"skin": "tan", "top": (0.35, 0.28, 0.22), "style": "coat", "hair": ("short", (0.12, 0.10, 0.09)), "extras": [], "legs": (0.25, 0.22, 0.20)},
    "mother":    {"skin": "light", "top": (0.62, 0.30, 0.38), "style": "dress", "hair": ("bun", (0.45, 0.25, 0.12)), "hat": "bonnet", "extras": [], "legs": None},
    "midwife":   {"skin": "brown", "top": (0.30, 0.42, 0.55), "style": "apron", "hair": ("bun", (0.10, 0.08, 0.07)), "hat": "cap", "extras": [], "legs": None},
    "child":     {"skin": "tan", "top": (0.95, 0.65, 0.20), "style": "shirt", "hair": ("messy", (0.25, 0.15, 0.08)), "extras": [], "legs": (0.25, 0.35, 0.55), "scale": 0.68},
    "elder":     {"skin": "light", "top": (0.40, 0.36, 0.30), "style": "coat", "hair": ("bald", (0.85, 0.85, 0.85)), "extras": ["beard", "glasses"], "legs": (0.30, 0.28, 0.25)},
    "worker":    {"skin": "dark", "top": (0.25, 0.45, 0.35), "style": "shirt", "hair": ("short", (0.08, 0.07, 0.07)), "hat": "cap_flat", "extras": [], "legs": (0.22, 0.25, 0.35)},
    "scientist": {"skin": "tan", "top": (0.94, 0.94, 0.92), "style": "coat", "hair": ("side", (0.10, 0.08, 0.08)), "extras": ["glasses"], "legs": (0.25, 0.25, 0.30)},
    "noble":     {"skin": "light", "top": (0.55, 0.12, 0.18), "style": "robe", "hair": ("long", (0.75, 0.62, 0.30)), "hat": "crown", "extras": [], "legs": None},
    "guard":     {"skin": "brown", "top": (0.20, 0.25, 0.45), "style": "uniform", "hair": ("short", (0.08, 0.07, 0.07)), "hat": "helmet", "extras": [], "legs": (0.15, 0.15, 0.20)},
    "sailor2":   {"skin": "tan", "top": (0.12, 0.25, 0.45), "style": "shirt", "hair": ("short", (0.30, 0.18, 0.10)), "hat": "bandana", "extras": ["stripes"], "legs": (0.85, 0.82, 0.75)},
    "patient":   {"skin": "light", "top": (0.90, 0.88, 0.82), "style": "robe", "hair": ("long", (0.40, 0.25, 0.15)), "extras": [], "legs": None},
}

MOODS = ["calm", "happy", "laugh", "sad", "sick", "scared", "shock", "angry", "doubt", "smug", "pain"]

# pose -> (left arm (shoulder, elbow), right arm, left leg (hip, knee), right leg, body tilt, crouch px)
# angles in radians: 0 = hanging straight down; positive = forward (toward the face direction).
_P = {
    "stand":     ((0.15, 0.1), (-0.15, 0.1), (0.05, 0), (-0.05, 0), 0.0, 0),
    "point":     ((0.15, 0.1), (1.55, 0.0), (0.05, 0), (-0.05, 0), 0.0, 0),
    "wave":      ((0.15, 0.1), (2.6, -0.6), (0.05, 0), (-0.05, 0), 0.0, 0),
    "hands_up":  ((2.8, 0.2), (2.8, 0.2), (0.12, 0), (-0.12, 0), 0.0, 0),
    "hold":      ((1.1, 0.5), (1.0, 0.6), (0.05, 0), (-0.05, 0), 0.0, 0),
    "scrub":     ((0.9, 1.1), (0.9, 1.1), (0.05, 0), (-0.05, 0), 0.08, 0),
    "shrug":     ((0.6, -1.6), (0.6, -1.6), (0.05, 0), (-0.05, 0), 0.0, 0),
    "think":     ((0.2, 0.1), (0.9, 2.2), (0.05, 0), (-0.05, 0), 0.0, 0),
    "facepalm":  ((0.2, 0.1), (1.0, 2.3), (0.05, 0), (-0.05, 0), 0.15, 0),
    "kneel":     ((0.9, 0.6), (0.7, 0.8), (1.4, -1.5), (0.0, -1.6), 0.1, 70),
    "beg":       ((1.6, 0.6), (1.5, 0.7), (1.4, -1.5), (0.0, -1.6), 0.2, 70),
    "sit":       ((0.4, 0.5), (0.4, 0.5), (1.5, -1.5), (1.5, -1.5), 0.0, 95),
    "fall":      ((2.4, 0.3), (-2.2, 0.3), (0.9, 0.2), (-0.6, 0.4), -0.6, 20),
    "walk":      None, "run": None, "lie": None,
}
POSES = sorted(_P)


def _rgb(c, col, a=1.0):
    c.set_source_rgba(col[0], col[1], col[2], a)


def _circle(c, x, y, r, fill, lw=6, a=1.0):
    c.arc(x, y, r, 0, 2 * math.pi); _rgb(c, fill, a); c.fill_preserve(); _rgb(c, INK); c.set_line_width(lw); c.stroke()


def _limb(c, x, y, a1, a2, l1, l2, w, col, end=None, end_r=0, end_col=None, face=1):
    """Two-segment limb from (x, y). Returns the end point."""
    x1, y1 = x + face * math.sin(a1) * l1, y + math.cos(a1) * l1
    x2, y2 = x1 + face * math.sin(a1 + a2) * l2, y1 + math.cos(a1 + a2) * l2
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for lw, colr in ((w + 10, INK), (w, col)):
        c.move_to(x, y); c.line_to(x1, y1); c.line_to(x2, y2); _rgb(c, colr); c.set_line_width(lw); c.stroke()
    if end == "hand":
        _circle(c, x2, y2, end_r, end_col, 5)
    elif end == "shoe":
        c.save(); c.translate(x2 + face * 10, y2 + 4); c.scale(1.5, 0.8); _circle(c, 0, 0, end_r, end_col, 6); c.restore()
    return x2, y2


def _pose(pose, t):
    if pose == "walk" or pose == "run":
        k = 7 if pose == "walk" else 13
        amp = 0.45 if pose == "walk" else 0.9
        s = math.sin(t * k)
        return ((-s * amp * 0.8, 0.3 + (0.6 if pose == "run" else 0)), (s * amp * 0.8, 0.3 + (0.6 if pose == "run" else 0)),
                (s * amp, max(0, -s) * 0.9), (-s * amp, max(0, s) * 0.9), 0.12 if pose == "run" else 0.03,
                abs(math.cos(t * k)) * (-14 if pose == "run" else -6))
    return _P.get(pose, _P["stand"])


def _face(c, mood, look, t, extras, skin):
    ex = look * 8
    # eyes
    for sx in (-28, 30):
        c.save(); c.translate(sx, -8)
        if mood in ("laugh", "happy") and mood == "laugh":
            c.set_line_width(6); _rgb(c, INK); c.arc(0, 6, 14, math.pi * 1.1, math.pi * 1.9); c.stroke()
        else:
            r = 20 if mood not in ("shock", "scared") else 24
            _circle(c, 0, 0, r, WHITE, 4)
            pr = 8 if mood not in ("shock", "scared") else 5
            _rgb(c, INK); c.arc(ex + (2 if mood != "doubt" else -3), 2, pr, 0, 2 * math.pi); c.fill()
            if mood in ("sick", "sad"):
                _rgb(c, skin); c.rectangle(-22, -24, 44, 16); c.fill()   # heavy eyelids
                c.set_line_width(4); _rgb(c, INK); c.move_to(-21, -8); c.line_to(21, -8); c.stroke()
        c.restore()
    if "glasses" in extras:
        c.set_line_width(5); _rgb(c, INK)
        for sx in (-28, 30):
            c.arc(sx, -8, 26, 0, 2 * math.pi); c.new_sub_path()
        c.stroke(); c.move_to(-2, -8); c.line_to(4, -8); c.stroke()
    # brows
    c.set_line_width(7); _rgb(c, INK); c.set_line_cap(cairo.LINE_CAP_ROUND)
    br = {"angry": ((-44, -38, -14, -28), (14, -28, 46, -38)), "doubt": ((-44, -34, -14, -34), (14, -44, 46, -52)),
          "sad": ((-44, -30, -14, -40), (14, -40, 46, -30)), "sick": ((-44, -30, -14, -40), (14, -40, 46, -30)),
          "scared": ((-44, -42, -14, -50), (14, -50, 46, -42)), "shock": ((-44, -50, -14, -54), (14, -54, 46, -50)),
          "smug": ((-44, -36, -14, -38), (14, -42, 46, -36)), "pain": ((-44, -30, -14, -42), (14, -42, 46, -30))}
    for x1, y1, x2, y2 in br.get(mood, ((-42, -38, -14, -40), (14, -40, 44, -38))):
        c.move_to(x1, y1); c.line_to(x2, y2)
    c.stroke()
    # mouth
    c.set_line_width(6)
    if mood in ("happy", "smug"):
        c.arc(4, 26, 20, 0.2 * math.pi, 0.8 * math.pi); c.stroke()
    elif mood == "laugh":
        c.move_to(-22, 22); c.curve_to(-14, 60, 22, 60, 30, 22); c.close_path(); _rgb(c, (0.55, 0.10, 0.15)); c.fill_preserve(); _rgb(c, INK); c.stroke()
    elif mood in ("shock", "scared"):
        c.save(); c.translate(4, 38); c.scale(1, 1.3 if mood == "shock" else 0.8); _circle(c, 0, 0, 13, (0.45, 0.06, 0.10), 5); c.restore()
    elif mood in ("sad", "sick", "pain"):
        c.arc(4, 52, 20, 1.2 * math.pi, 1.8 * math.pi); c.stroke()
        if mood == "sick":
            _rgb(c, (0.55, 0.75, 0.45), 0.35); c.arc(0, 0, 78, 0, 2 * math.pi); c.fill()
        if mood == "pain":
            _rgb(c, (0.4, 0.7, 1.0)); c.arc(52, -20 + (t * 40) % 30, 7, 0, 2 * math.pi); c.fill()
    elif mood == "angry":
        c.move_to(-16, 40); c.line_to(22, 34); c.stroke()
    elif mood == "doubt":
        c.move_to(-14, 36); c.line_to(22, 30); c.stroke()
    else:
        c.move_to(-12, 34); c.curve_to(-2, 38, 10, 38, 20, 33); c.stroke()
    if "mustache" in extras:
        c.save(); c.translate(4, 20); c.scale(1, 0.45); _rgb(c, (0.25, 0.16, 0.10)); c.arc(-14, 0, 16, 0, 2 * math.pi); c.arc(20, 0, 16, 0, 2 * math.pi); c.fill(); c.restore()
    if "beard" in extras:
        c.move_to(-58, 10); c.curve_to(-50, 95, 58, 95, 64, 10); c.curve_to(30, 50, -20, 50, -58, 10); _rgb(c, (0.88, 0.88, 0.88)); c.fill_preserve(); _rgb(c, INK); c.set_line_width(5); c.stroke()


def _hood(c, hat):
    if hat == "bonnet":
        _circle(c, 0, 4, 100, (0.95, 0.92, 0.85), 6)


def _hair_back(c, style, col):
    if style == "long":
        c.move_to(-80, -20); c.curve_to(-95, 90, 95, 90, 82, -20); c.close_path(); _rgb(c, col); c.fill_preserve(); _rgb(c, INK); c.set_line_width(6); c.stroke()
    if style == "bun":
        _circle(c, -55, -60, 34, col, 6)


def _hair_front(c, style, col):
    c.set_line_width(6)
    if style == "bald":
        c.move_to(-78, -10); c.curve_to(-84, -40, -70, -50, -62, -46); _rgb(c, col); c.set_line_width(14); c.stroke()
        return
    c.new_path()
    if style in ("short", "side", "bun", "long"):
        c.arc(0, -6, 80, math.pi * 1.02, math.pi * 1.98)
        if style == "side":
            c.curve_to(60, -30, 10, -40, -20, -20)
        else:
            c.curve_to(40, -40, -40, -40, -78, -14)
        c.close_path()
    elif style == "messy":
        c.move_to(-80, -10)
        for k in range(9):
            a = math.pi * (1.0 + k / 8)
            r = 92 if k % 2 else 78
            c.line_to(r * math.cos(a), -6 + r * math.sin(a))
        c.close_path()
    _rgb(c, col); c.fill_preserve(); _rgb(c, INK); c.stroke()


def _hat(c, hat, col):
    if not hat:
        return
    c.set_line_width(6)
    if hat == "bonnet":  # a brim around the top of the face; the hood itself is drawn behind the head
        c.new_path(); c.arc(0, 0, 98, math.pi * 1.08, math.pi * 1.92); c.arc_negative(0, 0, 78, math.pi * 1.92, math.pi * 1.08)
        c.close_path(); _rgb(c, (0.95, 0.92, 0.85)); c.fill_preserve(); _rgb(c, INK); c.stroke()
    elif hat == "cap":
        c.save(); c.translate(0, -70); c.scale(1.4, 0.7); _circle(c, 0, 0, 52, WHITE, 5); c.restore()
    elif hat == "cap_flat":
        c.save(); c.translate(0, -62); c.scale(1.5, 0.55); _circle(c, 0, 0, 58, (0.30, 0.30, 0.32), 5); c.restore()
    elif hat == "bandana":
        c.arc(0, -10, 82, math.pi * 1.05, math.pi * 1.95); c.close_path(); _rgb(c, (0.84, 0.15, 0.24)); c.fill_preserve(); _rgb(c, INK); c.stroke()
    elif hat == "crown":
        c.move_to(-60, -62)
        for k, (x, y) in enumerate(((-60, -130), (-30, -90), (0, -140), (30, -90), (60, -130), (60, -62))):
            c.line_to(x, y)
        c.close_path(); _rgb(c, (0.98, 0.80, 0.20)); c.fill_preserve(); _rgb(c, INK); c.stroke()
    elif hat == "helmet":
        c.arc(0, -20, 86, math.pi, 2 * math.pi); c.close_path(); _rgb(c, (0.62, 0.64, 0.68)); c.fill_preserve(); _rgb(c, INK); c.stroke()


def _body(c, look, sk):
    top, style = look["top"], look["style"]
    c.set_line_width(7)
    c.new_path()
    if style in ("dress", "robe"):
        c.move_to(-58, -235); c.curve_to(-70, -150, -120, -40, -110, 0); c.line_to(110, 0)
        c.curve_to(120, -40, 70, -150, 58, -235); c.close_path()
    else:
        c.move_to(-62, -240); c.curve_to(-80, -170, -78, -120, -66, -95); c.line_to(66, -95)
        c.curve_to(78, -120, 80, -170, 62, -240); c.close_path()
    _rgb(c, top); c.fill_preserve(); _rgb(c, INK); c.stroke()
    if style == "coat":
        c.move_to(0, -235); c.line_to(0, -98); _rgb(c, INK); c.set_line_width(4); c.stroke()
        for y in (-200, -165, -130):
            _circle(c, 12, y, 5, (0.85, 0.75, 0.40), 3)
        c.move_to(-14, -238); c.line_to(0, -205); c.line_to(14, -238); _rgb(c, WHITE); c.fill()
    if style == "apron":
        c.move_to(-46, -200); c.line_to(46, -200); c.line_to(80, -8); c.line_to(-80, -8); c.close_path()
        _rgb(c, (0.97, 0.96, 0.92)); c.fill_preserve(); _rgb(c, INK); c.set_line_width(5); c.stroke()
    if style == "uniform":
        c.move_to(-62, -170); c.line_to(62, -170); _rgb(c, (0.85, 0.75, 0.40)); c.set_line_width(10); c.stroke()
    if "stripes" in look.get("extras", []):
        for k in range(3):
            c.rectangle(-70, -210 + k * 36, 140, 12); _rgb(c, WHITE, 0.85); c.fill()


def draw(c, role, pose="stand", mood="calm", t=0.0, face=1, look=0.0, hold=None, hold_fn=None):
    """Draw a cast member with feet at the current origin."""
    L = ROLES[role]
    skin = SKINS[L["skin"]]
    sc = L.get("scale", 1.0)
    c.save(); c.scale(sc, sc)
    if pose == "lie":
        c.translate(0, -60); c.rotate(-math.pi / 2 * face); pose = "stand"
    la, ra, ll, rl, tilt, crouch = _pose(pose, t)
    breath = math.sin(t * 2.2) * 3
    # shadow
    c.save(); c.scale(1, 0.22); _rgb(c, INK, 0.22); c.arc(0, 0, 105, 0, 2 * math.pi); c.fill(); c.restore()
    c.translate(0, crouch)
    legs = L.get("legs")
    if legs:
        _limb(c, -26, -100, ll[0], ll[1], 52, 52, 26, legs, "shoe", 20, INK, face)
        _limb(c, 26, -100, rl[0], rl[1], 52, 52, 26, legs, "shoe", 20, INK, face)
    elif pose in ("kneel", "beg", "sit", "walk", "run"):
        _limb(c, -24, -60, ll[0], ll[1], 40, 30, 22, skin, "shoe", 18, INK, face)
        _limb(c, 24, -60, rl[0], rl[1], 40, 30, 22, skin, "shoe", 18, INK, face)
    c.save(); c.rotate(tilt * face); c.translate(0, breath)
    # back arm
    _limb(c, -52 * face, -225, la[0], la[1], 70, 64, 24, L["top"], "hand", 17, skin, face)
    _body(c, L, skin)
    # head
    c.save(); c.translate(face * 4, -318)
    _hood(c, L.get("hat"))
    _hair_back(c, L["hair"][0], L["hair"][1])
    _circle(c, 0, 0, 80, skin, 7)
    _hair_front(c, L["hair"][0], L["hair"][1])
    c.save()
    if face < 0:
        c.scale(-1, 1)
    _face(c, mood, look * face if face < 0 else look, t, L.get("extras", []), skin)
    c.restore()
    _hat(c, L.get("hat"), L["top"])
    c.restore()
    # front arm (holds things)
    hx, hy = _limb(c, 52 * face, -225, ra[0], ra[1], 70, 64, 24, L["top"], "hand", 17, skin, face)
    if hold_fn:
        c.save(); c.translate(hx, hy - 10); c.scale(0.45, 0.45); hold_fn(c); c.restore()
    if pose == "scrub":
        for k in range(4):
            a = t * 9 + k * 1.6
            _rgb(c, WHITE, 0.85); c.arc(hx + 30 * math.cos(a), hy - 30 + 22 * math.sin(a), 9, 0, 2 * math.pi); c.fill()
    c.restore()
    c.restore()
