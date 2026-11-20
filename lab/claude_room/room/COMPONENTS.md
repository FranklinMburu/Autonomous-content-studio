# COMPONENTS: the best existing part for each layer of a Short (20 Nov 2026)

Method: 24 web searches and page fetches on 20 Nov. Star counts come from GitHub pages fetched today. The proxy blocked the GitHub API, so most "last activity" dates are unknown (marked "?").
Commercial tools are black boxes. Everything about them here comes from their own docs or blogs, plus one Reap vendor report. I found no OpusClip patent. Nothing here has been tested hands-on yet (AI_TOOLS_LAB.md step 2 is still open).

## Summary

| # | Component | Best $0 option | Paid benchmark to imitate | Our current state | Gap |
|---|---|---|---|---|---|
| 1 | Topic/trend | YouTube Data API search + our own scrape (TREND_DATA_*.md) | Munch (trend-aware selection) | Manual 9-query scrape each day | Not scheduled; no velocity metric |
| 2 | Moment finding | yt-dlp `heatmap` + chat velocity (TwitchDownloader/chat-downloader) + LLM transcript scoring | OpusClip ClipAnything; Eklipse Gameplay Intelligence | LLM reads the transcript, plus a human | No heatmap or chat signal |
| 3 | Story/length/series | Our SERIES_PLAYBOOK + CHANNELS_LIKE_COLE data | OpusClip "Flow" score | Rules on paper | Length isn't chosen per format |
| 4 | Hook | HOOK_BLUEPRINT rubric + LLM | OpusClip "Hook" score; SupoClip burned-in hook title | Strong rubric | Rubric not enforced automatically |
| 5 | Reframing | OpenShorts reframe module (MediaPipe + YOLOv8) | OpusClip Gameplay layout (cam 30% / game 70%) | Hand-keyed crop keys, facecam stack | Tracking is manual |
| 6 | Pacing | auto-editor (silence/motion cuts) + ffmpeg zoompan | Submagic auto-zooms on transcript beats | Straight cuts | No beat-synced zooms, no loop check |
| 7 | Captions | whisperX alignment + pycaps (or our PIL) | Submagic / Reap keyword-highlight styles | One punch caption (PIL PNG) | No word-by-word karaoke |
| 8 | Audio | ffmpeg loudnorm (done); Kokoro TTS; YT Audio Library | Submagic SFX | -14 LUFS two-pass | No SFX layer (fine for now) |
| 9 | Packaging | Blueprint + desktop custom Shorts thumbnail (YPP only) | OpusClip "Trend" + title generation | Titles strong | Thumbnail unavailable (not in YPP) |
| 10 | Publishing | YouTube Data API `videos.insert` with `publishAt` | AutoClip/OpenShorts scheduler | Manual | No schedule |
| 11 | Analytics | YouTube Analytics API retention reports | OpusClip/SupoClip feedback loop | None automated | Biggest gap |
| 12 | QA/critique | Gemini video understanding (free YouTube-URL input) + our critic | OpusClip virality score (0-99) | Text-only critic | Critic can't watch the render |

---

## 1. Topic / trend selection
- **Open source:** google-marketing-solutions/youtube-topic-insights (Apache-2.0; public 22 Jan 2026, last update 4 Feb 2026) uses the YouTube Data API plus Gemini, but it needs GCP billing and Terraform; too heavy. pytrends is free but "breaks randomly" (dev.to 2026 test).
- **Paid:** Munch's trend-aware selection was its differentiator, but its standalone clipper is discontinued (Reap report). OpusClip folds "Trend" into its virality score.
- **Verdict:** Keep our own scrape. **Next step:** script the 9 TREND_DATA queries against the YouTube Data API (search.list + videos.list, about 1K quota units) in GitHub Actions twice a day, and rank by views per hour since publish.

## 2. Moment finding in long VODs
- **Open source:**
  - **OpenShorts** (mutonby/openshorts, 8.9k stars, MIT core): Gemini or a local LLM scores the transcript plus scene cuts and returns 3-15 moments with virality scores.
  - **FunClip** (modelscope): ASR plus LLM clipping.
  - **ClipsAI** (545 stars, MIT): transcript-based, built for podcasts.
  - **stream-clipper** (3 stars): RMS audio plus chat spikes, merged with weights. Reusable idea only.
  - **yt-dlp** exposes YouTube's Most-Replayed `heatmap` (start, end, value 0-1). That gives us free audience-truth for YouTube VODs.
- **Paid:**
  - OpusClip's own recipe: messages per 10 s against a baseline, flag several-times spikes, start the clip about 30 s before the spike.
  - Eklipse "Gameplay Intelligence": kill feed/game state, scene-aware frames, voice separated from game audio, action density.
  - StreamLadder ClipGPT doesn't disclose its signals.
