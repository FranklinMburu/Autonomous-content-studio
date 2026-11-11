# Motion engine: the Tech Education style

Faceless 45–75 s explainers built from real-looking software in a moving 3D world:
- a laptop and app windows;
- a server and a diagram that grows line by line;
- word-by-word captions and a camera that never stands still;
- music and sound effects composed in code.

Channel: **Tech Education (TE)**, series "Build Basics". Code: `studio/motion/`. Approved 11 Nov 2026 (lab v3).

This page is also the **method** for reaching any new reference style. Section 1 is the method, section 2 is how it
went for this style, and sections 3–7 are the engine.

## 1. The method (reuse it for every new style)

1. **The reference is a quality floor, not a template.** Never recreate the video. Make different videos at least as
   good (Franklin, 11 Nov 2026).
2. **Measure the reference, don't eyeball it.** Take frames every 0.5 s, read the captions with OCR as the script, and
   measure:
   - colours and caption position;
   - loudness (ebur128) and voice pitch;
   - music tempo and tone balance;
   - motion (average frame difference, and the share of frames that are almost still).

   Write the numbers down as a **quality bar** (Notion, on the channel's page).
3. **Lab first, pipeline second.** Build the style in a scratch folder with nothing connected to the pipeline.
   Iterate: render, measure against the bar, show Franklin, fix. Each version gets a number and a verdict.
4. **Lock what Franklin approves** (here: the voice) in a file the pipeline reads. Write down what was rejected so no
   agent tries it again.
5. **Generalise the lab version into data.** The video is described by files (script + plan); the engine draws any
   valid plan. The AI writes the files, a validator checks them, and the engine never guesses.
6. **Integrate in isolation:**
   - own folder, own workflow and concurrency group, own tests;
   - nothing shared changes;
   - a guardrail at every step: a fallback plan, a review flag, and a pre-release instead of a finished release.

## 2. How this style was reached (11 Nov 2026)

Reference: "Vibe Coding Essentials, Part 2: What actually is GitHub" (54.7 s, 720×1280, 30 fps).

**Measured:**
- about 140 words at about 155 wpm;
- male voice, pitch about 140 Hz;
- −14.1 LUFS, loudness range 2 LU;
- music bed about 100 BPM;
- near-black background, one accent colour;
- captions near the top, 18–25% down the frame;
- one running example and one growing diagram;
- 8% of frames almost still.

| Version | What it was | Verdict | Frames almost still |
|---|---|---|---|
| v1 | flat HTML scenes, a slight 3D sway, Kokoro `am_michael`, a library music track | "looks like a template": no camera movement, no animation; voice and music rejected ("trash") | 42% |
| v2 | a real 3D world (CSS 3D) with an orbit camera, springs, typing and counters; music and sound effects synthesised in code | big step; "not there yet" | 4% |
| v3 | v2 + lit grid floors under every scene, a 3D laptop and a server rack, hard cuts to new angles, the locked voice | accepted as the standard; integrate next | 1% |

**Voice lock:** Kokoro `am_fenrir` at 1.0, read line by line, then only a gentle EQ (more bass, a softer top).

Rejected: blending in a second voice, pitch shifting, room echo and `am_puck`. Together they "sound like two stacked
voices" or "soprano". A more human voice needs a bigger model on Kaggle (Chatterbox, MIT; Dia2, Apache 2.0); that
hasn't been done yet.

**Still below the reference:** average motion is about half (2.9 against 5.5). The reference changes scene almost
every second.

## 3. Architecture

```
episodes/tech_education/<NNN-slug>/       data only
  script.json   beats -> lines, key_words, display ("dot env" -> ".env"), claims
  plan.json     {"seed": N, "scenes": [{"line": i, "type": "<scene type>", "p": {...}}]}, one per line
  sources.md

channels/te/channel.json                 what is different about this channel:
                                         voice lock, accent palette, music range, series name

studio/motion/
  plan.py       the contract: TYPES (22 scene types + their fields), validate(), variety(), auto_plan()
  style.py      seed -> accent, camera direction and drift, music key and tempo (same seed, same look)
  narrate.py    the locked voice: shared Kokoro word timing (studio/voice.py) + the approved EQ
  web/engine.html
                the engine: init(data) builds the world from the plan, render(t) draws one frame;
                it also returns the sound cues and the music sections
  render.js     headless Chromium (Playwright, pinned): steps t frame by frame -> ffmpeg; also --stills and --cues
  sound.py      the music bed + 13 effects, synthesised; mix() ducks music under the voice, -14 LUFS
  writer.py     topic -> research -> script + plan (the AI picks a scene per line) -> fact check -> folder
  __main__.py   check | stills | make | write
```

**How a frame is made:**
1. Every scene starts on its line and is anchored to spoken words (`"word": "address"`).
2. Scenes live in sets (hook, stat, story, wall, cta, end). Each set has its own place in the world, and the camera
   flies between them.
3. The story set grows: laptop → app → server and link → packets, cards, key, leak, badges.
4. The camera is keyframed per scene type, with hard cuts for close-ups, plus a slow seeded handheld drift.

## 4. Determinism and guardrails

- **No clock, no randomness at render time.**
  - Time is stepped by `render.js`.
  - All variation comes from the seed: `plan.seed`, or a hash of the folder name.
  - Pinned Chromium, fonts and Playwright (`package-lock.json`).
  - `tests/test_motion.py` renders the same frames twice. Chromium's blur may change a few pixels (at most 0.5%,
    measured 0.2%); the picture may not.
