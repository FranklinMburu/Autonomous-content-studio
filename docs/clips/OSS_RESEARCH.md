# Open-source clipping projects, read down to the code (13 Nov 2026)

17 repos cloned and read (scratch copies, not vendored). Question: has anyone done better than us at
"stream in → viral Shorts out", and what can we take?

## Round 2 (Franklin pushed back: "no way no one has thought about this"; he was right)

Round 1 searched English GitHub only. Round 2 added China's livestream-slicing industry (直播切片), clip-farm bots and
2025–26 papers; 11 more repos cloned. **It found a project close to ours:**

**clipit** (github.com/EJaredMejia/clipit, MIT, updated 12 Nov 2026): Twitch and Kick VODs → 9:16 Shorts. Read in full:
- Finds moments from loudness plus lag-corrected, hype-weighted chat (`moments.py`): a simpler finder than ours, with
  no vision over the whole stream and no recall test.
- **Kick VOD chat with no key:** `web.kick.com/api/v1/chat/<channel_id>/history?cursor=<µs>`, sampled in parallel and
  then read closer around loud spots (`kick.py`). Our Kick blocker, solved.
- **Viewer clips first:** "a moment strangers already chose beats any spike".
- **Who to clip today:** ranks Twitch/Kick streamers by the views on their clips in the last day, plus a web search of
  LivestreamFail, X and TikTok for what just happened (`HOT_PROMPT`).
- **A picker prompt written for our niche** (Kai Cenat is in its examples): peak second, at most 20 s before and 6 s
  after it, cold open, named streamer + strong verb + specific, scoring that rewards conflict, cops, fights, rage bait
  and open doubts.
- **A veto reviewer that watches the finished clip** (contact sheets at 2 frames per second plus the words) against 7
  pass/fail checks (hook, tension, real, share, minors, honest, webcam), and re-cuts the peak and end. A clip posts
  only if every check passes. Their note: the picker once gave an 8 to a 49 s argument over a shared Photoshop screen.
- Facecam detection (webcam stacked above gameplay), YouTube upload through the official API, a keep/skip dashboard.

Others in round 2:
- **SliceQ** (MIT): two stages. Cheap text screening cuts hours to dozens of windows, then a multimodal model
  (Qwen-Omni) *watches and listens to the actual video* of each window. Lesson for us: our judge should get each
  candidate's low-res video and audio, not just the words.
- **BiliLiveCut** (MIT, Bilibili VTuber slicing): a hotspot detector fusing danmaku, audio, speech and trends; and
  **threshold learning**: every human approve/reject is stored, and the cut-off becomes the 15th percentile of approved
  scores. Lesson: learn from Franklin's keep/skip, later from real views.
- **HotClip** (AGPL, so read only, never copy): chat log fused with loudness, gifts and superchats weighted; a
  four-dimension review per cut.
- **bilive** (Apache): records, slices by danmaku density, and has a VLM write the title from the video.
- auto-slice-video (danmaku density only), biliup (recording and uploading), clip-farm bots (repost the top Twitch
  clips): nothing new for finding moments.
- Papers: "A Multimodal Transformer for Live Streaming Highlight Prediction" (Kuaishou, arXiv 2407.12002) and "Aha:
  online highlight detection" (arXiv 2509.16421). Their models and data aren't released or aren't for our niche, so
  they're ideas only.

**Revised verdict:** someone has built most of our pipeline (clipit), and we should stand on it. What still nobody
does: watch the whole stream with vision, learn taste from the top clip channels, and *measure* recall against what
went viral. Those stay our edge.

## Verdict (round 1)

Nobody open-source does what we're doing, and nobody measures it. Every project falls in one of two groups:

1. **Podcast / talking-head clippers**: transcript → LLM picks moments → face crop → karaoke captions. Strong at
   *making* the Short, blind to IRL streams (they only read words, so a slap, a celebrity walking in, or a stunt is
   invisible). Examples: ClippyMe, Hooky, OpenSource Clipping, AI-Youtube-Shorts-Generator, ClipsAI, FunClip.
2. **Gaming-stream highlighters**: chat-spike or loudness thresholds, sometimes game-HUD vision. Simple, and tuned to
   kills and clutches, not to the moments that win on Kick_Clippers. Examples: elowcraft-script, HighlightMiner,
   VoXCluTcH, LXGIC Clipper (mostly marketing; RMS z-score plus a keyword list), Auto-clipper.

