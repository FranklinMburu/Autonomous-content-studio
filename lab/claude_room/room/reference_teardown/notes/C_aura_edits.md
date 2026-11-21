# Group C: AURA / MUSIC EDITS / CINEMATIC (frame-by-frame notes)

Analyst notes for IntNext (GTA 6 Shorts). Source data: `/home/claude/reftear/out/<id>/` (report.json, hook.jpg,
sheet_*.jpg) and `/home/claude/reftear/meta.tsv`. Today = 2026-11-21. No transcript exists: speech is inferred from
burned captions, music from audio numbers (LUFS, LRA, RMS per 0.5 s). "Unclear" = cannot be told from the data.

## 0. Numbers at a glance

| id | what | views | like % | comments | age d | views/day | len s | res | cuts/10 s | median shot s | sharp | sat | colourful | text share | LUFS / LRA | loop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DGjgDx8w6ws | GTA 6 TRAILER "Gen Z meets Gen Alpha" POV edit | 8,387,211 | 3.54 | 3,433 | 31 | 271k | 22.0 | 720x960 | 6.36 | 0.60 | 173 | 108 | 33 | 0.41 | -7.7 / 2.8 | 0.904 |
| TOpWSZ-9kQw | Hitman movie edit, Raya (Slowed) | 3,192,013 | 2.10 | 169 | 16 | 200k | 59.9 | 720x800 | 5.35 | 1.22 | 811 | 138 | 38 | 0.74 | -17.2 / 4.5 | 0.754 |
| W330Tiq7j7k | Superman vs Gym Trainer, Montagem Royal (Slowed) | 10,187,648 | 2.41 | 808 | 38 | 268k | 54.8 | 1080x1080 | 2.01 | 1.61 | 665 | 93 | 60 | 0.93 | -15.7 / 9.5 | 0.688 |
| JhffeNS2EnA | Sarah Connor "aura farming", Montagem Ahora | 17,324,763 | 2.61 | 1,945 | 11 | **1.58M** | 59.0 | 720x800 | 6.27 | 1.24 | 2250 | 57 | 24 | 0.83 | -8.3 / 5.8 | 0.793 |
| GVYcVIQlb3g | John Wick "7 million dollars for one gun" | 24,916,395 | 3.13 | 1,473 | 93 | 268k | 58.0 | 720x746 | 3.10 | 1.53 | 433 | 112 | 26 | 0.52 | -17.9 / 8.5 | 0.784 |
| HMzSHD4N4b4 | Tweet + Walter White meme, 6 s | 2,777,467 | n/a (likes blank) | 148 | 8 | 347k | 5.9 | 608x1080 | 0 | 5.9 | 3074 | 60 | 45 | 1.00 | -9.2 / 2.7 | 0.907 |
| fK0vh96EjTk | "Just vibing", one-take open-world game | 8,463,174 | 1.44 | 1,045 | 44 | 192k | 34.9 | 720x922 | 0 | 34.9 | 970 | 119 | 40 | ~0 (OCR noise) | -11.8 / 5.0 | 0.744 |
| cj-NbCfWoNw | Bugatti "Pearl collection", real footage | 2,561,787 | 2.00 | 613 | 24 | 107k | 22.5 | 608x1080 | 1.34 (but a car change every ~2 s) | 4.58 | 1717 | 61 | 35 | 0.87 | -6.2 / 1.9 | 0.696 |
| j_SxWIIpDbs | "Jason's Home Gym in GTA 6 Is Insane" | 26,006 | 2.40 | 2 | 1 | 26k | 27.0 | 608x1080 | 6.67 | 1.30 | 145 | 70 | 36 | 0.81 | -17.0 / 0.9 | 0.690 |

Like % = likes / views. Text share = share of sampled seconds with OCR text (the OCR picks up noise; real burned
text is described per video).

Important honesty notes:
- 4 of the 9 are "music + movie scene" aura edits (TOpWSZ, W330, JhffeNS, GVYcV). DGjgD is a **GTA 6 trailer** POV meme
  edit with music (8.4M views, 3.54% likes, the best like and comment rate here: proof the format works on GTA 6 footage); fK0 is a single-take gameplay "vibe" clip; cj- is real-life luxury footage with a 2-word caption;
  HMz is a reaction meme; j_Sx is a GTA 6 voice-over info Short (Franklin called its feeling "aura", but structurally it
  is an explainer).
- Biggest per-day winner by far: JhffeNS2EnA (Sarah Connor) at ~1.58M views/day, 11 days old.

---

## 1. DGjgDx8w6ws: "GEN Z MEETS GEN ALPHA ☠️ | #gta #gta5 #gta6 #shorts #viral #trending #foryou #edit"
Channel PAGLUU. Franklin: "aura: music, scene, proven by likes/views".

**Numbers.** 8.39M views, 296.5k likes (3.54%, the best like rate in the group), 3,433 comments (best comment count),
31 days, 22.0 s, 720x960 (3:4 frame, not full 9:16), 60 fps, low bitrate 1,196 kbps, 14 cuts (6.36/10 s), median
shot 0.60 s, longest 4.39 s. Sharpness 173 (soft), saturation 108, colourfulness 33, motion 6.4. Text in 41% of seconds.
Loudness -7.7 LUFS (very loud), LRA 2.8, true peak +3.1 dB (clipped/limited hard), sound 98%. Loop similarity 0.904
(the highest of the long videos: end frame looks like the start).

**Beat list (from cuts, RMS, OCR).**
- 0.0-4.4 s: one shot (cut at 0.03 is the first frame). Caption "POV: GEN Z MEETS GEN ALPHA" at bottom/mid, game
  dialogue captions in quotes: "hey handsome!" (1.5 s), "GENERATOR! GENERATOR!" (3.5 s). Audio quieter (RMS -11 to -22 dB).
  Sharpness high in this section (356-548) then collapses after 5 s.
