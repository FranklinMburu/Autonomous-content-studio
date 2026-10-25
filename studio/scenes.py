"""The scene library. Each scene draws one beat of a video from data in the script.

A scene function receives:
  ctx  - cairo context (already pushed-in by the renderer)
  t    - seconds since the beat started
  b    - the beat dict from the script (scene parameters live here)
  K    - K(word, frac) -> seconds into the beat when `word` is spoken (falls back to frac of the beat)
  S    - the video's Style (palette)
Coordinates: 1080x1920 canvas; visuals stay between SAFE_TOP and SAFE_BOTTOM.
"""
import math
from .draw import (W, H, SOURCE_Y, appear, pop, back, ease, clamp, text, text_block, wrap, chip, rings, wave,
                   arrow, cross, badge, cat, bubble, rrect, text_width)


def _get(d, k, default=None):
    v = d.get(k, default) if isinstance(d, dict) else default
    return default if v is None else v


def decorations(ctx, t, b, S):
    k = b.get("kicker")
    if k:
        chip(ctx, str(k), W / 2, 222, S.good, appear(t, 0, .45), size=46)
    src = b.get("source")
    if src:
        text(ctx, str(src)[:70], W / 2, SOURCE_Y, 30, S.muted, weight="normal", alpha=appear(t, .2, .5))


# 1 ---------------------------------------------------------------
def sc_hero(ctx, t, b, K, S):
    icon = _get(b, "icon", "sparkles")
    p = appear(t, 0, .5)
    if icon == "@cat":
        rings(ctx, W / 2, 900, t, S.accent, strength=p)
        cat(ctx, W / 2, 680, 250 * (0.85 + .15 * back(t / .5)), S, purr=1, t=t)
    else:
        rings(ctx, W / 2, 640, t, S.accent, strength=p * .8, full=True, r0=230, spread=300, n=3)
        badge(ctx, icon, W / 2, 640, 230, S, p=pop(t, 0, .5), t=t)
    lab = b.get("label")
    if lab:
        text_block(ctx, lab, W / 2, 1000, 56, S.muted, alpha=appear(t, .3))
    rv = b.get("reveal")
    if rv:
        at = K(_get(rv, "at"), .6)
        q = pop(t, at, .4)
        if q > 0:
            ctx.save(); ctx.translate(W / 2, 1120); ctx.scale(q, q)
            text(ctx, _get(rv, "text", "?"), 0, 0, 96, S.bad, stroke=10); ctx.restore()


# 2 ---------------------------------------------------------------
def sc_tags(ctx, t, b, K, S):
    title = b.get("title")
    y0 = 330
    if title:
        text(ctx, title, W / 2, y0, 62, S.muted, alpha=appear(t, 0, .4))
    icon = b.get("icon")
    top = 470
    if icon:
        badge(ctx, icon, W / 2, 560, 140, S, p=pop(t, .05, .45), t=t)
        top = 800
    items = b.get("items", [])[:6]
    rows = [items[i:i + 2] for i in range(0, len(items), 2)]
    if any(len(_get(it, "text", "")) > 14 for it in items):
        rows = [[it] for it in items]           # long labels: one per row
    step = min(150, (1180 - top) / max(1, len(rows)))
    for r, row in enumerate(rows):
        for c, it in enumerate(row):
            x = W / 2 if len(row) == 1 else (300 if c == 0 else 780)
            frac = .15 + .6 * (r * 2 + c) / max(1, len(items))
            chip(ctx, _get(it, "text", ""), x, top + 40 + r * step, S.tone(_get(it, "tone")),
                 appear(t, K(_get(it, "at"), frac), .35), size=52)
    v = b.get("verdict")
    if v:
        at = K(_get(v, "at"), .85)
        if t > at - .3:
            q = appear(t, at - .3, .4)
            ctx.set_source_rgba(*S.bg1, .94 * q); ctx.rectangle(0, 0, W, H); ctx.fill()
            text_block(ctx, _get(v, "text", ""), W / 2, 760, 110, S.text, alpha=q)
            if v.get("sub"):
                text(ctx, v["sub"], W / 2, 960, 56, S.muted, alpha=q)


