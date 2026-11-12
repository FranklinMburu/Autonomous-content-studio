# Clipping research: how clipping works, what wins, and what we can measure (12 Nov 2026)

Written by Claude for the clipping engine (`studio/clips/`, `docs/CLIPS_ENGINE.md`). Every number has a link or is a
measurement we made (files and commands named). What could not be verified is said plainly, in section 6.

**In one paragraph.** Clipping is now a paid marketing channel: streamers, platforms and brands pay clippers per view
(about $0.40-$2 per 1,000 views). Kick funds a large part of it. The rules that matter for us are permission (only
clip people who invite clippers or license their content) and YouTube's 1 Oct 2026 change, which pushes down
channels that re-upload others' videos "without significant changes". From 14 real clip-style Shorts that Franklin
saved, the measured house style is: text on screen from frame 0, speech by 0.05 s (median), 1-3 words of captions
centred around mid-height, yellow highlight, about -14.5 LUFS, about 2 cuts per 10 s. **We do not yet have the 60
winners + 60 baselines dataset.** It needs a free YouTube Data API key, which is Franklin's decision. Section 6 has the
collector, ready to run.

---

## 1. How clipping works, end to end

### 1.1 Platform clip features (official sources)

| Platform | Clip length | Who can clip | Getting the file officially | VOD retention |
|---|---|---|---|---|
| **Kick** | 10-180 s; 60 s cooldown between clips; banned users can't clip | any logged-in viewer, or the streamer | "All Clips can be downloaded when viewed" (.mp4) | 30 days on verified channels, 7 days on others (Kick help centre, as quoted by cut.pro) |
| **Twitch** | 5-60 s, edited from a capture of up to 90 s (`edit_url`) | viewers; API `Create Clip` needs `clips:edit` | `Get Clips` (any token) lists clips with `vod_offset` and view counts. `Get Clips Download` (open beta since 19 Sep 2025) works **only for the broadcaster or their editors** (`editor:manage:clips` / `channel:manage:clips`), up to 10 IDs per call, 100 calls per minute | highlights and uploads capped at 100 h per channel from 19 Apr 2025; clips not affected |
| **YouTube** | Shorts up to 3 min for square or taller videos (since 15 Oct 2024) | n/a | YouTube's terms forbid downloading without YouTube's permission | n/a |

