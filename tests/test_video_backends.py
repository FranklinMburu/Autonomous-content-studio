"""The video adapter: fallback order, timeouts, allowances, benching, cache, paid tools off, same check for all.
Run: python tests/test_video_backends.py   (no GPU, no network; the own renderer really runs with ffmpeg)"""
import json, shutil, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.video_backends import Router, Shot  # noqa: E402
from studio.video_backends.base import Backend, BackendError, QuotaExceeded  # noqa: E402
from studio.video_backends.own import Own, ffmpeg  # noqa: E402
from studio.video_backends.paid import Kling  # noqa: E402


def still(d):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (480, 832), (20, 30, 60)); dr = ImageDraw.Draw(im)
    for i in range(0, 480, 40):
        dr.rectangle([i, 300, i + 20, 520], fill=(200, 220, 255))
    p = Path(d) / "still.png"; im.save(p); return str(p)


class Fake(Backend):
    def __init__(self, name, mode="ok", free=True):
        self.name, self.mode, self.free, self.calls = name, mode, free, 0

    def generate(self, shot, out):
        self.calls += 1
        if self.mode == "crash":
            raise RuntimeError("boom")
        if self.mode == "quota":
            raise QuotaExceeded("daily limit")
        if self.mode == "hang":
            time.sleep(5)
        if self.mode == "black":
            import subprocess
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=black:s=480x832:d=2",
                            "-c:v", "libx264", out], check=True)
            return
        Own().generate(shot, out)   # a real, moving clip


def cfg(order, **over):
    c = {"paid_ok": False, "order": order, "bench": {"after_failures": 2, "hours": 1},
         "backends": {n: {"enabled": True, "timeout_s": 1} for n in order}}
    c.update(over); return c


def run(order, fakes, d, **over):
    return Router(config=cfg(order, **over), backends={f.name: f for f in fakes}, root=d)


def test_all():
    d = tempfile.mkdtemp(); img = still(d)
    shot = Shot(prompt="chip macro", image=img, seconds=2)

    # 1. first tool crashes -> second makes it; the log says so
    a, b = Fake("a", "crash"), Fake("b")
    r = run(["a", "b"], [a, b], d).make(shot, Path(d) / "o1")
    assert r.backend == "b" and r.tried[0][1].startswith("failed") and Path(r.path).exists()

    # 2. the same shot again -> cache, nothing generated
    r2 = run(["a", "b"], [a, b], d).make(shot, Path(d) / "o2")
    assert r2.cached and b.calls == 1

    # 3. timeout, used-up allowance and a black clip all move on to the next tool
    s3 = Shot(prompt="other", image=img, seconds=2, seed=3)
    r3 = run(["h", "q", "k", "ok"], [Fake("h", "hang"), Fake("q", "quota"), Fake("k", "black"), Fake("ok")], d).make(s3, Path(d) / "o3")
    outs = [t[1] for t in r3.tried]
    assert r3.backend == "ok" and "timed out" in outs[0] and "allowance" in outs[1] and "quality check" in outs[2], outs

    # 4. a tool that keeps failing is benched (skipped without being called)
    c = Fake("c", "crash")
    for i in range(2):
        run(["c", "ok"], [c, Fake("ok")], d).make(Shot(prompt=f"b{i}", image=img, seconds=2), Path(d) / f"o4{i}")
    calls = c.calls
    r4 = run(["c", "ok"], [c, Fake("ok")], d).make(Shot(prompt="b9", image=img, seconds=2), Path(d) / "o49")
    assert c.calls == calls and "benched" in r4.tried[0][1]

    # 5. paid tools are refused unless paid_ok; the real paid slot is off without a secret
    p = Fake("p", free=False)
    r5 = run(["p", "ok"], [p, Fake("ok")], d).make(Shot(prompt="paid", image=img, seconds=2), Path(d) / "o5")
    assert p.calls == 0 and "costs money" in r5.tried[0][1]
    try:
        Kling().available(); assert False
    except BackendError as e:
        assert "paid" in str(e)

    # 6. the shipped config: free tools first, paid ones off
    real = json.loads((ROOT / "studio/video_backends/config.json").read_text())
    assert real["paid_ok"] is False and real["order"][-1] == "own"
    assert all(not v["enabled"] for v in real["backends"].values() if not v["free"])

    # 7. everything down -> a clear error, never a silent empty video
    try:
        run(["x"], [Fake("x", "crash")], d).make(Shot(prompt="none", image=img, seconds=2), Path(d) / "o7"); assert False
    except BackendError as e:
        assert "no backend" in str(e)

    # 8. text-only shot skips the own renderer (it needs a picture)
    r8 = run(["own2"], [], d)
    r8.backends = {"own2": type("O", (Own,), {"name": "own2"})()}
    try:
        r8.make(Shot(prompt="text only", seconds=2), Path(d) / "o8"); assert False
    except BackendError as e:
        assert "needs a picture" in str(e)
    shutil.rmtree(d)


if __name__ == "__main__":
    test_all(); print("ok")