- ~5.0 s: **drop**. RMS jumps to a flat -7.5 dB wall and stays there to the end (except a dip at 12.5-14 s).
- 4.42 / 5.02 / 5.53, 7.33 / 7.83, 9.65 / 10.15, 14.2 / 14.7, 16.53 / 17.03, 18.87 / 19.35: cuts come **in pairs 0.5 s
  apart, every ~2.3 s**. This is a repeating insert pattern: a 0.5 s flash/insert shot dropped on a beat, then back to
  the main shot. Motion peaks 6-12 s (29, 29, 21, 22) = the most active section, right after the drop.
- 8.0 s: "GENERATOR! GENERATOR!" again (a repeated line = running joke).
- 12-14 s: saturation peaks (153-154) while sharpness stays low: a colour-pumped section.
- 20 s: caption "...secret stash!" at bottom.
- 22 s: end; loops back (0.904).

**1b. Visual check (sheets 0-20 s seen).** **This is GTA 6 trailer footage**, the most directly copyable video here.
- 0.0 s: black frame. 0.25-4.25 s: Lucia in a red bandana bursts through a convenience-store door, sun flare behind,
  and points a pistol at the camera (trailer robbery shot). Warm, back-lit, hazy grade.
- Caption 0.25-5.0 s, lower-middle, bold sans caps with black outline, three colours: "POV:" white, "GEN Z" green,
  "MEETS" white, next line "GEN ALPHA!!" red.
- 4.5-6.25 s: trailer man in a beige T-shirt drinking from a can. 5.25 s: the caption is replaced by a **☠️ emoji**
  in the lower middle.
- 6.5-8.0 s: slushie machine → a man in a blazer behind the counter (skull at 7.5 s); 8.5-10 s store clerk with a gun
  (skull at 9.75 s); 10.25-14.5 s man in a white tank top in a parking lot, side profile, speaking (skull at 14.25 s);
  15.5-17 s man in a car (skull at 16.75 s); 17.25-19.25 s smiling man on a phone with a pearl necklace and floral shirt
  (skull at 19.0 s); 19.5 s dark silhouette holding a phone.
- So the 0.5 s cut pairs = each trailer character gets ~2.3 s, and the **skull emoji lands on the beat** at the end of
  each shot, followed by a fast cut. The "GENERATOR! GENERATOR!" and "secret stash!" OCR lines are quoted subtitles.
- Grade: warm sunset orange with teal shadows; contrast crushed; soft (sharpness falls to 36-154 after 5 s).

**Frame 0 / first 2 s.** Black frame 0, then by 0.25 s Lucia + gun + muzzle-to-camera + the coloured POV caption. Why a
scroller stops: a weapon pointed at the viewer, the GTA 6 star, and a generational meme they want to decode.

**Craft.** Cut-on-beat inserts in 0.5 s pairs; very loud mastered audio; soft image (sharpness 36-154 after 5 s, i.e.
blurred / motion-heavy / re-encoded); colour pushed in the middle. Letterbox: frame is 3:4, so YouTube shows it with
bars or crop (unclear which in-app).

**Text.** Short meme header "POV: ..." low-mid in frame; quoted character lines in caps with quote marks at bottom.

**Audio.** Continuous music (sound 98%, LRA 2.8). The quiet first 5 s then a wall of sound = build-up then drop.
Game voice lines are likely mixed in (captions are in quotes). Genre unclear from data.

**Arc.** Comedy-cringe "Gen Alpha" character → loud drop → funny repeated line. Feeling: ironic hype / meme aura, not
calm power.

