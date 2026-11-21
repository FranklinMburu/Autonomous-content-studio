# IntNext BLUEPRINT: what wins, what we make, how the critic gates it (21 Nov 2026)

Sources: the 4 analyst notes (A tips, B funny/NPC, C aura, D streamer/emotion), `summary.json` (36 references + our 3),
`meta.tsv`, our 3 best Shorts (`outours/*`: sheets viewed frame by frame), `ANALYTICS_21NOV.md`, `MASTER_PLAN.md`,
`PLAYBOOK.md`, `HOOK_BLUEPRINT.md`, `FORMAT_SPEC.md`, `SLATE.md`, `RULES_KAI_POOL.md`.
For the director, critic and editors. It replaces any rule in the older room files that it contradicts.

## 0. Read this first: how much to trust the numbers

- **Views are confounded.** We don't know channel sizes. Ages run from 1 to 203 days. Franklin picked the
  references as winners, so this is a survivor sample. The GTA 6 group is launch-week, when novelty is at its peak. A
  number that "separates" winners here is a hint, not proof.
- **No craft metric predicts views.** Spearman rank correlation with views across all 36 references:
  - cuts/10 s −0.15, median shot −0.04, first cut −0.08
  - sharpness +0.11, saturation −0.13, colourfulness +0.28, motion +0.06
  - LUFS +0.19, LRA +0.18, sound share +0.31
  - text share −0.08, loop similarity −0.19, like % +0.01

  Inside the 23 GTA-related references every |rho| is ≤0.21. **The winners are separated by content and structure
  (what happens, when, and what the text says), not by edit metrics.** That is the single biggest finding.
