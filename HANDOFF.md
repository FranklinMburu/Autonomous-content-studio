# HANDOFF — Autonomous Content Studio

Written by the build session (Claude, claude.ai chat with tools), 2026-10-26 ~04:20 Nairobi time (UTC+3),
for a second Claude session doing strategy and research. That session can read Notion, this repo and the
user's laptop folder, but not the build chat. This file captures what the build chat knows.

**Conventions:** `[VERIFIED]` = run/observed or checked against a primary source in this session.
`[REPORTED]` = from a secondary source or the user, not independently checked. `[UNVERIFIED]` = believed,
not checked. `[INFERRED]` = my interpretation of the user, not their words. Quotes in "double quotes" are the
user's own words (lightly cleaned of voice-dictation errors).

---

## 0. Read this first (60-second summary)

- **Goal:** a channel people actually watch, with a credible path to earnings, produced by a genuinely
  \$0-operating-cost system with minimal manual work. The system is the means; audience and earnings are the point.
- **Built:** a working pipeline (topic → Gemini script → fact check → Kokoro voice → Cairo animation from an
  11-scene library → captions → FFmpeg → QC report) running on **GitHub Actions in this public repo**.
  One GitHub run succeeded (hand-written script). Five videos made in total; the user called the first one "perfect".
- **Not yet proven:** that Gemini's free tier writes scripts as good as Claude's (the `GEMINI_API_KEY` secret
  had not been added when this was written). Nothing has been published. No niche chosen.
- **Biggest strategic finding:** Shorts pay very little and YouTube Partner Program thresholds rise on
  2027-02-01. Realistic money path = Shorts to test/grow + longer animated explainers in a winning lane (not built).
- **Biggest risk:** polishing the machine instead of putting videos in front of viewers.
- **How to work with this user:** read the Collaboration Charter and the Drift Guard in Notion first; verify
  claims; be candid; don't overbuild; never spend money or publish without explicit approval.

---

## 1. The user's intent

### In their own terms
- Build a "genuinely \$0-operating-cost, practical content-production system" that can "eventually automate as much
  of the workflow as is useful: discovering opportunities, researching, scripting, producing narration and
  visuals, assembling videos, quality-checking, publishing when authorized, and learning from performance"
  (Collaboration Charter, written by the user).
- "The aim is not to build impressive technology for its own sake. The aim is to find the right opportunity and
  create something people actually want to use or watch, with a credible path toward eventual earnings and
  minimal unnecessary manual work." (Charter)
- The Problem Statement (Notion) frames it as: a person starting a video-based online business wants "the
  strongest realistic chance of eventually earning income" while starting at \$0.
