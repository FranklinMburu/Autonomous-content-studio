"""Video backends: one standard job ("make this shot"), one small plug per tool, a router with a fallback order.

The pipeline only calls `make_shot(Shot(...), out_dir)`. It never knows which tool made the clip. If a tool dies,
changes or runs out of its free allowance, the router moves on; if every tool is down, our own renderer still makes
a clip from the shot's picture. Paid tools exist only as switched-off slots (Franklin's $0 rule): turning one on is a
one-line change in config.json plus a GitHub secret, never a rebuild. Design: docs/VIDEO_BACKENDS.md.
"""
from .job import Shot, Result  # noqa: F401
from .router import make_shot, Router  # noqa: F401
