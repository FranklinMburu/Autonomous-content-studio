"""Kick VOD chat, with no key: Kick's own website chat-history API, read the way clipit does it (MIT,
third_party/clipit/kick.py, which this imports unchanged).

    python lab/clips/kick_chat.py --slug n3on --start 2026-10-31T23:10:00Z --duration 6120 --out chat.json

Writes [{"time_in_seconds", "message", "weight"}]: big chats are sampled (a page is ~25 messages), and "weight" keeps
the rate right where a page stood for more seconds than it covers (recall.py multiplies by it).
"""
import argparse, datetime, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "third_party"))
from clipit import kick  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True); ap.add_argument("--start", required=True, help="VOD start time, ISO")
    ap.add_argument("--duration", type=float, required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cid = int(kick.get(f"https://kick.com/api/v2/channels/{kick.check_slug(a.slug)}")["id"])
    start = datetime.datetime.fromisoformat(a.start.replace("Z", "+00:00")).timestamp()
    t0 = time.time()
    msgs = kick.fetch_chat(cid, start, a.duration)
    out = [{"time_in_seconds": m[0], "message": m[1], "weight": m[2] if len(m) > 2 else 1} for m in msgs]
    Path(a.out).write_text(json.dumps(out))
    print(f"kick chat: {len(out)} messages over {a.duration/3600:.1f} h in {time.time()-t0:.0f} s")


if __name__ == "__main__":
    main()
