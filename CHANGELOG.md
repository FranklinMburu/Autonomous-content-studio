# Changelog

## v2.0 — Story style added (31 Oct 2026)
- New: `studio/story/` engine and `python -m studio.story make|stills|check` for 1-minute story videos (Hidden Reasons channel).
- New: `episodes/hidden_reasons/001-scurvy/` (first episode: script, scenes, sources).
- New: GitHub workflow "Make a story video" (publishes the video as a release `story-...`).
- New: `tests/test_story.py`, run on every push. `docs/STYLES.md` explains both styles.
- Unchanged: the explainer pipeline, its workflows and commands.

## v1.0-explainer (frozen branch)
- The explainer system as it ran before the story style: nightly research and drafts, Claude polish, gates,
  "Ready to upload" issues. `git checkout v1.0-explainer` to get it exactly.
