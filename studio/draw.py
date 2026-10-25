"""Drawing primitives shared by all scenes: palettes, backgrounds, text, chips, icon badges, the cat."""
import hashlib, math
import cairo
from . import icons

W, H, FPS = 1080, 1920, 30
FONT = "Poppins"
SAFE_TOP, SAFE_BOTTOM = 170, 1240          # visuals live here; captions sit below, YouTube UI below that
CAPTION_Y, SOURCE_Y = 1345, 1452

# ---------- palettes (one per video, for variety) ----------
PALETTES = {
    "midnight": dict(bg1=(.07, .065, .12), bg2=(.13, .09, .16), glow=(1, .70, .28),
                     accent=(1, .70, .28), good=(.31, .82, .77), bad=(1, .42, .42),
                     text=(.98, .95, .90), muted=(.62, .60, .70), panel=(.35, .18, .24)),
    "ocean":    dict(bg1=(.03, .09, .13), bg2=(.05, .15, .20), glow=(.30, .85, .95),
                     accent=(.36, .88, .98), good=(.55, .95, .60), bad=(1, .50, .45),
                     text=(.94, .98, 1), muted=(.55, .68, .74), panel=(.10, .25, .32)),
    "plum":     dict(bg1=(.10, .05, .12), bg2=(.18, .07, .17), glow=(1, .45, .60),
                     accent=(1, .55, .70), good=(.98, .80, .35), bad=(.55, .75, 1),
                     text=(1, .95, .97), muted=(.70, .58, .68), panel=(.30, .12, .26)),
    "forest":   dict(bg1=(.05, .09, .07), bg2=(.08, .14, .10), glow=(.70, .95, .40),
                     accent=(.78, .96, .42), good=(.45, .85, 1), bad=(1, .55, .40),
                     text=(.95, .98, .93), muted=(.58, .68, .60), panel=(.14, .26, .18)),
    "ink":      dict(bg1=(.06, .07, .14), bg2=(.10, .12, .24), glow=(.55, .60, 1),
                     accent=(.70, .72, 1), good=(.45, .95, .75), bad=(1, .52, .55),
                     text=(.96, .96, 1), muted=(.60, .62, .78), panel=(.18, .20, .38)),
}
BACKGROUNDS = ("glow", "dots", "rays")


def pick_style(script):
    """Deterministic per-video palette + background unless the script chose them."""
    h = int(hashlib.sha1(script.get("title", "").encode()).hexdigest(), 16)
    pal = script.get("palette") if script.get("palette") in PALETTES else list(PALETTES)[h % len(PALETTES)]
    h2 = int(hashlib.sha1(("bg:" + script.get("title", "")).encode()).hexdigest(), 16)
    bg = script.get("background") if script.get("background") in BACKGROUNDS else BACKGROUNDS[h2 % len(BACKGROUNDS)]
    return pal, bg


class Style:
    def __init__(self, palette, background):
        self.name, self.bg = palette, background
        self.__dict__.update(PALETTES[palette])

    def tone(self, tone):
        return {"good": self.good, "bad": self.bad, "neutral": self.accent, "accent": self.accent,
                "muted": self.muted}.get(tone or "neutral", self.accent)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x):
    x = clamp(x); c = 1.7
    return max(1e-3, 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2)
def appear(t, at, dur=.35): return ease((t - at) / dur) if t >= at else 0.0
def pop(t, at, dur=.4): return back((t - at) / dur) if t >= at else 0.0