# 3 ---------------------------------------------------------------
def sc_link(ctx, t, b, K, S):
    a, z = b.get("from", {}), b.get("to", {})
    ta = K(_get(a, "at"), 0)
    tz = K(_get(z, "at"), .35)
    # the subject is on screen from the start; its cue word makes it fire
    badge(ctx, _get(a, "icon", "circle"), W / 2, 430, 110, S, color=S.bad, p=pop(t, 0, .45), t=t)
    text(ctx, _get(a, "label", ""), W / 2 + 145, 445, 44, S.muted, align="left", alpha=appear(t, .2))
    if t >= ta:
        g = appear(t, ta, .3) * (.5 + .5 * math.sin((t - ta) * 6))
        ctx.new_path(); ctx.arc(W / 2, 430, 135, 0, 2 * math.pi)
        ctx.set_source_rgba(*S.bad, .25 * g); ctx.fill()
    if t < tz:  # faint outline of what's coming
        ctx.new_path(); ctx.arc(W / 2, 880, 135, 0, 2 * math.pi); ctx.set_dash([12, 12])
        ctx.set_source_rgba(*S.muted, .35 * appear(t, .2)); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    pa = appear(t, .1, .4)
    ctx.new_path(); ctx.set_source_rgba(*S.text, .3 * pa); ctx.set_line_width(8); ctx.set_dash([18, 14])
    ctx.move_to(W / 2, 555); ctx.line_to(W / 2, 740); ctx.stroke(); ctx.set_dash([])
    cut = b.get("cut")
    tc = K(_get(cut, "at"), .6) if cut else 1e9
    if t > ta + .2 and t < tc:
        for i in range(5):
            ph = ((t - ta) * 1.5 + i / 5) % 1
            ctx.new_path(); ctx.arc(W / 2, 555 + ph * 185, 13, 0, 2 * math.pi)
            ctx.set_source_rgba(*S.bad, 1 - ph * .4); ctx.fill()
    badge(ctx, _get(z, "icon", "circle"), W / 2, 880, 135, S, color=S.accent, p=pop(t, tz, .45), t=t)
    text(ctx, _get(z, "label", ""), W / 2, 1065, 44, S.muted, alpha=appear(t, tz))
    if cut and t >= tc - .2:
        q = appear(t, tc - .2, .35)
        cross(ctx, W / 2, 650, 55, S.bad, q)
        text(ctx, _get(cut, "label", ""), W / 2 + 90, 663, 42, S.bad, align="left", alpha=q)
    note = b.get("note")
    if note:
        tn = K(_get(note, "at"), .7)
        q = pop(t, tn, .45)
        if q > 0:
            ctx.save(); ctx.translate(W / 2, 1200); ctx.scale(q, q)
            text(ctx, _get(note, "text", ""), 0, 0, 66, S.accent, stroke=8); ctx.restore()


# 4 ---------------------------------------------------------------
def _fmt(v):
    if abs(v) >= 100 or float(v).is_integer():
        return f"{int(round(v)):,}"
    return f"{v:.1f}"


def sc_number(ctx, t, b, K, S):
    icon = b.get("icon")
    if icon:
        badge(ctx, icon, W / 2, 520, 150, S, p=pop(t, 0, .45), t=t)
    at = K(b.get("at"), .25)
    target = float(_get(b, "value", 0))
    prog = ease((t - at) / 1.2) if t >= at else 0
    s = f"{_get(b, 'prefix', '')}{_fmt(target * prog)}{_get(b, 'suffix', '')}"
    q = pop(t, at - .1, .4)
    if q > 0:
        ctx.save(); ctx.translate(W / 2, 900); ctx.scale(q, q)
        size = 170 if len(s) <= 7 else max(90, 170 * 7 / len(s))
        text(ctx, s, 0, 0, size, S.accent, stroke=8); ctx.restore()
    lab = b.get("label")
    if lab:
        text_block(ctx, lab, W / 2, 1020, 54, S.text, alpha=appear(t, at + .3))


# 5 ---------------------------------------------------------------
def sc_compare(ctx, t, b, K, S):
    title = b.get("title")
    if title:
        text_block(ctx, title, W / 2, 360, 60, S.muted, alpha=appear(t, 0))
    for side, x, col, frac in (("left", 290, S.good, .1), ("right", 790, S.bad, .45)):
        d = b.get(side, {})
        ta = min(K(_get(d, "at"), frac), (.25 if side == "left" else .55) * K.dur)
        p = appear(t, ta, .4)
        if p <= 0:
            continue
        ctx.save(); ctx.translate(0, 40 * (1 - p))
        ctx.new_path(); rrect(ctx, x - 205, 480, 410, 680, 40)
        ctx.set_source_rgba(*col, .10 * p); ctx.fill_preserve(); ctx.set_source_rgba(*col, .7 * p)
        ctx.set_line_width(4); ctx.stroke()
        badge(ctx, _get(d, "icon", "circle"), x, 650, 110, S, color=col, p=p, t=t, bob=False)
        ys = 860
        for ln in wrap(ctx, _get(d, "label", ""), 48, 370)[:2]:
            text(ctx, ln, x, ys, 50, S.text, alpha=p); ys += 60
        if d.get("value") is not None:
            text(ctx, str(d["value"]), x, 1080, 72, col, alpha=p)
        ctx.restore()
    tr = min(K(_get(b.get("right", {}), "at"), .45), .55 * K.dur)
    text(ctx, "vs", W / 2, 830, 44, S.muted, alpha=appear(t, tr))
    v = b.get("verdict")
    if v:
        tv = K(_get(v, "at"), .85)
        q = pop(t, tv, .4)
        if q > 0:
            ctx.save(); ctx.translate(W / 2, 1215); ctx.scale(q, q)
            text(ctx, _get(v, "text", ""), 0, 0, 58, S.accent, stroke=8); ctx.restore()


