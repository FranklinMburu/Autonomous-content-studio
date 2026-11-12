# Mission prompt v3: the Clipping Engine (13 Nov 2026)

You are Claude, building the clipping engine for Franklin Mburu's YouTube Creator Studio. Use your full creativity and
intelligence. **Build first. Make it as good as the best clippers.** Handle the sensitive parts (rights, platform
rules) when a clip is about to be published, not before it exists. That was Franklin's call on 13 Nov 2026, after an
over-constrained first attempt produced nothing real.

## 1. Franklin's intent (confirmed by him)

Add a clipping engine to the existing Creator Studio pipeline (repo `FranklinMburu/Autonomous-content-studio`),
integrated like the Tech Education engine: its own folder `studio/clips/`, its own workflow button, its own tests, and
nothing in Hidden Reasons or Tech Education touched.

What it does:
- It takes long live streams (3–6 hours, from Kick, Twitch, YouTube Live and other platforms) of the creators clip
  channels are built on: Kai Cenat, IShowSpeed, N3on, Adin Ross, DDG, Blueface, Deshae Frost and whoever is trending
  now.
- It works through the whole stream like the best human clipper and pulls out the moments that go viral:
  - celebrity and IRL encounters;
  - someone shocked, exposed, humbled or caught;
  - relationship drama;
  - emotional beats;
  - money and flex moments.
- It turns each moment into a finished Short indistinguishable from the reference channels below:
  - the payoff hooked in the first second;
  - the right vertical framing of the streamer and the guest;
  - bold word-by-word captions, tight cuts and clean sound;
  - their exact title style.

How it must work:
- Grounded in real, current, checkable research: real channels, real clips, real view counts, with links.
- It judges itself honestly against the real winners and keeps improving until its clips stand beside them
  (≥ 9.4/10).
- Automatic, $0, reusing free and open-source tools.
- When something blocks it, it finds a practical way around and doesn't stop.
- It doesn't waste Franklin's usage on work he can't see. **Franklin judges by watching real clips of real
  streamers**, so a real clip comes first and early.

## 2. The bar

Read from the channels' public lists by `clips-reference.yml` on 13 Nov 2026. The top 60 of @Kick_Clippers are in
`docs/clips/REFERENCE_kick_clippers.md`.

