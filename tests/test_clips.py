"""Clipping engine checks. Offline: no keys, no network, no models. Needs ffmpeg (and tesseract for the caption
OCR check; that one check is skipped where tesseract is missing).
Run: python tests/test_clips.py
"""
import hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.clips import edit as E, gates as G, moments as MO, signals as SG, sources as S  # noqa: E402
from studio.clips.__main__ import bar, find, make_one  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


SENTENCES = ["okay so this is a normal part of the stream", "nothing much happening here at all",
             "we just keep playing and talking", "alright chat here we go one more time",
             "forty minutes on this level and I never beat it", "no no no are you serious?",
             "I pressed it! I pressed the button!", "okay that was painful", "let's keep going chat",
             "another quiet moment in the stream"]


def fixture(d, dur=120, burst=60):
    """A tiny 'stream': grey test picture, quiet tone, one loud burst at `burst` s with reaction words and a chat spike,
    plus a decoy chat spike of bot commands at 25 s that must NOT be picked."""
    d.mkdir(parents=True, exist_ok=True)
    vol = f"if(between(t,{burst},{burst + 4}),0.8,0.08)"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=640x360:rate=30:duration={dur}",
                    "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={dur}",
                    "-af", f"volume='{vol}':eval=frame", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac",
                    "-shortest", str(d / "stream.mp4")], check=True)
    words, t = [], 2.0
    i = 0
    while t < dur - 6:
        s = SENTENCES[i % len(SENTENCES)]
        if abs(t - (burst - 7)) < 4:      # put the setup + reaction right before/at the burst
            s = SENTENCES[4]
        if burst - 0.5 <= t < burst + 3:
            s = SENTENCES[5] if t < burst + 1.5 else SENTENCES[6]
        for w in s.split():
            words.append({"w": w, "start": round(t, 3), "end": round(t + 0.32, 3)})
            t += 0.36
        t += 1.4 if abs(t - burst) > 10 else 0.3
        i += 1
    (d / "words.json").write_text(json.dumps({"words": words}))
    chat = [{"content_offset_seconds": k * 0.7, "commenter": {"display_name": "a"}, "message": {"body": "hi chat"}}
            for k in range(int(dur / 0.7))]
    chat += [{"content_offset_seconds": burst + 4 + k * 0.1, "commenter": {"display_name": "b"}, "message": {"body": "KEKW"}}
             for k in range(80)]
    chat += [{"content_offset_seconds": 25 + k * 0.1, "commenter": {"display_name": "c"}, "message": {"body": "!enter"}}
             for k in range(120)]
    (d / "chat.json").write_text(json.dumps({"comments": chat}))
    (d / "rights.json").write_text(json.dumps({"source": "own", "owner": "test", "title": "test stream"}))
    return d


def test_rights_are_required():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "stream.mp4").write_bytes(b"x")
        try:
            S.load(d)
            check(False, "a stream without rights.json is refused")
        except S.RightsError:
            check(True, "a stream without rights.json is refused")
        (d / "rights.json").write_text(json.dumps({"source": "found it on youtube"}))
        try:
            S.load(d)
            check(False, "an unknown rights kind is refused")
        except S.RightsError:
            check(True, "an unknown rights kind is refused")
        (d / "rights.json").write_text(json.dumps({"source": "program", "program": "X clipping"}))
        try:
            S.load(d)
            check(False, "a clipping program without its terms link is refused")
        except S.RightsError:
            check(True, "a clipping program without its terms link is refused")


def test_chat_formats():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "chat.json").write_text(json.dumps([{"time_in_seconds": 3.5, "author": {"name": "x"}, "message": "W"}]))
        check(S.chat(d) == [(3.5, "x", "W")], "chat-downloader format read")
        (d / "chat.json").write_text(json.dumps({"messages": [{"offset_s": 2, "sender": "k", "content": "L"}]}))
        check(S.chat(d) == [(2.0, "k", "L")], "Kick export format read")
        (d / "chat.json").write_text(json.dumps({"comments": [{"content_offset_seconds": 1, "commenter": {"display_name": "t"},
                                                               "message": {"body": "KEKW"}}]}))
        check(S.chat(d) == [(1.0, "t", "KEKW")], "TwitchDownloader format read")


