#!/usr/bin/env bash
# Copy files from this workspace into main and push them (retrying if main moved meanwhile).
#   tools/commit_to_main.sh "<message>" <path> [<path> ...]      (paths relative to the repo root)
# Needs GH_TOKEN with contents: write. Used to keep drafts and polish tickets safe in the repo.
set -uo pipefail
msg="$1"; shift
dir=$(mktemp -d)
git clone -q --depth 1 --branch main "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$dir" || exit 1
for p in "$@"; do mkdir -p "$dir/$(dirname "$p")"; rm -rf "$dir/$p"; cp -r "$p" "$dir/$p"; done
cd "$dir" || exit 1
git config user.name "content-studio-bot"; git config user.email "actions@users.noreply.github.com"
git add -A -- "$@"
git diff --cached --quiet && { echo "nothing new to save"; exit 0; }
git commit -qm "$msg"
for i in 1 2 3 4 5; do git push -q origin main && { echo "saved to main: $*"; exit 0; }; sleep $((i * 3)); git pull -q --rebase origin main; done
echo "could not push to main"; exit 1
