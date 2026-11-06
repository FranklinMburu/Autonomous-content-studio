# Needs fixes (checked 2026-11-06T06:24:15Z, answer by pull request #25 by FranklinMburu)

Fix every PROBLEM below in answer.json,
run `python -m studio.story.filmkit check-answer polish/film/004-why-john-snow-removed-a-london-pump-hand`, then push again.

```
fact check of the polished script: {'partial': 1, 'unsupported': 3, 'supported': 17}
PROBLEM: shot simon: 3.7 s on screen (max 3.2; split it)
PROBLEM: shot gap: only 0.52 s on screen (min 0.7)
PROBLEM: script: numbers not in the sources: ['twenty']; remove them or use the sources' numbers
PROBLEM: script: title: a string of at most 8 words
PROBLEM: script: not supported by the sources: You see, it's like a whole family getting sick after one meal.
PROBLEM: script: not supported by the sources: You don't blame the air.
PROBLEM: script: not supported by the sources: You check what they all swallowed.
7 problem(s)
```
