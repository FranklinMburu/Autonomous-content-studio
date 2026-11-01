#!/usr/bin/env bash
# Film style, production: episode folder (script.json + film.json + sources) -> finished video as a GitHub Release.
#   tools/film_produce.sh <episode-dir>
# Needs (GitHub secrets): KAGGLE_USERNAME, KAGGLE_API_TOKEN. Optional private Kaggle dataset <user>/studio-audio
# holding the owner's music and sound effects (never in this public repo); without it the video has narration only.
# Writes: film_out/ (the video folder), RELEASE_TAG and VIDEO_URL into $GITHUB_ENV, and updates the channel memory.
set -euo pipefail
EP="$1"
NAME=$(basename "$EP")
CHANNEL_DIR=$(dirname "$EP")
echo "::group::Pictures and clips on the free Kaggle GPU"
cp "$EP/film.json" lab/kaggle/film_episode/film.json
export KAGGLE_SLUG_SUFFIX="-$(printf %s "$NAME-${GITHUB_RUN_ID:-0}" | md5sum | cut -c1-6)"   # one private Kaggle script per run
python lab/kaggle/run.py film_episode --wait-min 150
mkdir -p film_assets
find lab_out/film_episode -type f \( -name 'shot_*.png' -o -name 'depth_*.png' -o -name 'clip_*.mp4' -o -name 'ref_*.png' -o -name 'log.txt' -o -name 'checks.json' \) -exec cp {} film_assets/ \;
cat film_assets/log.txt || true
echo "::endgroup::"

echo "::group::Music and effects (private)"
if kaggle datasets download -d "$KAGGLE_USERNAME/studio-audio" -p music --unzip -q 2>/dev/null; then
  export STORY_MUSIC_DIR="$PWD/music"; echo "music files: $(ls music | wc -l)"
else
  echo "No private dataset $KAGGLE_USERNAME/studio-audio yet: narration only."
fi
echo "::endgroup::"

echo "::group::Assemble the video"
gh release download channel-memory -p used.json -D . 2>/dev/null || echo '{"episodes": []}' > used.json
python -m studio.story.film make "$EP" --assets film_assets --out film_out --memory used.json
echo "::endgroup::"

TITLE=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['title'])" "$EP/script.json")
TAG="film-$NAME-run${GITHUB_RUN_NUMBER:-0}"
cp film_out/video.mp4 "$NAME.mp4"
cp film_assets/checks.json film_out/ 2>/dev/null || true
(cd "$CHANNEL_DIR" && zip -qr "$OLDPWD/episode-files.zip" "$NAME")
QC_PROBLEMS=$(python -c "import json; print('; '.join(json.load(open('film_out/qc.json'))['problems']))")
QC_NOTES=$(python -c "import json; print('; '.join(json.load(open('film_out/qc.json'))['notes']))")
{ echo "Film-style story video: $TITLE"; echo; echo "Checks: $QC_NOTES"; [ -n "$QC_PROBLEMS" ] && echo "NEEDS REVIEW: $QC_PROBLEMS"
  echo; echo "Episode: $EP"; echo; echo "Sources:"; cat "$EP/sources.md" 2>/dev/null || true; } > notes.md
if [ -z "$QC_PROBLEMS" ]; then
  gh release create "$TAG" "$NAME.mp4" film_out/contact.png episode-files.zip --title "Film: $TITLE" --notes-file notes.md
else   # guardrail: a video that failed a final check is never published as finished; the owner gets an issue
  gh release create "$TAG" "$NAME.mp4" film_out/contact.png episode-files.zip --prerelease --title "REVIEW: $TITLE" --notes-file notes.md
  gh label create review --color D93F0B --description "A video failed a final check" 2>/dev/null || true
  gh issue create --label review --title "Review needed: $TITLE" --body "The video was made but failed a final check, so it is held as a pre-release (not finished).

Problems: $QC_PROBLEMS

Video and contact sheet: https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG

To retry: Actions -> Make a story video -> episode = release:$TAG"
fi
echo "RELEASE_TAG=$TAG" >> "${GITHUB_ENV:-/dev/null}"
echo "VIDEO_URL=https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG" >> "${GITHUB_ENV:-/dev/null}"

# remember this episode's cast, places and music so later stories look and sound different
python -m studio.story.filmkit remember "$EP" used.json --music "$(cat film_out/music.txt 2>/dev/null)"
gh release view channel-memory >/dev/null 2>&1 || gh release create channel-memory --prerelease --title "Channel memory" \
  --notes "What earlier videos used (cast, places, music), so new stories don't repeat them. Updated by the pipeline."
gh release upload channel-memory used.json --clobber
