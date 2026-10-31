"""Episode 001 (Hidden Reasons): Why a lemon beat the sailors' deadliest enemy.
Scenes for studio.story. Facts and sources: sources.md in this folder.
"""
import math
import cairo
from studio.story import lib as L
from studio.story.lib import *  # noqa: F401,F403  (palette and drawing helpers)

wt = L.wt


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
    p = ease((T - wt("splits", 2)) / 0.9)
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
    n = 1 + int(min(5, max(0, (T - wt("Six", 2)) / 0.18)))
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
    (wt("The", 2), s_compare, 900), (wt("So"), s_pairs, 900), (wt("Each"), s_cures, 960),
    (wt("And", 3), s_fruit, 1000), (wt("Fruit"), s_doubt, 900), (wt("Six", 2), s_day6, 900),
    (wt("But"), s_duty, 1000), (wt("You"), s_you, 900), (wt("Your", 1), s_collagen, 860),
    (wt("And", 5), s_vitc, 860), (wt("Months"), s_slip, 860), (wt("Two", 3), s_win, 900),
    (wt("And", 8), s_navy, 900),
]

KEY = {"scar", "1747", "twelve", "six", "pairs", "oranges", "lemon", "fruit", "collagen", "vitamin", "c", "forty-eight", "duty", "years"}


