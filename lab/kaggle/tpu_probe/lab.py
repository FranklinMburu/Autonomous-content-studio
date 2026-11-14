"""TPU probe (14 Nov 2026, frontier-intelligence research): what does Franklin's free Kaggle TPU really give, and can it
serve a strong open model fast enough to matter?

Step 1: the machine (TPU type and memory per chip, host RAM, disk, CPUs), and Hugging Face download speed.
Step 2: vLLM's TPU backend with an ungated Apache-2.0 model (Qwen3-32B), tensor-parallel over every chip, on 24 real
        script-writing prompts: load time, compile time, tokens/s for one request and for the whole batch.
Uses TPU hours only (separate from the GPU hours the films use). Output: out/log.txt (+ out/samples.json).
"""
import json, os, shutil, subprocess, sys, time, traceback

OUT = "/kaggle/working/out"; os.makedirs(OUT, exist_ok=True)
LOG = open(f"{OUT}/log.txt", "a")
T0 = time.time()


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


def sh(cmd, timeout=1800):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return (r.stdout + r.stderr).strip()


# ---- step 1: the machine
log("== machine")
for c in ("nproc", "free -g", "df -h /kaggle/working /kaggle/tmp /tmp / 2>/dev/null", "python -V", "pip list 2>/dev/null | grep -i -E 'jax|torch|vllm|libtpu' "):
    log(f"$ {c}\n{sh(c)}")
try:
    import jax
    devs = jax.devices()
    log("jax devices:", len(devs), devs[:2])
    for d in devs[:1]:
        try:
            log("memory_stats:", {k: v for k, v in (d.memory_stats() or {}).items() if "limit" in k or "bytes" in k})
        except Exception as e:  # noqa: BLE001
            log("memory_stats n/a", e)
        log("device_kind:", getattr(d, "device_kind", "?"))
except Exception:
    log("jax import failed", traceback.format_exc()[-600:])

# download speed: one ~4 GB safetensors shard of a big model
try:
    sh(f"{sys.executable} -m pip install -q -U huggingface_hub hf_transfer", 600)
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import hf_hub_download
    t = time.time()
    f = hf_hub_download("Qwen/Qwen3-32B", "model-00001-of-00017.safetensors", cache_dir="/tmp/hfdl")
    sz = os.path.getsize(f) / 1e9
    log(f"download test: {sz:.2f} GB in {time.time() - t:.0f}s = {sz * 1000 / max(1, time.time() - t):.0f} MB/s")
    shutil.rmtree("/tmp/hfdl", ignore_errors=True)
except Exception:
    log("download test failed", traceback.format_exc()[-600:])

# ---- step 2: vLLM on TPU
PROMPTS = [f"Write a 120-word narration for a 40-second YouTube Short answering: {q} Hook in the first line, one surprising "
           f"finding, plain spoken English, a final line that pays off the hook. Narration only." for q in [
    "Why do cats purr?", "Why do dogs tilt their heads?", "Why do fingers wrinkle in water?", "Why do we yawn?",
    "Why is the sky blue?", "Why do onions make you cry?", "Why do we get goosebumps?", "Why do zebras have stripes?",
    "Why do we hiccup?", "Why do leaves change colour?", "Why does ice float?", "Why do we dream?",
    "Why do flamingos stand on one leg?", "Why does the moon look bigger at the horizon?", "Why do we sneeze in sunlight?",
    "Why do octopuses have three hearts?", "Why does popcorn pop?", "Why do bees make hexagons?",
    "Why do we get brain freeze?", "Why do cats knead?", "Why do owls turn their heads so far?", "Why do we blush?",
    "Why does bread go stale?", "Why do birds fly in a V?"]]
try:
    t = time.time()
    out = sh(f"{sys.executable} -m pip install -q vllm-tpu 2>&1 | tail -5", 2400)
    log(f"pip install vllm-tpu ({time.time() - t:.0f}s): {out[-800:]}")
    t = time.time()
    from vllm import LLM, SamplingParams
    import jax
    n = len(jax.devices())
    llm = LLM(model="Qwen/Qwen3-32B", tensor_parallel_size=n, max_model_len=4096, max_num_seqs=32,
              download_dir="/tmp/models")
    log(f"vLLM ready (download + load + compile) in {time.time() - t:.0f}s on {n} chips")
    sp = SamplingParams(temperature=0.8, max_tokens=400)
    chat = lambda p: [{"role": "user", "content": p + " /no_think"}]
    t = time.time(); one = llm.chat(chat(PROMPTS[0]), sp); d1 = time.time() - t
    n1 = len(one[0].outputs[0].token_ids)
    log(f"one request: {n1} tokens in {d1:.1f}s = {n1 / d1:.1f} tok/s (first call may include extra compile)")
    t = time.time(); one = llm.chat(chat(PROMPTS[1]), sp); d1 = time.time() - t
    n1 = len(one[0].outputs[0].token_ids)
    log(f"one request (warm): {n1} tokens in {d1:.1f}s = {n1 / d1:.1f} tok/s")
    t = time.time(); outs = llm.chat([chat(p) for p in PROMPTS], sp); db = time.time() - t
    ntok = sum(len(o.outputs[0].token_ids) for o in outs)
    log(f"batch of {len(PROMPTS)}: {ntok} tokens in {db:.1f}s = {ntok / db:.1f} tok/s aggregate")
    json.dump([{"prompt": p, "text": o.outputs[0].text} for p, o in zip(PROMPTS, outs)], open(f"{OUT}/samples.json", "w"), indent=1)
except Exception:
    log("vLLM step failed", traceback.format_exc()[-2500:])
log(f"total {time.time() - T0:.0f}s")
