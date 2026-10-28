# The trusted pipeline

Topic → research → grounded draft → gates → polish → gates → render → "Ready to upload" issue → published.
Full design and reasoning: the "Content Studio — End-to-End System Plan" doc.

## What you do

1. Keep ideas in `topics.txt` (one per line).
2. When a "Ready to upload: …" issue arrives, download the video from it, upload it in the YouTube app with the
   copy-ready title, description and tags, then **close the issue**.
3. Glance at the pinned **Studio status** issue now and then. It lists anything that needs attention, with the reason.

Optional: tap **Run now** on the "Polish the queue" scheduled task at claude.ai/code to polish sooner.

## What runs by itself

| Workflow | When | What |
| --- | --- | --- |
| Pipeline 1: draft | nightly 03:13 Nairobi | Research (Wikipedia + OpenAlex), free-model drafts, gates, fact check → `pipeline/queue/` |
| "Polish the queue" (Claude Code scheduled task) | every morning | Follows `POLISH.md`; opens a pull request with `polished.json` files only |
| Pipeline 2: polish gate | on that pull request | Gates + fact check + judge; accepted → `pipeline/ready/`; rejected → reason in `feedback.json`; PR closed |
| Pipeline 3: produce | after the gate, and daily | Render + technical checks → GitHub Release + "Ready to upload" issue → `pipeline/delivered/` |
| Pipeline 4: published | when you close an upload issue | → `pipeline/published/`, topic marked done |
| Pipeline 5: weekly quality test | Mondays | 3 fixed topics drafted and scored against a baseline; a drop opens a "Quality alert" issue |
| Pipeline 6: upload | label `approve-publish` on an upload issue | Off until Google's audit; see `YOUTUBE_SETUP.md` |

## Where things are

- `pipeline/<stage>/<id>/`: one folder per video idea, with frozen sources, draft, checks, polish, gate results,
  video links and the history of every move. Stages: queue, ready, delivered, published, attention.
- `pipeline/config.json`: buffer size, drafts per night, models used for drafting.
- `POLISH.md`: the polish rules (change them only through a pull request).
- `studio/pipeline/`: the code. Offline tests: `python tests/test_pipeline.py`.

## Rules the code enforces

- Facts only from frozen sources; no number, name or link that isn't in them.
- Icons only from the list offered to the writer (unknown icons fail instead of being swapped).
- Hook ≤ 14 words; 85–140 words; a complete final sentence; no banned phrases; no near-duplicates.
- After polish: zero unsupported or partial claims, no new facts vs the draft, and the judge must prefer the polish.
- Only the owner's pull requests are gated, and only `polished.json` files may change; PR code is never run.
