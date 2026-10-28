"""The pipeline's workflow steps. Each is run by one GitHub workflow; all share one concurrency group.

    python -m studio.pipeline draft [--topic T] [--count N]   nightly: research + draft + gates -> queue
    python -m studio.pipeline gate-pr --pr N                   on a polish pull request: check, accept or reject
    python -m studio.pipeline produce [--limit N]             render ready scripts -> Release + upload issue
    python -m studio.pipeline published --issue N             you closed an upload issue -> published
    python -m studio.pipeline status                          rewrite the pinned "Studio status" issue
"""
import json
import os
import re
import subprocess
import time
from pathlib import Path

from . import gates, polish, store

CONFIG = store.ROOT / "pipeline" / "config.json"
DEFAULTS = {"buffer_target": 5, "drafts_per_run": 2, "produce_per_run": 3, "max_unsupported_in_draft": 2,
            "draft_models": ["groq:openai/gpt-oss-120b", "google:gemini-3.6-flash", "nvidia:minimaxai/minimax-m3.1-flash"],
            "lane": None, "owner_logins": ["FranklinMburu"]}


def config():
    c = dict(DEFAULTS)
    c.update(store.read_json(CONFIG, {}))
    return c


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- git (only the workflows commit)

def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=store.ROOT, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def commit_and_push(message):
    git("add", "-A", "pipeline", "topics-done.txt", check=False)
    if not git("status", "--porcelain", "pipeline", "topics-done.txt").strip():
        log("nothing to commit")
        return False
    git("-c", "user.name=content-studio-bot", "-c", "user.email=actions@users.noreply.github.com",
        "commit", "-q", "-m", message)
    branch = os.environ.get("PIPELINE_BRANCH", "main")
    for i in range(4):
        if subprocess.run(["git", "push", "-q", "origin", f"HEAD:{branch}"], cwd=store.ROOT).returncode == 0:
            return True
        time.sleep(3 * (i + 1))
        git("pull", "-q", "--rebase", "origin", branch)
    raise RuntimeError("could not push to main after 4 tries")


# ---------------------------------------------------------------- draft

def topics_todo():
    todo = store.ROOT / "topics.txt"
    done = store.ROOT / "topics-done.txt"
    topics = [l.strip() for l in todo.read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.lstrip().startswith("#")] if todo.exists() else []
    done_keys = {store.topic_key(t) for t in (done.read_text(encoding="utf-8").splitlines() if done.exists() else [])
                 if t.strip()}
    have = store.all_topic_keys()
    return [t for t in topics if store.topic_key(t) not in done_keys and store.topic_key(t) not in have]


def buffer_size():
    return len(store.items("queue")) + len(store.items("ready")) + len(store.items("delivered"))


def draft_one(topic, lane, cfg):
    from ailayer import ask
    from . import draft as drafting, research
    item_id, f = store.create(topic, lane)
    log(f"[draft] {item_id}: {topic}")
    try:
        sources, plan = research.research(topic, ask=ask, log=log)
        recs = store.save_sources(f, sources)
        icons = drafting.allowed_icons(topic, recs, plan.get("questions", []))
        store.write_json(f / "allowed_icons.json", icons)
        others = polish.other_narrations() + [" ".join(gates.narration(store.read_json(store.folder("queue", i) / "draft.json", {})))
                                              for i in store.items("queue") if i != item_id]
        script, info = drafting.draft(topic, lane, recs, plan.get("questions", [topic]), icons,
                                      cfg["draft_models"], others=[o for o in others if o], log=log)
        script["topic"] = topic
        store.write_json(f / "draft.json", script)
        store.write_json(f / "draft_check.json", {"gates": [], **info})
        store.update(item_id, provenance={"research_plan": plan, "writer": info["writer"],
                                          "candidates": info["candidates"], "judge": info["judge"],
                                          "rules": "studio/pipeline/draft.py TASK + POLISH.md"})
        bad = info["fact_check"]["counts"].get("unsupported", 0)
        if bad > cfg["max_unsupported_in_draft"]:
            store.move(item_id, "attention", f"draft has {bad} unsupported claims (limit {cfg['max_unsupported_in_draft']})")
            return item_id, "attention"
        return item_id, "queue"
    except Exception as e:
        import traceback
        log(traceback.format_exc()[-2500:])
        store.move(item_id, "attention", f"drafting failed: {str(e)[:400]}")
        log(f"  -> attention: {str(e)[:300]}")
        return item_id, "attention"


