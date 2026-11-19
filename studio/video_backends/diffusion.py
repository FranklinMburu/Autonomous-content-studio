"""Open video models that run on our free Kaggle T4 GPUs (diffusers). Loaded once per process, then reused.

Wan 2.2 TI2V-5B (Apache-2.0): text-to-video and image-to-video in one model; the strongest open model that fits a T4
with CPU offload. LTX-Video 0.9.x distilled (Lightricks, open weights): fast, already used by Hidden Reasons.
"""
import gc, os
from .base import Backend, BackendError, NotAvailable

_PIPES = {}


def _gpu():
    try:
        import torch
    except ImportError:
        raise NotAvailable("torch not installed")
    if not torch.cuda.is_available():
        raise NotAvailable("no GPU here")
    return torch


def _free_other(keep):
    for k in [k for k in _PIPES if k != keep]:
        del _PIPES[k]
    gc.collect()
    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:  # noqa: BLE001
        pass


def _frames(seconds, fps, step):   # these models want 4k+1 (Wan) or 8k+1 (LTX) frames
    n = max(step + 1, round(seconds * fps))
    return (n - 1) // step * step + 1


def _export(frames, out_path, fps):
    from diffusers.utils import export_to_video
    export_to_video(frames, out_path, fps=fps)


class Wan22(Backend):
    name = "wan22"
    needs_gpu = True
    model = os.environ.get("WAN22_MODEL", "Wan-AI/Wan2.2-TI2V-5B-Diffusers")

    def available(self):
        _gpu()

    def _pipe(self):
        torch = _gpu()
        if "wan22" not in _PIPES:
            _free_other("wan22")
            from diffusers import AutoencoderKLWan, WanPipeline
            # T4 has no fast bfloat16: weights in float16, the VAE in float32 (Wan's VAE overflows in float16)
            vae = AutoencoderKLWan.from_pretrained(self.model, subfolder="vae", torch_dtype=torch.float32)
            p = WanPipeline.from_pretrained(self.model, vae=vae, torch_dtype=torch.float16)
            p.enable_model_cpu_offload()
            p.vae.enable_tiling()
            _PIPES["wan22"] = p
        return _PIPES["wan22"]

    def generate(self, shot, out_path):
        torch = _gpu()
        last = None
        for scale in (1.0, 0.8):   # a T4 has 15 GB: try the asked size, then a smaller one, before giving up
            try:
                return self._make(shot, out_path, scale)
            except torch.cuda.OutOfMemoryError as e:
                last = e
                _PIPES.clear(); gc.collect(); torch.cuda.empty_cache()
        raise BackendError(f"out of GPU memory even at 80% size: {str(last)[:200]}")

    def _make(self, shot, out_path, scale):
        torch = _gpu()
        p = self._pipe()
        w, h = (int(shot.width * scale) // 32) * 32, (int(shot.height * scale) // 32) * 32
        kw = dict(prompt=f"{shot.prompt}, {shot.camera}", negative_prompt=shot.negative, width=w, height=h,
                  num_frames=_frames(shot.seconds, shot.fps, 4), num_inference_steps=int(os.environ.get("WAN_STEPS", 30)),
                  guidance_scale=5.0, generator=torch.Generator("cpu").manual_seed(shot.seed))
        if shot.image:
            from PIL import Image
            from diffusers import WanImageToVideoPipeline
            if "wan22_i2v" not in _PIPES:  # same weights, no second download: pass the loaded parts in
                c = p.components
                _PIPES["wan22_i2v"] = WanImageToVideoPipeline.from_pretrained(
                    self.model, **{k: c[k] for k in ("vae", "text_encoder", "tokenizer", "transformer", "scheduler")},
                    torch_dtype=torch.float16)
                _PIPES["wan22_i2v"].enable_model_cpu_offload()
            p = _PIPES["wan22_i2v"]
            kw["image"] = Image.open(shot.image).convert("RGB").resize((w, h))
        frames = p(**kw).frames[0]
        _export(frames, out_path, shot.fps)


class LTX(Backend):
    name = "ltx"
    needs_gpu = True
    base = "Lightricks/LTX-Video"   # the production settings of Hidden Reasons (lab/kaggle/film_episode)

    def available(self):
        _gpu()

    def _pipes(self):
        torch = _gpu()
        if "ltx" not in _PIPES:
            _free_other("ltx")
            from diffusers import LTXImageToVideoPipeline, LTXPipeline
            i2v = LTXImageToVideoPipeline.from_pretrained(self.base, torch_dtype=torch.float16)
            i2v.enable_model_cpu_offload()
            t2v = LTXPipeline(**i2v.components)
            _PIPES["ltx"] = (t2v, i2v)
        return _PIPES["ltx"]

    def generate(self, shot, out_path):
        torch = _gpu()
        t2v, i2v = self._pipes()
        w, h = (shot.width // 32) * 32, (shot.height // 32) * 32
        kw = dict(prompt=f"{shot.prompt}, {shot.camera}", negative_prompt=shot.negative, width=w, height=h,
                  num_frames=_frames(shot.seconds, shot.fps, 8), num_inference_steps=30, guidance_scale=3.0,
                  decode_timestep=0.05, decode_noise_scale=0.025, generator=torch.Generator("cpu").manual_seed(shot.seed))
        if shot.image:
            from PIL import Image
            kw["image"] = Image.open(shot.image).convert("RGB").resize((w, h))
            pipe = i2v
        else:
            pipe = t2v
        try:
            frames = pipe(**kw).frames[0]
        except torch.cuda.OutOfMemoryError as e:
            raise BackendError(f"out of GPU memory at {w}x{h}") from e
        _export(frames, out_path, shot.fps)
