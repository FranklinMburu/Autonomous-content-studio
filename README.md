# Autonomous Content Studio

Turns a topic into a finished, fact-checked, animated YouTube Short, using only free tools.

```
topic ──▶ script (Gemini, free tier) ──▶ fact check (reads the sources)
      ──▶ narration (Kokoro voice) ──▶ animation (scene library + icons) ──▶ captions
      ──▶ video.mp4 + report.md (checks + your review checklist + upload text)
```

You press **Run** on GitHub, wait a few minutes, download the folder, watch the video, and upload it yourself.
Nothing runs on your laptop and nothing costs money.

---

## One-time setup (about 10 minutes)

1. **Put this folder in a public GitHub repository.** GitHub Actions is free for public repositories
   (no payment method needed). Public means anyone can see the code and the videos it makes, which is fine:
   the videos are meant to be public anyway. **Never put your API key in a file.**
2. **Get a free Gemini API key** at <https://aistudio.google.com/apikey> (sign in with Google, "Create API key").
   No card is needed for the free tier.
3. In the repository on GitHub: **Settings → Secrets and variables → Actions**
   - **Secrets** tab → *New repository secret* → name `GEMINI_API_KEY`, paste the key.
   - (optional) **Variables** tab → `CHANNEL_LANE` = a one-line description of your channel's focus and audience,
     e.g. `Human body science for curious adults, no medical advice`.
   - (optional) **Variables** tab → `GEMINI_MODEL` = comma-separated model names to try, if the defaults stop working.
4. **Actions** tab → if asked, click *I understand my workflows, go ahead and enable them*.

## Make a video

**Actions → Make a video → Run workflow**, then fill in *one* of:
- **topic**: a question, e.g. `Why do cats knead with their paws?`
- *(nothing)*: it takes the next unused topic from `topics.txt`
- **script**: path to a hand-written script, e.g. `scripts/noise_cancelling.json` (no AI needed)

When the run finishes (about 3–6 minutes), open it and download **video-N** under *Artifacts*. Inside:

| File | What it is |
|---|---|
| `video.mp4` | the finished Short (1080×1920, ~35–55 s) |
| `contact.png` | a strip of frames, to judge the video at a glance |
| `report.md` | technical checks, fact-check results, **your quality-bar checklist**, and the title/description/tags to paste into YouTube |
| `script.json` | the script, if you want to edit and re-render it |

**Before uploading, read the fact check in `report.md`.** Anything marked ⚠️ or ❌ needs a human look.

## Make videos automatically

Edit `.github/workflows/make-video.yml` and remove the `#` from the two `schedule` lines. It will then make one
video a day from `topics.txt` (and record finished topics in `topics-done.txt`). You still review and upload.

## Write a script yourself (no AI)

Copy any file in `scripts/` and edit it. Each beat has spoken `lines` and a `scene` that shows them.
Run it with the **script** field of the workflow. The available scenes:

| Scene | Shows | Good for |
|---|---|---|
| `hero` | big icon with pulse rings, optional punch text | the hook |
| `tags` | chips popping in, optional full-screen verdict | lists, "it happens when…" |
| `link` | icon A sending pulses to icon B, optional cut | cause → effect, mechanisms |
| `number` | a big number counting up | one striking statistic |
| `compare` | two cards, A vs B | contrasts, before/after |
| `timeline` | events down a line | history, steps |
| `bars` | bar chart | comparing amounts |
| `wave` | waveform; hidden pattern, flipped copy, cancel to flat | sound, light, signals |
| `meter` | gauge filling up | "how much / how strong" |
| `bubble` | character with a speech bubble | the payoff |
| `statement` | big words lighting up as spoken | one key sentence |

`at` values are single words from that beat's narration: the visual changes when the word is spoken.
Icons are names from the free [Tabler icon set](https://tabler.io/icons) (`brain`, `dog`, `headphones`…);
unknown names are matched to the closest icon automatically. `@cat` is the hand-drawn cat.
Full parameter list: `studio/schema.py`.

## Run it on a computer instead (optional)

Needs Python 3.10+, FFmpeg, and the Cairo graphics library, plus about 1 GB of disk for the voice model and icons.
Linux/macOS: `pip install -r requirements.txt`, then `python -m studio setup` and
`python -m studio render --script scripts/cat_purr.json`. Windows is untested (Cairo is awkward to install there);
GitHub Actions is the supported way to run it.

## What's free, and how sure we are

| Part | Tool | Cost | Notes |
|---|---|---|---|
| Script + fact check | Gemini API free tier | $0 | A *limited* free tier: Google can change limits; content you send may be used to improve Google's products. If it stops working, write scripts by hand (above). |
| Voice | Kokoro-82M via kokoro-onnx | $0 | Open source (Apache-2.0 model, MIT code). Runs on CPU. |
| Icons | Tabler Icons 3.49 | $0 | MIT license. |
| Font | Poppins | $0 | SIL Open Font License (included in `assets/fonts`). |
| Video | FFmpeg, Cairo | $0 | Open source. |
| Running it | GitHub Actions | $0 | Free for public repositories on standard runners. |

## Things a human still decides

- Whether each video is good enough (the quality bar in `report.md`).
- Anything the fact check flags.
- Uploading, and ticking YouTube's "altered or synthetic content" box when it applies.
- Which lane the channel commits to (see `topics.txt`).

## Troubleshooting

- **`GEMINI_API_KEY is not set`**: add the secret (setup step 3).
- **`All Gemini models failed` with HTTP 429**: free-tier limit reached; try later, or set `GEMINI_MODEL` to a
  Flash-Lite model.
- **Script rejected after 3 attempts**: the log lists why; run again, or write that one by hand.
- **Fact check shows `unreachable`**: the cited page couldn't be read. Check the claim yourself before uploading.
