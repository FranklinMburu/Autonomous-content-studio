# 10/10 GTA 6 streamer Short: the spec (19 Nov 2026)

Goal: Shorts that reach the top 10% of @Kick_Clippers / Clipatra (250K+ views). Franklin judges by watching. Real footage only.
Campaign: Kai Cenat $10K GTA 6 pool (Content Rewards): Kai must be the main focus; caption has #KaiCenat; paid disclosure.

## Tools
- Footage: /home/claude/clips/raw/<streamer>/<name>.mp4 (1920x1080, 30 fps, ~2-2.5 min around the moment fans clipped)
  and <name>.json: fan_titles (views: fan's clip title = proof of demand), fan_moment_in_section (seconds into the file
  where the fan clips start), words (Whisper word timestamps, seconds into the file), vod_page, section_start_in_vod.
- Look at frames: `ffmpeg -v error -ss T -i X.mp4 -frames:v 1 -vf scale=960:540 /tmp/x.jpg` then Read it. For a strip:
  `ffmpeg -v error -ss A -t D -i X.mp4 -vf "fps=1,scale=320:180,tile=6x3" -frames:v 1 /tmp/strip.jpg` (18 frames, 1 per s).
- Render: write a spec JSON and run `python3 /home/claude/clips/edit.py spec.json --sheet` (about 6 s). It writes the mp4
  and <out>.sheet.jpg (frames at 0 s, 0.5 s, 25/50/75 %, end). ALWAYS Read the sheet and fix until it passes.
  Spec: {"src", "start", "end" (seconds in the file), "face": [x,y,w,h] facecam rect in 1920x1080 px,
  "game": [x,y,w,h] gameplay crop (16:9, e.g. [420,180,1280,720]) or null for the full frame,
  "face_at": seconds into the CLIP to hard-switch to full-facecam layout, or null,
  "title": on-screen title box text, "punch": {"text" <=6 words, "at" s into the clip, "dur" 1.6} or null, "out"}
- Layout the editor makes: title box y 210-390 (safe zone), facecam band y 400-1000, gameplay band y 1000-1608, blurred
  background. face_at switches to full facecam y 400-1440 (use when the reaction IS the story).

## Find the facecam
Kai's facecam is a small box at the LEFT of the frame, roughly x 0-392, y 350-650 (it MOVES between segments: check
each file). Measure it on a 960x540 frame and double the numbers. Crop tight on the cam box (no chat, no border): the
face must fill the band. Keep 16:9-ish aspect (e.g. 392x220). Chat sits under the cam; viewer counters at the right
edge (x > 1720): the game crop must exclude cam, chat, counters and the minimap.

## Choosing the moment (what trends)
1. Fan-clip views = proof. Start at fan_moment_in_section, read the words, watch strips, find the TRIGGER and the PEAK reaction.
2. Ranking: Kai's big face reaction (shock, scream, laugh, rage, prayer/emotion "13 years"), a crazy/funny game event he
   reacts to, chaos with people in the room. Skip: calm gameplay, menus, loading, cutscene-only, story spoilers.
3. HARD NO: in-game nudity or sexual acts on screen (crop the game band away from it or use face_at from 0 with a
   game crop that hides it; if impossible, skip), slurs, anything sexual as the hook. Never invent what happened.

## Story arc
0-1 s: trigger already in motion, Kai's face visible. 1-4 s: just enough context. Build. Peak reaction before 80% of runtime.
End within 1.5 s after the payoff/laugh (hard cut). Length 12-35 s, target 18-25 s. Start 1-2 s before the trigger.

## Text
Title box: <= ~60 characters, 2 lines max, concrete noun, honest: "The moment / No way Kai Cenat [REALIZED / was SHOCKED /
couldn't believe] [specific thing] in GTA 6 😭" (vary emojis, 1-2). Punch: one quote he actually says (check words),
<= 6 words, uppercase ok, on the seam; only if it adds. Nothing ever covers his face or the action.

## Deliver per clip (into /home/claude/clips/out/)
<id>.mp4 + <id>.sheet.jpg + <id>.json: {"id","source_file","start","end","peak_in_clip","title_box","youtube_title" (<=95
chars, formula), "description" (title, "Kai Cenat's GTA 6 launch stream, Twitch, 18-19 Nov 2026. #ad Paid partnership",
hashtags), "hashtags" (#KaiCenat #GTA6 #GTAVI #kaicenatclips #shorts), "why_it_trends" (one line), "fan_proof" (views),
"self_score" 0-10 per: moment, hook, story, layout, text, ending, overall, "checklist" (12 points below, pass/fail)}.

## 12-point checklist (all must pass)
1 face visible at frame 0 · 2 trigger within 1.5 s · 3 title box at frame 0 · 4 text inside safe zone · 5 text never on
face/action (check 6 frames) · 6 face >= 300 px tall · 7 no chat/counters/overlays · 8 peak before 80% · 9 ends within
1.5 s of payoff · 10 length 12-35 s · 11 title honest + concrete · 12 no nudity/sexual hook, no radio music as the main sound.

## Lessons from the independent review (19 Nov, round 1: editors self-scored 9, the reviewer gave 4-7)
- FACE SIZE: crop TIGHT on head + shoulders (about 55-65% of the cam box), so the head is >= 350 px tall in the band.
  Check strips over the whole clip so the head is never cut when he moves.
- FRAME 0 = THE MOMENT: no loading screens, chatter or setup; start on the reveal/trigger. Full facecam from 0
  (face_at 0) when the game band shows nothing that explains the moment.
- No dead game strip: if the game band is dark, blank or meaningless, use full facecam instead.
- One Short per scene: never two Shorts from the same scene.
- End ON the payoff: never on a dark frame, a blank strip or seconds of silence.
- Titles must be literally true (no "found out" when nobody found out). No slurs or crude lines from the streamer
  near the end (negative-portrayal risk).
- Self-scores must be honest: a 9 means a harsh stranger would say it can hit 250K+. Most clips are 6-7.
- Edit.py now does two-pass loudness (-14 LUFS). "face_at": null works.

## Kick streamers (Adin Ross, xQc, N3on): footage = the fan's own Kick clip (11-180 s, starts where the fan began).
No paid campaign is known for them: description WITHOUT "#ad", hashtags #<Streamer> #GTA6 #GTAVI #<streamer>clips #shorts.
