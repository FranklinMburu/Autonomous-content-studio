# Candela: build spec for the landing site and the app (v4, approved 2 Nov 2026)

> **This file is the law**, together with `APP_PAGES.md` (every page and flow) and `DATA_CONTRACT.md` (where every
> value comes from). If anything conflicts with `UI_BRIEF.md`, these three win. If anything conflicts with
> your own ideas, this file wins. The goal is to rebuild the approved mockups **exactly**: same colours, same type,
> same positions, same copy. Nothing is "inspired by" them. They *are* the design.

---

## 0. The ten rules (read twice)

1. **Copy, don't invent.** Every screen already exists as a working HTML page in `design/reference/pages/` and as
   a picture in `design/mockups/`. Port that HTML/CSS into components **value for value** (same px, same colours,
   same font sizes, same letter-spacing, same copy). Do not "improve", restyle, re-space, re-word or re-colour.
2. **Use the kit.** `design/kit/` holds the finished, tested pieces: `candela.css` (all tokens and base styles),
   `earth.js` (the hero globe), `studio-world.js` (the section-5 sphere), `smooth-scroll.js` (the scroll and motion feel of Franklin's portfolio: no library),
   `github-data.js` (the data layer that reads the real studio on GitHub) and `places.json` (where each real story
   happened). Import them as they are. Do not rewrite them.
3. **Light only.** React + TypeScript. Allowed libraries: `react`, `react-dom`, `@phosphor-icons/react`. (No scroll library: the smooth scroll is our own code.)
   Nothing else. **No three.js, no WebGL libraries, no GSAP, no framer-motion, no Tailwind, no UI kits, no chart
   libraries, no icon packs other than Phosphor.** Animations are CSS transitions + `requestAnimationFrame`.
4. **One icon family:** Phosphor. Sidebar and feature icons use the **duotone** weight; small UI icons use **bold**
   or **regular** exactly as in the reference HTML (the SVGs are inlined there, so you can see which).
5. **Fonts are local files**, never Google Fonts: `Inter` (variable) for UI, `Inter Display` (Bold, ExtraBold and
   their italics) for headlines. Files: `design/reference/assets/fonts/` → copy to `public/fonts/`.
6. **Gold is a signal, not a paint.** Amber (`#F5A524` / `#FFC861`) is used ONLY for: the logo mark, the active
   sidebar item and its hover glow, live/running status dots, "Review" chips, the globe's sun, arcs and city lights,
   and the scheduled-time labels in the app. **Never** for headlines, primary buttons, charts, section titles or
   large areas. Headlines are **chrome** (white→grey gradient text). Primary buttons are **silver**.
7. **Ink, not blue.** The page background is neutral ink `#0B0B0F` with two faint radial tints and a film grain
   (all in `candela.css`). Do not add blue backgrounds or blue glows anywhere except the sidebar gradient.
8. **No seed data, no sample data, no mock data.** The backend already exists and runs on GitHub. Every title,
   number, status, video and picture comes from `github-data.js` (see `DATA_CONTRACT.md`). Missing → empty state or
   "—". Never create mock/seed/fixture files. No testimonials, no customer logos, no invented numbers. The values
   drawn inside the app mockups show layout only.
9. **Never touch `main`.** Work on the branch named in section 12. Never add secrets, keys, analytics or trackers.
10. **When unsure, open the reference page** in a browser (`design/reference/pages/<name>.html`) and measure it.
    The mockup PNGs are 1440 px wide screenshots of exactly those pages (1 CSS px = 1 image px).

---

## 1. What is in `design/`

| Path | What it is |
|---|---|
| `mockups/*.png` | The approved screens, 1440 px wide. The visual source of truth. |
| `reference/pages/*.html` | The exact HTML/CSS/JS that produced each mockup. Open in Chrome: it renders identically. |
| `reference/assets/img/*.jpg` | All pictures (film stills, posters). |
| `reference/assets/fonts/*.woff2` | Inter variable + Inter Display Bold/ExtraBold (+ italics), with the OFL licence. |
| `reference/assets/earth.json` | Land and ocean dot positions for the hero globe (lat/lon pairs). ~1 MB, gzips to ~250 KB. |
| `kit/candela.css` | All design tokens + base styles + chrome layer + app shell + landing shared styles. |
| `kit/earth.js` | Hero globe (Canvas 2D, layered, scroll-driven sun). Tested at 1440×900 and 390×844. |
| `kit/earth-demo.html` | A test page for the globe: serve the repo root and open `/design/kit/earth-demo.html`. |
| `kit/studio-world.js` | Section-5 sphere (Canvas 2D). |
| `kit/smooth-scroll.js` | The portfolio's scroll feel, exactly: gliding wheel scroll (lerp 0.1), `scrollVar`, `reveal`, `countUp`. |
| `reference/portfolio-scroll.md` | Full notes and code of Franklin's portfolio motion (the feel to match). |
| `kit/github-data.js` | The data layer: reads releases, issues, Actions runs and episode files of the real repo (no keys). |
| `kit/github-data.test.mjs` | Live test of the data layer (read-only). |
| `kit/places.json` | Where each real episode and each queued topic happened (for the globe). |
| `APP_PAGES.md` | Every route, the sidebar, the top bar, ⌘K, every page's content, flows, roadmap placeholders. |
| `DATA_CONTRACT.md` | Which function feeds which screen, status labels, empty/error states, read-only actions. |
| `AI_STUDIO_PROMPT.md` | The prompt to paste into Google AI Studio. |

### Mockup → page map

| Mockup | Reference page | What it is |
|---|---|---|
| `01_brand.png` | `01_brand.html` | Brand sheet: mark, colours, type, icons, family. Not a page of the site. |
| `02_landing_hero.png` | `02_landing_hero.html` | **Landing section 1 (hero)** at the top of the page (dawn on the left). |
| `02b_landing_hero_scrolled.png` | `02b_landing_hero_scrolled.html` | The same hero after scrolling ~800 px: the sun has risen to the top of the globe. |
| `02c_landing_app_panel.png` | `02c_landing_app_panel.html` | **Landing section 2: the live studio panel** (clickable app inside a browser frame). |
| `03_landing_family.png` | `03_landing_family.html` | **Landing section 3: the product family** (5 cards). |
| `04_landing_how_it_works.png` | `04_landing_how_it_works.html` | **Landing section 4: how a film is made** (pinned scroll story). |
| `05_landing_studio_world.png` | `05_landing_studio_world.html` | **Landing section 5: the Studio World** sphere + live numbers. |
| `06_landing_films_trust.png` | `06_landing_films_trust.html` | **Landing section 6: films gallery, guardrails, final call to action.** |
| `08_app_films.png` | `08_app_films.html` | App: Films (dark). Also the default view inside the section-2 panel. |
| `09_app_runs.png` | `09_app_runs.html` | App: Runs. |
| `10_app_review_polish.png` | `10_app_review_polish.html` | App: Review + Polish. |
| `11_app_light.png` | `11_app_light.html` | App: Films in the light theme. |
| `12_mobile.png` | `12_mobile.html` | Phone: landing hero (left phone) and app Films (right phone) at 390 px. |
| `13_app_soon_template.png` | `13_app_soon_template.html` | The template for every planned ("Soon") page, with the GROW group expanded. |

---

## 2. Stack and project layout

- **Vite + React 19 + TypeScript**, plain CSS (import `candela.css` once, then one CSS file per component, written
  by porting the `<style>` of the reference page). If your environment cannot run Vite, use its standard
  React + TypeScript setup; the rest of this spec does not change.
- Dependencies (exactly these): `react@^19`, `react-dom@^19`, `@phosphor-icons/react@^2.1`.
  Dev: `vite@^6`, `@vitejs/plugin-react`, `typescript`.
- Put the app in a folder named **`web/`** at the repo root:

```
web/
  index.html
  package.json
  vite.config.ts
  public/
    fonts/            <- design/reference/assets/fonts/*
    img/              <- design/reference/assets/img/*
    earth.json        <- design/reference/assets/earth.json
  src/
    main.tsx          (router: "/" = landing, "/app/*" = app)
    styles/candela.css   <- copy of design/kit/candela.css (font URLs already point to /fonts/)
    lib/earth.js  lib/studio-world.js  lib/smooth-scroll.js  lib/github-data.js  lib/places.json   <- copies of design/kit/*
    landing/  Nav.tsx Hero.tsx StudioPanel.tsx Family.tsx HowItWorks.tsx StudioWorld.tsx FilmsTrust.tsx Footer.tsx
    app/      AppShell.tsx Sidebar.tsx Topbar.tsx CommandPalette.tsx
              views/{Films,FilmDetail,Runs,RunDetail,Review,Polish,Upload,Channels,Channel,Topics,Schedule,Memory,
                     Brain,Lab,Guard,Soon,Settings,NotFound}.tsx      (one file per page in APP_PAGES.md)
    public/   FilmsPage.tsx FilmPage.tsx Pricing.tsx HowItWorksPage.tsx
    ui/       Mark.tsx Chip.tsx Button.tsx Icon.tsx
```

- **Pictures:** films show their real video (first frame as poster) and contact sheet from GitHub Releases. The
  files in `/public/img/` are only the stills used by the static landing sections (4 How it works, 6 Films gallery
  fallback before data loads) and the brand page. If your environment cannot hold binary
  files, use the public GitHub URLs instead:
  `https://raw.githubusercontent.com/FranklinMburu/Autonomous-content-studio/ui-sketch/design/reference/assets/img/<name>.jpg`
  (same for `fonts/` and `earth.json`). The repo is public, so these always work.
- Routing: no router library is needed; a 40-line router on `history.pushState` handles the routes in `APP_PAGES.md`.

## 3. Design tokens (all already in `kit/candela.css`)

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0B0B0F` (ink) | page base; the body also has two faint radial tints + grain (see `CHROME_CSS` block) |
| `--s1 / --s2 / --s3` | `#121217 / #18191F / #202128` | surfaces, stepping up |
| `--line / --line2` | `rgba(255,255,255,.07) / .12` | hairlines (always as `box-shadow: 0 0 0 1px … inset`) |
| `--tx / --tx2 / --tx3` | `#EDEFF5 / #A3A9B8 / #6E7586` | text: primary / secondary / labels only |
| `--amber / --amber2` | `#F5A524 / #FFC861` | **signal only** (rule 6) |
| status | ok `#3FB950`, bad `#F85149`, info `#58A6FF` | chips and dots only |
| Chrome text | `linear-gradient(180deg,#FFF 0%,#F2F3F7 36%,#B4B9C6 74%,#80869A 100%)` clipped to text | every `h1`, `h2` |
| Chrome italic | `'Inter Display'` 800 italic, gradient `#FFF → #E9EBF1 → #9BA1B1 → #6E7488` | the emphasised words (`.serif` class) |
| Silver button | `linear-gradient(180deg,#FFF,#E4E7EE 55%,#C3C8D3)`, text `#0A0C14` | `.btn.pri` (light theme: dark button) |
| Sidebar | `linear-gradient(180deg,#141832 0%,#151629 42%,#23181E 100%)` + two amber radial glows | app sidebar only |
| Light theme | `--bg #FAFAF7`, text `#111318`, chrome becomes dark ink gradient | `body.light` (mockup 11) |
| Radius | cards 14–16 px, buttons 10 px (hero buttons 999 px pill), chips 999 px | |
| Type | UI Inter 13–15 px; hero h1 72 px Inter Display 800, −0.045em; section h2 48–52 px | |

Never write a colour that is not in `candela.css` or the reference pages.

---

## 4. The landing page, top to bottom

Page width is fluid; the design is drawn at 1440 px. Content side margins are **96 px** at 1440 (use
`clamp(20px, 6.6vw, 96px)`). Sections are full-bleed. Call `startSmoothScroll()` once on mount (`kit/smooth-scroll.js`); it is the exact scroll of
Franklin's portfolio (mouse wheel glides, touch/keyboard/scrollbar stay native, off for reduced motion).

### 4.0 Nav (all landing sections)
From `02_landing_hero.html` (`.nav`): height 68 px, logo mark 26 px + "Candela" (17 px, 600), centre links
*Product ▾, Films, How it works, Pricing, Docs* (14 px, `--tx2`), right: "Sign in" + silver button **Start free**
(36 px high). The nav is `position: fixed`; after 40 px of scroll it gets `background: rgba(11,11,15,.72);
backdrop-filter: blur(14px); box-shadow: 0 1px 0 var(--line)` (transition 200 ms). Product ▾ opens a small menu
listing the five family products (same cards as section 3, compact: icon + name + one line).

### 4.1 Section 1: Hero with the Earth (`02_landing_hero` → `02b_landing_hero_scrolled`)
**Structure (this is what makes the sun rise):**
```
<section class="hero-wrap" style="height: calc(100vh + 800px)">   // tall wrapper = scroll room
  <div class="hero-stage" style="position: sticky; top: 0; height: 100vh; overflow: hidden">
     <canvas class="earth">  (fills the stage)            <- kit/earth.js
     <div class="lns"> + story cards + name tags (HTML, positioned from earth onPlace callback)
     <div class="hero"> product line, h1, p, buttons
     <div class="foot"> numbers row ;  <div class="scroll"> cue
```
- `progress = clamp((scrollY - wrapTop) / 800, 0, 1)` → `earth.setProgress(progress)`. At 0 the sun sits low on the
  left rim (dawn over the Americas, mockup 02); at 1 it has risen to the top of the globe above Europe (mockup 02b).
  The globe also turns 4° east. All of this is already inside `earth.js`; only feed it `progress`.
- Load `earth.json` with `fetch('/earth.json')` after first paint. Until it arrives, show the hero text and an empty
  ink stage (no spinner). The globe fades in over 600 ms (`opacity` transition on the canvas).
- Text block (`.hero`, centred, top 150 px): product line = mark 30 px + **Candela Studio** (19 px, 600, `#E9EBF1`),
  18 px gap; **h1** "History, *in motion.*" (72 px, Inter Display 800, chrome; "in motion." is the chrome italic),
  18 px gap; **p** "Short films about true stories. Researched, checked and painted for you." (21 px, `--tx2`),
  30 px gap; buttons: silver pill **Make a film** (44 px high, 22 px padding, radius 999; goes to `/app`) + text link
  **Watch a film ›** (15.5 px, 500, `#DDE2EE`; opens `/films/:id` of the newest finished film), gap 28 px.
- While scrolling, the text block moves up at 0.25× scroll speed and fades from opacity 1 to 0 between progress
  0.55 and 1.0. Nothing else moves except the globe and its labels.
- **The sheet (portfolio pattern):** after the sun has risen, section 2 slides up **over** the still-pinned hero like a
  sheet of glass: section 2 is wrapped in `.sheet` (radius 36 px on top, shadow `0 -30px 70px -20px rgba(0,0,0,.55)`,
  `z-index: 10`, ink background). Set `--hp` on the hero stage with `scrollVar(stage, "--hp", el =>
  (scrollY - 800) / el.offsetHeight)` and use it in CSS: hero stage content
  `transform: translateY(calc(var(--hp,0) * 70px)) scale(calc(1 - var(--hp,0) * .07)); opacity: calc(1 - var(--hp,0) * .85)`.
- **Places on the globe are real** (DATA_CONTRACT §6): `buildGlobe(await films(), await topics(), places)` from
  `kit/github-data.js` + `kit/places.json` returns the made films (bright lights, ring) and the queued topics (small
  dim lights) and the arcs. Pass `{ stories, arcs }` to `createEarth`.
- **Story cards (the two newest made films that have a place, decided by `buildGlobe`):** the `card: "left"` one is
  placed at `(x − 300, y − 150)` from its light, the `card: "right"` one at `(x + 150, y − 150)`. Card: 262 px wide,
  10 px padding, radius 14, `background: rgba(16,19,32,.62); backdrop-filter: blur(14px)`; poster 44×58 = the film's
  first video frame (`<video preload="metadata" muted src="…#t=0.5">`), or, for a film without a video yet (draft),
  a neutral tile with the `FilmStrip` icon; place line "LONDON · 1854" in 10.5 px caps `--tx3`; title 12.5 px 600;
  status chip (labels in DATA_CONTRACT §3). Clicking a card opens that film in the section-2 panel.
- **Name tags** for the other lights: `pickTags(places, { blocked: cardRects })` from `kit/earth.js` decides which
  tags fit (made films first, then queue order; never on top of another light or a card). 11.5 px 600 white + year
  in `--tx3`. Positions come from `onPlace`, so they follow the globe as it turns.
- **Numbers row** (bottom 34 px, centred): `{films made} films made | {facts} facts checked | {queued} stories queued
  | $0 to run`, all computed (DATA_CONTRACT §6; "—" until loaded). Numbers 15 px 650, labels 13 px `--tx3`,
  1×14 px dividers. **Scroll cue** bottom-right: 1×28 px gradient line + "SCROLL" (12 px, 0.14em).
- No app window, no pill badge, no paragraph in the hero. (These were removed on purpose.)
- **Phone (< 640 px):** see mockup 12 left phone. Text block on top (h1 46 px on two lines "History, / *in motion.*",
  p 15 px, full-width silver pill **Make a film**), globe fills the lower half (`earth.js` switches geometry
  automatically under 640 px), tags only for made films, no story cards, no numbers row.

### 4.2 Section 2: The live studio panel (`02c_landing_app_panel`): "Take a look inside."
This is the BridgeMind-style feature: **the real app, live and clickable, inside a browser frame on the landing page.**
It shows the real studio (the same data as `/app`), **read-only**.
- Section height 1080 px at 1440 wide. A faint gold residue of the sunrise at the top (`.sunres`).
- Title block (top 64 px, centred): eyebrow **INSIDE THE STUDIO**, h2 "Take a look *inside.*" (48 px, chrome),
  p "This is the real studio, live. Click anything." (17 px `--tx2`).
- **Frame:** left 100, top 236, 1240 × 806, radius 18, background `#0E0E12`, ring `rgba(255,255,255,.10)`, shadow
  `0 60px 140px -40px rgba(0,0,0,.9), 0 0 120px -40px rgba(245,165,36,.18)`. Top bar 42 px: three dots, a URL pill
  "🔒 studio.candela.film/films" (updates with the current view), and a segmented control
  **Films | Runs | Review | Polish** on the right (synced with the sidebar).
- **Inside the frame render the real `<AppShell embedded>` component** (the same one used at `/app`), laid out at
  1440 × 887 and scaled with `transform: scale(frameWidth / 1440)` (0.8611 at 1240 px), `transform-origin: 0 0`.
  Do **not** use an iframe and do **not** use a screenshot. Routing inside the frame is internal state (the page URL
  does not change).
- **Everything is clickable** (every page of `APP_PAGES.md`): sidebar, tabs, film cards → film detail with the real
  video, runs → timeline, review, polish (Copy works), upload, ⌘K, theme toggle. Buttons that act on GitHub open
  GitHub in a new tab, exactly as in the app (DATA_CONTRACT §4). Nothing is invented and nothing is saved.
- **Hints:** three white pills with an amber dot ("Every menu item works", "Click a film to watch it",
  "Live from our GitHub") at the positions in the mockup; they fade out after the first click inside the frame.
  Below the frame: `Live data | Read-only | Make your own film ›`.
- Entry animation: when the frame is 20% in view, it rises from `translateY(48px) scale(.97)` and `opacity 0` to
  rest over 700 ms (`cubic-bezier(.2,.7,.2,1)`). Once.
- Scrolling inside the frame scrolls the panel, not the page: give the panel's scroll areas `overflow-y: auto`;
  `startSmoothScroll` detects inner scrollable boxes and leaves their wheel native.
- **Phone:** the frame becomes full-width with 16 px gutters, shows the phone layout of the app (mockup 12 right
  phone: stats row, film cards, bottom tab bar) and stays interactive.

### 4.3 Section 3: The family (`03_landing_family`)
- Height 560. Eyebrow **ONE STUDIO, FIVE PARTS**, h2 "Everything a film needs. *Nothing* it doesn't." (52 px).
- Five cards in a 5-column grid (gap 14, top 240): icon tile 38–40 px (neutral glass; the Studio card's tile and
  border are amber because it is "where you are"), "Candela *Studio*" etc., one line, link "Open →".
- Clicking a card scrolls (`scrollIntoView({ behavior: 'smooth' })`) up to the section-2 panel and switches it to that product's view
  (Studio → Films, Brain → Brain, Lab → Lab, Guard → Guard, Channels → Channels). The clicked card becomes the
  amber "You are here" card.
- Stripe-style lines behind the cards: the SVG from the reference page (`lines_svg`), animated with a slow
  `stroke-dashoffset` drift (20 s loop); on hover over a card, the line nearest to it brightens (opacity .07 → .2,
  300 ms).
- Phone: cards become a horizontal scroll row (scroll-snap), 78% width each.

### 4.4 Section 4: How a film is made (`04_landing_how_it_works`)
- Pinned scroll story: wrapper height `100vh + 4 × 500px`, sticky stage 100vh. Five steps on the left (Topic, Script,
  30 painted shots, Motion & music, Review & upload); the active step (amber border, as in the mockup) advances every
  500 px of scroll. The right panel changes with the step:
  1 Topic: topic input with "Why did doctors refuse to wash their hands?" typed in;
  2 Script: script lines with claim chips "supported";
  3 Shots: the 12-shot grid exactly as the mockup (shots fade in one by one, 60 ms apart), the cast row and the
    picture checker questions;
  4 Motion & music: the same grid with three shots gently zooming (Ken Burns, 6 s) and a thin audio waveform;
  5 Review & upload: the Ready card with **Approve** and the "Ready to upload" chip.
- The thin vertical progress bar on the far right fills with scroll. "Smooth scroll · step N of 5" label.
- Phone: no pinning; the five steps stack, each with its panel underneath.

### 4.5 Section 5: The Studio World (`05_landing_studio_world`)
- Use `kit/studio-world.js` with the exact options from the reference page:
  `{"dots":3800,"r":0.40,"spin":2.1,"tilt":-0.3,"dim":1.5,"dotScale":1.3,"seed":11,"labels":["Research","Script","Fact check","Paint","Motion","Film"]}`,
  canvas 900 × 900 at left 270.
- Left: eyebrow **THE STUDIO WORLD**, h2 "Watch films *being made.*", p "Every light is a real step of a real film,
  right now. No fake numbers." Right: four computed numbers (films made this week, shots painted, facts checked
  against sources, $0 spent; DATA_CONTRACT §6) that count up once when visible (800 ms); "—" if not loaded.
