# IntNext GTA 6 Shorts: master plan (single source of truth)
Last updated 20 Nov 2026, 16:20 Nairobi. Read this first in any new session, then RUNBOOK.md and room/UPLOAD_QUEUE.md.

## Franklin's direction (in his words, condensed)
- **Focus:** GTA 6 only for now. The goal is views (views = money).
- **Copy what is proven,** then differentiate. Add creativity after traction. Stop inventing; stop endless prompt loops.
- **Score every clip** and only make those with the highest chance of succeeding. Quality over quantity.
- **Hooks are natural, human and funny,** and true to what is on screen. Never template or AI-sounding.
- **Map the full architecture of a great Short.** Take the best existing (open-source or reverse-engineered) component for each part. Agents iterate and critique until the quality is there.
- **Use suspense and multi-part series.**
- **Standing rules:**
  - commits are authored as Franklin, with no Claude co-author;
  - never push to main;
  - $0;
  - nothing illegal or misleading;
  - never type his passwords, card or ID details.

## What the evidence says (room/WINNING_FORMATS.md, room/GTA_CHANNELS_20NOV.md)
- **Small channels win on format, not size.** COLETHEMAN (11.8K subs) has a 1.5M median. VicePulse (5.7K) has 5.6M and 5.2M hits. FlayHQ (4.9K) hit 2.4M. Big channels with a bad format sit at 3–8K medians.
- **Same fact, different format:** Voice GTA 6's dog poop Short got 12K; COLETHEMAN's got 4.4M as item 1 of a "can't do in GTA 5" list.
- **Formats ranked by how many unrelated small channels hit 100K+ with them:**
  1. "[N] Things You NEED To Know Before Playing GTA 6": 8 channels
  2. "[N] Things In GTA 6 You CAN'T Do In GTA 5" / "[N] Secrets Players Found": 8 channels
  3. "How [System] Works In GTA 6": 5 channels
  4. "GTA 5 vs GTA 6 [measurable]", 6–21 s: 4 channels. We have no GTA 5 footage yet.
  5. Money methods: 3 channels. Needs a verified method.
- **Single streamer-reaction clips** (what we posted through 20 Nov) have weak evidence: 1 hit in 72 channels. Our own got 0–180 views.

## Our format: copy COLETHEMAN's structure, differentiated by real streamer proof
- **Structure:**
  - Numbered list with emoji headers ("1. THROW DOG POOP 💩").
  - Full-screen gameplay, a cut every ~2–2.5 s (measured: 4–5 cuts per 10 s; longest shot ≤7 s).
  - AI narrator with word-by-word captions and coloured keywords.
  - GTA 5 contrast where true.
  - Question CTA at the end; the last shot loops back to the first.
  - Length 60–70 s for lists, 20–40 s for "how it works".
- **Differentiation:** every item is a real streamer moment (Lirik, Cohh, Speed, Kai…). It is proof plus a familiar face. Titles stay plain and literal, like the winners'.
- **Series:** "GTA 6 Secrets Nobody Told You #N" (room/SERIES_PLAYBOOK.md):
  - Each part stands alone.
  - Link the next part with the related-video slot; comment links aren't tappable.
  - Post the next part 2–24 h later.
  - Stop a series if Part 2 gets under 25% of Part 1's views.
- **Hooks:** follow room/HOOK_BLUEPRINT.md. The loop is ChatGPT drafts and an independent critic scores. Ship only at ≥9.5 quality.

## Architecture: the components (room/COMPONENTS.md has details and the best tool for each)
| # | Component | Now | Next upgrade |
|---|---|---|---|
| 1 | Trend/topic | browser scrape (GTA_CHANNELS, WINNING_FORMATS) | scheduled scrape, views/hour |
| 2 | Moment finding | fan-clip title hunt (fetch.py --title-re), Whisper transcripts | + YouTube heatmap + Twitch chat spikes |
| 3 | Story/structure | COLETHEMAN list format, SERIES_PLAYBOOK | length per format |
| 4 | Hook | HOOK_BLUEPRINT + ChatGPT x critic | automatic rubric check |
| 5 | Reframe 16:9→9:16 | fullscreen.py with hand-set keys | OpenShorts tracker (MediaPipe/YOLO) |
| 6 | Pacing | hand cuts | cut every ~2 s, punch-in zooms, auto-editor |
| 7 | Captions | PIL punch captions | word-by-word karaoke from TTS/whisperX timings |
| 8 | Audio | two-pass loudnorm −14 LUFS | narrator TTS + light SFX |
| 9 | Packaging | blueprint titles, pinned comment | — |
| 10 | Publishing | Studio browser upload (≈10/24 h limit until verified) | API `publishAt` (needs Franklin's OK) |
| 11 | Feedback | manual Studio checks | retention pull per Short, rules updated |
| 12 | QA | teardown.py (measured vs winners) + critic agent | critic watches the frames |

## Assets (all new, never-posted footage unless noted)
- **Lirik:**
  - dog on a jet ski drives him to shore: raw d_lirik/lirik-01 → dog-L1 Short built;
  - Bigfoot knockout + bank app: d2_lirik/lirik-04;
  - Bigfoot sighting: lirik-02/03;
  - Rescue Dog fan clip.
- **Cohh:** parrot "Generator!" → +$1,405, cohhcarnage-02 → parrot-C1 Short built.
- **zackrawrr:** "you can feed snakes in GTA 6", zackrawrr-01.
- **Speed (laptop helper, release yt-sections):** hunt-speed-gator.mp4 (alligator attack, Speed's clips channel) and hunt-speed-lookalike.mp4.
- **18 winning Shorts for teardown:** release yt-sections, win-*.mp4. Includes the same alligator clip at 306K (26la2COuHM4) vs 816 views (P3vUekDgxrQ).
- **COLETHEMAN's 3 Shorts:** cole-*.mp4.

## Status / next steps (keep this list current)
1. DONE: research (formats, channels, components, series, hook blueprint); teardown.py; fullscreen.py.
2. DONE: parrot-C1 and dog-L1 singles, at the top of UPLOAD_QUEUE (post when the YouTube limit resets, ~00:00 Nairobi 21 Nov).
3. DONE: room/FORMAT_SPEC.md (measured from the 18 winners + COLE). Finding: the 306K vs 816 alligator posts are pixel-identical, so the gap was distribution (channel/timing/title), not the edit.
4. DONE: listshort.py (Kokoro narrator via claude-tts/** Actions branch, word-by-word ASS captions, COLE headers, ~2 s cuts, loop, labels).
5. DONE: secrets1b "5 GTA 6 Secrets Streamers Found": critic 6 -> 7.5 -> fixes applied; first in the upload queue.
6. NEXT: "5 Things You NEED To Know Before Playing GTA 6" (no autosave, story length, controls…), then "How The Wanted System Works In GTA 6" from xQc/Lirik/Cohh chases.
7. After posting: read retention at 1 h / 24 h, update the rules here.
