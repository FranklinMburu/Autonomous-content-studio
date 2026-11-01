"""Story style engine (used by the "Hidden Reasons" channel).

Shared by every story episode: palette, drawing helpers, the 'bean' characters, captions, camera moves and the
render loop. Each episode lives in episodes/<channel>/<NNN-slug>/ with script.json, scenes.py and sources.md.
An episode's scenes.py imports this module as L and defines SHOTS = [(start_time, draw_function, focus_y), ...]
and KEY = {words shown in yellow}. Word times come from L.wt("word", after_seconds).
"""
import math
import cairo

W, H, FPS = 1080, 1920, 30
FONT = "Poppins"
WORDS, DUR = [], 0.0

NAVY, NAVY2 = (0.06, 0.15, 0.26), (0.10, 0.22, 0.36)
ORANGE, LEMON = (0.95, 0.55, 0.16), (0.98, 0.86, 0.25)
CREAM, RED, SKIN = (0.96, 0.91, 0.80), (0.84, 0.15, 0.24), (0.95, 0.78, 0.63)
SEA, WOOD, WOOD2 = (0.12, 0.48, 0.55), (0.45, 0.28, 0.16), (0.34, 0.20, 0.11)
WHITE, INK = (1, 1, 1), (0.08, 0.07, 0.10)




def set_timing(timing):
    """Load narration word timings before an episode's scenes.py is imported."""
    global WORDS, DUR
    WORDS[:] = timing["words"]
    DUR = timing["duration"]


def wt(word, n=1):
    """Start time of the n-th time `word` is spoken (1 = first). Counting words, not seconds, keeps scenes
    in sync whatever the voice or speed."""
    seen = 0
    for w in WORDS:
        if w["w"].strip(".,?!").lower() == word.lower():
            seen += 1
            if seen == n:
                return w["start"]
    raise KeyError(f"word {word!r} is spoken {seen} time(s); scene asked for number {n}")


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
    c.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if weight else cairo.FONT_WEIGHT_NORMAL)
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




# ---------- engine: captions, camera, render loop ----------
def caption(c, T, key=()):
    """One spoken word at a time, big and centred; words in `key` are yellow."""
    cur = None
    for w in WORDS:
        if w["start"] <= T + 0.03:
            cur = w
    if not cur or T > cur["end"] + 0.6:
        return
    s = cur["w"].strip(".,!")
    k = s.strip("?").lower() in key
    p = max(0.3, min(1.0, (T - cur["start"]) / 0.08 + 0.85))
    c.save(); c.translate(540, 1560); c.scale(p, p)
    text(c, s, 0, 0, 118, LEMON if k else WHITE, INK, 18)
    c.restore()


def frame(c, T, shots, key=()):
    """Draw time T. A shot is (t0, scene_fn, focus_y) or (t0, scene_fn, focus_y, camera_fn, overlay_fn):
    camera_fn(T) -> (cx, cy, zoom) frames the scene; overlay_fn draws labels on top, outside the camera."""
    idx = max(i for i, s in enumerate(shots) if s[0] <= T + 1e-6)
    sh = shots[idx]
    t0, fn, fy = sh[0], sh[1], sh[2]
    t1 = shots[idx + 1][0] if idx + 1 < len(shots) else DUR
    lt = T - t0
    cam = sh[3] if len(sh) > 3 else None
    if cam:
        cx, cy, z = cam(T)
    else:
        cx, cy = 540, fy
        z = 1.0 + 0.07 * ease(lt / max(0.5, t1 - t0)) + 0.10 * (1 - ease(lt / 0.25))
    c.save()
    if cam:   # frame the scene around (cx, cy)
        c.translate(540, 960); c.scale(z, z); c.translate(-cx, -cy)
    else:     # older episodes: zoom around (540, focus_y)
        c.translate(540, fy); c.scale(z, z); c.translate(-540, -fy)
    fn(c, lt, T)
    c.restore()
    if len(sh) > 4 and sh[4]:
        sh[4](c, lt, T)
    g = cairo.RadialGradient(540, 960, 500, 540, 960, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    c.set_source(g); c.paint()
    caption(c, T, key)


def check_shots(shots):
    """Shots must start at 0 and be in time order (a word matched too early breaks the order)."""
    problems = []
    if not shots or shots[0][0] != 0.0:
        problems.append("the first shot must start at 0.0")
    for (a, fa, *_), (b, fb, *_) in zip(shots, shots[1:]):
        if b <= a:
            problems.append(f"shot {fb.__name__} starts at {b:.2f}s, not after {fa.__name__} ({a:.2f}s)")
    return problems


def stills(shots, key, times, out_dir):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    paths = []
    for T in times:
        c = cairo.Context(surf); rect(c, 0, 0, W, H, INK); frame(c, T, shots, key)
        p = f"{out_dir}/still_{T:05.2f}.png"; surf.write_to_png(p); paths.append(p)
    return paths


def render_video(shots, key, wav, out_mp4, preset="veryfast", log=print):
    import subprocess
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    n = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", preset, "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out_mp4)],
                          stdin=subprocess.PIPE)
    for i in range(n):
        c = cairo.Context(surf); rect(c, 0, 0, W, H, INK); frame(c, i / FPS, shots, key)
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
        if i % 300 == 0:
            log(f"  frame {i}/{n}")
    ff.stdin.close(); ff.wait()
    if ff.returncode != 0:
        raise RuntimeError("ffmpeg failed")
    return out_mp4
