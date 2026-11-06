#!/usr/bin/env python3
"""Story lab: put v1 (Milestone 1 rules) and v2 (emotion-led) scripts of the same topics side by side, BLIND.

    python tools/story_lab.py <drafts_dir> <out_dir>

For every topic folder in <drafts_dir> that has both script_v1.json (v1) and script.json (v2, the default), writes
<out_dir>/scripts.md (Script A / Script B per topic, order shuffled per topic) and <out_dir>/blind_key.json
(which letter is which). Rate scripts.md before opening the key.
"""
import json
import random
import sys
from pathlib import Path


def text(stage):
    s = stage["script"]
    out = [f"**{s.get('title', '')}**", ""]
    for b in s["beats"]:
        out.append(" ".join(b.get("lines", [])))
        out.append("")
    fc = stage.get("fact_check", {}).get("counts", {})
    out.append(f"_fact check: {fc}_")
    return "\n".join(out)


def main(drafts, out):
    out.mkdir(parents=True, exist_ok=True)
    md, key = ["# Story lab: blind script pairs", "",
               "For each topic, read Script A and Script B. Rate each 1-5 for: would you keep watching? "
               "did you feel something? is it clear? Then say which one you'd post.", ""], {}
    for d in sorted(p for p in drafts.iterdir() if p.is_dir()):
        v1, v2 = d / "script_v1.json", d / "script.json"
        if not (v1.exists() and v2.exists()):
            continue
        pair = [("v1", json.loads(v1.read_text(encoding="utf-8"))), ("v2", json.loads(v2.read_text(encoding="utf-8")))]
        random.shuffle(pair)
        key[d.name] = {"A": pair[0][0], "B": pair[1][0]}
        md += [f"## {d.name}", "", "### Script A", "", text(pair[0][1]), "", "### Script B", "", text(pair[1][1]), "", "---", ""]
    (out / "scripts.md").write_text("\n".join(md), encoding="utf-8")
    (out / "blind_key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"{len(key)} topic(s) paired")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
