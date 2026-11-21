# Handoff: GTA 6 Clip Room (IntNext Shorts), 19–21 Nov 2026

Written 21 Nov 2026 13:40 Nairobi. It is built from the full chat "GTA clipping campaigns and streamers" (87 messages, 19 Nov 13:21 → 21 Nov 12:55 Nairobi) on the account precisionexecutionlabs@gmail.com, and from the repo branch `claude-room`.

**Read this first in any new chat, then `lab/claude_room/MASTER_PLAN.md` → `RUNBOOK.md` → `room/UPLOAD_QUEUE.md` → `room/POSTED.md` on branch `claude-room`.**

## 1. Where everything lives

| What | Where |
|---|---|
| Single source of truth | repo `FranklinMburu/Autonomous-content-studio`, branch **`claude-room`**, folder `lab/claude_room/` |
| Plan and how to run | `MASTER_PLAN.md`, `RUNBOOK.md`, `SPEC.md` (layout and safety rules) |
| Tools | `edit.py` (stacked facecam/gameplay), `supercut.py`, `fullscreen.py` (9:16 crop follow), `listshort.py` (COLETHEMAN list format with Kokoro narrator and word-by-word captions), `teardown.py` (measures a Short against the winners) |
| Research | `room/`: WINNING_FORMATS, GTA_CHANNELS_20NOV (72 channels), CHANNELS_LIKE_COLE, COMPONENTS (best tool per part), FORMAT_SPEC (measured from 18 winners), HOOK_BLUEPRINT, HOOK_LAB (ChatGPT × critic rounds), SERIES_PLAYBOOK, PLAYBOOK (dated lessons), TREND_DATA_*, CAMPAIGNS (44 campaigns), RULES_KAI_POOL, CRITIQUE, REVIEW, SLATE |
| Finished Shorts | branch **`shorts/sc`** (`<id>.mp4` + `<id>.json` with title, description, hashtags) |
| What is posted | `room/POSTED.md` (links, times, views) |
| What to upload next | `room/UPLOAD_QUEUE.md` |
| Raw footage | GitHub release `yt-sections` (laptop helper uploads); fetch branches `claude-clips/*`, `footage/*` |
| Engine change (kept) | branch `clips-stream/kai-gta6`: the engine can process part of a long or live stream |
| Upload workflow | PR #159 "Clips: upload a Short" (API; blocked until Google approves the YouTube API audit) |
| Memory (other account) | `/areas/youtube-creator-studio.md`: Franklin's stated direction |
| Notion | Opportunity Radar: 12 campaign rows (Clipping campaign, lane SC); Kai row "Ready for Franklin" |

