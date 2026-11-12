# Mission: become a better clipper than the best humans (Clipping Engine, prompt v4, 13 Nov 2026)

Read first: `docs/clips/DECISIONS.md` (also the project doc `claude/CLIPS_DECISIONS.md`). It's the history of every
decision. This prompt builds on it.

## 0. The goal, in one line

**Produce Shorts from real live streams that have the highest possible probability of reaching the top-10% views of
the best clip channels (≥ 250K), and package them so Franklin can upload them.** Everything else serves this. Views
can't be guaranteed; it's a game of probability, and the highest probability wins. Aim for 9.5–9.8 out of 10 on every
part.

## 1. Why we can beat human clippers

Human clippers win on **intuition**: they've watched so much that they *feel* "this will blow up". They lose on
**stamina and coverage**: they get tired, skip parts of a 6-hour stream, watch one stream at a time and post late.

We win by doing both:
- **Build the intuition from data.** Study what actually went viral (thousands of real Shorts with view counts) until
  the engine knows *why* a moment works.
- **Never get tired.** Watch, hear and read every second of every stream, several streams at once, and be first to
  post.

## 2. The bar (real, measured)

- **@Kick_Clippers** (`UCIPD8q8n3Vy7Qfz59RTc1Jg`): 3,392 Shorts; median 21K; top 10% ≥ 248K; best 32M.
- **Clipatra** (`UCxlQSBBswmNP-wFDkcFrDBw`): 4,046 Shorts; best 7.8M.
- Top examples, with links, are in `docs/clips/REFERENCE_kick_clippers.md` and `docs/clips/DECISIONS.md`.
- Winning moments: IRL and celebrity encounters; someone shocked, exposed, humbled or caught; relationship drama;
  emotion; money and flex.
- Title formula: "The moment / No way [streamer] [REALIZED / was SHOCKED / EXPOSED] [situation] 😳😭💔 #streamer".

## 3. How to think (not a checklist; use your full judgement)

Go deep where it raises the probability; keep it simple where it doesn't. Before any piece of work, ask:
**"Does this raise the chance that a clip we post reaches 250K+ views?"** If not, don't do it.

1. **Learn the intuition.**
   - Mine both reference channels completely (titles, views, length, dates; public lists work from GitHub through
     `clips-reference.yml`).
   - Build a **viral-moment taxonomy**: kinds of moment, who's in them, the emotional trigger, the title pattern.
     Weight each kind by real views.
   - Find **what separates the top 10% from the median** of the *same* channel and streamer.
   - Turn this into the judge's rubric, with the strongest real examples as few-shot references.
2. **Choose the right streams.**
   - Choosing the stream matters as much as choosing the moment. Track which streamers and events are hot *right now*:
     their newest uploads on the reference channels, the top viewer clips on Twitch and Kick this week, and live
     campaigns.
   - Freshness wins: clip a big stream within hours of it ending.
3. **Watch every second, cheaply.** Never download whole streams.
   - **See:** the whole stream at low quality, read by a vision AI (Gemini through the brain at about 70 tokens per
     frame, or an open vision model on Kaggle's free GPU).
   - **Hear:** the transcript plus laughter, screams, sudden silence, music drops.
   - **Read the crowd:** chat spikes and the viewers' own clips with views (strong, but never the only signal).
   - **Judge like a top clipper:** an AI reviews every candidate with the full context and the rubric, and writes
     *why* it will or won't work.
   - **Then download in high quality only the winning sections,** with their setup and context.

   Already tested from GitHub: Twitch works fully (sections, audio-only, viewer clips); Kick works (API, clips);
   YouTube video is blocked, so YouTube sources go through Franklin's laptop runner, small sections only.
4. **Prove the intelligence before polishing anything.**
   - Run a **recall test** on real streams: ground truth is the fans' top clips (exact timestamps) and the hits on the
     reference channels.
   - Compare each signal alone with all of them together. **Bar:** about 9 of 10 real hits found in our top
     candidates, *and* new finds Franklin rates as strong.
   - Show him the table and 2–3 real moments. If it misses, find out what kind of moment and why, fix it, and re-test.
5. **Make each Short the way the winners do.** Measure the reference Shorts, don't guess:
   - payoff in the first second;
   - framing of streamer and guest;
   - caption font, size, place and colour;
   - cut rate and zooms;
   - sound;
   - length;
   - ending or loop;
   - title, description and hashtags.

   Each clip must also be clearly *ours*: hook, captions and edit add real value. YouTube favours original,
   transformed content; plain re-uploads get pushed down.
6. **Package for upload.** The first real product is a button: paste a stream link (or let it pick a hot stream), and
   get back finished Shorts, each with:
   - its title, description and hashtags;
   - a predicted view band and why;
   - a "before you post" note: the streamer's clipping status, campaign rules, and risks.

   Franklin uploads at first. Automatic upload comes later, with his yes.

## 4. Rate yourself, always, and be honest

After every round, score every finished clip and the whole system 0–10 on:
- moment strength;
- hook in the first second;
- title;
- framing and visual quality;
- captions;
- audio;
- pacing and cuts;
- length and ending;
- originality;
- overall: the predicted chance of reaching 250K+.

Scoring rules:
- Scores come from comparison with the real winners: blind side-by-side against reference Shorts, judged by a judge
  that didn't make the clip (the brain's `judge` on GitHub Actions, or a separate agent).
- **Any part under 9.5 is the next thing to improve.** Fix the *engine* (not one clip), remake, re-score. Keep going.
- Log each round in `docs/clips/PROGRESS.md`: scores, what changed, and the best real clip.
- Never inflate. If something is a 4, say 4 and fix it.

## 5. Guards against drifting (these caused the failure of v1)

Stop and correct course if you notice any of these:
- working on fake or test footage as if it were the product;
- polishing tools or infrastructure while no real clip exists;
- research or reports with no clip or measurement at the end;
- a score that isn't from a real comparison;
- a long run without showing Franklin something real.

**Every update to Franklin has a real clip or real numbers.**

## 6. The only fixed lines

1. $0. One account per provider.
2. Never Franklin's passwords, login cookies or `.env`. Keys only in GitHub secrets.
3. Nothing published, uploaded or merged to main without Franklin's yes. Work branches, PRs and GitHub releases for
   review are fine.
4. Nothing fake shown as a clip.

Everything else, including rights and campaign rules, is handled in the "before you post" note, not as a block.

## 7. Where things are

- Branch `clips-engine` (PR #100), worktree `/home/claude/clips-engine`.
- `studio/clips/` (finder, editor, gates, judge), `tests/test_clips.py`.
- Workflows: `make-clips.yml` (VOD link → clips; test runs through `clips-run/*` branches), `clips-reference.yml`
  (channel lists), `clips-probe.yml` (reachability tests).
- Repo rules: `CLAUDE.md`. Commits as `Franklin Mburu <184284364+FranklinMburu@users.noreply.github.com>`, ending
  with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. PRs through `gh api`. Never commit
  `polish/film/004-…/answer.json`.

## 8. Report

- Short, plain, often.
- Each update has a real clip or real numbers, the current self-scores, what changed, what's next, and any blocker
  with its workaround and exactly what Franklin could do.
- At the end: the PR, the button, how to use it, and the best clips with their scores.
