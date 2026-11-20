# FORMAT SPEC: winning GTA 6 list and "how it works" Shorts (measured 20 Nov)

The sample has 9 list/explainer winners from teardown_win plus COLETHEMAN's 3 (4.4M, 1.9M, 1.5M), so n=12. MASTER_PLAN.md is missing, so ids aren't mapped to titles or views; formats were classified by eye.

**Length**
- List/explainer: median 65 s (range 37-73). COLE: 64-68.
- Single clip or reaction: median 24 s (6-48).
- A/B comparison: 6-24 s.

**Cut rate and longest shot**
- The group splits in two:
  - COLE: 4.0-4.8 cuts per 10 s, median shot 1.4-2.0 s, longest 5-7 s.
  - The other list winners: median 1.7 cuts per 10 s, longest shot median 11 s (3-23). Several use one long gameplay shot under narration.
- COLE has 5-8 shots over 3 s per video, so the rule is "no dead shot", not "no 3 s shot".

**First text (when and where)**
- COLE: frame 0 is clean gameplay. At 0.5 s the GTA VI logo and title appear at the centre-top, with one keyword coloured (CRAZY in green, CAN'T in red). The title stays until about 3 s, and the first cut comes at 2.6-3.4 s (median 3.0 s across the group).
- Other list winners: a title or caption appears by 0.5-1 s, either top-third ("FOUND ON DAY 1" red tag) or centre (kinetic word).

**Header and caption style**
- Numbered header: white heavy sans, black stroke, top 15%, with an emoji under it. Example: "1. THROW DOG POOP 💩".
- Captions: 1-3 words, centre or lower-centre, white with one keyword coloured.
- 4 of 9 list winners letterbox 16:9 over a blurred fill rather than crop.

**Narration share**
- All list winners have continuous, voiced audio (sound share 1.0). Voice isn't separated from game audio: **thin data.**

**Loop**
- List median similarity is 0.23 and COLE's is 0.08, so winners don't depend on a loop.
- Seamless loops (0.95-0.99) appear only in the 6 s comparison and some single-clip winners.

**Frame 0**
- Moving gameplay with a readable subject (a character mid-action, a car, the map). Never a black or title card, except the alligator pair's 1-frame streak transition.

**Alligator: 306K (26la2COuHM4) vs 816 views (P3vUekDgxrQ)**
These are the same edit. The two were compared on:
- Resolution: 608x1080 in both.
- Length: 47.8 s vs 47.9 s.
- Text: the same single "BARKING" overlay at 1-1.5 s.
- Opening: the same streak transition, then a split screen with facecam on top and gameplay below.
- Pixels: mean frame difference is 2-4/255 at 13 timestamps, which is compression noise. Crop, text, length and first second are identical.

The only measurable difference is audio: the 816 version's quiet passages run 10-14 dB louder (sound share 0.95 vs 0.80, same LUFS). That can't explain a 375x gap.

**Conclusion:** the gap came from distribution (channel, posting time or order, title), not from the edit. Titles are unavailable to confirm. A second re-post of a viral clip earns nothing, and our open uses this clip.

## QA secrets1

**Score: 6/10.** The structure matches COLE (countdown, headers, about 2 s shots, -14 LUFS). Five things below it: two caption render bugs, a Bigfoot payoff that doesn't show Bigfoot, a murky parrot section, a loop line that doesn't join, and a weaker title card.

| Metric | Ours | Winners (list) | COLE |
|---|---|---|---|
| Length | 53.1 s | 37-73 (med 65) | 64-68 |
| Cuts per 10 s | 3.4 measured (about 3.8 true; dark parrot cuts missed) | 0.9-7.0 (med 1.7) | 4.0-4.8 |
| First cut | 2.1 s | med 3.0 | 2.6-3.4 |
| Longest shot | 4.9 s (48.2-53.1, continuous gator); parrot 18.2-21.5 = 3.3 s | 3-23 | 5-7 |
| Title on screen | 0.3 s, top, all white, no logo | 0.5-1 s | 0.5 s, centre, logo + coloured word |
| LUFS | -14.1 | -27 to -12.5 | -15 |
| Narration | 88% of runtime, 169 wpm | voiced, continuous | voiced, continuous |
| Loop similarity | 0.91 visual; audio line doesn't join | med 0.23 | 0.08 |

**Checks:**
- **Frame 0:** readable (Jason plus alligator), but the gator sits on the right edge and Jason's head is cut off.
- **First line** ("Streamers found five secrets... nobody told you about"): generic. The noun only arrives at 7.3 s.
- **Captions:**
  - Overlap at 15.5 s ("HEY.HANDSOME") and at 41.5 s ("LIRIKINTHESWAMP:OOT").
  - Overflow the frame edge at 50.5-52 s ("ECAUSE THAT ALLIGATOR") and touch the edges at 0.5 s and 11.5 s.
  - The source's burnt-in subtitles show at 1.5 s and 14.5 s ("WHERE'S THE CASH?").
- **Parrot (13-23 s):** dim, the parrot is small or half-cropped, and $1,405 is never shown.
- **Snake:** visible at the bottom edge, but the rat being eaten isn't shown.
- **Bigfoot:**
  - Only 41.0-42.2 s, a dark, blurry close-up of one leg. It reads as a tree trunk.
  - 39.4-41.0 s is an empty swamp boat.
- **Pacing:** fine. 169 wpm with 0.45 s beat gaps.

**Top 5 fixes (by view impact)**
1. **Fix the Bigfoot payoff.**
   - Open beat 5 on lirik-04 at 10.4-11.6 s with cx=1760, h=1440, so both hairy legs show. Brighten with eq gamma 1.25.
   - Hold it 2 s under "spotted Bigfoot" and add a "BIGFOOT 👇" arrow label.
   - Move the swamp boat to after it. Use the lying-down shot under "blacked out".
2. **Fix the caption render bugs.**
   - Clear the previous chunk before drawing the next. The two chunks overlap at 15.5 s and 41.5 s.
   - Cap chunks at 2 words or 80% safe width. Shrink "BECAUSE THAT ALLIGATOR" (50.3-52 s) to 2 lines.
   - Mask or crop out the burnt-in source subtitles at 1.5 s and 14.5 s (raise y0 or crop the bottom 8%).
3. **Rebuild the hook (0-4.5 s).**
   - Frame 0: lunge at hunt-speed-gator 20.0 s with cx=1050, h=820, so the gator fills a third of the frame.
   - Title at 0.3 s, centred, with the GTA VI logo and "SECRETS" in green.
   - New line: "This alligator is just secret number one streamers found in GTA 6." It names the noun in the first second.
4. **Make the loop line join.** End with "...and it all started with this alligator", then cut to frame 0 so the new opening line continues it. Trim the 4.9 s gator tail to 2.5 s.
5. **Make the parrot section readable.**
   - Use only shots with the parrot full in frame (cohh 15.8-17.3 s with cx=1300).
   - Gamma 1.4 on 17-21 s.
   - Show the cash pickup or a "$1,405" overlay at 21 s. Cut 18.2-21.5 s into two shots.

**Ready to post as-is: NO.** The caption overlap and overflow bugs alone are visible errors, and item 5 currently shows no Bigfoot.

## QA secrets1b

**Score: 7.5/10. Ready: NO. Two small fixes are needed, then yes.**

Teardown:
- 53.1 s, 3.2 cuts per 10 s, first cut 2.37 s, -14.2 LUFS, loop similarity 0.90.
- Spec shots are 0.8-2.2 s, except the first parrot shot at 3.2 s, which is fine.
- The teardown's longest shot of 9.8 s is a miss in the dim parrot section; the shots there do change.

**Fixed (checked frame by frame):**
- Frame 0 is the lunge, with the gator clearly readable.
- The new first line names the alligator at 0.3 s.
- The title has "SECRETS" in green.
- No caption overlap or overflow at 15.5, 41.5 or 50-52 s, or anywhere else I sampled.
- The parrot is visible in frame from 12.9 to 18.5 s, with a "+$1,405 💰" label at 22.5 s.
- Bigfoot's legs are on screen 39.1-41.7 s with a "BIGFOOT 👇" label. They're blurry, but this is the best footage we have. (My cx=1760 was a misread; cx≈1000 is right.)
- The loop line joins.

**Must fix:**
1. **The source's own subtitles are still burnt in.** "handsome! Hey, handsome!" shows at about 13.8-14.3 s and "WHERE'S THE CASH?" at about 16.3-17 s, at the bottom of the frame. Crop the bottom 10% of the cohh 15.8 s and 27.9 s shots (raise y0 or lower h), or blur that band.
2. **There's a dark shot in the hook.** 4.53-5.4 s is the dark Bigfoot legs under a lone "6." caption. Replace it with a bright shot (lirik-01 21.5 s, the dog), and keep "GTA 6." in one caption chunk.
3. **Optional: trim the silent tail.** About 1 s of silence follows "alligator." (52.1-53.1 s). End at 52.4 s so the voice restarts on the loop at once.
