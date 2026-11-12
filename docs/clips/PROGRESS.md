# Clipping engine: progress (plain language)

Updated after every round. Clips to watch: `out/samples/` (each with `video.mp4`, `clip.json` and `report.json`),
plus `out/samples/scorecard_rN.md`.

## Where we are: round 4 done, round 5 next (12 Nov 2026)

- **Source.** Two test streams the lab made itself (we own them), because we have no permitted real stream yet:
  - a 9-minute game stream: a cartoon streamer, a TTS voice and a live chat;
  - a 7-minute two-host talk stream.
- **Finding moments.**
  - Talk stream: all 4 real moments in the top 4.
  - Game stream: 4 of 5 in the top 5.
  - The chat-spam decoy (`!enter` giveaway) was never picked.
- **Clips made in round 4:** 6.
  - 4 passed every gate.
  - 2 went to REVIEW: one had too few cuts; one had captions that OCR read on only 41% of frames.

## Scores

**There are no blind AI-judge scores yet.** The blind judge (our clips mixed with real top clips, scored by the brain)
needs the brain, which runs only on GitHub Actions. It also needs real clips with transcripts.

What we have is the **measured craft score**: numbers from the files, compared with 14 real reference clips. It covers
hook timing, pace, captions, sound and duration only; it does not judge content.

| clip | hook timing | pace | captions | sound | duration | mean |
|---|---|---|---|---|---|---|
| talk 01 "YOUR LAST SEARCH WAS..." | 10 | 10 | 10 | 10 | 9 | 9.8 |
| talk 02 "IS A HOT DOG A SANDWICH?" | 10 | 10 | 9 | 9 | 10 | 9.7 (REVIEW: captions visible) |
| talk 03 "8 MINUTES OH NO" | 10 | 10 | 10 | 10 | 10 | 9.9 |
| game 01 "1 LIFE LEFT, LOW HEALTH..." | 10 | 10 | 8 | 10 | 10 | 9.7 |
| game 02 "I HAVE NEVER BEATEN LEVEL 9 40..." | 10 | 8 | 10 | 9 | 10 | 9.4 |
| game 03 "I NEED TO TELL YOU SOMETHING..." | 10 | 6 | 8 | 10 | 10 | 8.9 (REVIEW: pace) |

**Honest read.** The format matches the references: text and speech from the first second, about -14 LUFS, 1-3
caption words, cuts every few seconds. The content does not. Cartoon faces and TTS voices would not pass a blind
comparison with real streamer clips, and we will not claim the 9.4 bar until real streams and the blind judge say so.

## What changed last (round 4)

- **Shots.** Every sentence alternates "wide" (facecam over game, or both hosts) and "focus" (big facecam, or the
  host who is talking), so there is a real cut about every 3-4 s. The payoff is always on focus.
- **Sound.** A peak limiter runs before loudness normalisation. The crash sound had stopped one clip reaching
  -14 LUFS.
- **Hooks.** Hooks are cleaner: filler words ("okay", "chat") are dropped and whole phrases kept. They still come
  only from the transcript.
- **Captions.** They follow the seam when the shot changes, so they never cover the face.

## Next (round 5, running now)

- **Shot length.** No shot longer than 3.8 s. This fixes the low-pace REVIEW.
- **Talk-stream close-ups.** Wider (they were too tight and blurry), with better detection of who is talking.
- **Repeatable renders.** The video encoder could give different output on 1 run in 3. Fixed with sliced threads;
  the test now checks it.
- Then: render round 5, score it, and update this page and `out/samples/`.

## Waiting on Franklin

See `QUESTIONS_FOR_FRANKLIN.md`:
- a free YouTube API key, for the 60 + 60 dataset;
- a stream we are allowed to clip;
- a Twitch developer app (optional);
- the Notion page;
- merging PR #100.
