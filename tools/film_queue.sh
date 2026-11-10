#!/usr/bin/env bash
# Film queue: make ONE accepted polish into a video, record the result, then start the next run if more are waiting.
# Run by .github/workflows/film-queue.yml. Every outcome is saved in the ticket (polish/film/<episode>/ticket.json),
# so a run that dies (time limit, runner lost) is picked up again by the next run. See tools/film_queue.py.
# Needs: GH_TOKEN (contents, issues, actions: write), KAGGLE_* secrets.
set -uo pipefail
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-}/actions/runs/${GITHUB_RUN_ID:-0}"
T=$(python tools/film_queue.py next)
[ -n "$T" ] || { echo "Film queue is empty."; exit 0; }
eval "$(python tools/film_queue.py env "$T")" || exit 1
TRY=$((TRIES + 1))
echo "Making $NAME (try $TRY of 3), issue #$ISSUE"
python tools/film_queue.py set "$T" making
tools/commit_to_main.sh "Film queue: making $NAME (try $TRY)" "$T" || true
gh issue comment "$ISSUE" --body "Making the video now (try $TRY of 3, about 45 minutes; [progress]($RUN_URL))." >/dev/null || true

rm -rf draft "$EPISODE" film_assets film_out lab_out prev
ok=yes
gh release download "$DRAFT" -p episode-files.zip -D draft --clobber && mkdir -p "$(dirname "$EPISODE")" \
  && unzip -qo draft/episode-files.zip -d "$(dirname "$EPISODE")" || ok=no
[ -f used.json ] || gh release download channel-memory -p used.json -D . 2>/dev/null || echo '{"episodes": []}' > used.json
# </dev/null: ffmpeg must never read this script's input
[ "$ok" = yes ] && { tools/film_produce.sh "$EPISODE" < /dev/null || ok=no; }

if [ "$ok" = yes ]; then
  url=$(grep -h '^VIDEO_URL=' "${GITHUB_ENV:-/dev/null}" 2>/dev/null | tail -1 | cut -d= -f2-)
  gh issue comment "$ISSUE" --body "Your video is ready: ${url:-see Releases}" >/dev/null || true
  gh issue close "$ISSUE" --reason completed >/dev/null || true
  { echo "# Done"; echo; echo "Made into a video: ${url:-see Releases}"; echo; echo "Film queue run: $RUN_URL"; } > "$T/result.md"
  python tools/film_queue.py set "$T" done "$url"
  mkdir -p polish/done; rm -rf "polish/done/$NAME"; mv "$T" "polish/done/$NAME"   # finished tickets are kept forever
  tools/commit_to_main.sh "Film queue: $NAME done" "$T" "polish/done/$NAME" || true
else
  if [ "$TRY" -ge 3 ]; then
    status=attention
    msg="The video failed 3 times, so the queue stopped trying. Log: $RUN_URL . The polish is safe; a person needs to look."
    gh label create pipeline-alert --color B60205 --description "A video run failed" 2>/dev/null || true
    gh issue edit "$ISSUE" --add-label pipeline-alert >/dev/null || true
  else
    status=video-failed
    msg="The video failed this time (try $TRY of 3; log: $RUN_URL). The queue will try again automatically in about 20 minutes."
  fi
  gh issue comment "$ISSUE" --body "$msg" >/dev/null || true
  { echo "# Video failed (try $TRY of 3)"; echo; echo "$msg"; } > "$T/result.md"
  python tools/film_queue.py set "$T" "$status"
  tools/commit_to_main.sh "Film queue: $NAME $status (try $TRY)" "$T" || true
fi

# more waiting? start the next run now (retries of failed videos are picked up by the hourly timer)
git fetch -q origin main && git checkout -q origin/main -- polish 2>/dev/null || true
if [ -n "$(python tools/film_queue.py next)" ]; then
  gh workflow run film-queue.yml --ref main && echo "Started the next film-queue run."
fi
# a failed video that will be retried is handled, not a crash: the run only fails when the queue gave up (3 tries)
[ "$ok" = yes ] || [ "${status:-}" != attention ]
