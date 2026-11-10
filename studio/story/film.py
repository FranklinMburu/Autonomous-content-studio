"""Film style: an episode made of painted 3D-film shots (like the benchmark), not drawn 2D scenes.

film.json (in the episode folder) lists the cast (one look per role) and ~30 shots. Each shot starts on a spoken word
("at": word#n) and is either a short AI clip ("clip": true, ~1.4 s of real motion) or a still painting filmed with a
depth-parallax camera move ("move": push | pull | left | right | up | down). The pictures, depth maps and clips are made
on a free Kaggle GPU (lab/kaggle/film_episode) and arrive in one assets folder:
    shot_<name>.png  depth_<name>.png  clip_<name>.mp4 (clip shots)

    python -m studio.story.film make episodes/<ch>/<NNN-slug> --assets <dir> [--narration n.wav --timing t.json]

Rules from the benchmark (Ricks Clips, measured): a new shot every ~1.9 s, the camera never stops, hard cuts inside
motion plus a few crossfades on the big turns, one caption word at a time, music and hits under the voice.
"""
import argparse, json, math, shutil, subprocess, sys, time
from pathlib import Path

import cairo
import numpy as np

from . import board as B, lib as L
from .depth_scene import DepthScene

W, H, FPS = L.W, L.H, L.FPS
XFADE = 0.3      # seconds of crossfade into a shot marked "xfade"
CLIP_FPS = 24
MIN_SPEED = 0.6  # a clip may be slowed to 60% to fill its shot; after that it holds and the camera keeps pushing


def plan(film, timing):
    """[(t0, t1, shot)] from the narration timing."""
    L.set_timing(timing)
    shots = film["shots"]
    ts = [B.when(s["at"], 0) for s in shots]
    if ts[0] != 0 or ts != sorted(ts):
        raise SystemExit(f"film.json: shots must start at 0 and be in spoken order: {ts}")
    ends = ts[1:] + [float(timing["duration"])]
    return list(zip(ts, ends, shots))


def problems(film, timing, assets):
    """What is missing or too fast; empty = ready to render."""
    out = []
    for t0, t1, s in plan(film, timing):
        n = s["name"]
        if not (Path(assets) / f"shot_{n}.png").exists():
            out.append(f"{n}: no picture")
        if s.get("clip") and not (Path(assets) / f"clip_{n}.mp4").exists() and not (Path(assets) / f"depth_{n}.png").exists():
            out.append(f"{n}: no clip and no depth map")
        if not s.get("clip") and not (Path(assets) / f"depth_{n}.png").exists():
            out.append(f"{n}: no depth map")
        if t1 - t0 < 0.5:
            out.append(f"{n}: only {t1 - t0:.2f} s on screen")
    return out


