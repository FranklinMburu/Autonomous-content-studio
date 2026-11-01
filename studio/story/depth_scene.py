"""2.5D scenes: a painted background + its depth map, filmed by a moving camera (parallax), so the picture has real
depth like the benchmark's 3D world, without AI video (which melts after ~2 s on free GPUs, lab test 1).

    scene = DepthScene(bg_png, depth_png)        # depth: white = near, black = far (Depth-Anything output)
    scene.draw(c, k, move="push", amount=1.0)   # k = 0..1 progress through the shot
    scene.place(x, y, k, move, amount) -> (x', y', s)  # where a thing standing at (x, y) is at progress k

The picture is cut into depth layers; near layers move and grow more than far ones. Each layer also keeps everything
behind it, so no holes open up. Moves: push (dolly in), pull, left, right, up (crane), down.
"""
import math

import cairo
import numpy as np

W, H = 1080, 1920
MOVES = {"push": (0, 0, 1), "pull": (0, 0, -1), "left": (-1, 0, 0.3), "right": (1, 0, 0.3),
         "up": (0, -1, 0.3), "down": (0, 1, 0.3)}


def _load_png(path):
    s = cairo.ImageSurface.create_from_png(str(path))
    a = np.ndarray((s.get_height(), s.get_stride() // 4, 4), np.uint8, s.get_data())[:, :s.get_width()].copy()
    return a  # BGRA


def _box_blur(m, r):
    if r <= 0:
        return m
    k = 2 * r + 1
    c = np.cumsum(np.pad(m, ((r + 1, r), (0, 0)), mode="edge"), 0); m = (c[k:] - c[:-k]) / k
    c = np.cumsum(np.pad(m, ((0, 0), (r + 1, r)), mode="edge"), 1); return (c[:, k:] - c[:, :-k]) / k


def _resize_nearest(a, w, h):
    ys = (np.arange(h) * a.shape[0] / h).astype(int); xs = (np.arange(w) * a.shape[1] / w).astype(int)
    return a[ys][:, xs]


def _resize_bilinear(a, w, h):
    y = np.linspace(0, a.shape[0] - 1, h); x = np.linspace(0, a.shape[1] - 1, w)
    y0 = np.floor(y).astype(int); x0 = np.floor(x).astype(int)
    y1 = np.minimum(y0 + 1, a.shape[0] - 1); x1 = np.minimum(x0 + 1, a.shape[1] - 1)
    wy = (y - y0)[:, None, None] if a.ndim == 3 else (y - y0)[:, None]
    wx = (x - x0)[None, :, None] if a.ndim == 3 else (x - x0)[None, :]
    a = a.astype(np.float32)
    top = a[y0][:, x0] * (1 - wx) + a[y0][:, x1] * wx
    bot = a[y1][:, x0] * (1 - wx) + a[y1][:, x1] * wx
    return top * (1 - wy) + bot * wy


class DepthScene:
    def __init__(self, bg_png, depth_png, layers=7, overscan=1.12):
        bg = _resize_bilinear(_load_png(bg_png), W, H)                 # fill the frame
        d = _load_png(depth_png)[..., 1].astype(np.float32) / 255.0      # grey: any channel
        d = _box_blur(_resize_bilinear(d, W, H), 2)
        self.depth = d
        self.overscan = overscan
        qs = np.quantile(d, np.linspace(0, 1, layers + 1)[:-1])
        self.layers = []  # (surface, z) far -> near; each keeps everything nearer than its threshold
        for i, q in enumerate(qs):
            mask = np.ones_like(d) if i == 0 else np.clip((d - q) / 0.04 + 0.5, 0, 1)
            mask = _box_blur(mask, 2) if i else mask
            px = bg.copy()
            alpha = (mask * 255).astype(np.uint8)
            for ch in range(3):  # premultiply
                px[..., ch] = (px[..., ch].astype(np.float32) * mask).astype(np.uint8)
            px[..., 3] = alpha
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            np.ndarray((H, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :W] = px
            surf.mark_dirty()
            z = float(np.mean(d[mask > 0.5])) if (mask > 0.5).any() else float(q)
            self.layers.append((surf, z))

    def _xf(self, z, k, move, amount):
        mx, my, mz = MOVES.get(move, (0, 0, 1))
        e = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, k)))  # smooth start and stop
        p = (e - 0.5) * amount
        s = self.overscan * (1 + mz * p * (0.05 + 0.16 * z))
        return mx * p * (40 + 160 * z), my * p * (30 + 120 * z), s

    def draw(self, c, k, move="push", amount=1.0, until_z=None, from_z=None):
        """Draw the layers (optionally only those up to / beyond a depth, to put things between them)."""
        for surf, z in self.layers:
            if until_z is not None and z > until_z:
                continue
            if from_z is not None and z <= from_z:
                continue
            dx, dy, s = self._xf(z, k, move, amount)
            c.save(); c.translate(W / 2 + dx, H / 2 + dy); c.scale(s, s); c.translate(-W / 2, -H / 2)
            c.set_source_surface(surf, 0, 0); c.get_source().set_filter(cairo.FILTER_GOOD); c.paint(); c.restore()

    def depth_at(self, x, y):
        return float(self.depth[int(min(H - 1, max(0, y))), int(min(W - 1, max(0, x)))])

    def place(self, x, y, k, move="push", amount=1.0):
        """Where a thing standing at (x, y) appears at progress k, and how much bigger (it moves with the floor)."""
        z = self.depth_at(x, y)
        dx, dy, s = self._xf(z, k, move, amount)
        return W / 2 + dx + (x - W / 2) * s, H / 2 + dy + (y - H / 2) * s, s


def scene_light(scene, x, y, r=160):
    """The average colour of the background around (x, y): used to light a character with its scene's light."""
    bg = scene.layers[0][0]
    a = np.ndarray((H, bg.get_stride() // 4, 4), np.uint8, bg.get_data())
    y0, y1, x0, x1 = int(max(0, y - 2 * r)), int(min(H, y)), int(max(0, x - r)), int(min(W, x + r))
    m = a[y0:y1, x0:x1, :3].reshape(-1, 3).mean(0) / 255.0
    return float(m[2]), float(m[1]), float(m[0])  # BGRA -> rgb


def draw_lit(c, draw_fn, x, y, s, light, height=380):
    """Draw a cast member (draw_fn(c) with feet at the origin) standing at (x, y), scale s, lit by `light` (rgb):
    a soft contact shadow on the ground, the character's colours tinted by the scene light, a rim of that light."""
    # contact shadow
    c.save(); c.translate(x, y); c.scale(s, s * 0.22)
    g = cairo.RadialGradient(0, 0, 10, 0, 0, 150)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.45); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.arc(0, 0, 150, 0, 2 * math.pi); c.fill(); c.restore()
    # the character, graded by the scene light
    c.push_group()
    c.save(); c.translate(x, y); c.scale(s, s); draw_fn(c); c.restore()
    char = c.pop_group()
    c.set_source(char); c.paint()
    lum = 0.3 * light[0] + 0.59 * light[1] + 0.11 * light[2]
    tint = tuple(min(1.0, v / max(lum, 0.05) * 0.85) for v in light)
    c.save(); c.set_operator(cairo.OPERATOR_MULTIPLY); c.set_source_rgba(*tint, 0.45); c.mask(char); c.restore()
    dark = max(0.0, 0.55 - lum)  # darker scenes darken the character too
    if dark > 0:
        c.save(); c.set_source_rgba(0, 0, 0, dark * 0.7); c.mask(char); c.restore()