def test_chat_lag_is_estimated():
    import numpy as np
    a = np.zeros(600)
    c = np.ones(600)
    for p in (100, 250, 400, 520):
        a[p] = 12
        c[p + 7: p + 20] = np.linspace(8, 20, 13)   # chat keeps growing after the onset: the onset is what counts
    lag, corr = SG.estimate_lag(c, a)
    check(lag in (7, 8, 9), f"chat lag found from the data (got {lag} s, corr {corr:.2f})")


def test_utterances_and_window():
    words = [{"w": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate("one two three. four five six".split())]
    u = MO.utterances(words)
    check(len(u) == 2 and u[1]["text"] == "four five six", "utterances split at sentence ends")


def test_edit_never_cuts_the_payoff():
    words = [{"w": "a", "start": 0.0, "end": 0.3}, {"w": "b", "start": 3.0, "end": 3.3},
             {"w": "c", "start": 10.0, "end": 10.3}, {"w": "d", "start": 12.5, "end": 12.8}]
    segs = E.edit_list(words, 0.0, 13.0, 11.0, {"max_pause_s": 0.6})
    check(len(segs) == 2 and segs[0][1] < 3.0 and any(s[0] <= 10.0 and s[1] >= 12.8 for s in segs),
          f"dead air is cut, but never the 3 s around the payoff {segs}")


def test_end_to_end():
    b = bar()
    with tempfile.TemporaryDirectory() as tmp:
        st = fixture(Path(tmp) / "s")
        out = Path(tmp) / "out"
        dirs, src = find(st, 1, out, log=lambda *a: None, ask=None)
        cands = json.loads((out / "candidates.json").read_text())["candidates"]
        top = cands[0]
        check(55 <= top["peak"] <= 68, f"the moment finder picks the real burst, not the bot spam (peak {top['peak']} s)")
        check(not any(20 <= c["peak"] <= 32 and c["score"] >= top["score"] for c in cands), "the !enter spam does not win")
        clip = json.loads((dirs[0] / "clip.json").read_text())
        check(clip["captions"] and all(1 <= len(c["words"]) <= b["captions"]["max_words"] for c in clip["captions"]),
              "captions are chunks of 1-3 words")
        ok, nbad = G.captions_in_sync(clip, src["words"])
        check(ok, f"every caption word is where it is spoken ({nbad} out of sync)")
        check(clip["hook"]["text"] != "" and all(w in " ".join(x["w"] for x in src["words"]).upper().replace(",", "")
                                                 for w in re.sub(r"\.\.\.$", "", clip["hook"]["text"]).replace("40", "FORTY").split()),
              f"the heuristic hook only uses words from the transcript ({clip['hook']['text']!r})")
        check(clip["source"]["rights"]["source"] == "own" and "Our own stream" in clip["description"], "rights travel into the description")
        rep = make_one(dirs[0], src["words"], b, log=lambda *a: None)
        m = rep["measures"]
        check(1080 == m["w"] and 1920 == m["h"], "output is 1080x1920")
        check(abs(m["lufs"] - (-14)) <= 1.0, f"loudness normalised to -14 LUFS (got {m['lufs']})")
        check(rep["gates"]["rights_recorded"] and rep["gates"]["subject_in_frame"] and rep["gates"]["text_outside_ui_zones"],
              "rights, framing and UI-zone gates pass")
        # determinism: same clip.json -> the same frames
        from studio.clips.render import render
        v2 = render(clip, dirs[0] / "again.mp4", log=lambda *a: None)

        def frames_hash(v):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(v), "-vf", "fps=2,scale=108:192", "-f", "rawvideo", "-"],
                                 capture_output=True).stdout
            return hashlib.md5(raw).hexdigest()
        check(frames_hash(dirs[0] / "video.mp4") == frames_hash(v2), "same clip.json -> the same frames")