**@Kick_Clippers** (`UCIPD8q8n3Vy7Qfz59RTc1Jg`): 3,392 Shorts; median 21K views; top 10% ≥ 248K; best 32M.
- [IShowSpeed EXPOSED the strongest man in Africa for CHEATING](https://www.youtube.com/shorts/Y2eGg3Su7LI) (32M)
- [The moment N3on Realized Iggy Azalea hasn't USED her PHONE…](https://www.youtube.com/shorts/tq2tpazYM2Y) (28M)

**Clipatra** (`UCxlQSBBswmNP-wFDkcFrDBw`): 4,046 Shorts.
- [The moment Blueface used his viral catch phrase on his date and it worked](https://www.youtube.com/shorts/htxyiW5xBwE) (7.8M)
- [The moment DDG and India Love started flirting on stream](https://www.youtube.com/shorts/hX4BfgyVeA0) (4.5M)

**Title formula on both:** "The moment / No way [streamer] [REALIZED / was SHOCKED / EXPOSED / couldn't believe …]
[situation] 😳😭💔 #streamer", with key words in CAPS.

**Target:** the top-10% range of these channels, not their median.

## 3. The only fixed lines (everything else is your judgement)

1. $0: no paid tools or tiers. One account per provider.
2. Never use Franklin's passwords, login cookies or keys outside GitHub secrets. Never read `.env`.
3. Nothing is published or uploaded anywhere, and nothing is merged to main, without Franklin's yes. Work branches,
   PRs and GitHub releases for review are fine.
4. No fake footage presented as a clip. Real streams only for anything shown to Franklin; test media stays inside
   automated tests.

**At publish time, not before:** the engine attaches a "before you post" note to each clip:
- the streamer's clipping status (open campaign, encouraged, or unknown);
- the campaign's rules, such as required hashtags, platforms and footage window;
- any risk flags.

The engine must not refuse to make a clip because rights aren't recorded. Turn the current rights gate in
`studio/clips/sources.py` and the workflows into this note.

## 4. What exists (reuse it)

Branch `clips-engine` (PR #100), worktree `/home/claude/clips-engine`, docs in `docs/CLIPS_ENGINE.md`.
- `studio/clips/`:
  - moment finding (chat spikes, viewer clips, audio, transcript, LLM ranking through the brain);
  - vertical layout with wide and close shots, hooks, word-by-word captions, loudness, gates;
  - a blind-judge harness;
  - `tests/test_clips.py` passes.
- `make-clips.yml`: a VOD link (yt-dlp) or folder in, clips out as releases. It runs before merge through
  `clips-run/*` branches holding `clips_request.json`.
- `clips-reference.yml`: public channel lists and views (no video downloaded).
- **What GitHub's machine can and can't reach** (`clips-probe.yml`, 13 Nov 2026):
  - **Twitch works fully:**
    - listing VODs, with sizes (a long Kai Cenat VOD is 33 GB at 720p and 116 GB at 1080p60, but only 3 GB audio
      only);
    - **downloading only a section** (60 s at 1080p60 = 65 MB in 3 s);
    - audio only (10 min = 12 MB in 3 s, so a 6-hour stream is about 430 MB);
    - viewer-made clips with view counts, and the clip files themselves.
  - **Kick works:** the API (channel, VOD list, top clips with views) and the clip files on `clips.kick.com`. It
    returned 403 once earlier, so retry with backoff.
  - **YouTube is blocked** for video and player data ("Sign in to confirm you're not a bot"). Public lists and view
    counts still work.
  - Chat replay with `chat-downloader` produced nothing in the first test. Debug it, or use Twitch's comment data
    through another open tool.

## 5. The work, in order

1. **Smart ingest: never download a whole stream.**
   - **Find the moments without the video:**
     - viewer-made clips (Twitch and Kick, with view counts and offsets: the strongest signal);
     - chat replay;
     - the audio-only track (~70 MB per hour), for the transcript, laughter and hype;
     - on YouTube, the "most replayed" heatmap.
   - **Then download only the chosen moments,** with context (2–3 min each at the best quality, ~65 MB per minute at
     1080p60). Everything runs on GitHub's machine and is deleted after the run. A 6-hour stream costs about 0.5 GB of
     audio plus 1–2 GB of moments, not 20–100 GB.
   - **YouTube sources only** (blocked on GitHub): add a small `fetch_vod` job to Franklin's laptop runner
     (`runner.py` + `jobs/inbox`, allowed tasks in `jobspec.py`, repo `FranklinMburu/AI-layer`). It fetches the
     heatmap and transcript first, then only the chosen sections, uploads them to a GitHub release and deletes them
     locally.
2. **One real clip, fast.** Start with Twitch or Kick, because they work on GitHub today: Kai Cenat (Twitch) or N3on
   (Kick). The IShowSpeed × Expedia campaign stream (YouTube, 6 Nov 2026, from 2:56:29, see
   https://contentrewards.com/c/campaigns/afeca1a0-f44c-46ad-8194-09d62b56589e) needs the laptop route. Make the clips and show Franklin
   the best one with its title. Wait for his verdict.
3. **Study the bar deeply.**
   - Rank all Shorts on both channels and compare the top 10% with the median: topics, people, title words, emoji,
     length.
   - Fetch about 10 top Shorts per channel through the laptop route (or ask Franklin to save them) and measure them
     frame by frame: hook timing, framing of streamer and guest, caption font, size, position and colour, cut rate,
     zooms, sound, length, ending.
   - Write `docs/clips/RESEARCH.md`, "The bar, measured", with links.
4. **Make the engine match the bar:** moments of the winning kinds; titles in the exact formula; captions, layout,
   cuts and sound measured equal to the reference.
5. **Iterate on real streams:** at least 3 VODs, IRL and gaming. Each round: make, judge, fix the weakest criterion
   in the engine, remake. Show Franklin the best clip of each round.
6. **Ship:**
   - the button "Make clips": paste a VOD link, the laptop downloads it, GitHub clips it, and the clips come back as
     releases with the "before you post" note;
   - docs in plain language;
   - a PR with all tests green.

## 6. Judging

- **Scorecard 0–10:**
  - moment strength (would it stop a scroller?);
  - hook in the first second;
  - title in the formula;
  - framing;
  - captions;
  - pacing and cuts;
  - sound;
  - length;
  - ending.

  Weights come from the measured bar.
- **Blind:** our clips are mixed with real top clips from the reference channels, unlabelled. A judge that didn't make
  them (the brain's `judge` on GitHub Actions, or a separate agent) scores and ranks them all.
- **Bar:** ≥ 9.4, and on every measured feature at least the median of the reference top 10%.
- **Franklin's eye is final.** Never inflate. If 9.4 isn't reached, say exactly why.

## 7. Reporting

- Short plain updates, each with a real clip attached when one exists: what changed and what's next.
- Progress on PR #100 and in `docs/clips/PROGRESS.md`.
- **Tell Franklin about every bottleneck as soon as it appears,** with the workaround you found and exactly what he
  could do to help, if anything.
