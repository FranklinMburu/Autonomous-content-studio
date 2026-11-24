# CRITIQUE alien1 (24 Nov 2026), independent critic, views only

File: /home/claude/out/alien1.mp4, 1080x1920, 30 fps, 40.25 s, 9 segments from sp-alien.mp4 (31.0 s to 320.0 s).
Layout: label on black 0-300 px, facecam 300-~1120, game 1120-1728, black 1728-1920.
Measured: fps=2 strips over the whole video, full frames at 0.0 / 33.8 / 36.3 s, signalstats YAVG, ebur128, silencedetect,
OpenCV frame-diff (270x480 grey), Laplacian at 608x1080, Hasler-Suesstrunk colourfulness on the game panel, pixel rows
of caption and label, ASS events, Whisper words mapped onto the output timeline.

## Gate (section 5): 5/15. Any NO means no ship.

| # | Check | Result | Measured |
|---|---|---|---|
| 1 | Premise sentence and format declared | NO | The spec has no premise or format field, and nothing in room/ names alien1. Paperwork, but the gate asks for it. |
| 2 | Frame 0 shows the named subject; 0-2 s YAVG >= 70 | NO | The alien is on the table at t=0, but it is lying still. Mean YAVG 0-2 s = **64.0** (game panel 51-54). |
| 3 | First event <= 1.5 s; label <= 7 words, on by 0.3 s | NO | Speed screams "OH" at 0.06 s and the label is on at 0.0 s (good), but the label is **9 words + emoji** ("Speed rescued an alien in GTA 6 👽 it did NOT forget"). |
| 4 | No dead stretch > 2.5 s | NO | **11.92-14.57 s**: one caption chunk ("GOTTA GET YOU") held 2.65 s, no cut, frame-diff 0.65-0.76 (limit 2). Speed really pauses ("gotta" 11.9, "get" 13.8). 19.5-25 s is also low motion (1.05-1.48) on a near-black panel, but captions keep it legal. |
| 5 | Payoff legible on mute: >= 15% of height, >= 1 s, brightness >= 70 | NO | UFO at 31.5-34.5 s. Disc plus lights span about 12% of frame height (the disc alone ~5%). Panel YAVG 56-60. What "it saved him" means (the UFO kills the attackers) is not readable on mute: 26-31 s shows orange beams from a lit tower with no clear source. |
| 6 | Story: question planted by 2 s; payoff at 60-95% | YES | "it did NOT forget" plants the question at 0 s. UFO at 31.5-34.5 s = **78-86%**. |
| 7 | Ends <= 3.0 s after the payoff | NO | UFO leaves frame ~34.5 s, "THE ALIEN HELPED ME." ends at 36.99 s, video ends 40.25 s (**4.3-5.8 s later**). 37-40 s is a near-black panel (YAVG ~41) of a pylon and Lucia's back, plus "W ALIEN". |
| 8 | Joke lines captioned; <= 3 words; cap height >= 75 px | NO | Coverage is fine and chunks are <= 3 words. Measured cap height on "ME." at 36.2 s is **61 px** (rows 1097-1157). Two zero-length events never show: "OKAY," 8.68-8.67 and the second "COMPANY." 21.84-21.83, so 21.3 s reads "WE GOT A" with no word after it. |
| 9 | Text in x 6-88%, y 10-78%, clean | NO | Label pixels at x 42-959 (**3.9-88.8%**) and y 184-310 (**9.6%** top). Line 2 sits on the facecam's GTA neon logo. Captions are inside the zone (y ~57-60%), centred at x=500, not 540. No source subs; small HUD text in the corner at 20 s. |
| 10 | Frame used; filler bands <= 10%; face panel >= 40% | YES (marginal) | Pure black: top 0-187 px (9.7%), bottom 1728-1920 (**10.0%**). The face panel is ~43% of the height. 25% of the screen carries no picture. |
| 11 | Picture floor: Laplacian >= 150, colourfulness >= 20 on the payoff | NO | At 33.8 s: Laplacian full 648, game panel 170 (passes). Colourfulness on the game panel is **18.3** (fails, a dark night shot). For comparison: 29.0 s scores 54.3, 0.5 s scores 22.6. |
| 12 | -14 +/-1.5 LUFS, TP <= -1 dBTP, no silence > 0.8 s, slurs bleeped | YES | I = **-14.0 LUFS**, true peak **-1.5 dBFS**, LRA 12.6. No silence > 0.8 s at -30 dB. No slurs in the Whisper text. |
| 13 | Title | YES | "IShowSpeed Rescued An Alien In GTA 6… Then It Saved Him 👽🛸": **55 chars** before the emoji, streamer first, "GTA 6", concrete noun, 2 emoji, no "?", no red-flag words. The claim is audible ("the alien helped me"); it is not visible as a saving action (see 5). |
| 14 | Policy | YES | No nudity (Lucia in a crop top, seen from behind, 35-40 s), no gambling, real footage. The audio still has "fuck" at 22.9 s and 29.5 s and "Shit" at 32.9 s; the captions show "hell"/blank. Swearing isn't a policy strike and the channel isn't monetised, so it doesn't hurt views. Muting those three words would only matter for ad suitability. |
| 15 | Not a repost (no copy > 10K in 48 h unless we add something new) | NO | TREND_DATA 24 Nov 11:30: ~10 Speed alien/UFO Shorts, **25K, 23K, 20K** among them, plus a faceless 73K how-to. Ours adds no step, code, number or comparison: it is the same Speed reaction with a tighter crop. Editing can't fix this one. |

