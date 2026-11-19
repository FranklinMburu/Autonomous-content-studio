"""Our own last step: a slow camera move over the shot's picture (ffmpeg only, no GPU, no network, never down).

It needs a picture. For a text-only shot the pipeline should first draw one with our own engines (the 3D showcase
engine or the motion engine); this plug does not invent pictures.
"""
import shutil, subprocess
from .base import Backend, BackendError, NotAvailable

MOVES = {  # zoompan expressions per camera word (z = zoom, x/y = top-left of the window)
    "push in": ("min(1+0.0009*on,1.25)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pull out": ("max(1.25-0.0009*on,1)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    "pan left": ("1.15", "(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"),
    "pan right": ("1.15", "(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"),
    "rise": ("1.15", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/{n})"),
}


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:  # noqa: BLE001
            exe = None
    return exe


class Own(Backend):
    name = "own"
    can_text_to_video = False

    def available(self):
        if not ffmpeg():
            raise NotAvailable("ffmpeg not found")

    def generate(self, shot, out_path):
        if not shot.image:
            raise NotAvailable("own renderer needs a start picture")
        n = max(1, round(shot.seconds * shot.fps))
        move = next((v for k, v in MOVES.items() if k in shot.camera.lower()), MOVES["push in"])
        z, x, y = (e.replace("{n}", str(n)) for e in move)
        # upscale first so the slow zoom stays smooth (no 1-pixel jitter)
        vf = (f"scale={shot.width * 4}:{shot.height * 4}:force_original_aspect_ratio=increase,"
              f"crop={shot.width * 4}:{shot.height * 4},"
              f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={shot.width}x{shot.height}:fps={shot.fps},format=yuv420p")
        r = subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", shot.image, "-vf", vf,
                            "-frames:v", str(n), "-c:v", "libx264", "-crf", "18", out_path], capture_output=True, text=True)
        if r.returncode:
            raise BackendError("ffmpeg: " + r.stderr[-400:])
