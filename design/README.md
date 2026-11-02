# design/: start here

Everything needed to build the Candela landing site and app **exactly as approved** (Franklin, 2 Nov 2026), with
no guessing and no seed data.

| Read | What it gives you |
|---|---|
| [`AI_STUDIO_PROMPT.md`](AI_STUDIO_PROMPT.md) | The prompt to paste into Google AI Studio (or any AI builder). |
| [`BUILD_SPEC.md`](BUILD_SPEC.md) | The law: rules, stack, design tokens, every landing section with exact sizes, motion, performance, checklist. |
| [`APP_PAGES.md`](APP_PAGES.md) | Every route, the sidebar (groups, icons, badges, states), top bar, ⌘K, every page's content, flows, roadmap. |
| [`DATA_CONTRACT.md`](DATA_CONTRACT.md) | Where every value comes from (the real studio on GitHub), status labels, empty/error states, read-only actions. |
| `mockups/` | 14 approved screens, 1440 px wide (1 px = 1 CSS px). |
| `reference/pages/` | The exact HTML/CSS/JS of each mockup. Open one in Chrome: it renders identically. |
| `reference/assets/` | Fonts (Inter, Inter Display; OFL), film stills, `earth.json` (land dots for the globe). |
| `kit/` | Finished, tested code to use as-is: `candela.css`, `earth.js` (+ `earth-demo.html`), `studio-world.js`, `smooth-scroll.js`, `github-data.js` (+ live test), `places.json`. |
| [`UI_BRIEF.md`](UI_BRIEF.md) | The earlier brief (taste and references). Superseded where it differs. |

## The decisions in one screen

- **Brand:** Candela (working name; check the trademark before launch). Mark = a candle flame in a film ring with a
  play cut-out. Product family: Studio, Brain, Lab, Guard, Channels.
- **Look:** ink black `#0B0B0F` with grain and two faint tints; chrome (white→grey) headlines in Inter Display;
  silver buttons; gold only as a signal (logo, active item, live dots, the globe's sun, arcs and city lights).
  The app sidebar keeps its blue-to-ember gradient. Phosphor duotone icons.
- **Hero:** Apple-style, product first: "Candela Studio" / **History, *in motion.*** / one line / Make a film. A
  dotted Earth with real continents; the sun rises over its rim as you scroll; the lights are real: films already
  made and topics in the queue, placed where each story happened.
- **Right under the globe:** the real studio, live and clickable, inside a browser frame (read-only).
- **Data:** no seed data anywhere. The site reads the running backend on GitHub (releases, issues, Actions runs,
  episode files) with `kit/github-data.js`. Every action opens GitHub.
- **Light:** React + Phosphor only (the smooth scroll is the portfolio's own 50 lines). Canvas 2D globes (no three.js), measured ~13 ms per frame without a GPU.

## Test the kit yourself

```bash
python3 -m http.server 8765            # from the repo root
# open http://localhost:8765/design/kit/earth-demo.html   (live globe, scroll to raise the sun)
node design/kit/github-data.test.mjs   # live read-only test of the data layer
```
