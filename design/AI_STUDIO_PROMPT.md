# Prompt for Google AI Studio (copy everything inside the box)

How to use (Franklin):
1. In Google AI Studio → **Build**, import the GitHub repo **FranklinMburu/Autonomous-content-studio**, branch
   **`ui-sketch`** (or upload the `design/` folder if import is not available).
2. Paste the prompt below as your first message. Nothing else.
3. When it is done, check it against `design/BUILD_SPEC.md` §11 (the acceptance checklist). If something differs,
   reply: *"Section X of BUILD_SPEC.md is not met: <what you see>. Fix only that."*

---

```text
You are building the website and app for "Candela", a studio that turns true stories into short films. Everything
is already designed and decided. Your job is to BUILD IT EXACTLY, not to design it.

READ THESE FILES FIRST, IN THIS ORDER, COMPLETELY, BEFORE WRITING ANY CODE:
1. design/README.md            - what is where
2. design/BUILD_SPEC.md        - the law: stack, rules, every landing section with exact sizes, motion, performance
3. design/APP_PAGES.md         - every route, the sidebar, the top bar, the command palette, every page, every flow
4. design/DATA_CONTRACT.md     - where every value comes from (the real backend on GitHub), states, actions
5. design/mockups/*.png        - the approved screens (1440 px wide, 1 image px = 1 CSS px)
6. design/reference/pages/*.html - the exact HTML/CSS/JS of each mockup (copy values from here)
7. design/kit/*                - finished, tested code you must use as-is: candela.css, earth.js, studio-world.js,
                                 smooth-scroll.js, github-data.js, places.json

HARD RULES (breaking any of them means the work is rejected):
- Rebuild the mockups exactly: same layout, positions, sizes, colours, fonts, letter-spacing, copy. Port the CSS of
  the reference pages value for value. Do not redesign, restyle, re-space, re-word or "improve" anything.
- Use the kit files unchanged (copy them into web/src/lib and web/src/styles). Do not rewrite the globe, the data
  layer, the smooth scroll or the CSS tokens.
- NO SEED DATA. NO SAMPLE DATA. NO MOCK DATA. The backend already exists and is running on GitHub. Every film,
  number, status, video and picture comes from design/kit/github-data.js (read-only, public, no keys). If a value is
  missing, show the empty state or "—" defined in DATA_CONTRACT.md. Do not create any mock, seed, fixture, sample,
  demo-data, lorem or faker file or constant. Do not hard-code film titles or counts.
- The site never writes anything and has no secrets: every action button opens the GitHub page listed in
  DATA_CONTRACT.md section 4, in a new tab.
- Build only the pages listed in APP_PAGES.md. Planned pages use the "Soon" template (mockup 13) with no numbers.
- Stack: React 19 + TypeScript (+ Vite if available). Allowed packages ONLY: react, react-dom,
  @phosphor-icons/react. NO three.js or any WebGL library, NO GSAP, NO framer-motion, NO Tailwind, NO UI kits,
  NO chart libraries, NO other icon sets, NO Google Fonts (fonts are local files in design/reference/assets/fonts).
- Icons: Phosphor only. Duotone in the sidebar and on feature tiles; bold/regular for small UI icons, exactly as in
  the reference HTML.
- Colour: ink background #0B0B0F (never a blue background). Headlines are chrome gradient text. Primary buttons are
  silver. Gold/amber (#F5A524, #FFC861) ONLY for: the logo mark, the active sidebar item and its glow, live status
  dots, Review/Polish chips, the globe's sun, arcs and city lights, schedule times. Never on headlines, buttons,
  charts or large areas.
- Motion: only what BUILD_SPEC.md section 7 lists. Smooth scroll, reveals and count-ups with kit/smooth-scroll.js (Franklin's portfolio
  feel; no scroll library). Animate only transform
  and opacity. Respect prefers-reduced-motion.
- Performance: BUILD_SPEC.md section 8 (first-load JS <= 180 KB gzipped, canvases paused off-screen, fps watchdog).
- Put all code in a new folder web/ at the repo root. Work on a new branch named ui-web created from ui-sketch.
  Never commit to main. Do not change any file outside web/.
- If something is not specified, do the simplest thing that uses only components already in the mockups, and list
  it at the end under "Decisions I made". Do not invent new sections, features, badges, testimonials or copy.

BUILD ORDER (finish and check each step before the next):
1. web/ project, fonts, candela.css, the 40-line router, AppShell (sidebar + top bar + command palette) with every
   route from APP_PAGES.md rendering its page title, connected to github-data.js.
2. App pages: Films, Film detail, Runs, Run detail, Review, Polish, Upload (they match mockups 08-10), then Channels,
   Topics, Schedule, Memory, Brain, Lab, Guard, Settings, the six Soon pages (mockup 13), 404. Loading, empty and
   error states from DATA_CONTRACT.md section 5 on every page.
3. Light theme (mockup 11) and the phone layout (mockup 12).
4. Landing: nav, hero with the globe (earth.js + buildGlobe + pickTags; the sun rises with scroll as in mockups
   02 and 02b), the live studio panel (mockup 02c, the real AppShell inside the frame, no iframe), family (03),
   how it works (04), Studio World (05, studio-world.js), films and trust (06), footer. Public pages /films,
   /films/:id, /pricing, /how-it-works.
5. Run the acceptance checklist in BUILD_SPEC.md section 11 and report each item as pass/fail with a short note.

When you finish, reply with: the list of files created, the checklist results, and "Decisions I made" (if any).
```