# 6 ---------------------------------------------------------------
def sc_timeline(ctx, t, b, K, S):
    title = b.get("title")
    top = 300
    if title:
        text(ctx, title, W / 2, top, 58, S.muted, alpha=appear(t, 0)); top += 90
    ev = b.get("events", [])[:5]
    n = max(1, len(ev))
    step = min(220, (1180 - top - 40) / n)
    x = 210
    last = top + 40 + step * (n - 1)
    grow = clamp(t / max(.5, K(_get(ev[-1], "at") if ev else None, .8) + .2)) if ev else 1
    ctx.new_path(); ctx.set_source_rgba(*S.muted, .5); ctx.set_line_width(6)
    ctx.move_to(x, top + 40); ctx.line_to(x, top + 40 + (last - top - 40) * ease(grow)); ctx.stroke()
    for i, e in enumerate(ev):
        y = top + 40 + i * step
        te = K(_get(e, "at"), .1 + .7 * i / n)
        p = appear(t, te, .35)
        if p <= 0:
            continue
        ctx.new_path(); ctx.arc(x, y, 22 * back(min(1, (t - te) / .35)), 0, 2 * math.pi)
        ctx.set_source_rgb(*S.accent); ctx.fill()
        text(ctx, str(_get(e, "when", "")), x + 60, y + 18, 58, S.accent, align="left", alpha=p)
        wl = text_width(ctx, str(_get(e, "when", "")), 58) + 90
        lines = wrap(ctx, _get(e, "label", ""), 44, 960 - x - wl)[:2]
        for j, ln in enumerate(lines):
            text(ctx, ln, x + wl, y + 14 + j * 52, 44, S.text, align="left", alpha=p)


# 7 ---------------------------------------------------------------
def sc_bars(ctx, t, b, K, S):
    title = b.get("title")
    top = 330
    if title:
        text_block(ctx, title, W / 2, top, 58, S.muted, alpha=appear(t, 0)); top += 110
    bars = b.get("bars", [])[:5]
    if not bars:
        return
    mx = max(float(_get(x, "value", 0)) for x in bars) or 1
    step = min(200, (1180 - top) / len(bars))
    unit = _get(b, "unit", "")
    cols = [S.accent, S.good, S.bad, S.muted, S.text]
    for i, bar in enumerate(bars):
        y = top + i * step
        tb = K(_get(bar, "at"), .1 + .7 * i / len(bars))
        p = appear(t, tb, .25)
        if p <= 0:
            continue
        g = ease((t - tb) / .8)
        text(ctx, _get(bar, "label", ""), 110, y + 20, 46, S.text, align="left", alpha=p)
        wbar = 820 * float(_get(bar, "value", 0)) / mx * g
        ctx.new_path(); rrect(ctx, 110, y + 45, max(40, wbar), 64, 32)
        ctx.set_source_rgba(*cols[i % len(cols)], p); ctx.fill()
        val = float(_get(bar, "value", 0)) * g
        lab = f"{_fmt(val)}{unit}"
        inside = wbar > text_width(ctx, lab, 40) + 50
        text(ctx, lab, 110 + wbar - 25 if inside else 110 + max(40, wbar) + 20, y + 91, 40,
             S.bg1 if inside else S.text, align="right" if inside else "left", alpha=p)


# 8 ---------------------------------------------------------------
def sc_wave(ctx, t, b, K, S):
    icon = b.get("icon")
    if icon:
        badge(ctx, icon, W / 2, 470, 120, S, p=pop(t, 0, .45), t=t)
    show = appear(t, 0, .5)
    ctx.new_path(); ctx.set_source_rgba(*S.text, .25 * show); ctx.set_line_width(3)
    rrect(ctx, 90, 700, 900, 420, 30); ctx.stroke()
    text(ctx, _get(b, "label", ""), 130, 760, 40, S.accent, align="left", alpha=show)
    ov = b.get("overlay")
    o = 0
    if ov:
        to = K(_get(ov, "at"), .4)
        o = appear(t, to, .5)
        text(ctx, _get(ov, "label", ""), 950, 760, 40, S.bad, align="right", alpha=o)
    anti, flat = b.get("anti"), b.get("flat")
    amp = 70
    if flat:
        tf = K(_get(flat, "at"), .75)
        amp = 70 * (1 - ease((t - tf) / .8)) if t >= tf else 70
    if anti:
        ta = K(_get(anti, "at"), .45)
        pa = appear(t, ta, .5)
        if pa > 0 and amp > 1:
            # the mirror-image wave, drawn upside down (180 degrees out of phase)
            wave(ctx, 130, 950, 920, -amp * pa, 5, t * 6, S.good, 6, alpha=pa * .9)
            text(ctx, _get(anti, "label", ""), 950, 1095, 40, S.good, align="right", alpha=pa)
    wave(ctx, 130, 950, 920, amp, 5, t * 6, S.accent if amp > 1 else S.text, 7, alpha=show, overlay=o,
         overlay_cycles=75)
    if flat and t >= K(_get(flat, "at"), .75):
        q = appear(t, K(_get(flat, "at"), .75) + .5, .4)
        text(ctx, _get(flat, "label", ""), W / 2, 1010, 64, S.text, alpha=q)
    note = b.get("note")
    if note:
        chip(ctx, _get(note, "text", ""), W / 2, 1200, S.bad, appear(t, K(_get(note, "at"), .7), .4), size=46)


