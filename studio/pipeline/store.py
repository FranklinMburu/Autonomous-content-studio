"""The pipeline's state: one folder per script, inside the stage folder it is in.

    pipeline/queue/<id>/       drafted, checked, waiting for the polish step
    pipeline/ready/<id>/       polished and accepted by the gates, waiting to be rendered
    pipeline/delivered/<id>/   rendered; video in a GitHub Release; "Ready to upload" issue open
    pipeline/published/<id>/   you uploaded it and closed the issue
    pipeline/attention/<id>/   stopped with a reason (needs a person, or a retry)

Git is the source of truth: every move is a commit you can see on your phone. Only the GitHub workflows move
items, and they share one concurrency group, so there is never more than one writer.

Files in an item folder:
    item.json      id, topic, stage, history of moves (with reasons), attempts, provenance
    sources/NN.json  frozen source text (url, title, text, sha256, retrieved)
    draft.json     the checked free-model draft (studio script format)
    draft_check.json  gate + fact-check results for the draft
    polished.json  the polished script (added by the polish step, through a pull request)
    gate.json      post-polish gate results
    video.json     render result, release URL, issue number
    feedback.json  why earlier polish attempts were rejected (read by the next polish)
"""
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "pipeline"
STAGES = ("queue", "ready", "delivered", "published", "attention")
ALLOWED = {
    ("queue", "ready"), ("queue", "attention"),
    ("ready", "delivered"), ("ready", "attention"),
    ("delivered", "published"),
    ("attention", "queue"),
}
ID_RE = re.compile(r"^[0-9]{8}-[a-z0-9-]{1,60}$")


class StoreError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def base():
    return Path(os.environ.get("PIPELINE_DIR") or BASE)


def slug(text, n=50):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return (s[:n].rstrip("-")) or "item"


def topic_key(topic):
    """Normalised topic hash: same question, different punctuation/case/word order = same key."""
    words = sorted(set(re.findall(r"[a-z0-9]+", str(topic).lower())) - {"do", "does", "why", "how", "the", "a",
                                                                            "an", "you", "your", "we", "our"})
    return hashlib.sha256(" ".join(words).encode()).hexdigest()[:16]


def write_json(path, data):
    """Atomic write: a crash leaves either the old file or the new one, never half a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def folder(stage, item_id):
    if stage not in STAGES:
        raise StoreError(f"unknown stage {stage!r}")
    if not ID_RE.match(item_id):
        raise StoreError(f"bad item id {item_id!r}")
    return base() / stage / item_id


def find(item_id):
    """(stage, folder) of an item, or (None, None)."""
    for st in STAGES:
        f = base() / st / item_id
        if (f / "item.json").exists():
            return st, f
    return None, None


def items(stage):
    d = base() / stage
    if not d.exists():
        return []
    return sorted(p.name for p in d.iterdir() if (p / "item.json").exists())


def all_topic_keys():
    keys = {}
    for st in STAGES:
        for i in items(st):
            it = read_json(base() / st / i / "item.json", {})
            if it.get("topic_key"):
                keys[it["topic_key"]] = (st, i)
    return keys


def create(topic, lane=None, stage="queue", day=None):
    """Make a new item folder (in `stage`, normally queue or attention). Refuses duplicates by topic."""
    key = topic_key(topic)
    dup = all_topic_keys().get(key)
    if dup:
        raise StoreError(f"duplicate topic: already in {dup[0]} as {dup[1]}")
    day = day or datetime.now(timezone.utc).strftime("%Y%m%d")
    item_id = f"{day}-{slug(topic)}"
    n = 2
    while find(item_id)[0]:
        item_id = f"{day}-{slug(topic, 44)}-{n}"
        n += 1
    f = folder(stage, item_id)
    f.mkdir(parents=True, exist_ok=False)
    write_json(f / "item.json", {"id": item_id, "topic": topic, "lane": lane, "topic_key": key, "stage": stage,
                                 "created": now(), "attempts": 0,
                                 "history": [{"at": now(), "to": stage, "why": "created"}], "provenance": {}})
    return item_id, f


def item(item_id):
    st, f = find(item_id)
    if not st:
        raise StoreError(f"no item {item_id!r}")
    return read_json(f / "item.json"), f


def update(item_id, **fields):
    it, f = item(item_id)
    it.update(fields)
    write_json(f / "item.json", it)
    return it


def move(item_id, to, why):
    """Move an item to another stage, only along an allowed arrow. Records the move and its reason."""
    st, f = find(item_id)
    if not st:
        raise StoreError(f"no item {item_id!r}")
    if (st, to) not in ALLOWED:
        raise StoreError(f"not allowed: {st} -> {to} for {item_id}")
    dest = folder(to, item_id)
    if dest.exists():
        raise StoreError(f"{dest} already exists")
    it = read_json(f / "item.json")
    it["stage"] = to
    it["history"].append({"at": now(), "from": st, "to": to, "why": str(why)[:500]})
    write_json(f / "item.json", it)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(f), str(dest))
    return dest


def save_sources(item_folder, sources):
    """Freeze source texts: url, title, text, sha256, retrieved time. Returns the stored records."""
    out = []
    for i, s in enumerate(sources, 1):
        rec = {"n": i, "url": s["url"], "title": s.get("title", ""), "text": s["text"],
               "sha256": hashlib.sha256(s["text"].encode()).hexdigest(), "retrieved": s.get("retrieved") or now(),
               "kind": s.get("kind", "")}
        write_json(Path(item_folder) / "sources" / f"{i:02d}.json", rec)
        out.append(rec)
    return out


def load_sources(item_folder):
    d = Path(item_folder) / "sources"
    recs = [read_json(p) for p in sorted(d.glob("*.json"))] if d.exists() else []
    for r in recs:   # a frozen source must not change after research
        if hashlib.sha256(r["text"].encode()).hexdigest() != r["sha256"]:
            raise StoreError(f"source {r['n']} of {item_folder.name} was modified after it was frozen")
    return recs


def counts():
    return {st: len(items(st)) for st in STAGES}


def waiting_for_polish():
    out = []
    for i in items("queue"):
        f = base() / "queue" / i
        if not (f / "polished.json").exists():
            out.append(i)
    return out

