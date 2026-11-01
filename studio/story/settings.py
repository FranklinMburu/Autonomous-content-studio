"""Drawn settings (backgrounds): real places instead of plain gradients. Each fills the 1080 x 1920 frame.

    draw(c, name, T, tone="day")      name in SETTINGS, tone in TONES

Ground line is at y = 1300 for indoor/outdoor scenes, so characters stand at y 1300-1750.
"""
import math
import cairo

INK = (0.08, 0.07, 0.10)
W, H = 1080, 1920
TONES = {"day": None, "dusk": (0.95, 0.45, 0.25, 0.22), "night": (0.05, 0.08, 0.25, 0.48), "warm": (1.0, 0.75, 0.35, 0.18)}


def _rgb(c, col, a=1.0):
    c.set_source_rgba(col[0], col[1], col[2], a)


def _rect(c, x, y, w, h, col, a=1.0, lw=0):
    c.rectangle(x, y, w, h); _rgb(c, col, a)
    if lw:
        c.fill_preserve(); _rgb(c, INK); c.set_line_width(lw); c.stroke()
    else:
        c.fill()


def _grad(c, top, bot, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1); g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    c.set_source(g); c.rectangle(-400, y0, W + 800, y1 - y0); c.fill()


def _floor_planks(c, y0, col, line):
    _rect(c, -400, y0, W + 800, H - y0 + 400, col)
    for k in range(14):
        y = y0 + (k ** 1.6) * 6
        _rect(c, -400, y, W + 800, 3, line)


def _window(c, x, y, w, h, light, frame=(0.35, 0.24, 0.16)):
    _rect(c, x, y, w, h, light, lw=8)
    _rect(c, x + w / 2 - 5, y, 10, h, frame); _rect(c, x, y + h / 2 - 5, w, 10, frame)
    c.rectangle(x, y, w, h); _rgb(c, INK); c.set_line_width(10); c.stroke()


def ward(c, T):
    _grad(c, (0.86, 0.83, 0.74), (0.74, 0.70, 0.60), 0, 1300)
    _rect(c, -400, 980, W + 800, 320, (0.52, 0.40, 0.30))
    _rect(c, -400, 975, W + 800, 12, (0.30, 0.22, 0.16))
    for x in (120, 470, 820):
        _window(c, x, 300, 200, 420, (0.85, 0.93, 1.0))
        g = cairo.LinearGradient(0, 720, 0, 1300); g.add_color_stop_rgba(0, 1, 1, 0.9, 0.25); g.add_color_stop_rgba(1, 1, 1, 0.9, 0)
        c.set_source(g); c.move_to(x, 720); c.line_to(x + 200, 720); c.line_to(x + 300, 1300); c.line_to(x - 60, 1300); c.close_path(); c.fill()
    _floor_planks(c, 1300, (0.55, 0.42, 0.30), (0.40, 0.30, 0.21))
    for x in (60, 760):  # beds along the sides
        _rect(c, x, 1150, 260, 70, (0.95, 0.95, 0.92), lw=6); _rect(c, x, 1215, 260, 30, (0.55, 0.45, 0.40), lw=6)
        _rect(c, x + (0 if x < 500 else 210), 1080, 50, 150, (0.45, 0.35, 0.28), lw=6)


def street(c, T):
    _grad(c, (0.55, 0.75, 0.92), (0.88, 0.90, 0.92), 0, 1250)
    cols = [(0.70, 0.52, 0.40), (0.62, 0.62, 0.55), (0.78, 0.66, 0.48), (0.55, 0.45, 0.42), (0.72, 0.58, 0.45)]
    x = -60
    for i in range(6):
        w, h = 230 + (i % 3) * 40, 650 + (i * 137) % 300
        col = cols[i % len(cols)]
        _rect(c, x, 1250 - h, w, h, col, lw=7)
        c.move_to(x - 15, 1250 - h); c.line_to(x + w / 2, 1250 - h - 110); c.line_to(x + w + 15, 1250 - h); c.close_path()
        _rgb(c, (0.40, 0.22, 0.18)); c.fill_preserve(); _rgb(c, INK); c.set_line_width(7); c.stroke()
        for r in range(int((h - 160) / 170)):
            for k in range(2):
                _window(c, x + 35 + k * (w / 2), 1250 - h + 60 + r * 170, w / 2 - 70, 110, (0.95, 0.88, 0.60) if (i + r + k) % 3 == 0 else (0.70, 0.80, 0.88))
        x += w
    _rect(c, -400, 1250, W + 800, 700, (0.55, 0.53, 0.50))
    for r in range(10):
        y = 1260 + r * (18 + r * 6)
        for k in range(18):
            c.save(); c.translate(k * 70 + (r % 2) * 35 - 20, y); c.scale(1, 0.45)
            c.arc(0, 0, 28 + r * 2, 0, 2 * math.pi); _rgb(c, (0.62, 0.60, 0.57)); c.fill_preserve(); _rgb(c, (0.42, 0.40, 0.38)); c.set_line_width(4); c.stroke(); c.restore()


