"""Make every shot of a film-style episode (film.json, see studio/story/film.py) on a free Kaggle T4 x2.

GPU 0: SDXL + face IP-Adapter paints each shot with the cast kept consistent (a reference portrait per role), then
Depth-Anything makes its depth map. GPU 1, at the same time: LTX-Video turns each finished "clip" shot into ~1.4 s of
motion. Output: out/ref_<role>.png, shot_<name>.png, depth_<name>.png, clip_<name>.mp4, log.txt.
"""
import gc, json, os, re, subprocess, sys, time, traceback
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
OUT = "/kaggle/working/out"; os.makedirs(f"{OUT}/jobs", exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")
FILM = json.loads(FILES["film.json"])  # noqa: F821  (injected by lab/kaggle/run.py)

# settings chosen from visual tests 4-5
IP_SCALE = 0.6          # face lock strength, applied only AFTER the composition is set (see LOCK_FROM)
LOCK_FROM = 0.4         # first 40% of steps: no face lock, so the pose/action comes from the prompt (test 5: a lock
                        # from step 0 made kneeling/lying people stand, and gave every face in a crowd the hero's face)
IMG_W, IMG_H = 832, 1216
CLIP_W, CLIP_H, CLIP_FRAMES, CLIP_STEPS = 512, 896, 41, 30   # test 5: 33 frames barely moved; 49 melted (test 4)


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.34", "transformers", "accelerate", "compel",
                "sentencepiece", "imageio[ffmpeg]"], check=False)
NGPU = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.count("GPU ")
TWO = NGPU > 1
os.environ["CUDA_VISIBLE_DEVICES"] = "0"   # this process paints on GPU 0; the clip maker is its own process on GPU 1
import torch  # noqa: E402
from PIL import Image  # noqa: E402
log(f"install {time.time() - t0:.0f}s; gpus {NGPU}")

# The image model reads only the first ~77 tokens of a prompt, so the order matters (lab-run of 003, 1 Nov: long
# free-model prompts pushed the style words past the cut-off and the pictures turned into realistic portraits):
#   1. the style (short), 2. the shot and the ACTION with short labels for people ("a 38 year old surgeon"),
#   3. the era, 4. the full look of the people in the shot (identity is also held by the face lock).
ERA = str(FILM.get("era", "")).strip()
PAST = ERA.lower() not in ("", "today", "now", "modern", "present")
STYLE_SHORT = "3D animated movie still, Pixar-like stylized characters, cinematic lighting"
STYLE = FILM.get("style") or ("single scene, one continuous image, 3D animated movie still, Pixar-like stylized "
                              "characters, soft global illumination, cinematic lighting, rich colors, highly detailed")
NEG_BASE = ("collage, multiple panels, split screen, grid, comic panels, border, frame, multiple views, duplicate, inset, "
            "photo, photograph, realistic, photorealistic, oil painting, portrait painting, ugly, deformed, extra limbs, "
            "extra fingers, bad hands, text, letters, watermark, blurry, plain background, sketch, pencil drawing, line art, "
            "black and white, monochrome, grayscale, cartoon creature, mascot")
NEG_PAST = (", modern, electric light, fluorescent light, modern hospital corridor, modern hospital bed, scrubs, "
            "stethoscope, surgical mask, rubber gloves, cars, phones")
NEG = NEG_BASE + (NEG_PAST if PAST else "")
ONLY = set(FILM.get("only") or [])   # redo just these shots (the rest of the episode is kept)
CAST = FILM["cast"]


def label(desc):
    """'a 38 year old surgeon with neat ...' -> 'a 38 year old surgeon' (short name used inside the action)."""
    head = re.split(r",| with | in a | wearing ", desc, maxsplit=1)[0].strip()
    return " ".join(head.split()[:7])


def fill(p):
    """Full descriptions in place (for the video model, which reads long prompts)."""
    for k, v in CAST.items():
        p = p.replace("{" + k + "}", v)
    return p


def picture_prompt(p, shot=None):
    """Prompt for the image model: style first, then the action with short labels, the era, then the full looks."""
    used = [k for k in CAST if "{" + k + "}" in p]
    for k in used:
        p = p.replace("{" + k + "}", label(CAST[k]))
    looks = "; ".join(f"the {label(CAST[k]).removeprefix('a ').removeprefix('an ')} is {CAST[k]}" for k in used)
    era = f"{ERA}, " if ERA and not (shot or {}).get("modern") else ""
    return f"{STYLE_SHORT}, {era}{p}" + (f", {looks}" if looks else "")