- The sphere turns slowly (as in the reference script) **only while the section is on screen**
  (IntersectionObserver). Footer note: "5 KB globe · pauses off-screen · still image on slow phones".

### 4.6 Section 6: Films and trust (`06_landing_films_trust`)
- Eyebrow **MADE WITH CANDELA**, h2 "Real films. *Not slideshows.*"; up to five vertical cards of real finished films
  (`films()` with status ready / uploaded / finished; poster = first video frame; plays muted on hover; click →
  `/films/:id`). Fewer films → fewer cards, centred. Hovering a card lifts it 4 px and shows a play icon.
- Four guardrails with amber-outline icons: Every claim has a source / Every picture is checked / You stay in control /
  Free to run (copy exactly as the mockup).
- Final CTA band (bottom 40, 120 px high, radius 20): "Your first film is one topic away." + silver **Start free**.

### 4.7 Footer (not in the mockups; keep it this simple)
One row, 96 px side margins, 64 px tall, top hairline: mark + "Candela" · links (Films, How it works, Pricing, Docs,
GitHub) in 13 px `--tx3` · "© 2026 Candela". Nothing else.

---

## 5. The app (`/app`, mockups 08–11 and 13)

- **Every route, the sidebar (groups, items, icons, badges, states), the top bar, ⌘K, the content of every page, the
  planned pages and the flows are defined in `APP_PAGES.md`.** Build exactly that.
