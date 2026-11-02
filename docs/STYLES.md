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
fact check (one repair round) -> whole-story logic check (who did what, order, misleading lines; one repair)
-> narration (pace corrected to 195-235 words/min) -> storyboard (up to 3 repair rounds against the checks AND the
quality gate) -> sources.md + report.md. Then the Claude polish step (POLISH.md, "Story episodes"):
`python -m studio.story review <episode>` shows numbers, gate results, every sentence and a still of every shot.

By hand: copy an episode folder, edit script.json, storyboard.json and sources.md, then `check`, `stills`, `make`.
New kinds of pictures are added to the library in `studio/story/board.py` (once, for every later video).
`python tests/test_story.py` must pass.

### What the engine gives every video (no code per video)

- Cast (`studio/story/cast.py`): 12 roles x 16 poses x 11 moods; pose/mood/position change on the spoken words.
- Places (`studio/story/settings.py`): ward, street, room, lab, deck, each in day, dusk, night or warm light.
- Auto camera (`board.make_camera`): cuts to each thing the moment it is named, otherwise moves between wide,
  medium and close about every second (benchmark: a new picture every ~1 s). Episode 001: one every 0.88 s.
- Quality gate (`board.quality`): opening shot mid-action, no empty moments, words-only shots under 10%,
  places rather than plain colour, a new picture at least every 1.5 s. The AI writer must pass it; `make` warns.

### What's next for this style

Painted backgrounds (free image model on Hugging Face), music and sound effects, a more expressive voice test.
A separate 3D line (Branch Education bar) is being planned for the "how it works" channels.

## Style 2b: Film (the default for new story videos)

Painted 3D-film shots instead of 2D drawings, built to match the benchmark (Ricks Clips, ~30 shots in 56 s, the
camera always moving). Everything runs free: GitHub Actions + the owner's Kaggle GPU (30 h/week) + free AI models.

**How a video is made (no Claude needed):**
1. *Make a story video* (Actions tab), style `film`, type a topic. Free models research, write and fact-check the
   script, narrate it, and write `film.json`: the cast (a look per person) and ~30 shots, each starting on a word.
2. Kaggle paints every shot with the cast kept consistent (one reference portrait per person; the face lock starts
   only after the pose is set), makes a depth map per shot, and turns ~2/3 of the shots into short moving clips on
   the second GPU at the same time. About 45 minutes.
3. `studio/story/film.py` cuts it together: clips, 3D camera moves on the stills, crossfades on the story's turns,
   one caption word at a time, the music bed and a few real sound effects, then publishes a Release.

**No repeats across the channel.** After each video, its cast, scenes and music go into the channel memory (the
`channel-memory` pre-release, `used.json`). The next story's shot list is checked against it: a new person may not
reuse an earlier look, at most 20% of shots may resemble earlier scenes, and the music avoids the last 4 videos' tracks.

**When the free models can't finish (the copy-paste polish).** The run opens an issue *Polish needed: <title>*
(GitHub emails you). Open it, copy the grey box, paste it into a new claude.ai chat, copy Claude's answer, and paste
it as a comment on the issue. The *Polish return* workflow checks the answer (shot list, script rules, a new fact
check if the wording changed). If something is wrong it replies with a new box; if it passes it makes the video and
posts the link, then closes the issue. Only the owner's comments are read. Locally the same kit is
`python -m studio.story.filmkit prompt|apply|verify <episode>`.

**Sound.** Music: the owner's YouTube Audio Library tracks (private Kaggle dataset `studio-audio`, never in this
public repo), picked by the story's mood, ~19 dB under the voice, steady (its level follows the word timing, so it
never pumps), a swell after the last word, then a fade. Effects: only real recordings from that dataset (`sfx.json`),
a whoosh into each crossfade, a low hit on 2-5 dramatic words, a reverse swell into the last shot; never two within
1.5 s. Final loudness -14 LUFS in two passes (one even gain).

**After a video is made (film style).**
- Passed every check → a release "Film: <title>" and an issue **Ready to upload: <title>** (download, upload to
  YouTube, close the issue). Nothing is ever published to YouTube automatically.
- Failed a final check (3+ weak shots, or length/loudness/black gaps) → a pre-release "REVIEW: <title>" and an
  issue **Review needed: <title>**. Reply **approve** (it becomes Ready to upload) or **repaint** (only the weak shots
  are redone on Kaggle, ~15-20 min, then checked again). Every release keeps `film-assets.zip` (all pictures and
  clips) so a repaint never redoes the good shots.
- Schedule: 5 videos a day (03:23, 08:23, 13:23, 20:23, 00:23 Nairobi), at most 36 a week.
