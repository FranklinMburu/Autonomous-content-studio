"""The seeded look of one video: accent colour, camera direction and drift, music key and tempo.
Same seed -> same style. Different episodes get different seeds, so no two videos look or sound alike while all of
them stay inside the channel's look (channels/te/channel.json)."""
import hashlib, json

from ..paths import ROOT


def channel(code="te"):
    return json.loads((ROOT / "channels" / code / "channel.json").read_text(encoding="utf-8"))


def seed_of(name):
    """A stable seed from the episode folder name (used when plan.json has none)."""
    return int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)


def _pick(seed, salt, n):
    return int(hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()[:8], 16) % n


def style_for(seed, ch=None):
    ch = ch or channel()
    look, mus = ch["look"], ch["music"]
    acc = look["accents"][_pick(seed, "accent", len(look["accents"]))]
    rgb = [int(acc[i:i + 2], 16) for i in (1, 3, 5)]
    lo, hi = mus["bpm"]
    return {"seed": int(seed) % 2_147_483_647, "accent": acc, "accent_rgb": rgb,
            "cool_rgb": look["cool"][_pick(seed, "cool", len(look["cool"]))],
            "sign": 1 if _pick(seed, "sign", 2) else -1,
            "drift": [round(_pick(seed, f"drift{i}", 628) / 100, 2) for i in range(4)],
            "music": {"bpm": lo + _pick(seed, "bpm", hi - lo + 1), "key": mus["keys"][_pick(seed, "key", len(mus["keys"]))]}}
