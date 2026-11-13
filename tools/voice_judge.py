"""AI listening panel for the voice lab: rates the blind samples so Franklin does not have to (13 Nov 2026).

    python tools/voice_judge.py rate   --dir samples/ --script episodes/.../script.json --out verdict.json
    python tools/voice_judge.py reveal --verdict verdict.json --key blind_key.json [--scores scores.json] --out report.md

How it stays fair:
- The judges only get the samples (A, B, C ...) and never the key; inside each round the samples are re-labelled
  "Voice 1..N" in a fresh random order, so neither the letter nor the position can favour one engine.
- Several judges: every free Gemini model that can listen (up to 2) x 2 rounds. Each one compares ALL voices at once
  (a comparison is steadier than separate scores) and must say what it heard (a timestamped flaw, or "none").
- `reveal` runs only after `rate` has written its verdict; it joins the letters with the key and the measured scores.
The choice is a recommendation: the TE voice is locked in the TE channel settings and changes only with Franklin's yes.

Key: GEMINI_API_KEY from the environment (GitHub secret). Never printed.
"""
import argparse
import base64
import json
import random
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.clips import ai_pass as G  # noqa: E402  (the same paced, retried Gemini caller the clips judge uses)

TRAITS = ["natural", "clarity", "pace", "warmth", "clean"]
RUBRIC = """You are the casting director of a YouTube tech-education channel ("Build Basics": how software really
works, calm explainer videos for beginners). The reference is the channel Maitis: a calm, warm, confident storyteller
at about 150-175 words a minute with many short pauses (about 20-26 a minute). Every voice below reads the SAME script.
Listen to every voice fully, then score each one 1-10 on:
- natural: sounds like a real person talking, not a machine (breathing, intonation, stress on the right words)
- clarity: every word easy to understand, correct pronunciation of tech words
- pace: speed and pauses fit a calm explainer (too fast, rushed, flat or dragging = low)
- warmth: friendly, trustworthy, a voice you would listen to for 10 minutes
- clean: no glitches, clicks, robotic buzz, skipped or repeated words, wrong emphasis (10 = none at all)
and "overall" 1-10 = how good this voice is as the channel's narrator. Be harsh and use the whole scale.
For each voice give "heard": one concrete observation with a rough time ("0:12 'database' mispronounced", or
"none"). Then "rank": every voice label, best first. Return JSON:
{"voices": [{"label": "Voice 1", "natural": n, "clarity": n, "pace": n, "warmth": n, "clean": n, "overall": n,
"heard": "..."}], "rank": ["Voice 2", ...], "why": "one sentence on the winner"}"""


def small(mp3):
    """Mono 48 kbps copy: keeps every request far under the inline limit."""
    out = Path(tempfile.mkdtemp()) / "a.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", "24000", "-b:a", "48k", str(out)], check=True)
    return out


def script_text(p):
    s = json.loads(Path(p).read_text(encoding="utf-8"))
    return " ".join(l.strip() for b in s["beats"] for l in b["lines"] if l.strip())


def valid(r, labels):
    if not isinstance(r, dict) or not isinstance(r.get("voices"), list):
        return False
    got = {v.get("label") for v in r["voices"] if isinstance(v, dict)}
    return set(labels) <= got and all(isinstance(v.get("overall"), (int, float)) for v in r["voices"] if v.get("label") in labels)