- In chat the user repeatedly asked for an **end-to-end** system ("build for me this system end to end, all of it",
  "from first to the very end until it's working… then iterate"), and wanted Claude to be **creative** and not
  bound to earlier tool choices ("I'm not sticking to Oracle or prompt creator… I'm very open. I just want your
  creativity, and as long as you get such kind of video, good").

### Long-term vision `[INFERRED from charter + chat]`
- Full workflow automation eventually: opportunity discovery → research → script → narration → visuals →
  assembly → QC → publishing (when authorized) → analytics feedback loop.
- A channel (or channels) that earns money; the user wants to know if it can "blow up" (asked 2026-10-26).
- Minimal ongoing human time. **Unanswered:** whether the end state is fully hands-off or a short daily
  approval routine (asked twice by Claude; no answer yet).
- **Unanswered:** Shorts only, or Shorts as a testing ground for long-form.

### What the user is NOT after
- Impressive tech for its own sake; dashboards; multi-agent frameworks; "so it scales later" infrastructure.
- Studio-grade 3D (after viewing comparison channels the user said Claude would "sophisticate this before we
  even build what we want to build" — i.e. keep the simple style).

---

## 2. The \$0 rule

### Definition (from the Charter, the user's own document)
- "Do not rely on paid APIs, subscriptions, billing-enabled services, rented compute, expiring promotional
  credits, or an assumed future upgrade as the foundation of the ongoing workflow."
- Verify "current free-tier quotas, restrictions, commercial-use rights, licensing, persistence, regional
  availability, and hidden costs from primary sources where possible."
- "Clearly distinguish truly sustainable no-cost options from temporary trials, limited free tiers, and options
  that require a payment method. If the full vision cannot be achieved reliably at \$0, state the limitation
  honestly and propose the best viable compromise without silently weakening the constraint."

### Allowed (as applied in this session)
- Open-source software and models: Kokoro (Apache-2.0 weights) via kokoro-onnx (MIT), FFmpeg, Cairo/pycairo,
  CairoSVG, Tabler Icons (MIT), Poppins font (OFL).
- **GitHub Actions in a public repo** on standard runners `[VERIFIED: GitHub Docs — free for public repos;
  without a payment method usage is blocked, not billed, after quota]`.
- **Gemini API free tier** — treated as a *limited free tier*, not a permanent guarantee, with a no-AI fallback
  (hand-written scripts). `[VERIFIED: Google pricing page says free of charge; free-tier content "used to improve
  our products"; Kenya is a supported region]`. `[REPORTED: no card needed — third-party guide, not official]`.
- Claude Pro: the user pays for it already and accepts it as an existing cost for building/research, but said
  they "cannot be able to afford the pro plan after we depleted" → **it must not be a foundation of the ongoing
  pipeline.** Claude stated that Pro has no programmatic API access `[UNVERIFIED against Anthropic docs]`.

### Forbidden
- Card on file / card for "identity verification" as a foundation (this is why **Oracle Always Free was rejected**).
- Trials, expiring/promo credits (AWS/Azure/GCP credits; the earlier research doc wrongly allowed "promo credits").
- Paid APIs (OpenAI etc.), paid stock media, rented GPUs (Paperspace etc.).
- Anything that silently assumes a future paid upgrade.
- Spending money, enabling billing, or making payment commitments **without explicit approval** (Charter §7).

### Reasoning `[INFERRED]`
The user is starting with no budget and wants a business that can exist before it earns. Temporary or card-based
"free" options create surprise bills or collapse when credits expire, so they can't be the foundation.

---

## 3. Premium / later

**Important: the user has NOT stated any specific paid tools, upgrade targets, or budget trigger in this session.**
Do not invent a premium wish-list on their behalf. What exists:

- **User's statement:** they can't keep paying for Claude Pro long-term → the system must run without Claude.
- **Charter:** an "assumed future upgrade" may not be the foundation — implies paid options are acceptable only
  as optional add-ons once justified, never as dependencies.
- **Deferred by design (Claude's proposals, approved implicitly by the build plan; not user-requested premium items):**
  - Automated YouTube upload (YouTube Data API + OAuth). `[UNVERIFIED: uploads from unaudited API projects may be
    forced private]`. Publishing always needs explicit approval.
  - Topic discovery from trends (YouTube Data API, pytrends, Reddit) — deliberately not built before a lane is chosen.
  - Analytics feedback loop (YouTube Analytics API).
  - Long-form (3–8 min) animated explainers in the winning lane — Claude's recommended earnings path.
  - Stock-footage path (Pexels/Pixabay) — untested (blocked in Claude's sandbox); not needed so far.
  - Local LLM on the laptop — blocked by disk space.
  - Daily schedule in the workflow (present but commented out).
- **Quality upgrades Claude would suggest if resources ever allowed `[Claude's opinion, not user's]`:** a more
  distinctive visual identity/mascot, better voice options, two-pass loudness normalisation. None requested.
- **Trigger for moving to paid anything:** not defined by the user. Ask them. Charter requires explicit approval.

---

## 4. Preferences and working style

### How they want to work with Claude (Charter + chat)
- Think independently, challenge assumptions, don't just agree; recommend the best path even if it rejects
  an earlier idea.
- Inspect existing pages/research/assets before proposing a direction. **The user caught Claude proposing a plan
  before reading every Notion page** ("Did you read all my documents? Like all of them?") — read everything first.
- Treat earlier research as leads, not truth; verify claims from primary sources.
- Prefer the smallest complete, testable solution. Move from research to working results.
- Never claim something works without evidence. Label facts vs assumptions vs unverified.
- Be autonomous on reversible details; ask only when it changes direction.
- Get explicit approval before: spending, billing, card commitments, sharing credentials, destructive file
  operations, public publishing, account creation, irreversible external changes.
- Keep records aligned: decisions → Research & Approach; architecture → Architecture & Logic; verified
  implementation → Implementation & Runbook.
- Decision hierarchy: (1) real goal/audience value, (2) \$0, (3) evidence over hype, (4) simple/maintainable,
  (5) quality/originality/compliance, (6) automate more only when it clearly helps.

### Communication style observed `[INFERRED from chat]`
- The user dictates by voice; messages contain transcription errors ("cloud idea" = Claude idea,
  "mummy diagram" = Mermaid diagram, "intern" = intent, "chatter"/"chart" = charter/chat). Read charitably.
- Wants **detailed** outputs when asking for understanding/documentation ("be very detailed", "most detailed way
  possible") but **plain English** and "do not overcomplicate it".
- Got frustrated when Claude kept asking questions or explaining instead of deciding after full context was given
  ("I've said so much and I've not understood…", "you've not settled on something"). Once context is complete,
  be decisive and present one clear plan to approve.
- Likes to see real examples (asked for clickable links to comparable channels before deciding).
- Wants Claude to keep itself from drifting → created the **Drift Guard** page at the user's request.

### Likes / rejections
- **Liked:** the first proof video ("this is so good", "perfect. I mean, perfect"). Flat 2D animated style,
  dark backgrounds, warm accent colours, word-highlighted captions, hand-drawn cat.
- **Rejected:** chasing studio-grade/3D polish (Zack D. Films, Kurzgesagt level) at this stage.
- **Not yet given verdicts on:** the 4 system-made test videos; the GitHub-made `video-1`; voice naturalness;
  caption sync. Claude cannot hear audio — the user's ears are the only check on the voice.
- Voice used: Kokoro `af_heart` (US English female). Alternatives sampled but not chosen by the user:
  `am_michael`, `bm_george`, `af_bella`.

### Privacy rules
- **Git commits must use the GitHub no-reply email:** `184284364+FranklinMburu@users.noreply.github.com`,
  author/committer name `FranklinMburu` (user's request; their real email must not be exposed).
- Gemini key only as a GitHub secret; never in files or chat.
- Repo is public; artifacts are downloadable by logged-in GitHub users.

### Charter / Drift Guard essentials
- The five drift checks (Drift Guard): (1) infrastructure before one good video, (2) "the pipeline ran" ≠ good
  video, (3) research tables treated as facts, (4) niche from trend data alone, (5) quiet reliance on trials/
  credits/cards. Show how a recommendation passes them.
- Video quality bar (draft, user hasn't formally confirmed): hook in ~2 s; every claim sourced; visual matches
  the words at that moment; natural pacing; synced captions; real payoff; not mass-produced; you'd watch to the end.

---

## 5. Decisions and why (chronological, 2026-10-25 → 26)

| # | Decision | Alternatives considered | Why |
|---|---|---|---|
| 1 | Discussion first; no building until user approves | Run the "delegation prompt" in the old research doc | User explicitly said the prompt was a planning artifact, not an instruction |
| 2 | Create Notion **Drift Guard** page | Rely on chat memory (Claude memory is off) | User asked for a self-check anchor across sessions |
| 3 | Build the **first proof video in Claude's own sandbox** | Kaggle/Colab notebooks; laptop | \$0 extra (Pro), no new accounts, no laptop disk use; sandbox could run Kokoro + FFmpeg on CPU |
| 4 | Kokoro via **kokoro-onnx**, model files from GitHub releases | Hugging Face (blocked), edge-tts (blocked + unofficial endpoint), Coqui, gTTS | Open licence, CPU-fast (~2× real time), reachable |
| 5 | **Original drawn animation (Cairo)** instead of stock footage | Pexels/Pixabay (blocked in sandbox), Stable Diffusion (GPU), Automated Video Generator | Forced by network blocks, then judged better: original, distinctive, safer under YouTube's 2025 "inauthentic content" rules |
| 6 | Cut the "purring heals bones" claim | Include it (popular online) | Only a 2001 conference abstract; not established |
| 7 | Keep the flat 2D style; don't chase 3D/studio quality | Emulate Zack D. Films / Kurzgesagt | User's verdict after reviewing comparison channels |
| 8 | Scripts by **Gemini free tier**, with hand-written fallback | Claude (not \$0 long-term, no API), local LLM (disk), OpenAI (paid) | Free, Kenya supported, no card (reported); fallback keeps the system alive if Gemini changes |
| 9 | Runner = **GitHub Actions, public repo** | Oracle Always Free (card), Kaggle/Colab (sessions, manual), laptop (9 GB C:, 2 GB D:; Windows + Cairo untested), Cloudflare Workers (no Python/FFmpeg) | Free for public repos, no card, persistent workflow, enough CPU |
| 10 | **Reusable 11-scene library** driven by script JSON | Hand-code visuals per video (as in proof) | New topic = new script, not new code; required for automation |
| 11 | **Tabler Icons 3.49.0** for pictures | Hand-drawn per topic; other icon sets | MIT, 5,184 outline + 1,054 filled, tag search for fuzzy matching |
| 12 | Switch to Kokoro **`model-files-v1.1`** | v1.0 files | v1.1 ONNX exposes a `duration` output → real per-word timings |
| 13 | Flexible word↔phoneme-group alignment | Exact count match / proportional estimate | Speech merges words ("of a"); alignment made every word model-timed |
| 14 | Per-video palette (5) × background (3) from title hash | Single fixed look | Avoid templated look (YouTube inauthentic-content risk) |
| 15 | Gemini model fallback chain `gemini-3.8-flash → 3.6-flash → 3.5-flash-lite → flash-latest`, override via `GEMINI_MODEL` | Single alias | Google models page lists these; a June 2026 forum thread reported Flash/flash-latest failing on free keys while Flash-Lite worked |
| 16 | Fact check reads the actual source pages; unreadable/bot-check pages flagged "unreachable", never passed | Trust Gemini's own sources | Gemini can invent or misread sources |
| 17 | **Manual review + upload** | Automated upload | Publishing is public/irreversible → explicit approval; YouTube API audit issue unverified |
| 18 | Three test lanes: A body, B animals, C everyday tech | Pick one niche now | No audience evidence yet; decide on retention data |
| 19 | Earnings path = Shorts to test + long-form later | Shorts only | Shorts RPM ~\$0.02–1.48 vs Education long-form ~\$15–18 (vendor data); 2027 YPP thresholds |
| 20 | Code in `C:\Users\DELL\Autonomous-content-studio` + public repo `FranklinMburu/Autonomous-content-studio` | — | User created both |
| 21 | Commits with no-reply email | Real email | User request |
| 22 | Add a "System Map — How It Works" Notion page as "Start here" | Only technical pages | User wanted a plain-English map with diagrams |

---

## 6. Current state

### Works today `[VERIFIED]`
- **Repo** `FranklinMburu/Autonomous-content-studio` (public), branch `main`. Commits: `350f1b5` (v1 system),
  `56237c6` (report on run page), plus this HANDOFF commit.
- **Workflow** `.github/workflows/make-video.yml` ("Make a video"): manual dispatch with inputs `topic`, `lane`,
  `script`; schedule commented out; caches `cache/`; uploads `out/` as artifact `video-N` (14 days); writes
  `report.md` to the run summary page; commits `topics-done.txt` in next-topic mode.
- **GitHub run 40224527308** (script `scripts/noise_cancelling.json`): success, 2 min 13 s; artifact `video-1`
  4.9 MB. Claude could NOT download/view it (GitHub serves artifacts from an Azure blob host blocked in Claude's
  sandbox) → **the user must confirm it plays correctly.**
- **Voice:** Kokoro v1.1, `af_heart`, speed 1.0, model word timings on every word of all 4 test videos.
- **Scenes:** 11 types — hero, tags, link, number, compare, timeline, bars, wave (incl. overlay/anti/flat),
  meter, bubble, statement. 9 seen in real videos; **timeline and bars never rendered in a video yet.**
- **Videos produced:**

| Video | Where | Length | Loudness | Script by |
|---|---|---|---|---|
| Proof v1/v2 "Why do cats purr" (hand-coded, pre-system) | Claude sandbox only — **lost when sandbox ends** | 45.3 / 44.9 s | −14.9 LUFS (v2) | Claude |
| Your cat's purr is hiding a cry | laptop `out/` | 48.5 s | −15.7 | Claude |
| Wrinkly fingers aren't soggy skin | laptop `out/` | 42.6 s | −15.8 | Claude |
| What your dog's head tilt means | laptop `out/` | 35.8 s | −15.5 | Claude |
| Silence made of sound (noise-cancelling) | laptop `out/` + GitHub `video-1` | 33.1 s | −15.6 | Claude |

### Half-built / unverified live
- Gemini script writing (`studio/writer.py`, `studio/gemini.py`) — tested only with a stand-in; Gemini is blocked
  from Claude's sandbox.
- Live fact check (`studio/factcheck.py`) — page extraction verified; Gemini judgement untested live.
- Next-topic mode on GitHub (commit of `topics-done.txt`) — logic tested locally with stand-ins only.
- Windows local runs — untested (Cairo/CairoSVG on Windows likely painful; CairoSVG needs a cairo DLL).

### Fragile / known issues
- **Loudness lands at −15.5 to −15.8 LUFS**, not −14 (single-pass `loudnorm`). Passes the ±2 LU check; a two-pass
  normalisation would fix it.
- Prompt vs validator mismatch: prompt asks 95–130 words and hook ≤14 words; validator accepts 85–140 and ≤16.
  (The headphones script is 87 words — passes.) Intentional slack, but note it.
- Gemini model names may change or be unavailable on free tier; set `GEMINI_MODEL` repo variable to override.
- Some news sites serve bot-check pages → their claims will show "unreachable" in reports (by design).
- Each video's palette/background is a hash of the title: two videos can share a look by chance
  (cat and wrinkly fingers both got "plum").
- `make` always returns success even if the report says NEEDS ATTENTION (status lives in the report).
- Laptop folder is **not a git clone** and is **one commit behind** (no run-summary step in `setup/make-video.yml`;
  no HANDOFF.md). Treat the GitHub repo as the source of truth.
- `.github/` cannot be written on the laptop via Claude's remote-device tool (protected path); laptop shell
  (`device_bash`) was unavailable ("Workspace unavailable") in this session.
- Synthetic voice: some viewers dislike AI narration `[opinion]`.

---

## 7. Open items

### User's side
- [ ] Create Gemini API key (aistudio.google.com/apikey) and add repo secret `GEMINI_API_KEY`.
- [ ] Download and watch GitHub artifact `video-1`; confirm it matches the local headphones video.
- [ ] Watch the 4 test videos **with sound**; give verdicts on voice, caption sync, and which lane appeals.
- [ ] Answer: fully hands-off vs short daily review? Shorts only vs Shorts + long-form?
- [ ] Decide when to start uploading (explicit approval needed for public publishing; also needs a YouTube channel).
- [ ] Optional: set repo variable `CHANNEL_LANE` once a lane is chosen.

### Claude's side (build session) / next planned steps
1. First live Gemini run (`topic` input) → compare against the Claude-scripted videos; fix the prompt/validator
   based on what Gemini actually produces.
2. Render a script that uses `timeline` and `bars` to verify them visually.
3. Consider two-pass loudness; consider guaranteeing distinct palettes across consecutive videos.
4. After uploads begin: ~10 videos per lane, then choose the lane with the best average view duration and
   returning viewers (proposed decision rule).
5. Later: long-form rendering in the winning lane; then analytics loop; automated upload only with approval.

### Open questions for the strategy session (good research targets)
- Which lane has the best mix of demand, low competition for *animated, sourced* explainers, and long-form potential?
- What distinctive angle/character could make the channel recognisable (e.g. the cat as recurring host for
  "why animals do that")? Claude's view: breakout depends more on a unique angle than on the machine.
- Realistic growth expectations for a new faceless Shorts channel; how to reach YPP before/after 2027-02-01.
- YouTube's current synthetic-media disclosure rules for animated explainers with AI voice.
- Whether Claude Pro includes API access (claimed no; unverified).
- Whether YouTube API uploads from unaudited projects are forced private (only matters for automated upload).

---

## 8. NOT written down anywhere else (most important)

These live only in the build chat until now:

1. **The user's original research documents** (pasted into chat from another tool; not in Notion or repo).
   Five pasted docs, two identical. Summary:
   - *Doc A — "Refined cloud-first plan"*: Kaggle/Colab for compute; Oracle/GitHub Actions/Cloudflare for
     orchestration; first test = one 30–60 s "Why do cats purr?" Short; provider comparison table; a ready-made
     "delegation prompt for Claude" (NOT to be executed — user said so); success criteria allowed "promo credits"
     (conflicts with charter); laptop "~18.8 GB free"; malformed sample FFmpeg command; mislabelled
     "vertical 9:16: e.g. 1920x1080".
   - *Doc B — "Cloud compute options"*: Colab, Kaggle (20 GB, ~30 GPU h/week claimed), Oracle Always Free (needs card),
     GitHub Actions, Codespaces (120 core-hours/15 GB claimed), Cloudflare Workers (100k req/day), HF Spaces;
     mapping of stages to providers; hybrid Oracle + Kaggle + Actions proposal.
   - *Doc C (twice) — "Local laptop toolchain"*: per-stage tool tables; Automated Video Generator (MIT) as core;
     pytrends, PRAW, Ollama/GPT4All, Kokoro/edge-tts/Coqui/gTTS, Pexels/Pixabay, FFmpeg/MoviePy/Remotion, YouTube APIs.
   - *Doc D — "Three toolchains"*: Self-hosted (AVG, recommended), Lightweight Python (edge-tts + Pixabay + FFmpeg),
     Visual-rich (Stable Diffusion); hardware footprints.
   - These docs contradicted each other (Kokoro licence MIT vs Apache; Pixabay key; Pexels attribution; quotas).
   Only the *evolution* is summarised in Notion Research & Approach; the details above are not stored elsewhere.
2. **Disk numbers:** user said on 2026-10-25 "I have like 9 GB in my C drive and maybe like 2 GB in my D drive" and
   "I might have deleted some few stuffs". Earlier reports: ~7 GB/~2 GB; research doc: ~18.8 GB. Never measured.
   (Problem Statement has the 9/2 figure; the "deleted stuff" remark isn't recorded.)
3. **Claude Pro affordability:** "of course I cannot be able to afford the pro plan after we depleted" — the reason
   the system must not depend on Claude. Recorded in Notion only in paraphrase.
4. **The user's confusion/frustration moments** and what fixed them: they wanted a decisive, settled plan once all
   context was given; they want Claude to "remain as creative as possible" within the constraints; they disliked
   being asked to re-explain. Approval came as: "build for me this system end to end, all of it."
5. **The "Claude idea"**: the user mentioned a "cloud idea" early on; Claude interpreted it as "Claude idea"
   (Claude writing scripts / running the pipeline). The user later confirmed Claude's role: use Pro now for
   building, but not as an ongoing dependency. The original "Claude idea" was never separately pasted.
6. **The user's reaction to comparison channels:** they found MinuteEarth/TED-Ed/Kurzgesagt/Zack D. Films
   "really high definition or really animated" and told Claude not to over-sophisticate.
7. **"Will it blow up?" (2026-10-26):** Claude's candid answer — as-is, probably not; strengths are accuracy,
   originality, zero cost (staying power), solid Shorts craft; weaknesses are plain visuals, crowded topics, no
   personality/character, synthetic voice; recommendation: upload soon, treat first 20–30 videos as experiments,
   judge by retention, look for a distinctive angle (e.g. cat as recurring host). Claude's progress estimate:
   ~75% toward a working \$0 video machine, ~15% toward an earning channel.
8. **Comparison links shared** (for the strategy session to reuse): MinuteEarth Short "Adult Cats Only Meow At
   Humans" https://www.youtube.com/shorts/-b14o6luDjo ; MinuteMinis https://www.youtube.com/@minuteminis ;
   TED-Ed https://www.youtube.com/@TEDEd ; Kurzgesagt https://www.youtube.com/@kurzgesagt/videos ;
   Zack D. Films https://www.youtube.com/@zackdfilms/shorts (reported 26M+ subs, ~65B views mid-2026 per
   iVideoNow, unverified); 100SekundenPhysik, Drawcumentaries, Branch Education, ExtinctZoo; several
   "why do cats purr" competitors (e.g. https://www.youtube.com/watch?v=boZOQD1olOI).
9. **Retention advice source caveat:** OpusClip's "15–30 s Shorts retain best; captions +15–25%" has no cited data
   and is vendor marketing. Our videos are 33–48 s.
10. **Facts researched for test scripts** (sources): cat purr — Univ. Vienna press release (Herbst et al.,
    Current Biology 2023), National Geographic on McComb et al. 2009 (~380 Hz cry; 10 cats, 50 listeners);
    wrinkly fingers — Newcastle 2013 (12% faster wet marbles), MDC Berlin 2014 (40 volunteers, no advantage),
    PopSci (1936 Pickering & Lewis nerve-damage observation); dog head tilt — ELTE 2021 (40 dogs: 33 typical,
    7 gifted word learners; same side over 24 months); noise-cancelling — SoundGuys (phase inversion; better on
    steady sounds). Wikipedia "Active_noise_control" was cited but **not fetched/verified**.
11. **Claude's sandbox environment facts** (will not persist): 2 CPU, 7 GB RAM, no GPU; reachable: PyPI, npm,
    GitHub releases, raw.githubusercontent.com; blocked: Hugging Face, Pexels, Pixabay, Microsoft speech,
    Gemini API, GitHub artifact storage, api.github.com user endpoints (repo-scoped endpoints work).
    GitHub access goes through the Claude GitHub App installed by the user on this repo.
12. **Account facts:** GitHub user `FranklinMburu` (id 184284364); the user's other repos are public (~100,
    per the Notion "GitHub ↔ Notion Project Reconciliation" page). The user already uses Gemini API keys in
    other projects (mini-agentic-ai, prototypeictalgo, a transport UI) → may already have a key.
13. **User location/timezone:** Nakuru, Kenya (UTC+3). Kenya is YPP-eligible `[VERIFIED]`.
14. **Claude memory is OFF** for this user; the claude.ai Project "Autonomous Content Studio — Zero-Cost Automation
    Lab" exists with 0 project docs. Continuity relies on Notion + this repo.
15. **A Notion PDF** is embedded on the project page but could not be read via the Notion connector (no file
    returned). Its contents are unknown to Claude.
16. The **original proof-video code** (`/home/claude/studio/render.py`, `narrate.py`, hand-coded scenes) lived only
    in Claude's sandbox; it is superseded by `studio/` in this repo and will be lost.

---

## 9. File map

### Notion (workspace of the user; project row in the "Projects" database)
| Page | URL | Purpose |
|---|---|---|
| Youtube-creator-system (project control centre) | https://app.notion.com/p/400da224599e80ff94b2c9009c5f1671 | Navigation, current checkpoint, action items; DB fields (Repository URL, Next milestone, Last verified) |
| 🗺️ System Map — How It Works | https://app.notion.com/p/404da224599e81a799d4e389a064fe04 | **Start here.** Simple + detailed Mermaid maps, each part in plain English |
| 🤝 Claude Collaboration Charter — Working Intent | https://app.notion.com/p/404da224599e812c8079f1027318c841 | The user's rules for working with Claude (authoritative) |
| 🧭 Drift Guard — Claude Self-Check | https://app.notion.com/p/404da224599e8128a5c1f83d3b532937 | Five drift checks, quality bar, state snapshot, decision log, drift log |
| 🎯 Problem Statement | https://app.notion.com/p/402da224599e8170b7faf2e6cbff3c8a | Problem, constraints, verified vs hypotheses, success criteria |
| 🔎 Research & Approach | https://app.notion.com/p/402da224599e8101abd7ca571bce989b | Research evolution, verified findings + sources, lanes, decision log |
| 🧩 Architecture & Logic | https://app.notion.com/p/402da224599e81608ca0e1381fa611c6 | Mermaid diagrams, components, script format, timing, failure paths, security |
| 🛠️ Implementation & Runbook | https://app.notion.com/p/402da224599e8141a896da7e4d553dc5 | How to run, evidence log, bugs fixed, troubleshooting |
| 📄 Pitch Document / 🗣️ Pitch Talking Points | https://app.notion.com/p/402da224599e81668f6cde4b19a7082f / https://app.notion.com/p/402da224599e81618e5af91bd30aaa7d | Verified-only pitch; no metrics yet |
| GitHub ↔ Notion Project Reconciliation | https://app.notion.com/p/400da224599e81549693fafec25cee52 | Older cross-project audit (context on the user's other repos) |
| DUPLICATE — YouTube Creator System | https://app.notion.com/p/400da224599e815baf56e431830906ce | Placeholder; ignore |

### Repo (`FranklinMburu/Autonomous-content-studio`)
| Path | Purpose |
|---|---|
| `HANDOFF.md` | This file |
| `README.md` | User-facing setup + usage guide |
| `.github/workflows/make-video.yml` | The "Make a video" workflow (Run button, cache, artifact, run summary) |
| `requirements.txt` | kokoro-onnx 0.6.1, onnxruntime, soundfile, numpy, pycairo, cairosvg |
| `topics.txt` / `topics-done.txt` | Topic queue (15 ideas across lanes A/B/C) / finished topics (created on first next-mode run) |
| `scripts/*.json` | Hand-written scripts: `cat_purr`, `wrinkly_fingers`, `dog_head_tilt`, `noise_cancelling` |
| `studio/__main__.py` | CLI: `setup`, `write`, `render`, `make`, `next` |
| `studio/paths.py` | Paths; downloads Kokoro v1.1 + Tabler 3.49.0 to `cache/`; font registration |
| `studio/gemini.py` | Gemini REST client + model fallback |
| `studio/writer.py` | Prompt, script generation, retry loop |
| `studio/schema.py` | Scene docs, validation, EXAMPLE script |
| `studio/factcheck.py` | Source fetching + claim judgement |
| `studio/voice.py` | Kokoro narration + word-timing alignment |
| `studio/icons.py` | Tabler icon lookup/rendering |
| `studio/draw.py` | Canvas constants, palettes, backgrounds, primitives, cat |
| `studio/scenes.py` | The 11 scene types |
| `studio/render.py` | Timeline, cue timing, captions, frame loop, FFmpeg encode |
| `studio/qc.py` | Technical checks, contact sheet, report.md |
| `assets/fonts/` | Poppins Bold/Medium/Regular + OFL.txt |
| `cache/`, `out/` | Not committed (gitignored): downloaded assets; run outputs |

### Laptop folder `C:\Users\DELL\Autonomous-content-studio`
- Copy of the code at commit `350f1b5` state (not a git clone), plus:
- `setup/make-video.yml` — copy of the workflow (couldn't write `.github/` remotely); **outdated** (no run-summary step).
- `out/20261025-2114-your-cat-s-purr-is-hiding-a-cry/`, `…-2116-wrinkly-fingers-aren-t-soggy-skin/`,
  `…-2118-what-your-dog-s-head-tilt-means/`, `…-2120-silence-made-of-sound/` — each with `video.mp4`,
  `contact.png`, `report.md`, `script.json`. These are the 4 test videos.
- No HANDOFF.md (lives in the repo).

### Other locations
- GitHub Actions run with the first artifact: run id 40224527308 (artifact `video-1`, expires ~14 days after
  2026-10-25).
- Claude sandbox (`/home/claude/acs`, `/home/claude/studio`) — temporary; not a source of truth.
