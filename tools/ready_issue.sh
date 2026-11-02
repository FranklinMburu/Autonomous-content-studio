#!/usr/bin/env bash
# Opens the "Ready to upload" issue for a finished film video (Franklin downloads it, uploads it to YouTube, closes it).
#   tools/ready_issue.sh <release tag> <title> <episode dir>
set -euo pipefail
TAG="$1"; TITLE="$2"; EP="$3"
URL="https://github.com/$GITHUB_REPOSITORY/releases/tag/$TAG"
NAME=$(basename "$EP")
DESC=$(python - "$EP" <<'PY'
import json, sys
s = json.load(open(sys.argv[1] + "/script.json"))
lines = [l for b in s["beats"] for l in b["lines"]]
print(lines[0] + " " + (lines[1] if len(lines) > 1 else ""))
PY
)
gh label create ready-to-upload --color 0E8A16 --description "A finished video waiting for upload" 2>/dev/null || true
gh issue create --label ready-to-upload --title "Ready to upload: $TITLE" --body "**$TITLE** passed every check.

1. Download **$NAME.mp4** from $URL
2. Upload it to YouTube as a Short (Hidden Reasons). Suggested title: **$TITLE**
   Suggested description: $DESC (sources: see the release notes)
3. Close this issue.

Nothing is published automatically: uploading is always your call."
