"""Visual test 2: backgrounds only (no people) in the benchmark's soft-3D animated-film look, plus a depth map
for each, so the camera can glide through them (parallax) and our own animated cast can stand inside them.

Models (licences allow commercial use): SDXL base 1.0 (OpenRAIL++), FLUX.1-schnell (Apache-2.0),
Depth-Anything-V2-Small (Apache-2.0). Output: out/bg_<model>_<scene>.png, out/depth_<...>.png, out/log.txt.
"""
import os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate",
                "sentencepiece", "protobuf", "bitsandbytes"], check=False)
import torch  # noqa: E402
log("gpus", [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], f"install {time.time() - t0:.0f}s")

STYLE = ("3D animated movie background, stylized Pixar-like render, soft global illumination, warm cinematic lighting, "
         "volumetric light, rich colors, shallow depth of field, highly detailed, empty scene, no people, no characters")
SCENES = {
    "ward": "interior of an old 1847 Vienna hospital maternity ward, rows of iron beds with white sheets, tall arched windows, evening light, candles",
    "street": "cobblestone street of old 19th century Vienna at dusk, warm gas lamps, long shadows, colorful old buildings",
    "lab": "19th century anatomy room, wooden tables, glass bottles on shelves, brass microscope, warm lamp light",
    "room": "cozy 19th century study room, wooden floor, bookshelves, window with blue night light, oil lamp on a desk",
}
NEG = "people, person, man, woman, character, text, watermark, signature, blurry, lowres, deformed"
made = []
try:
    from diffusers import StableDiffusionXLPipeline
    t = time.time()
    pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16,
                                                     variant="fp16", use_safetensors=True).to("cuda")
    for k, p in SCENES.items():
        im = pipe(prompt=f"{p}, {STYLE}", negative_prompt=NEG, width=768, height=1344, num_inference_steps=30,
                  guidance_scale=6.5, generator=torch.Generator("cuda").manual_seed(7)).images[0]
        f = f"{OUT}/bg_sdxl_{k}.png"; im.save(f); made.append(f)
    log(f"sdxl 4 backgrounds {time.time() - t:.0f}s")
    del pipe; torch.cuda.empty_cache()
except Exception:
    log("SDXL FAILED", traceback.format_exc()[-1200:])

try:
    from diffusers import FluxPipeline
    t = time.time()
    fp = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.float16)
    fp.enable_sequential_cpu_offload()
    log(f"flux load {time.time() - t:.0f}s")
    for k, p in SCENES.items():
        t = time.time()
        im = fp(prompt=f"{p}, {STYLE}", width=768, height=1344, num_inference_steps=4, guidance_scale=0.0,
                max_sequence_length=256, generator=torch.Generator("cpu").manual_seed(7)).images[0]
        f = f"{OUT}/bg_flux_{k}.png"; im.save(f); made.append(f)
        log(f"flux {k} {time.time() - t:.0f}s")
    del fp; torch.cuda.empty_cache()
except Exception:
    log("FLUX FAILED", traceback.format_exc()[-1200:])

try:
    from transformers import pipeline
    from PIL import Image
    dp = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=0)
    for f in made:
        d = dp(Image.open(f))["depth"]
        d.save(f.replace("bg_", "depth_"))
    log("depth maps done")
except Exception:
    log("DEPTH FAILED", traceback.format_exc()[-1200:])
log(f"total {time.time() - t0:.0f}s")
