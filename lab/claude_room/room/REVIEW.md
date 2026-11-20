# REVIEW 2: finished renders in final2/ (critic pass, 19 Nov 2026)

Method: for each Short I made a 2 fps contact strip (`<id>.strip.jpg`) and a 540x960 frame 0 (`<id>.f0.jpg`) in this folder, checked the kept words in the source `.json` transcripts, and compared the render against the spec and CRITIQUE.md.
Score = expected views, 0-10, for a stranger scrolling Shorts.

## Patterns across the batch (fix these once in the template)
1. **Dead bottom ~20%.** Every render has a blurred, empty strip under the game band (y ~800-960 at 540w). It wastes about a fifth of the screen. Grow the game band (or the face band on face-only cuts) to fill it.
2. **Spoken game lines that carry the hook aren't captioned.** C11 "free up some beds", C04 "he's my boyfriend", C14 "rabid iguana... coma". About half of Shorts viewers watch muted, so burn in these lines.
3. **Face-only cuts drop the game.** C05, C1r and C3r show no game for most or all of their length. A stranger can't tell it's GTA 6 or what he's reacting to.

## Per-Short verdicts

### kai-C01 (Kai, 24.2 s): 6, SHIP (optional tweak)
- **Frame 0:** Kai mid-word with his hand up, plus a big readable "NAVIGATION EXPERIENCE" menu. It grabs, but the face is soft (upscaled small cam).
- **Hook:** It says "brightness settings", but the first 8 s are the navigation and text-size menus. HDR doesn't arrive until ~6 s. It's close enough; a stranger gets "settings menu".
- **Payoff:** "NO NO NO NO" over the paper-white slider lands at ~16 s. The close is "MY RUN NEEDS TO BE X" and then the controller map, which works as an ending.
- **Risk:** No yacht or bikinis visible. One "shit" at the far end of the source is outside the cut.
- **Tweak:** Change the hook to `13 years of waiting. 4 MINUTES in the settings menu 💀` so it matches the opening. Fill the blurred bottom band.

### xqc-C03 (xQc, 6.6 s): 6, FIX
- **Frame 0:** The photo is already in his hands, which is good. But the photo is dim and only about 40% of the band.
- **The problem:** At the payoff (5.45 s) the layout switches to face-only, so **the photo disappears right when he says "that's gotta be AI"**. Viewers can't judge it themselves, and that judging is what drives the comments.
- **Fix:**
  - Keep the split layout to the end.
  - Zoom the game crop to the photo, roughly game `[470,190,700,394]`, and brighten it (eq gamma 1.3).
  - Start the caption at the first "AI" (176.6) and end at 179.3.

### agent00-C14 (Agent00, 19.5 s): 6, FIX
- **Frame 0:** A great open-mouth face, but the band shows an **Esperanza Insurance ad** for the first 2.6 s. That contradicts the "soap opera / iguana" hook.
- **Captions:** The iguana story is TV dialogue with no captions, so a muted viewer gets nothing.
- **HUD:** "EXIT / VOLUME (MAX)" sits beside his head.
- **Fix:**
  - Cut piece 1 to 28.5-29.3: the gasp only, no insurance line.
  - Burn in the TV lines: "RABID IGUANA... PUT HER IN A COMA" (41.4-45.5) and "IT FELL FROM A TREE, NIPPED HER SHOULDER" (50.8-53.5).
  - Keep "NO!" at 54.6 and the end at 57.55.

### n3on-C04 (N3on, 10.0 s): 6, FIX (light)
- **Frame 0:** N3on grins with a big, clear head, and Lucia and the cop are in frame. That's strong.
- **Captions:** Lucia's "he's my boyfriend" (0.6-2.0 s) isn't captioned, and the cutscene is dark.
- **Fix:**
  - Caption "HE'S MY BOYFRIEND" at 0.6-2.0.
  - Caption "WHAT UP, LUCIA? 😭" at 9.4-10.0.
  - Lift the band (eq brightness +0.08, gamma 1.25).
  - Optional: start at 76.4 so the cop's "Miss, you know this guy?" sets it up. That's +2 s, still fine.

