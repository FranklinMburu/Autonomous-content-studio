# Clipping engine: live streams → finished Shorts

Takes a long stream recording (3-6 h; Kick, Twitch, YouTube Live or our own) that we are **allowed** to clip. Finds
the moments most likely to work, and makes each one a finished 1080×1920 Short with:
- a hook in the first second;
- a layout that fits the content;
- word-by-word captions;
- framing changes and punch-ins;
- Shorts loudness;
- a title and a description that says where the clip is from.

Every clip is described by a data file (`clip.json`) and checked by gates. A clip that fails a gate becomes a REVIEW
pre-release plus a `review-clips` issue, never a finished release.

- Code: `studio/clips/`.
- Research and evidence: `docs/clips/RESEARCH.md`.
- Questions only Franklin can answer: `docs/clips/QUESTIONS_FOR_FRANKLIN.md`.

## 1. The method (the same as the motion engine's)

1. **Measure the references, write a quality bar.** Fourteen real clip-style Shorts were measured with
   `python -m studio.clips measure`. The numbers are in `studio/clips/bar.json`, each with its evidence (`_why`).
2. **Lab first.** We made two streams of our own (`lab/clips/`), a game stream and a two-host talk stream, each with:
   - long dull stretches and real moments;
   - a live chat that reacts late;
   - a bot-spam decoy;
   - donation alerts and viewer clips.

   The engine is never told where the moments are. A separate `truth.json` scores the finder.
3. **Lock what Franklin approves.** Nothing is locked yet: there is no real stream and no Franklin verdict.
4. **Data, not guesses.** One `clip.json` per clip; the renderer draws that file and nothing else. The same inputs
   give the same frames (tested).
5. **Integrate in isolation, with guardrails:**
   - own folder and own workflow (`make-clips.yml`, concurrency group `make-clips`);
   - own cache key (`clips-whisper-*`) and own review label (`review-clips`);
   - nothing else imports it, and it imports no other engine (`tests/test_clips.py`).

## 2. Architecture

```
<stream folder>/                       input; the engine never downloads anything
  stream.mp4    rights.json (REQUIRED)    chat.json | chat.csv    clips.json (viewer clips)    words.json (cached)

studio/clips/
  sources.py    ingest + rights check; chat readers: TwitchDownloader, chat-downloader, Kick export, CSV
  transcribe.py faster-whisper (MIT), int8 CPU, word times -> words.json (on GitHub Actions)
  signals.py    one streaming pass each over audio and picture -> per-second curves; chat curves; chat lag
                measured per stream; viewer-clip coverage; reaction words
  moments.py    score(t) = weighted robust z-scores (bar.json signal_weights) -> peaks -> payoff point ->
                setup walk-back on one thread (shared words, story markers, no long pause) -> end on the reaction
                -> rank: the brain (critical tier, rubric from bar.json, must say WHY) or the heuristic fallback
  layout.py     facecam box (straight edges that never move), faces (OpenCV Haar), people (motion regions)
                -> stack | split2 | speaker | letterbox, plus where the action is
  edit.py       clip.json: edit list (dead air > 0.6 s cut, never within 3 s of the payoff), cold open when the
                payoff is > 9 s in, hook text, 1-3 word captions, framing cuts and punch-ins, title, description
                (source + rights + #ad when a program requires it)
  render.py     numpy + Pillow per frame -> ffmpeg (x264, 30 fps); stream audio + 8 ms crossfades + whoosh,
                two-pass loudnorm to -14 LUFS / -1.5 dBTP; `stills` for quick looks
  gates.py      rights, hook <= 1 s, duration, captions in sync and visible, no black/frozen, loudness,
                subject in frame, text outside the Shorts UI, pace >= the references' median
  measure.py    the numbers for any short (ours or a reference): the bar, the gates and the judge all use it
  judge.py      blind scorecard: measured craft scores + the brain scoring ours mixed with real clips, unlabelled
  dataset.py    the winners-vs-baseline collector + statistics (YouTube Data API; needs a key)
  bar.json      the quality bar and every tunable number, each with its evidence
  __main__.py   find | make | render | stills | check | measure | judge
```

## 3. How to run

```
python -m studio.clips find    streams/<name> --top 6        # ranked clip.json files in out/clips/<name>/
python -m studio.clips stills  out/clips/<name>/01-*/clip.json   # quick look
python -m studio.clips make    streams/<name> --top 6        # + video.mp4 + report.json per clip
python -m studio.clips judge   out/clips/<name> <folder of reference .mp4>
python tests/test_clips.py
```

On GitHub: **Actions → "Make clips (live streams)"**. Give a stream folder in the repo, or the name of a release
`clips-src-<name>` holding `stream.zip`. You get one release per clip, or "REVIEW: …" plus an issue if a gate failed.

**Lab streams** (our own):

```
ACS_CACHE=<cache with Kokoro> python lab/clips/make_stream.py neon_dash out/lab_streams
```

## 4. Determinism and guardrails

- **No clock and no randomness at render time.** Frame counts and audio lengths are exact. We don't use
  `-shortest`: it was racy with piped frames, and the last 7 frames differed between runs on 12 Nov. x264 uses sliced
  threads: frame threads gave different output on 1 encode in 3 in our test, slices never did. A test renders twice and compares the frames.
- **Rights first.** Without `rights.json` of an allowed kind, nothing is made:
  - `own`;
  - `program`, which needs the program name and its terms link;
  - `permission`, which needs who granted it and proof;
  - `licence`, which needs the licence and proof.

  The workflow checks this before anything else.
- **The line never dies.** If the brain is unavailable, ranking falls back to the signals and hooks come from the
  transcript (never invented words). If OpenCV has no face detector, layout falls back to overlay and motion
  detection.
- **Gates** are listed in section 2. Any failure → pre-release "REVIEW: …" + a `review-clips` issue.
- **Isolation.**
  - It does not import `studio.story`, `studio.motion` or `studio.pipeline`.
  - Nothing outside imports it.
  - Its workflow is manual only, has its own concurrency group, no Kaggle and no channel memory.
  - Shared and read-only: `studio/paths.py` and the fonts. The lab script (not the engine) uses `studio/voice.py`
    to make the test streams.

## 5. History

| Round | What changed | Result |
|---|---|---|
| r1 (12 Nov) | first end-to-end: signals → moments → stack layout → render | top 4 of 5 found on the game stream. Facecam box wrong (found the lamp, not the cam); game crop cut the player off; captions over game text; hook covered the face; setup started in unrelated chatter |
| r2 | facecam found from straight edges that never move; game kept at 77% width on a blurred fill; captions on the seam; hook placed per layout; payoff = loudest reaction near the score peak; setup = one thread (shared words, story markers); chat lag by voting on burst starts | see `docs/clips/ITERATIONS.md` |

## 6. Known limits / next steps

- **No real stream yet.** Everything is proven on our own two lab streams: cartoon avatars and TTS voices. A blind
  judge will not rate those like real streamer clips (`ITERATIONS.md`). First real proof: a stream from a program
  Franklin joins.
- **The brain is text-only.** The AI judge reads transcripts and measured numbers, not pictures. A vision judge
  would need a free vision model (e.g. Gemini through the brain, if the brain gains image input).
- **The heuristic hook** is a shortened setup sentence. The brain writes better ones. Compare both on the first
  real stream.
- **Signal weights** are priors from the literature until the dataset (RESEARCH section 6) or real outcomes refit
  them.
- Haar face detection is weak on side views. MediaPipe's face detector (Apache-2.0) is the next step if real
  facecams are missed.
