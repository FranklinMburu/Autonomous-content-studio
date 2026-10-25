"""Stage: script. Topic -> script JSON in our format, written by Gemini and checked by our validator."""
import json
from . import gemini, schema

SYSTEM = """You write scripts for short, animated, vertical YouTube explainer videos (YouTube Shorts).
Your output is rendered automatically: a calm narrator voice, flat 2D motion graphics, word-by-word captions.
You care about three things, in order: (1) factual accuracy, (2) a story that makes viewers watch to the end,
(3) visuals that show exactly what is being said at that moment."""

RULES = """WRITE THE SCRIPT FOR THIS TOPIC: {topic}
{lane}
Hard rules:
- Total narration {wmin}-{wmax} words (about 35-55 seconds). Count carefully.
- Beat 1 is the HOOK: one line, at most 14 words, a surprising claim or question that creates curiosity.
  Do not answer it yet. No greetings, no "did you know", no "in this video".
- Then 3-5 beats, each one idea, each 1-3 short spoken lines. Plain conversational English, short sentences.
- The last beat is the PAYOFF: answers the hook in a satisfying, slightly surprising way. If possible its final
  line flows naturally back into the hook so the video loops. No "subscribe" or "follow" requests.
- Every factual claim must be true and come from a real, publicly accessible web page that you are confident
  exists. Prefer Wikipedia, university, museum, government, or major science-news pages. Give the exact URL.
  If you are not sure of a fact, leave it out. No medical, legal, or financial advice.
- Choose a scene for each beat from the catalogue below, picking what best SHOWS that beat. Use at least 4
  different scene types. "at" values are single words copied exactly from that beat's narration; they make the
  visual change at the moment the word is spoken.
- Icons: use simple English names of common objects ("brain", "heart", "moon", "rocket", "fish", "clock").
  Only use "@cat" if the topic is about cats.
- Labels on screen: 1-4 words. Never repeat the whole narration on screen (captions already do that).
- Write numbers in narration as words if spoken ("twenty-five"); years as digits ("1969") are fine.
- Optional per beat: "kicker" (2-4 word label at top, e.g. "The old theory", "1969 · NASA") and "source"
  (short citation shown small, e.g. "NASA (2019)").

Scene catalogue:
{scenes}

Return ONLY a JSON object with this shape (this is a complete example for a different topic):
{example}
"""

FIX = """Your previous script had these problems:
{problems}
Return the corrected complete JSON object only."""


def build_prompt(topic, lane=None):
    scenes = "\n".join(f"- {k}: {v}" for k, v in schema.SCENE_DOCS.items())
    lane_txt = f"Channel focus / audience: {lane}" if lane else ""
    return RULES.format(topic=topic, lane=lane_txt, wmin=schema.WORDS_MIN + 10, wmax=schema.WORDS_MAX - 10,
                        scenes=scenes, example=json.dumps(schema.EXAMPLE, ensure_ascii=False, indent=1))


def write(topic, lane=None, attempts=3, log=print):
    prompt = build_prompt(topic, lane)
    history = prompt
    last = None
    for i in range(attempts):
        txt, model = gemini.generate(history, system=SYSTEM)
        try:
            script = gemini.parse_json(txt)
        except Exception as e:
            problems = [f"output was not valid JSON ({e})"]
        else:
            script.setdefault("topic", topic)
            errors, warns = schema.validate(script, fix=True)
            last = (script, errors, warns, model)
            if not errors:
                log(f"  script written by {model} (attempt {i + 1}); {schema.words_of(script)} words")
                return script, warns, model
            problems = errors
        log(f"  attempt {i + 1} rejected: {'; '.join(problems)[:300]}")
        history = prompt + "\n\n" + (txt if len(txt) < 12000 else txt[:12000]) + "\n\n" + \
            FIX.format(problems="\n".join(f"- {p}" for p in problems))
    if last:
        raise ValueError(f"script still invalid after {attempts} attempts: {last[1]}")
    raise ValueError("Gemini never returned valid JSON")
