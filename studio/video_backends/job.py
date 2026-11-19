"""The one standard job every backend understands, and what comes back."""
import hashlib, json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Shot:
    prompt: str                       # what happens in the shot, in plain words
    image: str | None = None          # start picture (path); None = text-to-video
    seconds: float = 3.0
    width: int = 480                  # 9:16 by default; backends round to what they support
    height: int = 832
    fps: int = 24
    camera: str = "slow push in"      # a camera move in words; the own renderer reads it too
    negative: str = "text, watermark, logo, blurry, distorted, low quality, flicker"
    seed: int = 0
    tags: dict = field(default_factory=dict)   # free-form (episode, shot id) for the log

    def key(self):
        """Same shot = same key, so a re-run reuses the clip instead of generating it again."""
        d = asdict(self); d.pop("tags")
        if self.image and Path(self.image).exists():
            d["image"] = hashlib.sha256(Path(self.image).read_bytes()).hexdigest()
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:20]


@dataclass
class Result:
    path: str
    backend: str
    seconds_taken: float
    cached: bool = False
    tried: list = field(default_factory=list)   # [(backend, outcome)] in order, for the log