- `AppShell` = Sidebar (248 px) + Topbar (56 px) + page. Exactly the reference pages' markup and CSS (`APP_CSS` part
  of `candela.css`). Pages with mockups: Films (08 / 11 light), Runs (09), Review + Polish (10), any planned page (13).
  Pages without a mockup are built only from components that appear in the mockups (cards, rows, chips, tabs,
  stat tiles, the player, the copy box, the sources list).
- All content comes from `kit/github-data.js` (DATA_CONTRACT). The mockups' numbers and titles show layout only.
- Light theme: `body.light` (mockup 11): cream sidebar gradient, dark silver button, dark chrome headings.

## 6. Phone (`12_mobile`)

- Breakpoint 640 px. Landing phone hero described in 4.1. App on phone: no sidebar; header (mark + "Films" +
  "5 / day"), 3 stat tiles, film cards (poster 46×80 left, title, chip), **bottom tab bar** (Films, Runs, Review,
  Channels) with the amber active icon. Safe-area padding at the bottom.
- Touch targets ≥ 44 px. No hover-only interactions on phone.

## 7. Motion (complete list; add nothing else)

| Where | What | Timing |
|---|---|---|
| Whole landing | gliding wheel scroll (`startSmoothScroll`, portfolio code) | lerp 0.1 per 16.7 ms, frame-time corrected |
| Every section title and block | reveal once (`reveal()`, `.reveal`) | 0.9 s `cubic-bezier(.2,.7,.2,1)` from `translateY(60px) scale(.98)`; stagger `i × 80 ms` |
| Hero → panel | the panel section slides up over the pinned hero like a sheet (`.sheet`) while the hero content sinks and dims (`--hp`) | scroll-linked |
| Hero | sun rises + globe turns 4°, driven by scroll | progress over 800 px, ease-out cubic (inside earth.js) |
| Hero | globe fades in after `earth.json` loads | 600 ms opacity |
| Hero | text parallax 0.25× and fade between progress 0.55–1 | scroll-linked |
| Hero | arcs: the small light on each arc travels along it | 6 s loop, ease-in-out (optional, only if 60 fps holds) |
| Nav | glass background after 40 px | 200 ms |
| Panel | frame rises in once | 700 ms `cubic-bezier(.2,.7,.2,1)` |
| Panel | view switch | 180 ms cross-fade (opacity only) |
| App + panel | live refresh of runs while a run is in progress | every 30 s (visible tab only) |
| Family | lines drift; nearest line brightens on hover | 20 s loop / 300 ms |
| How it works | step change; shots fade in | 250 ms / 60 ms stagger |
| Studio World | sphere spin (only when visible); numbers count up once | per reference / 800 ms |
| Films | card lift on hover | 200 ms |
| Buttons | hover brighten 4%, press scale .98 | 120 ms |

