"""Diagnose one model: tiny text, tiny JSON, and a long prompt; print timing and the full (scrubbed) error.

    python -m studio.pipeline.probe_model nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b
"""
import sys
import time


def main(ref):
    from ailayer.client import call_model, load_config
    from ailayer.providers import ProviderError
    cfg = load_config()
    long_prompt = ("Summarise this in one sentence: " + "Goosebumps are tiny bumps on the skin caused by muscles "
                   "pulling hairs upright when cold or emotional. " * 300)
    for name, prompt, mt in (("tiny text", "Reply with the single word OK.", 50),
                             ("tiny JSON", 'Return JSON only: {"ok": true}', 50),
                             ("long prompt (~6k tokens)", long_prompt, 200)):
        for attempt in (1, 2):
            t0 = time.time()
            try:
                text, info = call_model(ref, prompt, temperature=0, max_tokens=mt, cfg=cfg, tier="probe")
                print(f"{name} #{attempt}: OK in {time.time() - t0:.1f}s -> {text.strip()[:120]!r}")
            except ProviderError as e:
                print(f"{name} #{attempt}: FAILED in {time.time() - t0:.1f}s -> HTTP {e.status}: {str(e.reason)[:300]}")
            except Exception as e:
                print(f"{name} #{attempt}: FAILED in {time.time() - t0:.1f}s -> {type(e).__name__}: {str(e)[:300]}")
            time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1])