## 2. Franklin's direction (his words, condensed; newest wins)
1. **Goal: views → money.** GTA 6 only for now.
2. **Copy what is proven, then differentiate;** add creativity after traction. Stop inventing and stop endless prompt loops.
3. **Score every clip** (independent critic); make only those with the highest chance. Quality over quantity. He wants scores, but not "5% chance" clips. Honest rule: no single Short has 80–90% for 100K; aim for a batch with an 80%+ chance of one 100K hit, each clip ≥ 9.5 quality and ≥ 15% for 100K.
4. **Hooks:** natural, funny, human (like a friend's text), true to what's on screen. Never template or AI-sounding. ChatGPT (in his browser) drafts, an independent critic scores, ship at ≥ 9.5.
5. **Map the architecture** of a winning Short. Use the best existing or open-source component per part, and have agents critique and iterate.
6. **Suspense and multi-part series** (each part must stand alone).
7. **Run in the background, end to end, without asking him** (approved 20 Nov), within the hard rules below.
8. He considers COLETHEMAN GTA (channel UCDcsKrsuHgy55hH8V4_elOQ, 4.4M "5 CRAZY THINGS In GTA 6 That You CAN'T Do In GTA 5") the level to reach.

**Hard rules:**
- no nudity or sexual hooks, no slurs, no cruel mockery;
- real footage only, $0 tools;
- never type his passwords, card or ID details, and never verify his identity;
- commits authored `Franklin Mburu <184284364+FranklinMburu@users.noreply.github.com>`, **no Claude co-author line**;
- never push to main;
- no gambling campaigns (GATTOUZ x 1WIN excluded).

## 3. What was done
- **19 Nov:**
  - Round 1: 12 Shorts (stacked facecam/gameplay). Rejected by Franklin as "identical, no creativity".
  - Round 2: trend analyst, director, critic, editors → 13 Shorts.
- **Accounts:**
  - YouTube channel **IntNext** (UCgp716DoAZXqiCdAkghHGVQ), new.
  - **Content Rewards** account created (Gaming/Entertainment/Lifestyle, faceless). Joined 8 campaigns: Kai Cenat GTA 6 $10K, Lacy GTA VI $12.5K, Clix $5K, YourRAGE $5K, AsianJeff $2.5K, Dylan Page GTA VI $5K, Expedia x IShowSpeed $8K, KreekCraft GTA 6.
  - Kai pool rules: name Kai in caption or on-screen text, #KaiCenat, Kai is the main focus, never negative, no logos, no audience-country rule.
- **20 Nov:**
  - Study of COLETHEMAN and 72 GTA channels: format beats size. Top formats: "N things you NEED to know before playing GTA 6", "N things you CAN'T do in GTA 5" / "secrets found", "How X works", "GTA 5 vs 6" (6–21 s).
  - Single streamer reactions: 1 hit in 72 channels; ours got 0–180 views.
  - Built: parrot-C1 and dog-L1 (critic 9.5); secrets1b "5 GTA 6 Secrets Streamers Found 🔍" (list format, Kokoro Puck voice, QA 6 → 7.5 → fixed).
- **Uploads to IntNext** (YouTube Studio in the built-in browser; about 10 uploads per 24 h until the channel is verified). See `room/POSTED.md`:
  - 19–20 Nov batch of 10. Best: Kai "4 MINUTES in the Settings Menu", 460 views, 54% stayed.
  - 21 Nov 00:00 run: secrets1b (public 20 Nov 23:35), parrot-C1 03:00, list-R1 10:00, kai-R2b 13:00, adin-C10 16:00, n3on-R7 19:00, kai-C05 21:30, kai-R3 22 Nov 10:00, kai-C3r 22 Nov 13:00. The Kai ones carry #ad and paid promotion.
  - Held back: dog-L1 (it is item 3 of secrets1b).
- **21 Nov 11:23 loop run:** stopped at the usage limit. Before it stopped, it pushed three new Shorts to `shorts/sc` at 12:26: **k07 Niko, k04 ending face (marked ship), k03 kid (held for fix)**. They are not in POSTED.md or UPLOAD_QUEUE.md yet, so check Studio before uploading them.

## 4. Running automation (other account, precisionexecutionlabs@gmail.com)
- **Scheduled task "Clip Room loop (IntNext Shorts)"** `trig_01BATGMdsxnnr3arjnRZuu5k`:
  - 11:23 AM and 11:23 PM Nairobi, Auto permissions.
  - Requires the desktop DESKTOP-7F8BK0I (built-in browser).
  - Last run 21 Nov 11:23 **failed (usage limit)**. Next run 21 Nov 23:23.
  - Its prompt is the full loop: trend scout, footage, director/critic/editors, publish, push room files.
- **One-off reminder** `trig_01BGNfUPJuSZEoeeGPi3v6R9` (21 Nov 00:05): already fired; nothing left to do.
- **Laptop helper:** a Windows scheduled task `ClipsLaptopHelper`, every 10 min while logged in. It downloads YouTube pieces (Speed) for GitHub and works.
- **Collision rule:** only ONE account may run the loop or upload to IntNext at a time. Before any upload, read POSTED.md and check YouTube Studio's content list, so nothing is posted twice and the 10/day cap is respected.

## 5. Waiting on Franklin
1. **Content Rewards:** sign in and link IntNext's YouTube ("Open YouTube" → IntNext → Allow). Until then the 4+ Kai Shorts are not submitted to the $10K pool, and each must be submitted within 30 min of posting (or as the pool allows).
2. **Verify IntNext** in YouTube Studio (6-second selfie or ID) to lift the ~10 uploads/day cap.
3. **Vyro:** finish sign-up (birthday). Then join "GTA VI YouTube Livestream" ($3 per 1K, funded by YouTube).
4. Decide on a **TikTok account** for the Kai clips (counts toward the pool, faster growth).
5. PR #159 (upload workflow) and the Google API audit (weeks).

## 6. Next steps (from MASTER_PLAN, still current)
1. Read secrets1b's retention (1 h and 24 h). Above 70% stayed → make more lists; below 50% → fix the first second.
2. Build "5 Things You NEED To Know Before Playing GTA 6" (no autosave, story length, controls…), then "How The Wanted System Works In GTA 6" (xQc/Lirik/Cohh chases). Each needs a footage hunt via the fetch workflow (`fetch.py --title-re`).
3. Check k07, k04 and k03 (shorts/sc); upload k04 if it passes and the cap allows; fix k03.
4. Feedback loop: pull retention per Short and update PLAYBOOK.md.

## Latest
- 21 Nov 13:20: the loop moved to Franklin's main Claude account (new scheduled task trig_01Xnz3yJBKhgAGJ58ngaiHKu, same 11:23/23:23 schedule); the old one on precisionexecutionlabs is PAUSED. Both chats on that account are in its project "YouTube Creator Studio — GTA Clip Room (IntNext)". k04 was uploaded this morning; numbers and lesson in POSTED.md / PLAYBOOK.md.
- 21 Nov 19:00: **read room/BLUEPRINT_21NOV.md before making anything.** It holds the 10 laws, the myths we believed, 5 format recipes, a gap analysis of our best 3 and a 15-point critic gate. It comes from a frame-by-frame teardown of 36 winning Shorts Franklin picked (room/reference_teardown/). The critic applies the gate in section 5 before anything ships.
