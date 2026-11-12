"""Proof stage, the two AI layers (docs/clips/PROMPT.md §3.3):

  eyes   Gemini looks at the whole stream (one 160p frame every STEP s, in batches) and marks what is happening and
         how clip-worthy each moment is, the way a viewer watching would.
  judge  For each candidate moment (from the signals and the eyes), Gemini gets what was said and what was seen
         around it, plus what wins on the reference channels, and scores it like a top clipper (0-10) with a title.

    python lab/clips/ai_pass.py eyes  --video low.mp4 --out eyes.json [--step 4]
    python lab/clips/ai_pass.py judge --cands cands.json --words words.json --eyes eyes.json --out judged.json

Key: GEMINI_API_KEY from the environment (GitHub secret). Never printed. Free tier: requests are paced and retried.
"""
import argparse, base64, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta"
TASTE = """What wins on the best clip channels (real view counts, @Kick_Clippers and Clipatra, 13 Nov 2026):
IRL and celebrity encounters (a famous or surprising person appears or interacts); someone gets SHOCKED, EXPOSED,
HUMBLED, CAUGHT or left speechless; relationship and flirting drama; emotional beats (crying, a parent, a gift);
money and flex (expensive things, big bets, giving money away); physical surprises (a fall, a slap, a stunt, a fight);
a funny or awkward reaction anyone understands with the sound off. Titles: "The moment / No way [streamer]
[REALIZED / was SHOCKED / EXPOSED / couldn't believe] [situation]". Boring: menus, loading, quiet walking, chatting
about nothing, reading donations, gameplay without a reaction."""


def key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        sys.exit("GEMINI_API_KEY is not set")
    return k


def call(model, parts, want_json=True, tries=6):
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0.2, **({"responseMimeType": "application/json"} if want_json else {}),
                                 "mediaResolution": "MEDIA_RESOLUTION_LOW"}}
    req = urllib.request.Request(f"{API}/models/{model}:generateContent", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key()})
    for i in range(tries):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=180))
            txt = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
            return json.loads(txt) if want_json else txt
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:200]
            if e.code in (429, 500, 503):
                time.sleep(min(90, 10 * (i + 1)))
                continue
            if e.code == 400 and "mediaResolution" in msg:          # older model: no media-resolution field
                body["generationConfig"].pop("mediaResolution", None)
                req.data = json.dumps(body).encode()
                continue
            raise SystemExit(f"Gemini error {e.code}: {msg}")
        except (KeyError, IndexError, json.JSONDecodeError, TimeoutError, urllib.error.URLError):
            time.sleep(5)
    return None


def pick_model():
    d = json.load(urllib.request.urlopen(urllib.request.Request(f"{API}/models?pageSize=200", headers={"x-goog-api-key": key()}), timeout=60))
    names = [m["name"].split("/")[-1] for m in d.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
    good = [n for n in names if "flash" in n and not any(b in n for b in ("lite", "image", "tts", "live", "audio", "exp", "preview", "thinking"))]
    good = good or [n for n in names if "flash" in n] or names
    good.sort(key=lambda n: [int(x) if x.isdigit() else 0 for x in n.replace("-", ".").split(".")], reverse=True)
    print("models available:", ", ".join(names[:20]), "| using", good[0])
    return good[0]


def eyes(a):
    model = a.model or pick_model()
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-vf", f"fps=1/{a.step},scale=284:160", "-q:v", "6", str(tmp / "f%05d.jpg")], check=True)
    frames = sorted(tmp.glob("f*.jpg"))
    print(f"[eyes] {len(frames)} frames, one every {a.step} s; batches of {a.batch}")
    out = []
    for b in range(0, len(frames), a.batch):
        chunk = frames[b:b + a.batch]
        t0 = b * a.step
        parts = [{"text": f"You are watching a live stream like a top clip-channel editor. These are {len(chunk)} frames, one every "
                          f"{a.step} s, starting at {t0} s. {TASTE}\nReturn JSON: a list of the notable moments only, each "
                          '{"t": seconds from stream start, "score": 0-10 clip-worthiness from the picture alone, "what": short description}. '
                          "Most frames are not notable; return [] if nothing stands out."}]
        for i, f in enumerate(chunk):
            parts += [{"text": f"t={t0 + i * a.step}"}, {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(f.read_bytes()).decode()}}]
        r = call(model, parts) or []
        for m in r if isinstance(r, list) else r.get("moments", []):
            if isinstance(m, dict) and "t" in m:
                out.append({"t": float(m["t"]), "score": float(m.get("score", 0)), "what": str(m.get("what", ""))[:200]})
        print(f"[eyes] {min(len(frames), b + a.batch)}/{len(frames)} frames, {len(out)} notable so far", flush=True)
        time.sleep(a.pause)
    Path(a.out).write_text(json.dumps({"model": model, "step": a.step, "moments": out}, indent=0))


def judge(a):
    model = a.model or pick_model()
    cands = json.loads(Path(a.cands).read_text())
    words = json.loads(Path(a.words).read_text())["words"] if a.words and Path(a.words).exists() else []
    seen = json.loads(Path(a.eyes).read_text())["moments"] if a.eyes and Path(a.eyes).exists() else []
    out = []
    for i in range(0, len(cands), 8):
        batch = cands[i:i + 8]
        blocks = []
        for c in batch:
            t = c["t"]
            said = " ".join(w["w"] for w in words if t - 60 <= w["start"] <= t + 30)[:900]
            saw = "; ".join(f"{m['t']:.0f}s {m['what']}" for m in seen if t - 60 <= m["t"] <= t + 30)[:500]
            blocks.append(f"MOMENT t={t}\nSAID (t-60..t+30): {said or '-'}\nSEEN: {saw or '-'}")
        prompt = (f"You are the best clip-channel editor alive. {TASTE}\nFor each moment below, decide how likely a Short "
                  "cut from it reaches 250K+ views. Return JSON list of {\"t\", \"score\" 0-10, \"kind\", \"title\" in the "
                  "winning formula, \"why\" one sentence}. Be harsh: most moments are 2-5.\n\n" + "\n\n".join(blocks))
        r = call(model, [{"text": prompt}]) or []
        for m in r if isinstance(r, list) else r.get("moments", []):
            if isinstance(m, dict) and "t" in m:
                out.append({k: m.get(k) for k in ("t", "score", "kind", "title", "why")})
        print(f"[judge] {min(len(cands), i + 8)}/{len(cands)}", flush=True)
        time.sleep(a.pause)
    Path(a.out).write_text(json.dumps({"model": model, "judged": out}, indent=1))


def show(a):
    for m in sorted(json.loads(Path(a.eyes).read_text())["moments"], key=lambda m: -m["score"])[:30]:
        t = int(m["t"])
        print(f"  {t//3600}:{t%3600//60:02d}:{t%60:02d} [{m['score']:.0f}] {m['what']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("eyes"); e.add_argument("--video", required=True); e.add_argument("--out", required=True)
    e.add_argument("--step", type=int, default=4); e.add_argument("--batch", type=int, default=60)
    j = sub.add_parser("judge"); j.add_argument("--cands", required=True); j.add_argument("--words"); j.add_argument("--eyes")
    j.add_argument("--out", required=True)
    sh = sub.add_parser("show"); sh.add_argument("--eyes", required=True)
    for x in (e, j):
        x.add_argument("--model"); x.add_argument("--pause", type=float, default=6)
    a = ap.parse_args()
    {"eyes": eyes, "judge": judge, "show": show}[a.cmd](a)


if __name__ == "__main__":
    main()
