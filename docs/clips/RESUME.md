# Resume here (clipping engine). Written 13 Nov 2026, 01:22 Nairobi, before a usage-limit pause

Read these, in this order:
1. `docs/clips/DECISIONS.md`: every decision so far, and why.
2. `docs/clips/PROMPT.md` (v4): the mission. Follow it.

## State when paused

- Branch `clips-engine`, PR #100, worktree `/home/claude/clips-engine`. Nothing running.
- Done:
  - the bar measured (`REFERENCE_kick_clippers.md`; Clipatra numbers in `DECISIONS.md`);
  - the reachability tests (`clips-probe.yml`: Twitch and Kick work from GitHub, YouTube video is blocked);
  - prompt v4 written.
- Not started: the recall test (the proof stage). No real clip exists yet.

## Progress since (13 Nov, 02:00–03:00)

- **Answer key built** (workflow `clips-recall.yml`, branch `clips-recall/1`). Kai Cenat's Twitch "JAPAN NIGHT LIFE
  STREAM" (v2910392998, 3.3 h, IRL) has 10 fan clips. The top one is "Kai hits his camera man who quits on the spot"
  (27,527 views, about 3:20:36).
  - N3on's Kick streams: fan clips rarely map to listed VODs (the clip `livestream_id` usually isn't in the VOD list).
    Best match: "N3on x Lizzo Halloween Special" (1.7 h), 1 clip only.
  - Kick VOD `source` (`master.m3u8`) works from GitHub, from 160p to 1080p60, **with free subtitles (transcripts)
    in 7 languages**.
- **`lab/clips/recall.py`:** each signal family alone, then all together, picks its top 20; it reports recall
  against the fans' clips (count and view share) and the new finds with what was said.
- **Running:** the full recall run on the Japan VOD (audio-only and 160p download, Whisper base transcript, chat via
  `chat-downloader` (debug), then `recall.py`). Read its log: `gh run view <id> --log` on branch `clips-recall/1`.
- **Still to add:** the vision AI pass (Gemini on frames) and the AI clipper-judge pass, then compare.

## Progress, 13 Nov 03:00–04:00

- Run 43327666336 (signals-only recall, Whisper transcript) running on `clips-recall/1`; its artifact `recall-key`
  holds `words.json`, which the next run reuses (`REUSE_RUN` in `clips-recall.yml`) to skip the 1 h transcription.
- Built and committed (dc38515): `lab/clips/ai_pass.py`
  - `eyes`: Gemini looks at one 160p frame every 4 s (60 per request) and marks clip-worthy moments;
  - `judge`: Gemini scores each candidate (signals top 40 + strong eyes moments) with what was said and seen, against
    the reference-channel taste, and writes a title;
  - `recall.py` gains `--eyes`, `--cands-out`, `--judged`, and the final finder "ALL + AI JUDGE".
