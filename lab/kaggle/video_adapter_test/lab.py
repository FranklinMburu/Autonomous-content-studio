"""Video adapter test (19 Nov 2026): the chip close-up through every free backend, on Kaggle's free T4.

Shot A: image-to-video from OUR OWN 3D-engine still of the chip (keeps our composition, adds realism and motion).
Shot B: text-to-video, no picture (how far an open model gets alone).
Each backend is forced in turn (router `only=`) so Franklin can compare them side by side; the router's own checks
(plays, right length, not black, moves, no flicker) run on every clip. FILES (added by run.py) carries the adapter
source and the still, so this single script runs the same code as the repo.
"""
import base64, json, os, subprocess, sys, time, traceback
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ.setdefault("WAN_STEPS", "20")
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
src = json.loads(FILES["src.json"])  # noqa: F821  (injected by lab/kaggle/run.py)
for rel, text in src["files"].items():
    p = f"/kaggle/working/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(text)
open("/kaggle/working/chip_still.jpg", "wb").write(base64.b64decode(src["still_b64"]))
sys.path.insert(0, "/kaggle/working")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.35", "transformers>=4.50", "accelerate",
                "sentencepiece", "ftfy", "imageio[ffmpeg]", "imageio-ffmpeg"], check=False)
log(f"install {time.time() - t0:.0f}s")

from studio.video_backends import Router, Shot  # noqa: E402

PROMPT = ("extreme close-up macro shot of a modern computer processor chip on a dark circuit board, photorealistic, "
          "glossy black silicon die with a silver heat spreader frame and a grid of small square cores, thin glowing "
          "blue traces, shallow depth of field, cinematic studio lighting, subtle reflections, product commercial")
shots = {
    "A_from_our_still": Shot(prompt=PROMPT, image="/kaggle/working/chip_still.jpg", seconds=2.5, camera="slow push in",
                             tags={"test": "chip", "mode": "image-to-video"}),
    "B_text_only": Shot(prompt=PROMPT, seconds=2.5, camera="slow push in, camera orbits slightly",
                        tags={"test": "chip", "mode": "text-to-video"}),
}
router = Router(root="/kaggle/working")
summary = {}
for backend in ("wan22", "ltx", "own"):
    for name, shot in shots.items():
        t = time.time()
        try:
            r = router.make(shot, f"{OUT}/tmp", only=[backend])
            dest = f"{OUT}/{name}__{backend}.mp4"; os.replace(r.path, dest)
            summary[f"{name}/{backend}"] = r.tried[-1][1]
        except Exception as e:  # noqa: BLE001
            summary[f"{name}/{backend}"] = str(e)[-400:]
        log(f"{name} / {backend}: {time.time() - t:.0f}s -> {summary[f'{name}/{backend}']}")
json.dump(summary, open(f"{OUT}/summary.json", "w"), indent=1)
log(f"total {time.time() - t0:.0f}s")