- **Verdict:** Fuse three free signals: heatmap (YouTube), chat velocity (Twitch/Kick via TwitchDownloader CLI / chat-downloader), and the LLM transcript score we already have. **Next step:** add `signals.py` that prints the top 10 windows per VOD as `score = 0.4·heatmap + 0.4·chat_z + 0.2·llm`, then check it against the moments we already picked by hand.

## 3. Story structure / length / series
- Nothing reusable (repos emit 15-60 s windows; OpusClip's "Flow" score is opaque).
- **Our data** (CHANNELS_LIKE_COLE): comparisons at 6-21 s loop best; explainers and lists work at 37-68 s; streamer reactions are setup, turn, consequence.
- **Verdict:** Our own rules beat any tool here. **Next step:** add a `format` field to each spec (reaction / comparison / list) with a hard length band per format.

## 4. Hook (frame 0 + on-screen text)
- **Open source:** SupoClip (AGPL-3.0) burns an AI hook title into the opening seconds and scores hook, engagement, value and shareability.
- **Paid:** OpusClip's "Hook" score asks whether the intro grabs attention and relates to the topic.
- **Verdict:** HOOK_BLUEPRINT is more specific than anything public. **Next step:** turn the 10-point rubric into a JSON-output critic gate (ship at 8+), and add a check that frame 0 matches the noun (feed frame 0 to a vision model).

## 5. Reframing 16:9 → 9:16
- **Open source:**
  - **OpenShorts** does per-scene MediaPipe + YOLOv8 tracking, with blurred-background, split and screencast layouts. This is the best reusable code.
  - **ClipsAI** reframes on the active speaker via pyannote.
- **Paid:**
  - OpusClip has 7 layouts, including Gameplay (speaker on top 30%, game below 70%) and Fill.
  - A user review says OpusClip is weaker on gaming (about 60% usable clips vs 80-85% for podcasts), and reframes fail 5-10% of the time.
- **Verdict:** Lift OpenShorts' tracker into fullscreen.py to generate our crop keys. Keep our facecam-stack layout. **Next step:** run YOLOv8n on 2 fps samples, smooth with an EMA, write `keys`, and compare against the hand keys on the parrot/dog clips.

## 6. Edit pacing
- **Open source:** auto-editor (5.9k stars, Unlicense) cuts silence or motion with `--margin` and exports to Resolve/Premiere. PySceneDetect finds cuts.
- **Paid:** Submagic syncs zooms to transcript key moments (6 styles), auto-cuts silence, and adds B-roll.
- **Verdict:** auto-editor for dead-air removal inside a window, plus a 1.0→1.08 ffmpeg punch-in on the turn word (from Whisper timestamps). **Next step:** pass `--edit audio:threshold=4% --margin 0.15s` on a reaction clip and A/B it against the uncut version. Also add a loop check: is the last frame close to the first?

## 7. Captions
- **Open source:**
  - **whisperX** (23.9k stars, BSD-2): wav2vec2 alignment fixes Whisper's drifting word timestamps. It runs on CPU.
  - **pycaps** (francozanardi): CSS-styled word-by-word animation, with an optional LLM keyword tagger.
- **Paid:** Submagic has 35+ styles and animated emoji. Reap claims AI keyword highlighting. These are the visual benchmark.
- **Verdict:** whisperX for timing, then render karaoke ourselves (PIL overlays per word, keyword in yellow). This fits edit.py better than adding a new renderer. **Next step:** swap `small.en` for whisperX align and diff word start times on one clip.

## 8. Audio
- **Open source:** Kokoro-82M (9.8k stars, Apache-2.0) is the best free TTS if we ever narrate. Note that HOOK_BLUEPRINT flags "narrator voice" as a red flag for reaction clips. Two-pass loudnorm is already correct.
- **Verdict:** No change for reaction Shorts. Kokoro only for future knowledge/explainer Shorts. **Next step:** none now; a 1-hour trial of Kokoro if we start an explainer format.

## 9. Packaging (title, description, hashtags, thumbnail)
- **Facts:**
  - Custom Shorts thumbnails rolled out 25 Jul 2026. They are desktop upload only, Partner Program channels first, with no A/B testing.
  - At ~300 subs we aren't in the Partner Program, so we likely only get frame choice on mobile.
- **Verdict:** Titles via blueprint. Description is the first line plus #GTA6 #Shorts plus the streamer name. **Next step:** template the description and hashtags in the spec JSON.

## 10. Publishing (timing, cadence)
- **Open source:** OpenShorts publishes via Upload-Post (third-party). The YouTube Data API `videos.insert` with `status.publishAt` is free.
- **Data:** Buffer (1.8M videos) found Friday is best for Shorts, then Saturday and Thursday. Evenings around 6-11 pm are strongest; Monday and Tuesday are weakest. That data is US-centric, so convert for our audience.
- **Verdict:** Schedule through the API from GitHub Actions. **Next step:** OAuth once, then upload as private with `publishAt`. Franklin decides on connecting the account (AI_TOOLS_LAB rule: never connect social accounts without approval).

## 11. Feedback analytics
- SupoClip feeds performance back into selection: the pattern to copy.
- **API:** The YouTube Analytics API exposes `audienceWatchRatio` and `relativeRetentionPerformance` by `elapsedVideoTimeRatio`. I couldn't fetch the Google page (robots), so confirm Shorts support in the docs. "Viewed vs swiped" is visible in Studio; I couldn't confirm it's in the API.
- **Verdict:** This is our biggest gap. **Next step:** a nightly job that pulls views, average view %, and the retention curve per Short into `analytics.csv`. Tag each row with its rubric score and format, and after 30 Shorts fit simple rules ("noun hooks > mood hooks").

## 12. Automated QA / critique
- **Open source / free:**
  - Gemini video understanding takes a public YouTube URL free (preview, 8 h/day on the free tier). It samples 1 fps by default and accepts `MM:SS` prompts.
  - Unlisted and private videos aren't supported, so render-time QA must upload the file instead.
- **Paid:** The OpusClip virality score (Hook / Flow / Value / Trend, 0-99, weighting undisclosed) is the thing to imitate as a triage, not a verdict.
- **Verdict:** Upgrade the critic from text-only to "watches the render". **Next step:** send each final MP4 at 2 fps with the 10-point rubric and a checklist (caption in safe zone, frame 0 matches text, no black frames, LUFS) and block below 8.

---

## REA (Reverse Engineer Anything): any legitimate use?
1. REA (github.com/morluto/rea, MIT; project-reported 180K+ stars, Oct 2026) analyses things you own or are authorised to examine: binaries, Electron apps, APKs, .NET, and websites' client-side scripts and network. Its disclaimer excludes DRM, licence-check and anti-cheat bypass.
2. It cannot see OpusClip/Submagic/Klap server-side models. Those run on vendor servers, and at most it would show the web client calling an API. Their ToS also forbid reverse engineering, so it's not worth doing.
3. The one legitimate niche: understanding how an open-source or locally installed desktop clipper (e.g. an Electron app we've installed) builds its ffmpeg filter graph. Reading the source on GitHub is faster and cleaner, so treat REA as a low priority.

## Sources
- OpenShorts: https://github.com/mutonby/openshorts
- ClipsAI: https://github.com/ClipsAI/clipsai
- auto-editor: https://github.com/wyattblue/auto-editor
- whisperX: https://github.com/m-bain/whisperx
- SupoClip: https://raw.githubusercontent.com/FujiwaraChoki/supoclip/main/README.md
- pycaps: https://dev.to/francozanardi/how-to-create-content-aware-animated-subtitles-with-python-24dn
- Kokoro: https://github.com/hexgrad/kokoro
- stream-clipper: https://github.com/nirvagold/stream-clipper
- yt-dlp heatmap type: https://docs.rs/crate/yt-dlp/latest/source/src/model/types/heatmap.rs
- OpusClip chat recipe: https://www.opus.pro/mcp/inspiration/clip-the-moments-your-live-chat-exploded
- OpusClip virality score: https://help.opus.pro/docs/article/virality-score.md
- OpusClip layouts: https://help.opus.pro/docs/article/layout-and-reframing.md
- OpusClip on gaming: https://polyinnovator.space/opusclip-is-not-great-at-gaming-clips-here-is-why-i-use-it-anyways
- Eklipse: https://blog.eklipse.gg/streaming-tips/how-gameplay-intelligence-works-2.html
- StreamLadder: https://streamladder.com/clipgpt-features/ai-clipping
- Submagic: https://submagic.co/features/auto-zooms
- Reap vendor report: https://reap.video/reports/state-of-top-ai-video-clipping-tools-2026
- YouTube Topic Insights: https://ppc.land/youtube-topic-insights-googles-open-source-gemini-tool-that-finds-trends-for-you/
- Google Trends scrapers: https://dev.to/sonagara-vashram/i-tested-6-google-trends-scrapers-so-you-dont-have-to-heres-what-actually-works-in-2026-1l2e
- Shorts thumbnails: https://ppc.land/youtube-ends-2-year-wait-for-shorts-thumbnails-but-blocks-a-b-testing/
- Buffer timing: https://buffer.com/resources/best-time-to-post-on-youtube/
- Gemini video: https://ai.google.dev/gemini-api/docs/video-understanding.md.txt
- REA: https://github.com/morluto/rea and https://www.developersdigest.tech/blog/reverse-engineer-anything-rea-mcp-agents-guide-2026