Only `transform` and `opacity` are animated in CSS. Respect `prefers-reduced-motion`: no smooth scroll, sun stays at
the start position (earth.js already does this), no parallax, no tickers.

## 8. Performance budget (non-negotiable)

- First load JS ≤ 180 KB gzipped (React + Phosphor icons imported **one by one**, never the whole set).
- `earth.json` is fetched after first paint and cached (`Cache-Control` long); gzip/brotli on.
- Hero canvas: device pixel ratio capped at 2; `earth.js` redraws the dots only when the globe turns ≥ 0.5° and uses
  no canvas blur filter (measured ~13 ms per frame without a GPU at 1440×900). Redraw only on scroll changes.
- fps watchdog: if average frame time > 20 ms for 60 frames, recreate the globe with `{ step: 2 }` (half the dots)
  and `maxDpr: 1.5`.
- Pause every canvas (hero, Studio World) when it is off-screen (IntersectionObserver).
- Images: posters `loading="lazy"`, `decoding="async"`, explicit width/height. Fonts: `font-display: swap`,
  preload `InterVariable-latin.woff2` and `InterDisplay-ExtraBold.woff2`.
- Lighthouse (mobile) targets: Performance ≥ 90, CLS < 0.05, LCP < 2.5 s.

## 9. Accessibility