Sources: [Kick help: how to create clips](https://help.kick.com/en/articles/7120566-how-to-create-clips-on-kick);
[Twitch API: clips](https://dev.twitch.tv/docs/api/clips/);
[Twitch forum: Get Clips Download open beta, 19 Sep 2025](https://discuss.dev.twitch.com/t/get-clips-download-twitch-api-endpoint-now-available-in-open-beta/64334);
[TechCrunch: Twitch 100-hour cap, 20 Feb 2025](https://techcrunch.com/2025/02/20/twitch-caps-streamers-storage-at-100-hours-of-highlights-and-uploads);
[9to5Google: Shorts up to 3 minutes, 3 Oct 2024](https://9to5google.com/2024/10/03/youtube-shorts-3-minutes/);
[cut.pro: Kick pays clippers (VOD retention quoted from Kick's help centre)](https://cut.pro/en/blog/kick-paga-clipador-direto-2026).

**What this means for the engine.** The permitted ways to get a stream are:
1. our own streams;
2. a streamer who gives us the VOD or makes us an editor (then `Get Clips Download` works for their clips);
3. a clipping program whose terms allow it;
4. Kick clips through Kick's own download button.

Twitch `Get Clips` with a free app token gives us viewer-clip offsets and view counts. That is the strongest "where
is the moment" signal we can get, without downloading anything. It needs a Twitch developer app (an account, so
Franklin decides).

### 1.2 Clipping programs and campaigns: who pays, how much, rules

- **Rates.** Content Rewards (Whop) listed a median of **$1.09 per 1,000 views** across 707 live campaigns
  (10 Nov 2026): YouTube $1.43, Instagram $1.20, TikTok $1.00. Most campaigns that fill sit at $0.80-$2.00, often with
  a **$200 cap per clip** and a minimum payout (e.g. 2,000 views at $1). Content Rewards takes a 10% creator fee.
  - Clips submitted since 25 Sep 2026 earn for 30 days after they cross the payout threshold.
  - Clips are approved by bot scores, automatic flags and human review. There is one appeal.
  - "Yes, you need permission to clip streamers."

  Sources: [Content Rewards: payouts explained, 9 Nov 2026](https://contentrewards.com/articles/clipping-payouts-explained);
  [Content Rewards: streamer clipping index with rate data, 10 Nov 2026](https://contentrewards.com/blog/get-paid-clip-streamers).
- **Streamer networks.**
  - N3on pays **$40 per 100,000 views** (up to $50), and paid **$1.4M to 303 clippers in five weeks**.
  - MrBeast pays his clippers **$50 per 100k views**, and launched **Vyro** (Oct 2025) for brand and creator briefs.

  Source: [Tubefilter, 29 Apr 2026, citing Business Insider and Complex](https://www.tubefilter.com/2026/04/29/n3on-spending-millions-stream-clippers-tiktok-kick/amp/).
- **Kick.**
  - Clavicular says Kick spent **almost $700,000 in one month** promoting his clips ([Dexerto, 30 Jul 2026](https://www.dexerto.com/kick/clavicular-says-kick-spent-nearly-700000-promoting-his-clips-in-a-single-month-3393030/)).
    That is his claim; Kick did not confirm it.
  - Per Bloomberg (as summarised by cut.pro), one Kick campaign had 1,737 clippers in a month, and 93% of them made
    Clavicular videos.
  - "Kick has no open program that pays any clipper": the money flows through streamer and agency campaigns
    ([cut.pro](https://cut.pro/en/blog/kick-paga-clipador-direto-2026)).
  - Kick is owned by Easygo (Stake). Casino stream clips can count as gambling promotion, which is banned in some
    countries (e.g. Brazil, 25 Sep 2026). **Rule for us: no gambling content.**
- **Red flags** (cut.pro):
  - a fee to join;
  - asking for your account password;
  - "official Kick program" with no trace on Kick's own channels;
  - no written payment terms.

### 1.3 Which streamers and categories are clipped most

From the sources above: Kick IRL / "just chatting" personalities (Clavicular, N3on, Adin Ross) and the largest Twitch
and YouTube streamers. We could not find a public, sourced ranking of the most-clipped categories with numbers. Kick
being the funder explains why Kick IRL dominates the paid campaigns. **Not verified with our own data** (section 6).

### 1.4 YouTube's rules for clip channels (decisive for the design)

On **1 Oct 2026** YouTube said it is "updating our recommendation systems to further prioritize original content".
Channels "primarily aggregating or re-uploading other creators' videos without significant changes" will likely get
less Shorts distribution. Creators should "add real value through your own original commentary, unique edits, or
storytelling".

The reused-content policy disallows "Clips of moments from your favorite show edited together with little or no
narrative".

Sources:
- [YouTube Help community post, 1 Oct 2026](https://support.google.com/youtube/blog/470890423/prioritizing-original-content-on-shorts?hl=en), as summarised by [OutlierKit](https://outlierkit.com/resources/youtube-shorts-original-content-update/);
- [YouTube channel monetization policies](https://support.google.com/youtube/answer/1311392?hl=en).

**Design consequence.** Every clip must carry editorial value: a hook that frames the story, a cold open, captions
and our framing. The workflow does not mass-upload raw cuts. Our edits are "unique edits / storytelling". Whether
that is "significant" enough is YouTube's call, so publishing stays Franklin's decision.

---

## 2. Method

1. Official docs and reputable reporting for section 1, through web search and fetch (links above).
2. **Measurement, not eyeballing.** `python -m studio.clips measure <file>` (`studio/clips/measure.py`) reads:
   - ffprobe;
   - loudness: ffmpeg ebur128;
   - hard cuts: ffmpeg scene score > 0.3;
   - motion and frozen frames: 10 fps grey frames;
   - layout: per-frame textured band, letterbox vs full vs stack;
   - speech onset: RMS above -35 dBFS for 0.15 s;
   - burned-in captions: tesseract OCR every 0.25 s for the first 3 s, then every 1 s; only text at least 1.8% of the
     frame tall counts, so UI text is skipped.
3. The same tool measures our clips. So the comparison is like for like.

## 3. What the best clips look like now (measured)

### 3.1 The reference set (n = 14, measured 12 Nov 2026)

Franklin's saved references, in `C:\Users\DELL\Downloads\video-ideas\refs`:
- `kick-clips/` (2): stream clips used in clipping-payout videos;
- `podcast-cutaways/` (8 under 3 min): podcast and talk-show clips;
- `football/` (4).

They are clip-format Shorts chosen as good examples. We do **not** have their view counts, so this is a quality floor
(the motion-engine method), not a winners-vs-baseline study. Raw numbers: `docs/clips/reference_measurements.csv`.

| Measure | Median | Range |
|---|---|---|
| duration | 60.7 s | 21-161 s |
| first on-screen text | **0.0 s** | 0.0-0.5 s |
| speech starts | **0.05 s** | 0.0-0.92 s |
| hard cuts per 10 s | 2.1 | 0-5.1 |
| median shot | 3.1 s | 1.3-53 s |
| loudness | **-14.5 LUFS** | -22.6 to -4.5 |
| captions on screen | 64% of sampled frames | 38-100% |
| caption height (centre) | 0.575 of the frame (Kick clips: 0.49-0.50) | 0.18-0.85 |
| caption text height | 3.0% of the frame | 2.2-8.2% |
| words on screen | 2 | 1-10 |
| highlight colour | yellow in 11 of 14 | |

Layout: 10 of 14 open full-frame; 4 open letterboxed (both Kick clips open on a 16:9 stream picture centred in the
9:16 frame, with big captions over it, then go full-frame).

### 3.2 Length (secondary sources)

- quso.ai, 108,138 Shorts at least 14 days old: median views peak at **11-20 s (901)**, then 21-30 s (542, read from
  the chart), 31-45 s (347), 46-60 s (188).
  [quso.ai research, updated 29 Jun 2026](https://quso.ai/research/youtube-shorts-length).
  This is all Shorts, not clips; it is quso's own dataset; no dates are given.
- Adobe Express surveyed 507 creators (March 2026): 53% say under 30 s is best for views. This is an opinion survey,
  not analytics. [Adobe Express, 24 Jun 2026](https://www.adobe.com/express/learn/blog/youtube-shorts-length-study).
- Shorts views have counted "starts or replays with no minimum watch time" since March 2025, so raw view counts
  over-reward short loops.
  [Bytecap synthesis of YouTube Help, 17 Jul 2026](https://www.bytecap.io/research/youtube-shorts-retention-benchmarks).

**Decision** (`bar.json duration_s`): target 20-45 s, hard limits 15-58 s. A stream moment needs its setup (which
pushes up from 11-20 s), and the data says shorter is better (which caps it).

### 3.3 Hook

All 14 references put text on screen at once and start talking within a second. YouTube's "viewed vs swiped away"
is the first-second test. **Decision:**
- on-screen hook text from frame 0;
- a clip may not start with silence;
- when the payoff comes more than 9 s in, a ≤2.4 s cold open shows it first (the same moment, so it stays honest).

### 3.4 UI safe zones

YouTube publishes no organic Shorts template. Reap's editorial guide (7 Sep 2026) keeps:
- about 15% clear at the top;
- 25-35% at the bottom;
- 10-15% on each side.

[Reap: safe zones](https://reap.video/blog/short-form-video-safe-zones). **Decision:** captions and hook between 15%
and 72% of the height, 10-88% of the width (`bar.json ui_safe`).

## 4. Prior art (open source)

Licence and release data from PyPI's JSON API (12 Nov 2026). GitHub's API was not reachable from the sandbox, so star
counts were not checked.

| Need | Project | Licence | Latest release | CPU/GPU | Verdict for us |
|---|---|---|---|---|---|
| transcription with word times | **faster-whisper** | MIT | 1.2.1 (31 Oct 2025) | CPU int8 fine | **used** (`transcribe.py`), on GitHub Actions |
| better word alignment | whisperX | BSD-2 | 3.8.6 (May 2026) | GPU best | later, on Kaggle, if word timing drifts |
| | stable-ts | MIT | 2.19.1 | CPU/GPU | alternative |
| speaker diarisation | pyannote.audio | MIT code, gated models | 4.0.7 | GPU best | not used: the models need a Hugging Face account; we use face/motion regions instead |
| scene cuts | PySceneDetect | BSD-3 | 0.7.3 (8 Nov 2026) | CPU | not needed: an ffmpeg scene score in one streaming pass is enough |
| silence cutting | auto-editor | Unlicense | 29.3.1 | CPU | idea reused (cut pauses > 0.6 s from word gaps) |
| face / reframing | MediaPipe (incl. AutoFlip) | Apache-2.0 | 1.2.3 | CPU | the OpenCV Haar face + overlay-box + motion-region detector covers our layouts with no model download |
| | OpenCV | Apache-2.0 | 4.10 pinned | CPU | **used** |
| | Ultralytics YOLO | **AGPL-3.0** | | | **avoided** (licence) |
| chat logs | chat-downloader | MIT | 0.2.8 (2023, stale) | | formats supported in `sources.py` |
| | TwitchDownloader | MIT | | | formats supported in `sources.py` |
| whole pipeline (transcribe → LLM picks → resize) | ClipsAI | MIT | 0.2.1 (Jan 2024, unmaintained) | GPU for diarisation | ideas only: its LLM-free "TextTiling" segmentation is weaker than our signal + LLM ranking |
| VAD | silero-vad | MIT | 6.2.3 | CPU | optional, if Whisper's VAD isn't enough |
| loudness | ffmpeg loudnorm (two-pass) | LGPL/GPL build | | CPU | **used** |

Highlight detection from chat:
- **Lightor** (ICDE 2020): per 25 s window, *message count*, *message length* (people type short when something
  happens) and *message similarity* predict highlights, with top-k precision of "up to 70-90%".
- Chat trails the moment. Lightor found about 20 s on recorded streams, with its learned adjustment at 23-27 s.
- [paper](https://ar5iv.labs.arxiv.org/html/1910.12201).
- Fu et al., 2017 (League of Legends, Twitch): chat and video together predict highlights.
  [arXiv 1707.08559](https://arxiv.org/abs/1707.08559).

### 4.1 Signals we compute, and why (`studio/clips/signals.py`)

- **Chat:** messages per second, short-message share, emote/ALL-CAPS share and copy-paste similarity (Lightor's three
  features). Bot commands are removed: a `!enter` giveaway flood is not a highlight.
- **Chat lag:** measured per stream, not assumed. We vote over (chat-burst start − loud-burst) gaps, then take the
  median.
- **Viewer clips:** coverage weighted by log views; direct human votes.
- **Audio:** loudness, the jump against the last 10 s, high-frequency share (screams and laughs).
- **Picture change.**
- **Transcript:** reaction phrases ("no way", "are you serious", "clip it", laughter).

### 4.2 Which signals actually predict, so far

- On our two lab streams, the moment finder put the real moments first: 4 of 5 in the top 4 on the game stream, and
  3 of 4 in the top 3 on the talk stream. The bot-spam decoy was never picked. That proves the plumbing, not the
  weights, because we wrote those streams.
- The weights in `bar.json signal_weights` are **priors** from Lightor. Refitting them needs real streams with known
  outcomes (section 6).

## 5. Hypothesis report (what we can honestly claim today)

**H1 (format floor, measured, n = 14).** Top clip-style Shorts:
- show text at 0.0 s and speak by 0.05 s (medians);
- caption 1-3 words at about mid-height, upper case, yellow highlight;
- play at about -14.5 LUFS;
- cut about every 5 s (2.1 cuts per 10 s).

A clip below this floor is worse on a feature every reference shares. **Confidence:** these are the medians of 14
clips Franklin picked, with the ranges in 3.1. We have no views for them, so this is a floor, not a cause of views.

**H2 (length, secondary, n = 108k).** Shorter Shorts (11-30 s) get more median views than 31-60 s ones: about 2.6×
for 11-20 s against 31-45 s. **Correlation only:** short videos get more replays, and views count replays.

**H3 (moment finding, literature + lab).** Chat volume, short messages and similarity, measured after correcting for
chat lag, find highlights with precision of up to 70-90% (Lightor). Viewer clips are the strongest single vote.

**H4 (distribution, YouTube policy).** Since 1 Oct 2026, clips without significant editorial change get less reach.
Hook framing, cold opens and our captions are needed for distribution, not optional.

**Not yet testable:** "clips with X, Y, Z get N× more views per day (CI)". That sentence needs the 60 + 60 dataset
(section 6). We will not write it before the data exists.

## 6. The winners-vs-baseline dataset: built, not yet run (blocked)

**What's built.** `studio/clips/dataset.py`:
1. `collect`: YouTube Data API v3. Per clip channel, every Short from the last 90 days: views, age, views/day,
   duration, title. Winners = the top quartile of views/day within each channel, baseline = the bottom quartile, so
   the audience size is the same.
2. Title features.
3. `stats`: Cliff's delta for every feature, and the views/day ratio with a 2,000-sample bootstrap 95% CI.

**Why it is not run.**
- It needs `YOUTUBE_API_KEY`: a free key from the studio's existing Google Cloud project (10,000 units a day; this
  uses about 1 unit per 50 videos). Creating a key is a credential step only Franklin may take. See
  `QUESTIONS_FOR_FRANKLIN.md` Q1.
- Picture and sound features of other people's Shorts (cut rate, caption style, hook) can only be measured from files
  we are allowed to have. YouTube's terms forbid downloading, so the collector never downloads. Options are in Q2.
- The sandbox can reach only package registries and GitHub. YouTube's RSS feeds are blocked to automated fetches
  (robots), and a channel's Shorts page does not render its list without JavaScript (tested 12 Nov 2026).

**Seed channel list.** `docs/clips/channels.txt` is to be filled with the campaigns we actually join. This keeps the
data about the content we would make.

## 7. Raw notes

- Reference measurements: `docs/clips/reference_measurements.csv` (one row per clip, every measured field).
- Reference frames: contact sheets made in the session (`fps=1/2.5`, tiled). The Kick references:
  - both hooks are a stream moment, letterboxed, with 1-3 word green/yellow captions;
  - both then cut to a talking-head tutorial about Content Rewards and Crayo-style auto-clippers;
  - both show campaign dashboards (e.g. "$574.80 earned", an IShowSpeed × Expedia campaign) as screenshots inside
    the video. That is not a source for any number in this report.
