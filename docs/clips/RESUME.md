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