### agent00-C06 (Agent00, 18.5 s): 5, FIX
- **Frame 0:** It's Mandy in a crop top on a bed, framed torso-centred, with the laptop barely visible. It reads as thirst bait (the source fan title says "horny"), not as "tech job satire". Strangers who stop for that leave when the joke starts, and it risks a "sexualised thumbnail" limit.
- **Payoff:** The second half (9 s of Agent00 talking to camera, big face) is good.
- **Fix:**
  - Reframe pieces 1-2 to her face plus the laptop only, about `[880,300,560,315]`, with no chest or bed.
  - Caption her line: "I'VE MANAGED LIKE A MILLION ENGINEERS".
  - Optional: open on Agent00's "she can't pay rent?" face for 0.5 s first.

### kai-C02 (Kai, 19.5 s): 5, FIX
- **Frame 0:** A great hands-on-head face. But Kai is small in a wide room shot (head ~20% of width), and the whole bottom quarter is blurred.
- **Later sections:** Under the "MY BAD x6" count he's turned or standing. The PS5 section (12-19.5 s) has a tiny face, and "I'M SCARED BRO" is spoken only.
- **Fix:**
  - Crop piece 1 tighter, about face `[700,120,560,560]`, so the head reaches ~40% of width.
  - Extend the face band down to fill the blur.
  - On the PS5 pieces, zoom the band to the "Play Game" button.
- **Risk:** The GTA VI box art on the PS5 screen is a game logo, not a watermark. Acceptable, but crop it out if the pool reviewers are strict.

### fanum-1r (Fanum, 12.8 s): 5, FIX
- **Problem:** 5.25 s of setup ("dynamic dynamic dynamic... the middle one") comes before count x1. Fanum looks sideways and small on frame 0.
- **Fix:**
  - Drop piece 1 (52.25-53.9) and start at 55.25, so x1 lands at ~4.1 s.
  - Better: start at 57.3 ("the middle one") so x1 lands at ~1.7 s.
- **Spacing:** It's the same NAVIGATION EXPERIENCE screen as Kai C01, so post at least 12 h apart.

### agent00-C11 (Agent00, 13.2 s): 5, FIX
- **Frame 0:** Lucia in an orange jumpsuit reads "prison" instantly, which is good.
- **Captions and pacing:** The "free up some beds" line isn't captioned. Then 8 s of filler ("eligible for the trial", "he's in a chat", "help me understand") comes before the payoff.
- **Framing:** In piece 2 the face crop drifts, and his head is cut off at the top at the end.
- **Fix:**
  - Pieces: 105.5-107.1 with the caption "THE COUNTY'S LOOKING TO FREE UP SOME BEDS", then 115.5-118.6. That's about 4.7 s.
  - Re-measure the face box for 115.5+, about `[1300,660,440,290]`.

### kai-C05 (Kai, 12.2 s): 4, FIX
- **Frame 0:** The painted teal room with Jason and the roller is a good open.
- **The problem:** After 1.8 s the game disappears. That leaves 10 s of a low-energy face with a counter, and the strangers' "object" (the house) is gone.
- **Audio:** The first audible line is "make sure this **shit** sturdy" (0.6 s).
- **Fix:**
  - Use the split layout (game band = the room) for the whole clip.
  - Start at 1.38 ("you heard?") to drop the swear.
  - Hook: `Kai painted his GTA 6 house for his girl. "She gon' like that" x6 😭`.

