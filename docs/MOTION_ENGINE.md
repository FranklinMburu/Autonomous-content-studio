# Motion engine: the Tech Education style

Faceless 45–75 s explainers built from real-looking software, seen straight on:
- one diagram that stays on screen and changes in place (app → line → API door → server);
- word-by-word captions, and a camera that moves only to show what the voice is naming;
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

After a review of the first pipeline version (PR #88, 11 Nov), the engine also got **coverage cuts**, light wipes
between sets, brighter panels and livelier slow scenes (section 3). Measured on the API episode: average motion 2.8 → 4.2
and a whole-picture change every 5.7 s → 1.8 s (the reference: 5.5 and 0.7 s).

**Voice lock:** Kokoro `am_fenrir` at 1.0, read line by line, then only a gentle EQ (more bass, a softer top).

Rejected: blending in a second voice, pitch shifting, room echo and `am_puck`. Together they "sound like two stacked
voices" or "soprano". A more human voice needs a bigger model on Kaggle (Chatterbox, MIT; Dia2, Apache 2.0); that
hasn't been done yet.

**v4/v5 rejected (11 Nov, Franklin): "weird", "not making someone understand", "the camera moving just for the
sake of moving".** The causes:
- coverage cuts and a handheld drift that moved the camera with no reason;
- many small, tilted panels floating in 3D space;
- overlay cards that hid the diagram instead of changing it;
- abstract metaphors.

**v6 (11 Nov), one diagram, straight on.** Studied frame by frame, the reference:
- shows everything facing the viewer, with one big subject at a time;
- keeps one diagram (its timeline) on screen and changes it in place;
- pans and zooms only to follow what is being said, and holds still otherwise.

The engine was rewritten to do the same (section 3). Rejected for good: automatic angle cuts, drift, tilted 3D panels,
and cards laid over the diagram.

**Before v6, still below the reference:** average motion is about three quarters of it (4.2 against 5.5), and contrast is lower (26 against
35). The reference fills the frame with one bright screen far more often.

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
2. Scenes live in zones (hook, stat, story, wall, cta, end, free), far apart in a flat world. Changing zone is a hard
   cut; inside a zone the camera only pans and zooms (2D, straight on).
3. The story zone is one vertical diagram:
   - the terminal builds the app, then steps aside;
   - app, then a line, then the API door on top of the server.

   Whatever explains the line opens **in the gap on the line**, one thing at a time:
   - the request opens into its URL;
   - the answer opens into its data, and the value rises into the app;
   - the request waits at the door and the key attaches to it;
   - the password comparison;
   - strangers with copied keys, and the server's quota meter filling up;
   - the status codes coming back.
4. **The camera moves only with a reason** (`direct()`): to the panel being named, following a message down the line,
   or pulling back to show a connection. Every move is listed with its reason in `info.json` (`moves`). Between moves
   it holds still; the motion comes from the diagram changing. There is no drift and no automatic angles.
5. **Framing guard** (`fitShots()`): a shot is "show these things". It becomes a camera where they are whole, inside
   the frame and below the captions, as big as fits. If another panel alive during the shot would be cut by the edge,
   the frame widens to take it in, so a frame at rest never halves a panel.
6. **Frame audit** (`audit()`): it steps through every frame at rest and lists any solid panel that is cut off, under
   the captions or overlapping another. The list goes into `info.json`, and the `layout_ok` gate holds the video if
   it is not empty.

## 4. Determinism and guardrails

- **No clock, no randomness at render time.**
  - Time is stepped by `render.js`.
  - All variation comes from the seed: `plan.seed`, or a hash of the folder name.
  - Pinned Chromium, fonts and Playwright (`package-lock.json`).
  - `tests/test_motion.py` renders the same frames twice and they are byte-identical. `render.js` waits two
    animation frames after each `render(t)`, so Chromium has finished drawing before the screenshot (without this, frames
    differed by up to 2% under CPU load).
- **Layout rules** (after the 11 Nov video with cut-off and overlapping panels):
  - two solid things never share screen space: app on top, badges in the gap, door mounted on the server, meter where
    the app was;
  - overlay cards (code, data, compare) own the frame, and everything behind them fades to 10% before the cut;
  - the door and the "?" are their own objects, so the server box can't hide them.
- **Guardrails, so the line never dies and nothing bad is published:**
  1. An invalid plan becomes `auto_plan()` (plain but valid), and the video is flagged for review.
  2. Facts still unsupported after the fact check go into `NEEDS_REVIEW.md`, and the result is a pre-release
     "REVIEW: …" plus a `review` issue.
  3. Measured gates in `report.json`: plan valid, loudness within 1 LU of −14, no more than 10% of frames almost still,
     and `layout_ok` (the frame audit found nothing).
     If any gate fails, the video is held for review.
  4. The writer repairs the closest draft with its exact problems before giving up (the shared `repair_draft`).
- **Isolation from Hidden Reasons:**
  - no motion module imports the story engine, and nothing in `studio/`, the workflows, `tools/` or the website
    mentions the motion engine (two tests check this);
  - its own workflows: `make-motion.yml` (concurrency group `make-motion`) and `motion-review.yml`;
  - its own cache key (`motion-kokoro-v1.1`, the voice model only), so it can never replace the Hidden Reasons cache;
  - its own review label, `review-motion`, with its own marker. These issues do not appear in the Hidden Reasons
    review queue on the website, and the film review workflow ignores them;
  - no Kaggle GPU, no channel memory, no schedule.

  Shared, read-only: the Kokoro voice model and word timing (`studio/voice.py`), the brain, the research step and
  `tools/commit_to_main.sh`. Every pacing value of the locked voice is set in `channels/te/channel.json`, so a change
  to the shared voice defaults for another channel cannot change this voice. The model-call helpers are a copy in
  `studio/motion/calls.py`, not imported from the story engine (importing them pulled in pycairo and broke the CI job
  on 11 Nov).

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
- a new episode written by the AI is saved to `episodes/tech_education/` on main, so it can be fixed and re-made, and
  the next one gets the next number;
- you get a release `motion-<episode>-runN`, or a pre-release "REVIEW: …" plus an issue labelled `review-motion` if a
  check failed;
- on that issue, comment `approve` (the release becomes finished) or fix the episode files, delete
  `NEEDS_REVIEW.md`, and comment `remake`.

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

- Motion is about three quarters of the reference's. Next: scene types that fill the whole frame with one bright screen (a browser
  page, a full-screen terminal, a phone), which is where most of the reference's motion and contrast come from.
- The voice is Kokoro's best for this channel, but still recognisably AI. Next step up: Chatterbox or Dia2 on Kaggle.
- Only one approved episode so far. The AI writer is tested offline with fake models, and the two workflows have never
  run on GitHub (they can't until they are on main). Their first real run is the next proof; expect small fixes.
- No schedule for TE yet. Add one only after Franklin approves a few AI-written episodes.