- Chat: a Twitch chat-replay step was **not** added (the tool guard refused using Twitch's web client id). Chat stays
  out until there's an approved way; the other signals carry the test.
- **Next:** when 43327666336 finishes, force-push `clips-engine` to `clips-recall/1` to run eyes + judge, then
  report the table to Franklin.

## Result of run 1 (43327666336, signals only; sent to Franklin)

Audio 2/10 (9% of views), speech 4/10 (14%), picture 3/10 (6%), ALL 5/10 (32%). Missed the top clip (camera man,
27.5K) because its estimated offset (12036) is past the VOD end (11805): creation-time offsets are unreliable.
Fix: `lab/clips/align.py` matches each fan clip's sound to the stream (offline test: exact to 0.1 s).
New finds worth judging: Drake on the phone (~0:36:48), fan from Uzbekistan (2:24:37).

Run 2 (43331217075, commit f8f4cdd): exact key + AI eyes + AI judge. Read its log for the table.

## 13 Nov 04:00–04:35 Nairobi

- Open-source research, 2 rounds (`docs/clips/OSS_RESEARCH.md`). Closest project: **clipit** (MIT). Copied as-is into
  `third_party/` (clipit, ClippyMe, Hooky) at Franklin's request.
- Franklin approved TwitchDownloaderCLI for Twitch chat on GitHub (in `clips-recall.yml`).
- Judge upgrades: ClippyMe gate and rubric, Hooky global ranking, and it now **watches and hears** a 90 s low-res
  clip of each candidate (SliceQ/clipit lesson).
- `lab/clips/kick_chat.py`: Kick VOD chat with no key (clipit's reader), tested in the recall run.
- A background watcher pushes `clips-engine` to `clips-recall/1` (run 3) when run 2 (43331217075) ends. If the
  session restarted, check: `gh api "repos/FranklinMburu/Autonomous-content-studio/actions/runs?branch=clips-recall/1&per_page=3"`.
- Next after run 3: port clipit's veto reviewer (7 checks on the finished clip) and "who's hot today"; benchmark:
  clipit's own finder caught 20 of 38 good clips on 10 Kick VODs.

## Next step, exactly

1. Pick 2 real streams: a recent Kai Cenat Twitch VOD (`clips-probe` listed `https://www.twitch.tv/videos/2924282282`
   and others) and a recent N3on Kick VOD (from `https://kick.com/api/v2/channels/n3on/videos`).
2. Answer key: the fans' top clips of those VODs, with timestamps and views (Twitch clips list; Kick
   `/api/v2/channels/n3on/clips`), plus any matching Shorts on the reference channels.
3. On GitHub, fetch for each stream: audio only, low-quality video, chat (find a chat tool that works; `chat-downloader`
   returned nothing). Run the finder five ways: chat only, audio only, picture only, all together, all plus the AI judge.
4. Score recall against the answer key. Show Franklin the table and 2–3 real moments found, including ones nobody
   clipped.
5. If about 9 of 10 hits are found and Franklin likes the new finds: build the Short-making and packaging (prompt v4 §5–6),
   rating every part each round until everything is ≥ 9.5.

## Also open (Tech Education, a separate track)

- PR #89 (Tech Education variety + episodes 002 and 003) is finished and waiting for Franklin to merge.
- The untracked `polish/film/004-…/answer.json` in the main checkout waits for Franklin's call. Don't commit it.

## 13 Nov 04:35–06:45 Nairobi (latest)

- **Recall run 5 (43358915880):** all signals + AI judge find **9 of 10 fan clips (98% of their views) in the top 60**;
  top 20 = 5/10, top 30 = 7/10. Weak spot: the judge's ranking (camera-man moment 5.9, rank 53 of 83). Next: teach the
  judge physical surprises with the crew; more picks per stream.
- **Lanes approved (Franklin):** HR, TE, SC (Streamer Clips), WC (World Clips). **Notion Studio Board** (database under
  YouTube Creator Studio, one tab per lane, stages Picked → Making → Review → Approved → Posted / Skipped). Lane pages:
  SC (was "livestream clipping"), WC (new). Full record: Notion page "Clipping engine: full record (13 Nov 2026)".
- **Who's hot** (`studio/clips/hot.py`, `clips-hot.yml`): streamers lane and world lane both working.
- **Laptop helper** installed by Franklin and proven: `WC-test-aligvslogan` (40 s, 1080p, 20.5 MB) uploaded to release
  `yt-sections`. Requests go on branch `clips-jobs`. Downloading release assets from Claude's workspace: use
  `gh api -H "Accept: application/octet-stream" repos/.../releases/assets/<id>` (gh release download uses GraphQL, blocked).
- **Next:** judge fix + re-test; first real SC Shorts from the board picks; WC after; Notion token for automatic board.
- **Notion board automatic (13 Nov 06:53):** secret `NOTION_TOKEN` (connection "Studio Board bot", board only). Proven by run 43361862139 (card "Board connection test"). `studio/clips/board.py`; `clips-hot.yml` posts top 5 SC + WC picks each run.
- **13 Nov 07:30–08:30:** mentor agent (`.claude/agents/mentor.md`); first 5 real Shorts (scores 7, 7, 4, 3, 3);
  judge with real-winner anchors + crew/cameraman class (run 6: top 20 = 6/10, top 30 = 8/10 = 96% of views; camera
  man rank 53 → 20); the winners' look measured (above, REFERENCE_kick_clippers.md) and copied; Shorts in parallel
  jobs; research on voice / pipelines / presenters in `docs/lanes/`; reference breakdown of Maitis and Griffin in
  `docs/lanes/REFERENCE_maitis_griffin.md`.