### kai-C1r (Kai, 12.6 s): 4, FIX
- **Frame 0:** A big, clean face.
- **Problem:** No game is visible, and neither the hook nor the frame says GTA 6, so a stranger sees a man praying. Nothing marks "survive" when it lands (4.2 s).
- **Positive:** The end, "I didn't mean to curse, God", is a nice beat. Keep it.
- **Fix:**
  - Hook: `Before GTA 6: "Thank you God for making me SURVIVE this long" 🙏`.
  - Add the punch "SURVIVE THIS LONG 😭" at 4.1-5.0.
  - Post it 2-3 h after C02 as part 2.
- **Kai portrayal:** Sincere and fine; don't mock it.

### adin-C09 (Adin, 15.1 s): 4, SHIP (low)
- **Frame 0:** The snake is being handled in the terrarium, so the hook is paid off immediately. The close-up from ~8 s is good.
- **Weaknesses:**
  - Adin is mild.
  - The "IS HE GONNA EAT THE RAT?" caption sets up an expectation that never pays off. It's his real question, but it leaves viewers unsatisfied.
  - It ends on "Oh shit" (14.2 s) over the coiling snake.
- **Optional:** End at 86.1 (before "oh shit") for a cleaner loop.

### adin-C10 (Adin, 15.9 s): 3, FIX
- **Frame 0:** It's 0.85 s of a **blurred pause menu**, an instant swipe.
- **Weaknesses:** The pink map blobs are unreadable on a phone. Adin is flat, and nothing on screen proves "no stores".
- **Fix:**
  - Drop piece 1 and start at 9.3.
  - Zoom the band 1.5x on the map icons.
  - Better: pieces 9.3-10.6 ("let me zoom out") + 18.4-24.3, so "BRO, THERE'S NO CLOTHING STORES" lands at ~1.5 s and the "Northeast First Avenue" ramble is gone. About 7 s.
- **Fallback:** If it's not re-cut, DROP.

### kai-C3r (Kai, 12.7 s): 3, FIX (or post last)
- **Frame 0:** A calm hand-to-mouth face. The scream doesn't come until ~4.5 s.
- **Problems:** The GTA intro is only a blurred background. The hook "13 years of waiting, in 12 seconds" is vague and in the saturated bucket.
- **Fix:**
  - Start at ~3.5 s (raw 58.8).
  - Put the intro unblurred in a game band.
  - Hook: `Kai Cenat's reaction to the first GTA 6 frame 😭`.
- **Pool:** It costs nothing, so post it for the Kai pool's 1K-per-clip count, last.

## Posting order (max views; streamers and angles spread, Kai spaced)
| # | ID | Score | Verdict | Angle |
|---|---|---|---|---|
| 1 | kai-C01 | 6 | SHIP | settings time-sink (Kai pool) |
| 2 | xqc-C03 | 6 | FIX | "is it AI" comment fight |
| 3 | agent00-C14 | 6 | FIX | TV satire |
| 4 | kai-C02 | 5 | FIX | nerves, part 1 (Kai pool) |
| 5 | n3on-C04 | 6 | FIX | Lucia "girlfriend" |
| 6 | agent00-C06 | 5 | FIX | NPC job satire |
| 7 | kai-C1r | 4 | FIX | prayer, part 2, 2-3 h after C02 (Kai pool) |
| 8 | fanum-1r | 5 | FIX | settings irony (12 h or more after C01) |
| 9 | adin-C09 | 4 | SHIP | realism discovery |
| 10 | kai-C05 | 4 | FIX | house renovation (Kai pool) |
| 11 | agent00-C11 | 5 | FIX | realism "too real" |
| 12 | adin-C10 | 3 | FIX/DROP | realism limit |
| 13 | kai-C3r | 3 | FIX | reaction (Kai pool, zero cost) |

**Post first (6):** kai-C01, xqc-C03, agent00-C14, kai-C02, n3on-C04, agent00-C06.
Of these, only C01 can go out as-is; the other five need the fixes above before posting.

**Honest outlook:** Nothing in this batch is a 100K+ lock. C01, C03, C14 and C04 have the best odds (10-50K range) once fixed.
The cheapest big gain is in the template: fill the dead bottom band and caption the game lines.
