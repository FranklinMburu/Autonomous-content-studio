"""Visual test 4: consistent characters painted inside full scenes, animated ~2 s.

Fixes from test 3: the face-only IP-Adapter (so the scene isn't replaced by the reference's plain background),
the fp16-safe SDXL VAE (MIT) + tiled decoding (no out-of-memory), memory freed between images.
Hero (Semmelweis) and Mother each get a reference portrait; every shot uses the right one.
"""
import gc, os, subprocess, sys, time, traceback
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate",
                "sentencepiece", "imageio[ffmpeg]"], check=False)
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from diffusers import StableDiffusionXLPipeline, AutoencoderKL  # noqa: E402
from transformers import CLIPVisionModelWithProjection  # noqa: E402
log(f"install {time.time() - t0:.0f}s")

STYLE = ("3D animated movie still, Pixar-like stylized characters, soft global illumination, cinematic lighting, "
         "volumetric light, rich colors, shallow depth of field, highly detailed, 1840s, oil lamps and candles only")
NEG = ("photo, realistic, ugly, deformed, extra limbs, extra fingers, bad hands, text, letters, watermark, blurry, "
       "modern, electric light, plain background, studio backdrop")
HERO = "a 19th century doctor with black slicked hair, a black mustache and a long dark green coat with gold buttons"
MOTHER = "a young mother with brown hair in a bun and a long dark red 19th century dress"

vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, image_encoder=enc,
                                                 torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
pipe.enable_vae_tiling()


def gen(prompt, seed, w=768, h=1344, **kw):
    im = pipe(prompt=f"{prompt}, {STYLE}", negative_prompt=NEG, width=w, height=h, num_inference_steps=30,
              guidance_scale=6.0, generator=torch.Generator("cuda").manual_seed(seed), **kw).images[0]
    gc.collect(); torch.cuda.empty_cache()
    return im


# 1. reference portraits (no adapter yet)
refs = {}
for name, look, seed in (("hero", HERO, 3), ("mother", MOTHER, 4)):
    t = time.time()
    im = gen(f"close-up portrait of {look}, friendly face, front view, soft light, simple warm background", seed, 1024, 1024)
    im.save(f"{OUT}/ref_{name}.png"); refs[name] = im
    log(f"ref {name} {time.time() - t:.0f}s")

pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus-face_sdxl_vit-h.safetensors")
log("face adapter loaded")
SHOTS = [
    ("scrub", "hero", f"{HERO} scrubbing his hands with soap foam at a white porcelain washbasin on a wooden stand inside a long 1847 hospital ward with iron beds, evening candle light, medium shot"),
    ("begging", "mother", f"{MOTHER} kneeling and begging with raised hands on the stone steps in front of a grand old hospital gate at dusk, warm gas lamps, low angle"),
    ("ward", "mother", f"{MOTHER} lying sick and pale in an old iron hospital bed in a long 1847 maternity ward with many beds, gloomy dusk light through tall arched windows"),
    ("died", "hero", f"{HERO} lying sick and pale in an iron bed in a bare stone asylum room at night, moonlight through a barred window, sad, high angle"),
]
made = []
for k, who, p in SHOTS:
    for scale in (0.5, 0.7):
        try:
            t = time.time()
            pipe.set_ip_adapter_scale(scale)
            im = gen(p, 5, ip_adapter_image=refs[who])
            f = f"{OUT}/shot_{k}_s{scale}.png"; im.save(f); made.append((k, f))
            log(f"shot {k} scale {scale}: {time.time() - t:.0f}s")
        except Exception:
            log(f"shot {k} FAILED", traceback.format_exc()[-600:]); gc.collect(); torch.cuda.empty_cache()
del pipe; gc.collect(); torch.cuda.empty_cache()

try:
    from diffusers import LTXImageToVideoPipeline
    from diffusers.utils import export_to_video
    lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
    lp.enable_model_cpu_offload()
    MOTION = {"scrub": "he scrubs his hands quickly in the basin, soap foam, candle flames flicker, camera slowly pushes in",
              "begging": "she pleads with her raised hands, her dress moves, lamps flicker, camera slowly tilts up",
              "ward": "she breathes weakly and turns her head, curtains move, camera slowly glides sideways",
              "died": "he breathes weakly and closes his eyes, moonlight flickers, camera slowly moves down"}
    done = set()
    for k, f in made:
        if k in done or "_s0.5" not in f:
            continue
        t = time.time()
        fr = lp(image=Image.open(f).convert("RGB").resize((480, 832)), prompt=f"{MOTION[k]}, {STYLE}", negative_prompt=NEG,
                width=480, height=832, num_frames=49, num_inference_steps=40, generator=torch.Generator("cpu").manual_seed(0)).frames[0]
        export_to_video(fr, f"{OUT}/clip_{k}.mp4", fps=24); done.add(k)
        log(f"clip {k}: {time.time() - t:.0f}s")
except Exception:
    log("LTX FAILED", traceback.format_exc()[-1200:])
log(f"total {time.time() - t0:.0f}s")