def test_isolated():
    hits = [str(p.relative_to(ROOT)) for p in list((ROOT / "studio").rglob("*.py")) + list((ROOT / ".github" / "workflows").glob("*.yml"))
            if ("studio.clips" in p.read_text(encoding="utf-8", errors="ignore") or "studio/clips" in p.read_text(encoding="utf-8", errors="ignore"))]
    hits = [h for h in hits if not h.startswith("studio/clips/") and h not in (".github/workflows/make-clips.yml", ".github/workflows/pipeline-tests.yml")]
    check(hits == [], f"nothing outside the clipping engine uses it {hits}")
    for p in (ROOT / "studio" / "clips").glob("*.py"):
        txt = p.read_text(encoding="utf-8")
        bad = [m for m in ("studio.story", "from ..story", "studio.motion", "from ..motion", "studio.pipeline", "from ..pipeline")
               if m in txt]
        check(not bad, f"{p.name} imports no other engine {bad}")
    wf = (ROOT / ".github" / "workflows" / "make-clips.yml").read_text()
    check("group: make-clips" in wf and "workflow_dispatch" in wf and "schedule:" not in wf,
          "own workflow: manual only, own concurrency group")
    check("review-clips" in wf and "--prerelease" in wf, "a failed gate becomes a REVIEW pre-release + a review-clips issue")


def test_dataset_offline():
    """The winners/baseline collector with a fake API: labels within each channel, statistics with CIs."""
    from datetime import datetime, timezone, timedelta
    from studio.clips import dataset as D
    now = datetime(2026, 11, 12, tzinfo=timezone.utc)
    vids = [{"id": f"v{i}", "snippet": {"title": ("NO WAY he did this \U0001F631 #shorts" if i % 2 else "stream clip part " + str(i)),
                                        "publishedAt": (now - timedelta(days=10 + i)).isoformat().replace("+00:00", "Z")},
             "statistics": {"viewCount": str((100000 if i % 2 else 5000) + i)}, "contentDetails": {"duration": "PT35S"}}
            for i in range(20)]

    def get(path, **p):
        if path == "channels":
            return {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}, "snippet": {"title": "ch"}, "statistics": {}}]}
        if path == "playlistItems":
            return {"items": [{"contentDetails": {"videoId": v["id"], "videoPublishedAt": v["snippet"]["publishedAt"]}} for v in vids]}
        return {"items": [v for v in vids if v["id"] in p["id"].split(",")]}
    rows = D.collect(["UCx"], days=90, now=now, get=get)
    win = [r for r in rows if r["group"] == "winner"]
    check(len(rows) == 20 and len(win) == 5 and all(r["t_has_emoji"] for r in win), "collector labels the top quartile per channel")
    st = {x["feature"]: x for x in D.stats(rows)}
    check(st["t_has_emoji"]["cliffs_delta"] == 1.0 and st["t_has_emoji"]["vpd_ratio"] and st["t_has_emoji"]["vpd_ratio"] > 10,
          f"stats find the separating feature with an effect size and a CI {st['t_has_emoji']}")
    check(D.iso_seconds("PT1M5S") == 65 and D.iso_seconds("PT45S") == 45, "ISO 8601 durations read")


def test_bar_cites_evidence():
    b = bar()
    for k, v in b.items():
        if isinstance(v, dict) and k not in ("rubric",):
            check("_why" in v, f"bar.json '{k}' says why (cites the research)")
    check(abs(sum(v["weight"] for v in b["rubric"].values()) - 1.0) < 1e-6, "rubric weights sum to 1")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print(f"\n{len(FAILS)} failure(s)" if FAILS else "\nall clips checks pass")
    sys.exit(1 if FAILS else 0)
