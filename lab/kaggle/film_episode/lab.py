"""Make every shot of a film-style episode (film.json, see studio/story/film.py) on a free Kaggle T4 x2.

GPU 0: SDXL + face IP-Adapter paints each shot with the cast kept consistent (a reference portrait per role), then
Depth-Anything makes its depth map. GPU 1, at the same time: LTX-Video turns each finished "clip" shot into ~1.4 s of
motion. Output: out/ref_<role>.png, shot_<name>.png, depth_<name>.png, clip_<name>.mp4, log.txt.
"""
import gc, json, os, queue, subprocess, sys, threading, time, traceback
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")
FILM = json.loads(FILES["film.json"])  # noqa: F821  (injected by lab/kaggle/run.py)

# settings chosen from visual tests 4-5
IP_SCALE = 0.6          # face lock strength, applied only AFTER the composition is set (see LOCK_FROM)
LOCK_FROM = 0.4         # first 40% of steps: no face lock, so the pose/action comes from the prompt (test 5: a lock
                        # from step 0 made kneeling/lying people stand, and gave every face in a crowd the hero's face)
IMG_W, IMG_H = 832, 1216
CLIP_W, CLIP_H, CLIP_FRAMES, CLIP_STEPS = 512, 896, 41, 30   # test 5: 33 frames barely moved; 49 melted (test 4)
DISTILLED = False       # test 5: the 8-step distilled LTX dissolved into noise with these settings


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate",
                "sentencepiece", "imageio[ffmpeg]"], check=False)
import torch  # noqa: E402
from PIL import Image  # noqa: E402
log(f"install {time.time() - t0:.0f}s; gpus {torch.cuda.device_count()}")
TWO = torch.cuda.device_count() > 1

STYLE = ("single scene, one continuous image, 3D animated movie still, Pixar-like stylized characters, soft global "
         "illumination, cinematic lighting, rich colors, highly detailed, 1840s, oil lamps and candles only")
NEG = ("collage, multiple panels, split screen, grid, comic panels, border, frame, multiple views, duplicate, inset, "
       "photo, realistic, ugly, deformed, extra limbs, extra fingers, bad hands, text, letters, watermark, blurry, "
       "modern, electric light, plain background")
CAST = FILM["cast"]


def fill(p):
    for k, v in CAST.items():
        p = p.replace("{" + k + "}", v)
    return p


# ---------- GPU 1: clips (a worker that waits for finished pictures) ----------
jobs, clip_times = queue.Queue(), []


def clip_worker():
    try:
        from diffusers import LTXImageToVideoPipeline
        from diffusers.utils import export_to_video
        t = time.time()
        lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
        if DISTILLED:
            from diffusers import LTXVideoTransformer3DModel
            tr = LTXVideoTransformer3DModel.from_single_file(
                "https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-2b-0.9.6-distilled-04-25.safetensors",
                torch_dtype=torch.float16)
            lp = LTXImageToVideoPipeline(**{**lp.components, "transformer": tr})
        lp.enable_model_cpu_offload(gpu_id=1 if TWO else 0)
        log(f"ltx load {time.time() - t:.0f}s (gpu {1 if TWO else 0})")
    except Exception:
        log("LTX LOAD FAILED", traceback.format_exc()[-900:]); return
    while True:
        item = jobs.get()
        if item is None:
            return
        name, path, motion = item
        try:
            t = time.time()
            kw = dict(num_inference_steps=8, guidance_scale=1.0) if DISTILLED else \
                dict(num_inference_steps=CLIP_STEPS, negative_prompt=NEG)
            fr = lp(image=Image.open(path).convert("RGB").resize((CLIP_W, CLIP_H)), prompt=f"{motion}, {STYLE}",
                    width=CLIP_W, height=CLIP_H, num_frames=CLIP_FRAMES, decode_timestep=0.05, decode_noise_scale=0.025,
                    generator=torch.Generator("cpu").manual_seed(0), **kw).frames[0]
            export_to_video(fr, f"{OUT}/clip_{name}.mp4", fps=24)
            clip_times.append(time.time() - t)
            log(f"clip {name}: {time.time() - t:.0f}s")
        except Exception:
            log(f"clip {name} FAILED", traceback.format_exc()[-600:])
        gc.collect(); torch.cuda.empty_cache()


worker = threading.Thread(target=clip_worker, daemon=True)
if TWO:
    worker.start()   # loads LTX while SDXL paints

# ---------- GPU 0: pictures + depth ----------
from diffusers import StableDiffusionXLPipeline, AutoencoderKL  # noqa: E402
from transformers import CLIPVisionModelWithProjection, pipeline  # noqa: E402
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, image_encoder=enc,
                                                 torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda:0")
pipe.vae.enable_tiling()
depth = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=0)


def gen(prompt, seed, w=IMG_W, h=IMG_H, **kw):
    im = pipe(prompt=f"{prompt}, {STYLE}", negative_prompt=NEG, width=w, height=h, num_inference_steps=30,
              guidance_scale=6.5, generator=torch.Generator("cuda:0").manual_seed(seed), **kw).images[0]
    gc.collect(); torch.cuda.empty_cache()
    return im


def to916(im):
    w, h = im.size; nw = int(h * 9 / 16)
    return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))


refs = {}
for i, (role, look) in enumerate(CAST.items()):
    t = time.time()
    refs[role] = gen(f"close-up portrait of {look}, friendly face, front view, soft light, simple warm background", 3 + i, 1024, 1024)
    refs[role].save(f"{OUT}/ref_{role}.png")
    log(f"ref {role}: {time.time() - t:.0f}s")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus-face_sdxl_vit-h.safetensors")
blank = Image.new("RGB", (224, 224), (128, 128, 128))
img_times = []
for i, s in enumerate(FILM["shots"]):
    n = s["name"]
    try:
        t = time.time()
        who = s.get("who")
        scale = float(s.get("ip", IP_SCALE)) if who else 0.0
        pipe.set_ip_adapter_scale(0.0)
        start = int(30 * LOCK_FROM)

        def late_lock(p_, step, ts, kw, scale=scale, start=start):
            if step == start and scale:
                p_.set_ip_adapter_scale(scale)
            return kw
        im = to916(gen(fill(s["prompt"]), int(s.get("seed", 7)), ip_adapter_image=refs.get(who, blank),
                       callback_on_step_end=late_lock))
        p = f"{OUT}/shot_{n}.png"; im.save(p)
        depth(im)["depth"].save(f"{OUT}/depth_{n}.png")
        img_times.append(time.time() - t)
        log(f"shot {n}: {time.time() - t:.0f}s")
        if s.get("clip"):
            jobs.put((n, p, fill(s.get("motion", "slow camera push in"))))
    except Exception:
        log(f"shot {n} FAILED", traceback.format_exc()[-600:]); gc.collect(); torch.cuda.empty_cache()
log(f"pictures done at {time.time() - t0:.0f}s")
if not TWO:      # one GPU: free it, then make the clips
    del pipe, depth; gc.collect(); torch.cuda.empty_cache()
    worker.start()
jobs.put(None); worker.join()
log(f"per picture {sum(img_times) / max(1, len(img_times)):.0f}s x {len(img_times)}; "
    f"per clip {sum(clip_times) / max(1, len(clip_times)):.0f}s x {len(clip_times)}")
log(f"total {time.time() - t0:.0f}s")
