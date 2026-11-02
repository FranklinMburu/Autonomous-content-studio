"""Story style: 1-minute animated stories with a hidden scientific reason (channel: Hidden Reasons).

    python -m studio.story make episodes/hidden_reasons/001-scurvy      narrate + render -> out/<date>-<slug>/video.mp4
    python -m studio.story stills episodes/hidden_reasons/001-scurvy    a few still frames to check the look quickly
    python -m studio.story check episodes/hidden_reasons/001-scurvy     offline checks (no voice, no rendering)
    python -m studio.story write --topic "..." [--make]                 AI writes a new episode (needs the brain + keys)

An episode is data: script.json + storyboard.json + sources.md. storyboard.json uses only the shared library in
board.py (backgrounds, characters, props, animations), so a new video needs no new code.

The explainer pipeline (python -m studio ...) is separate and unchanged.
"""