# ---------- GPU 1: the clip maker, a SEPARATE process (test: two GPUs driven from one process crashed CUDA) ----------
# It waits for job files (out/jobs/<name>.json) written as pictures finish, and stops after out/jobs/DONE.
CLIPPER = r"""
import gc, json, os, sys, time, traceback
import torch
from PIL import Image
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video
OUT, W, H, N, STEPS, STYLE, NEG = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], sys.argv[7]
LOG = open(f"{OUT}/log.txt", "a")
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
t = time.time()
lp = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.float16)
lp.enable_model_cpu_offload()
log(f"ltx load {time.time() - t:.0f}s")
done, times = set(), []
while True:
    jobs = sorted((f for f in os.listdir(f"{OUT}/jobs") if f.endswith(".json") and f not in done),
                  key=lambda f: os.path.getmtime(f"{OUT}/jobs/{f}"))
    if not jobs:
        if os.path.exists(f"{OUT}/jobs/DONE"):
            break
        time.sleep(3); continue
    f = jobs[0]; done.add(f)
    j = json.load(open(f"{OUT}/jobs/{f}"))
    try:
        t = time.time()
        fr = lp(image=Image.open(j["path"]).convert("RGB").resize((W, H)), prompt=f"{j['motion']}, {STYLE}", negative_prompt=NEG,
                width=W, height=H, num_frames=N, num_inference_steps=STEPS, decode_timestep=0.05, decode_noise_scale=0.025,
                generator=torch.Generator("cpu").manual_seed(0)).frames[0]
        export_to_video(fr, f"{OUT}/clip_{j['name']}.mp4", fps=24)
        times.append(time.time() - t); log(f"clip {j['name']}: {time.time() - t:.0f}s")
    except Exception:
        log(f"clip {j['name']} FAILED", traceback.format_exc()[-600:])
    gc.collect(); torch.cuda.empty_cache()
json.dump(times, open(f"{OUT}/clip_times.json", "w"))
"""
open("/kaggle/working/clipper.py", "w").write(CLIPPER)
clip_args = [sys.executable, "/kaggle/working/clipper.py", OUT, str(CLIP_W), str(CLIP_H), str(CLIP_FRAMES), str(CLIP_STEPS), STYLE, NEG]
clipper = None
if TWO:   # starts now: loads LTX on GPU 1 while GPU 0 paints
    clipper = subprocess.Popen(clip_args, env={**os.environ, "CUDA_VISIBLE_DEVICES": "1"})


# ---------- GPU 0: pictures + depth ----------
from diffusers import StableDiffusionXLPipeline, AutoencoderKL  # noqa: E402
from transformers import CLIPVisionModelWithProjection, pipeline  # noqa: E402
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
enc = CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter", subfolder="models/image_encoder", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, image_encoder=enc,
                                                 torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
pipe.vae.enable_tiling()
depth = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=0)


COMPEL = None
try:   # long prompts: the whole description is read, not just the first 77 tokens (compel, MIT)
    from compel import Compel, ReturnedEmbeddingsType
    COMPEL = Compel(tokenizer=[pipe.tokenizer, pipe.tokenizer_2], text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
                    returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
                    requires_pooled=[False, True], truncate_long_prompts=False)
    log("long prompts: on (compel)")
except Exception:
    log("long prompts: off (compel failed to load)", traceback.format_exc()[-300:])


def gen(prompt, seed, w=IMG_W, h=IMG_H, neg=None, **kw):
    full, negp = f"{prompt}, {STYLE}", neg or NEG
    args = dict(width=w, height=h, num_inference_steps=30, guidance_scale=6.5,
                generator=torch.Generator("cuda").manual_seed(seed), **kw)
    if COMPEL is not None:
        try:
            c, pooled = COMPEL(full)
            nc, npooled = COMPEL(negp)
            if c.shape[1] != nc.shape[1]:   # pad the shorter one with "empty prompt" chunks (compel's own pad fails on SDXL)
                empty, _ = COMPEL("")
                while c.shape[1] < nc.shape[1]:
                    c = torch.cat([c, empty], dim=1)
                while nc.shape[1] < c.shape[1]:
                    nc = torch.cat([nc, empty], dim=1)
            im = pipe(prompt_embeds=c, pooled_prompt_embeds=pooled, negative_prompt_embeds=nc,
                      negative_pooled_prompt_embeds=npooled, **args).images[0]
            gc.collect(); torch.cuda.empty_cache()
            return im
        except Exception:
            log("compel failed for one prompt; using the short form", traceback.format_exc()[-300:])
    im = pipe(prompt=prompt, prompt_2=full, negative_prompt=negp, **args).images[0]
    gc.collect(); torch.cuda.empty_cache()
    return im


