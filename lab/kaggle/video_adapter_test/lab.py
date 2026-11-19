"""Video adapter test, run 3 (19 Nov 2026): the chip close-up through every free backend on Kaggle's free T4.

Run 1: Wan out of GPU memory (VAE decode); LTX distilled made coloured noise that passed the numeric checks.
Run 2: Kaggle killed the job (RAM) while Wan's image mode loaded the model a second time.
Now: Wan's image mode reuses the loaded parts, its VAE is tiled and it retries smaller; LTX uses Hidden Reasons'
production settings; a vision judge (Qwen2-VL-2B) checks every clip; each backend runs in its own process.
Shot A: image-to-video from OUR OWN 3D-engine still. Shot B: text-to-video only.
"""
import base64, json, os, subprocess, sys, time
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
src = json.loads(FILES["src.json"])  # noqa: F821  (injected by lab/kaggle/run.py)
for rel, text in src["files"].items():
    p = f"/kaggle/working/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(text)
open("/kaggle/working/chip_still.jpg", "wb").write(base64.b64decode(src["still_b64"]))
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.35", "transformers>=4.50", "accelerate",
                "sentencepiece", "ftfy", "imageio[ffmpeg]", "imageio-ffmpeg", "qwen-vl-utils"], check=False)
log(f"install {time.time() - t0:.0f}s")

CHILD = r'''
import json, os, sys, time
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
os.environ.setdefault("WAN_STEPS", "20")
sys.path.insert(0, "/kaggle/working")
from studio.video_backends import Router, Shot
from studio.video_backends.judge import VisionJudge
OUT, ONE = "/kaggle/working/out", sys.argv[1]
LOG = open(f"{OUT}/log.txt", "a")
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
PROMPT = ("extreme close-up macro shot of a modern computer processor chip on a dark circuit board, photorealistic, "
          "glossy black silicon die with a silver heat spreader frame and a grid of small square cores, thin glowing "
          "blue traces, shallow depth of field, cinematic studio lighting, subtle reflections, product commercial")
shots = {
    "A_from_our_still": Shot(prompt=PROMPT, image="/kaggle/working/chip_still.jpg", seconds=2.5, camera="slow push in",
                             tags={"test": "chip", "mode": "image-to-video"}),
    "B_text_only": Shot(prompt=PROMPT, seconds=2.5, camera="slow push in, camera orbits slightly",
                        tags={"test": "chip", "mode": "text-to-video"}),
}
router = Router(root="/kaggle/working", extra_check=VisionJudge("a computer chip"), keep_rejected=True)
summary = {}
for name, shot in shots.items():
    t = time.time()
    try:
        r = router.make(shot, f"{OUT}/tmp", only=[ONE])
        os.replace(r.path, f"{OUT}/{name}__{ONE}.mp4")
        summary[name] = r.tried[-1][1]
    except Exception as e:
        summary[name] = str(e)[-500:]
        for f in os.listdir(f"{OUT}/tmp"):
            if f.startswith("rejected_") and f.endswith(f"_{ONE}.mp4"):
                os.replace(f"{OUT}/tmp/{f}", f"{OUT}/{name}__{ONE}__REJECTED.mp4")
    log(f"{name} / {ONE}: {time.time() - t:.0f}s -> {summary[name]}")
json.dump(summary, open(f"{OUT}/summary_{ONE}.json", "w"), indent=1)
'''
open("/kaggle/working/child.py", "w").write(CHILD)
os.makedirs(f"{OUT}/tmp", exist_ok=True)
for backend in ("own", "ltx", "wan22"):   # cheapest first, so a late kill still leaves results
    t = time.time()
    r = subprocess.run([sys.executable, "/kaggle/working/child.py", backend])
    log(f"backend {backend}: child exit {r.returncode} after {time.time() - t:.0f}s")
log(f"total {time.time() - t0:.0f}s")
