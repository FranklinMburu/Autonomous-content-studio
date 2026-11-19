"""The same quality check for every backend, so switching tools can't quietly lower the bar.

Basic checks here (always on, no GPU): the file plays, the length is right, it isn't black, it actually moves and
doesn't flicker wildly. The pipeline can pass a stronger judge on top (e.g. Hidden Reasons' picture checker,
Qwen2-VL) through Router(extra_check=...).
"""
import json, subprocess
from .own import ffmpeg


def probe(path):
    exe = ffmpeg().replace("ffmpeg", "ffprobe")
    try:
        r = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                           capture_output=True, text=True)
        return float(json.loads(r.stdout)["format"]["duration"])
    except Exception:  # noqa: BLE001  (no ffprobe next to imageio's ffmpeg: fall back to decoding)
        return None


def frame_stats(path, size=64):
    """Mean brightness and mean change between frames, from small grey frames."""
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-vf", f"scale={size}:{size},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    raw, n = r.stdout, size * size
    frames = [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)]
    if len(frames) < 2:
        return None
    bright = sum(sum(f) / n for f in frames) / len(frames)
    diffs = [sum(abs(a - b) for a, b in zip(f1, f2)) / n for f1, f2 in zip(frames, frames[1:])]
    return {"frames": len(frames), "brightness": bright, "motion": sum(diffs) / len(diffs), "max_jump": max(diffs)}


def basic_check(path, shot):
    s = frame_stats(path)
    if not s:
        return False, "unreadable or under 2 frames"
    dur = probe(path) or s["frames"] / shot.fps
    if dur < shot.seconds * 0.6:
        return False, f"too short ({dur:.1f}s of {shot.seconds}s)"
    if s["brightness"] < 8:
        return False, "black"
    if s["motion"] < 0.15:
        return False, "doesn't move"
    if s["max_jump"] > 60:
        return False, "flickers / jumps"
    return True, f"ok ({dur:.1f}s, motion {s['motion']:.1f})"
