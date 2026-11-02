"""Paint every shot of an episode (shots.json): SDXL background in the soft-3D film look + a depth map for parallax.
Output: out/bg_<id>.png, out/depth_<id>.png, out/log.txt. About 30 s per shot on a free Kaggle T4."""
import json, os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


SPEC = json.loads(FILES["shots.json"])  # noqa: F821  (injected by lab/kaggle/run.py)
t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate"], check=False)
import torch  # noqa: E402
from diffusers import StableDiffusionXLPipeline  # noqa: E402
from transformers import pipeline  # noqa: E402
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16,
                                                 variant="fp16", use_safetensors=True).to("cuda")
dp = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=1 if torch.cuda.device_count() > 1 else 0)
log(f"ready {time.time() - t0:.0f}s")
for sh in SPEC["shots"]:
    try:
        t = time.time()
        im = pipe(prompt=f"{sh['prompt']}, {SPEC['style']}", negative_prompt=SPEC["negative"], width=768, height=1344,
                  num_inference_steps=32, guidance_scale=6.5, generator=torch.Generator("cuda").manual_seed(sh.get("seed", 7))).images[0]
        im.save(f"{OUT}/bg_{sh['id']}.png")
        dp(im)["depth"].save(f"{OUT}/depth_{sh['id']}.png")
        log(f"{sh['id']}: {time.time() - t:.0f}s")
    except Exception:
        log(f"{sh['id']} FAILED", traceback.format_exc()[-600:])
log(f"total {time.time() - t0:.0f}s")