def cmd_draft(topic=None, count=None):
    cfg = config()
    lane = cfg.get("lane") or os.environ.get("LANE") or None
    if topic:
        todo = [topic]
    else:
        if buffer_size() >= cfg["buffer_target"]:
            log(f"buffer full ({buffer_size()} >= {cfg['buffer_target']}); no new drafts tonight")
            return 0
        todo = topics_todo()[: count or cfg["drafts_per_run"]]
    if not todo:
        log("No new topics in topics.txt. Add ideas there.")
        return 0
    done = []
    for t in todo:
        try:
            done.append(draft_one(t, lane, cfg))
        except store.StoreError as e:
            log(f"skipped {t!r}: {e}")
        commit_and_push(f"Draft: {', '.join(i for i, _ in done) or 'none'}")
    return 0


# ---------------------------------------------------------------- polish gate (pull request)

PATH_RE = re.compile(r"^pipeline/queue/([0-9]{8}-[a-z0-9-]{1,60})/polished\.json$")

RUBRIC = """Rate this short-video script from 1 to 5 against the criteria, using the source material to judge accuracy.
5 = publish as is; 4 = good, minor nitpicks; 3 = accurate but flat; 2 = weak; 1 = wrong or broken.
CRITERIA:
{criteria}

SCRIPT:
{script}

{sources}
Return JSON only: {{"score": <1-5>, "reason": "<one sentence>"}}"""


def score(script, sources):
    from ailayer import ask
    from ailayer.skills import Source, sources_block, untrusted
    from .draft import JUDGE_CRITERIA
    srcs = [Source(s["url"], s["text"], s.get("title", "")) for s in sources]

    def v(d):
        return [] if isinstance(d, dict) and isinstance(d.get("score"), (int, float)) and 1 <= d["score"] <= 5 \
            else ['need {"score": 1-5, "reason": "..."}']
    r = ask(RUBRIC.format(criteria=JUDGE_CRITERIA, script=untrusted(json.dumps(script, ensure_ascii=False), "SCRIPT"),
                          sources=sources_block(srcs, " ".join(gates.narration(script)), 5000)),
            tier="critical", validate=v, temperature=0.1, max_tokens=400)
    return {"score": r.data["score"], "reason": str(r.data.get("reason", ""))[:300], "model": r.ref}


def gate_one(item_id, polished):
    """All post-polish gates for one script. Returns (ok, report)."""
    from ailayer.skills import Source, fact_check, judge
    from .draft import JUDGE_CRITERIA
    p = polish.packet(item_id)
    report = {"at": store.now(), "offline": polish.check(item_id, polished)}
    if report["offline"]:
        return False, report
    srcs = [Source(s["url"], s["text"], s.get("title", "")) for s in p["sources"]]
    fc = fact_check(" ".join(gates.narration(polished)), srcs)
    report["fact_check"] = {k: fc[k] for k in ("results", "counts", "model")}
    if fc["counts"]["unsupported"] or fc["counts"]["partial"]:
        report["offline"] = [f"fact check: {fc['counts']['unsupported']} unsupported, {fc['counts']['partial']} partial "
                             "claims: " + "; ".join(r["claim"] for r in fc["results"] if r["verdict"] != "supported")[:600]]
        return False, report
    j = judge([json.dumps(p["draft"], ensure_ascii=False), json.dumps(polished, ensure_ascii=False)],
              criteria=JUDGE_CRITERIA, task=f"Short video script: {p['item']['topic']}", sources=srcs)
    report["judge"] = j
    if j["index"] != 1:
        report["offline"] = [f"the judge preferred the draft over the polish: {j['reason']}"]
        return False, report
    report["score"] = score(polished, p["sources"])
    return True, report


