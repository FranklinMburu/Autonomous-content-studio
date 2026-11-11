# Changelog

## v3.0 — Motion engine for Tech Education (11 Nov 2026)
- New: `studio/motion/` (data-driven 3D motion engine: plan contract, seeded style, locked voice, synthesised music and
  effects, headless-Chromium renderer) and `python -m studio.motion check|stills|make|write`.
- New: channel profile `channels/te/channel.json` and the approved episode `episodes/tech_education/001-what-is-an-api/`.
- New: workflow "Make a motion video (Tech Education)" (manual, own concurrency group) and `tests/test_motion.py`
  (separate CI job with a real render smoke test).
- New: `docs/MOTION_ENGINE.md`: the reference-to-pipeline method, the v1 -> v3 history and the architecture.
- New: workflow "Motion review (approve or remake)" for issues labelled `review-motion`; AI-written episodes are saved to main.
- Engine: automatic coverage cuts (a new angle about every second), light wipes between sets, brighter panels.
- Unchanged: the explainer and story styles, their workflows, schedule and Kaggle use.

## v2.0 — Story style added (31 Oct 2026)
- New: `studio/story/` engine and `python -m studio.story make|stills|check` for 1-minute story videos (Hidden Reasons channel).
- New: `episodes/hidden_reasons/001-scurvy/` (first episode: script, scenes, sources).
- New: GitHub workflow "Make a story video" (publishes the video as a release `story-...`).
- New: `tests/test_story.py`, run on every push. `docs/STYLES.md` explains both styles.
- Unchanged: the explainer pipeline, its workflows and commands.

## v1.0-explainer (frozen branch)
- The explainer system as it ran before the story style: nightly research and drafts, Claude polish, gates,
  "Ready to upload" issues. `git checkout v1.0-explainer` to get it exactly.
