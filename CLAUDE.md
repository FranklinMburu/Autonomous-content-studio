# YouTube Creator Studio — instructions for any AI working in this repo

## What this repo is
The code of **YouTube Creator Studio** (also called Youtube-creator-system, YouTube Creator System,
Autonomous Content Studio). One system, many channels.

## Read first (Notion)
Projects table → **YouTube Creator Studio** → Project Control Centre. Also read its Drift Guard.
Channels are the **Sub-item** records of that page. They are parts of this project, never separate projects.

## Channels
| Code | Channel | Stage | Notion record |
|---|---|---|---|
| BS | Body Science (placeholder name) | Pilot | YouTube Creator Studio · Body Science |
| HR | Hidden Reasons (true stories behind history's strangest acts) | Film style Stage 1 (episode 002 film v2); scheduled pipeline built | YouTube Creator Studio · Hidden Reasons — True Stories Behind History's Strangest Acts (HR) |

Six more channels are ideas only (ranked in Notion); they have no code yet.

## Two video styles (see docs/STYLES.md)
- Explainer: `python -m studio ...` + the pipeline. Unchanged. Pre-story version kept on branch `v1.0-explainer` (frozen; never commit to it).
- Story: `python -m studio.story make episodes/<channel>/<NNN-slug>` or `write --topic "..."` (AI writes it). Each episode = script.json + storyboard.json (data, uses the library in studio/story/board.py) + sources.md.
  Scenes refer to words by occurrence (`L.wt("six", 2)`), never seconds. `tests/test_story.py` must pass.

Rules:
- Shared things (engine, gates, pipeline, rules, Toolbox) live once, here and on the parent page.
- A channel holds only what is different: niche, audience, voice, style, engine choice.
- The channel code is the same in Notion, in this repo (`channels/<code>/`, when built) and in video IDs.
- Channel results go on the channel's Notion page; system changes go on the parent page.
- Notion only states what is true in the code.

## Safety (Franklin's rules)
- Never open, print or copy `.env` or any secret. Keys live only in GitHub secrets.
- $0 only. Explain and ask before anything that could cost money, expose secrets, push to main, or publish.
- Commits use the no-reply email `184284364+FranklinMburu@users.noreply.github.com`.

## Where things are
- How the pipeline works: `docs/PIPELINE.md`. Polishing: `POLISH.md`. Handoff notes: `HANDOFF.md`.
- Engine experiments (Manim vs MoneyPrinterTurbo): branch `experiment-engines`, folder `experiments/engines/`.
- Story style: `studio/story/` (engine), `episodes/` (one folder per video), `docs/STYLES.md` (how to run, on GitHub or locally).
- Benchmark research raw notes: branch `experiment-engines`, folder `experiments/hidden_reasons/`.