def cmd_gate_pr(pr, author=None, head_ref=None):
    from . import github as gh
    cfg = config()
    if author and author not in cfg["owner_logins"]:
        gh.comment(pr, "Only the channel owner's polish runs are accepted. Closing.")
        gh.close_pr(pr)
        return 0
    git("fetch", "-q", "origin", f"pull/{pr}/head:pr-{pr}")
    changed = [l for l in git("diff", "--name-only", f"HEAD...pr-{pr}").splitlines() if l.strip()]
    bad_paths = [c for c in changed if not PATH_RE.match(c)]
    if not changed or bad_paths:
        gh.comment(pr, "Rejected: a polish pull request may only add `pipeline/queue/<id>/polished.json` files.\n"
                       f"Not allowed: {', '.join(bad_paths[:10]) or '(no files)'}")
        gh.close_pr(pr)
        return 1
    lines, accepted = [f"## Polish gate for #{pr}", ""], []
    for path in changed:
        item_id = PATH_RE.match(path).group(1)
        st, f = store.find(item_id)
        if st != "queue":
            lines.append(f"- `{item_id}`: skipped, it is not in the queue (now: {st})")
            continue
        try:
            polished = json.loads(git("show", f"pr-{pr}:{path}"))   # data only: PR code is never executed
        except Exception as e:
            ok, report = False, {"at": store.now(), "offline": [f"polished.json is not valid JSON: {str(e)[:120]}"]}
        else:
            ok, report = gate_one(item_id, polished)
        if ok:
            store.write_json(f / "polished.json", polished)
            store.write_json(f / "gate.json", report)
            store.move(item_id, "ready", f"polish accepted from PR #{pr} (score {report['score']['score']})")
            accepted.append(item_id)
            lines.append(f"- ✅ `{item_id}` accepted (score {report['score']['score']}/5: {report['score']['reason']})")
        else:
            fb = store.read_json(f / "feedback.json", [])
            fb.append({"at": store.now(), "pr": pr, "problems": report["offline"]})
            store.write_json(f / "feedback.json", fb)
            it = store.update(item_id, attempts=store.read_json(f / "item.json")["attempts"] + 1)
            lines.append(f"- ❌ `{item_id}` rejected: " + "; ".join(report["offline"])[:800])
            if it["attempts"] >= polish.MAX_ATTEMPTS:
                store.move(item_id, "attention", f"polish rejected {it['attempts']} times; last: {report['offline'][:2]}")
                lines.append(f"  moved to attention after {it['attempts']} attempts")
    commit_and_push(f"Polish gate for PR #{pr}: {len(accepted)} accepted")
    lines += ["", "Accepted scripts are in `pipeline/ready/` and are being rendered now. "
                  "Rejected ones stay in the queue with the reason in `feedback.json` for the next polish run.",
              "This pull request is closed by design: the gate copies accepted scripts to main itself."]
    gh.comment(pr, "\n".join(lines))
    gh.close_pr(pr)
    if head_ref and head_ref.startswith("claude/"):
        gh.delete_branch(head_ref)
    if accepted:
        gh.dispatch("pipeline-produce.yml")
    return 0


# ---------------------------------------------------------------- produce

def _issue_body(script, item_id, asset_url, release_url, gate):
    yt = script.get("youtube", {}) or {}
    title = yt.get("title") or script.get("title")
    desc = (yt.get("description") or "").strip()
    srcs = "\n".join(f"- {s['url']}" for s in script.get("sources", []))
    desc_full = f"{desc}\n\nSources:\n{srcs}\n\n#Shorts".strip()
    tags = ", ".join(yt.get("tags", []))
    fc = gate.get("fact_check", {}).get("counts", {})
    sc = gate.get("score", {})
    return f"""**Download the video:** [{Path(asset_url).name}]({asset_url})

### 1. Title (copy)
```
{title}
```
### 2. Description (copy)
```
{desc_full}
```
### 3. Tags (copy)
```
{tags}
```
### 4. When uploading
- YouTube asks whether the video has realistic altered or synthetic content. These are clearly animated
  explainers with a synthetic voice; check YouTube's current guidance when you answer.
- Audience: not made for kids (unless your channel is).

### Checks this video passed
- Fact check: {fc.get('supported', 0)} claims supported, {fc.get('partial', 0)} partial, {fc.get('unsupported', 0)} unsupported
- Quality score from the judge: {sc.get('score', '-')}/5 ({sc.get('reason', '')})
- Technical checks: all passed

[Release page]({release_url}) · item `{item_id}`

**After you upload it, close this issue.** That marks it published.
"""


def cmd_produce(limit=None):
    from .. import __main__ as studio_cli
    from ..paths import ensure_fonts, slugify, OUT
    from . import github as gh
    cfg = config()
    ensure_fonts()
    gh.ensure_label("ready-to-upload", "2da44e", "Finished video: download, upload to YouTube, then close")
    done = 0
    for item_id in store.items("ready")[: limit or cfg["produce_per_run"]]:
        f = store.folder("ready", item_id)
        script = store.read_json(f / "polished.json")
        gate = store.read_json(f / "gate.json", {})
        out = OUT / item_id
        out.mkdir(parents=True, exist_ok=True)
        fact = {"results": [{**r, "url": ""} for r in gate.get("fact_check", {}).get("results", [])], "problems": []}
        try:
            studio_cli.produce(json.loads(json.dumps(script)), out, fact, [])
            tech = store.read_json(out / "qc.json", {}).get("technical", {})
            if not tech.get("passed"):
                failed = [k for k, ok in tech.get("checks", {}).items() if not ok]
                store.move(item_id, "attention", f"render failed technical checks: {failed}")
                continue
            video = out / f"{slugify(script['title'])}.mp4"
            (out / "video.mp4").rename(video)
            rel, assets = gh.create_release(f"video-{item_id}", script["title"],
                                            f"Video for `{item_id}`. Topic: {script.get('topic', '')}",
                                            [video, out / "contact.png"])
            asset_url = next(a["browser_download_url"] for a in assets if a["name"].endswith(".mp4"))
            issue = gh.create_issue(f"Ready to upload: {script['title']}",
                                    _issue_body(script, item_id, asset_url, rel["html_url"], gate), ["ready-to-upload"])
            store.write_json(f / "video.json", {"at": store.now(), "release": rel["html_url"], "asset": asset_url,
                                                "issue": issue["number"], "technical": tech})
            store.move(item_id, "delivered", f"rendered; issue #{issue['number']}")
            done += 1
            log(f"[produce] {item_id} -> issue #{issue['number']}")
        except Exception as e:
            store.move(item_id, "attention", f"render or delivery failed: {str(e)[:400]}")
        commit_and_push(f"Produce: {item_id}")
    log(f"produced {done} video(s)")
    return 0


