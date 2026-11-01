"""Push a lab folder to Kaggle as a private GPU script, wait for it, download its output.

    python lab/kaggle/run.py <lab-name> [--wait-min 180]

Needs KAGGLE_USERNAME and KAGGLE_API_TOKEN in the environment (GitHub secrets). Prints nothing secret.
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path

name = sys.argv[1]
wait_min = int(sys.argv[sys.argv.index("--wait-min") + 1]) if "--wait-min" in sys.argv else 180
user = os.environ["KAGGLE_USERNAME"]
src = Path(__file__).parent / name
work = Path("lab_push") / name
shutil.rmtree(work, ignore_errors=True); shutil.copytree(src, work)
slug = f"studio-lab-{name}".replace("_", "-")
(work / "kernel-metadata.json").write_text(json.dumps({
    "id": f"{user}/{slug}", "title": slug, "code_file": "lab.py", "language": "python", "kernel_type": "script",
    "is_private": True, "enable_gpu": True, "enable_internet": True, "dataset_sources": [],
    "competition_sources": [], "kernel_sources": []}, indent=1))


def run(*a):
    r = subprocess.run(["kaggle", *a], capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


print(run("kernels", "push", "-p", str(work)), flush=True)
t0 = time.time()
status = ""
while time.time() - t0 < wait_min * 60:
    time.sleep(60)
    status = run("kernels", "status", f"{user}/{slug}")
    print(f"[{(time.time() - t0) / 60:5.1f} min] {status}", flush=True)
    low = status.lower()
    if "complete" in low or "error" in low or "cancel" in low:
        break
Path("lab_out").mkdir(exist_ok=True)
print(run("kernels", "output", f"{user}/{slug}", "-p", "lab_out"), flush=True)
print("FINAL:", status)