def rate(a):
    samples = sorted(Path(a.dir).glob("sample_*.mp3"))
    if len(samples) < 2:
        sys.exit(f"need at least 2 samples in {a.dir}")
    letters = [p.stem.split("_")[1] for p in samples]
    audio = {l: base64.b64encode(small(p).read_bytes()).decode() for l, p in zip(letters, samples)}
    text = script_text(a.script) if a.script else ""
    first = G.pick_model()
    judges = [first] + [m for m in G.FALLBACK if "lite" not in m][:1]
    rounds = []
    rnd = random.Random(a.seed)
    for model in judges:
        for r_i in range(a.rounds):
            order = letters[:]
            rnd.shuffle(order)
            labels = [f"Voice {i + 1}" for i in range(len(order))]
            parts = [{"text": RUBRIC + (f"\n\nTHE SCRIPT (what every voice should say):\n{text[:3000]}" if text else "")}]
            for lab, letter in zip(labels, order):
                parts += [{"text": f"\n{lab}:"}, {"inline_data": {"mime_type": "audio/mpeg", "data": audio[letter]}}]
            r = G.call(model, parts)
            if not valid(r, labels):
                print(f"[judge] {model} round {r_i + 1}: no usable answer, skipped", flush=True)
                continue
            back = dict(zip(labels, order))
            voices = {back[v["label"]]: {k: v.get(k) for k in TRAITS + ["overall", "heard"]} for v in r["voices"] if v.get("label") in back}
            rank = [back[x] for x in r.get("rank", []) if x in back]
            rank += [l for l in sorted(voices, key=lambda l: -voices[l]["overall"]) if l not in rank]
            rounds.append({"judge": model, "round": r_i + 1, "voices": voices, "rank": rank, "why": r.get("why", "")})
            print(f"[judge] {model} round {r_i + 1}: " + " > ".join(rank), flush=True)
    if not rounds:
        sys.exit("no judge answered (free quota?): nothing written")
    summary = {}
    for l in letters:
        got = [r["voices"][l] for r in rounds if l in r["voices"]]
        num = lambda k: round(statistics.mean(float(g[k]) for g in got if isinstance(g.get(k), (int, float))), 2) if got else None
        summary[l] = {**{k: num(k) for k in TRAITS + ["overall"]},
                      "avg_rank": round(statistics.mean(r["rank"].index(l) + 1 for r in rounds if l in r["rank"]), 2),
                      "firsts": sum(r["rank"][0] == l for r in rounds),
                      "heard": [g.get("heard") for g in got]}
    best = sorted(letters, key=lambda l: (summary[l]["avg_rank"], -(summary[l]["overall"] or 0)))
    out = {"judges": judges, "rounds": rounds, "summary": summary, "order": best,
           "agree": sum(r["rank"][0] == best[0] for r in rounds), "of": len(rounds)}
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("AI panel order (letters only, still blind):", " > ".join(best), f"({out['agree']}/{out['of']} judges put {best[0]} first)")


def reveal(a):
    v = json.loads(Path(a.verdict).read_text(encoding="utf-8"))
    key = json.loads(Path(a.key).read_text(encoding="utf-8"))
    scores = json.loads(Path(a.scores).read_text(encoding="utf-8")) if a.scores and Path(a.scores).exists() else {}
    eng = lambda l: key.get(l, {}).get("engine", "?")
    s = v["summary"]
    lines = ["# Voice lab: the AI listening panel's verdict", "",
             f"Judges: {', '.join(v['judges'])}; {v['of']} blind rounds (labels and order shuffled every round). "
             f"{v['agree']} of {v['of']} put the winner first.", "",
             "| Rank | Sample | Engine | Overall | Natural | Clarity | Pace | Warmth | Clean | Avg rank | Firsts |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(v["order"], 1):
        x = s[l]
        lines.append(f"| {i} | {l} | {eng(l)} | {x['overall']} | {x['natural']} | {x['clarity']} | {x['pace']} | {x['warmth']} | "
                     f"{x['clean']} | {x['avg_rank']} | {x['firsts']} |")
    lines += ["", "## What the judges heard"]
    for l in v["order"]:
        lines.append(f"- **{l} ({eng(l)})**: " + " / ".join(h for h in s[l]["heard"] if h)[:600])
    if scores:
        lines += ["", "## Measured (machine) scores per engine", "", "```", json.dumps(scores, indent=1)[:3000], "```"]
    lines += ["", "The TE voice is locked in the TE channel settings: this is a recommendation; it changes only with Franklin's yes."]
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4 + 2 + len(v["order"])]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("rate")
    r.add_argument("--dir", required=True)
    r.add_argument("--script")
    r.add_argument("--out", default="verdict.json")
    r.add_argument("--rounds", type=int, default=2)
    r.add_argument("--seed", type=int, default=13)
    r.set_defaults(fn=rate)
    v = sub.add_parser("reveal")
    v.add_argument("--verdict", required=True)
    v.add_argument("--key", required=True)
    v.add_argument("--scores")
    v.add_argument("--out", default="report.md")
    v.set_defaults(fn=reveal)
    a = ap.parse_args()
    a.fn(a)