def to916(im):
    w, h = im.size; nw = int(h * 9 / 16)
    return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))


refs = {}
for i, (role, look) in enumerate(CAST.items()):
    t = time.time()
    refs[role] = gen(f"{STYLE_SHORT}, close-up of the face of {look}, friendly face, front view, soft light, simple warm background", 3 + i, 1024, 1024)
    refs[role].save(f"{OUT}/ref_{role}.png")
    log(f"ref {role}: {time.time() - t:.0f}s")
pipe.load_ip_adapter("h94/IP-Adapter", subfolder="sdxl_models", weight_name="ip-adapter-plus-face_sdxl_vit-h.safetensors")
blank = Image.new("RGB", (224, 224), (128, 128, 128))
img_times = []
SHOTS = [s for s in FILM["shots"] if not ONLY or s["name"] in ONLY]


def paint(s, attempt=0):
    """Paint one shot (attempt 0 = its own seed; retries use new seeds; the last retry drops the face lock, which
    can fight the pose). Saves shot + depth and queues its clip. Returns the picture."""
    n, who = s["name"], s.get("who")
    t = time.time()
    scale = (float(s.get("ip", IP_SCALE)) if who else 0.0) if attempt < 2 else 0.0
    pipe.set_ip_adapter_scale(0.0)
    start = int(30 * LOCK_FROM)

    def late_lock(p_, step, ts, kw, scale=scale, start=start):
        if step == start and scale:
            p_.set_ip_adapter_scale(scale)
        return kw
    im = to916(gen(picture_prompt(s["prompt"], s), int(s.get("seed", 7)) + 1000 * attempt,
                   neg=NEG_BASE if s.get("modern") else NEG, ip_adapter_image=refs.get(who, blank),
                   callback_on_step_end=late_lock))
    p = f"{OUT}/shot_{n}.png"; im.save(p); im.save(f"/kaggle/working/try{attempt}_{n}.png")
    depth(im)["depth"].save(f"{OUT}/depth_{n}.png")
    img_times.append(time.time() - t)
    log(f"shot {n}{f' (retry {attempt})' if attempt else ''}: {time.time() - t:.0f}s")
    if s.get("clip"):   # a repaint queues a new clip job; the clip maker works in order, so the last one wins
        tmp = f"{OUT}/jobs/{n}__{attempt}.tmp"
        json.dump({"name": n, "path": p, "motion": fill(s.get("motion", "slow camera push in"))}, open(tmp, "w"))
        os.replace(tmp, tmp[:-4] + ".json")   # the clip maker never sees half a file
    return im


pictures = {}
for s in SHOTS:
    try:
        pictures[s["name"]] = paint(s)
    except Exception:
        log(f"shot {s['name']} FAILED", traceback.format_exc()[-600:]); gc.collect(); torch.cuda.empty_cache()

