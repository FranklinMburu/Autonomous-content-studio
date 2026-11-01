"""Calibrate the picture checker (a free vision model) on episode 002's painted shots from lab-run14, where we
know the answers: 'begging' shows a STANDING woman (should fail "Is a woman kneeling?"), 'living' is a modern
corridor (should fail the era check), 'dying' is fine but the dress colour is wrong (not checked)."""
import json, os, subprocess, sys, time, urllib.request
OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")
SPEC = json.loads(FILES["shots.json"])  # noqa: F821


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


t0 = time.time()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "transformers", "accelerate", "qwen-vl-utils"], check=False)
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from transformers import AutoProcessor, AutoModelForImageTextToText  # noqa: E402
BASE = "https://github.com/FranklinMburu/Autonomous-content-studio/releases/download/lab-run14/film_episode__shot_{}.png"
MODEL = "Qwen/Qwen2-VL-2B-Instruct"   # Apache-2.0
t = time.time()
proc = AutoProcessor.from_pretrained(MODEL, min_pixels=256 * 28 * 28, max_pixels=768 * 28 * 28)
vlm = AutoModelForImageTextToText.from_pretrained(MODEL, torch_dtype=torch.float16).to("cuda").eval()
log(f"install+load {time.time() - t0:.0f}s")


def ask(img, q):
    msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": q + " Answer yes or no."}]}]
    text = proc.apply_chat_template(msgs, add_generation_prompt=True)
    inp = proc(text=[text], images=[img], return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = vlm.generate(**inp, max_new_tokens=3, do_sample=False)
    return proc.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip().lower()


GENERIC = [("text", "Is there any text, letters or writing in this picture?"),
           ("panels", "Is this picture made of several separate panels or frames?"),
           ("modern", "Does this picture show anything modern, such as electric lights, fluorescent tubes, a modern hospital corridor, cars or phones?")]
rows = []
for s in SPEC["shots"]:
    try:
        fn = f"/kaggle/working/{s['name']}.png"
        urllib.request.urlretrieve(BASE.format(s["name"]), fn)
        img = Image.open(fn).convert("RGB")
        t = time.time()
        a = {"check": ask(img, s["check"])}
        for k, q in GENERIC:
            a[k] = ask(img, q)
        rows.append({"name": s["name"], **a})
        log(f"{s['name']:11s} check={a['check']:4s} text={a['text']:4s} panels={a['panels']:4s} modern={a['modern']:4s} ({time.time() - t:.1f}s)  | {s['check']}")
    except Exception as e:  # noqa: BLE001
        log(f"{s['name']} FAILED {e}")
json.dump(rows, open(f"{OUT}/answers.json", "w"), indent=1)
log(f"total {time.time() - t0:.0f}s")