# 9 ---------------------------------------------------------------
def sc_meter(ctx, t, b, K, S):
    title = b.get("title")
    if title:
        text_block(ctx, title, W / 2, 470, 56, S.muted, alpha=appear(t, 0))
    at = K(b.get("at"), .4)
    v = clamp(float(_get(b, "value", .8)))
    fill = ease((t - at + .2) / .9) * v if t > at - .2 else .12 * appear(t, 0)
    ctx.new_path(); rrect(ctx, 150, 620, 780, 96, 48); ctx.set_source_rgba(*S.text, .15); ctx.fill()
    ctx.new_path(); rrect(ctx, 150, 620, max(96, 780 * fill), 96, 48); ctx.set_source_rgb(*S.bad); ctx.fill()
    lo, hi = _get(b, "low", ""), _get(b, "high", "")
    text(ctx, lo, 150, 780, 38, S.muted, align="left", alpha=appear(t, 0))
    text(ctx, hi, 930, 780, 38, S.muted, align="right", alpha=appear(t, 0))
    q = appear(t, at, .5)
    text_block(ctx, _get(b, "label", ""), W / 2, 920, 96, S.bad, alpha=q)


# 10 --------------------------------------------------------------
def sc_bubble(ctx, t, b, K, S):
    icon = _get(b, "icon", "message-circle")
    at = K(b.get("at"), .75)
    look = appear(t, at - 1.2, .5)
    if icon == "@cat":
        rings(ctx, W / 2, 860, t, S.accent)
        cat(ctx, W / 2, 640, 230, S, eyes_open=.5 + .5 * look, look_up=look, purr=1, t=t)
    else:
        badge(ctx, icon, W / 2, 660, 220, S, p=pop(t, 0, .45), t=t)
    if b.get("prop"):
        badge(ctx, b["prop"], W / 2, 1060, 110, S, color=S.good, p=pop(t, .3, .45), t=t, bob=False)
    bubble(ctx, 800, 215, _get(b, "text", "..."), S, appear(t, at - .1, .4), size=60)


# 11 --------------------------------------------------------------
def sc_statement(ctx, t, b, K, S):
    words = _get(b, "text", "").split()
    hl = {w.lower().strip(",.!?") for w in b.get("highlight", [])}
    size = 104 if len(words) <= 6 else 84
    lines = wrap(ctx, " ".join(words), size, 920)
    n = len(words); i = 0
    y = 760 - (len(lines) - 1) * size * .6
    for ln in lines:
        lw = text_width(ctx, ln, size); x = W / 2 - lw / 2
        space = text_width(ctx, " ", size)
        for w in ln.split():
            tw = K(w, .05 + .55 * i / max(1, n)) if b.get("sync", True) else .05 + .55 * i / max(1, n)
            p = appear(t, tw - .05, .25)
            col = S.accent if w.lower().strip(",.!?") in hl else S.text
            ghost = .18 * appear(t, 0, .4)          # whole statement visible faintly from the start
            ctx.save(); ctx.translate(0, 18 * (1 - p))
            text(ctx, w, x, y, size, col, align="left", alpha=max(ghost, p), stroke=8 if p > .5 else 0)
            ctx.restore()
            x += text_width(ctx, w, size) + space; i += 1
        y += size * 1.2
    if b.get("sub"):
        text(ctx, b["sub"], W / 2, y + 40, 52, S.muted, alpha=appear(t, .6))
    if b.get("icon"):
        badge(ctx, b["icon"], W / 2, 420, 120, S, p=pop(t, 0, .45), t=t)


SCENES = {"hero": sc_hero, "tags": sc_tags, "link": sc_link, "number": sc_number, "compare": sc_compare,
          "timeline": sc_timeline, "bars": sc_bars, "wave": sc_wave, "meter": sc_meter,
          "bubble": sc_bubble, "statement": sc_statement}
