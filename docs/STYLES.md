# Two ways to make videos

YouTube Creator Studio now makes two kinds of video. They share the voice (Kokoro), the fonts and this repo.
Adding the second one changed nothing in the first.

| | Style 1: Explainer | Style 2: Story (new) |
| --- | --- | --- |
| Channel | Body Science | Hidden Reasons |
| What it is | Facts explained with icons and scene templates | A 1-minute story with a character, then the hidden science |
| How it's made | Fully automatic pipeline: research, AI drafts, polish, gates | Script, scenes and sources written per episode (by Claude today) |
| Command | `python -m studio ...` | `python -m studio.story ...` |
| GitHub button | **Make a video** / the pipeline workflows | **Make a story video** |
| Where the work lives | `pipeline/`, `scripts/` | `episodes/<channel>/<NNN-slug>/` |
| Code | `studio/` | `studio/story/` |
| Finished videos | GitHub Releases + "Ready to upload" issues | GitHub Releases named `story-...` |

## Style 1: Explainer (unchanged)

Everything in `docs/PIPELINE.md` still applies: the nightly pipeline, polish, gates and "Ready to upload" issues.
The exact version that was running before the story style was added is saved as the branch **`v1.0-explainer`** (never changed after today):

```
git checkout v1.0-explainer      # the old system, exactly as it was
git checkout main                # back to the current one
```

## Style 2: Story

Each video is one folder:

```
episodes/hidden_reasons/001-scurvy/
  script.json   the narration (beats and lines), voice, speed and pace
  scenes.py     the pictures: one function per shot and the SHOTS list
  sources.md    a source for every claim (required)
```

Shots are tied to words, not seconds: `L.wt("Six", 2)` means "the second time 'six' is spoken", so a change of
voice or speed keeps pictures and words in sync.

### Make one on GitHub (no setup)

**Actions → Make a story video → Run workflow**, type the episode folder, press **Run**. After about 5 minutes
the video is on the **Releases** page (`story-001-scurvy-runN`), with the sources in the release notes.

### Make one on your computer

One-time setup (Windows, PowerShell, inside your clone of this repo):

```
git pull
pip install -r requirements.txt
winget install Gyan.FFmpeg          (only if `ffmpeg -version` doesn't work)
python -m studio setup              (downloads the voice model once, about 330 MB, into cache/)
```

Then:

```
python -m studio.story check episodes\hidden_reasons\001-scurvy     (5 seconds, no rendering)
python -m studio.story make  episodes\hidden_reasons\001-scurvy     (about 3 minutes)
```

The video lands in `out\<date>-story-...\video.mp4` with `contact.png` (one frame every 2 seconds).
`out/` and `cache/` are never committed. To share code changes: `git add`, `git commit`, `git push` on a branch,
then open a pull request; the tests run automatically.

Note: the story style needs only `pycairo` for drawing (Windows wheels exist). The explainer's icon renderer
(`cairosvg`) is the part that is awkward on Windows; it isn't used here.

### Add a new episode

1. Copy an episode folder, number it (`002-...`).
2. Write `script.json` in the Hidden Reasons format: a strange hook in the first 3 seconds, doubt, escalation,
   "You see..." with an everyday comparison, the real science, a one-line twist. 145-235 words.
3. Write `sources.md`: one row per claim.
4. Write `scenes.py` using the helpers in `studio/story/lib.py` (characters, props, captions).
5. `python -m studio.story check ...`, then `stills ...` to look at frames, then `make ...`.
6. `python tests/test_story.py` must pass.

### What's next for this style

Today each episode's scenes are written by hand (by Claude). The next step is a scene library big enough for an
AI to assemble scenes from a script on its own, checked by the same kind of gates as the explainer.