def room(c, T):
    _grad(c, (0.80, 0.66, 0.52), (0.66, 0.52, 0.40), 0, 1300)
    for k in range(12):
        _rect(c, k * 100 - 20, 0, 8, 1300, (0.72, 0.58, 0.45))
    _window(c, 640, 330, 300, 380, (0.80, 0.90, 1.0))
    _rect(c, 120, 520, 330, 780, (0.40, 0.26, 0.16), lw=8); c.arc(400, 920, 14, 0, 2 * math.pi); _rgb(c, (0.85, 0.70, 0.30)); c.fill()
    _rect(c, 520, 380, 80, 110, (0.35, 0.25, 0.20), lw=6)
    _floor_planks(c, 1300, (0.45, 0.30, 0.20), (0.32, 0.21, 0.14))


def lab(c, T):
    _grad(c, (0.84, 0.88, 0.86), (0.70, 0.76, 0.74), 0, 1300)
    for y in range(0, 1300, 90):
        for x in range(0, W, 90):
            c.rectangle(x, y, 90, 90); _rgb(c, (0.62, 0.70, 0.68)); c.set_line_width(2); c.stroke()
    for sy in (360, 600):
        _rect(c, 60, sy, 960, 22, (0.45, 0.32, 0.22), lw=5)
        for k in range(9):
            col = [(0.6, 0.85, 0.6), (0.9, 0.6, 0.3), (0.5, 0.7, 0.95), (0.9, 0.85, 0.5)][k % 4]
            h = 70 + (k * 23) % 50
            _rect(c, 100 + k * 100, sy - h, 50, h, col, 0.85, lw=4)
    _rect(c, -400, 1080, W + 800, 40, (0.30, 0.30, 0.32), lw=6)
    _rect(c, -400, 1120, W + 800, 180, (0.50, 0.50, 0.52))
    _floor_planks(c, 1300, (0.60, 0.62, 0.60), (0.48, 0.50, 0.48))


def deck(c, T):
    _grad(c, (0.60, 0.80, 0.95), (0.95, 0.90, 0.80), 0, 1000)
    _grad(c, (0.15, 0.45, 0.55), (0.08, 0.25, 0.38), 1000, 1150)
    for k in range(6):
        y = 1010 + k * 22
        c.move_to(-50, y)
        for xx in range(-50, W + 60, 50):
            c.line_to(xx, y + math.sin(xx / 60 + T * 2 + k) * 5)
        _rgb(c, (1, 1, 1), 0.3); c.set_line_width(3); c.stroke()
    _rect(c, -400, 1050, W + 800, 90, (0.40, 0.25, 0.14), lw=8)
    for k in range(10):
        _rect(c, k * 120 + 20, 950, 22, 100, (0.40, 0.25, 0.14), lw=5)
    _rect(c, 800, -100, 50, 1150, (0.45, 0.30, 0.18), lw=8)
    c.move_to(825, 0); c.line_to(1100, 900); c.move_to(825, 0); c.line_to(400, 1050); _rgb(c, (0.35, 0.28, 0.20)); c.set_line_width(6); c.stroke()
    _floor_planks(c, 1140, (0.62, 0.45, 0.28), (0.45, 0.32, 0.20))


SETTINGS = {"ward": ward, "street": street, "room": room, "lab": lab, "deck": deck}


def draw(c, name, T, tone="day"):
    SETTINGS[name](c, T)
    t = TONES.get(tone)
    if t:
        c.rectangle(-400, -400, W + 800, H + 800); _rgb(c, t[:3], t[3]); c.fill()
