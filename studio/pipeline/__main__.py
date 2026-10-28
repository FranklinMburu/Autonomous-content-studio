"""python -m studio.pipeline <step> ...   (see run.py for the steps)"""
import argparse
import sys

from . import run


def main(argv=None):
    p = argparse.ArgumentParser(prog="studio.pipeline", description=run.__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("draft"); s.add_argument("--topic"); s.add_argument("--count", type=int)
    s = sub.add_parser("gate-pr"); s.add_argument("--pr", type=int, required=True); s.add_argument("--author")
    s.add_argument("--head-ref")
    s = sub.add_parser("produce"); s.add_argument("--limit", type=int)
    s = sub.add_parser("published"); s.add_argument("--issue", type=int, required=True)
    sub.add_parser("status")
    s = sub.add_parser("drift"); s.add_argument("--set-baseline", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "draft":
        return run.cmd_draft(a.topic, a.count)
    if a.cmd == "gate-pr":
        return run.cmd_gate_pr(a.pr, a.author, a.head_ref)
    if a.cmd == "produce":
        return run.cmd_produce(a.limit)
    if a.cmd == "published":
        return run.cmd_published(a.issue)
    if a.cmd == "status":
        return run.cmd_status()
    if a.cmd == "drift":
        from . import drift
        return drift.run(a.set_baseline)
    return 2


if __name__ == "__main__":
    sys.exit(main())
