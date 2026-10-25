"""Minimal client for Google's Gemini API (free tier). No SDK needed.

The key comes from the GEMINI_API_KEY environment variable (a GitHub secret in the workflow).
Models are tried in order; on quota/availability errors we fall back to the next one.
"""
import json, os, re, time, urllib.error, urllib.request

DEFAULT_MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiError(RuntimeError):
    pass


def models():
    env = os.environ.get("GEMINI_MODEL", "").strip()
    return [m.strip() for m in env.split(",") if m.strip()] if env else DEFAULT_MODELS


def generate(prompt, system=None, json_mode=True, temperature=0.8, max_tokens=8192):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise GeminiError("GEMINI_API_KEY is not set. Add it as a secret (see README).")
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}}
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = json.dumps(body).encode()
    errors = []
    for model in models():
        for attempt in range(3):
            req = urllib.request.Request(URL.format(model=model), data=data, method="POST",
                                         headers={"Content-Type": "application/json", "x-goog-api-key": key})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    out = json.loads(r.read())
                parts = out["candidates"][0]["content"]["parts"]
                txt = "".join(p.get("text", "") for p in parts if not p.get("thought"))
                return txt, model
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")[:300]
                errors.append(f"{model}: HTTP {e.code} {msg}")
                if e.code in (429, 500, 503) and attempt < 2:
                    time.sleep(8 * (attempt + 1)); continue
                break  # 400/403/404 or out of retries -> next model
            except (KeyError, IndexError) as e:
                errors.append(f"{model}: unexpected response ({e})"); break
            except Exception as e:
                errors.append(f"{model}: {e}")
                if attempt < 2:
                    time.sleep(5); continue
                break
    raise GeminiError("All Gemini models failed:\n  " + "\n  ".join(errors[-6:]))


def parse_json(txt):
    txt = txt.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", txt, re.S)
    if m:
        txt = m.group(1)
    start = min([i for i in (txt.find("{"), txt.find("[")) if i >= 0], default=0)
    return json.loads(txt[start:])
