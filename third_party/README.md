# Third-party code, copied as-is (Franklin's call, 13 Nov 2026: "copy that just in case")

Kept untouched, with each project's licence, so we can port pieces into `studio/clips/` when we build Short-making.
Nothing here is imported or run yet. Read `docs/clips/OSS_RESEARCH.md` for what each part does and why we picked it.

| Folder | Source | Commit | Licence |
|---|---|---|---|
| `clippyme/` | https://github.com/fralapo/clippyme (`src/clippyme/...`) | 00b2f3a9d2b0cca8a77e7a51bc002f026d46d7ce | MIT (`clippyme/LICENSE`) |
| `clipit/` | https://github.com/EJaredMejia/clipit (`clipit/...`, README) | 6e8c2075eb2ba9ff636c3b300ca3fe9053178c5f | MIT (`clipit/LICENSE`) |
| `hooky/` | https://github.com/pranav256/Hooky (`hooky/core/...`) | 7a6fbabd5614b8c2680140257642fa7e6b93cf1f | MIT (`hooky/LICENSE`) |

What was copied:
- clippyme/reframe: vertical framing (faces, who's talking, person fallback, per-scene lock, smoothing).
- clippyme/editing: smartcut (fillers and silences), karaoke subtitles, hook overlay, compose, banner.
- clippyme/analysis: the virality prompt and its parser.
- clippyme/monitoring + integrations: live Kick/Twitch watcher (capture in segments while live).
- clippyme/media, postprocess.py: ffmpeg helpers the above use.
- hooky/highlights.py: chunked candidates, global ranking pass, sentence-boundary snapping. hooky/subtitles.py.

When porting, imports must change (`clippyme.*` → our paths) and the original licence notice stays with the code.
- clipit (the closest project to ours: Twitch + Kick streams → Shorts): audio + chat moments, Kick VOD chat history,
  viewer clips first, 'who's hot today' search, picker prompt, the vision veto reviewer, facecam layout, YouTube upload.
