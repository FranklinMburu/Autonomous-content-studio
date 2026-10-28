"""Anti-drift test set (weekly). The same fixed topics are researched, drafted and scored every week; a drop
against the stored baseline opens an alert issue. Nothing here enters the real queue.

    python -m studio.pipeline drift                  run, compare, alert on a drop
    python -m studio.pipeline drift --set-baseline   accept this run as the new normal
"""
import json

from . import gates, store

BENCH = store.ROOT / "pipeline" / "benchmarks"
TOPICS = ["Why do our fingers wrinkle in water?", "Why do cats purr?", "Why can't you tickle yourself?"]
DROP = 0.75          # alert when the average score falls this much below the baseline


def run(set_baseline=False, log=print):
    from ailayer import ask
    from . import draft as drafting, research, run as steps
    cfg = steps.config()
    results = []
    for t in TOPICS:
        rec = {"topic": t}
        try:
            sources, plan = research.research(t, ask=ask, log=log)
            for i, s in enumerate(sources, 1):
                s.setdefault("n", i)
            icons = drafting.allowed_icons(t, sources, plan.get("questions", []))
            script, info = drafting.draft(t, None, sources, plan.get("questions", [t]), icons, cfg["draft_models"],
                                          log=log)
            rec.update(passed_gates=True, writer=info["writer"], fact=info["fact_check"]["counts"],
                       score=steps.score(script, sources)["score"])
        except Exception as e:
            rec.update(passed_gates=False, error=str(e)[:300], score=0)
        results.append(rec)
        log(f"  {t}: {rec.get('score')} ({rec.get('writer', rec.get('error', ''))})")
    avg = round(sum(r["score"] for r in results) / len(results), 2)
    out = {"at": store.now(), "average": avg, "results": results}
    BENCH.mkdir(parents=True, exist_ok=True)
    with open(BENCH / "history.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(out, ensure_ascii=False) + "\n")
    base = store.read_json(BENCH / "baseline.json")
    alerts = []
    if base and not set_baseline:
        if avg < base["average"] - DROP:
            alerts.append(f"average score fell from {base['average']} to {avg}")
        for r, b in zip(results, base["results"]):
            if b.get("passed_gates") and not r["passed_gates"]:
                alerts.append(f"'{r['topic']}' no longer passes the gates: {r.get('error', '')[:200]}")
    if set_baseline or (not base and all(r["passed_gates"] for r in results)):
        store.write_json(BENCH / "baseline.json", out)
        log(f"baseline saved (average {avg})")
    if alerts:
        from . import github as gh
        gh.ensure_label("drift-alert", "d1242f", "Quality drop found by the weekly test set")
        gh.create_issue("Quality alert: the weekly test set dropped",
                        "The weekly anti-drift run found:\n\n" + "\n".join(f"- {a}" for a in alerts) +
                        f"\n\nScores this week: {json.dumps(results, ensure_ascii=False)[:3000]}\n\n"
                        "Nothing was published because of this; the gates still apply. Check the brain's health "
                        "report and recent model changes.", ["drift-alert"])
    steps.commit_and_push(f"Drift check: average {avg}")
    log("ALERTS: " + "; ".join(alerts) if alerts else f"No drop (average {avg}).")
    return 1 if alerts else 0
