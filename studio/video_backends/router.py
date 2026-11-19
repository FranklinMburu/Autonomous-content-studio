"""The router: try each backend in order; on error, timeout, used-up allowance or a failed check, move to the next.

    from studio.video_backends import Shot, make_shot
    r = make_shot(Shot(prompt="macro shot of a computer chip", image="still.png", seconds=4), "out/")
    r.path, r.backend, r.tried

Every shot is cached by its content (same shot = same clip, never generated twice) and logged (which backend made
it, what the others did). A backend that keeps failing is benched for a while; a paid one is never used unless
config.json says so. Timeouts: each attempt runs in a worker thread; a stuck GPU job is abandoned and the next
backend is tried (the process should then be restarted before that backend is used again).
"""
import concurrent.futures as cf, json, os, shutil, time
from pathlib import Path

from .base import BackendError, NotAvailable, QuotaExceeded
from .checks import basic_check
from .job import Result

HERE = Path(__file__).parent


def registry():
    from .diffusion import LTX, Wan22
    from .own import Own
    from .paid import Higgsfield, Kling, Veo
    return {b.name: b for b in (Wan22(), LTX(), Own(), Kling(), Veo(), Higgsfield())}


class Router:
    def __init__(self, config=None, backends=None, extra_check=None, root="."):
        self.cfg = config or json.loads((HERE / "config.json").read_text())
        self.backends = backends or registry()
        self.extra_check = extra_check
        self.root = Path(root)
        self.cache = self.root / self.cfg.get("cache_dir", "cache/video_shots")
        self.logf = self.root / self.cfg.get("log", "cache/video_shots/log.jsonl")
        self.benchf = self.cache / "bench.json"

    # ---- bench: a tool that keeps failing rests for a while ----
    def _bench(self):
        try:
            return json.loads(self.benchf.read_text())
        except (OSError, ValueError):
            return {}

    def _note(self, name, failed):
        b = self._bench()
        e = b.get(name, {"fails": 0, "until": 0})
        e["fails"] = e["fails"] + 1 if failed else 0
        pol = self.cfg.get("bench", {})
        if failed and e["fails"] >= pol.get("after_failures", 3):
            e["until"], e["fails"] = time.time() + pol.get("hours", 6) * 3600, 0
        b[name] = e
        self.cache.mkdir(parents=True, exist_ok=True)
        self.benchf.write_text(json.dumps(b))

    def _benched(self, name):
        return self._bench().get(name, {}).get("until", 0) > time.time()

    def _allowed(self, name):
        c = self.cfg["backends"].get(name, {})
        if not c.get("enabled"):
            return "switched off"
        be = self.backends.get(name)
        if be is None:
            return "no plug"
        if not be.free and not self.cfg.get("paid_ok"):
            return "costs money (paid_ok is false)"
        if self._benched(name):
            return "benched after repeated failures"
        return None

    def _log(self, row):
        self.logf.parent.mkdir(parents=True, exist_ok=True)
        with self.logf.open("a") as f:
            f.write(json.dumps(row) + "\n")

    def make(self, shot, out_dir, only=None):
        out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        key = shot.key()
        cached = self.cache / f"{key}.mp4"
        dest = out_dir / f"shot_{key}.mp4"
        if cached.exists() and not only:
            shutil.copy(cached, dest)
            meta = json.loads((self.cache / f"{key}.json").read_text()) if (self.cache / f"{key}.json").exists() else {}
            r = Result(str(dest), meta.get("backend", "?"), 0.0, cached=True, tried=[(meta.get("backend", "?"), "cache")])
            self._log({"key": key, "tags": shot.tags, "backend": r.backend, "cached": True, "t": time.time()})
            return r
        tried, t_all = [], time.time()
        for name in (only or self.cfg["order"]):
            why = self._allowed(name)
            if why:
                tried.append((name, f"skipped: {why}")); continue
            be = self.backends[name]
            if shot.image is None and not be.can_text_to_video:
                tried.append((name, "skipped: needs a picture")); continue
            tmp = out_dir / f".{key}.{name}.mp4"
            t = time.time()
            try:
                be.available()
                ex = cf.ThreadPoolExecutor(max_workers=1)
                fut = ex.submit(be.generate, shot, str(tmp))
                try:
                    fut.result(timeout=self.cfg["backends"][name].get("timeout_s", 900))
                finally:
                    ex.shutdown(wait=False, cancel_futures=True)
                ok, why = basic_check(str(tmp), shot)
                if ok and self.extra_check:
                    ok, why = self.extra_check(str(tmp), shot)
                if not ok:
                    raise BackendError(f"failed the quality check: {why}")
            except NotAvailable as e:
                tried.append((name, f"not available: {e}")); continue
            except QuotaExceeded as e:
                tried.append((name, f"allowance used up: {e}")); self._note(name, True); continue
            except cf.TimeoutError:
                tried.append((name, f"timed out after {time.time() - t:.0f}s")); self._note(name, True); continue
            except Exception as e:  # noqa: BLE001  (any crash in a plug must never stop the video)
                tried.append((name, f"failed: {str(e)[:300]}")); self._note(name, True)
                tmp.unlink(missing_ok=True); continue
            self._note(name, False)
            tmp.replace(dest)
            took = time.time() - t
            tried.append((name, f"made in {took:.0f}s; check {why}"))
            if not only:
                self.cache.mkdir(parents=True, exist_ok=True)
                shutil.copy(dest, cached)
                (self.cache / f"{key}.json").write_text(json.dumps({"backend": name, "tried": tried}))
            r = Result(str(dest), name, took, tried=tried)
            self._log({"key": key, "tags": shot.tags, "backend": name, "took_s": round(took, 1), "tried": tried, "t": time.time()})
            return r
        self._log({"key": key, "tags": shot.tags, "backend": None, "tried": tried, "t": time.time()})
        raise BackendError(f"no backend could make the shot after {time.time() - t_all:.0f}s: {tried}")


def make_shot(shot, out_dir, **kw):
    return Router(**kw).make(shot, out_dir)
