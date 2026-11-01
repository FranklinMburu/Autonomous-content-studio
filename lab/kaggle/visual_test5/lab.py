"""Visual test 5: fix what test 4 showed.

Test 4: faces stayed consistent and the scenes looked like a 3D film, but (1) the tall 768x1344 pictures often came out as
2-3 stacked panels (a collage), (2) the action was ignored (begging/sick/dying became standing/sitting), (3) clips melt
after ~1.3 s. Here: 832x1216 (a size SDXL handles well) cropped to 9:16, anti-collage negatives, action first in the
prompt and a weaker face lock (0.35/0.5), 33-frame clips with small motions, and a try of the faster distilled LTX.
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

STYLE = ("single scene, one continuous image, 3D animated movie still, Pixar-like stylized characters, soft global "
         "illumination, cinematic lighting, rich colors, highly detailed, 1840s, oil lamps and candles only")
NEG = ("collage, multiple panels, split screen, grid, comic panels, border, frame, multiple views, duplicate, inset, "
       "photo, realistic, ugly, deformed, extra limbs, extra fingers, bad hands, text, letters, watermark, blurry, "
       "modern, electric light, plain background")
HERO = "a 19th century doctor with black slicked hair, a black mustache and a long dark green coat with gold buttons"
MOTHER = "a young mother with brown hair in a bun and a long dark red 19th century dress"

vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, image_encoder=enc,
                                                 torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
pipe.vae.enable_tiling()


def gen(prompt, seed, w=832, h=1216, **kw):
    im = pipe(prompt=f"{prompt}, {STYLE}", negative_prompt=NEG, width=w, height=h, num_inference_steps=30,
              guidance_scale=6.5, generator=torch.Generator("cuda").manual_seed(seed), **kw).images[0]
    gc.collect(); torch.cuda.empty_cache()
    return im


def to916(im):  # centre crop to 9:16
    w, h = im.size; nw = int(h * 9 / 16)
    return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))


refs = {}
for name, look, seed in (("hero", HERO, 3), ("mother", MOTHER, 4)):
    t = time.time()
    im = gen(f"close-up portrait of {look}, friendly face, front view, soft light, simple warm background", seed, 1024, 1024)
    im.save(f"{OUT}/ref_{name}.png"); refs[name] = im
    log(f"ref {name} {time.time() - t:.0f}s")

pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus-face_sdxl_vit-h.safetensors")
log("face adapter loaded")
SHOTS = [
    ("scrub", "hero", f"medium shot, a man scrubbing his hands hard with white soap foam in a porcelain washbasin, he is {HERO}, inside a long 1847 hospital ward with iron beds, evening candle light"),
    ("begging", "mother", f"full body, a woman on her knees begging with clasped hands raised, she is {MOTHER}, on the stone steps in front of a grand old hospital gate at dusk, warm lamps, low angle"),
    ("ward", "mother", f"a sick pale woman lying flat in an iron hospital bed under a white blanket, head on a pillow, eyes half closed, she is {MOTHER}, long 1847 maternity ward with many beds, gloomy dusk light, tall arched windows"),
    ("died", "hero", f"high angle, a sick pale man lying in an iron bed under a grey blanket, head on a pillow, he is {HERO}, bare stone asylum cell at night, moonlight through a barred window"),
    ("laughed", "hero", f"medium shot, {HERO} looking hurt and embarrassed while three older doctors in black coats laugh at him and point, a grand 1847 lecture hall with wooden benches, warm lamp light"),
]
made = {}
for k, who, p in SHOTS:
    for scale in (0.35, 0.5):
        try:
            t = time.time()
            pipe.set_ip_adapter_scale(scale)
            im = to916(gen(p, 7, ip_adapter_image=refs[who]))
            f = f"{OUT}/shot_{k}_s{scale}.png"; im.save(f); made.setdefault(k, f)
            log(f"shot {k} scale {scale}: {time.time() - t:.0f}s")
        except Exception:
            log(f"shot {k} FAILED", traceback.format_exc()[-600:]); gc.collect(); torch.cuda.empty_cache()
del pipe; gc.collect(); torch.cuda.empty_cache()

MOTION = {"scrub": "his hands rub together in the soap foam, candle flames flicker, slow camera push in",
          "begging": "her clasped hands shake slightly, her lips move, lamps flicker, slow camera push in",
          "ward": "she breathes slowly, her eyes blink, the curtains sway a little, slow camera push in",
          "died": "he breathes slowly and closes his eyes, slow camera push in",
          "laughed": "the doctors laugh and shake, he lowers his eyes, slow camera push in"}
try:
    from diffusers import LTXImageToVideoPipeline
    from diffusers.utils import export_to_video
    t = time.time()
    lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
    lp.enable_model_cpu_offload(); log(f"ltx load {time.time() - t:.0f}s")
    for k, f in made.items():
        t = time.time()
        fr = lp(image=Image.open(f).convert("RGB").resize((512, 896)), prompt=f"{MOTION[k]}, {STYLE}", negative_prompt=NEG,
                width=512, height=896, num_frames=33, num_inference_steps=30, decode_timestep=0.05, decode_noise_scale=0.025,
                generator=torch.Generator("cpu").manual_seed(0)).frames[0]
        export_to_video(fr, f"{OUT}/clip_{k}.mp4", fps=24)
        log(f"clip {k}: {time.time() - t:.0f}s")
    # the faster distilled 2B model (8 steps), on two shots, to compare speed and quality
    try:
        from diffusers import LTXVideoTransformer3DModel
        t = time.time()
        tr = LTXVideoTransformer3DModel.from_single_file(
            "https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-2b-0.9.6-distilled-04-25.safetensors", torch_dtype=torch.float16)
        dp = LTXImageToVideoPipeline(**{**lp.components, "transformer": tr}); dp.enable_model_cpu_offload()
        log(f"distilled load {time.time() - t:.0f}s")
        for k in ("scrub", "ward"):
            t = time.time()
            fr = dp(image=Image.open(made[k]).convert("RGB").resize((512, 896)), prompt=f"{MOTION[k]}, {STYLE}",
                    width=512, height=896, num_frames=33, num_inference_steps=8, guidance_scale=1.0,
                    decode_timestep=0.05, decode_noise_scale=0.025, generator=torch.Generator("cpu").manual_seed(0)).frames[0]
            export_to_video(fr, f"{OUT}/clipd_{k}.mp4", fps=24)
            log(f"distilled clip {k}: {time.time() - t:.0f}s")
    except Exception:
        log("distilled FAILED", traceback.format_exc()[-900:])
except Exception:
    log("LTX FAILED", traceback.format_exc()[-1200:])
log(f"total {time.time() - t0:.0f}s")
