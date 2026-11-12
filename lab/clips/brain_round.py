"""Lab: run a round with the brain doing the ranking/hooks/titles, where the brain runs on another machine.

The sandbox cannot reach the free model APIs; Franklin's linked computer can (it has the brain). So:
    python lab/clips/brain_round.py prompt <stream dir> <out dir>       -> <out>/rank_prompt.txt  (send it to the brain)
    (on the brain's machine: ask(prompt, tier="critical", json_out=True) -> rank_answer.json {"model":..,"data":..})
    python lab/clips/brain_round.py make <stream dir> <out dir> <rank_answer.json>
The answer is replayed exactly; nothing else changes. On GitHub Actions the engine calls the brain directly.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.clips.__main__ import bar, find, make_one  # noqa: E402


class _Stop(Exception):
    pass


def main(cmd, stream, out, answer=None):
    out = Path(out)
    if cmd == "prompt":
        box = {}

        def grab(prompt, **k):
            box["p"] = prompt
            raise _Stop("prompt captured")
        find(stream, 3, out, log=lambda *a: None, ask=grab)
        (out / "rank_prompt.txt").write_text(box["p"], encoding="utf-8")
        print(out / "rank_prompt.txt")
        return
    a = json.loads(Path(answer).read_text(encoding="utf-8"))

    class R:
        data, ref = a["data"], a["model"]
    dirs, src = find(stream, 3, out, ask=lambda *x, **k: R)
    for d in dirs:
        make_one(d, src["words"], bar())


if __name__ == "__main__":
    main(*sys.argv[1:])
