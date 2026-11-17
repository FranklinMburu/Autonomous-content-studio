# Needs fixes (checked 2026-11-17T02:11:17Z, answer by pull request #131 by FranklinMburu)

Fix every PROBLEM below in answer.json,
run `python -m studio.story.filmkit check-answer polish/film/006-why-titanic-skimped-on-lifeboats`, then push again.

```
fact check of the polished script: {'unsupported': 4, 'supported': 14, 'partial': 0}
PROBLEM: shot rewrite: 3.4 s on screen (max 3.2; split it)
PROBLEM: cast executive looks like supervisor from 005-why-the-radium-girls-licked-poison; give this person a new look
PROBLEM: script: numbers not in the sources: ['hundred', 'nine', 'ninety', 'sixty']; remove them or use the sources' numbers
PROBLEM: script: every beat needs a "feel": the one emotion the viewer should have there
PROBLEM: script: not supported by the sources: Sailors lower a lifeboat built for sixty-five, carrying just twenty-eight people.
PROBLEM: script: not supported by the sources: It is the first boat to leave the sinking Titanic.
PROBLEM: script: not supported by the sources: In 1909, that worked perfectly when another liner, the Republic, sank.
PROBLEM: script: not supported by the sources: So in 1914, the world rewrote the rules.
8 problem(s)
```
