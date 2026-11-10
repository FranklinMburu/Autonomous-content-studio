"""Push lab folders to Kaggle as private GPU scripts, wait for them, download their outputs.

    python lab/kaggle/run.py <lab-name>[,<lab-name>...] [--wait-min 180]

Needs KAGGLE_USERNAME and KAGGLE_API_TOKEN in the environment (GitHub secrets). Prints nothing secret.
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

fetch_only = sys.argv[1].startswith("fetch:")
names = [n for n in sys.argv[1].replace("fetch:", "").split(",") if n]
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
    # an optional suffix gives each production run its own private Kaggle script (two episodes never collide)
    slug = (f"studio-lab-{name}" + os.environ.get("KAGGLE_SLUG_SUFFIX", "")).replace("_", "-")[:50]
    data = {f.name: f.read_text(encoding="utf-8") for f in src.glob("*.json")}
    if data:  # a Kaggle script is a single file: carry the lab's data files inside it
        code = (work / "lab.py").read_text(encoding="utf-8")
        (work / "lab.py").write_text(f"FILES = {json.dumps(data)}\n" + code, encoding="utf-8")
    (work / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{user}/{slug}", "title": slug, "code_file": "lab.py", "language": "python", "kernel_type": "script",
        "is_private": True, "enable_gpu": True, "enable_internet": True, "dataset_sources": [],
        "competition_sources": [], "kernel_sources": []}, indent=1))
    if not fetch_only:
        print(name, "->", run("kernels", "push", "-p", str(work), "--accelerator", "NvidiaTeslaT4"), flush=True)
    slugs[name] = slug

t0, done = time.time(), ({n: "fetch only" for n in names} if fetch_only else {})
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
# one flat folder with unique names, ready to publish (lab name + original file name)
flat = Path("lab_publish"); flat.mkdir(exist_ok=True)
for name in slugs:
    root = Path("lab_out") / name
    # a lab that writes an out/ folder publishes only that (earth_film's Blender install is full of .txt/.json files)
    outs = [p for p in root.rglob("out") if p.is_dir()]
    for f in (outs[0] if outs else root).rglob("*"):
        if f.is_file() and f.suffix in (".mp4", ".webm", ".png", ".jpg", ".txt", ".wav", ".log", ".json") and f.parent.name != "jobs":
            dest = flat / f"{name}__{f.name}"
            if dest.exists():   # two files with the same name: keep both (GitHub refuses duplicate asset names)
                dest = flat / f"{name}__{f.parent.name}__{f.name}"
            if not dest.exists():
                shutil.copy(f, dest)
print("FINAL:", done)
# a script that crashed still "completes" on Kaggle: fail the run (after publishing, so the logs stay readable)
# (every lab ends by logging "total <seconds>s"; no such line = it died part-way)
crashed = [n for n in slugs if not any(ln.startswith("total ") for f in (Path("lab_out") / n).rglob("log.txt")
                                       for ln in f.read_text(errors="ignore").splitlines())]
if crashed:
    Path("lab_publish/CRASHED.txt").write_text("crashed: " + ", ".join(crashed) + "\n")
    print("CRASHED:", crashed)
