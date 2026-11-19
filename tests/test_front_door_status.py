"""The front-door status job may only rewrite its own box (Franklin, 19 Nov 2026: "not accidental mistakes on that page
in whatever scenario"). Run: python tests/test_front_door_status.py"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SRC = (ROOT / "tools" / "front_door_status.py").read_text()


def test_only_guarded_calls():
    assert "DELETE" not in SRC and '"/pages' not in SRC and "archived\": True" not in SRC
    raw = [m for m in re.findall(r"\bcall\(", SRC)]
    assert len(raw) == 1, "the only raw call() is inside guarded()"
    assert 'PAGE = "41dda224599e8114b120eee8ded4ca75"' in SRC and "environ.get(\"FRONT_DOOR_PAGE\"" not in SRC


def test_guard_refuses():
    import tools.front_door_status as f
    sent = []
    f.call = lambda m, p, b=None: sent.append((m, p)) or {}
    for m, p, b in [("DELETE", "/blocks/x", None), ("PATCH", "/pages/x", {"properties": {}}),
                    ("PATCH", "/blocks/x", {"paragraph": {"rich_text": []}}),
                    ("PATCH", "/blocks/x", {"callout": {"rich_text": [], "icon": {}}}),
                    ("PATCH", "/blocks/x", {"archived": True}),
                    ("GET", "/blocks/400da224599e80ff94b2c9009c5f1671/children", None),
                    ("POST", "/pages", {})]:
        try:
            f.guarded(m, p, b)
            raise AssertionError(f"allowed {m} {p}")
        except SystemExit:
            pass
    assert not sent
    f.guarded("PATCH", "/blocks/abc", {"callout": {"rich_text": []}})
    assert sent == [("PATCH", "/blocks/abc")]


if __name__ == "__main__":
    test_only_guarded_calls(); test_guard_refuses(); print("ok")
