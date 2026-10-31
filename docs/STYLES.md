# Two ways to make videos

YouTube Creator Studio now makes two kinds of video. They share the voice (Kokoro), the fonts and this repo.
Adding the second one changed nothing in the first.

| | Style 1: Explainer | Style 2: Story (new) |
| --- | --- | --- |
| Channel | Body Science | Hidden Reasons |
| What it is | Facts explained with icons and scene templates | A 1-minute story with a character, then the hidden science |
| How it's made | Fully automatic pipeline: research, AI drafts, polish, gates | AI writes script + storyboard from a topic, checked by gates; or hand-written |
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
  storyboard.json  the pictures as data: shots, backgrounds, characters, props, animations (no code)
  sources.md    a source for every claim (required)
```

A storyboard only uses the shared library in `studio/story/board.py` (backgrounds, characters, props,
animations), so a new video needs no new code. Shots are tied to words, not seconds: `"Six#2"` means "the second
time 'six' is spoken", so a change of voice or speed keeps pictures and words in sync.
Episode 001's storyboard reproduces the original hand-coded video frame for frame (mean pixel difference < 1/255).

### Make one on GitHub (no setup)

**Actions → Make a story video → Run workflow**. Either type a **topic** (the AI researches, writes, fact-checks
and storyboards a new episode, then renders it) or an existing **episode** folder. After about 5 minutes
the video is on the **Releases** page (`story-...`), with the sources in the release notes and the episode files
(`episode-files.zip`) attached. A topic takes about 30 minutes (most of it the storyboard step).

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

Automatic: `python -m studio.story write --topic "..." --make` (needs the brain and its keys; normally run on GitHub).
The writer: research (Wikipedia + OpenAlex) -> script by the free models (judge picks the best) -> claim-by-claim
fact check (one repair round) -> narration (pace corrected to 195-235 words/min) -> storyboard (up to 3 repair
rounds against the checks) -> sources.md + report.md.

By hand: copy an episode folder, edit script.json, storyboard.json and sources.md, then `check`, `stills`, `make`.
New kinds of pictures are added to the library in `studio/story/board.py` (once, for every later video).
`python tests/test_story.py` must pass.

### What's next for this style

Episode 002 was made by the AI from a topic alone and passed every check, but the library is still small, so its
pictures repeat. Next: more settings, characters and props (some generated once with free image models), a visual
check that rejects repeated or empty shots, and a second logic check on the script.