- **Guardrails, so the line never dies and nothing bad is published:**
  1. An invalid plan becomes `auto_plan()` (plain but valid), and the video is flagged for review.
  2. Facts still unsupported after the fact check go into `NEEDS_REVIEW.md`, and the result is a pre-release
     "REVIEW: …" plus a `review` issue.
  3. Measured gates in `report.json`: plan valid, loudness within 1 LU of −14, no more than 10% of frames almost still.
     If any gate fails, the video is held for review.
  4. The writer repairs the closest draft with its exact problems before giving up (the shared `repair_draft`).
- **Isolation from Hidden Reasons:**
  - nothing in `studio/story`, `studio/pipeline` or any other workflow imports `studio.motion` (a test checks this);
  - its own workflow `make-motion.yml` with concurrency group `make-motion`;
  - no Kaggle GPU, no channel memory, no schedule.

  Shared, read-only: the Kokoro voice model and word timing (`studio/voice.py`), the brain, and the research step.
  The writer also reuses the story writer's model-call helpers (`_cfg`, `_compat`, `patient`, `_timed`,
  `repair_draft`). If those change, `tests/test_motion.py` (offline writer test) will show it.

## 5. How to run

```
cd studio/motion && npm ci && npx playwright install chromium     # once
python -m studio.motion check  episodes/tech_education/001-what-is-an-api
python -m studio.motion stills episodes/tech_education/001-what-is-an-api        # one still per scene, in out/
python -m studio.motion make   episodes/tech_education/001-what-is-an-api        # ~0.25-0.5 s per frame on 2-4 cores
python -m studio.motion write  --topic "What is a database?" --make              # needs the brain (keys in GitHub only)
```

On GitHub, run **Actions → "Make a motion video (Tech Education)"**:
- enter a topic for a new video, or an episode folder;
- you get a release `motion-<episode>-runN`, or "REVIEW: …" plus an issue if a check failed.

## 6. Adding a scene type

1. Add it to `plan.TYPES` (fields and kinds), and to `NEEDS` if it depends on another scene.
2. In `web/engine.html`, add:
   - `SET_OF` (or leave it in the story set);
   - `BUILD.<type>` (the HTML);
   - `RENDER.<type>`, or the loop in `renderStory`;
   - a `case` in `direct()` (camera keys and sound cues).
3. Describe it in `writer.PLAN_RULES` so the AI can use it.
4. `python tests/test_motion.py` must pass. It also checks that every type in `TYPES` appears in the engine.

## 7. Known limits / next steps

- Motion is about half the reference's. Next: more scene changes per line, plus new scene types (a browser page, a
  3D chart, a phone).
- The voice is Kokoro's best for this channel, but still recognisably AI. Next step up: Chatterbox or Dia2 on Kaggle.
- Only one approved episode so far. The AI writer is tested offline with fake models. Its first real run is the
  next proof.
- No schedule for TE yet. Add one only after Franklin approves a few AI-written episodes.