Failed: 1, 2, 3, 4, 5, 7, 8, 9, 11, 15.

## Score: 5.0 / 10. Verdict: KILL this cut (do not ship). Fix the footage into a different angle only if the steps are in the VOD.

What is good: the story arc is real (find the alien → carry it out under fire → enemies → UFO arrives → "the alien helped me"), the stack
layout keeps Speed's face large, loudness is right, and the payoff lands at 78-86%.
What sinks it:
- It is the 11th copy of a moment whose biggest copies already took 20-25K. L10 and gate 15 say skip or add something.
- The payoff happens in a dark, small bottom panel that a muted phone viewer in Brazil can't read: a few white dots in the sky and an
  ambiguous orange beam.
- The last 4-6 s are a black tail.

## Honest odds (IntNext, 3 subs, today's cooling wave)
- > 1K views: **~25%**. Our good Shorts get tested to ~1.0-1.35K; a 10th repost of a saturated moment tends to be tested lower.
- > 10K views: **~4%**
- > 100K views: **< 1%**

## Weakest second
**13.0 s** (inside 11.9-14.6 s): one frozen caption "GOTTA GET YOU", Lucia slowly crouching in a dim green room, frame-diff 0.7,
while Speed is silent between "gotta" and "get".
**Single change:** remove source 165.8-167.6 s (output ~12.1-13.9), so the line runs "I gotta get you out of here". Same edit pass:
end the video at 36.99 s, after "HELPED ME.". That fixes gates 4 and 7 and takes the length to ~35 s.
None of this rescues gate 15. The only open angle in the market (TREND_DATA) is the **steps/code plus the reward**, proved by Speed doing it.
If the 1:16:20 VOD before our section shows how he got into the bunker, rebuild it as F1/F4 ("how to get the alien → what it does for
you"). Otherwise, spend the effort on a moment nobody has clipped.

## Better title and label (if it ships at all)
- Title: **"IShowSpeed Saved An Alien In GTA 6… Then A UFO Saved Him 👽🛸"** (57 chars before the emoji). It names the second concrete
  object, the UFO, which is the actual payoff.
- On-screen label (<= 7 words, 2 lines, >= 70 px, inside x 6-88%): **"He saved the alien. / Watch the sky 🛸"**. It plants the question
  and tells the eye where the payoff will come from, which partly offsets the small UFO.
- Also: gamma/exposure on the night segments (19.5-25 s panel YAVG 34-41, payoff 56-60) until the payoff panel is >= 70; caption font
  so the cap height is >= 75 px (now 61); delete the two zero-length ASS events.

## Numbers to check if it is posted anyway
1 h >= 150 views and stayed >= 60%; 24 h >= 1K; 72 h >= 2K. Below that, the repost verdict stands; don't re-upload it (Franklin's 21 Nov rule).