# ---------- background ----------
def background(ctx, t, S):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *S.bg1); g.add_color_stop_rgb(1, *S.bg2)
    ctx.set_source(g); ctx.paint()
    if S.bg == "dots":
        ctx.set_source_rgba(*S.muted, .07)
        off = (t * 12) % 60
        for y in range(-60, H + 60, 60):
            for x in range(0, W + 60, 60):
                ctx.new_path(); ctx.arc(x + (30 if (y // 60) % 2 else 0), y + off, 3, 0, 2 * math.pi); ctx.fill()
    elif S.bg == "rays":
        ctx.save(); ctx.translate(W / 2, 640); ctx.rotate(t * .04)
        for i in range(12):
            ctx.new_path(); ctx.move_to(0, 0)
            a = i * math.pi / 6
            ctx.arc(0, 0, 1600, a, a + math.pi / 14); ctx.close_path()
            ctx.set_source_rgba(*S.glow, .025); ctx.fill()
        ctx.restore()
    gx = W / 2 + 180 * math.sin(t * .25); gy = 700 + 120 * math.cos(t * .2)
    r = cairo.RadialGradient(gx, gy, 0, gx, gy, 900)
    r.add_color_stop_rgba(0, *S.glow, .10); r.add_color_stop_rgba(1, *S.glow, 0)
    ctx.set_source(r); ctx.paint()


# ---------- text ----------
def set_font(ctx, size, weight="bold"):
    w = cairo.FONT_WEIGHT_BOLD if weight == "bold" else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, w); ctx.set_font_size(size)


def text_width(ctx, s, size, weight="bold"):
    set_font(ctx, size, weight); return ctx.text_extents(s).x_advance


def text(ctx, s, x, y, size, color, align="center", weight="bold", alpha=1.0, stroke=0):
    if alpha <= 0 or not s:
        return 0
    set_font(ctx, size, weight)
    adv = ctx.text_extents(s).x_advance
    dx = {"center": -adv / 2, "left": 0, "right": -adv}[align]
    ctx.new_path()
    if stroke:
        ctx.move_to(x + dx, y); ctx.text_path(s)
        ctx.set_source_rgba(0, 0, 0, .75 * alpha); ctx.set_line_width(stroke)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.move_to(x + dx, y); ctx.set_source_rgba(*color, alpha); ctx.show_text(s)
    return adv


def wrap(ctx, s, size, maxw, weight="bold"):
    set_font(ctx, size, weight)
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if ctx.text_extents(t).x_advance <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(ctx, s, x, y, size, color, maxw=900, align="center", alpha=1.0, weight="bold", lh=1.18, stroke=0):
    """Wrapped text; shrinks font until it fits in 3 lines. Returns height used."""
    while True:
        lines = wrap(ctx, s, size, maxw, weight)
        if len(lines) <= 3 or size <= 34:
            break
        size *= .9
    for i, ln in enumerate(lines):
        text(ctx, ln, x, y + i * size * lh, size, color, align, weight, alpha, stroke)
    return len(lines) * size * lh


# ---------- shapes ----------
def rrect(ctx, x, y, w, h, r):
    r = min(r, h / 2, w / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def chip(ctx, label, cx, cy, color, p, size=54, S=None):
    if p <= 0:
        return
    s = back(p) if p < 1 else 1
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    w = min(text_width(ctx, label, size) + 70, 960); h = size * 1.75
    if w >= 960:
        size *= 900 / (w - 70); h = size * 1.75; w = 960
    a = clamp(p * 2)
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    ctx.set_source_rgba(*color, .18 * a); ctx.fill_preserve()
    ctx.set_source_rgba(*color, a); ctx.set_line_width(4); ctx.stroke()
    text(ctx, label, 0, size * .36, size, color, alpha=a)
    ctx.restore()


def rings(ctx, cx, cy, t, color, strength=1.0, n=4, r0=60, spread=420, full=False):
    for i in range(n):
        ph = ((t * .9) + i / n) % 1
        ctx.new_path()
        if full:
            ctx.arc(cx, cy, r0 + ph * spread, 0, 2 * math.pi)
        else:
            ctx.arc(cx, cy, r0 + ph * spread, math.pi * .15, math.pi * .85)
        ctx.set_source_rgba(*color, (1 - ph) * .5 * strength); ctx.set_line_width(10 * (1 - ph) + 2); ctx.stroke()


def wave(ctx, x0, x1, y, amp, cycles, phase, color, width=6, alpha=1, overlay=0.0, overlay_cycles=70):
    ctx.new_path(); ctx.set_source_rgba(*color, alpha); ctx.set_line_width(width)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    n = 400
    for i in range(n + 1):
        u = i / n; x = x0 + (x1 - x0) * u
        v = amp * math.sin(2 * math.pi * cycles * u + phase)
        v += overlay * amp * .45 * math.sin(2 * math.pi * overlay_cycles * u + phase * 3)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y + v)
    ctx.stroke()


def arrow(ctx, x0, y0, x1, y1, color, alpha=1, width=8, dashed=False):
    ctx.new_path(); ctx.set_source_rgba(*color, alpha); ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if dashed:
        ctx.set_dash([18, 14])
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke(); ctx.set_dash([])
    a = math.atan2(y1 - y0, x1 - x0)
    ctx.new_path()
    for s in (-1, 1):
        ctx.move_to(x1, y1); ctx.line_to(x1 - 30 * math.cos(a + s * .5), y1 - 30 * math.sin(a + s * .5))
    ctx.stroke()


def cross(ctx, cx, cy, size, color, p):
    if p <= 0:
        return
    ctx.new_path(); ctx.set_source_rgba(*color, p); ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    s = size * p
    ctx.move_to(cx - s, cy - s * .6); ctx.line_to(cx + s, cy + s * .6); ctx.stroke()
    ctx.move_to(cx + s, cy - s * .6); ctx.line_to(cx - s, cy + s * .6); ctx.stroke()


# ---------- icons ----------
def badge(ctx, name, cx, cy, r, S, color=None, p=1.0, t=0.0, bob=True, filled_bg=True):
    """An icon inside a soft circular badge. `name` may be a Tabler icon or '@cat'."""
    if p <= 0:
        return
    color = color or S.accent
    s = back(p) if p < 1 else 1
    y = cy + (6 * math.sin(t * 2.2) if bob else 0)
    ctx.save(); ctx.translate(cx, y); ctx.scale(s, s)
    if name.startswith("@"):
        cat(ctx, 0, r * .08, r * .82, S, t=t, purr=0.4)
        ctx.restore(); return
    if filled_bg:
        ctx.new_path(); ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*color, .16); ctx.fill_preserve()
        ctx.set_source_rgba(*color, .9); ctx.set_line_width(max(4, r * .04)); ctx.stroke()
    size = int(r * 1.25)
    surf = icons.surface(name, size, tuple(color))
    ctx.set_source_surface(surf, -size / 2, -size / 2); ctx.paint()
    ctx.restore()


FUR, FUR_D, PINK = (.91, .63, .35), (.72, .44, .22), (.96, .55, .62)


def cat(ctx, cx, cy, R, S, eyes_open=0.0, look_up=0.0, purr=0.0, t=0):
    """Hand-drawn cat character (the original proof video's mascot)."""
    ctx.save(); ctx.translate(cx + purr * 3 * math.sin(t * 2 * math.pi * 12), cy)
    ctx.new_path()
    for sgn in (-1, 1):
        ctx.move_to(sgn * R * .95, -R * .25); ctx.line_to(sgn * R * .72, -R * 1.32); ctx.line_to(sgn * R * .18, -R * .82)
        ctx.close_path(); ctx.set_source_rgb(*FUR); ctx.fill()
        ctx.move_to(sgn * R * .80, -R * .42); ctx.line_to(sgn * R * .70, -R * 1.08); ctx.line_to(sgn * R * .36, -R * .78)
        ctx.close_path(); ctx.set_source_rgb(*PINK); ctx.fill()
    ctx.save(); ctx.scale(1.08, .94); ctx.arc(0, 0, R, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgb(*FUR); ctx.fill()
    ctx.set_source_rgb(*FUR_D); ctx.set_line_width(R * .07); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for dx, l in ((-.22, .28), (0, .36), (.22, .28)):
        ctx.move_to(R * dx, -R * .9); ctx.line_to(R * dx, -R * (.9 - l)); ctx.stroke()
    ctx.save(); ctx.translate(0, R * .32); ctx.scale(1.25, .8); ctx.arc(0, 0, R * .36, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgb(.99, .90, .80); ctx.fill()
    ey = -R * .08 - look_up * R * .04
    for sgn in (-1, 1):
        ex = sgn * R * .38
        ctx.new_path()
        if eyes_open < .5:
            ctx.set_source_rgb(.15, .1, .1); ctx.set_line_width(R * .055)
            ctx.arc(ex, ey - R * .04, R * .16, math.pi * .15, math.pi * .85); ctx.stroke()
        else:
            o = (eyes_open - .5) * 2
            ctx.save(); ctx.translate(ex, ey); ctx.scale(1, .25 + .75 * o)
            ctx.arc(0, 0, R * .17, 0, 2 * math.pi); ctx.restore(); ctx.set_source_rgb(.55, .78, .35); ctx.fill()
            ctx.save(); ctx.translate(ex, ey - look_up * R * .07); ctx.scale(.45, .25 + .75 * o)
            ctx.arc(0, 0, R * .14, 0, 2 * math.pi); ctx.restore(); ctx.set_source_rgb(.08, .06, .06); ctx.fill()
            ctx.arc(ex + R * .05, ey - R * .06, R * .035, 0, 2 * math.pi); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.new_path()
    ctx.move_to(-R * .09, R * .17); ctx.line_to(R * .09, R * .17); ctx.line_to(0, R * .28); ctx.close_path()
    ctx.set_source_rgb(*PINK); ctx.fill()
    ctx.set_source_rgb(.3, .18, .15); ctx.set_line_width(R * .035)
    ctx.move_to(0, R * .28); ctx.line_to(0, R * .36); ctx.stroke()
    for sgn in (-1, 1):
        ctx.move_to(0, R * .36); ctx.curve_to(sgn * R * .04, R * .46, sgn * R * .16, R * .46, sgn * R * .19, R * .38); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, .8); ctx.set_line_width(R * .018)
    for sgn in (-1, 1):
        for k in (-1, 0, 1):
            ctx.move_to(sgn * R * .42, R * .30 + k * R * .07); ctx.line_to(sgn * R * 1.25, R * .22 + k * R * .14); ctx.stroke()
    ctx.restore()


def bubble(ctx, cx, cy, label, S, p, size=60):
    if p <= 0:
        return
    q = back(p) if p < 1 else 1
    ctx.save(); ctx.translate(cx, cy); ctx.scale(q, q)
    w = text_width(ctx, label, size) + 90; h = size * 2.1
    ctx.new_path(); rrect(ctx, -w / 2, -h / 2, w, h, h / 2); ctx.set_source_rgb(*S.text); ctx.fill()
    ctx.move_to(-w * .25, h * .32); ctx.line_to(-w * .40, h * .95); ctx.line_to(-w * .08, h * .40); ctx.close_path(); ctx.fill()
    text(ctx, label, 0, size * .36, size, S.bg1)
    ctx.restore()
