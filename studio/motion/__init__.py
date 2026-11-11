"""Motion engine: the Tech Education (TE) style. Faceless explainers made of real-looking software in a moving 3D
world: a laptop, app windows, a server, a diagram that grows, word-by-word captions, a seeded camera, music and
sound effects made in code. Proven in the lab on 11 Nov 2026 (v1 -> v3, see docs/MOTION_ENGINE.md).

Separate from the story/film engine on purpose: nothing in studio/story or the Hidden Reasons workflows imports it,
and it imports nothing from them except the shared voice model (studio/voice.py) and the brain doorway.

    python -m studio.motion check  episodes/tech_education/001-what-is-an-api      # offline: script + plan rules
    python -m studio.motion stills episodes/tech_education/001-what-is-an-api 3 12  # a few frames to look at
    python -m studio.motion make   episodes/tech_education/001-what-is-an-api      # the full video
    python -m studio.motion write  --topic "What is a database?"                    # AI writes script + plan

An episode is data only: script.json (lines), plan.json (one scene per line, from plan.TYPES), sources.md.
Same files + same seed -> same video (no clock, no randomness at render time).
"""