Semantic landmarks (`header`, `main`, `section` with `aria-labelledby`, `footer`); the globe canvas is
`aria-hidden="true"` with the story cards as real links; all buttons are `<button>`; focus ring
`0 0 0 2px #0B0B0F, 0 0 0 4px #FFC861`; text contrast AA (never use `--tx3` for body text); the live panel is
keyboard-navigable (Tab through sidebar, Enter to open).

## 10. Never

- Never change copy, colours, sizes or positions from the mockups. Never add sections, badges, emojis, testimonials,
  logos of other companies, "AI-powered" slogans, gradient blobs, glassmorphism cards outside those specified,
  or stock illustrations.
- Never use gold on headlines, buttons or charts (rule 6). Never use a blue page background (rule 7).
- Never use three.js/WebGL libraries, Lenis or any scroll library, Locomotive-style scroll, GSAP, framer-motion, Tailwind,
  component kits, or Google Fonts.
- Never add cursor-chasing effects, big cursor glows, or `filter: blur()` glows (glows are layered `radial-gradient`).
- Scroll moves must vary: never repeat the same entrance for every section (reveal for blocks, pinning for the hero
  and How it works, the sheet for the panel).
- Never put the app panel in an iframe or as an image. Never fetch anything except our own files.
- Never commit to `main`, never add secrets, keys, analytics or third-party scripts.

