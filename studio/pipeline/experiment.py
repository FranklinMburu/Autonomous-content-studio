"""Model try-out: can a new free model do our drafting or polishing? Same jobs, same gates, same judge.

    python -m studio.pipeline.experiment [--match nemotron-3.5] [--models nvidia:x,groq:y]

For each model: (1) write a grounded draft for 2 real queued topics, (2) polish an existing draft using
POLISH.md. Each output goes through our gates, the claim-by-claim fact check and the 1-5 quality score.
Results go to the run's Summary page and pipeline/experiments/<date>/ (scripts kept for blind rating).
"""
import argparse
import json
import re
import time

from . import gates, store

BASELINE = ["groq:openai/gpt-oss-120b"]


def nvidia_models(match):
    from ailayer.client import load_config
    from ailayer.env import secret
    from ailayer.providers import ADAPTERS
    p = load_config()["providers"]["nvidia"]
    names = ADAPTERS[p["kind"]][1](p["base_url"], secret(p["key_env"]))
    return sorted(n for n in names if re.search(match, n, re.I))


def packets():
    out = []
    for st in ("delivered", "queue", "ready"):
        for i in store.items(st):
            f = store.folder(st, i)
            d = store.read_json(f / "draft.json")
            if d:
                out.append({"id": i, "topic": store.read_json(f / "item.json")["topic"], "draft": d,
                            "sources": store.load_sources(f), "icons": store.read_json(f / "allowed_icons.json", []),
                            "flagged": [r for r in store.read_json(f / "draft_check.json", {}).get("fact_check", {})
                                        .get("results", []) if r.get("verdict") != "supported"],
                            "claude_polish_score": (store.read_json(f / "gate.json") or {}).get("score", {}).get("score")})
    return out[:2]


def polish_prompt(pk):
    from ailayer.skills import Source, sources_block
    rules = (store.ROOT / "POLISH.md").read_text(encoding="utf-8").split("## Hard rules")[1]
    srcs = [Source(s["url"], s["text"], s.get("title", "")) for s in pk["sources"]]
    return ("You are the EDITOR of a short animated explainer. Polish this DRAFT script (JSON) into a script viewers "
            "watch to the end, following these rules.\n\n## Hard rules" + rules +
            "\n\nDRAFT:\n" + json.dumps(pk["draft"], ensure_ascii=False) +
            "\n\nCLAIMS THE FACT CHECK FLAGGED (fix or remove):\n" +
            ("\n".join(f"- [{r['verdict']}] {r['claim']}" for r in pk["flagged"]) or "- none") +
            "\n\nALLOWED ICONS: " + ", ".join(pk["icons"]) + "\n\n" +
            sources_block(srcs, pk["topic"], 7000) + "\n\nReturn ONLY the complete polished JSON object.")


def evaluate(script, pk, stage, draft=None):
    from ailayer.skills import Source, fact_check
    from .run import score
    srcs = [Source(s["url"], s["text"], s.get("title", "")) for s in pk["sources"]]
    fc = fact_check(" ".join(gates.narration(script)), srcs)
    sc = score(script, pk["sources"])
    return {"fact": fc["counts"], "score": sc["score"], "score_reason": sc["reason"], "judge_model": sc["model"]}


def run(models, log=print):
    from ailayer import ask
    from . import draft as drafting
    pks = packets()
    rows, keep = [], {}
    for ref in models:
        for pk in pks:
            for job in ("draft", "polish"):
                rec = {"model": ref, "topic": pk["topic"], "job": job}
                t0 = time.time()
                try:
                    if job == "draft":
                        script, info = drafting.draft(pk["topic"], None, pk["sources"], [pk["topic"]], pk["icons"],
                                                      [ref], log=log)
                    else:
                        def v(d):
                            return gates.check_script(d, pk["sources"], pk["icons"], stage="polished", draft=pk["draft"])
                        r = ask(polish_prompt(pk), models=[ref], validate=v, temperature=0.6, max_tokens=6000)
                        script = r.data
                    rec.update(gates="pass", **evaluate(script, pk, job))
                    keep[f"{job}__{pk['id']}__{re.sub(r'[^a-z0-9]+', '-', ref.lower())}"] = script
                except Exception as e:
                    rec.update(gates="FAIL", error=str(e)[:240])
                rec["seconds"] = round(time.time() - t0)
                rows.append(rec)
                log(f"  {ref} | {job} | {pk['topic']} -> {rec.get('gates')} score={rec.get('score')} "
                    f"fact={rec.get('fact')} {rec.get('error', '')[:160]} ({rec['seconds']}s)")
    return rows, keep, pks


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", default=r"nemotron-3\.5|nemotron-3-5")
    ap.add_argument("--models", default="")
    ap.add_argument("--no-baseline", action="store_true")
    a = ap.parse_args(argv)
    found = nvidia_models(a.match)
    print(f"NVIDIA models matching {a.match!r}: {found or 'NONE'}")
    cands = [m.strip() for m in a.models.split(",") if m.strip()] or [f"nvidia:{m}" for m in found
                                                                       if not re.search(r"embed|rerank|guard|safety|reward", m, re.I)][:2]
    if not cands:
        print("No candidate model available on this NVIDIA account.")
        return 1
    base = [] if a.no_baseline else BASELINE
    rows, keep, pks = run(cands + base)
    lines = ["| Model | Job | Topic | Gates | Fact check | Score /5 | Time |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        fc = r.get("fact") or {}
        lines.append(f"| {r['model']} | {r['job']} | {r['topic'][:40]} | {r['gates']} | "
                     f"{fc.get('supported', '-')}/{fc.get('partial', '-')}/{fc.get('unsupported', '-')} | "
                     f"{r.get('score', '-')} | {r['seconds']}s |")
    ref_scores = [p["claude_polish_score"] for p in pks if p["claude_polish_score"]]
    lines.append(f"\nFact check = supported/partial/unsupported. Claude's accepted polish scored: {ref_scores or 'n/a'}.")
    print("\n".join(lines))
    day = time.strftime("%Y%m%d-%H%M")
    out = store.base() / "experiments" / day
    store.write_json(out / "results.json", {"models": cands + base, "rows": rows})
    for k, s in keep.items():
        store.write_json(out / f"{k}.json", s)
    from .run import commit_and_push
    commit_and_push(f"Experiment {day}: {', '.join(cands)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
