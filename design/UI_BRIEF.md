# UI brief: YouTube Creator Studio (landing site + app)

> **Superseded (2 Nov 2026, v4).** The approved design, every page and the data rules now live in
> [`README.md`](README.md) → [`BUILD_SPEC.md`](BUILD_SPEC.md), [`APP_PAGES.md`](APP_PAGES.md),
> [`DATA_CONTRACT.md`](DATA_CONTRACT.md). Where this brief differs (blue base, gold buttons and headlines, the app
> window in the hero, sample data), those files win. Kept for the taste notes and references.

> **How to use this file.** Paste it whole into Google AI Studio (or any AI builder) as the first message, or import
> this repo and say: *"Read design/UI_BRIEF.md and follow it exactly."* It records Franklin's taste (2 Nov 2026) and
> the decisions made with Claude, so every tool starts from the same place. Change it here, not in chat.

---

## 1. What we are building

**YouTube Creator Studio** turns a topic into a finished, fact-checked, animated short film, automatically, for $0.
A free AI pipeline researches, writes, fact-checks, narrates, paints ~30 film shots with a consistent cast,
animates them, mixes music and publishes. A human only reviews and uploads.

- First channel: **Hidden Reasons** (true stories behind history's strangest acts, 3D-animated film look).
- Proof we can show: real finished films (e.g. *Why Doctors Were Ordered to Wash Their Hands*), real pipeline runs,
  real guardrails (picture checker, fact check, review gate).
- Audience for the site: creators and small media teams first; enterprise media teams later. **No one knows us
  yet**, so the site must be minimal but never boring: it shows the product working instead of describing it.

## 2. Franklin's taste (the brief, in his words, ordered)

1. **A product family, presented as one serious company** (reference: BridgeMind, bridgemind.ai: several products
   under one brand). Ours, working names: **Studio** (the app), **Brain** (free-model AI layer), **Lab** (GPU film
   engine), **Guard** (fact check + picture checker + review gate), **Channels** (each niche). Do not copy BridgeMind.
2. **Click the real app from the landing page.** The hero/product section contains a live, clickable mock of the app
   (sidebar tabs switch real screens: Films, Runs, Review, Channels). Not a screenshot. (References: BridgeMind,
   Raycast's looping product demo.)
3. **A living "world" that moves**, light enough for any phone (reference: tradingview.com hero; stripe.com globe
   with dots and arcs; github.com globe). Ours is **not a copy of a globe of users** (we have none yet and never fake
   data). Concept: **"The Studio World"**: a slowly turning dotted sphere or constellation where each glowing point
   is a real step of a real film being made (research → script → fact check → paint → film), arcs travel between
   steps. Must run at 60 fps on a mid phone (see section 5).
4. **Smooth scrolling** (the feel Claude built on Franklin's own website): use **Lenis** (MIT, a few KB), never a
   heavy 3D scroll engine.
5. **Minimalism in the hero** (references: apple.com, tradingview.com): one headline (max 8 words), one line under
   it, one primary button, and the product itself (a real film playing inside the app window). No paragraphs.
6. **Stripe-style interactive lines**: thin animated lines/gradients that react to hover (subtle, decorative).
7. **App sidebar: a smooth, premium gradient** (glass-ish tint, not loud) + **premium icons** on the sidebar only
   (see 4.3). Rest of the app stays calm and neutral.

## 3. Page layout (landing)

1. **Nav**: logo, Product (family menu), Films, Pricing, Docs, Sign in, one button "Start free".
2. **Hero** (100vh): headline + one line + one button; the app window below it, playing a real film; The Studio World
   glowing softly behind.
3. **The family**: five products as five quiet cards (icon, name, one line), each opens its part of the live demo.
4. **Live demo**: the clickable app (Films / Runs / Review / Channels), real data shapes, fake nothing.
5. **How a film is made**: a pinned scroll story in 5 steps (topic → script + fact check → 30 painted shots →
   motion + music → review and upload), each step animating the app.
6. **The Studio World**: full-width living sphere with real numbers (films made, shots painted, checks passed).
7. **Films**: a gallery of finished films (vertical cards, play on hover, sound off).
8. **Guardrails**: why it is trustworthy: sources on every claim, picture checker, review gate, $0.
9. **Pricing / waitlist**, then **footer**.

## 4. Visual system

### 4.1 Colour (proposal: confirm with Franklin)
- Base (dark default): near-black navy `#0A0C14` (surfaces step up: `#10131D`, `#161A26`, `#1D2230`); hairline
  borders `rgba(255,255,255,0.06)`.
- Text: `#EDEFF5` primary, `#A3A9B8` secondary, `#6E7586` muted (muted only for labels, never body: keep WCAG AA).
- **One accent: "film amber" `#F5A524`** (the warm candle-light of our films; no competitor uses it; stands out
  from the purple/blue SaaS crowd). Used for the primary button, focus ring, active nav, key numbers. Never more
  than once per screen area.
- Status: success `#3FB950`, warning `#D29922`, danger `#F85149`, info `#58A6FF` (only for states).
- Light theme required too (base `#FAFAF7`, text `#111318`).

### 4.2 Sidebar gradient (Franklin's request, with Claude's guard rails)
- A **very low-contrast vertical gradient** on the sidebar only: from `#11141F` (top) to `#1A1622` (bottom) with a
  soft amber glow (`#F5A524` at 6-8% opacity, 240px blur) near the active item.
- Optional frosted glass: `backdrop-filter: blur(20px)` over the gradient, 1px top highlight `rgba(255,255,255,.06)`.
- Rule: the gradient is atmosphere, not decoration: text on it must still pass WCAG AA; no rainbow, no more than
  2 hues. (Reference: Arc browser sidebar themes.)

### 4.3 Icons
- Sidebar: **Phosphor Icons, Duotone weight** (MIT, 9,000+ icons, 6 weights), 20px, active item: amber duotone fill;
  inactive: muted duotone. Same family everywhere else, Regular weight, 16-18px. Never mix icon families.
- Alternatives if Franklin prefers: Hugeicons (premium styles paid) or Streamline (premium).

### 4.4 Type and spacing
- **Inter** (UI) / **Inter Display** (headlines); optional one serif for the hero headline only (cinema feel).
- Hero headline 72-96px desktop / 44-56px mobile, tight line-height (1.0-1.05); body 15-17px, line-height 1.5.
- 4px spacing grid (8, 12, 16, 24, 32, 48, 64, 96). App rows 36-40px.
- Radius 10-14px for cards, 8px for inputs. Shadows minimal; depth comes from surface steps.

## 5. Motion and performance (non-negotiable: "no stutter on any phone")

- **Budgets:** LCP < 2.5 s on 4G mid phone; landing JS < 200 KB gzipped before the demo loads; 60 fps target.
- **Smooth scroll:** Lenis, `respectReducedMotion` on (it is the default).
- **The Studio World:** use **cobe** (MIT, ~5 KB WebGL globe) or a hand-written Canvas2D point sphere, **not
  three.js**. Copy the proven techniques from Stripe's and GitHub's globes:
  - show a static SVG/WebP image first, fade into the live canvas when ready;
  - antialias off; pixel ratio max 2 (1.5 on weak devices);
  - pause when off-screen (IntersectionObserver) and while scrolling fast;
  - watch fps: if under ~55 fps for 50 frames, lower dot count and pixel ratio (GitHub's 4 quality tiers);
  - `prefers-reduced-motion` → static image.
- Hover lines (Stripe-style): CSS/SVG stroke animations or a tiny canvas, GPU-friendly (transform/opacity only).
- Videos: muted, `playsinline`, poster image, lazy-loaded, never autoplay with sound.

## 6. The app (Studio) screens to sketch

- **Sidebar** (gradient + duotone icons): Films, Runs, Review, Polish, Channels, Topics, Brain, Lab, Settings.
- **Films**: vertical film cards (poster, title, channel, status chip: Ready / Review / Making), click → player +
  sources + checks.
- **Runs**: a timeline per film (research → script → fact check → plan → paint → clips → mix → checks), live state,
  minutes per step (like Vercel deployments).
- **Review**: the weak shots side by side with buttons **Approve** / **Repaint**.
- **Polish**: the copy box for Claude + paste-back box (mirrors the GitHub issue flow).
- **Channels**: one card per channel (niche, schedule 5/day, memory: cast, places, music used).
- ⌘K command palette (Linear-style).

## 7. Stack for the sketch

React + TypeScript + Vite + Tailwind CSS, folder `web/` in this repo, on branch **`ui-sketch`** (never `main`).
Libraries allowed: `lenis`, `cobe`, `@phosphor-icons/react`, `framer-motion` (for small UI transitions only).
No three.js unless Claude and Franklin agree after a performance test. No secrets or API keys in the code. Mock data
only, shaped like the real pipeline (films, runs, checks).

## 8. Never

- Never copy another site's layout pixel-for-pixel, logos, illustrations or copy (BridgeMind, Stripe, TradingView,
  Linear, Vercel are references for *qualities*, not templates).
- Never fake numbers, users, testimonials or logos. Before we have users, show real pipeline numbers only.
- Never more than one accent colour; never more than one icon family; never paragraphs in the hero.

## 9. References (to study, not copy)

| Quality | Where to see it | Proof / why |
|---|---|---|
| Product family under one brand | bridgemind.ai | 4 products, one brand (BridgeCode, BridgeVoice, BridgeMCP, BridgeSpace) |
| Living globe with dots and arcs | stripe.com, stripe.com/blog/globe | 60 fps target, static fallback, antialias off, works on mobile |
| Light globe engineering | github.com, github.blog "How we built the GitHub globe" | fps watchdog + 4 quality tiers, instanced dots, SVG first |
| Minimal hero | tradingview.com, apple.com | TradingView hero: 28-character headline, one line, one button |
| App-first landing, looping product demo | raycast.com | dark base, animated product demo in the hero |
| Engineering-grade app UI | linear.app | one accent, Inter only, 4px grid, ⌘K |
| Deployment timeline UI | vercel.com | runs/deployments view = our film runs |
| Gradient sidebar themes | Arc browser (arc.net) | theme gradient sidebar, frosted panes |
| Small globe library | github.com/shuding/cobe | ~5 KB, MIT |
| Smooth scroll | lenis.dev | few KB, MIT, respects reduced motion |
| Premium icons | phosphoricons.com | 9,072 icons, 6 weights incl. Duotone |