def _surface(rgb):
    """numpy HxWx3 uint8 -> cairo surface."""
    h, w = rgb.shape[:2]
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    a = np.ndarray((h, s.get_stride() // 4, 4), np.uint8, s.get_data())
    a[:, :w, 0], a[:, :w, 1], a[:, :w, 2], a[:, :w, 3] = rgb[..., 2], rgb[..., 1], rgb[..., 0], 255
    s.mark_dirty()
    return s


def read_clip(mp4, max_frames=None):
    """Frames of a clip as cairo surfaces (native size). None if the clip is missing, empty or broken: the shot then
    uses its still picture with depth motion instead of crashing the whole video (10 Nov, Fleming: Kaggle returned
    41 pictures but 0 usable clips, and one unreadable clip stopped the edit)."""
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", str(mp4)],
                               capture_output=True, text=True, check=True).stdout
        w, h = (int(v) for v in probe.strip().split(",")[:2])
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    except (subprocess.CalledProcessError, ValueError, OSError) as e:
        print(f"clip {Path(mp4).name} unreadable ({type(e).__name__}): using the still picture", flush=True)
        return None
    if not len(fr):
        return None
    if max_frames:
        fr = fr[:max_frames]
    fr = fr[:good_frames(fr)]
    return [_surface(f) for f in fr]


MELT = 0.85  # AI clips go soft as they "melt": keep frames while they stay at least 85% as sharp as the first one


def good_frames(fr, min_keep=12):
    """How many frames of a clip to keep: up to the first frame that lost >15% of the first frame's detail
    (measured on episode 002: every clip that visibly smeared dropped below 0.85, the clean ones stayed above 0.93)."""
    def sharp(x):
        g = x.astype(np.float32).mean(2)
        return np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean()
    s0 = sharp(fr[0]) + 1e-6
    for i in range(min_keep, len(fr)):
        if sharp(fr[i]) / s0 < MELT:
            return i
    return len(fr)


def _cover(c, surf, zoom=1.0, dx=0.0, dy=0.0, alpha=1.0):
    """Paint a surface so it fills the 9:16 frame (centre crop), zoomed around the centre."""
    w, h = surf.get_width(), surf.get_height()
    s = max(W / w, H / h) * zoom
    c.save(); c.translate(W / 2 + dx, H / 2 + dy); c.scale(s, s); c.translate(-w / 2, -h / 2)
    c.set_source_surface(surf, 0, 0); c.get_source().set_filter(cairo.FILTER_GOOD)
    c.paint_with_alpha(alpha) if alpha < 1 else c.paint()
    c.restore()


class Shot:
    def __init__(self, t0, t1, spec, assets):
        self.t0, self.t1, self.spec, self.name = t0, t1, spec, spec["name"]
        a = Path(assets)
        clip = a / f"clip_{self.name}.mp4"
        self.frames = read_clip(clip, spec.get("clip_frames")) if spec.get("clip") and clip.exists() else None
        self.scene = None
        if not self.frames:
            self.scene = DepthScene(a / f"shot_{self.name}.png", a / f"depth_{self.name}.png")

    def draw(self, c, T, alpha=1.0):
        d = max(0.3, self.t1 - self.t0)
        k = (T - self.t0) / d
        if self.frames:
            n = len(self.frames)
            speed = max(MIN_SPEED, min(1.0, (n / CLIP_FPS) / d))
            pos = min(n - 1.0, max(0.0, (T - self.t0) * speed * CLIP_FPS))
            i = int(pos); f = pos - i
            held = max(0.0, (T - self.t0) * speed * CLIP_FPS - (n - 1)) / CLIP_FPS  # seconds past the clip's end
            # the camera always moves (benchmark: ~85% of frames move), on top of the clip's own motion
            e = 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, k)))
            z = 1.0 + 0.06 * e + 0.035 * held
            if alpha < 1:
                c.push_group()
            _cover(c, self.frames[i], z)
            if f > 0.01 and i + 1 < n:   # blend neighbours: smooth slow motion
                _cover(c, self.frames[i + 1], z, alpha=f)
            if alpha < 1:
                c.pop_group_to_source(); c.paint_with_alpha(alpha)
        else:
            if alpha < 1:
                c.push_group()
            self.scene.draw(c, k, self.spec.get("move", "push"), float(self.spec.get("amount", 1.0)))
            if alpha < 1:
                c.pop_group_to_source(); c.paint_with_alpha(alpha)


def _vignette(c):
    g = cairo.RadialGradient(W / 2, H / 2, 520, W / 2, H / 2, 1300)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.42)
    c.set_source(g); c.paint()


def cues(film, timing):
    """Sound effects for the film: a whoosh into each crossfade, hits on shots marked "hit", a riser into the ending."""
    pl = plan(film, timing)
    out = []
    for t0, t1, s in pl:
        if s.get("xfade"):
            out.append((t0, "whoosh", 1.0))
        if s.get("hit"):
            out.append((B.when(s["hit"], t0) if isinstance(s["hit"], str) else t0, "impact", 1.0))
    if len(pl) > 2:
        out.append((pl[-1][0], "riser", 1.0))   # a reverse swell that ends on the cut into the last shot
    out.sort()
    spaced, last = [], {}
    for t, k, g in out:
        if t < 0 or t - last.get(k, -99) < {"impact": 4.0, "whoosh": 3.0, "riser": 5.0}.get(k, 0.5):
            continue
        if spaced and t - spaced[-1][0] < 1.5 and k != "riser":   # never two effects on top of each other
            continue                                             # (the swell ENDS on its cue, so it may meet a hit)
        spaced.append((t, k, g)); last[k] = t
    return spaced


def render(film, timing, assets, audio, out_mp4, preset="veryfast", log=print):
    pl = plan(film, timing)
    dur = float(timing["duration"])
    key = {w.lower() for w in film.get("key_words", [])}
    L.set_timing(timing)
    cache = {}

    def shot(i):
        if i not in cache:
            for j in [j for j in cache if j < i - 1]:
                del cache[j]   # keep memory small: only the current and previous shot
            t0, t1, s = pl[i]
            cache[i] = Shot(t0, t1, s, assets)
        return cache[i]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    n = int(dur * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset", preset, "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_mp4)],
                          stdin=subprocess.PIPE)
    for f in range(n):
        T = f / FPS
        i = max(j for j, p in enumerate(pl) if p[0] <= T + 1e-6)
        c = cairo.Context(surf); c.set_source_rgb(0, 0, 0); c.paint()
        t0, _, s = pl[i]
        if i and s.get("xfade") and T - t0 < XFADE:   # crossfade from the previous shot
            shot(i - 1).draw(c, T)
            shot(i).draw(c, T, alpha=(T - t0) / XFADE)
        else:
            shot(i).draw(c, T)
        _vignette(c)
        L.caption(c, T, key)
        surf.flush(); ff.stdin.write(bytes(surf.get_data()))
        if f % 300 == 0:
            log(f"  frame {f}/{n}")
    ff.stdin.close(); ff.wait()
    if ff.returncode != 0:
        raise RuntimeError("ffmpeg failed")
    return out_mp4