# ---------------------------------------------------------------- published

def cmd_published(issue):
    for item_id in store.items("delivered"):
        f = store.folder("delivered", item_id)
        v = store.read_json(f / "video.json", {})
        if v.get("issue") == issue:
            it = store.read_json(f / "item.json")
            store.move(item_id, "published", f"upload issue #{issue} closed")
            with open(store.ROOT / "topics-done.txt", "a", encoding="utf-8") as fh:
                fh.write(it["topic"] + "\n")
            commit_and_push(f"Published: {item_id}")
            return 0
    log(f"issue #{issue} is not a delivered video; nothing to do")
    return 0


# ---------------------------------------------------------------- status

def status_markdown():
    c = store.counts()
    lines = ["Rewritten automatically after every pipeline run. Don't edit; it gets replaced.", "",
             "| Stage | Count | What it means |", "| --- | --- | --- |",
             f"| Waiting for polish | {len(polish.waiting())} | Drafted and checked; the polish task picks these up |",
             f"| Ready to render | {c['ready']} | Polished and accepted; rendering next |",
             f"| Ready to upload | {c['delivered']} | Open issues labelled **ready-to-upload** |",
             f"| Published | {c['published']} | Done |",
             f"| Needs attention | {c['attention']} | Stopped with a reason (below) |", ""]
    days = len(polish.waiting()) + c["ready"] + c["delivered"]
    lines.append(f"**Buffer:** {days} video(s) in the pipeline (at 1 a day, about {days} day(s) of content).")
    att = store.items("attention")
    if att:
        lines += ["", "### Needs attention"]
        for i in att[-15:]:
            it = store.read_json(store.folder("attention", i) / "item.json", {})
            lines.append(f"- `{i}`: {it.get('history', [{}])[-1].get('why', '')[:300]}")
    lines += ["", f"_Updated {store.now()}_"]
    return "\n".join(lines)


def cmd_status():
    from . import github as gh
    gh.ensure_label("studio-status", "0969da", "The pinned studio status issue")
    body = status_markdown()
    found = gh.issues("studio-status")
    if found:
        gh.update_issue(found[0]["number"], body=body)
    else:
        n = gh.create_issue("Studio status", body, ["studio-status"])["number"]
        subprocess.run(["gh", "issue", "pin", str(n)], cwd=store.ROOT)
    log(body)
    return 0


# ---------------------------------------------------------------- upload (after Google's audit)

def cmd_upload(issue, privacy="public"):
    import urllib.request
    from . import github as gh, youtube
    if os.environ.get("YOUTUBE_UPLOADS_APPROVED", "").lower() != "true":
        gh.comment(issue, "Automatic upload isn't switched on yet (it waits for Google's API audit; until then "
                          "YouTube would lock the video as private). Upload it by hand, then close this issue.")
        return 0
    for item_id in store.items("delivered"):
        f = store.folder("delivered", item_id)
        v = store.read_json(f / "video.json", {})
        if v.get("issue") != issue:
            continue
        script = store.read_json(f / "polished.json")
        local = store.ROOT / "out" / f"{item_id}.mp4"
        local.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(v["asset"], timeout=300) as r:
            local.write_bytes(r.read())
        try:
            vid = youtube.upload(local, script, privacy)
        except youtube.YouTubeError as e:
            gh.comment(issue, f"Upload failed: {e}. Nothing was published; you can upload by hand.")
            return 1
        v["youtube"] = {"id": vid, "url": f"https://youtube.com/shorts/{vid}", "at": store.now(), "privacy": privacy}
        store.write_json(f / "video.json", v)
        it = store.read_json(f / "item.json")
        store.move(item_id, "published", f"uploaded to YouTube as {vid}")
        with open(store.ROOT / "topics-done.txt", "a", encoding="utf-8") as fh:
            fh.write(it["topic"] + "\n")
        commit_and_push(f"Uploaded: {item_id}")
        gh.comment(issue, f"Uploaded: https://youtube.com/shorts/{vid} ({privacy}). Closing this issue.")
        gh.update_issue(issue, state="closed")
        return 0
    gh.comment(issue, "This issue isn't a delivered video I can find; nothing uploaded.")
    return 1