**Packaging.** All-caps meme title + skull emoji + 8 hashtags (#gta #gta5 #gta6 ...). The footage is the GTA 6 trailer,
so #gta5 is there only for reach.

**Why it wins.** (1) A meme frame (Gen Z vs Gen Alpha) that comments love: 3,433 comments, 3.54% likes. (2) 22 s, very
loud, drop at 5 s, a 0.5 s insert every ~2.3 s keeps rewatching cheap. (3) 0.904 loop similarity: viewers replay
without noticing the restart.

**Scores.** Hook 8, story 6, editing 7, visual quality 4, text 7, audio 8, ending/loop 9.

**GTA 6 version.** This one already is one: 22 s of trailer shots, one character per ~2.3 s, a meme POV caption in 3
colours for the first 5 s, a ☠️ on each beat, loud music with the drop at 5 s, loop back to Lucia. Make our own versions
with other POV jokes ("POV: Vice City meets Florida Man") and our own clip order.

---

## 2. TOpWSZ-9kQw: "Why You Should Never Cross Agent 47 🥶🔥 | Hitman Movie | Song - Raya (Slowed) #trending #shorts"
Channel AfridiAE. Franklin: "aura movie edit + music".

**Numbers.** 3.19M views, 67.1k likes (2.10%), 169 comments (low: people watch, few talk), 16 days, 59.9 s,
720x800 (almost square), 60 fps, 3,257 kbps. 32 cuts (5.35/10 s), median 1.22 s, longest 6.22 s. Sharpness 811,
saturation **138 (highest of the group)**, colourfulness 38. Text in 74% of seconds. -17.2 LUFS, LRA 4.5, sound 100%.
Loop 0.754.

**Beat list.**
- 0-1.5 s: two quick cuts (0.98, 1.48). Hook text appears ~3 s: "BUT THIS IS FOR ANOTHER GENTLEMAN" (mid, caps).
- 3-14 s: slow dialogue section, long shots (5.87→8.0→14.22). Captions are the film dialogue, mid-screen, caps:
  "YOU KNOW WHAT TABLE THAT IS?", "SAW THE LAYOUT WHEN WE CAME IN", "REMEMBER EVERYTHING".
- 5 s and 8 s: motion spikes (49, 51) = whip/snap moments at cuts.
- 17-24 s: "WHAT'S SHE WEARING?" "CORRECT" "WHAT COLOR UNDERWEAR AM I WEARING?" "YOU'RE NOT WEARING ANY UNDERWEAR"
  = the "he notices everything" proof beat (competence = aura).
- 26-30 s: bracketed narrator captions start: "(47 TARGETS ... STOMACH PAIN)", "COME WITH US SIR".
- 32-37 s: "BUT DONE!", "THEN HURRY", "SORRY,".
- 40-49 s: "(47 IS SEARCHED BY SECURITY GUARDS)", "(47 TAKES OUT SYRINGE FROM THE TOILET TANK)",
  "(HE IS PREPARING TO SILENTLY ASSASSINATE)". Cuts accelerate: 41.4, 43.4, 44.0, 44.45, 45.23, 46.03, 47.23, 48.03, 49.0.
- 41-58 s: **climax**. Saturation drops from ~185 to 50-100 (grade goes darker/cooler for the kill), motion explodes
  (51, 42, 48, 66, 81 at 44-51 s; 96, 104 at 57-58 s). "MR PRICE" at 53.5 s. 5 cuts in the last 6 s (53.37-58.75).
- 59.9 s: ends on action; loop 0.754.

**2b. Visual check (sheet 0-10 s seen).** Frame 0 = back of Agent 47's bald head with the barcode tattoo, in a warm
amber restaurant. 0.5 s: woman in a red dress by candlelight; 1.0 s back to 47; 2.25 s a waiter in a white jacket with a
tray. Captions are small glowing caps centred at mid-height, typed on letter by letter, **each line a different colour**:
"I'M SORRY, SIR" (white), "BUT THIS IS FOR ANOTHER GENTLEMAN" (purple glow), "TABLE 26?" (yellow), "THAT'S RIGHT"
(white), "MY MISTAKE" (green), "YOU KNOW WHAT TABLE THAT IS?" (pink). Watermark "AFRIDIAE" at lower centre with a
typing cursor. Grade: warm gold/brown, heavy sharpening and grain on skin. 9.75 s: 47 close-up face looking up into
camera (menace beat).

**Frame 0 / first 2 s.** Barcode tattoo on a bald head is instantly "Hitman"; two cuts by 1.5 s; red dress + candle =
warm, rich colour. Stop reason = iconic character from behind + glamour shot.

**Craft.** Story-cut of one film scene, kept in order, with dialogue subtitles burned in and bracketed "narrator"
captions explaining silent actions. Slow first half (dialogue), fast second half (action) = the edit tracks the song's
build. Heavy saturation boost in the first 40 s (sat 150-198), then a darker grade for the violence.

**Text.** Centre-screen caps, white (colour detail in 2b), changes word-group by word-group, dialogue + "(47 DOES X)"
stage directions. The brackets are a smart device: they turn a silent scene into a readable story.

**Audio.** "Raya (Slowed)" per title: slowed, moody track; LRA 4.5 suggests music + film dialogue under it. Cut density
follows rising energy; no single hard "drop" in RMS (flat -15 to -20 dB) except a dip 35-40 s before the climax.

**Arc.** Calm confidence → proof of perception → quiet menace → silent kill. Feeling: "never cross him" = menace + cold
competence.

**Packaging.** "Why You Should Never Cross [character] 🥶🔥 | [film] | Song - [song] (Slowed)". The "Song - X" credit
is a convention of this niche (viewers search songs).

**Why it wins.** (1) A complete mini-story in 60 s with captions, watchable muted. (2) Title promises a consequence
("never cross") that the last 15 s pays off. (3) Pacing curve: slow set-up, 2x faster cuts in the last 20 s with motion
spikes = retention to the end.

**Scores.** Hook 6, story 9, editing 8, visual quality 7, text 8, audio 7, ending/loop 6.

**GTA 6 version.** "Why You Should Never Cross Jason & Lucia" from trailer shots: set-up (calm), proof (a detail they
notice), action (robbery cut fast). Bracketed captions: "(LUCIA CHECKS THE EXITS)". Slowed song, 45-60 s.

---

## 3. W330Tiq7j7k: "\"Superman Vs Gym Trainer\" - Superman | MONTAGEM ROYAL - NUEKI (Slowed) #edit"
Channel AfterAditZZ. Franklin: "aura feeling".

**Numbers.** 10.19M views, 245.7k likes (2.41%), 808 comments, 38 days, 54.8 s, **1080x1080 square**, 60 fps,
5,038 kbps (highest bitrate). Only 11 cuts (2.01/10 s), median 1.61 s, **longest shot 28.4 s** (4.3 → 32.7 s).
Sharpness 665, saturation 93, **colourfulness 60 (highest)**. Text 93% of seconds. -15.7 LUFS, LRA 9.5 (widest:
dialogue scene + music). Loop 0.688.

**Beat list.**
- 0-1.3 s: first shot; cut 1.3 s; 1.5 s top caption appears: **"Bro Really Tried To Hold Back So Hard"**, which stays at
  the top from 1.5 s to ~36 s (persistent hook caption).
- 4.3-32.7 s: one uncut 28 s scene (gym trainer vs Superman). Motion moderate (6-28). Mid-frame text bits in OCR
  ("YOUR FRIEND", "HELP", "NOW") are dialogue subtitles (mostly unreadable in OCR).
- 32.7, 34.6, 37.6 s: cuts; 40-48 s more dialogue ("No, Clark" at 47-48.5 s).
- 48.8 s: cut; then **cut burst every 0.5 s: 51.82, 52.32, 52.82, 53.32, 54.32** = the beat-synced finale.
  RMS jumps to -9.6/-10 dB from ~51.5 s: **the drop is at ~51.5 s**, and motion peaks (31, 40, 46, 33).
- 54.8 s: ends right after the burst.

**3b. Visual check (sheet 0-10 s seen).** Bright 1980s-style gym, warm wood walls. Clark Kent (glasses, grey/teal
Adidas tracksuit, towel round the neck) stands on a machine; 1.5-4.25 s close-up, a trainer's voice line caption
"JUST PUSH DOWN" (orange-tinted caps, mid-height); 4.5-7 s wide again; 7.25-9.75 s a muscular man in a red top: caption
"Need some" (white italic) + "HELP?" (red caps). The top caption that the OCR reads ("Bro Really Tried To Hold Back So
Hard") is not legible at thumbnail size: unclear how big it is. Grade natural-warm, very clean image (bitrate 5 Mbps).

**Frame 0 / first 2 s.** Frame 0 is a wide, busy gym shot with a woman walking past; the stop reason is the concept
(Clark Kent, the man of steel, nerd-acting in a gym) plus the hook caption. The viewer waits for the moment he stops
holding back.

**Craft.** Patience edit: lets one funny scene play long, music underneath, and saves all fast cutting for the last
3 s on the drop. Square format keeps the full movie frame; colour stays natural-but-rich.

**Text.** One persistent top caption in title case (opinion/comment voice: "Bro..."), plus small dialogue subtitles.

**Audio.** Montagem (Brazilian phonk/funk) slowed. LRA 9.5 because film dialogue sits on a quieter bed and the song
hits hard only at the end.

**Arc.** Restraint → comedy → release. Feeling: "hidden overwhelming power" (the strongest guy pretending to be normal).

**Packaging.** Quoted scene name + "- Character | SONG - ARTIST (Slowed) #edit".

**Why it wins.** (1) A concept everyone gets in 1 s (Superman in a normal gym). (2) The caption creates suspense for
55 s. (3) The payoff is a beat drop with 0.5 s cuts.

**Scores.** Hook 8, story 8, editing 7, visual quality 8, text 8, audio 7, ending/loop 6.

**GTA 6 version.** "Jason Really Tried To Stay Calm" over a long, calm trailer-like moment (gas station, gym, police
stop), then 0.5 s cuts of action on the drop in the last 3-4 s.

---

## 4. JhffeNS2EnA: "\"Fought Terminator at this age💀\" | Sarah Connor | MONTAGEM AHORA - NUEKI"
Channel Maqurak. Franklin: "amazing aura". **Best performer per day (1.58M/day).**

**Numbers.** 17.32M views, 451.9k likes (2.61%), 1,945 comments, 11 days, 59.0 s, 720x800, 60 fps, 3,636 kbps.
37 cuts (6.27/10 s), median 1.24 s, longest 5.0 s. **Sharpness 2,250** (heavy sharpening / upscaling; the sheets show
oversharpened skin texture and edge halos), **saturation 57 (low, desaturated)**, colourfulness 24. Text 83%.
-8.3 LUFS (loud), LRA 5.8. Loop 0.793.

**Beat list (sheets 20-59 s seen in detail; 0-20 s from data + 4b).**
- 0-0.9 s: first shot, cut at 0.92 and 1.75; motion spike at 1 s (51).
- 0.5-24 s: persistent top caption **"Aura farming at this age is crazy"** (white, top).
- 0-15 s: build. RMS around -12 to -16 dB. Cuts at 6.77, 9.1, 10.77, 14.07.
- ~15 s: **drop**. RMS jumps to -9.7/-7 dB. Dialogue subtitle "WHEN [THEY] START TO KILL ME" at 15-16 s (mid).
- 20-22 s: truck hits the Terminator (Rev-9) at 20 s; wheel close-up 21-21.75 s; metal endoskeleton crawling 22-23.25 s.
- 23.5-25.5 s: reaction close-up of the young man (calm, quiet beat).
- 25.75-27 s: **hero entrance**: low shot of a boot stepping out of a car (feet first, no face).
- 27.25-29 s: Sarah Connor reveal, sunglasses, holding a drum-fed gun. Watermark "MAQURAK" appears mid-lower,
  white with a glow and a **typing cursor** (types on/off).
- 29.25-32.25 s: the man runs; metal blade arm; 32.5-33.5 s Sarah fires (loudest section RMS -6 to -7 dB at 33-35 s).
- 33.75-37.75 s: chaotic smeared frames (motion-blur / frame-blend look) of the fight.
- 37.75-39.5 s: Sarah walks forward, picks up a rocket launcher. RMS dips (-15 dB) = calm before the hit.
- 40-43 s: Terminator separates (two bodies) and stands up.
- 43.25-43.5 s: Sarah aims the launcher (face to camera).
- **44.25-44.5 s: explosion fireball fills the frame** (flash). Cut cluster 43.07-45.8 s (6 cuts in 2.7 s).
- 45-45.75 s: smeared crash onto a car; 46-47 s Sarah lowers the launcher, slow head turn.
- 47.25-50 s: walks, reloads, group behind her; 50-51 s an over-sharpened textured frame (graphic/glitch look).
- 52.5-54.5 s: close-up, she says a line; caption **"I'LL BE BACK!"** in blue glowing caps, mid-frame, typed on.
- ~56 s: white flash frame; RMS jumps to -6/-7 dB again (final hit 56-58.5 s). Cuts 55.95, 56.65, 57.3, 57.93, 58.57
  (one every ~0.65 s).
- 57.5-58.75 s: close-ups on her face with sunglasses; last frame = tight face close-up.

**4b. Visual check (sheet 0-10 s seen; 10-20 s sheet was viewed earlier in the session, details not kept).**
0-0.75 s: the villain (human form) steps over a highway guardrail toward camera; 1.0-1.5 s a young woman runs, mouth
open; 1.75-2.75 s low shot of boots walking; 3-4.75 s the black metal endoskeleton walks toward camera, red eyes;
5.25-5.75 s whip-pan with palm-leaf motion blur; 6-6.75 s skull close-up; 7-7.5 s human form again; 7.75-9 s two women
run with a metal pole; 9.25-9.75 s close-up, struggling. Watermark "MAQURAK" types on at 1.25 s. The top caption the OCR
reads is not legible at thumbnail size.

**Frame 0 / first 2 s.** Frame 0 is a man stepping over a rail toward camera in harsh sun; a cut at 0.92 s to a
screaming runner and at 1.75 s to boots: three shots in 2 s = immediate danger. Top caption "Aura farming at this age is
crazy" (OCR from 0.5 s) gives the angle. Age contrast (older woman vs Terminator) is the idea.

**Craft.** Cuts follow the music: calm beats get 1.5-3 s shots, hits get 0.5-0.7 s shots. Hero entrance built with
feet-first shot → reveal. Explosion and white flash on the drops. Desaturated, contrasty, sharpened "cinema" grade
(teal-beige). Typing-cursor watermark and glowing typed caption for the famous line. Smear/blend frames on the
chaos to add energy.

**Text.** Top hook caption, sentence case, white, ~first 24 s; one iconic quote at 53-54 s in glowing blue caps; a
couple of dialogue subtitles mid-frame.

**Audio.** Montagem Ahora (Brazilian funk/phonk, not slowed in title). Loud master (-8.3 LUFS). Clear structure: build
0-15, drop 15, peak 33-35, dip 38-43, hit 44, final hit 56-58.

**Arc.** Disbelief → entrance → unstoppable calm competence → famous line → face. Feeling: power + calm confidence +
nostalgia (the "I'll be back" callback).

**Packaging.** Quoted meme sentence + 💀 + "| Character | SONG - ARTIST".

**Why it wins.** (1) A simple funny-impressive contrast in the caption ("at this age"). (2) Edit locked to a
structured funk track with 3 clear hits (explosion, line, final face). (3) Hero framing: entrance, sunglasses, walking
away from explosions, iconic quote = the textbook aura beats.

**Scores.** Hook 9, story 8, editing 9, visual quality 7 (sharpened/smeared, but reads as "cinematic" on phones),
text 9, audio 9, ending/loop 7.

**GTA 6 version.** "Lucia did this on day one 💀" or "Aura farming in Vice City is crazy": build on night city shots,
drop on Lucia stepping out of a car (feet first), sunglasses close-up, explosion or police lights on the hit, one
trailer line typed in glowing caps, end on her face.

---

## 5. GVYcVIQlb3g: "7 million dollars for one gun | John Wick"
Channel Jemeditzs. No label from Franklin (in his list). **Most views in the group (24.9M), 3.13% likes.**

**Numbers.** 24.92M views, 779.6k likes (3.13%), 1,473 comments, 93 days, 58.0 s, 720x746 (near-square), 60 fps,
1,734 kbps. 18 cuts (3.10/10 s), median 1.53 s, **longest 12.0 s**. Sharpness 433, saturation 112, colourfulness 26,
motion 4.3 (lowest: slow, still shots). Text 52%. -17.9 LUFS, LRA 8.5 (dialogue-led). Loop 0.784.

**Beat list (all sheets seen).**
- Top of frame: a thin **white strip with small black text "7 million dollars per bullet"** (visible in the hook strip,
  OCR 5.5-6.5 s). The frame below is the film.
- 0-0.7 s: silhouette of John Wick through subway bars (backlit, cyan-white light).
- 0.75-5.5 s: close-up of a homeless man with a tin cup; a bloody hand drops a gold coin into the cup (1.25-2.25 s); the
  man slowly looks up (4.5-5.5 s). Long held shot = curiosity.
- 5.75-8.25 s: back to bars; dialogue caption "TAKE ME TO HIM" in **red glowing caps** (6.25-7.0 s).
- 8.5-10.75 s: Wick close-up, bloodied face; caption **"TELL HIM IT'S JOHN WICK"** in cyan glow (9.25-10.25).
  RMS peak at 8.5 s (-10.7 dB) = first musical hit on the name.
- 11-20 s: Wick lies down under a blue blanket (12 s held), the man stands, walks away (slow, quiet).
- 20.5-22.5 s: a worker in the subway; 22.75-23.75 s the homeless man: "HEY MAN YOU GOT A QUARTER?" (cyan glow).
- 24-25.75 s: through bars, a dog; 26-27.25 s low-angle profile shot, silenced pistol in frame.
- 27.5-28.75 s: gun case opens: Kimber 1911.
- 29-39.5 s: the Bowery King hands over the gun: small white captions "KIMBER 1911" (29.5-31), ".45 ACP" (31.25-32),
  "SEVEN-ROUND CAPACITY" (white + orange "CAPACITY", 36-37.5).
- 39.75-44.75 s: Wick looking down; "SEVEN ROUNDS?" (42.5-43.25 s, small white), "SEVEN MILLION DOLLARS" (44.5-45).
- 45-47.25 s: the King: "GETS YOU SEVEN ROUNDS" (gold/orange caps).
- 47.5-53.75 s: hands take the gun, check it (bloodied hand, gun close-ups). Quiet.
- 54-55.5 s: Wick profile, light flare behind; "LET'S GO" in **red** small caps (54.75-55.5). RMS rises to -13 dB.
- **55.65-57.73 s: final burst, 6 cuts in 2 s**: back tattoo (55.75-56), car headlights + red light leak (56.25-56.5),
  Wick walking in three different films/outfits (56.75-57.25), fight (57.5-57.75). = the drop / "trailer" ending.
- Watermark "JEMEDITZS" small white at lower-centre with a typing cursor (15.25 s onward, 40 s).

**Frame 0 / first 2 s.** Dark silhouette behind bars + a bloody hand giving a gold coin: mystery and a strong
object (gold coin). Top strip text "7 million dollars per bullet" gives the curiosity number.

**Craft.** Mostly film-paced (long holds, motion 4.3), no beat cutting until the last 2 s. Teal/cyan subway grade with
crushed blacks, warm orange inside the King's room. Each quoted line gets its own colour (red, cyan, white, orange) and
glow; spec captions (KIMBER 1911, .45 ACP) read like a product card. Light leaks/flares on the final montage.

**Text.** Top white title strip; mid-frame glowing caps for key lines only (not every line); small spec labels.

**Audio.** LRA 8.5, -17.9 LUFS: film dialogue with a music bed; loud moments at the name reveal (8.5 s), the quarter
(23 s), the price (43.5-44.5 s) and the end (54.5-57.5 s).

**Arc.** Mystery → identity reveal ("It's John Wick") → value ("seven million dollars") → readiness ("Let's go") →
action montage. Feeling: calm menace + respect.

**Packaging.** Plain-language number hook "7 million dollars for one gun | John Wick". No emoji, no song credit.

**Why it wins.** (1) A number that sounds impossible ("7 million for one gun") answered inside the video. (2) Selective,
colour-coded captions make a dialogue scene easy muted. (3) Patient build to a 2-second, 6-cut ending that hits hard and
loops into the silhouette.

**Scores.** Hook 8, story 9, editing 8, visual quality 7, text 9, audio 7, ending/loop 8.

**GTA 6 version.** "$2 million for one car | GTA 6": a hold on one object (car key, cash, a gun case), captions as spec
cards ("TOP SPEED", "PRICE"), one coloured quoted line, slow first 50 s, 6-cut burst in the last 2 s.

---

## 6. HMzSHD4N4b4: "Melting Moments: The Way You Look at Me"
Channel Liberty Laugh. Franklin: "very unique". 6 s.

**Numbers.** 2.78M views, likes not given, 148 comments, 8 days (347k/day), **5.93 s**, 608x1080, 30 fps, 1,019 kbps.
0 cuts (one composition), sharpness 3,074, saturation 60, colourfulness 45. Text 100%. -9.2 LUFS, LRA 2.7. **Loop 0.907.**

**Beat list (sheet seen).**
- 0-5.9 s, top half: a static screenshot of a tweet thread: Andrew: "My wife wouldn't let me buy a PS5, so I bought one
  for my daughter!" (photo of man, baby and PS5 boxes); Sony: "What does she like? We'll send it to her for free!";
  Andrew: "Call of Duty."
- Bottom half: caption **"After that reply"** (white, bold italic serif with dark shadow) over Walter White
  (Breaking Bad) clip: 0-1.3 s face close-up, 1.6-2.4 s sun flare, 2.67-3.2 s he stands, 3.5-4.5 s bright flare,
  4.8-5.9 s he collapses face-down in the desert dirt.
- Watermark "GigaGiggle" lower-middle.
- RMS: -16 to -22 dB in the first second, then -11 to -13 dB: song comes in after ~1 s.

**Frame 0.** You can read the whole joke in 2 s (tweet = setup, "Call of Duty" = punch); Walter = reaction.

**Craft / text / audio.** Split-screen meme template; one reaction clip; a soft emotional song (title suggests a song,
"The Way You Look at Me"; unclear which version); 6 s so most people watch 2-3 times (loop 0.907).

**Arc.** Wholesome setup → absurd dad answer → dramatic "collapse" reaction. Feeling: irony.

**Why it wins.** (1) 6 s with a full joke = completion and replays. (2) Familiar reaction face. (3) Text carries
everything; works muted.

**Scores.** Hook 8, story 6, editing 4, visual quality 6, text 9, audio 6, ending/loop 10.

**GTA 6 version (not an aura edit).** Top: a real GTA 6 news headline / tweet screenshot (ours, not fake); bottom: a
Jason/Lucia reaction moment captioned "After that reply"; 5-7 s; end frame = start frame. Note: do not fake tweets.

---

## 7. fK0vh96EjTk: "Just vibing"
Channel dougfaze. 8.5M views. No label.

**Numbers.** 8.46M views, 121.9k likes (1.44%, lowest), 1,045 comments, 44 days, 34.9 s, 720x922, 60 fps, 4,039 kbps.
**0 cuts (one continuous take)**. Sharpness 970, **saturation 119**, colourfulness 40, motion 11.4. **No burned text**
(OCR hits are noise from building edges). -11.8 LUFS, LRA 5.0. Loop 0.744.

**Beat list (all sheets seen).** Third-person open-world game in a sunny San Francisco-like city (steep streets,
painted houses; the game is not named in the title; it does not look like GTA trailer footage: unclear which game).
Character: back view, headphones, plaid shirt, skateboard on the backpack.
- 0-4 s: walking down a sunny sidewalk, skyline ahead, police car drives up (2-4 s).
- 4.5-6 s: camera swings, police car with lights stops right next to him.
- 7-10 s: he keeps walking calmly; cops get out.
- 10.5-11.25 s: close pass of a police car with lights; 12-14 s officer approaches him.
- 14.5-16.5 s: **hands up** (motion peak 13-14 s).
- 16.75-17.25 s: he spins/dodges the officer and **runs** (RMS rises at ~17 s: music lifts).
- 17.5-21.75 s: runs into an alley, up steps into a shop ("S&V" door).
- 22-25.25 s: through the dark shop, out the front glass door into the street.
- 25.5-28.5 s: jumps into a silver sports car (door opens 27.75-28.5 s).
- 28.5-34.75 s: drives off, rear view, **green exhaust flames** (31-34.75 s). End.

**Frame 0.** Bright, warm, saturated city with a calm walking character and music: the "vibe". The police car arriving
at 2 s is the real hook (tension inside a calm clip).

**Craft.** No edit at all: the camera work (swing to the police car, follow cam) is the craft; warm golden grade,
high saturation. The "story" is emergent gameplay: calm → arrest → escape → getaway car.

**Text / packaging.** No text in video; title is two words, "Just vibing" (understatement as a joke against the chaos).

**Audio.** Music throughout (sound 100% implied, LRA 5), energy rises at the escape (~17 s) and again at 21-31 s.

**Arc.** Chill → tension → cheeky escape → flex exit (flames). Feeling: carefree cool.

**Why it wins.** (1) One unbroken take feels real and "unedited". (2) Mini-story in gameplay with a clear turn at 14-17
s. (3) Ironic title + no text = curiosity in comments.

**Scores.** Hook 6, story 8, editing 5, visual quality 8, text n/a (0), audio 6, ending/loop 6.

**GTA 6 version.** One continuous 30-35 s take: Jason walks Vice City at sunset with headphones-style calm music, police
stop, hands up, escape on foot through a shop, steal a car, drive off. Title "Just vibing" / "Normal day in Vice City".

---

## 8. cj-NbCfWoNw: "The PEARL COLLECTION ! 55 000 000 € BUGATTI COLLECTOR 😳 #bugatti #chiron #divo #mistral #centodieci"
Channel G-E SUPERCARS. No label.

**Numbers.** 2.56M views, 51.3k likes (2.00%), 613 comments, 24 days, 22.5 s, 608x1080, 30 fps. 3 detected cuts
(4.8, 6.63, 11.0) but the camera moves from car to car about **every 1.6-2.2 s**. Sharpness 1,717 (crisp phone video),
saturation 61 (natural), colourfulness 35. Text 87%. **-6.2 LUFS (loudest), LRA 1.9 (flattest)**: a loud, constant song.
Loop 0.696.

**Beat list (all sheets seen).**
- 0-4.5 s: caption **"THE OWNER."** (white condensed bold caps, black outline, upper third). A grey-haired man in a
  brown suede jacket and white trousers walks across a lawn through photographers (one in a BUGATTI jacket);
  3.2-3.5 s he spreads his arms wide (a "this is mine" gesture).
- 4.8 s: wide shot of a château; 5.07-6.4 s wide with the cars lined up in front. Caption switches to
  **"THE COLLECTION."** and stays to the end.
- 6.67-8.8 s EB110 (grey-blue); 9.07-10.9 Veyron (black/orange); 11.2-12.8 Chiron (dark blue); 13.07-14.67 Divo
  (yellow); 14.93-16.53 Chiron (black/orange); 16.8-18.67 light-blue car; 18.93-20.53 orange Chiron; 20.8-22.4 mint
  green Mistral (roadster). One car per ~2 s, framed in front of the house.

**Frame 0.** "THE OWNER." on a man being photographed: you want to see what he owns. Two-word set-up, two-word payoff.

**Craft.** Simple: real footage, steady framing, a reveal list of rarer and rarer cars, the caption never changes after
4.8 s. Colours of the cars do the work (yellow, orange, mint).

**Audio.** Loud, flat song (LRA 1.9), unclear genre.

**Arc.** Person → place → possessions. Feeling: awe / wealth aura.

**Packaging.** Caps name + big number "55 000 000 €" + 😳 + model hashtags.

**Why it wins.** (1) A 2-beat caption story ("THE OWNER." → "THE COLLECTION."). (2) A new colourful car every 2 s.
(3) Big money number in the title.

**Scores.** Hook 7, story 6, editing 5, visual quality 8, text 8, audio 6, ending/loop 5.

**GTA 6 version.** "THE OWNER." (Jason/Lucia stepping out at a mansion) → "THE COLLECTION." (one car per 2 s in front of
a Vice City mansion at night under lights), 20-25 s, loud flat song.

---

## 9. j_SxWIIpDbs: "Jason's Home Gym in GTA 6 Is Insane! #gta6 #gtavi #shorts"
Channel LocaRishi. Franklin: "crazy nice aura". **The only GTA 6 video; 1 day old.**

**Numbers.** 26,006 views, 625 likes (2.40%), 2 comments, 1 day, 27.0 s, 608x1080, 29.97 fps, 1,722 kbps.
18 cuts (6.67/10 s), median 1.30 s. **Sharpness 145 (soft, upscaled)**, saturation 70, colourfulness 36.
Text 81%. -17.0 LUFS, **LRA 0.9** (flat: a voice-over over a bed). Loop 0.69.

**Beat list (all sheets seen).** The 16:9 source sits in the middle of a 9:16 frame, with a **blurred copy filling the
top and bottom bands**. Captions are **one word at a time**, lime-green with a dark outline, centre-low, synced to a
voice-over (likely TTS; unclear):
- 0-0.5 s: warm, blown-out, blurry back shot of Jason shirtless ("Jason's").
- 0.7-1.2 s Jason walks onto a deck gym with a can ("home", "gym in"); 1.4-2.1 s kettlebells, towel ("GTA six").
- 2.3-3.5 s top-down bench press ("isn't just decoration."); 3.7-6.3 s squat ("You can actually workout using
  equipment like squat"); 6.5-7.7 s rack, bench press; 7.9-9.1 s kettlebell swing ("kettlebells and punching");
  9.3 s "bags."
- 9.58 s magazine cover "BODY COPY / BEAST MODE" ("But"); 9.8-10.7 s basketball shot ("here's interesting detail.").
- 11-12 s cycling ("Working out contributes to your"); 12.4-13.8 s running on sand ("character's physical fitness,").
- 14-16 s kitchen, coffee mug ("and the nutrition system is connected to it too."); 16.3-18.5 s cupboard UI
  "FUEL TANK PROTEIN BAR / THROB PROTEIN BAR" ("You can grab protein bars [from the] kitchen cupboard,").
- 18.7-20.1 s fridge UI "PATRIOT BEER / PROTEIN SHAKE / RAINÉ WATER" ("protein shakes [from the] fridge.").
- 20.3-21.5 s drinking ("Even better, consuming"); 21.7-23.1 s blurry transition / bench ("protein after a workout");
  23.4-25.5 s UI toast **"Fitness: Protein reduced your recovery time"** ("reduces recovery time by 50%,").
- 25.7-26.9 s Jason punches a car window, glass flies ("according to in-game tutorial."). End.

**Frame 0.** Blurry, over-exposed back shot: weak frame 0 (no face, no text until 0.23 s). The stop reason is the
"Jason's" word + muscular body + "GTA 6".

**Craft.** Fast b-roll matched to words; UI close-ups as proof; warm look. Soft image (sharpness 145), blur fill bands
make the picture small. No music drop; flat voice.

**Why Franklin feels "aura".** Jason's physique, sunny Florida deck, calm routine, ending punch = lifestyle power. But
the format is explainer, and it has 26k views on day 1, 2 comments.

**Scores.** Hook 5, story 6, editing 6, visual quality 4, text 7, audio 4, ending/loop 5.

**How to turn it into a real aura edit.** Same footage, no voice: slowed phonk/montagem from the Shorts library; top
caption "Jason's routine is crazy 💀"; full-bleed vertical crop (no blur bands); shots on the beat: deck walk (build),
bench/kettlebell on 0.5 s cuts at the drop, protein shake close-up, the "Fitness" toast as the one text proof, end on
the window punch in slow motion and a face close-up.

---

## GROUP SECTION: the GTA 6 "aura" recipe

### What the 5 real winners share (DGjgD, TOpWSZ, W330, JhffeNS, GVYcV: 3.2M-24.9M views)
- **Length**: 22-60 s. The three biggest movie edits are 55-60 s; meme edits 22 s.
- **Frame**: near-square or 3:4 crops of 16:9 footage are common (720x800, 720x746, 1080x1080, 720x960). They do not
  stretch to 9:16; they keep the cinema frame large and add text above it.
- **Cuts**: 2-6.4 per 10 s average, but the distribution matters more than the average: **slow (1.5-12 s shots) in the
  build, 0.5-0.7 s shots on the drop**. Every one ends or peaks with a burst: W330 5 cuts in 2.5 s, GVYcV 6 cuts in
  2 s, JhffeNS 6 cuts in 2.7 s on the explosion and 5 in the last 2.6 s, TOpWSZ 10 cuts in 8 s at 41-49 s, DGjgD 0.5 s
  insert pairs every 2.3 s.
- **Drop position**: 5 s in 22 s videos (DGjgD); ~15 s, ~33 s, ~44 s, ~56 s in Sarah Connor; ~51.5 s in W330;
  final 3 s in GVYcV. In RMS terms: a jump of 5-10 dB from the build level.
- **Loudness**: two families: loud music edits -7.7 to -8.3 LUFS (meme / funk); dialogue-led film edits -15.7 to -17.9
  LUFS with LRA 4.5-9.5.
- **Text**: a hook caption on screen by 1.5 s and kept for 20-36 s (W330, JhffeNS); quoted lines as glowing coloured caps
  only for the key 2-4 lines (GVYcV, JhffeNS); bracketed stage directions for silent action (TOpWSZ).
- **Colour**: either pumped saturation (TOpWSZ 138, GVYcV 112, DGjgD 108) or desaturated contrasty "cinema" (JhffeNS
  57) with heavy sharpening. Plain natural colour is the minority.
- **Arc**: calm restraint or mystery → proof (a detail, a number, a name) → release (action/explosion) → iconic face or
  line at the end. The aura feeling = calm confidence under pressure.
- **Packaging**: `"Meme sentence 💀" | Character | SONG - ARTIST (Slowed)` or a number promise ("7 million dollars for
  one gun"). Songs are Brazilian montagem/phonk or slowed tracks.

### The aura recipe as measurable rules (GTA 6 edition)
1. Length 45-58 s for the story edit; 18-25 s for the meme edit. Loop similarity target ≥ 0.85 (end on the frame or
   face you opened with).
2. Hook caption visible by **1.0-1.5 s**, sentence case, top of frame, 4-8 words, kept on screen ≥ 15 s
   (e.g. "Jason really tried to stay calm", "Aura farming in Vice City is crazy").
3. Build phase: shots 1.5-4 s, motion low, 1-2 key lines as captions. Drop: shots 0.5-0.7 s, ≥ 5 cuts in ≤ 3 s, at
   least twice (first drop at 25-30% of the length, last at the final 3-4 s).
4. One hero entrance: feet/hand/car door first (0.75-1.5 s), then the face reveal on a beat.
5. One "proof" beat: a number, item name or skill shown as a spec caption ("$2,000,000", "FUEL TANK", "5 STARS").
6. One iconic quoted line from the trailer, glowing coloured caps, typed on, at 85-95% of the length.
7. Grade: pick one: (a) night Vice City neon pumped to saturation 110-140, or (b) desaturated teal-orange 55-70 with
   strong contrast. Never leave the raw grade. Keep sharpness ≥ 400 (avoid soft upscales: j_Sx 145 and DGjgD 173 are
   the softest).
8. Frame: crop to 3:4 or 1:1 with text above, or full 9:16 crop; **no blurred fill bands**.
9. Music: one song from YouTube's Shorts audio library (montagem/phonk/slowed style), credited in the title
   "| Song - X". Loud edit master around -8 to -10 LUFS; if dialogue is used, -15 to -17 LUFS with dialogue on top.
10. Flash/explosion/white frame (1-2 frames) on the biggest hit; light leak or flare on the final montage.
11. Title: `"<meme sentence> 💀" | Jason / Lucia | Song - <song>` or a number promise.

### Top 7 rules (plus rule 0)
0. **Proof on our footage**: DGjgDx8w6ws turned the GTA 6 trailer into 8.4M views with a 3-colour meme caption, one
   character per ~2.3 s and a ☠️ on each beat. Start there.
1. **Caption the idea in 1.5 s and leave it up**: the two best-per-day edits (Sarah Connor 1.58M/day, Superman 268k/day)
   both pin a 5-7 word opinion caption at the top for 24-36 s.
2. **Slow build, fast drop**: hold shots 1.5-12 s, then ≥ 5 cuts in ≤ 3 s on the music hit; end with that burst.
3. **Build the hero beat**: entrance (feet/door first) → sunglasses/face → walk away from chaos → iconic line.
4. **Show proof, not hype**: a name, a number or a skill ("It's John Wick", "seven million dollars", "remember everything").
5. **Grade hard and keep it sharp**: saturation 110-140 or desaturated 55-70 with contrast; no soft or blurred-band frames.
6. **Use a montagem/phonk/slowed song from the Shorts library, credit it in the title, master loud (-8 to -10 LUFS)**.
7. **Loop it**: end on a face or frame that matches the opening (DGjgD 0.904, HMz 0.907).

### Copyright caution
- Use only songs available in YouTube's Shorts audio library (added in the Shorts editor) to stay $0 and avoid claims.
- GTA 6 trailer footage belongs to Rockstar; trailer clips may get Content ID claims; own gameplay (when available)
  is safer. Movie edits in this group are reuploads of studio footage: we should not copy that part.
- Never fake tweets or screenshots (HMz format) with real names.
- Session note: the 10-20 s sheets of JhffeNS, the later sheets of TOpWSZ/W330/DGjgD (20+ s) and their hook strips were
  viewed earlier but dropped from memory before writing; their beat lists past the re-checked range rely on cut times,
  RMS and OCR rather than a second look.
