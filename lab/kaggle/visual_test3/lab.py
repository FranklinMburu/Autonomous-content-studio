"""Visual test 3: characters painted INSIDE the scenes (same light, perspective, shadows), kept consistent with a
reference image (IP-Adapter, Apache-2.0), then animated for ~2 s with LTX-Video (where it holds up).

1. Reference sheet for the hero (Semmelweis): our own simple toon design, soft 3D film look.
2. Four story shots with the characters in the scene (SDXL + IP-Adapter on the hero reference).
3. Each shot -> 49-frame clip (2 s at 24 fps) with LTX-Video. Timings in out/log.txt.
"""
import os, subprocess, sys, time, traceback
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate",
                "sentencepiece", "imageio[ffmpeg]"], check=False)
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from diffusers import StableDiffusionXLPipeline  # noqa: E402
log(f"install {time.time() - t0:.0f}s")

LOOK = ("cute stylized toon character with a big perfectly round white head, two small black dot eyes, simple short "
        "eyebrows, small mustache, thin black outline, small simple body, 3D animated movie character, Pixar-like soft render")
STYLE = ("1840s, antique, oil lamps and candles only, 3D animated movie still, stylized, soft global illumination, "
         "cinematic lighting, volumetric light, rich colors, shallow depth of field, highly detailed")
NEG = ("realistic human, photo, realistic face, skin pores, ugly, deformed, extra limbs, extra fingers, text, letters, "
       "watermark, signature, blurry, modern, electric light")

pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16,
                                                 variant="fp16", use_safetensors=True).to("cuda")
# 1. hero reference
t = time.time()
ref = pipe(prompt=f"full body {LOOK}, wearing a long dark green 19th century doctor coat with gold buttons, standing, "
                  f"front view, plain light grey background, studio light",
           negative_prompt=NEG, width=832, height=1216, num_inference_steps=32, guidance_scale=6.5,
           generator=torch.Generator("cuda").manual_seed(3)).images[0]
ref.save(f"{OUT}/ref_hero.png"); log(f"reference {time.time() - t:.0f}s")

SHOTS = {
    "scrub": "the doctor in the green coat scrubbing his hands with soap at an old porcelain washbasin in an 1847 hospital ward at night, candle light, medium shot",
    "begging": "a frightened mother in a long red dress kneeling and begging in front of the doctor in the green coat at the stone steps of an old hospital gate at dusk, low angle",
    "friend": "a student in a brown coat accidentally cutting the hand of a doctor in a white coat with a scalpel at a wooden table in an old anatomy room, morning light",
    "died": "the doctor in the green coat lying sick in an iron bed in a bare asylum room at night, moonlight through a barred window, sad, high angle",
}
try:
    pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter_sdxl.bin")
    log("ip-adapter loaded")
    have_ipa = True
except Exception:
    log("IP-ADAPTER FAILED", traceback.format_exc()[-800:]); have_ipa = False
made = {}
for k, p in SHOTS.items():
    for scale in ((0.45, 0.65) if have_ipa else (None,)):
        try:
            t = time.time()
            kw = {}
            if scale is not None:
                pipe.set_ip_adapter_scale(scale); kw["ip_adapter_image"] = ref
            im = pipe(prompt=f"{p}, {LOOK}, {STYLE}", negative_prompt=NEG, width=768, height=1344, num_inference_steps=32,
                      guidance_scale=6.5, generator=torch.Generator("cuda").manual_seed(5), **kw).images[0]
            f = f"{OUT}/shot_{k}_ipa{scale}.png"; im.save(f); made.setdefault(k, f)
            log(f"shot {k} ipa={scale}: {time.time() - t:.0f}s")
        except Exception:
            log(f"shot {k} FAILED", traceback.format_exc()[-800:])
del pipe; torch.cuda.empty_cache()

# 3. two-second clips
try:
    from diffusers import LTXImageToVideoPipeline
    from diffusers.utils import export_to_video
    t = time.time()
    lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
    lp.enable_model_cpu_offload()
    log(f"ltx load {time.time() - t:.0f}s")
    MOTION = {"scrub": "he scrubs his hands quickly, soap foam, camera slowly pushes in",
              "begging": "she pleads with her hands raised, the doctor looks down, camera slowly tilts up",
              "friend": "the scalpel slips and cuts, the doctor flinches in pain, camera slowly pushes in",
              "died": "he breathes weakly, moonlight flickers, camera slowly moves down"}
    for k, f in made.items():
        t = time.time()
        im = Image.open(f).convert("RGB").resize((480, 832))
        fr = lp(image=im, prompt=f"{MOTION[k]}, {STYLE}", negative_prompt=NEG, width=480, height=832, num_frames=49,
                num_inference_steps=40, generator=torch.Generator("cpu").manual_seed(0)).frames[0]
        export_to_video(fr, f"{OUT}/clip_{k}.mp4", fps=24)
        log(f"clip {k}: {time.time() - t:.0f}s")
except Exception:
    log("LTX FAILED", traceback.format_exc()[-1200:])
log(f"total {time.time() - t0:.0f}s")