OUTRO = 1.6  # seconds after the last word: the final shot holds while the music swells and fades


def qc(video, expected_s, assets=None):
    """Last guardrail before publishing: length, loudness, no black gaps, and the picture checker's verdict.
    Returns (problems, notes)."""
    probs, notes = [], []
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                             capture_output=True, text=True).stdout or 0)
    if abs(d - expected_s) > 0.5:
        probs.append(f"video is {d:.1f}s, expected {expected_s:.1f}s")
    er = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    m = [l for l in er.splitlines() if l.strip().startswith("I:")]
    lufs = float(m[-1].split()[1]) if m else None
    if lufs is None or abs(lufs + 14) > 1.5:
        probs.append(f"loudness {lufs} LUFS (want -14)")
    bd = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "blackdetect=d=0.3:pix_th=0.06", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    if "black_start" in bd:
        probs.append("black gap(s) in the picture: " + "; ".join(l.split("blackdetect")[-1].strip() for l in bd.splitlines() if "black_start" in l)[:200])
    ck = Path(assets or "") / "checks.json"
    if assets and ck.exists():
        failed = json.loads(ck.read_text(encoding="utf-8")).get("failed", [])
        if failed:
            notes.append(f"picture checker: still failing after 3 tries: {', '.join(failed)}")
        if len(failed) >= 3 or "(checker did not run)" in failed:
            probs.append(f"{len(failed)} shot(s) failed the picture check: {', '.join(failed)}")
    notes.append(f"length {d:.1f}s, loudness {lufs} LUFS")
    return probs, notes


def make(folder, assets, narration=None, timing_path=None, out_dir=None, preset="veryfast", memory=None, log=print):
    from ..paths import OUT, ensure_fonts, slugify
    from . import sound
    folder = Path(folder)
    film = json.loads((folder / "film.json").read_text(encoding="utf-8"))
    script = json.loads((folder / "script.json").read_text(encoding="utf-8"))
    ensure_fonts()
    out = Path(out_dir) if out_dir else OUT / f"{time.strftime('%Y%m%d-%H%M')}-film-{slugify(script.get('title', folder.name))}"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if narration and timing_path:
        shutil.copy(narration, out / "narration.wav"); timing = json.loads(Path(timing_path).read_text(encoding="utf-8"))
    else:
        from .__main__ import narrate
        timing = narrate(script, out)
    probs = problems(film, timing, assets)
    if probs:
        log("Film problems:\n  " + "\n  ".join(probs))
        if any("no picture" in p or "no depth" in p for p in probs):
            return 1
    audio, track = out / "narration.wav", None
    if script.get("sound", True):
        from .filmkit import load_memory
        avoid = [e.get("music") for e in load_memory(memory).get("episodes", [])[-4:] if e.get("episode") != folder.name]
        audio, track = sound.mix_film(timing, out / "narration.wav", out / "mix.wav", cues(film, timing),
                                      mood=film.get("music"), title=script.get("title", folder.name), avoid=avoid,
                                      outro=OUTRO, log=log, track_name=script.get("music"))
    (out / "music.txt").write_text(track or "", encoding="utf-8")
    log(f"[render] {len(film['shots'])} shots")
    full = {**timing, "duration": float(timing["duration"]) + (OUTRO if script.get("sound", True) else 0)}
    render(film, full, assets, audio, out / "video.mp4", preset=preset, log=log)
    from ..qc import contact_sheet
    contact_sheet(out / "video.mp4", out / "contact.png", every=2.0)
    qp, qn = qc(out / "video.mp4", full["duration"], assets)
    (out / "qc.json").write_text(json.dumps({"problems": qp, "notes": qn}, indent=1), encoding="utf-8")
    log("[qc] " + ("; ".join(qn)) + ("" if not qp else "\n[qc] PROBLEMS: " + "; ".join(qp)))
    for f in ("script.json", "sources.md", "film.json"):
        if (folder / f).exists():
            shutil.copy(folder / f, out / f)
    log(f"[done] {time.time() - t0:.0f} s -> {out / 'video.mp4'}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m studio.story.film")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("episode"); m.add_argument("--assets", required=True)
    m.add_argument("--narration"); m.add_argument("--timing"); m.add_argument("--out"); m.add_argument("--preset", default="veryfast")
    m.add_argument("--memory", help="the channel memory (used.json): recent videos' music is not repeated")
    a = ap.parse_args(argv)
    return make(a.episode, a.assets, a.narration, a.timing, a.out, a.preset, a.memory)


if __name__ == "__main__":
    sys.exit(main())