- **OCR bug: `text` share and OCR lines are partly wrong.** `tools/deep_teardown.py` writes every OCR frame to the
  same `/tmp/_ocr.png`, so videos torn down in parallel leaked text into each other. The evidence:
  - `ours-parrot-C1` OCR contains "POV: GEN Z MEETS" (DGjgD's caption).
  - Analyst C's DGjgD beat list quotes "hey handsome!", "GENERATOR! GENERATOR!" and "secret stash!". Those are our parrot clip's captions, not DGjgD's.
  - `ArYw4lzatNA` and `CHwDiB6HyI0` OCR contain our Kai "13 years of waiting… HDR CALIBRATION" box.
  - `ours-secrets1b` OCR contains HBQo's "JOIN PRIVATE MATCH / SPPED / Password".

  Trust the sheets (frames), not OCR text or `text` share. Fix: use a unique tmp file per process before the next teardown.
- **Our sharpness numbers can't be compared with the references.** Laplacian variance is computed at native
  resolution: ours are 1080x1920 (often upscaled stream video), most references are 608x1080. Compare ours only with ours.
- **Our own analytics:** 3 Shorts made 96% of ~3.7K views. Stayed-to-watch is 41–57%. Traffic is 94.9% Shorts feed.
  The audience is 100% new and mostly Brazil/Portugal (9:1 over the US). The main search term is "gta 6 kaicenat".

---

## 1. The ten laws (held in all four groups)

Strength: **[MANY]** means ≥8 references across ≥3 groups agree with no clear counter-example. **[SOME]** means 4–7
references or 2 groups. "Rests on 1–2" items are listed separately after the laws.

**L1. The premise is visible and named within 1.5 s. [MANY]**

Frame 0–1.5 s shows the conflict or the odd object, and text names it. No intro, no title card, no blur, no "nothing happens" opening.

| | Reference | What happens in the first seconds |
|---|---|---|
| Winners | T8F (7.0M) | head-hit kill at 0.8 s |
| | eSMw (517K) | mutant crab grabs Jason at 0.3 s, plus "$" |
| | SUiw (4.2M) | drop kick at 1.3 s with the streamer laughing |
| | aCt (46.7M) | "ASHTON HALL VS 2 BIKES" at 0.25 s over the lift |
| | HBQo (42.1M) | password box under Speed's grin, caption at 0.27 s |
| | LGAJ (2.5M) | PS5 under a running tap at 0.27 s |
| | DGjgD (8.4M) | Lucia aims a gun at the camera at 0.25 s |
| | YVEp (308K) | dog in goggles driving a jet ski at frame 0 |
| | OAQ (2.5M) | GTA 6 vs RDR2 panels read with zero words |
| Losers | qX (7.3K) | static title card for 5.6 s |
| | ArY (4.6K) | static title box, first cut at 8.9 s |
| | CHwD (5.5K) | 4.4 s of normal driving |
| | 6xe (16.7K) | 2–7 s of wading and staring at a wall |
| | nvQ (2.3K) | dark fade-in |
| | NpT (5.8K) | blurred grass, Bigfoot a speck |
| | 3dK and Gtk | open on GTA 5 footage (7.4K, 8.9K) |

Our analytics agree: 43–59% leave in the first second on all three of our best.

**L2. One payoff that is physical, close, and legible without sound. [MANY]**

Shown, not told.

| | Reference | Payoff |
|---|---|---|
| Winners | qdFB | NPC crashes the stolen bike at 17.5 s |
| | uytx | mugger slammed onto a bonnet at 11.5 s |
| | OAQ | croc drags him in, then "wasted" |
| | 5cn | scooter "wasted" |
| | SUiw | tiger leaps out of the van |
| | LH4T | "$1,200" wallet in green |
| | eSMw | code 00072, then "$8,000" |
| | T8F | Dismemberment row in the settings menu |
| | JhffeNS | rocket explosion fills the frame |
| | GVYc | "SEVEN MILLION DOLLARS" |
| | HBQo | lobby fills with strangers |
| Losers | NpT | Bigfoot never shown close |
| | CHwD | crash seen from far away |
| | 6xe | #1 glitch unclear |
| | 3dK | proof buried in B-roll |

Same content, different visibility: the jet-ski dog island got 4.8M (LH4T, wallet shown, human voice), 308K (YVEp,
faceless) and 2.3K (nvQ, a 5 s clip with no payoff).

**L3. Hold one open question and pay it late, at 60–95% of the runtime. [MANY]**

| Reference | Payoff time / length | Position |
|---|---|---|
| qdFB | 17.5/21 s | 83% |
| uytx | 11.5/16.5 s | 70% |
| k9d | 18.5–22/24 s | 77–92% |
| DayZ FFpE | 65/69 s | 94% |
| SUiw | tiger 74.7/79 s | 95% |
| eSMw | "$8,000" 58.7/60 s | 98% |
| GVYc | 6-cut burst 55.7/58 s | 96% |
| aCt | 4th race and 💀 | end |
| LGAJ | hope-then-crush 22.7/41 s, plus the deadpan button 38–41 s | 55%, then 93–100% |

Devices that hold the question: numbered rounds (aCt), "#1 SPOILER ALERT…its INSANE" (SUiw), a 5-slot ranking
template (LFjt), "two options… three seconds to decide" (DayZ), dramatic irony (HBQo, LGAJ).

**L4. Stop within 3 s of the payoff, with no outro. [MANY]**

Examples: qdFB ends 3.5 s after the crash, uytx 3 s after the slam, k9d on the fail screen, DayZ on the body, aCt on a 1 s 💀,
SUiw on the tiger, LGAJ on the last line, GVYc on the burst. The only CTA-plus-subscribe ending in the set is
qX's animated like/subscribe bar (7.3K). Loop **similarity** does not separate winners (see Myth 7). Ending fast does.

**L5. Selection beats editing: let the take run when the moment is good. [MANY, measured]**

- The 13 references under 1 cut/10 s have a median of **4.2M** views. That group includes 4 one-take videos: uytx 2.7M,
  esIs 464K, DayZ 8.9M, fK0 8.5M. k9d 31.6M has one cut.
- Cuts/10 s vs views: rho −0.15.
- Fast cutting works only as a **burst on a beat** inside aura edits (W330 5 cuts in 2.5 s, GVYc 6 in 2 s, JhffeNS 6 in 2.7 s).
  It is never the whole video.
- The craft in the Wisebenda pair (4.98M + 2.71M, 1 day old) is choosing a 16–21 s window and writing a label.

**L6. The text frames the idea; it doesn't describe the footage. [MANY]**

Winning text is written as:
- the viewer's reaction: "God dayym" 💀😭, "That death stare says it all"
- a known meme: "Goofy Oblivion NPC Moment", "Aura farming at this age is crazy", "POV: GEN Z MEETS GEN ALPHA"
- a stake or number: "7 million dollars per bullet", "THE OWNER." → "THE COLLECTION.", "ASTON HALL VS 2 BIKES"
- a promise: "#1 SPOILER ALERT"

Losing text is a generic label: "The crash physics are insane" (5.5K), "Ranking the Top 5 Clutch Moments" (16.7K),
"Ranking Craziest GTA 6 Moments" (2.3K). Text **presence** (90–100% everywhere) doesn't separate them (Myth 6).

**L7. Any line that carries the joke must be readable on mute. [MANY]**

- esIs has the best dialogue in the set but tiny native subtitles and a dark frame 0. It reached 464K while the analysts rate it a multi-million script.
- k9d (31.6M) is flagged "needs English version" for the same reason.
- Winners enlarge or recolour speech:
  - HBQo: 1–2 words on the divider, PASSWORD green, LEAKED red
  - DayZ: captor white with the current word red, hostage green
  - LGAJ: speaker tags plus *stage directions*
  - CkYQ: a zoomed band that doubles the subtitle size (5.9% likes)
  - qdFB: game subtitles recoloured light purple and enlarged
  - TOpWSZ: bracketed narration of silent action, "(47 TAKES OUT SYRINGE…)"
- Our watch time is 67% phone and our audience is mostly Portuguese-speaking, so muted reading matters more for us than for them.

**L8. Concrete nouns, numbers and names beat adjectives, in the title and on screen. [MANY]**

- Winning examples:
  - money: "$8,000", "00072", "$1,200", "$1,218", "7 million dollars for one gun", "55 000 000 €"
  - count: "5 Things", "4 MINUTES"
  - names: "Speed… Ashton Hall", "Speed… Jynxzi"
  - objects: "PS5 with SOAP", "mobility scooter", "Dog Who Drives Jet Ski"
- Losers: "Broke the Biggest Rule" 7.4K, "INSANE" 5.5K, "Craziest" 2.3K, "Fast & Furious Car Location" 4.6K.
- Ours: "4 MINUTES" (1.2K) and "$1,405" (1.2K and climbing) are our two top titles. The abstract reaction titles (SHOCKED, PANICKED) got 0–12 views.

**L9. A broad premise beats a niche one. [SOME]**

Broad premises: money, status reversal or contest, a relationship, a taboo, "you didn't know", a famous name.
- Tips group: 2 of 3 winners are money; 0 of 6 losers are. The losers were gym, UFO, train AI, a car location, Bigfoot.
- Streamer group: two famous names in a contest (46.7M, 42.1M); a relationship (PS5 soap 2.5M, married ranking 12M).
- Aura group: Superman, John Wick, Terminator, Hitman.
- Caveat: confounded with channel size.

**L10. Own the moment: be early, be the first-hand version, don't repost. [SOME, strong single proofs]**

- The jet-ski dog: first-hand human version 4.8M vs a faceless retell 308K vs a list clip 2.3K.
- Our FORMAT_SPEC found the pixel-identical alligator edit got 306K for one uploader and 816 for another.
- The re-uploads that did well (LGAJ 0.81% likes, K5q "Cred:") rode launch-day timing.
- The Wisebenda clips were 1 day old at the peak of GTA 6 novelty.

So for a moment that has already been clipped, add something new (a streamer's first-hand reaction, a number, a
comparison) or skip it.

**Rests on only 1–2 examples (use, but don't call it a law):**

| Pattern | Evidence |
|---|---|
| Two-colour speaker captions, explicit "two options" plus a spoken 3-second countdown, ambiguous twist ending (comment debate) | DayZ only (8.9M, 3,670 comments, 3.88% likes) |
| Stacked split: cause on one panel, reaction on the other, caption on the divider | HBQo (42.1M); partly SUiw (4.2M, facecam on 2 of 5 clips) |
| A closing first-person "I'm at a loss for words" lifts likes | LH4T only (6.18% likes) |
| A stacked comparison (GTA 6 vs another game, same situation) | OAQ only (2.5M); we have no RDR2/GTA 5 footage |
| An aura edit on GTA 6 footage | DGjgD only. The other 4 aura winners are movie scenes we must not reupload. |
| A mid-video "…JUST WATCH WHAT HAPPENED NEXT" line; a 💀 sting as the end card | aCt only |
| A real-world fact twist ("Florida has a real dog island… shipwrecks since the 1700s") | YVEp only |
| Asterisk action labels (*FAILS*, *MEANWHILE*); speaker-tag screenplay captions | aCt; LGAJ |
| A ranking template with cryptic labels filled 5→1 | LFjt (12M) and SUiw (4.2M), but 6xe and nvQ used lists and lost. The promise and a strong #1 are what made it work. |
| Portuguese text helps us | Our analytics only (Brazil 9.7% of views, 42% stayed; Portugal 2.8%, 69% stayed). Untested. |

---

## 2. Myths our playbook believed that the data contradicts

| # | Our belief (where) | What the data shows | Verdict and new rule |
|---|---|---|---|
| M1 | "Cut every ~2–2.5 s, 4–5 cuts/10 s, longest shot ≤7 s" (MASTER_PLAN structure; COMPONENTS #6 pacing; copied from COLETHEMAN) | ≥1M median **1.02 cuts/10 s** vs <100K median **2.42**. Under 1 cut/10 s: 13 videos, median 4.2M. 4.5+ cuts/10 s: 6 videos; besides 4 movie edits only DGjgD wins, and the GTA tips with 4.9–6.7 cuts/10 s (Gtk, qX, j_Sx) got 7–26K. Longest shot ≤7 s is broken by T8F (17.4 s take, 7.0M), W330 (28.4 s, 10.2M) and DayZ (69 s, 8.9M). | **Myth.** COLE's pace suits his narrated list, not as a law. New rule: no **dead** stretch (>2.5 s with no new event, caption or line). Cut only when the next shot carries the next beat. Bursts are allowed only on a payoff or beat drop. |
| M2 | Sharpness and picture quality are levers (teardown compares sharpness; FORMAT_SPEC QA) | rho +0.11. Sharpness <500: 6 videos, median **8.4M** (DGjgD 173, GVYc 433, DayZ 402). Sharpest videos: YVEp 2400 got 308K, 6xe 2311 got 16.7K. Luke (664) beat VANCE (2400) 15x with the same discovery. | **Myth as a lever.** True only as **legibility of the payoff object** (Bigfoot as a speck lost; our parrot's dark, half-black 7–12 s lost). Gate brightness and size of the subject, not global sharpness. |
| M3 | "Lists 60–70 s; streamer clips under 40 s; 20–40 s for how-it-works" (MASTER_PLAN, PLAYBOOK #7) | Views are bimodal by length: ≤25 s has 8/9 ≥1M; **25–45 s has 3/12**; 45–65 s has 7/12; 65–90 s has 3/3. Long ones win only when the question is held (Luke escalation 79 s, SUiw "#1 spoiler" 79 s, DayZ countdown 69 s, aCt numbered races 55 s). The 25–45 s band holds most launch-week tips (confound), but its 3 winners (HBQo 42 s, LGAJ 41 s, fK0 35 s) are all stories. | **Partly a myth.** A single moment runs **15–25 s**. A story or list runs **45–65 s only with an on-screen promise or counter**. Never pad to 30–40 s: a 30–40 s clip must be a complete story. |
| M4 | "Narrator voice" is a title/hook red flag (HOOK_BLUEPRINT red flags) | Narrated winners: T8F 7.0M (first-person "I learned"), LH4T 4.8M, eSMw 517K, GWIH 99K. Our narrated list is our #2 Short. What loses is the **faceless retell of someone else's discovery** (YVEp 308K vs LH4T 4.8M). | **Myth.** Narration is right for tips and lists. Make it first person ("streamers found…", "here's what I found") and splice the streamer's **real line** in as each item's receipt. |
| M5 | "Full 9:16, never letterbox or square, no blur bands" (PLAYBOOK D-rules; HOOK_BLUEPRINT) | 9 of 21 ≥1M references are not 9:16: aCt 46.7M 3:4, HBQo 42.1M 3:4, k9d 31.6M 4:5, GVYc 24.9M 720x746, JhffeNS 17.3M 720x800, W330 10.2M 1:1, fK0 8.5M, DGjgD 8.4M 3:4, TOpWSZ 3.2M. What hurts is a **small subject**: ArY uses ~45% of the screen and has no captions; K5q is square and quiet at −22.9 LUFS. | **Myth as stated.** New rule: the main subject fills ≥60% of the frame's width at its widest moment. The content area is ≥4:5 tall. Blurred filler bands are ≤10% of the height. Kai C01 wastes ~25% of the frame on a bottom blur band. |
| M6 | "Text on 95–100% of seconds; word-by-word captions on everything" (FORMAT_SPEC, PLAYBOOK #9) | Text presence doesn't separate winners (B group ~100% for winners **and** losers; Gtk 100% at 8.9K; GVYc 52% at 24.9M; rho −0.08, contaminated by the OCR bug). The Wisebenda winners and k9d use **one static label** plus game subtitles, with no word-by-word captions. | **Myth as a universal rule.** Text must frame the idea (L6) and make every joke-carrying line readable (L7). Word-by-word only for narration and streamer speech. Visual-gag clips use a static label. |
| M7 | "Make the last frame flow into the first: loop" (ANALYTICS #4; earlier critic notes) | Loop similarity: ≥1M median 0.74 vs <100K median 0.77, rho −0.19. Gtk has 0.85 plus a perfect loop and got 8.9K. | **Myth as measured.** What matters is L4 (stop ≤3 s after the payoff). A seamless loop is a free bonus when the first and last shots match naturally. Don't spend editor time on it. |
| M8 | "−14 LUFS two-pass loudnorm is a quality lever" (COMPONENTS #8) | LUFS rho +0.19, range −32.7 (uytx 2.7M) to −6.2 (cj- 2.6M). T8F is −26.8 at 7.0M. | **Neutral hygiene, not a lever.** Keep −14 because YouTube normalises down only and it is safe. Quiet audio hurt only where speech carried the joke and wasn't captioned (esIs −27.6, K5q −22.9). |
| M9 | "Single streamer reactions are dead; stop making them" (ANALYTICS #1) | Our reactions got 1–12 views, but the biggest references are streamer clips (aCt 46.7M, HBQo 42.1M). Those are **stories with a visible cause** (contest, mistake, consequence), not reactions. CHwD (a neutral streamer face over a far-away crash) got 5.5K. | **Half-myth.** Stop **reaction-only** clips. Make **streamer story clips** (Format F3): cause on screen, question planted, consequence shown. |
| M10 | "Add a natural question ending to get comments" (ANALYTICS #3) | Comments came from debate and ambiguity: T8F "didn't know" list 1,598; DayZ twist 3,670; aura/meme edits 1.9–3.4K. The explicit question endings are weak: Gtk "WOULD YOU FOLLOW THE LIGHT?" 4 comments; K5q "What would you do" 232. | **Unproven.** Do it as a pinned comment that takes a side ("Kai's settings were right. Fight me.") rather than an on-screen question that delays the end. |
| M11 | "First cut at 2.6–3.4 s (COLE median 3.0)" (FORMAT_SPEC) | First cut: rho −0.08. Many winners never cut. | **Irrelevant.** Measure **first event** (first readable action or caption-plus-subject) at ≤1.5 s instead. |
| Kept | "No question titles", "name first plus GTA 6", "concrete noun" (HOOK_BLUEPRINT, PLAYBOOK) | 0 of 21 ≥1M titles are questions. The 3 question titles: 8.9K, 269K, 308K. Names first: aCt, HBQo. Search term "gta 6 kaicenat" is 11.9% of our search traffic. | **Confirmed, keep.** |

---

## 3. Five formats, ranked

Each format is ranked by expected views for a 3-subscriber channel (feed-only distribution, so the swipe rate decides) and
by fit with our footage (streamer VODs with facecams, Rockstar trailers, ffmpeg tools, Kokoro narrator, library music at upload).

| Rank | Format | Expected for us | Footage fit | Kai pool? | Why this rank |
|---|---|---|---|---|---|
| 1 | F1 Money tip with on-screen receipts | High: our fastest climber (parrot 77% viewed); eSMw 517K and GWIH 99K on day 1-2 | Medium: needs a verified method in a VOD | only if it's Kai's play | Utility is language-neutral (Brazil), searchable and gives a clear payoff |
| 2 | F3 Streamer STORY clip | High ceiling (42–47M refs); our Kai irony is our #1 (1.2K) | High: VODs with facecams | **yes** | Earns pool money; a known name; dramatic irony is in our footage |
| 3 | F4 Escalating or ranked list with a saved-for-last promise | Medium-high (T8F 7.0M, SUiw 4.2M, LFjt 12M); our #2 (1.1K) | High: listshort.py exists | yes, if Kai is the through-line | Proven on our channel; the fix (promise plus order) is cheap |
| 4 | F2 Single NPC/physics payoff (Wisebenda) | High ceiling and cheap (qdFB 5.0M, uytx 2.7M, k9d 31.6M, 5cn 1.2M) | Medium-low: our gameplay sits under facecams; NPC-centric windows have to be hunted | only Kai VODs | The best cost/ceiling ratio, but we don't yet have a qualifying moment in hand |
| 5 | F5 GTA 6 trailer aura/meme edit (DGjgD) | Variable: 8.4M proof but only one GTA 6 example; the trailer is a month old and heavily edited by others | Medium: we have trailers, but music is added at upload, so beat sync is approximate; possible Rockstar Content ID claim | no | Highest like rate (3.54%) and comments, but most uncertain for us |

Text spec shared by all formats (1080x1920):
- **Safe zone:** x 6–88% (the right ~12% is under the like/comment buttons). y 10–78% (the bottom ~22% is under the title and channel).
- **Word-by-word caption:**
  - Anton, Bebas Neue or Montserrat Black (free fonts). Cap height 80–95 px (~4.5% of H). White fill, 7 px black stroke, soft shadow.
  - 1–3 words per chunk; one keyword coloured: money #39FF6A, names #FF4D6D, warnings/fails #FFD60A.
  - Centre at y ≈ 58–62%, unless that covers the payoff object; then move it to the divider or to y ≈ 30%.
- **Static header/label:** 56–64 px, white on a black or white band, top at y 10–16%. 2–7 words plus 1–2 emoji.
- **Never** put a caption over the payoff object, never let a word run past the safe zone, and never leave the source's own burnt-in subtitles visible under ours.

### F1. Money tip with on-screen receipts (rank 1)
Model on: **eSMwSZ1avbU** (517K: monster plus money promise at 0.3 s, a map at 3.7 s, exact code, "$8,000" at the end),
**GWIHgzGkIzw** (99K: map pin at 2 s, obstacle → solution → cash), **T8FzQ5cW-94** (receipts shown big).
Avoid GWIH's 3:4 frame and j_Sx's tiny lime text.

- **Length:** 18–30 s for one method. 45–60 s only for a multi-stop route with a running total.
- **Frame 0:** the money receipt already on screen: the "+$1,405" HUD toast or cash pile, **or** the strange object
  (the parrot) with "+$1,405 💰" stamped over it. Brightness mean ≥80/255 (lift gamma 1.2–1.3, saturation +15%).
  Never a dark cage or a walking back.
- **0–2 s:** the header "FREE $1,405 💰" (top, static, the whole video). The first spoken/caption words state the value
  and the object: "this parrot pays you 1,405 dollars".
- **Beats:**

  | Time | Beat |
  |---|---|
  | 0–1.5 s | receipt flash and value |
  | 1.5–3.5 s | where: map pin or a named area, shown big |
  | 3.5 s to (end−5 s) | numbered steps, ≤4 s each, every step with its own receipt shot (prompt, door, vent, code); the streamer's real line as an audio receipt where available ("GENERATOR!") |
  | end−5 to end−1.5 s | the payoff again, held ≥1.5 s: HUD "+$X" plus the cash on screen; a running total if there's more than one stash |
  | last 1–1.5 s | hard cut |

  No stretch >2.5 s without a new step or line (the parrot's 7.2–12.5 s walk breaks this).
- **Text:**
  - top: the static value header, white band, 60 px
  - middle: word-by-word narration, money words green
  - a step counter "1/3, 2/3, 3/3" under the header
  - the HUD money toast punched in at 1.3x
- **Audio:**
  - Kokoro narrator, continuous, ~165–180 wpm, sentence gaps ≤0.4 s
  - keep the game's cash pickup SFX and the source character's line, ducked under the voice
  - −14 LUFS
  - a library track at upload, low (beat-neutral lo-fi/phonk)
- **Ending:** the last frame is the cash HUD plus the location. No outro. Pinned comment with the exact location and "worked for me?".
- **Title:** `Free $[exact] In GTA 6: [the odd instruction] [object emoji]💰` or `This GTA 6 [object] Pays You $[exact] [emoji]`.
  - "Free $1,405 In GTA 6: Ask The Parrot 'Where's The Cash?' 🦜💰" (our template; parrot footage, cohhcarnage-02)
  - "This GTA 6 Dog Digs Up A Wallet With $1,2XX In It 🐕💰". Only if our Lirik dog footage (lirik-01 or the laptop helper)
    actually shows the island, the wallet and the HUD amount. Use the exact HUD number. If our footage only has the ride to shore, don't make it.
- **Language test (optional, one Short):** Portuguese header plus captions ("DINHEIRO GRÁTIS: $1.405 💰"), English title.
  Judge on 72 h stayed-to-watch for Brazil/Portugal vs the English version.

### F3. Streamer STORY clip: contest, a mistake the viewer sees first, a countdown (rank 2; the Kai pool vehicle)
Model on: **HBQo-U7Q0No** (42.1M: stacked cause and reaction, 1–2 word coloured captions on the divider, mistake → visible
consequence), **aCt-AwZi380** (46.7M: set-up → fail → MEANWHILE → numbered rounds, asterisk labels), **FFpEdgNtLk4**
(countdown/choice, two-colour speakers), **LGAJcSVguwE** (dramatic irony, speaker tags).

- **Length:** 22–35 s for one mistake. 40–55 s only with numbered rounds or a visible counter.
- **Frame 0:** both halves already loaded. TOP 45%: the streamer's face, cropped head and shoulders (face ≥30% of panel width).
  BOTTOM 45%: the exact screen that holds the irony (the menu, the "press L" prompt, the bank app), cropped so its text is
  ≥40 px tall. A 4 px divider. No blur bands.
- **0–2 s:**
  - a top label (≤7 words) states the stake or irony, e.g. "13 years of waiting. 4 MINUTES in settings 💀"
  - the first spoken line is captioned on the divider by 0.3 s
  - add a **visible counter** if one is true: "⏱ 0:00" counting up, or "my bad ×1 … ×9"
- **Beats:**

  | Time | Beat |
  |---|---|
  | 0–3 s | the set-up line plus the cause on screen |
  | 3 s to 70% | escalation: each new line tops the last, the counter climbs, the bottom panel swaps to the next proof every 2–5 s (HBQo swaps every 1–3 s), punch-in 1.15x on the face at each punch word |
  | 70–90% | consequence or payoff: the thing the viewer saw coming happens; the biggest face, held ≥1 s |
  | last 0–2 s | a button line or 💀 sting, then a hard cut |

- **Text:**
  - word-by-word on the divider, 1–2 words, keyword colours
  - streamer = white with the active word red; second speaker or NPC = green (DayZ)
  - asterisk labels for beats (*STILL IN SETTINGS*, *MEANWHILE CHAT*) in yellow
  - the top label stays the whole video
  - English captions even when the speech is clear
- **Audio:** the original stream audio, levelled; −14 LUFS; bleep slurs; a library track at upload only if the stream audio has gaps.
- **Ending:** on the payoff face plus the last line. Pinned comment that takes a side.
- **Title:** `[Streamer] [concrete verb] [specific thing] In GTA 6… Then [consequence] 😭` plus `#KaiCenat #ad` for pool clips.
  - "Kai Cenat Spent 4 MINUTES In GTA 6 Settings Before Playing 😭 #KaiCenat #ad" (kaicenat-09, the structure fixed per §4)
  - "N3on Robbed A Bank In GTA 6 Before Learning The Controls… 'What Is L?!' 😭" (n3on-03 48–73 s; only if the on-screen
    prompt showing L is visible, so the viewer sees the answer before N3on does)
- **Kai pool:** Kai's face is on screen ≥90% of the seconds, "Kai Cenat" is in the top label or title, `#KaiCenat` is in the
  title or description, and there are no logos (crop out channel/watermark logos). Positive or affectionate framing only.

### F4. Escalating-discovery or ranked list with a saved-for-last promise (rank 3)
Model on: **SUiwFz6SQtU** (4.2M: persistent banner "#1 SPOILER ALERT…its INSANE", best clip last), **T8FzQ5cW-94**
(7.0M: "5 things", a receipt per item, settings-menu proof), **LFjtt8hQMt0** (12M: 5-slot template filled 5→1, cryptic
labels), **LH4T5ngfVXw** (each reveal tops the last). Avoid **6xe1HngB418** and **nvQ-xtnAXuc**: no promise, weak #1, 5 s items.

- **Length:** 45–60 s. 4–5 items, 8–12 s each. Cut an item rather than keep one without a receipt.
- **Frame 0:**
  - a 1.0 s **teaser of the #1 payoff** (the strongest image; for us that's the alligator lunge or the dog driving the jet ski)
  - under it the promise header "5 GTA 6 SECRETS 🔍 (#1 is unreal)"
  - a 5-slot list down the left (filled as you go), 40 px numbers
- **0–2 s:** the narrator's first words are the promise plus the #1 hint: "Streamers found five secrets in GTA 6, and number one
  is a dog that drives you home."
- **Beats:**

  | Time | Beat |
  |---|---|
  | 0–1 s | #1 teaser |
  | 1–3 s | promise |
  | then | items **5 → 1** in order of increasing payoff, each one header (top) → claim (≤3 s) → receipt shot ≥1.5 s (the creature or prize big, the streamer's real reaction line) → slot filled |
  | final 10–12 s | #1, the longest and best item |
  | after #1's payoff | end ≤2 s later |

- **Text:**
  - item header at the top in white heavy caps with an emoji ("3. DOG UBER 🐕"), 60 px
  - word-by-word narration in the centre, keywords coloured
  - left slot list
  - the persistent promise stays at the top during 0–3 s, then lives in the slot list ("#1 ???")
- **Audio:** Kokoro narrator, continuous, −14 LUFS. The streamer's own reaction line spliced in (≤1.5 s) inside each item as proof (L10).
- **Ending:** #1 payoff → one closing line that ties back to the teaser ("…and that dog still drives better than you"), then a cut.
- **Title:** `[N] GTA 6 [Secrets/Things] [Streamer names] Found` (names searchable), or `Ranking [noun] In GTA 6`.
  - "5 GTA 6 Settings Kai Cenat Changed Before Playing ⚙️ #KaiCenat #ad" (kaicenat-09 plus fanum-01 menus: UI text size,
    HDR, paper white, minimap, motion blur off; Kai's face top panel throughout; #1 = the one he fought hardest, "NO NO NO NO")
  - "Lirik, Cohh & Speed Found 5 Secrets In GTA 6 (#1 Drives You Home) 🐕". This reuses secrets1b items, so post it only
    after 7+ days and only re-ordered with real receipts. Otherwise skip it (L10).

### F2. Single NPC/physics payoff clip, Wisebenda style (rank 4)
Model on: **qdFB8OEuet0** (4.98M), **uytxUcsxXvs** (2.71M), **k9d_A6m8W1s** (31.6M), **5cnouD4GH8Y** (1.18M),
**CkYQQSTwxqY** (226K but 5.9% likes: what to fix is in note D7).

- **Length:** 15–25 s. One take, 0–2 cuts (one allowed to remove dead air before the set-up).
- **Frame 0:** gameplay already in motion with the NPC in frame (the carjacker, the mugger, the cop). The full-height crop
  centres on the NPC/player pair, which fill ≥50% of the frame height. If the source is a stream, crop the game only. A facecam
  is optional and small (≤20% of height, a corner) unless it's a Kai pool clip, where Kai's cam is a 30% top band.
- **0–2 s:** the top meme label is on by 0.3 s. The NPC's first threat or line is captioned big by ~2 s.
- **Beats:**

  | Time | Beat |
  |---|---|
  | 0–2 s | the situation plus the label |
  | 2 s to 65% | tension: the NPC acts tough or absurd, each line enlarged |
  | 65–85% | the physical payoff (crash, slam, "wasted", fail screen), close |
  | +1–3 s | the player just standing there, then a cut |

  Trim every gap >1.5 s with no line or motion (esIs's mistake).
- **Text:**
  - the top label, 2–5 words plus 1–2 emoji, written as the viewer's reaction or a gamer meme ("Goofy Oblivion NPC Moment 😭",
    "\"God dayym\" 💀😭"), white 60 px on a black band 12% tall, kept the whole video
  - NPC dialogue re-typed big, 1–3 words, light purple #C9A7FF or white, stroked, lower-middle
  - no narration
- **Audio:** game audio only, levelled to −14 LUFS. Optional library track added at upload at a low level.
- **Ending:** ≤3 s after the payoff.
- **Title:** an ironic understatement or meme phrase plus 1 emoji, ≤6 words ("A Perfectly Valid Reaction 😭", "Oblivion Level AI In GTA 6 💀").
  - "GTA 6 Jail Was Too Full To Keep Him 💀" (agent00 footage, C11 window; the NPC line is the payoff, Agent00's face small)
  - "'I'm Sorry, He Shot Me FIRST!' 😭" (n3on-07 8–31.5 s; borderline F2/F3, because the payoff is N3on's line, not an NPC action)
- **Honest gap:** none of the moments we have catalogued has a Wisebenda-grade **physical NPC payoff**. We need a hunt (see §6, Short 4).

### F5. GTA 6 trailer aura/meme edit, DGjgD style (rank 5)
Model on: **DGjgDx8w6ws** (8.4M, 3.54% likes, 3,433 comments). Borrow the structure only from **JhffeNS2EnA** (build → drop →
hero entrance → iconic line), **W330Tiq7j7k** (a pinned opinion caption for 24–36 s, a burst on the final drop) and
**GVYcVIQlb3g** (one number promise, colour-coded quoted lines, a 6-cut burst in the last 2 s). Never use their movie footage.

- **Length:** 18–24 s (meme edit). The 45–58 s "story aura" version is not worth it until a short one works.
- **Frame 0:** a trailer shot with direct menace or eye contact (Lucia aiming at the camera; Jason's stare), already moving.
  Black frame 0 for ≤1 frame only.
- **0–2 s:** the POV/meme caption on by 0.25 s in three colours, lower-middle ("POV:" white, the key phrase green, the
  punch red). It is replaced by ☠️ at the drop.
- **Beats:**

  | Time | Beat |
  |---|---|
  | 0–5.0 s | build: one shot, the trailer's own line audible, lower energy |
  | 5.0 s | **drop**: a white flash frame (2 frames) |
  | 5–20 s | one character per ~2.3 s, each closed by a 0.5 s insert and a ☠️ on the beat |
  | final 2 s | ≥5 cuts at 0.4–0.5 s on the last hit |
  | end | the opening character, so it loops (0.9 similarity is easy here) |

- **Grade:** pick one per video. Warm teal-orange with saturation 105–140, or desaturated contrast (sat 55–70). Never the raw trailer grade.
- **Text:**
  - the POV caption 0–5 s
  - quoted trailer lines in caps with quote marks, 1 per character max
  - ☠️ or 💀 as the beat marker
  - no word-by-word narration
- **Audio:** the trailer dialogue in the build. The music must come from the Shorts library at upload, so **we can't sync
  in ffmpeg**. Workaround (unproven):
  - cut on a fixed 0.5 s grid (120 BPM) with the drop at exactly 5.0 s
  - at upload, choose a library phonk/montagem track near 120/240 BPM and set its start so its drop lands at 5.0 s (check by watching the preview)
  - master the trailer audio at −12 LUFS so the music sits on top

  If the track can't be aligned, don't post it.
- **Title:** `"[Meme sentence]" 💀 | [Jason/Lucia] | GTA 6` with hashtags #gta6 #edit.
  - "Lucia Did This On Day One 💀 | GTA 6" (trailer 1 robbery shots, Lucia's entrance on the drop)
  - "POV: Vice City Meets Florida Man ☠️ | GTA 6 Trailer" (one trailer character per beat, a ☠️ on each)
- **Risks:** Rockstar may Content ID-claim trailer footage (a claim costs us nothing, but a block or strike would hurt): post one
  and watch for 48 h before a second. Not Kai-eligible. The trailer was released a month ago and is heavily edited by others (L10 risk).

---

## 4. Gap analysis of our three best Shorts

Scores are 1–10, on the same scale the analysts used for the references.

### ours-kai-C01: "Kai waited 13 years… 4 MINUTES in the settings menu" (1,210 views, 73.7% viewed, 53.4% stayed)
Measured: 24.2 s, 3 cuts, first cut 6.07 s, motion 0.6 (near-static), −14.0 LUFS, a **silence at 4.0–5.0 s (−53/−50 dB)**,
loop 0.87. From the frames, the layout is:
- purple blur band with the white caption box: y 0–12%
- Kai cam: y 12–43%
- menu: y 43–75%
- **brown blur band: y 75–100%**

**What's right**
- The best idea on the channel: irony with a number (L8) and dramatic irony. Viewers see a "13-year" fan burn time on HDR sliders.
- The cause (the menu) and the reaction (Kai) are on screen together.
- The static white-box label is in the format the winners use (5cn, k9d).
- 73.7% viewed means the idea holds the people who stay.

| Hook | Story | Editing | Visual | Text | Audio | Ending/loop |
|---|---|---|---|---|---|---|
| 5 | 5 | 4 | 4 | 5 | 5 | 4 |

**Biggest misses and fixes**
1. **Frame 0 and the first 5 s don't show the joke escalating** (L1, L3). Frame 0 is Kai mid-gesture over a generic
   "NAVIGATION EXPERIENCE" menu, a 12-word label has to be read, and then there is 1 s of silence at 4–5 s. Nothing climbs, so
   the retention curve "slides steadily" with no hold.
   - Fix: add a big **elapsed-time counter** on the divider ("⏱ 0:12 … 4:31") that jumps at each cut (true VOD times: 633 s → 901 s).
   - Open on the busiest frame (the HDR slider moving plus a talking face).
   - Close the 4–5 s gap.
   - Order the beats so each is more absurd than the last: text size → brightness → black levels → paper white "NO NO NO NO" → "MY RUN NEEDS TO BE X".
2. **About 37% of the frame is filler and Kai's face is small** (M5). The bottom 25% is a blur band (also under YouTube's
   title overlay), the top 12% is a blur band, and the face panel is only 31% of the height.
   - Fix: face panel 45% (head and shoulders), menu panel 40% cropped so the slider names are ≥40 px, label on a 10% white band, no blur bands.
3. **Most of Kai's funny lines aren't readable muted** (L7). Only ~4.5 s of 24 s carries speech captions ("LET'S ELEVATE THE
   LIFESTYLE", "NO NO NO NO", "MY RUN NEEDS TO BE X"). "I like me a medium", "levels of the black" and "max brightness"
   aren't captioned.
   - Fix: word-by-word captions on every Kai line, keyword colour (MEDIUM, BLACK, PAPER WHITE in yellow).
   - Also, the ending is a controller-layout screen with no button: end on "MY RUN NEEDS TO BE X" plus 💀 (or the "motion blur off" line at VOD 139 s), with the counter frozen at "4:31".

### ours-secrets1b: "5 GTA 6 Secrets Streamers Found" (1,109 views, 57.2% viewed, 56.8% stayed; stalled after ~12 h)
Measured: 52.6 s, 3.42 cuts/10 s, −14.2 LUFS, loop 0.86. From the frames:
- frame 0 is the alligator lunge, with "THIS ALLIGATOR IS SECRET NUMBER ONE OF FIVE…" word by word from 0.27 s
- headers "1. ALLIGATOR ATTACK 🐊 / 2. THE PARROT PAYS 🦜 / 3. DOG UBER 🐕 / 4. PET SNAKE 🐍 / 5. BIGFOOT IS REAL 👣"
- the closing line "because it all started with this alligator" loops back to the alligator

**What's right**
- Frame 0 is a creature in motion.
- Text is on screen almost all the time, with coloured keywords.
- Headers with emoji, continuous narration, and a story-loop closing line. This is the closest of our Shorts to the T8F and COLE structure.

| Hook | Story | Editing | Visual | Text | Audio | Ending/loop |
|---|---|---|---|---|---|---|
| 6 | 4 | 6 | 5 | 7 | 6 | 6 |

**Biggest misses and fixes**
1. **The order runs backwards, with no promise** (L3; SUiw vs 6xe). The strongest image (the alligator) is spent first. The
   weakest item (Bigfoot: an empty airboat at 39.2–41.6 s, a dark leg that reads as a tree trunk, "blacked out") is last. There is
   no on-screen reason to stay. Counting 1→5 tells the viewer "5 of the same".
   - Fix: count down 5→1 with "#1 ???" in a slot list.
   - Tease #1 for 1 s at frame 0 and keep the strongest receipt for #1 (the alligator or the dog).
   - Drop Bigfoot unless the legs are shown big and bright (FORMAT_SPEC fix: lirik-04 10.4–11.6 s, gamma 1.25).
2. **Payoffs are told, not shown** (L2).
   - Parrot: dim; "+$1,405" shows only for ~0.8 s at 22.1 s.
   - Snake: the rat being eaten isn't visible ("SHE EATS IT" over an empty tank at 37.3–38.9 s).
   - Bigfoot: not visible.
   - Fix: every item gets a ≥1.5 s receipt shot (the creature or money big, brightness ≥80). An item without one is cut, and the list becomes 4 items/45 s.
3. **A faceless retell of other people's discoveries, with generic packaging** (L10, L8). The voice is the TTS narrator,
   streamers are named only in passing ("LIRIK CAME UP"), and the title "Streamers Found" has no searchable name. Our own
   search traffic is "gta 6 kaicenat".
   - Fix: splice each streamer's real 1–1.5 s reaction line as the item's receipt ("is that a dog?", "GENERATOR!").
   - Name them in the title ("Lirik, Cohh & Speed Found…").
   - Narrate in the first person plural ("streamers found…, here's the proof").

### ours-parrot-C1: "Free $1,405… ask the parrot" (~1.2K and climbing; 77.3% viewed, 40.9% stayed)
Measured: 18.5 s, 6 cuts, −14.1 LUFS, no silences, loop 0.80.
- **Brightness 26–50/255 for 0–9 s**, colourfulness 14 (the dullest of all 39 videos).
- Sharpness collapses to ~5–9 at 7.2–12.3 s: the camera clips through a wooden post at 8.5–9.4 s and the frames are soft.

From the frames:
- 0–2.2 s: header "ask the parrot 'where's the cash?' 🦜" plus "hey handsome!"
- 2.4–3.5 s: WHERE'S THE CASH?
- 3.7–7.2 s: "GENERATOR! GENERATOR!"
- **7.2–12.5 s: no text**, walking to the vent
- 12.5–15 s: "yes! secret stash!"
- 15.2–18 s: "+$1,405 💰", plus "did you walk past this bird?" from 16.3 s

The source's own burnt-in subtitles show at 1.1–2.1 s.

**What's right**
- Money plus an exact number plus an odd object (L8, L9).
- A real step chain (parrot → generator → vent → cash).
- 18.5 s.
- 77% viewed: the best content-retention on the channel. It's the format with momentum.

| Hook | Story | Editing | Visual | Text | Audio | Ending/loop |
|---|---|---|---|---|---|---|
| 4 | 7 | 5 | 3 | 4 | 5 | 6 |

**Biggest misses and fixes**
1. **The value arrives at 15.2 s, but 59% decide in the first second** (L1). Frame 0 is a dark cage with a small parrot and an
   instruction without a reward.
   - Fix: frame 0 = "+$1,405 💰" over the parrot (or the open vent with cash).
   - Static header "FREE $1,405 💰" from 0.0. The first caption words: "this parrot gives you 1,405 dollars".
   - Lift the brightness to ≥80 (gamma 1.25, saturation +15%).
2. **A 5.3 s dead stretch and an unclear "how"** (7.2–12.5 s with no text, a blurred clip-through, no stated step).
   - Fix: numbered step captions ("1. ask the parrot → 2. go behind the generator → 3. open the grate"), with the grate
     prompt punched in.
   - Cut the post clip-through.
   - Add a narrator or keep the game lines as receipts. Hide the source's burnt-in subtitles (crop or cover).
3. **No location and no receipt hold.** The "+$1,405" sits over a walking-away shot, never over the cash at the vent. The viewer
   can't act on it, and there are 0 comments.
   - Fix: map pin or a named area at 1.5–3.5 s (if the footage has it).
   - Hold the HUD toast plus the cash ≥1.5 s at the vent, then cut within 1 s.
   - Pinned comment with the location.

**Rule that comes out of all three:** our ideas are right. Frame 0, the order and legibility lose the viewers.

---

## 5. Quality gate: the critic applies all 15 before anything ships (any NO = no ship)

Measure with ffmpeg and teardown (after the OCR tmp-file fix), the ASS caption file and the frames. Record the numbers in the Short's json.

1. **Premise sentence written:** "[who] [does what] in GTA 6, then [consequence]". The payoff object is named, and the
   format (F1–F5) is declared. YES/NO
2. **Frame 0 shows what the text names:** at t=0.0 the subject named by the label/first caption is visible and moving. No black,
   title card or blur. Mean brightness of 0–2 s ≥70/255. YES/NO
3. **First event ≤1.5 s:** a readable action, the money receipt, or the conflict appears by 1.5 s. Label or first caption on by ≤0.3 s, ≤7 words. YES/NO
4. **No dead stretch:** no window >2.5 s with no new caption word, no cut, no new line and frame-diff motion <2 (Kai C01 4–5 s
   silence fails; parrot 7.2–12.5 s fails). A deliberate suspense pause is allowed only if the director flags it. YES/NO
5. **Payoff legible on mute in ≤2 s:** the payoff object is ≥15% of the frame height, on screen ≥1.0 s (money ≥1.5 s), brightness
   ≥70, and not covered by text. YES/NO
6. **Payoff position:**
   - single clip: the final payoff starts at 60–95% of the runtime
   - list: items run in increasing strength, #1 is the strongest and is promised in the first 3 s
   - story: a question or counter is planted by 2 s

   YES/NO
7. **Ends ≤3.0 s after the final payoff:** no outro, subscribe card or "follow for more". YES/NO
8. **Every joke-carrying line is captioned:** from the ASS file, 100% of the streamer/NPC/narrator lines that the premise
   depends on are burned in English. Word-by-word chunks ≤3 words. Cap height ≥75 px at 1080x1920. YES/NO
9. **Text in the safe zone, clean:**
   - all text inside x 6–88%, y 10–78%
   - no overlapping or clipped words (secrets1b had "HEY.HANDSOME", "ECAUSE")
   - the source's burnt-in subtitles hidden
   - text never over the payoff object

   YES/NO
10. **Frame used:** the main subject fills ≥60% of the frame width at its widest moment, and no blurred/filler band is >10% of the
    height. 3:4 or 4:5 content is OK if the subject is large. In the stacked layout the face panel is ≥40% of the height. YES/NO
11. **Picture floor:** no payoff frame has a Laplacian variance <150 measured at 608x1080 (downscale first so it compares with the
    references), no frame clips through geometry, and the colour isn't left at the dull raw grade (colourfulness ≥20 on the payoff shot). YES/NO
12. **Audio:** integrated −14 ±1.5 LUFS, true peak ≤ −1.0 dBTP, no silence >0.8 s unless flagged as suspense, and slurs bleeped. YES/NO
13. **Title:**
    - concrete noun or number plus "GTA 6"
    - the streamer's name first if there is a streamer
    - ≤60 characters before the emoji, 1–2 emoji, no "?"
    - no red-flag words (INSANE, TOO REAL, LOSES IT, COOKED, goes crazy)
    - every claim visible or audible in the clip

    YES/NO
14. **Policy and campaign:**
    - no nudity, slurs, gambling or fake/modded footage; real footage only
    - Kai pool clips: Kai's face on screen ≥90% of the seconds, "Kai Cenat" in the label or title, `#KaiCenat` and `#ad`
      (plus YouTube's paid-promotion box), no logos (crop watermarks), Kai not shown negatively

    YES/NO
15. **Not a repost:** no other Short of this exact moment has >10K views in the last 48 h, unless ours adds a first-hand
    reaction, a number or a comparison the others lack (306K vs 816 alligator rule). YES/NO

After the gate, the critic writes three lines: the weakest second (timestamp), the change that would fix it, and the 1-hour /
24-hour / 72-hour numbers to check. Formats are judged on several Shorts and fixed windows, never on one Short (Franklin's 21 Nov rule).

---

## 6. The next 6 Shorts (this week, footage we hold or can pull with the laptop helper)

Order = priority. The upload cap is ~10/24 h. Kai pool items are spaced ≥3 h apart.

| # | Format | Footage | Hook text (on screen, ≤7 words) | Title | Gate notes |
|---|---|---|---|---|---|
| 1 | F4 list (Kai pool) | kaicenat-09 (settings: UI text size 34–37 s, max brightness 65–67 s, black levels 71–76 s, paper white 85–90 s, "my run needs to be X" 126–130 s, "motion blur off" 139–142 s) + kaicenat-06/09 VOD times for the counter | "Kai's GTA 6 settings, ranked ⚙️" with "#1 took 4 minutes" | **5 GTA 6 Settings Kai Cenat Changed Before Playing ⚙️ #KaiCenat #ad** | This is a utility list (T8F used settings receipts), not a repost of C01. Kai cam top 45%, menu 40% with the setting name and value ≥40 px; countdown 5→1; #1 = paper white "NO NO NO NO". Verify every value on screen before captioning it. |
| 2 | F3 story | lirik-04 (legs 9.0–12.0 s, "What happened?… Did he do something to me?… He drained my Buckme account" 20–35 s, phone 36–38 s, balance 45–47 s, "Even Bigfoot's got a phone" 51–53 s) | "bigfoot walked right past me 😭" | **Lirik Blacked Out Next To Bigfoot In GTA 6… Then Checked His Bank App 😭** | Make it only if the bank balance is legible on screen (the payoff). The legs are bright and big at frame 0 (gamma 1.25). Question planted by 2 s: "what did he do to me?". End on the balance plus Lirik's line, then cut. |
| 3 | F3 story, mistake the viewer sees first | n3on-03 48–73 s (bank stick-up, "Oh no… oh my god", "What's L? What is L?" 64.6–65.6 s, "lose the cops") | "the game said press L. mid-robbery 😭" | **N3on Robbed A Bank In GTA 6 Before Learning The Controls 😭** | Make it only if the game's button prompt is visible: enlarge it 2x on the bottom panel with an arrow so the viewer knows before N3on does. Otherwise it's a reaction-only clip (dead format): skip it. |
| 4 | F2 NPC payoff | **Hunt first** in Kai Part 1/2, xQc, Lirik and Cohh VODs: transcript or laughter spike within 5 s of an NPC line; keep only windows with a physical payoff (crash, slam, fall, "wasted", the NPC outruns or outfights) in ≤20 s | written per moment as the viewer's reaction, e.g. "this NPC did NOT come to lose 😭" | per moment, ≤6 words, ironic: e.g. "GTA 6 NPC Chose Violence 💀" | Ship only with a visible physical payoff at 65–85%. If no window qualifies by tonight, replace it with Agent00 C11 ("no space in the jail") re-cut as F2 under its NPC-line payoff. That moment already went out as "Agent00… Jail Is FULL" (84 views, 37.8% stayed), so ask Franklin before re-cutting it (no re-uploads for low views). |
| 5 | F1 money tip | **Hunt** with Whisper transcripts and HUD frames across all raw VODs for "cash / stash / money / wallet / safe / code" plus a "+$" toast; candidates: Lirik dog island wallet (if present), Lirik bank app, any streamer stash route | "FREE $[exact] 💰" | **Free $[exact] In GTA 6: [odd instruction] [emoji]💰** (e.g. "This GTA 6 Dog Digs Up $[exact] For You 🐕💰" if the wallet footage exists) | Exact HUD amount only. Location named or map shown. Optional PT text test on this one (§3 F1). If no verified method exists, don't fake one: move F5 up. |
| 6 | F5 aura/meme edit | Rockstar GTA 6 trailer 1 (Lucia's robbery entrance, gun to the camera, the store shots) | "POV: Vice City meets Florida Man" in 3 colours, then ☠️ on each beat | **POV: Vice City Meets Florida Man ☠️ \| GTA 6 Trailer** | 22 s, drop at 5.0 s, cuts on a 0.5 s grid. Pick the library track before rendering and align its drop at upload; if it can't be aligned, don't post. Watch 48 h for a Content ID claim before making a second. |

**Not on this list, on purpose:**
- re-uploads of posted Shorts (Franklin's rule)
- reaction-only clips
- dog-L1 as built (a faceless repeat of a 4.8M discovery with no wallet receipt; post it only as an F1 or F4 item with the receipt)
- any list item without a receipt shot

**Measure after posting:** stayed-to-watch at 1 h and 24 h vs our 41–57% baseline. The goal is ≥65% on every Short that passes the gate. If the gate holds but stayed-to-watch doesn't move after 6 Shorts, the gate is wrong: revisit L1–L4 with the new data, not the editors.