# ---------- guardrail: a vision model checks every picture; failures are repainted (up to 2 more tries) ----------
# Episode 002 showed what slips through otherwise: a woman standing where she should kneel, a modern hospital
# corridor in 1847. Each shot's "check" question must be answered yes; text, panels and (for past eras) modern
# things must be answered no.
CHECKS, failed = {}, []
try:
    from transformers import AutoProcessor, AutoModelForImageTextToText
    VLM_ID = "Qwen/Qwen2-VL-2B-Instruct"   # Apache-2.0
    gc.collect(); torch.cuda.empty_cache()   # SDXL stays on the GPU (idle); the checker fits beside it in fp16
    t = time.time()
    proc = AutoProcessor.from_pretrained(VLM_ID, min_pixels=256 * 28 * 28, max_pixels=768 * 28 * 28)
    vlm = AutoModelForImageTextToText.from_pretrained(VLM_ID, torch_dtype=torch.float16).to("cuda").eval()
    log(f"checker load {time.time() - t:.0f}s")
    
    def ask(img, q):
        msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": q + " Answer yes or no."}]}]
        text = proc.apply_chat_template(msgs, add_generation_prompt=True)
        inp = proc(text=[text], images=[img], return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = vlm.generate(**inp, max_new_tokens=3, do_sample=False)
        return proc.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip().lower()

    def problems(s, img):
        a, bad = {}, []
        if s.get("check"):
            a["check"] = ask(img, s["check"])
            if not a["check"].startswith("yes"):
                bad.append(f"no to: {s['check']}")
        a["text"] = ask(img, "Is there any text, letters or writing in this picture?")
        if a["text"].startswith("yes"):
            bad.append("text in the picture")
        # (no "split into panels?" question: calibration showed the 2B model says yes to almost every picture)
        if PAST and not s.get("modern"):
            a["modern"] = ask(img, "Does this picture show anything modern, such as electric lights, fluorescent tubes, "
                                   "a modern hospital corridor, cars or phones?")
            if a["modern"].startswith("yes"):
                bad.append("modern things in a past era")
        return a, bad

    todo = [s for s in SHOTS if s["name"] in pictures]
    tries = {}   # name -> [(problems, attempt)]
    for attempt in range(3):
        retry = []
        for s in todo:
            a, bad = problems(s, pictures[s["name"]])
            tries.setdefault(s["name"], []).append((len(bad), attempt))
            CHECKS[s["name"]] = {"attempt": attempt, "answers": a, "problems": bad}
            if bad:
                retry.append(s); log(f"check {s['name']}: FAIL ({'; '.join(bad)})")
        log(f"check round {attempt + 1}: {len(todo) - len(retry)} of {len(todo)} pass")
        if not retry or attempt == 2:
            failed = [s["name"] for s in retry]
            break
        vlm.to("cpu"); gc.collect(); torch.cuda.empty_cache()     # room for SDXL to paint
        for s in retry:
            pictures[s["name"]] = paint(s, attempt + 1)
        vlm.to("cuda")
        todo = retry
    del vlm; gc.collect(); torch.cuda.empty_cache()
    # still failing after 3 tries: use the try with the fewest problems (the first one on a tie), not the last
    for s in SHOTS:
        n = s["name"]
        if n in tries and len(tries[n]) > 1:
            fewest, best = min(tries[n])
            if best != tries[n][-1][1]:
                im = Image.open(f"/kaggle/working/try{best}_{n}.png"); im.save(f"{OUT}/shot_{n}.png")
                depth(im)["depth"].save(f"{OUT}/depth_{n}.png")
                CHECKS[n]["kept_try"] = best
                log(f"shot {n}: kept try {best} ({fewest} problem(s))")
                if s.get("clip"):
                    tmp = f"{OUT}/jobs/{n}__best.tmp"
                    json.dump({"name": n, "path": f"{OUT}/shot_{n}.png", "motion": fill(s.get("motion", "slow camera push in"))}, open(tmp, "w"))
                    os.replace(tmp, tmp[:-4] + ".json")
except Exception:
    log("CHECKER FAILED (pictures kept unchecked)", traceback.format_exc()[-900:])
    failed = ["(checker did not run)"]
json.dump({"failed": failed, "shots": CHECKS}, open(f"{OUT}/checks.json", "w"), indent=1)
log(f"checks: {len(failed)} shot(s) still failing after retries: {failed}")
log(f"pictures done at {time.time() - t0:.0f}s")
open(f"{OUT}/jobs/DONE", "w").close()
if not TWO:      # one GPU: free it, then make the clips
    del pipe, depth; gc.collect(); torch.cuda.empty_cache()
    clipper = subprocess.Popen(clip_args, env={**os.environ, "CUDA_VISIBLE_DEVICES": "0"})
clipper.wait()
clip_times = json.load(open(f"{OUT}/clip_times.json")) if os.path.exists(f"{OUT}/clip_times.json") else []
log(f"per picture {sum(img_times) / max(1, len(img_times)):.0f}s x {len(img_times)}; "
    f"per clip {sum(clip_times) / max(1, len(clip_times)):.0f}s x {len(clip_times)}")
log(f"total {time.time() - t0:.0f}s")
