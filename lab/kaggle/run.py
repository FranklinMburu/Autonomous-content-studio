"""Push lab folders to Kaggle as private GPU scripts, wait for them, download their outputs.

    python lab/kaggle/run.py <lab-name>[,<lab-name>...] [--wait-min 180]

Needs KAGGLE_USERNAME and KAGGLE_API_TOKEN in the environment (GitHub secrets). Prints nothing secret.
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

names = [n for n in sys.argv[1].split(",") if n]
wait_min = int(sys.argv[sys.argv.index("--wait-min") + 1]) if "--wait-min" in sys.argv else 180
user = os.environ["KAGGLE_USERNAME"]


def run(*a):
    r = subprocess.run(["kaggle", *a], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if "Traceback" in out:
        sys.exit("kaggle tool failed:\n" + out[-1500:])
    return out


slugs = {}
for name in names:
    src = Path(__file__).parent / name
    work = Path("lab_push") / name
    shutil.rmtree(work, ignore_errors=True); shutil.copytree(src, work)
    slug = f"studio-lab-{name}".replace("_", "-")
    (work / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{user}/{slug}", "title": slug, "code_file": "lab.py", "language": "python", "kernel_type": "script",
        "is_private": True, "enable_gpu": True, "enable_internet": True, "dataset_sources": [],
        "competition_sources": [], "kernel_sources": []}, indent=1))
    print(name, "->", run("kernels", "push", "-p", str(work)), flush=True)
    slugs[name] = slug

t0, done = time.time(), {}
while len(done) < len(slugs) and time.time() - t0 < wait_min * 60:
    time.sleep(60)
    for name, slug in slugs.items():
        if name in done:
            continue
        st = run("kernels", "status", f"{user}/{slug}")
        print(f"[{(time.time() - t0) / 60:5.1f} min] {name}: {st}", flush=True)
        if any(w in st.lower() for w in ("complete", "error", "cancel")):
            done[name] = st
for name, slug in slugs.items():
    d = Path("lab_out") / name; d.mkdir(parents=True, exist_ok=True)
    print(name, "output:", run("kernels", "output", f"{user}/{slug}", "-p", str(d))[-300:], flush=True)
print("FINAL:", done)
