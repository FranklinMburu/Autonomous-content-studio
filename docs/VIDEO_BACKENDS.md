# Video backends: one job, many tools, never stuck (19 Nov 2026)

**Why.** Generative video tools (Wan, LTX, Kling, Veo, Higgsfield…) come and go, change prices and run out of free
allowance. The pipeline must not depend on any one of them. Code: `studio/video_backends/`. Tests:
`tests/test_video_backends.py`.

## How it works
1. **One standard job:** `Shot(prompt, image=None, seconds, width, height, fps, camera, negative, seed)`. The pipeline
   only calls `make_shot(shot, out_dir)` and never knows which tool made the clip.
2. **One plug per tool** (`diffusion.py`: Wan 2.2 TI2V-5B and LTX-Video distilled on Kaggle's T4; `own.py`: a slow
   camera move over the shot's picture with ffmpeg; `paid.py`: switched-off slots). A tool that dies or changes = fix or
   remove one plug.
3. **Router** (`router.py`): tries `config.json` → `order`; moves on after an error, a timeout, a used-up allowance or a
   failed check; benches a tool after repeated failures (`bench`).
4. **Last step we own:** `own` never needs a GPU or the network, so a video is always made from the shot's picture.
5. **Same check for every tool** (`checks.py`): plays, right length, not black, moves, no flicker; plus any stronger
   judge passed as `Router(extra_check=...)` (e.g. Hidden Reasons' picture checker).
6. **Cache and log:** a shot is keyed by its content (`Shot.key()`); a re-run reuses the clip. Every attempt goes to
   `cache/video_shots/log.jsonl` (which tool made it, what the others did).

## Free vs paid (checked 19 Nov 2026; prices change)
| Tool | Free and automatable? | State |
|---|---|---|
| Wan 2.2 TI2V-5B (open weights) | yes, on Kaggle's free T4 (slow) | on, first |
| LTX-Video distilled (open weights) | yes, on Kaggle | on, second |
| own renderer | yes, anywhere | on, last |
| Kling API | no free tier (~$0.056–0.42 per second) | off |
| Veo (Gemini API) | paid tier only | off |
| Higgsfield | paid subscription | off |

Free *websites* (Kling web, Google Flow) are not plugs: scripting a website usually breaks its terms.
To enable a paid tool (only with Franklin's yes): write its request code in `paid.py`, add its key as a GitHub
secret, set `"enabled": true` for it and `"paid_ok": true` in `config.json`.

## Limits
- GPU time: Kaggle gives 30 free T4 hours a week and Hidden Reasons comes first. Wan on a T4 takes minutes per
  second of video, so AI shots are for the few shots that need realism, not every shot.
- Control: AI video can't reliably draw exact text, numbers or the same product twice. Put text, numbers and diagrams
  on top with our own engines.