## 11. Acceptance checklist (do all of these before saying "done")

1. At a 1440×900 window, screenshots of `/` at scroll 0 and scroll 800 match `02_landing_hero.png` and
   `02b_landing_hero_scrolled.png` (same layout, same copy, globe framing within ±10 px).
2. Scrolling further shows, in order: the studio panel (02c), family (03), how it works (04), Studio World (05),
   films and trust (06), footer.
3. In the panel: every sidebar item switches page; a film card opens its detail with the real video; GitHub actions open
   GitHub in a new tab; ⌘K works;
   the hint pills disappear after the first click; nothing scrolls the page while scrolling inside the panel.
4. `/app` shows the same app full-screen; Films/Runs/Review/light/planned pages match the layout of 08/09/10/11/13;
   every route in `APP_PAGES.md` exists; the numbers shown equal what GitHub shows (spot-check 3 of them).
4b. Search the code for `mock`, `seed`, `fixture`, `sample`, `lorem`, `faker`, hard-coded film titles or counts:
   there must be none (the only content files allowed are `places.json` and the fixed copy of the pages).
5. At 390×844 the landing and app match `12_mobile.png`.
6. Gold appears only where rule 6 allows (search the CSS for `F5A524`/`FFC861`/`245,165,36` and check each use).
7. `npm run build` passes with no TypeScript errors and no console errors in the browser.
8. Lighthouse mobile Performance ≥ 90.

## 12. Git

- Branch: **`ui-web`**, created from `ui-sketch`. Never `main`. Commit message style: short, plain English.
- Commit author email: `184284364+FranklinMburu@users.noreply.github.com`.
- Commit `web/` only (plus `web/public` assets). Do not modify `design/`, `studio/`, `pipeline/`, `.github/` or any
  other folder.
