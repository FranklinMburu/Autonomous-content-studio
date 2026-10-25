"""Where things live, and one-time downloads of the free assets (voice model, icon set, fonts).

Everything heavy is downloaded into cache/ on first use, so the code itself stays small.
"""
import hashlib, io, json, os, platform, shutil, subprocess, tarfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path(os.environ.get("ACS_CACHE", ROOT / "cache"))
OUT = Path(os.environ.get("ACS_OUT", ROOT / "out"))
FONTS = ROOT / "assets" / "fonts"

KOKORO_BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/"
KOKORO_FILES = {"kokoro-v1.0.onnx": 300_000_000, "voices-v1.0.bin": 25_000_000}  # minimum sane sizes
TABLER_VERSION = "3.49.0"
TABLER_URL = f"https://registry.npmjs.org/@tabler/icons/-/icons-{TABLER_VERSION}.tgz"


def _download(url, dest, min_size=0):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "autonomous-content-studio"})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 20)
    if tmp.stat().st_size < min_size:
        tmp.unlink()
        raise RuntimeError(f"download of {url} looks truncated")
    tmp.replace(dest)


def models_dir():
    d = CACHE / "models"
    for name, min_size in KOKORO_FILES.items():
        p = d / name
        if not p.exists() or p.stat().st_size < min_size:
            _download(KOKORO_BASE + name, p, min_size)
    return d


def icons_dir():
    d = CACHE / "icons" / TABLER_VERSION
    if not (d / "icons" / "outline").exists():
        buf = io.BytesIO()
        req = urllib.request.Request(TABLER_URL, headers={"User-Agent": "autonomous-content-studio"})
        print(f"  downloading icon set {TABLER_URL}")
        with urllib.request.urlopen(req, timeout=120) as r:
            buf.write(r.read())
        buf.seek(0)
        d.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=buf, mode="r:gz") as t:
            for m in t.getmembers():
                # keep only what we use; strip the leading "package/"
                rel = m.name.split("/", 1)[-1]
                if not (rel.startswith("icons/outline/") or rel.startswith("icons/filled/")
                        or rel in ("icons.json", "LICENSE")):
                    continue
                if not m.isfile() or ".." in rel:
                    continue
                target = d / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(t.extractfile(m).read())
    return d


def ensure_fonts():
    """Make the bundled Poppins font visible to Cairo. Falls back silently to a system sans font."""
    system = platform.system()
    try:
        if system == "Linux":
            target = Path.home() / ".local" / "share" / "fonts" / "acs"
            if not (target / "Poppins-Bold.ttf").exists():
                target.mkdir(parents=True, exist_ok=True)
                for f in FONTS.glob("*.ttf"):
                    shutil.copy(f, target / f.name)
                if shutil.which("fc-cache"):
                    subprocess.run(["fc-cache", "-f", str(target)], check=False, capture_output=True)
        elif system == "Windows":
            import ctypes
            FR_PRIVATE = 0x10
            for f in FONTS.glob("*.ttf"):
                ctypes.windll.gdi32.AddFontResourceExW(str(f), FR_PRIVATE, 0)
        elif system == "Darwin":
            target = Path.home() / "Library" / "Fonts"
            for f in FONTS.glob("*.ttf"):
                if not (target / f.name).exists():
                    shutil.copy(f, target / f.name)
    except Exception as e:  # fonts are cosmetic; never block a render
        print(f"  note: could not register bundled font ({e}); using system sans")


def slugify(s):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in s)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")[:60] or "video"
