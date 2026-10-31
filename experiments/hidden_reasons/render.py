"""Hidden Reasons test video: 'Why a lemon beat the sailors' deadliest enemy'.
Original style: round 'bean' characters, flat painted scenes, a new shot every ~2 s, slow camera push, one caption word at a time.
Run with the Manim venv (has pycairo + numpy):  mvenv/bin/python render.py
"""
import json, math, subprocess, sys
import cairo

W, H, FPS = 1080, 1920, 30
D = "/home/claude/engines/hr/"
T = json.load(open(D + "timing.json"))
WORDS = T["words"]
DUR = T["duration"]

NAVY, NAVY2 = (0.06, 0.15, 0.26), (0.10, 0.22, 0.36)
ORANGE, LEMON = (0.95, 0.55, 0.16), (0.98, 0.86, 0.25)
CREAM, RED, SKIN = (0.96, 0.91, 0.80), (0.84, 0.15, 0.24), (0.95, 0.78, 0.63)
SEA, WOOD, WOOD2 = (0.12, 0.48, 0.55), (0.45, 0.28, 0.16), (0.34, 0.20, 0.11)
WHITE, INK = (1, 1, 1), (0.08, 0.07, 0.10)


def wt(word, after=0.0):
    for w in WORDS:
        if w["start"] >= after and w["w"].strip(".,?!").lower() == word.lower():
            return w["start"]
    raise KeyError(word)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def pop(t, t0, d=0.25):
    """0->1 with a little overshoot, starting at t0."""
    x = (t - t0) / d
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1.0 + 0.18 * math.sin(x * math.pi) * (1 - x) + (ease(x) - 1)


# ---------- drawing helpers ----------
def rgb(c, col, a=1.0):
    c.set_source_rgba(col[0], col[1], col[2], a)


def rect(c, x, y, w, h, col, a=1.0):
    rgb(c, col, a); c.rectangle(x, y, w, h); c.fill()


def rrect(c, x, y, w, h, r, col, a=1.0, stroke=None, lw=6):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()
    rgb(c, col, a)
    if stroke:
        c.fill_preserve(); rgb(c, stroke); c.set_line_width(lw); c.stroke()
    else:
        c.fill()


def circle(c, x, y, r, col, a=1.0, stroke=None, lw=6):
    c.arc(x, y, r, 0, 2 * math.pi); rgb(c, col, a)
    if stroke:
        c.fill_preserve(); rgb(c, stroke); c.set_line_width(lw); c.stroke()
    else:
        c.fill()


def vgrad(c, top, bot, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    c.set_source(g); c.rectangle(-400, y0 - 400, W + 800, (y1 - y0) + 800); c.fill()


def glow(c, x, y, r, col, a=0.5):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a); g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()


def text(c, s, x, y, size, col=WHITE, stroke=INK, lw=12, align="c", weight=True):
    c.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if weight else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    e = c.text_extents(s)
    tx = x - e.width / 2 - e.x_bearing if align == "c" else x
    c.move_to(tx, y); c.text_path(s)
    if stroke:
        rgb(c, stroke); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    rgb(c, col); c.fill()


