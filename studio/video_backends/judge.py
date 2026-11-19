"""A looking judge for clips: a small vision model (Qwen2-VL-2B-Instruct, Apache-2.0, the same family as Hidden
Reasons' picture checker) answers yes/no about frames from the clip. Needed because simple numbers can't tell a real
picture from coloured noise (19 Nov 2026: LTX made pure noise that passed every numeric check).

    Router(extra_check=VisionJudge(subject="a computer chip"))

Runs on the second GPU when there is one (Kaggle T4 x2), otherwise the first, otherwise refuses (no silent pass).
"""
import subprocess, tempfile
from pathlib import Path
from .own import ffmpeg


class VisionJudge:
    model_id = "Qwen/Qwen2-VL-2B-Instruct"

    def __init__(self, subject, frames=(0.15, 0.5, 0.85), need=2):
        self.subject, self.at, self.need, self._m = subject, frames, need, None

    def _load(self):
        import torch
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration
        dev = "cuda:1" if torch.cuda.device_count() > 1 else "cuda:0"
        self.dev = dev
        self._m = Qwen2VLForConditionalGeneration.from_pretrained(self.model_id, torch_dtype=torch.float16).to(dev)
        self._p = AutoProcessor.from_pretrained(self.model_id, min_pixels=256 * 28 * 28, max_pixels=512 * 28 * 28)

    def ask(self, image_path):
        from PIL import Image
        if self._m is None:
            self._load()
        q = (f"Look at this picture. Is it a clear, sharp, realistic picture of {self.subject}, without heavy noise, "
             f"blotches or distortion? Answer only yes or no.")
        msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": q}]}]
        text = self._p.apply_chat_template(msgs, add_generation_prompt=True)
        inp = self._p(text=[text], images=[Image.open(image_path).convert("RGB")], return_tensors="pt").to(self.dev)
        out = self._m.generate(**inp, max_new_tokens=3, do_sample=False)
        ans = self._p.batch_decode(out[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip().lower()
        return ans.startswith("yes"), ans

    def __call__(self, clip, shot):
        d = Path(tempfile.mkdtemp())
        dur = shot.seconds
        votes = []
        for i, f in enumerate(self.at):
            p = d / f"f{i}.jpg"
            subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{dur * f:.2f}", "-i", clip, "-frames:v", "1", str(p)])
            if p.exists():
                votes.append(self.ask(str(p)))
        yes = sum(v for v, _ in votes)
        return yes >= self.need, f"vision judge {yes}/{len(votes)} yes ({', '.join(a for _, a in votes)})"
