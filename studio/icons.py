"""Icons from the open-source Tabler set (MIT license), looked up by name or by tag.

The script names icons in plain words ("brain", "heart", "rocket"). If a name doesn't exist,
we search the tags and pick the closest match, so a script never fails over an icon name.
"""
import difflib, io, json, re
import cairo, cairosvg
from .paths import icons_dir

_index = None
_cache = {}
FALLBACK = "sparkles"


def _load():
    global _index
    if _index is None:
        d = icons_dir()
        meta = json.loads((d / "icons.json").read_text(encoding="utf-8"))
        _index = {"dir": d, "meta": meta, "names": sorted(meta)}
    return _index


def resolve(name):
    """Return (resolved_name, exact?) for a requested icon name."""
    if not name:
        return FALLBACK, False
    if name.startswith("@"):  # hand-drawn characters handled by draw.py
        return name, True
    idx = _load()
    n = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if n in idx["meta"]:
        return n, True
    words = set(n.split("-"))
    best, score = None, 0
    for k, m in idx["meta"].items():
        tags = set(m.get("tags", [])) | set(k.split("-"))
        s = len(words & tags) * 3 - len(k) / 40  # prefer short, simple icons
        if "off" in k.split("-") and "off" not in words:
            s -= 5
        if s > score:
            best, score = k, s
    if best:
        return best, False
    close = difflib.get_close_matches(n, idx["names"], n=1, cutoff=0.6)
    return (close[0], False) if close else (FALLBACK, False)


def exists(name):
    return resolve(name)[1]


def surface(name, size, color, filled=False):
    """Cairo surface of the icon at `size` px, stroked in `color` (r,g,b 0..1)."""
    name, _ = resolve(name)
    key = (name, size, color, filled)
    if key in _cache:
        return _cache[key]
    d = _load()["dir"] / "icons"
    path = d / "filled" / f"{name}.svg"
    if not (filled and path.exists()):
        path = d / "outline" / f"{name}.svg"
    svg = path.read_text(encoding="utf-8")
    hexc = "#%02x%02x%02x" % tuple(int(c * 255) for c in color)
    svg = svg.replace("currentColor", hexc)
    if not filled:  # slightly heavier stroke reads better on phones
        svg = svg.replace('stroke-width="2"', 'stroke-width="1.75"')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    surf = cairo.ImageSurface.create_from_png(io.BytesIO(png))
    _cache[key] = surf
    return surf