def bean(c, x, y, s=1.0, body=NAVY2, mood="calm", hat=None, t=0.0, look=0.0, arm=0.0, lie=False):
    """Our character: a round bean body, big eyes, tiny arms. (x,y) = feet centre."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if lie:
        c.rotate(-math.pi / 2)
    bob = math.sin(t * 6) * 4
    c.translate(0, bob)
    # shadow
    c.save(); c.scale(1, 0.25); circle(c, 0, 0, 110, INK, 0.25); c.restore()
    # body
    rrect(c, -100, -330, 200, 330, 100, body, stroke=INK, lw=7)
    # shirt stripes for sailors
    if hat == "bandana":
        for k in range(3):
            rect(c, -92, -150 + k * 42, 184, 16, WHITE, 0.85)
    # face plate
    c.save(); c.translate(0, -230)
    circle(c, 0, 0, 82, SKIN, stroke=INK, lw=6)
    # eyes
    ey = -10
    for sx in (-30, 30):
        circle(c, sx, ey, 22, WHITE, stroke=INK, lw=4)
        circle(c, sx + 7 * look, ey + 3, 9 if mood != "shock" else 6, INK)
    # brows / mouth by mood
    c.set_line_width(6); rgb(c, INK); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if mood == "doubt":
        c.move_to(-48, -48); c.line_to(-14, -42); c.move_to(14, -52); c.line_to(48, -62); c.stroke()
        c.move_to(-18, 38); c.line_to(20, 32); c.stroke()
    elif mood == "sick":
        c.move_to(-48, -40); c.line_to(-14, -46); c.move_to(14, -46); c.line_to(48, -40); c.stroke()
        c.move_to(-20, 40); c.curve_to(-8, 30, 8, 30, 20, 40); c.stroke()
        rgb(c, (0.55, 0.75, 0.45), 0.35); c.arc(0, 0, 82, 0, 2 * math.pi); c.fill()
    elif mood == "shock":
        circle(c, 0, 42, 16, INK)
    elif mood == "happy":
        c.arc(0, 26, 24, 0.15 * math.pi, 0.85 * math.pi); c.stroke()
    elif mood == "gums":
        rrect(c, -40, 22, 80, 46, 20, (0.45, 0.05, 0.08), stroke=INK, lw=5)
        rect(c, -36, 24, 72, 12, (0.9, 0.3, 0.35))
        for i, tx in enumerate((-26, -9, 8, 25)):
            dx = math.sin(t * 18) * 4 if i == 2 else 0
            rect(c, tx - 7 + dx, 30, 14, 14, CREAM)
        for k in range(3):
            yy = 70 + ((t * 60 + k * 23) % 60)
            circle(c, -15 + k * 15, yy, 5, RED, 0.9)
    else:
        c.move_to(-16, 36); c.line_to(16, 36); c.stroke()
    # hats
    if hat == "bandana":
        c.new_path(); c.arc(0, -10, 84, math.pi * 1.05, math.pi * 1.95); c.close_path(); rgb(c, RED); c.fill_preserve(); rgb(c, INK); c.set_line_width(5); c.stroke()
    if hat == "wig":
        for sx in (-1, 1):
            for k in range(3):
                circle(c, sx * 78, -30 + k * 30, 22, (0.93, 0.93, 0.9), stroke=INK, lw=4)
        rect(c, -50, -12, 100, 6, INK)  # spectacles bar
        circle(c, -30, -10, 26, (1, 1, 1), 0.0, stroke=INK, lw=4); circle(c, 30, -10, 26, (1, 1, 1), 0.0, stroke=INK, lw=4)
    c.restore()
    # arms
    for sx in (-1, 1):
        a = arm if sx == 1 else 0
        c.save(); c.translate(sx * 98, -150); c.rotate(sx * (0.3 - a))
        rrect(c, -16, 0, 32, 90, 16, body, stroke=INK, lw=5); circle(c, 0, 92, 18, SKIN, stroke=INK, lw=4)
        c.restore()
    c.restore()


def orange(c, x, y, r, a=1.0):
    circle(c, x, y, r, ORANGE, a, stroke=INK, lw=6)
    circle(c, x - r * 0.35, y - r * 0.35, r * 0.25, WHITE, 0.35 * a)
    c.save(); c.translate(x + r * 0.2, y - r * 0.95); c.rotate(-0.5); c.scale(1, 0.5); circle(c, 0, 0, r * 0.35, (0.25, 0.6, 0.25), a, stroke=INK, lw=4); c.restore()


def lemon(c, x, y, r, a=1.0):
    c.save(); c.translate(x, y); c.scale(1.35, 1.0); circle(c, 0, 0, r, LEMON, a, stroke=INK, lw=5); c.restore()
    circle(c, x - r * 0.4, y - r * 0.3, r * 0.22, WHITE, 0.4 * a)


def sea_bg(c, t, top=(0.98, 0.62, 0.35), bot=(0.45, 0.25, 0.45), horizon=1150):
    vgrad(c, top, bot, 0, horizon)
    glow(c, 540, horizon - 120, 380, (1, 0.85, 0.5), 0.55)
    vgrad(c, (0.12, 0.40, 0.50), (0.04, 0.12, 0.22), horizon, H)
    for k in range(9):
        y = horizon + 40 + k * 90
        c.set_line_width(5); rgb(c, WHITE, 0.25)
        c.move_to(-50, y)
        for xx in range(-50, W + 60, 60):
            c.line_to(xx, y + math.sin(xx / 80 + t * 2 + k) * 10)
        c.stroke()


def ship(c, x, y, s, t):
    c.save(); c.translate(x, y + math.sin(t * 1.5) * 8); c.rotate(math.sin(t * 1.2) * 0.02); c.scale(s, s)
    c.move_to(-330, 0); c.line_to(330, 0); c.line_to(250, 140); c.line_to(-260, 140); c.close_path()
    rgb(c, WOOD2); c.fill_preserve(); rgb(c, INK); c.set_line_width(8); c.stroke()
    for k in range(5):
        circle(c, -200 + k * 100, 60, 16, INK)
    for mx, mh in ((-120, 560), (90, 640)):
        rect(c, mx - 10, -mh, 20, mh, WOOD)
        for k, (w, hh) in enumerate(((240, 170), (280, 200))):
            yy = -mh + 40 + k * 230
            c.move_to(mx - w / 2, yy); c.curve_to(mx - w / 2 + 30, yy + hh / 2, mx - w / 2 + 30, yy + hh / 2, mx - w / 2, yy + hh)
            c.line_to(mx + w / 2, yy + hh); c.curve_to(mx + w / 2 + 30, yy + hh / 2, mx + w / 2 + 30, yy + hh / 2, mx + w / 2, yy)
            c.close_path(); rgb(c, CREAM); c.fill_preserve(); rgb(c, INK); c.set_line_width(6); c.stroke()
    rect(c, 80, -700, 70, 40, RED)
    c.restore()


def arm_scar(c, t, open_amt, glow_red=0.0):
    vgrad(c, (0.20, 0.10, 0.12), (0.05, 0.04, 0.08))
    glow(c, 540, 900, 700, (0.9, 0.4, 0.3), 0.25)
    c.save(); c.translate(540, 900); c.rotate(-0.18)
    rrect(c, -700, -260, 1400, 520, 260, SKIN, stroke=INK, lw=10)
    for k in range(6):
        circle(c, -400 + k * 160, -150 + (k % 2) * 60, 6, (0.8, 0.6, 0.5))
    # old scar line
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    rgb(c, (0.85, 0.55, 0.5)); c.set_line_width(14)
    c.move_to(-260, 10); c.curve_to(-120, -20, 120, 30, 260, 0); c.stroke()
    for k in range(7):
        xx = -220 + k * 70
        c.move_to(xx, -25); c.line_to(xx + 8, 35); c.stroke()
    if open_amt > 0:
        g = open_amt * 36
        c.move_to(-240, 8)
        c.curve_to(-120, -20 - g, 120, 30 - g, 240, 2)
        c.curve_to(120, 30 + g, -120, -20 + g, -240, 8)
        c.close_path(); rgb(c, (0.55, 0.05, 0.08)); c.fill()
        for k in range(4):
            yy = 40 + ((t * 120 + k * 50) % 160) * open_amt
            circle(c, -60 + k * 40, yy, 9, RED, 0.9 * open_amt)
    c.restore()


def calendar(c, x, y, s, top_txt, big_txt, col=RED):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -150, -170, 300, 340, 26, CREAM, stroke=INK, lw=8)
    rrect(c, -150, -170, 300, 90, 26, col, stroke=INK, lw=8)
    text(c, top_txt, 0, -108, 46, WHITE, None)
    text(c, big_txt, 0, 70, 120, INK, None)
    c.restore()


def ropes(c, n_show, slip=0.0, t=0.0, knots=0.0):
    """Collagen ropes crossing a cut. n_show 0..1 how many are woven; slip loosens them."""
    c.save(); c.translate(540, 860)
    # cut edges
    rect(c, -900, -1100, 1800, 2400, (0.93, 0.66, 0.56))
    gap = 150 + slip * 90
    c.move_to(-600, -gap / 2); c.curve_to(-200, -gap / 2 - 30, 200, -gap / 2 + 30, 600, -gap / 2)
    c.line_to(600, gap / 2); c.curve_to(200, gap / 2 + 30, -200, gap / 2 - 30, -600, gap / 2); c.close_path()
    rgb(c, (0.55, 0.07, 0.10)); c.fill()
    N = 9
    for i in range(N):
        if i / N > n_show:
            break
        x = -480 + i * 120
        sag = slip * (40 + 25 * math.sin(i + t * 3))
        c.set_line_width(18); c.set_line_cap(cairo.LINE_CAP_ROUND)
        rgb(c, (0.98, 0.93, 0.80))
        c.move_to(x - 30, -gap / 2 - 70); c.curve_to(x + 40, -10 + sag, x - 40, 10 + sag, x + 30, gap / 2 + 70); c.stroke()
        rgb(c, INK, 0.5); c.set_line_width(3)
        for k in range(5):
            yy = -gap / 2 - 50 + k * (gap + 100) / 5
            c.move_to(x - 12, yy); c.line_to(x + 12, yy + 10); c.stroke()
        if knots > i / N:
            circle(c, x, sag * 0.5, 26 * (1 - slip * 0.6), ORANGE, stroke=INK, lw=5)
    c.restore()


def vit_c(c, x, y, r, a=1.0):
    circle(c, x, y, r, ORANGE, a, stroke=INK, lw=5)
    text(c, "C", x, y + r * 0.38, r * 1.1, WHITE, INK, 6)


# ---------- shots ----------
def s_hook(c, lt, T):
    arm_scar(c, T, ease((T - wt("splits")) / 0.8))


def s_ship(c, lt, T):
    sea_bg(c, T)
    ship(c, 540, 1170, 1.0, T)
    p = pop(T, wt("1747"))
    if p:
        c.save(); c.translate(540, 330); c.scale(p, p); text(c, "1747", 0, 0, 180, CREAM, INK, 16); c.restore()
    p = pop(T, wt("HMS"))
    if p:
        c.save(); c.translate(540, 470); c.scale(p, p); text(c, "HMS SALISBURY", 0, 0, 84, ORANGE, INK, 12); c.restore()


def s_gums(c, lt, T):
    vgrad(c, (0.20, 0.30, 0.40), (0.06, 0.10, 0.18))
    glow(c, 540, 700, 600, (1, 0.8, 0.5), 0.3)
    bean(c, 540, 1800, 3.2, NAVY2, "gums", "bandana", T)


def s_deck(c, lt, T):
    vgrad(c, (0.20, 0.12, 0.08), (0.07, 0.04, 0.03))
    glow(c, 540, 300, 520, (1, 0.75, 0.35), 0.5)
    rect(c, 530, 100, 20, 160, INK); circle(c, 540, 300, 40, (1, 0.85, 0.45))
    for row in range(3):
        for k in range(3):
            x = 220 + k * 320 + (row % 2) * 60
            y = 760 + row * 380
            c.set_line_width(8); rgb(c, CREAM); c.move_to(x - 160, y - 60); c.curve_to(x - 60, y + 40, x + 60, y + 40, x + 160, y - 60); c.stroke()
            bean(c, x + 20, y - 40, 0.72, NAVY2, "sick", "bandana", T + row + k, lie=True)


def s_compare(c, lt, T):
    vgrad(c, (0.10, 0.12, 0.20), (0.04, 0.05, 0.10))
    t0 = wt("kills")
    # enemy guns (small)
    c.save(); c.translate(300, 1150)
    rrect(c, -150, -60, 260, 110, 50, (0.25, 0.25, 0.28), stroke=INK, lw=7); circle(c, -60, 70, 55, WOOD, stroke=INK, lw=6)
    text(c, "ENEMY GUNS", 0, 220, 54, CREAM, INK, 8)
    c.restore()
    hA = 220 * ease((T - t0) / 0.6)
    rrect(c, 230, 850 - hA, 140, hA + 1, 20, (0.6, 0.6, 0.65))
    # scurvy (tall)
    c.save(); c.translate(780, 1150)
    bean(c, 0, 60, 0.55, NAVY2, "sick", "bandana", T)
    text(c, "SCURVY", 0, 220, 64, ORANGE, INK, 8)
    c.restore()
    hB = 620 * ease((T - t0 - 0.3) / 0.9)
    rrect(c, 710, 850 - hB, 140, hB + 1, 20, RED)
    text(c, "kills more sailors", 540, 300, 70, WHITE, INK, 10)


def s_pairs(c, lt, T):
    vgrad(c, (0.55, 0.75, 0.85), (0.85, 0.80, 0.65))
    rect(c, 0, 1250, W, 700, WOOD)
    for k in range(12):
        rect(c, 0, 1250 + k * 60, W, 4, WOOD2)
    p = ease((T - wt("splits", 14)) / 0.9)
    for i in range(12):
        col, row = i % 4, i // 4
        x0, y0 = 170 + col * 250, 820 + row * 260
        pair = i // 2
        x1, y1 = 200 + (pair % 3) * 340 + (i % 2) * 120, 820 + (pair // 3) * 420
        x, y = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
        bean(c, x, y, 0.42, NAVY2, "sick", "bandana", T + i)
    pl = pop(T, wt("Lind"))
    if pl:
        bean(c, 540, 600, 0.75 * pl, INK, "calm", "wig", T, look=0.5)
        text(c, "JAMES LIND", 540, 260, 84, CREAM, INK, 12)
    if p > 0.9:
        for pair in range(6):
            text(c, str(pair + 1), 260 + (pair % 3) * 340, 600 + (pair // 3) * 420, 60, ORANGE, INK, 8)


def s_cures(c, lt, T):
    vgrad(c, (0.18, 0.14, 0.12), (0.06, 0.05, 0.05))
    items = [("Cider", "CIDER"), ("Vinegar", "VINEGAR"), ("Seawater", "SEAWATER")]
    p0 = pop(T, T - lt + 0.05)
    if p0:
        c.save(); c.translate(540, 260); c.scale(p0, p0); text(c, "6 DIFFERENT CURES", 0, 0, 92, LEMON, INK, 12); c.restore()
    for i, (w, label) in enumerate(items):
        p = pop(T, wt(w))
        if not p:
            continue
        x, y = 540, 520 + i * 330
        c.save(); c.translate(x, y); c.scale(p * 0.78, p * 0.78)
        rrect(c, -380, -190, 760, 380, 40, (0.25, 0.20, 0.17), stroke=INK, lw=8)
        if i == 0:
            rrect(c, -260, -110, 150, 210, 20, (0.85, 0.65, 0.3), stroke=INK, lw=6); c.set_line_width(14); rgb(c, INK); c.arc(-100, 0, 50, -1.2, 1.2); c.stroke()
        elif i == 1:
            rrect(c, -230, -60, 100, 170, 20, (0.6, 0.75, 0.5), stroke=INK, lw=6); rect(c, -205, -130, 50, 80, (0.6, 0.75, 0.5))
        else:
            rrect(c, -270, -80, 180, 180, 20, (0.55, 0.42, 0.28), stroke=INK, lw=6); rect(c, -255, -60, 150, 40, SEA)
        text(c, label, 110, 30, 92, CREAM, INK, 10)
        c.restore()


def s_fruit(c, lt, T):
    vgrad(c, (0.30, 0.18, 0.08), (0.08, 0.05, 0.03))
    glow(c, 540, 1000, 700, (1, 0.8, 0.3), 0.6 * ease(lt / 0.6))
    c.save(); c.translate(540, 1200); c.scale(1, 0.32); circle(c, 0, 0, 420, CREAM, stroke=INK, lw=10); c.restore()
    t1, t2 = wt("oranges"), wt("lemon")
    for k, dx in enumerate((-190, 40)):
        p = pop(T, t1 + k * 0.15)
        if p:
            orange(c, 540 + dx, 1080 - (1 - p) * 500, 130)
    p = pop(T, t2)
    if p:
        lemon(c, 820, 1110 - (1 - p) * 500, 95)
    p = pop(T, wt("every"))
    if p:
        c.save(); c.translate(540, 420); c.scale(p, p); text(c, "EVERY DAY", 0, 0, 110, LEMON, INK, 14); c.restore()


def s_doubt(c, lt, T):
    vgrad(c, (0.45, 0.55, 0.65), (0.15, 0.20, 0.28))
    bean(c, 540, 1750, 2.6, NAVY2, "doubt", "bandana", T, look=-0.6)
    for k in range(3):
        p = pop(T, T - lt + 0.2 + k * 0.25)
        if p:
            text(c, "?", 230 + k * 300, 380 + (k % 2) * 80, 220 * p, ORANGE, INK, 14)


def s_day6(c, lt, T):
    vgrad(c, (0.22, 0.17, 0.13), (0.08, 0.06, 0.05))
    rrect(c, 240, 1050, 600, 330, 30, WOOD, stroke=INK, lw=8)
    text(c, "EMPTY", 540, 1260, 90, CREAM, INK, 10)
    n = 1 + int(min(5, max(0, (T - wt("Six", 24)) / 0.18)))
    calendar(c, 540, 600, 1.4, "DAY", str(n))


def s_duty(c, lt, T):
    vgrad(c, (0.55, 0.80, 0.95), (0.95, 0.85, 0.60))
    glow(c, 540, 500, 600, (1, 1, 0.8), 0.6)
    rect(c, 0, 1400, W, 600, WOOD)
    stand = ease((T - wt("already")) / 0.5)
    bean(c, 540, 1420, 1.6, NAVY2, "happy" if stand > 0.5 else "sick", "bandana", T, arm=1.6 * stand)
    p = pop(T, wt("back"))
    if p:
        c.save(); c.translate(540, 360); c.scale(p, p); text(c, "BACK ON DUTY", 0, 0, 110, WHITE, INK, 14); c.restore()


def s_you(c, lt, T):
    vgrad(c, (0.93, 0.92, 0.95), (0.80, 0.82, 0.90))
    c.save(); c.translate(540, 1050); c.rotate(-0.3)
    rrect(c, -130, -560, 260, 1100, 130, SKIN, stroke=INK, lw=10)
    rrect(c, -100, -540, 200, 170, 80, (0.98, 0.88, 0.85), stroke=INK, lw=5)
    cut = ease((T - wt("cut")) / 0.3)
    if cut:
        c.set_line_width(12 * cut); rgb(c, RED); c.move_to(-90, -120); c.line_to(90, -150); c.stroke()
    c.restore()
    text(c, "YOU", 540, 360, 160, NAVY, None)


def s_collagen(c, lt, T):
    ropes(c, ease((T - wt("collagen")) / 1.6), 0, T)
    p = pop(T, wt("collagen"))
    if p:
        c.save(); c.translate(540, 300); c.scale(p, p); text(c, "COLLAGEN", 0, 0, 120, CREAM, INK, 14); c.restore()


def s_vitc(c, lt, T):
    k = ease((T - wt("vitamin")) / 1.2)
    ropes(c, 1.0, 0, T, knots=k)
    for i in range(5):
        p = pop(T, wt("vitamin") + i * 0.1)
        if p:
            vit_c(c, 160 + i * 190, 1330 - (1 - p) * 200, 60)
    if T >= wt("can't"):
        c.save(); rect(c, 0, 0, W, H, INK, 0.55)
        bean(c, 540, 1300, 1.3, NAVY2, "shock", None, T)
        p = pop(T, wt("can't"))
        c.set_line_width(36); rgb(c, RED); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(340, 520); c.line_to(340 + 400 * p, 520 + 400 * p); c.move_to(740, 520); c.line_to(740 - 400 * p, 520 + 400 * p); c.stroke()
        vit_c(c, 540, 720, 120)
        c.restore()


def s_slip(c, lt, T):
    if T < wt("Even"):
        ropes(c, 1.0, ease((T - wt("knots")) / 1.0), T, knots=1.0)
        text(c, "NO FRESH FOOD", 540, 320, 96, CREAM, INK, 12)
    else:
        arm_scar(c, T, ease((T - wt("Even")) / 0.5))
        text(c, "EVEN OLD SCARS", 540, 320, 96, ORANGE, INK, 12)


def s_win(c, lt, T):
    vgrad(c, (0.98, 0.75, 0.30), (0.85, 0.35, 0.15))
    glow(c, 540, 900, 700, (1, 1, 0.7), 0.7)
    for i in range(10):
        a = i / 10 * 2 * math.pi + T * 0.4
        rgb(c, WHITE, 0.15); c.move_to(540, 900); c.line_to(540 + 1600 * math.cos(a), 900 + 1600 * math.sin(a)); c.line_to(540 + 1600 * math.cos(a + 0.2), 900 + 1600 * math.sin(a + 0.2)); c.close_path(); c.fill()
    orange(c, 380, 900, 170); orange(c, 690, 860, 170); lemon(c, 540, 1130, 120)
    p = pop(T, wt("medicine"))
    if p:
        for k, x in enumerate((200, 880)):
            rrect(c, x - 60, 1450, 120, 220, 20, (0.75, 0.80, 0.85), 0.9 * p, stroke=INK, lw=5)
            c.set_line_width(14); rgb(c, RED, p); c.move_to(x - 80, 1430); c.line_to(x + 80, 1690); c.stroke()


def s_navy(c, lt, T):
    vgrad(c, (0.12, 0.10, 0.12), (0.04, 0.03, 0.05))
    glow(c, 540, 700, 600, (0.9, 0.7, 0.4), 0.35)
    rect(c, 0, 1350, W, 600, WOOD2)
    bean(c, 540, 1360, 1.2, NAVY, "calm", "wig", T, look=-1)
    t0 = wt("took")
    y = 1747 + int(min(48, max(0, (T - t0) / 1.0 * 48)))
    calendar(c, 540, 560, 1.25, "YEAR", str(y), NAVY)
    p = pop(T, wt("forty-eight"))
    if p:
        c.save(); c.translate(540, 1720); c.scale(p, p); text(c, "48 YEARS", 0, 0, 140, ORANGE, INK, 16); c.restore()


SHOTS = [  # (start time, function, zoom focus y)
    (0.0, s_hook, 900), (wt("It's"), s_ship, 900), (wt("His"), s_gums, 900), (wt("And"), s_deck, 1000),
    (wt("The", 9), s_compare, 900), (wt("So"), s_pairs, 900), (wt("Each"), s_cures, 960),
    (wt("And", 19), s_fruit, 1000), (wt("Fruit"), s_doubt, 900), (wt("Six", 24), s_day6, 900),
    (wt("But"), s_duty, 1000), (wt("You"), s_you, 900), (wt("Your", 30), s_collagen, 860),
    (wt("And", 34), s_vitc, 860), (wt("Months"), s_slip, 860), (wt("Two", 42), s_win, 900),
    (wt("And", 44.5), s_navy, 900),
]

KEY = {"scar", "1747", "twelve", "six", "pairs", "oranges", "lemon", "fruit", "collagen", "vitamin", "c", "forty-eight", "duty", "years"}


def caption(c, T):
    cur = None
    for w in WORDS:
        if w["start"] <= T + 0.03:
            cur = w
    if not cur or T > cur["end"] + 0.6:
        return
    s = cur["w"].strip(".,!").replace("?", "?")
    k = s.strip("?").lower() in KEY
    p = min(1.0, (T - cur["start"]) / 0.08 + 0.85)
    p = max(p, 0.3)
    c.save(); c.translate(540, 1560); c.scale(p, p)
    text(c, s, 0, 0, 118, LEMON if k else WHITE, INK, 18)
    c.restore()


def frame(c, T):
    idx = max(i for i, s in enumerate(SHOTS) if s[0] <= T + 1e-6)
    t0, fn, fy = SHOTS[idx]
    t1 = SHOTS[idx + 1][0] if idx + 1 < len(SHOTS) else DUR
    lt = T - t0
    z = 1.0 + 0.07 * ease(lt / max(0.5, t1 - t0)) + 0.10 * (1 - ease(lt / 0.25))  # punch-in at cut, then slow push
    c.save()
    c.translate(540, fy); c.scale(z, z); c.translate(-540, -fy)
    fn(c, lt, T)
    c.restore()
    # vignette
    g = cairo.RadialGradient(540, 960, 500, 540, 960, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    c.set_source(g); c.paint()
    caption(c, T)


def main(only=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    if only is not None:  # still frames for checking
        for T in only:
            c = cairo.Context(surf); rect(c, 0, 0, W, H, INK); frame(c, T)
            surf.write_to_png(D + f"still_{T:05.2f}.png")
        return
    n = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", D + "voice.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", D + "hidden_reasons_scurvy.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        c = cairo.Context(surf); rect(c, 0, 0, W, H, INK); frame(c, i / FPS)
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
        if i % 150 == 0:
            print(f"frame {i}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        main([float(x) for x in sys.argv[2:]])
    else:
        main()
