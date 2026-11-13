# Long-form tech lane: research on voice and video pipelines (13 Nov 2026, research agents)

Two research agents read the repositories, model cards and licences. Full reports were delivered in the session; the
decisions they support are below. A third report (realistic presenters / lip-sync) follows separately.

## Voice (TTS) for 10–20 minute English narration

- Human preference (Artificial Analysis open-weights Speech Arena): **Kokoro v1.0 Elo 1061 already beats Chatterbox
  (1021)**. Models above Kokoro there (Fish S2 Pro 1106, Voxtral 1091, OpenAudio S1-mini 1042) are non-commercial.
- **Top 2 to blind-test against Kokoro (both Apache-2.0 code and weights):**
  1. **Qwen3-TTS 1.7B** (Alibaba): Seed-TTS English WER 1.24, similarity ~0.78; clones from 3+ s with its transcript;
     VoiceDesign makes an original voice from a description. Stable over a 16k-character story (the 0.6B was not).
     Kaggle T4: fp16, `attn_implementation="sdpa"` (no FlashAttention 2 on T4); estimate 45–70 GPU-min per 15-min
     episode (to measure).
  2. **VoxCPM2 2B** (OpenBMB): Seed-TTS English WER 1.84, similarity 75.3; ~8 GB VRAM; clone with reference + transcript.
  Alternates: Fun-CosyVoice3 0.5B (Apache; `[breath]` tags), Chatterbox (MIT; watermark on every output).
- **Recipe for human-sounding long-form:** one fixed reference voice file per channel; one paragraph (300–600 chars) per
  call, never split sentences; always condition on the original reference (never on the previous chunk); QA every
  chunk with Whisper (regenerate if WER > 3–5% or characters/second off by > 25%); insert pauses yourself (0.30 s
  sentence, 0.7 s paragraph, 1.2 s section); room tone at −60 dBFS under everything; EQ (highpass 75 Hz, de-ess, 2:1
  compression); **two-pass** loudnorm I=−15, TP=−1.5.
- **Avoid (licence or limits):** OpenAudio S1-mini, Fish S2 Pro, F5-TTS, Spark-TTS, Voxtral (non-commercial);
  MegaTTS3 (no local cloning); VibeVoice (code removed, research-only, audible disclaimer); Higgs Audio v2 (user cap +
  attribution); Dia2 (2 min per call); IndexTTS-2 (bilibili licence, PRC law, indemnity).
- Honest limit: no open model guarantees 15 minutes without artefacts (expect 5–10% of chunks regenerated); Franklin
  reading the script himself beats any TTS. On GitHub CPU only Kokoro, Pocket TTS or Chatterbox Nano are practical.

## Video pipelines and engines: what to borrow

- **No new engine needed.** Best borrow: **HyperFrames** (HeyGen, Apache-2.0, updated 13 Nov 2026): HTML/CSS rendered
  frame by frame in headless Chrome, deterministic, ~450 motion blocks: our own idea, productised.
  Blocks using GSAP (not open source) must be rewritten as plain time-based CSS/JS.
- **Ranked borrow list:**
  1. 3D-tilted panels with depth of field and camera dollies: `registry/components/camera-rig-depth-stack`,
     `focus-rack`, `blocks/rack-focus`, `camera-dolly-zoom`, `ui-3d-reveal`, `exploded-stack`.
  2. Auto-zoom and cursor for screen recordings: `registry/components/cursor-zoom-follow` (pure functions of time:
     `cursorAt(t)`, `zoomAt(t)`, `cameraAt(t)`; critically damped spring), `ui-focus-zoom`, `browser-device-stage`.
  3. Where to zoom (MIT): Clipwise `src/effects/zoom.ts` (`calculateZoomSequence`, `mergeClickZones`); OpenScreen
     `zoomSuggestionUtils.ts` (`detectZoomDwellCandidates`), `cursorFollowUtils.ts`, `zoomSpring.ts`. Capture the real
     app once with Playwright (click log), replay the camera in our engine (deterministic).
  4. Word-by-word headline text: `kinetic-center-build`, `per-word-rise`, `caption-editorial-emphasis`.
  5. Renderer hardening: HyperFrames `packages/engine/src/services/frameCapture.ts` (BeginFrame capture, readiness
     gates, skipping identical still frames, parallel workers), `motionBlur.ts`, `docs/concepts/determinism.mdx`.
  6. AI self-review of layout (MIT): Code2Video `src/agent.py` (`get_mllm_feedback`, `optimize_with_feedback`; 6×6
     anchor grid in `prompts/stage3.py`).
  7. Line breaks at grammar boundaries (Apache-2.0): VideoLingo `core/spacy_utils/split_long_by_root.py`, `_5_split_sub.py`.
  8. Retention rules (ideas only; OpenMontage is AGPL): hook done by 0:30, first payoff before 2:00, re-hook every
     3–4 min, small pattern interrupt every 20–30 s, big one every 60–90 s, chapters 2–4 min.
  9. Demos as tests (pattern only): ScreenCI re-records walkthroughs as Playwright end-to-end tests in CI.
- **Gaps nobody fills:** a $0 believable presenter; planning an episode in a reference style automatically;
  choosing which real app moment to show for a line; checking open loops pay off; voice naturalness may be the
  ceiling; 10–20 min renders on CPU need still-frame skipping and parallel shards.
- **Fastest path to a first 10-minute episode (5 days):** (1) port three new worlds (`depth_stack`, `screen_zoom`,
  `headline_build`); (2) Playwright capture of 4–6 real app screens with a click log; (3) retention lint in plan.json +
  a chapter template for the writer; (4) chapters rendered in parallel jobs, still-frame skipping, loudness gate;
  (5) Gemini layout review on sampled frames, then Franklin reviews.
