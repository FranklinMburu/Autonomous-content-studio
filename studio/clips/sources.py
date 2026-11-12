"""Ingest: one stream = one folder. The engine only reads files; it never downloads anything itself.

    <stream>/
      stream.mp4      the VOD (a file Franklin provides, or one fetched by an official, permitted route)
      rights.json     REQUIRED: why we are allowed to clip it (no rights file -> nothing is made)
      chat.json       optional chat log (TwitchDownloader JSON, chat-downloader JSON, or CSV "t,user,text")
      clips.json      optional viewer-made clips {"clips": [{"vod_offset": s, "duration": s, "views": n}]}
                      (Twitch Get Clips returns vod_offset; Kick clips can be listed by hand)
      words.json      optional transcript with word times; made by `transcribe` when missing

Adapters per platform only differ in how chat and clips are read; add one function to CHAT_READERS.
"""
import csv, json
from pathlib import Path

ALLOWED_RIGHTS = {
    "own": "our own stream or our own recording",
    "program": "the streamer runs an official clipping program or campaign that invites clippers",
    "permission": "explicit written permission from the rights holder",
    "licence": "a licence that allows reuse and editing (e.g. CC BY)",
}
VIDEO_NAMES = ("stream.mp4", "vod.mp4", "stream.mkv", "vod.mkv", "stream.webm")


class RightsError(Exception):
    pass


def rights(folder):
    """The rights record. Raises RightsError when it is missing or not one of the allowed kinds."""
    p = Path(folder) / "rights.json"
    if not p.exists():
        raise RightsError(f"{folder}: no rights.json - we only clip streams we are allowed to clip")
    r = json.loads(p.read_text(encoding="utf-8"))
    kind = r.get("source")
    if kind not in ALLOWED_RIGHTS:
        raise RightsError(f"{folder}: rights.json source must be one of {sorted(ALLOWED_RIGHTS)} (got {kind!r})")
    need = {"own": ["owner"], "program": ["program", "terms_url"], "permission": ["granted_by", "proof"],
            "licence": ["licence", "proof"]}[kind]
    missing = [k for k in need if not r.get(k)]
    if missing:
        raise RightsError(f"{folder}: rights.json ({kind}) is missing {', '.join(missing)}")
    return r


def video(folder):
    for n in VIDEO_NAMES:
        if (Path(folder) / n).exists():
            return Path(folder) / n
    raise FileNotFoundError(f"{folder}: no stream video ({', '.join(VIDEO_NAMES)})")


# --- chat ---------------------------------------------------------------------------------------------------------
def _twitchdownloader(d):
    return [(float(c["content_offset_seconds"]), (c.get("commenter") or {}).get("display_name", ""),
             (c.get("message") or {}).get("body", "")) for c in d["comments"]]


def _chat_downloader(d):   # xenova/chat-downloader --output x.json: a list of messages with time_in_seconds
    return [(float(m["time_in_seconds"]), (m.get("author") or {}).get("name", ""), m.get("message", ""))
            for m in d if "time_in_seconds" in m]


def _kick(d):              # Kick chat replay export: {"messages": [{"offset_s": .., "sender": .., "content": ..}]}
    return [(float(m["offset_s"]), m.get("sender", ""), m.get("content", "")) for m in d["messages"]]


CHAT_READERS = [("comments", _twitchdownloader), ("messages", _kick)]


def chat(folder):
    """[(seconds, user, text)] sorted, or [] when there is no chat log."""
    folder = Path(folder)
    p = folder / "chat.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d, list):
            out = _chat_downloader(d)
        else:
            reader = next((f for key, f in CHAT_READERS if key in d), None)
            if not reader:
                raise ValueError(f"{p}: unknown chat format (keys {list(d)[:5]})")
            out = reader(d)
        return sorted(out)
    p = folder / "chat.csv"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return sorted((float(r["t"]), r.get("user", ""), r.get("text", "")) for r in csv.DictReader(f))
    return []


def viewer_clips(folder):
    p = Path(folder) / "clips.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return [c for c in d.get("clips", []) if c.get("vod_offset") is not None]


def words(folder):
    p = Path(folder) / "words.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) else d


def load(folder):
    """Everything the engine knows about one stream. Rights are checked first."""
    folder = Path(folder)
    r = rights(folder)
    return {"folder": folder, "rights": r, "video": video(folder), "chat": chat(folder),
            "viewer_clips": viewer_clips(folder), "words": words(folder)}
