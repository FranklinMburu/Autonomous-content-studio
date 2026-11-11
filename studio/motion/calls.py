"""Model-call helpers for the motion writer: config, retries while free models cool down, call logs, draft repair.
A copy of the generic helpers in studio/story/writer.py, kept here on purpose so the motion engine never imports
the story engine (that pulled in pycairo and broke the isolation on 11 Nov). Change them here, not by importing."""
import json, re

from ..paths import ROOT

NEW_BRAIN_ARGS = ("time_budget_s", "parallel")
RATE = re.compile(r"rate limit|cooling down|HTTP (0|429|5\d\d)|daily|allowance|quota|could answer|timed? ?out", re.I)


def _cfg():
    p = ROOT / "pipeline" / "config.json"
    cfg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    return cfg.get("story_script_models") or cfg.get("draft_models") or ["groq:openai/gpt-oss-120b"]


def repair_draft(prompt, models, check, ask, log, rounds=3, budget_s=900):
    """Fallback when no model's first draft passes the rules: each model drafts once without the rule gate, then
    the best draft (fewest problems) is repaired round by round with its exact problems. Returns (draft, problems);
    problems may be non-empty (then the copy-paste polish finishes the script)."""
    import time
    t0, best, best_p = time.time(), None, None
    for m in models:
        if time.time() - t0 > budget_s:
            break
        try:
            r = ask(prompt, models=[m], json_out=True, temperature=0.7, max_tokens=3000, time_budget_s=300)
        except Exception as e:  # noqa: BLE001
            log(f"    {m}: no draft ({str(e)[:120]})"); continue
        pr = check(r.data)
        log(f"    {m}: draft with {len(pr)} rule problem(s): {'; '.join(pr)[:300]}")
        if best_p is None or len(pr) < len(best_p):
            best, best_p = r.data, pr
        if not pr:
            return best, []
    for rnd in range(rounds):
        if not best_p or best is None or time.time() - t0 > budget_s:
            break
        fix = (prompt + "\n\nYOUR DRAFT:\n" + json.dumps(best, ensure_ascii=False)[:9000] + "\n\nIt breaks these rules. "
               "Fix every one and return the complete corrected JSON only:\n" + "\n".join(f"- {x}" for x in best_p))
        for m in models:
            try:
                r = ask(fix, models=[m], json_out=True, temperature=0.4, max_tokens=3000, time_budget_s=300)
            except Exception:  # noqa: BLE001
                continue
            pr = check(r.data)
            log(f"    repair {rnd + 1} by {m}: {len(pr)} problem(s) {('; '.join(pr))[:200]}")
            if len(pr) < len(best_p):
                best, best_p = r.data, pr
            break
    return best, best_p or []


def calls(x):
    """One line per model call (model, seconds, outcome) from a Result or an AIError: the timing log."""
    out = []
    for a in getattr(x, "attempts", None) or []:
        secs = a.get("latency_s", a.get("seconds"))
        t = f" {secs:.0f}s" if isinstance(secs, (int, float)) else ""
        if a.get("ok"):
            out.append(f"{a['ref']}{t} ok")
        elif a.get("skipped"):
            out.append(f"{a['ref']} skipped ({a['skipped']})")
        elif a.get("invalid"):
            out.append(f"{a['ref']}{t} invalid: {'; '.join(map(str, a['invalid']))[:220]}")
        else:
            out.append(f"{a['ref']}{t} {a.get('error', '')} {str(a.get('reason', ''))[:160]}")
    return out


def _compat(fn):
    """Call a brain function with the newer options (time_budget_s, parallel); if the installed brain is older and
    doesn't know them, call it again without them (the error is raised before any request is made)."""
    def call(*a, **kw):
        try:
            return fn(*a, **kw)
        except TypeError as e:
            if not any(k in str(e) for k in NEW_BRAIN_ARGS):
                raise
            return fn(*a, **{k: v for k, v in kw.items() if k not in NEW_BRAIN_ARGS})
    return call


def _timed(log, label, fn):
    """Run one AI step, log every model call with its time, and re-raise failures with the call log."""
    import time
    t0 = time.time()
    try:
        r = fn()
    except Exception as e:  # noqa: BLE001
        log(f"  {label}: FAILED after {time.time() - t0:.0f}s: {str(e)[:300]}")
        for line in calls(e):
            log(f"    call: {line}")
        raise
    log(f"  {label}: {time.time() - t0:.0f}s")
    for line in calls(r[0] if isinstance(r, tuple) else r):
        log(f"    call: {line}")
    return r


def patient(fn, label, log, max_wait_s=1500):
    """Run fn(); when every free model is rate-limited or down, wait for the cooldown and try again (up to
    max_wait_s in total) instead of failing the video (1 Nov: a fact check failed because all three providers were
    cooling down at that minute)."""
    import time, datetime as dt
    t0 = time.time()
    while True:
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            err = str(e)
            if not RATE.search(err) or time.time() - t0 > max_wait_s:
                raise
            m = re.search(r"until (\d\d):(\d\d) UTC", err)
            wait = 120
            if m:
                now = dt.datetime.now(dt.timezone.utc)
                until = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=5)
                if until < now:
                    until += dt.timedelta(days=1)
                wait = (until - now).total_seconds()
            wait = max(30, min(300, wait, max_wait_s - (time.time() - t0)))
            log(f"  {label}: all models busy ({err[:120]}); waiting {wait:.0f}s and trying again")
            time.sleep(wait)
