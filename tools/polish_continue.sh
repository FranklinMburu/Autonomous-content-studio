#!/usr/bin/env bash
# Continue one film-style episode after a polish answer: check it, then either ask for fixes or make the video.
# The same path for every polisher: the owner's pasted comment, Claude, Codex or a person writing answer.json.
#   tools/polish_continue.sh <issue> <episode-dir> <draft-tag> <reply-file> [<ticket-dir>] [<who>]
# Needs: GH_TOKEN, the brain on PYTHONPATH (fact check), KAGGLE_* (video). Writes the result into the repo ticket
# (polish/film/<episode>/result.md, status in ticket.json) on main, so any agent can see what to fix next.
set -uo pipefail
ISSUE="$1"; EPISODE_DIR="$2"; DRAFT_TAG="$3"; REPLY="$4"; TICKET="${5:-}"; WHO="${6:-an answer}"
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-}/actions/runs/${GITHUB_RUN_ID:-0}"
NAME=$(basename "$EPISODE_DIR")

# safety: only well-formed paths and tags (the values come from the issue marker or ticket.json)
[[ "$EPISODE_DIR" =~ ^episodes/[a-z0-9_]+/[0-9]{3}-[a-z0-9-]+$ ]] || { echo "bad episode path: $EPISODE_DIR"; exit 1; }
[[ "$DRAFT_TAG" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "bad draft tag: $DRAFT_TAG"; exit 1; }
[[ -z "$TICKET" || "$TICKET" =~ ^polish/film/[0-9]{3}-[a-z0-9-]+$ ]] || { echo "bad ticket path: $TICKET"; exit 1; }

save_ticket() {   # save_ticket <status> <result-file> [video-url]: record the outcome in the repo (main)
  [ -n "$TICKET" ] || return 0
  local status="$1" result="$2" url="${3:-}" dir
  dir=$(mktemp -d)
  git clone -q --depth 1 --branch main "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$dir" || return 0
  local t="$dir/$TICKET"
  mkdir -p "$t"
  cp "$result" "$t/result.md"
  [ -f "$REPLY" ] && [ ! -f "$t/answer.json" ] && cp "$REPLY" "$t/answer.json"
  python - "$t/ticket.json" "$status" "$url" "$WHO" <<'PY'
import json, sys, datetime, pathlib
p = pathlib.Path(sys.argv[1]); t = json.loads(p.read_text()) if p.exists() else {}
t.update({"status": sys.argv[2], "checked": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
          "last_answer_by": sys.argv[4]})
if sys.argv[3]: t["video"] = sys.argv[3]
p.write_text(json.dumps(t, indent=1))
PY
  if [ "$status" = "done" ]; then   # finished tickets move to polish/done/ (kept forever: the polished script)
    mkdir -p "$dir/polish/done"; rm -rf "$dir/polish/done/$NAME"; git -C "$dir" mv "$TICKET" "polish/done/$NAME" 2>/dev/null || mv "$t" "$dir/polish/done/$NAME"
  fi
  (cd "$dir" && git config user.name "content-studio-bot" && git config user.email "actions@users.noreply.github.com" \
     && git add -A polish && git commit -qm "Polish ticket $NAME: $status" \
     && for i in 1 2 3 4; do git push -q origin main && break; sleep $((i * 3)); git pull -q --rebase origin main; done) || true
}

gh issue comment "$ISSUE" --body "Got ${WHO}. Checking it now ([progress]($RUN_URL))." || true

mark() {   # mark polished|polish: show on GitHub (title + label) and on the website whether the polish is done
  gh label create polished --color 0E8A16 --description "Polish accepted; the video is being made" 2>/dev/null || true
  local t; t=$(gh issue view "$ISSUE" --json title --jq .title 2>/dev/null | sed -E 's/^(Polish needed|Polished, making the video): *//')
  [ -n "$t" ] || return 0
  if [ "$1" = polished ]; then
    gh issue edit "$ISSUE" --add-label polished --remove-label polish --title "Polished, making the video: $t" >/dev/null || true
    # an episode retried by the schedule can have older "Polish needed" issues for the same title: point them here
    gh issue list --label polish --state open --json number,title --jq '.[] | "\(.number)\t\(.title)"' 2>/dev/null |
      while IFS=$'\t' read -r n title; do
        [ "$n" != "$ISSUE" ] && [ "${title#Polish needed: }" = "$t" ] || continue
        gh issue comment "$n" --body "Same video as #$ISSUE, where the polish was accepted. Closing this copy." >/dev/null || true
        gh issue close "$n" --reason "not planned" >/dev/null || true
      done
  else
    gh issue edit "$ISSUE" --add-label polish --remove-label polished --title "Polish needed: $t" >/dev/null || true
  fi
}

echo "::group::Draft files"
rm -rf draft film_assets film_out lab_out prev "$EPISODE_DIR"
gh release download "$DRAFT_TAG" -p episode-files.zip -D draft --clobber || exit 1
mkdir -p "$(dirname "$EPISODE_DIR")"; unzip -qo draft/episode-files.zip -d "$(dirname "$EPISODE_DIR")"
[ -f used.json ] || gh release download channel-memory -p used.json -D . 2>/dev/null || echo '{"episodes": []}' > used.json
ls "$EPISODE_DIR"
echo "::endgroup::"

echo "::group::Apply and check"
python -m studio.story.filmkit apply "$EPISODE_DIR" "$REPLY" > apply.txt; rc=$?
cat apply.txt
if [ $rc -ne 0 ]; then cp apply.txt problems.txt; ok=no
else
  flag=""; grep -q "SCRIPT_CHANGED=yes" apply.txt && flag="--renarrate"
  python -m studio.story.filmkit verify "$EPISODE_DIR" --memory used.json $flag | tee problems.txt
  if grep -q "^PROBLEM:" problems.txt; then ok=no; else ok=yes; fi
fi
rm -f "$EPISODE_DIR/NEEDS_POLISH.md"
# keep the latest version with the draft, so the next answer builds on it
(cd "$(dirname "$EPISODE_DIR")" && zip -qr "$OLDPWD/episode-files.zip" "$NAME")
gh release upload "$DRAFT_TAG" episode-files.zip --clobber || true
echo "::endgroup::"

if [ "$ok" = no ]; then
  python -m studio.story.filmkit issue "$EPISODE_DIR" --draft "$DRAFT_TAG" --memory used.json --problems problems.txt > again.md
  gh issue comment "$ISSUE" --body-file again.md || true
  { echo "# Needs fixes (checked $(date -u +%FT%TZ), answer by ${WHO})"; echo; echo "Fix every PROBLEM below in answer.json,"
    echo "run \`python -m studio.story.filmkit check-answer $TICKET\`, then push again."; echo; echo '```'; cat problems.txt; echo '```'; } > result.md
  # the next prompt (with these problems) replaces PROMPT.md, so the next polisher starts from it
  [ -n "$TICKET" ] && python -m studio.story.filmkit prompt "$EPISODE_DIR" --memory used.json --problems problems.txt > next_prompt.md || true
  mark polish
  save_ticket needs-fix result.md
  if [ -n "$TICKET" ] && [ -s next_prompt.md ]; then   # update PROMPT.md and files/ too
    dir=$(mktemp -d); git clone -q --depth 1 --branch main "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$dir" \
      && cp next_prompt.md "$dir/$TICKET/PROMPT.md" \
      && (cd "$dir" && git config user.name "content-studio-bot" && git config user.email "actions@users.noreply.github.com" \
          && git add -A polish && git commit -qm "Polish ticket $NAME: next prompt" && git push -q origin main) || true
  fi
  exit 2
fi

gh issue comment "$ISSUE" --body "Accepted: every check passed. Making the video now (about 45 minutes). The link will appear here." || true
mark polished
tools/film_produce.sh "$EPISODE_DIR" || { mark polish; echo "# Video failed" > result.md; echo "Log: $RUN_URL" >> result.md; save_ticket video-failed result.md; exit 1; }
url=$(grep -h '^VIDEO_URL=' "${GITHUB_ENV:-/dev/null}" 2>/dev/null | tail -1 | cut -d= -f2-)
gh issue comment "$ISSUE" --body "Your video is ready: ${url:-see Releases}" || true
gh issue close "$ISSUE" --reason completed || true
{ echo "# Done"; echo; echo "Accepted and made into a video: ${url:-see Releases}"; echo; echo "Answer by: ${WHO}"; } > result.md
save_ticket done result.md "$url"
exit 0