**None tests recall against what really went viral, none learns taste from reference channels, and none targets
IRL/celebrity/drama moments.** That remains our edge. But for **making** the Short, ClippyMe and Hooky are far ahead of
anything we have, and both are MIT: port, don't rebuild.

## What to take, by part of the engine

| Our part | Take from | What exactly | Licence |
|---|---|---|---|
| AI judge prompt | ClippyMe `pipeline/analysis/gemini_request.py` | A worth-cutting gate (unexpected turn / strong emotion / relatable / useful) applied before scoring; 5 axes × 20 (hook, emotional payoff, quotability, self-contained, density); "the reaction beat is part of the clip, end after it lands"; never name who speaks unless the name is said; titles: exaggerate the framing, never invent the event; two triggers per title; leave the loop open | MIT |
| Judge method | Hooky `core/highlights.py` | Candidates per chunk → **one global ranking pass** (the model orders all candidates against each other, more reliable than separate 0–10 scores) → a visual check of frames per candidate | MIT |
| Clip boundaries | Hooky `snap_clip_boundaries`, ClippyMe hard rules | Snap start to the first word of a sentence and end to the last word, using word timestamps (search ±6 s for pauses) | MIT |
| Signal fusion | HighlightMiner `scoring.py` | Bonus when two or more independent signals fire together | (read only) |
| Vertical framing | ClippyMe `pipeline/reframe/` (part ported from kamilstanuch/Autocrop-vertical) | MediaPipe face + mouth-opening ratio to pick who's talking + YOLOv8n person fallback; scene detection; AutoFlip-style per-scene lock and two-pass smoothing; letterbox when two people can't fit | MIT |
| Tight cuts | ClippyMe `editing/smartcut.py` + auto-editor | Drop fillers and gaps from word timestamps, then an auto-editor loudness pass | MIT / auto-editor Unlicense |
| Captions | ClippyMe `editing/subtitles.py`; captacity | Word-by-word karaoke ASS through libass; strips `{}` so transcript text can't inject styling | MIT |
| Hook overlay | ClippyMe `editing/hook_overlay.py`; OpenSource Clipping teaser hook | 3–8-word overlay in the first seconds | MIT |
| Freshness | ClippyMe `monitoring/live_monitor.py` | Watch Kick/Twitch channels, capture the live stream in segments with streamlink, clip while the stream is still on | MIT |
| Twitch chat | TwitchDownloaderCLI (lay295; used by elowcraft-script, the format HighlightMiner reads) | VOD chat to JSON. Needs Franklin's yes: it's an external program that uses Twitch's website API | MIT |
| Extra eyes (only if Gemini falls short) | line/lighthouse | Text-query moment retrieval ("a person slaps another person") on CLIP features; trained on vlogs/news, so unproven on IRL streams | Apache-2.0 |

## Not worth taking

- ClipsAI: TextTiling topic splits (podcasts) and pyannote diarization (needs a Hugging Face token); last commit Jan 2024.
- FunClip: Chinese ASR first; LLM over the transcript only.
- Game-HUD detectors (Auto-clipper): one game each.

## Repos read

ClippyMe github.com/fralapo/clippyme · Hooky github.com/pranav256/Hooky · OpenSource Clipping
github.com/NaufalRizqullah/opensource-clipping · AI-Youtube-Shorts-Generator github.com/SamurAIGPT/AI-Youtube-Shorts-Generator ·
ClipsAI github.com/ClipsAI/clipsai · FunClip github.com/modelscope/FunClip · Lighthouse github.com/line/lighthouse ·
captacity github.com/unconv/captacity · HighlightMiner github.com/jekku0966/HighlightMiner · VoXCluTcH
github.com/Rohi56u/VoXCluTcH · elowcraft-script github.com/Mica-J7/elowcraft-script · LXGIC Clipper
github.com/lxgicstudios/lxgic-clipper · Auto-clipper github.com/bendawg2010/Auto-clipper · stream-clipper
github.com/sidgaikwad/stream-clipper · twitch-highlight-detection github.com/dscig/twitch-highlight-detection ·
github.com/artkulak/twitch-stream-highlights-detection
