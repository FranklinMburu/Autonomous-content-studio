# Clipping engine: decisions so far (read this before any clipping work)

Updated 13 Nov 2026, 01:15 Nairobi. Kept in the project docs and in the repo (`docs/clips/DECISIONS.md`, branch
`clips-engine`, PR #100).

## Franklin's intent (confirmed by him on 13 Nov)

A clipping engine inside the existing Creator Studio pipeline, isolated like Tech Education.
- It takes 3–6 hour streams of the big creators (Kai Cenat, IShowSpeed, N3on, Adin Ross, DDG, Blueface, Deshae Frost
  and whoever is trending).
- It finds the moments that go viral, **better than a human clipper:** it catches what fans clipped *and* what nobody
  clipped.
- It makes Shorts that stand beside the reference channels.
- It runs automatically, at $0, and judges itself honestly. Franklin judges by watching real clips.

## Decisions, in order

1. **v1 failed** (12 Nov). The agent clipped fake cartoon streams it built itself, because the prompt boxed it in with
   rules and no real footage. Verdict: "trash". **Never again:** real streams only for anything shown to Franklin.
2. **The bar** (13 Nov), Franklin's choice:
   - **@Kick_Clippers** (`UCIPD8q8n3Vy7Qfz59RTc1Jg`): 3,392 Shorts, median 21K views, top 10% ≥ 248K, best 32M.
   - **Clipatra** (`UCxlQSBBswmNP-wFDkcFrDBw`): 4,046 Shorts, best 7.8M.
   - The winning moments are IRL and celebrity encounters, shock, exposure, relationship drama, emotion and money.
   - The title formula is "The moment / No way [streamer] [REALIZED / SHOCKED / EXPOSED] … 😳💔 #streamer".
   - The aim is their top-10% range.
3. **Build first, guard at publish time** (13 Nov). Few rules up front. Rights and campaign rules become a "before you
   post" note. The only fixed lines:
   - $0;
   - never Franklin's passwords or cookies;
   - nothing posted or merged without his yes;
   - no fake footage shown as a clip.
4. **No whole-stream downloads; no laptop storage** (13 Nov). Tested on GitHub's machine:
   - **Twitch works:**
     - VOD lists and sizes (a long VOD is 116 GB at 1080p60, 33 GB at 720p, 3 GB audio only);
     - only a section (60 s at 1080p60 = 65 MB in 3 s);
     - audio only (about 70 MB per hour);
     - viewer clips with views.
   - **Kick works:** API, VOD list, top clips with views, clip files (one earlier 403, so retry).
   - **YouTube is blocked** for video ("not a bot" check). Lists and views work.
   - Chat replay with `chat-downloader` didn't work yet.

   So the engine finds moments from cheap signals, then downloads only the winning sections in high quality. Franklin's
   laptop runner is used only for YouTube sources, and only for small sections, deleted after.
5. **The intelligence must not miss moments** (13 Nov). Viewer clips, audio and chat alone would miss silent visual
   moments and anything nobody clipped. So the engine **watches the whole stream at low quality** (about 1–2 GB per
   6 h) with a vision AI (Gemini at about 70 tokens per frame at low resolution, or an open model on Kaggle's free GPU),
   **hears everything** (transcript and audio cues), **reads the crowd** (chat and viewer clips), and an AI then judges
   every candidate like a clipper.
6. **Prove before building** (13 Nov). The engine is only built further once a recall test shows a high chance (about
   9/10) that it finds the moments that really went viral, plus good ones nobody clipped. Recall test:
   - real streams;
   - ground truth from the fans' top clips (exact timestamps) and the reference channels' hits;
   - each signal alone, then all together;
   - measure how many real hits are found in the top candidates, and inspect the new finds.

## Open items

- Does Gemini's free daily allowance cover a whole stream? If not: Kaggle's open vision model, or fewer frames.
- A working chat-replay tool for Twitch and Kick.
- Campaign status for the first streamers. The IShowSpeed × Expedia campaign covers his 6 Nov 2026 YouTube stream from
  2:56:29 (needs the laptop route).
