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
# Repaint mode (a "repaint" reply on a Review issue): REPAINT_FROM=<release tag> REPAINT_SHOTS="a,b,c" keeps every
# other shot of that release and redoes only these on Kaggle (pictures checked again, clips remade).
mkdir -p film_assets
if [ -n "${REPAINT_FROM:-}" ]; then
  gh release download "$REPAINT_FROM" -p film-assets.zip -D prev --clobber
  unzip -qo prev/film-assets.zip -d film_assets
  python - "$EP/film.json" lab/kaggle/film_episode/film.json "$REPAINT_SHOTS" <<'PY'
import json, sys
f = json.load(open(sys.argv[1])); f["only"] = [x for x in sys.argv[3].split(",") if x]
json.dump(f, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
PY
  rm -f film_assets/checks.json
else
  cp "$EP/film.json" lab/kaggle/film_episode/film.json
fi
echo "::group::Pictures and clips on the free Kaggle GPU"
export KAGGLE_SLUG_SUFFIX="-$(printf %s "$NAME-${GITHUB_RUN_ID:-0}" | md5sum | cut -c1-6)"   # one private Kaggle script per run
python lab/kaggle/run.py film_episode --wait-min 150
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
(cd film_assets && zip -qr "$OLDPWD/film-assets.zip" .)   # every picture, depth map and clip: a later repaint keeps the good ones
QC_PROBLEMS=$(python -c "import json; print('; '.join(json.load(open('film_out/qc.json'))['problems']))")
QC_NOTES=$(python -c "import json; print('; '.join(json.load(open('film_out/qc.json'))['notes']))")
{ echo "Film-style story video: $TITLE"; echo; echo "Checks: $QC_NOTES"; [ -n "$QC_PROBLEMS" ] && echo "NEEDS REVIEW: $QC_PROBLEMS"
  echo; echo "Episode: $EP"; echo; echo "Sources:"; cat "$EP/sources.md" 2>/dev/null || true; } > notes.md
URL="https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG"
FAILED=$(python -c "import json; print(','.join(json.load(open('film_assets/checks.json')).get('failed', [])))" 2>/dev/null || true)
if [ -z "$QC_PROBLEMS" ]; then
  gh release create "$TAG" "$NAME.mp4" film_out/contact.png episode-files.zip film-assets.zip --title "Film: $TITLE" --notes-file notes.md
  tools/ready_issue.sh "$TAG" "$TITLE" "$EP"
else   # guardrail: a video that failed a final check is never published as finished; the owner gets an issue
  gh release create "$TAG" "$NAME.mp4" film_out/contact.png episode-files.zip film-assets.zip --prerelease --title "REVIEW: $TITLE" --notes-file notes.md
  gh label create review --color D93F0B --description "A video failed a final check" 2>/dev/null || true
  gh issue create --label review --title "Review needed: $TITLE" --body "<!-- review: tag=$TAG episode=$EP failed=$FAILED -->
The video was made but a final check failed, so it is held as a pre-release (not finished).

**Problems:** $QC_PROBLEMS

**Watch it:** $URL (the video and a contact sheet of every second)

**Reply with one word as a comment:**
- **approve**: it is good enough. The release becomes finished and a *Ready to upload* issue opens.
- **repaint**: redo only the weak shots (${FAILED:-none listed}) on Kaggle (about 15-20 min), check again, and post the new video here.

(Only your comments are read.)"
fi
echo "RELEASE_TAG=$TAG" >> "${GITHUB_ENV:-/dev/null}"
echo "VIDEO_URL=https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG" >> "${GITHUB_ENV:-/dev/null}"

# remember this episode's cast, places and music so later stories look and sound different
python -m studio.story.filmkit remember "$EP" used.json --music "$(cat film_out/music.txt 2>/dev/null)"
gh release view channel-memory >/dev/null 2>&1 || gh release create channel-memory --prerelease --title "Channel memory" \
  --notes "What earlier videos used (cast, places, music), so new stories don't repeat them. Updated by the pipeline."
gh release upload channel-memory used.json --clobber
