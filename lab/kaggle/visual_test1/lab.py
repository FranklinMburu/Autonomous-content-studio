"""Visual test 1: can free open models on a free Kaggle GPU make benchmark-style shots?

1. A painted still (SDXL, open licence that allows commercial use) in the benchmark's style:
   a soft 3D cartoon world with an egg-headed character, warm light, depth of field.
2. That still turned into a short clip with a camera move (image-to-video), two open models:
   LTX-Video and Wan 2.2 TI2V-5B. Timings and any errors go to out/log.txt.
"""
import os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate",
                "sentencepiece", "imageio[ffmpeg]", "ftfy"], check=False)
import torch  # noqa: E402
log("torch", torch.__version__, "cuda", torch.cuda.is_available(), [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
log(f"install {time.time() - t0:.0f}s")

STYLE = ("soft 3D animated film still, painterly textures, warm cinematic lighting, depth of field, "
         "simple cute cartoon character with a big round white egg-shaped head, small black dot eyes, thin black outline, "
         "tiny mustache, stick-thin legs")
SCENES = {
    "scrub": ("a 19th century doctor in a dark green coat scrubbing his hands in a white washbasin, inside an old Vienna "
              "hospital ward in 1847, rows of iron beds, tall windows, evening candle light, vertical composition"),
    "street": ("two cartoon doctors in black coats arguing on a cobblestone street of old Vienna at dusk, long shadows, "
               "warm gas lamps, vertical composition"),
}
NEG = "photo, realistic human face, text, watermark, blurry, deformed, extra limbs, ugly"
img_path = {}
try:
    from diffusers import StableDiffusionXLPipeline
    t = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16,
                                                     variant="fp16", use_safetensors=True).to("cuda")
    log(f"sdxl load {time.time() - t:.0f}s")
    for k, p in SCENES.items():
        for seed in (1, 2):
            t = time.time()
            im = pipe(prompt=f"{p}, {STYLE}", negative_prompt=NEG, width=768, height=1344, num_inference_steps=30,
                      guidance_scale=6.0, generator=torch.Generator("cuda").manual_seed(seed)).images[0]
            f = f"{OUT}/still_{k}_{seed}.png"; im.save(f); img_path.setdefault(k, f)
            log(f"still {k} seed {seed}: {time.time() - t:.0f}s")
    del pipe; torch.cuda.empty_cache()
except Exception:
    log("SDXL FAILED", traceback.format_exc()[-1500:])

from PIL import Image  # noqa: E402
from diffusers.utils import export_to_video  # noqa: E402
MOTION = {"scrub": "the camera slowly pushes in toward the doctor as he scrubs his hands, soap bubbles, candle flames flicker",
          "street": "slow camera tracking shot past the two doctors as they argue and gesture, lamps flicker"}

# --- LTX-Video ---
try:
    from diffusers import LTXImageToVideoPipeline
    t = time.time()
    lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
    lp.enable_model_cpu_offload()
    log(f"ltx load {time.time() - t:.0f}s")
    for k, f in img_path.items():
        t = time.time()
        im = Image.open(f).convert("RGB").resize((480, 832))
        fr = lp(image=im, prompt=f"{MOTION[k]}, {STYLE}", negative_prompt=NEG, width=480, height=832, num_frames=97,
                num_inference_steps=40, generator=torch.Generator("cpu").manual_seed(0)).frames[0]
        export_to_video(fr, f"{OUT}/ltx_{k}.mp4", fps=24)
        log(f"ltx {k}: {time.time() - t:.0f}s for 97 frames")
    del lp; torch.cuda.empty_cache()
except Exception:
    log("LTX FAILED", traceback.format_exc()[-1500:])

# --- Wan 2.2 TI2V-5B ---
try:
    from diffusers import WanImageToVideoPipeline
    t = time.time()
    wp = WanImageToVideoPipeline.from_pretrained("Wan-AI/Wan2.2-TI2V-5B-Diffusers", torch_dtype=torch.float16)
    wp.enable_model_cpu_offload()
    log(f"wan load {time.time() - t:.0f}s")
    for k, f in list(img_path.items())[:1]:
        t = time.time()
        im = Image.open(f).convert("RGB").resize((480, 832))
        fr = wp(image=im, prompt=f"{MOTION[k]}, {STYLE}", negative_prompt=NEG, width=480, height=832, num_frames=49,
                num_inference_steps=30, guidance_scale=5.0).frames[0]
        export_to_video(fr, f"{OUT}/wan_{k}.mp4", fps=24)
        log(f"wan {k}: {time.time() - t:.0f}s for 49 frames")
except Exception:
    log("WAN FAILED", traceback.format_exc()[-1500:])
log(f"total {time.time() - t0:.0f}s")
