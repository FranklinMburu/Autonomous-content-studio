# Agent handbook: the whole studio in one page

For any AI agent (Codex, Claude, others) picking up this project. Read it once per session, then run
`python tools/sync_check.py` for the live state: **this file explains, the sync check proves.** If they disagree,
trust the sync check and the code, and tell Franklin which line of this file is out of date.

Last updated: 6 Nov 2026 (Claude). Update sections 4-6 whenever you change the system.

## 1. Goal and constraints

- **Goal:** YouTube channels people actually watch, made by a system that runs itself with minimal manual work.
  First channel: **Hidden Reasons (HR)**: 1-minute film-style Shorts about true stories where someone did something
  strange for a hidden reason. Target: **5 films a day**. (An older "explainer" style exists for Body Science (BS).)
- **$0 forever:** the repo is public (free Actions minutes), free AI tiers (Gemini/Gemma, Groq, NVIDIA through
  Franklin's private "brain" repo `FranklinMburu/AI-layer`), Kaggle's free weekly GPU hours, GitHub Pages.
- **Franklin decides; the system does the work.** He reviews videos, merges pull requests and uploads to YouTube.
  Nothing is published or uploaded without him.

## 2. How a film is made (Hidden Reasons)

```
Story clock ──(at each slot)──> Story schedule ──(guardrails ok)──> Make a story video
  story-clock.yml                 story-schedule.yml                  make-story.yml
  waits for x:23 UTC slots        picks the next topic                writes script + shot list (free models),
  0,5,10,17 and 21 UTC,           (episodes/hidden_reasons/topics.txt fact-checks against frozen sources,
  then restarts itself            minus what the channel memory       paints on Kaggle (lab.py), assembles
                                  says is done)                       (tools/film_produce.sh), publishes a
                                                                      GitHub Release
         │
         ├─ script not good enough ──> "polish" issue + ticket polish/film/<episode>/ ──> Claude/Codex/person
         │                             writes answer.json ──> polish-return.yml checks it ──> video made
         │
         └─ video made ──> all checks pass ──> release "Film: ..." + "Ready to upload" issue
                         └─ ≥3 shots fail the picture check ──> pre-release "REVIEW: ..." + "Review needed" issue
                            Franklin comments approve / repaint ──> review-reply.yml
```

- **Picture check** (`lab.py`): a small vision model (Qwen2-VL-2B) asks each shot's `check` question
  ("Is there a brick well?"), plus "any text?" and "anything modern?". A failed shot is repainted up to 2 more times;
  repaints put the checked thing first in the prompt. ≥3 shots still failing → held for review (`studio/story/film.py qc()`).
- **Channel memory:** release `channel-memory`, asset `used.json` = episodes made (topic, cast, places, music) +
  topic tries. `studio/story/topics.py` reads it to pick the next topic; `filmkit remember` adds a film after it's made.
- **Releases are the storage:** every run's video, contact sheet, `episode-files.zip` and `film-assets.zip`
  (pictures, `checks.json`, Kaggle `log.txt`). Tags: `film-<episode>-runN`, `draft-<episode>-runN`.

## 3. The other parts

- **Explainer pipeline** (`studio/pipeline/`, `docs/PIPELINE.md`): Pipeline 1 draft (nightly) → queue → "Polish the
  queue" (a Claude Code scheduled task, daily 12:43 Nairobi, follows `POLISH.md`, opens a PR with `polished.json`) →
  Pipeline 2 gate → Pipeline 3 produce → "Ready to upload" issue → Franklin uploads and closes it → Pipeline 4.
  If Claude doesn't polish for 72 h, the nightly run uses a free model as backup. 3 rejections → "needs attention".
- **Website "Candela Studio"** (`web/`, React 19 + TypeScript + Vite, only react/react-dom/@phosphor-icons):
  public at **https://franklinmburu.github.io/Autonomous-content-studio/**, published by `pages.yml` on every
  website change to main. No server: the browser reads `feed.json` (branch `site-data`, rebuilt by `site-feed.yml`
  every 30 min and after pipeline runs) or, if missing, the public GitHub API. Design spec: `design/` (copy it,
  don't invent). Rule: real data only, gold used only as a signal, ink background.
- **Issues used as the control panel:** `studio-status` (#4, rewritten each run), `pipeline-alert` (#15),
  `review`, `ready-to-upload`, `polish`, `polish-stalled`.

## 4. Current state (6 Nov 2026)

- Film schedule: the **Story clock** started 6 Nov; first slot 17:23 UTC. Before that GitHub's own timer fired the
  hourly schedule only ~2 times a day, so only 1-2 films a day started.
- Episodes: 002 (Semmelweis) finished; 003 (Lister) made 7 times, all held for review → keep **#16** (fewest weak
  shots), the others closed as duplicates; 004 (John Snow) polished by Claude through PR #25, video held for review
  (#29), repaint with the new method started 6 Nov 15:56 UTC.
- Explainers: 4 "Ready to upload" issues waiting for Franklin (#5, #8, #12, #31). Dogs topic can't be polished from
  its sources; it will go to "needs attention" after its next rejection.
- Website: live on GitHub Pages since 6 Nov. Feed working.

### Update 10 Nov 2026
- **9 polished films** (Jenner, Goldberger, Barry Marshall, Mary Mallon, Great Stink, Fleming, canaries, Radium
  Girls, Venice) were polished by Claude via PRs #63 and #69. Videos made: Jenner, Barry Marshall (old voice),
  Mary Mallon, Great Stink, Goldberger; the rest were in progress at 20:30 Nairobi time.
- **Story voice changed** (PR #71): `STORY_VOICE` in `studio/story/__main__.py` = Kokoro `af_heart` at 1.15x, gaps
  0.22/0.42 s, line-end silence trimmed (Franklin's pick "E"). The old voice (`am_michael` at 1.38-1.6x) rated 5/10.
- Issues: a passed polish is renamed **"Polished, making the video: …"** with label `polished` (PR #66); duplicate
  polish issues are closed automatically.
- Reference videos and the per-style gap report: Notion "Reference videos: gap report (10 Nov 2026)".

### Update 11 Nov 2026
- **Third style: motion engine for Tech Education (TE)** (`studio/motion/`, `docs/MOTION_ENGINE.md`). Built in the lab
  v1 -> v3 against a measured quality bar, then generalised: script.json + plan.json (one scene per line from 22 scene
  types) -> deterministic render in headless Chromium. Manual workflow "Make a motion video (Tech Education)" only;
  isolated from Hidden Reasons (own concurrency group, no Kaggle, no memory; `tests/test_motion.py` checks the isolation).
- TE voice locked by Franklin: Kokoro `am_fenrir` 1.0 + gentle EQ (`channels/te/channel.json`). Rejected: voice
  blends, pitch shifting, echo.

## 5. Decisions and incidents (why things are the way they are)

| Date | What happened | Cause (evidence) | Fix |
|---|---|---|---|
| 2-6 Nov | Story schedule failed 9/9 runs | `pycairo` needs `libcairo2-dev` (run logs) | installed in workflows; test in `test_workflows.py` |
| 2-6 Nov | Polish stalled, drafts at risk | Claude away; no backup agent | `polish/film/` tickets + `polish/README.md` so Codex/anyone can polish; drafts archived in `polish/archive/` |
| 6 Nov | Fact check rejected the required "You see," comparison | it was fact-checked like a claim | `factual_text()` in `studio/story/writer.py` skips it |
| 6 Nov | Only ~2 of 5 films a day | GitHub ran `23 * * * *` only twice a day (run history) | `story-clock.yml` (self-chaining, free, oldest run wins) |
| 6 Nov | Every film held for review | repaints reused the same prompt with a new seed (John Snow run2: 11/36 failed 3×, e.g. "brick well" painted as boots) | repaints focus on the checked thing; checker asks twice; storyboard rules avoid unpaintable shots |
| 6 Nov | Lister made 7 times | `film_produce.sh` uploaded a 45-min-old `used.json`, erasing the schedule's topic tries | re-download the memory right before `remember` |
| 6 Nov | "Polish stalled" never closed | failed backup polishes weren't counted as attempts | counted in `studio/pipeline/run.py`; 3 → attention |
| 6 Nov | Website showed invented data, white scrollbars, stutter | AI Studio build | rewritten to real data only; `earth.js` v2 globe; see PR #27 |
| 10 Nov | Goldberger video failed at once | Kaggle allows **2 GPU sessions**; two Earth-film renders held both | `lab/kaggle/run.py` waits up to 90 min for a free slot (#64) |
| 10 Nov | A made video lost the next answer in the batch | ffmpeg/gh read stdin = `jobs.tsv` in the polish loop | `< /dev/null` + `-` for empty fields (#70), loop test in `test_workflows.py` |
| 10 Nov | True facts flagged "not supported" | the fact check saw only 6,000 chars per source, picked for the whole script | AI-layer #3: `claim_excerpt()` gives each claim its passage |
| 10 Nov | Pipeline save crashed: `Committer identity unknown` | the rebase retry had no git identity (found by Codex) | identity for commit and rebase (#65) + `tests/test_git_identity.py` |
| 10 Nov | Tests hung 10 min | apt mirror stall in the test workflow, tests twice per push | apt 3-min timeout + retry, man-db/needrestart off, push runs only on main (#65) |
| 10 Nov | Films sounded rushed | voice forced to 1.38-1.6x with 0.08/0.2 s gaps | `STORY_VOICE` (#71); voice lab re-baselined (#76) |

## 6. Known issues and open questions (verify before acting)

- Whether the repaint changes lower the picture-check failure rate is **not proven yet**: compare the next films'
  `checks.json` ("check round N: X of Y pass" in `log.txt`) with John Snow run2 (11 of 36 failed).
- The picture checker is a 2B model: it sometimes says "no" to things that are clearly there (beer mugs). A second
  question now guards against that. Don't loosen the threshold without Franklin.
- The 6-hourly fallback timer of the clock depends on GitHub's unreliable timer; the chain itself doesn't.
- Kaggle GPU: 30 h/week. One film ≈ 45 min of GPU; the schedule caps at 36 films/week.
- YouTube upload (Pipeline 6) is off until Google's audit (`docs/YOUTUBE_SETUP.md`). Franklin uploads by hand.
- Kaggle runs at most **2 GPU sessions** at once: films and labs share them; runs wait for a slot (#64).
- Kokoro says some phrases fast ("at health officials") even at 1.0x: the model's rhythm. Idea for later: detect words
  spoken much faster than their neighbours and re-read that line.
- AI-layer #2 logs the start of every rejected model answer: read it before blaming a provider for "invalid output".
- Speech-to-text model downloads (Hugging Face) are blocked in Claude's sandbox and on Franklin's linked computer; run
  transcription on GitHub Actions.
