# Claude Clip Room: the background loop (runbook)

Franklin's goal (his words, 19-20 Nov 2026): Shorts whose hook "captures the gap instantly": you read it and go "damn", you
watch and you laugh. Views = money. Diverse, unexpected angles, not "X was SHOCKED". Formats that reach millions
(e.g. 3.9M "5 CRAZY THINGS In GTA 6 That You CAN'T Do In GTA 5": a countdown vs GTA 5). His pipeline is paused; Claude does
the creative work. He approved running end to end without asking (19 Nov): pick, edit, upload, schedule to IntNext.

Fixed lines: $0 tools; real footage only; nothing sexual/nudity (incl. GTA strip clubs, shower, sex scenes), no slurs;
never mock streamers cruelly; never paid tools; never Franklin's passwords/cards/ID; commits authored as Franklin
(184284364+FranklinMburu@users.noreply.github.com), never a Claude co-author line; never push to main.

## 0. Set up (fresh session)
```
git clone -q -b claude-room https://github.com/FranklinMburu/Autonomous-content-studio.git /home/claude/studio
mkdir -p /home/claude/clips && cp -r /home/claude/studio/lab/claude_room/* /home/claude/clips/
```
Workspace: no Twitch/Kick/YouTube access; only GitHub (git + gh) and the web tools. ffmpeg, PIL, numpy are installed.
Footage comes through GitHub Actions; YouTube footage only through Franklin's laptop helper.

## 1. Trend scout (10 min, browser)
In the built-in browser (tab on youtube.com), run the search script: queries "<streamer> gta 6" for Kai Cenat, IShowSpeed,
xQc, Jynxzi, Lacy, Adin Ross + "gta 6 streamer", filter "uploaded today" (sp=EgIIAg%253D%253D), collect Shorts
(shortsLockupViewModel: views + title), sort by views. Save room/TREND_DATA_<date>.md with the pattern of the day.
Also read IntNext's own numbers (studio.youtube.com, channel UCgp716DoAZXqiCdAkghHGVQ, videos/short + each video's
analytics: views, "Stayed to watch" %). Our bar: stayed-to-watch >= 70%. Add one dated line per lesson to room/PLAYBOOK.md.

## 2. Footage (GitHub, 20-60 min)
Branch claude-clips/gta6 has lab/claude_clips/fetch.py + .github/workflows/claude-fetch.yml (push to a claude-clips/*
branch with a matrix of sources; footage lands on branch footage/<name> as mp4 + json with Whisper words + fan-clip
titles/views; clone it with --depth 1). Twitch: `twitch --vod <url> --channel <login> [--from-s/--to-s] --top N`;
Kick: `kick --slug <slug> --uuid <vod uuid> --top N` (uses the fan clips themselves). Find current VODs with the probe on
branch clips-probe/gta-launch. Fan-clip views = proof of demand. Live VODs are slow: top <= 9, timeout 75.
For source quality re-renders: fetch exact ranges (claude-clips/kai-hq branch pattern) and align by audio
cross-correlation (fallback: normalized frame matching); Twitch VOD timelines can shift, verify the match > 0.9.
YouTube (IShowSpeed etc.): append to youtube_requests.json on branch clips-jobs ({"id","url","kind":"info"} or
{"id","url","start","end"} <= 600 s); the laptop helper uploads <id>.mp4 / <id>.info.json to release yt-sections within
~10 min while the laptop is on; read with `gh api -H "Accept: application/octet-stream" repos/.../releases/assets/<id>`.
Moment-finding on YouTube needs the "Most replayed" heatmap (appears hours after a stream ends).

## 3. Creative room (agents)
1. Creative director: reads trend data + PLAYBOOK + all transcripts/frames; writes room/SLATE.md: 15-25 concepts, each with
   4 competing hooks; must include at least 2 compilation/list formats (e.g. "5 things streamers discovered in GTA 6",
   "GTA 6 vs GTA 5" moments) built only from campaign-eligible streamer footage.
2. Critic (views only, harsh, independent): CRITIQUE.md, BUILD/FIX/KILL, final hooks, build-first list.
3. Editors (2-3 in parallel): build with edit.py / supercut.py per SPEC.md (facecam band + gameplay band, title box
   y 210-390, punch captions on the seam, -14 LUFS, face >= 350 px, frame 0 = the funniest/most surprising frame).
4. Critic reviews the renders frame by frame (fps=2 strips); only SHIP goes out.
Kai Cenat clips: description has "#ad" + #KaiCenat, Kai main focus, never negative (RULES_KAI_POOL.md).

## 4. Publish (browser, IntNext)
Push mp4 + json to branch shorts/sc. In the built-in browser at viewport 1366x900, open https://www.youtube.com/upload;
JS: fetch https://raw.githubusercontent.com/FranklinMburu/Autonomous-content-studio/shorts/sc/<id>.mp4 -> File ->
DataTransfer -> ytcp-uploads-dialog input[type=file] + change event; title/description via focus + execCommand
('selectAll' then 'insertText'); paid promotion (Kai) = Show more (#toggle-button) then the "Yes, my video includes
paid promotion" tp-yt-paper-radio-button; NOT_MFK radio; #next-button x3; #second-container-expand-button; set the
time with JS: input.value='H:MM AM/PM' + input + change events + keydown Enter event (never press a real Enter key:
it closes the dialog as a draft); wait for "Checks complete"; #done-button -> "Video scheduled".
New channel limit: about 10-11 uploads per 24 h ("Daily upload limit reached"); verification is Franklin's.
Space posts 2-4 per day, 2-3 h apart, mixing streamers; Kai clips spaced.
Then submit Kai clips on Content Rewards (Kai pool) once IntNext's YouTube is linked there; record links in
room/POSTED.md and push the room back to branch claude-room.

## 5. Report
Send Franklin a short message: what went up (links + times), current numbers, the one lesson learned.
