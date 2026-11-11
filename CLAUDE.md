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
| TE | Tech Education (working name; series "Build Basics") | Motion engine approved in the lab 11 Nov 2026 (v3); integrated, manual runs only | YouTube Creator Studio · Tech Education |

Six more channels are ideas only (ranked in Notion); they have no code yet.

## Three video styles (see docs/STYLES.md)
- Explainer: `python -m studio ...` + the pipeline. Unchanged. Pre-story version kept on branch `v1.0-explainer` (frozen; never commit to it).
- Story: `python -m studio.story make episodes/<channel>/<NNN-slug>` or `write --topic "..."` (AI writes it). Each episode = script.json + storyboard.json (data, uses the library in studio/story/board.py) + sources.md.
  Scenes refer to words by occurrence (`L.wt("six", 2)`), never seconds. `tests/test_story.py` must pass.
- Motion (Tech Education): `python -m studio.motion make episodes/tech_education/<NNN-slug>` or `write --topic "..."`.
  Each episode = script.json + plan.json (one scene per line from `studio/motion/plan.py` TYPES) + sources.md.
  Isolated from Hidden Reasons; the method, architecture and history are in `docs/MOTION_ENGINE.md`. `tests/test_motion.py` must pass.
  The TE voice is locked in `channels/te/channel.json` (Franklin, 11 Nov): never blend voices, pitch-shift or add echo.

Rules:
- Shared things (engine, gates, pipeline, rules, Toolbox) live once, here and on the parent page.
- A channel holds only what is different: niche, audience, voice, style, engine choice.
- The channel code is the same in Notion, in this repo (`channels/<code>/`, when built) and in video IDs.
- Channel results go on the channel's Notion page; system changes go on the parent page.
- Notion only states what is true in the code.

## Safety (Franklin's rules)
- Never open, print or copy `.env` or any secret. Keys live only in GitHub secrets.
- $0 only. Explain and ask before anything that could cost money, expose secrets, push to main, or publish.
- Commits use the no-reply email `184284364+FranklinMburu@users.noreply.github.com` as author (in Claude's sandbox the
  committer is `noreply@anthropic.com` so GitHub can verify the signature).

## Polish (any agent)
- Every unfinished film draft is a ticket in `polish/film/<episode>/`; the method, examples and commands are in
  `polish/README.md` (also for Codex via `AGENTS.md`). Deliver only `answer.json`; the pipeline checks and continues.

## Where things are
- Start of every session: `python tools/sync_check.py` (live state) and `docs/AGENT_HANDBOOK.md` (whole system, decisions). How the pipeline works: `docs/PIPELINE.md`. Polishing: `POLISH.md`. Handoff notes: `HANDOFF.md`.
- Engine experiments (Manim vs MoneyPrinterTurbo): branch `experiment-engines`, folder `experiments/engines/`.
- Story style: `studio/story/` (engine), `episodes/` (one folder per video), `docs/STYLES.md` (how to run, on GitHub or locally).
- Benchmark research raw notes: branch `experiment-engines`, folder `experiments/hidden_reasons/`.
