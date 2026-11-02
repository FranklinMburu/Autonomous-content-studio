# Portfolio scroll and motion handoff

For the session building **Candela**. This describes how Franklin's portfolio scrolls and moves, with the exact code.

- **Live site:** https://franklins-portfolio-v1.vercel.app
- **Repo:** https://github.com/FranklinMburu/my-portfolio (branch `main`, commit `125a257`, released 27 Oct 2026)
- **Extracted:** 2 Nov 2026, from commit `125a257`. Every value below is copied from that commit.

---

## 0. The short version

- **No Lenis, no GSAP, no ScrollTrigger, no Framer Motion, no motion library of any kind.** Dependencies are only `react@^18.3.1`, `react-dom@^18.3.1` and `lucide-react@^0.344.0`.
- The "Lenis feel" is about 50 lines of hand-written code (`startSmoothScroll` in `src/lib/motion.ts`):
  - It eases toward a wheel target with a lerp of **0.1 per 60 fps frame**, corrected for frame time.
  - It is mouse-wheel and trackpad only. Touch, keyboard, scrollbar and links stay native.
  - It is off when the visitor asks for reduced motion, and off on devices without a fine pointer.
- Scroll-linked animation is plain `requestAnimationFrame` on a passive `scroll` listener. Positions are worked out from `window.scrollY` and written straight to element styles or CSS variables.
- Pinning is CSS `position: sticky` plus a tall spacer `div` that creates the scroll room.
- Section reveals are one IntersectionObserver plus one CSS transition: **0.9 s, `cubic-bezier(0.2, 0.7, 0.2, 1)`, from `translateY(60px) scale(0.98)` and opacity 0.**
- The house easing curve is `cubic-bezier(0.2, 0.7, 0.2, 1)`. It is used for reveals, entrances, the rise keyframe and tilt return.

### If you want the same feel with Lenis

This is a translation, not something the site uses:

| Lenis option | Equivalent on the portfolio |
|---|---|
| `lerp` | `0.1` (per 16.7 ms frame; the code corrects for frame time with `1 - (1 - 0.1)^(dt/16.7)`, `dt` capped at 64 ms) |
| `duration` / `easing` | not used (lerp-based, not duration-based) |
| `smoothWheel` | `true` |
| `wheelMultiplier` | `1` (raw `deltaY`; `deltaMode` 1 = ×16 px per line, 2 = ×`innerHeight` per page) |
| `syncTouch` / `smoothTouch` | `false`: touch is fully native |
| `touchMultiplier` | not applicable (touch is native) |
| `orientation` / `gestureOrientation` | `vertical` (horizontal-dominant wheel events are ignored and left native) |
| `infinite` | `false` (clamped to `0 … scrollHeight - innerHeight`) |
| `autoRaf` | not applicable: its own rAF runs only while gliding, then stops |
| `prevent` | inner scrollable boxes that can still scroll get the native wheel |
| Ctrl/⌘ + wheel | native (browser zoom) |
| Reduced motion / coarse pointer | not started at all |

---

## 1. Smooth scroll: `src/lib/motion.ts`

```ts
import { useEffect, type RefObject } from 'react';

/**
 * Small motion toolkit for the "premium feel" layer.
 * Everything here is additive: with reduced motion (or on touch screens where
 * noted) the page renders exactly as it does without it.
 */

export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export const hasFinePointer = () =>
  typeof window !== 'undefined' && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

const clamp = (value: number, min = 0, max = 1) => Math.min(max, Math.max(min, value));

/** True when the wheel event should scroll an inner scrollable box instead of the page. */
const scrollsInside = (target: EventTarget | null, deltaY: number) => {
  let node = target instanceof Element ? target : null;
  while (node && node !== document.body && node !== document.documentElement) {
    const style = getComputedStyle(node);
    const scrollable = /(auto|scroll)/.test(style.overflowY) && node.scrollHeight > node.clientHeight + 1;
    if (scrollable) {
      const atTop = node.scrollTop <= 0;
      const atBottom = node.scrollTop + node.clientHeight >= node.scrollHeight - 1;
      if ((deltaY < 0 && !atTop) || (deltaY > 0 && !atBottom)) return true;
    }
    node = node.parentElement;
  }
  return false;
};

/**
 * Weighted, gliding mouse-wheel scrolling (the "Lenis" feel) without a dependency.
 * Desktop mouse/trackpad only; keyboard, scrollbar, touch and links keep native behaviour.
 * Returns a cleanup function.
 */
export const startSmoothScroll = () => {
  if (prefersReducedMotion() || !hasFinePointer()) return () => undefined;

  let target = window.scrollY;
  let current = window.scrollY;
  let lastWritten = window.scrollY;
  let lastTime = 0;
  let frame = 0;

  const maxScroll = () => document.documentElement.scrollHeight - window.innerHeight;

  const tick = (time: number) => {
    // Something else moved the page (a link, the keyboard, the scrollbar): let it win.
    if (Math.abs(window.scrollY - lastWritten) > 2) {
      frame = 0;
      return;
    }
    const dt = lastTime ? Math.min(64, time - lastTime) : 16.7;
    lastTime = time;
    const ease = 1 - Math.pow(1 - 0.1, dt / 16.7);
    current += (target - current) * ease;
    if (Math.abs(target - current) < 0.5) current = target;
    window.scrollTo({ top: current, behavior: 'instant' as ScrollBehavior });
    lastWritten = window.scrollY;
    frame = current === target ? 0 : requestAnimationFrame(tick);
  };

  const onWheel = (event: WheelEvent) => {
    if (event.defaultPrevented || event.ctrlKey || event.metaKey) return;
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (document.body.style.overflow === 'hidden') return;
    if (scrollsInside(event.target, event.deltaY)) return;

    event.preventDefault();
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? window.innerHeight : 1;
    if (!frame) {
      target = current = lastWritten = window.scrollY;
      lastTime = 0;
    }
    target = clamp(target + event.deltaY * unit, 0, maxScroll());
    if (!frame) frame = requestAnimationFrame(tick);
  };

  window.addEventListener('wheel', onWheel, { passive: false });
  return () => {
    window.removeEventListener('wheel', onWheel);
    cancelAnimationFrame(frame);
  };
};
```

**The exact values:**

- **lerp:** `0.1` per 16.7 ms.
- **Snap threshold:** `0.5` px.
- **"Someone else scrolled" tolerance:** `2` px. If the page moves for another reason, the glide stops and that movement wins.
- **dt cap:** `64` ms.
- **Wheel units:** pixels ×1, lines ×16, pages ×`innerHeight`.
- **Listener:** `wheel`, `{ passive: false }`, on `window`.
- **Writes:** `window.scrollTo({ top, behavior: 'instant' })`. `'instant'` is needed because `html` has `scroll-behavior: smooth`; see §4.
- **Modal guard:** when `document.body.style.overflow === 'hidden'` (the mobile menu sets this), the wheel stays native.

### How it starts: `src/App.tsx`

There is no global rAF loop. It is started once on mount:

```tsx
import { startSmoothScroll, startSpotlight } from './lib/motion';

// inside App():
  // Premium feel: gliding wheel scroll and the light that follows the cursor on cards.
  useEffect(() => {
    const stopScroll = startSmoothScroll();
    const stopSpotlight = startSpotlight();
    return () => {
      stopScroll();
      stopSpotlight();
    };
  }, []);
```

---

## 2. Scroll-linked helper: `useScrollVar` (same file)

Writes a 0..1 number into a CSS variable once per animation frame. CSS uses it in `calc()`. It is skipped with reduced motion, so the CSS fallback value applies.

```ts
export const useScrollVar = <T extends HTMLElement>(
  ref: RefObject<T>,
  name: string,
  compute: (element: T) => number
) => {
  useEffect(() => {
    const element = ref.current;
    if (!element || prefersReducedMotion()) return;
    let frame = 0;
    const update = () => {
      frame = 0;
      element.style.setProperty(name, clamp(compute(element)).toFixed(4));
    };
    const request = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    update();
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    return () => {
      window.removeEventListener('scroll', request);
      window.removeEventListener('resize', request);
      cancelAnimationFrame(frame);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ref, name]);
};
```

The pattern used everywhere is: a passive `scroll` listener, then one `requestAnimationFrame`, then read `scrollY` or `getBoundingClientRect()` and write styles. No scroll-timeline CSS and no ScrollTrigger.

---

## 3. Pinned scroll stories

### 3a. Home hero story: `src/components/Hero.tsx`

The hero has three modes:

```ts
/**
 * The hero "story":
 *  - full (large screens): the whole hero is pinned; the name starts huge and shrinks into place,
 *    then every group arrives in turn, then the next section slides over.
 *  - compact (phones and tablets): the top of the hero (pill, name, title, line, buttons) is pinned;
 *    the name starts as three huge stacked words and settles into place, then the rest arrives;
 *    stats and skill cards rise in as they scroll into view.
 *  - off (reduced motion): the hero exactly as designed, no story.
 */
type Mode = 'full' | 'compact' | 'off';

const FULL_SCREENS = 1.6;     // scroll room for the story on large screens = 1.6 × viewport height
const COMPACT_SCREENS = 1.1;  // on phones/tablets = 1.1 × viewport height

const getMode = (): Mode => {
  if (typeof window === 'undefined' || prefersReducedMotion()) return 'off';
  return window.matchMedia('(min-width: 1024px) and (min-height: 600px)').matches ? 'full' : 'compact';
};

const clamp = (v: number, min = 0, max = 1) => Math.min(max, Math.max(min, v));
/** 0..1 progress of `story` through the window [from, to]. */
const segment = (story: number, from: number, to: number) => clamp((story - from) / (to - from));
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/** Fade/rise/un-blur an element by t (0 hidden .. 1 in place). At 1 every inline style is removed. */
const arrive = (el: HTMLElement | null, t: number) => {
  if (!el) return;
  if (t >= 1) return resetStyles(el);
  setStyles(el, {
    opacity: t.toFixed(3),
    transform: `translateY(${((1 - t) * 44).toFixed(1)}px)`,
    filter: `blur(${((1 - t) * 6).toFixed(1)}px)`,
    pointerEvents: t < 0.6 ? 'none' : ''
  });
};
```

**Large screens (`full`).** The section is `lg:sticky`, and its `top` is set so the whole section stays pinned:

```ts
section.style.top = wide.matches ? `${Math.min(0, window.innerHeight - section.offsetHeight)}px` : '';
```

The scroll room comes from a spacer placed after the hero:

```tsx
{mode === 'full' && <div aria-hidden="true" style={{ height: `${FULL_SCREENS * 100}vh` }} />}
```

The timeline uses `progress = clamp(scrollY / (innerHeight * 1.6))`. Each step:

- **Name:** starts at scale `big`, then shrinks to 1 and moves to its place over progress **0 → 0.36**, using `easeInOut`.
  - `big = max(1, min(3.4, innerWidth*0.88 / textWidth))`.
  - The name starts vertically centred.
- **The other groups arrive with `easeOut` + `arrive()`, over these windows:**

  | Group | Arrives between |
  |---|---|
  | title | 0.26 – 0.44 |
  | line | 0.32 – 0.50 |
  | buttons | 0.44 – 0.62 |
  | stats | 0.54 – 0.72 |
  | skill card *i* | 0.64 + 0.06·i – 0.80 + 0.06·i |

- **Stat count-up** starts when progress > 0.58.
- **The scroll cue** fades over progress 0 → 0.08 (`--cue`).

```ts
const update = () => {
  frame = 0;
  const progress = clamp(window.scrollY / storyLength.current);
  const n = easeInOut(segment(progress, 0, 0.36));
  applied = 1 + (metrics.big - 1) * (1 - n);
  const y = metrics.shift * (1 - n);
  name.style.transform = `translateY(${y.toFixed(1)}px) scale(${applied.toFixed(4)})`;
  pill.style.transform = `translateY(${(y - ((applied - 1) * metrics.height) / 2).toFixed(1)}px)`;
  for (const [el, from, to] of groups) arrive(el, easeOut(segment(progress, from, to)));
  if (progress > 0.58) count();
  cueRef.current?.style.setProperty('--cue', (1 - segment(progress, 0, 0.08)).toFixed(3));
};
```

**The sheet that slides over the hero.** After the story, `--hp` runs 0..1 as the next section slides over the still-pinned hero:

```ts
useScrollVar(sectionRef, '--hp', (element) =>
  modeRef.current === 'full' ? (window.scrollY - storyLength.current) / Math.max(1, element.offsetHeight) : 0
);
```

The hero content uses it in CSS:

```tsx
// hero content block
style={{
  transform: 'translateY(calc(var(--hp, 0) * 70px)) scale(calc(1 - var(--hp, 0) * 0.07))',
  opacity: 'calc(1 - var(--hp, 0) * 0.85)'
}}
// background glows (parallax, also mouse depth)
style={{ transform: 'translate(calc(var(--mx, 0) * -18px), calc(var(--my, 0) * -14px + var(--hp, 0) * 160px))' }}
// stars layer
style={{ transform: 'translate(calc(var(--mx, 0) * 10px), calc(var(--my, 0) * 8px + var(--hp, 0) * -90px))' }}
// scroll cue
style={{ opacity: 'calc(min(var(--cue, 1), 1 - var(--hp, 0) * 4))' }}
```

The sheet itself, in `src/pages/HomePage.tsx`:

```tsx
{/* Everything below slides up over the pinned hero like a sheet of glass. */}
<div className="relative z-10 bg-page sheet-shadow lg:overflow-hidden lg:rounded-t-[36px]">
```

```css
.sheet-shadow { box-shadow: 0 -30px 70px -20px rgb(0 0 0 / 0.55); }
html.light .sheet-shadow { box-shadow: 0 -18px 40px -24px rgb(15 27 51 / 0.18); }
```

**Phones and tablets (`compact`).** Only the top block is pinned:

- It uses `position: sticky` with `top = max(84, round((innerHeight - topBlockHeight) / 2))`.
- The spacer is `COMPACT_SCREENS * 100` vh (110 vh).
- Progress is `scrollY / (innerHeight * 1.1)`.

The steps:

- **Big stacked name:** moves and scales to the real name over **0 → 0.42** (`easeInOut`). It fades and blurs (to 8 px) during n 0.35 → 0.75.
- **Real name:** rises out of a mask over **0.19 → 0.36** (`easeOut`, `translateY(110% → 0)`).
- **Title, line and buttons** arrive over **0.46–0.66**, **0.54–0.74** and **0.64–0.88**.
- **Stats and skill cards** are not scroll-driven. They rise in when visible: IntersectionObserver with `rootMargin: '0px 0px -12% 0px', threshold: 0.2`, then transition `opacity 0.9s ease, transform 0.9s cubic-bezier(0.2, 0.7, 0.2, 1), filter 0.9s ease`. Cards stagger by `90 * (index % 2)` ms.
- **Resize:** the address bar hiding on phones triggers resize events, so it only re-measures on real width changes (more than 2 px).

**Mouse depth (desktop only).** Stars and glows drift a few pixels toward the cursor:

```ts
// --mx/--my run from -1 to 1, eased 0.06 per frame toward the cursor
p.x += (p.tx - p.x) * 0.06;
p.y += (p.ty - p.y) * 0.06;
// settles when within 0.002; returns to 0,0 on pointer leave
// ignored unless pointerType === 'mouse' && hasFinePointer() && !prefersReducedMotion()
```

### 3b. Websites page: pinned 3D laptop story (`src/components/websites/WebsitesStory.tsx`)

An Apple-product-page style story. A CSS 3D laptop:

- rises,
- opens,
- then carries one site at a time, with **8 different moves** between sites.

**Pinning:**

```tsx
<section className="story relative bg-background-dark"
  style={{ height: `calc(100svh + ${110 + 70 + (n - 1) * 90}vh)` }}>
  <div className="story-stage sticky top-0 h-[100svh] overflow-hidden"> …
```

Scroll budget: intro 110 vh, then 90 vh per site, then a 70 vh tail.

```ts
const geometry = () => {
  const vh = window.innerHeight;
  const intro = vh * 1.1;
  const tail = vh * 0.7;
  const range = section.offsetHeight - vh;
  const per = Math.max(1, (range - intro - tail) / Math.max(1, n - 1));
  return { vh, intro, per, tail };
};
```

**Its own inertia layer**, on top of the global smooth scroll. The story glides after the scroll position:

```ts
// Inertia: the story glides after the scroll instead of stepping with each
// wheel notch. About a tenth of a second to settle.
const dt = lastTime ? Math.min(64, time - lastTime) : 16.7;
lastTime = time;
if (current === null) current = target;
current += (target - current) * (1 - Math.pow(1 - 0.16, dt / 16.7));   // lerp 0.16
if (Math.abs(target - current) < 0.3) current = target;
```

**Holding on each site:**

```ts
const smooth = (t: number) => t * t * (3 - 2 * t);       // smoothstep
const f = clamp((scrolled - intro) / per, 0, n - 1);
const base = Math.floor(f);
const frac = f - base;
const t = smooth(clamp((frac - 0.45) / 0.55));          // hold for the first 45% of each site's stretch, then move
```

**Moves, in order (they repeat):**

```ts
const MOVES = ['swing', 'spin', 'dive', 'overhead', 'drop', 'bank', 'away', 'lid'] as const;
const CUTS = new Set<string>(['spin', 'overhead', 'drop', 'lid']);   // screen swaps while hidden
// bump = Math.sin(Math.PI * t)
// swing:    y -= bump*vh*0.035; s *= 1 - bump*0.05
// spin:     ry += 360*t; y -= bump*vh*0.03; s *= 1 - bump*0.14
// dive:     s *= 1 + bump*(wide ? 0.85 : 0.3); x *= 1-bump; rx,ry -> 0
// overhead: rx -> -80 at bump; y += bump*vh*0.05; s *= 1 - bump*0.08
// drop:     y += bump^0.8 * vh*0.95; x crosses over at t 0.35..0.65
// bank:     rz = ±bump*(wide ? 12 : 7)deg; y -= bump*vh*0.06
// away:     s *= 1 - bump*0.55; y -= bump*vh*0.08; ry += bump*35*side
// lid:      lid -> -90 at bump*1.25; rx -> -32; y += bump*vh*0.03
```

**Resting pose per site (index order, repeats):**

```ts
const HOLDS = [
  { ry: 17, rx: -9, s: 1, dy: 0, lid: 12 },
  { ry: 22, rx: -4, s: 0.96, dy: 0.03, lid: 14 },
  { ry: 12, rx: -12, s: 1.05, dy: -0.01, lid: 10 },
  { ry: 15, rx: -17, s: 0.94, dy: 0.01, lid: 16 },
  { ry: 23, rx: -7, s: 1, dy: 0, lid: 8 },
  { ry: 12, rx: -10, s: 1.04, dy: -0.01, lid: 12 },
  { ry: 19, rx: -4, s: 1.02, dy: 0.02, lid: 12 },
  { ry: 16, rx: -13, s: 0.95, dy: 0, lid: 14 },
  { ry: 14, rx: -8, s: 1, dy: -0.01, lid: 12 }
];
// wide (>=1024px): laptop alternates sides at x = ±0.17·vw, y = vh*(dy - 0.09)
// phones: x = 0, y = vh*(dy*0.5 - 0.17), scale change halved, ry × 0.55
// start pose: { y: vh*(wide?0.2:0.14), s: wide?0.58:0.66, rx: -62, lid: -90 (closed) }
// end pose:   { y: vh*(wide?0:-0.1),  s: wide?0.78:0.82, rx: -24, lid: -62 }
```

**Performance rules this file follows.** These came out of a smoothness pass that cut style recalculation from 2.1 s to 0.15 s over a test scroll:

- Write each element's own `style` directly, never a CSS variable on a big subtree.
- Write only when a value changed (a `WeakMap` cache of last values).
- Read sizes once per resize, never in the middle of a frame's writes.
- No `filter: blur()` glows. Brand glows are layered `radial-gradient` with `color-mix`.
- `img.decode()` every screenshot up front.
- Perspective: `2400px` with origin `50% 40%`, plus `transform-style: preserve-3d`.
- `.story-stage { contain: paint; }`

**The rail buttons** jump with native smooth scrolling:

```ts
window.scrollTo({ top: top + intro + per * i + 2, behavior: 'smooth' });
```

---

## 4. CSS that affects the scroll feel: `src/index.css`

```css
@layer base {
  html {
    scroll-behavior: smooth;   /* used by anchor/hash links and the story rail; the wheel glide overrides with behavior:'instant' */
  }
  body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background-color: rgb(var(--c-page));
    color: rgb(var(--c-ink));
  }
}

/* Header height, shared by every page's top spacing (Header.tsx). */
:root { --header-h: 70px; }
@media (max-width: 767px) { :root { --header-h: 105px; } }   /* phones show a second row of page links */
@media (max-width: 339px) { :root { --header-h: 64px; } }    /* tiny phones: menu button only */

.hero-clip {
  overflow: hidden;
  overflow: clip; /* clips like hidden, but still lets the top of the hero stay pinned on phones */
}

.no-scrollbar { scrollbar-width: none; }
.no-scrollbar::-webkit-scrollbar { display: none; }
```

**Not set anywhere (browser defaults):**

- `overscroll-behavior`
- `html`/`body` height
- `scroll-snap`
- `scroll-padding-top`

Anchor offset under the fixed header is handled by each page using `pt-[var(--header-h)]` padding.

**Routing scroll** (custom router, `src/lib/router.ts`):

- **New page:** jump to the top instantly (`window.scrollTo(0, 0)`).
- **`#hash` present:** `scrollIntoView({ behavior: 'smooth' })` on the next frame.
- **Same-page link:** smooth scroll to the hash, or smooth to the top.

```ts
const scrollToHash = (hash: string) => {
  const target = hash ? document.getElementById(decodeURIComponent(hash.slice(1))) : null;
  if (target) { target.scrollIntoView({ behavior: 'smooth' }); return true; }
  return false;
};
// same page:  if (!scrollToHash(url.hash)) window.scrollTo({ top: 0, behavior: 'smooth' });
export const useScrollOnRouteChange = (path: string) => {
  useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
      requestAnimationFrame(() => { if (!scrollToHash(hash)) window.scrollTo(0, 0); });
    } else {
      window.scrollTo(0, 0);
    }
  }, [path]);
};
```

---

## 5. Reduced motion and touch

**Reduced motion (`prefers-reduced-motion: reduce`):**

- `startSmoothScroll` is not started.
- `useScrollVar` does nothing, so CSS fallbacks like `var(--hp, 0)` apply.
- The hero mode is `'off'`: the static layout with no pinning.
- `CountUp` shows final numbers.
- The Websites page shows a still hero instead of the laptop story.
- Mouse depth and tilt are off.
- CSS:

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  .intro, .intro-name { animation: none !important; }
  .reveal.reveal-grow { transform: none; }
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}
```

**Touch and phones:**

- Smooth scroll requires `(hover: hover) and (pointer: fine)`, so **touch scrolling is 100% native**. There is no `syncTouch` equivalent.
- Card spotlight, tilt and hero mouse depth are mouse-only.
- The hero uses `compact` mode below 1024 px wide or 600 px tall.
- The laptop story uses centred poses and smaller turns on phones.
- The Websites laptop story pins with `100svh` (the small viewport, which stays stable when the address bar hides). The Home hero uses `min-h-screen` (`100vh`) and measures `window.innerHeight` in JS. It ignores height-only resizes on phones, so the address bar showing or hiding doesn't make it jump.

---

## 6. Reveal and entrance motion

### Section reveal: `src/components/Reveal.tsx`

```tsx
const observer = new IntersectionObserver(
  ([entry]) => {
    if (entry.isIntersecting) { setVisible(true); observer.disconnect(); }   // once only
  },
  { threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
);
// <div className={`reveal ${visible ? 'is-visible' : ''}`} style={delay ? { transitionDelay: `${delay}ms` } : undefined}>
```

```css
.reveal {
  opacity: 0;
  transform: translateY(60px) scale(0.98);
  transition: opacity 0.9s cubic-bezier(0.2, 0.7, 0.2, 1), transform 0.9s cubic-bezier(0.2, 0.7, 0.2, 1);
}
.reveal.is-visible { opacity: 1; transform: none; }

/* Call-to-action card grows into place. */
.reveal.reveal-grow { transform: scale(0.92); }
.reveal.reveal-grow.is-visible { transform: none; }
```

Typical staggers in use:

- `delay={i * 80}` for decision cards on case studies.
- `delay={i * 100}` for gallery shots.
- `delay={120}` for the right-hand column of the Websites grid.

### Page-load entrances

```css
/* Hero entrance: each piece rises out of a soft blur, in order (--d sets the wait). */
@keyframes intro {
  from { opacity: 0; transform: translateY(28px); filter: blur(8px); }
  to   { opacity: 1; transform: none; filter: blur(0); }
}
.intro { animation: intro 1s cubic-bezier(0.2, 0.7, 0.2, 1) backwards; animation-delay: var(--d, 0ms); }

/* The name rises up from behind an invisible edge. */
@keyframes intro-name {
  from { transform: translateY(110%); letter-spacing: 0.06em; filter: blur(6px); }
  to   { transform: none; letter-spacing: normal; filter: blur(0); }
}
.intro-mask { overflow: hidden; padding: 0 0.25em 0.15em; margin-bottom: -0.15em; }
.intro-name { animation: intro-name 1.2s cubic-bezier(0.16, 1, 0.3, 1) backwards; animation-delay: var(--d, 0ms); }

/* Hero story (large screens): scroll drives these groups instead of the load entrance. */
.hero-story .stage, .hero-story .stage .intro { animation: none !important; }

/* Page titles on inner pages (Websites, detail pages, case studies) */
@keyframes rise { from { opacity: 0; transform: translateY(80px); } to { opacity: 1; transform: none; } }
.animate-rise      { animation: rise 1.1s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
.animate-rise-late { animation: rise 1.1s 0.25s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
```

### Ambient motion

```css
@keyframes twinkle { 0%,100% { opacity: .2; transform: scale(1); } 50% { opacity: 1; transform: scale(1.2); } }
.animate-twinkle { animation: twinkle ease-in-out infinite; }   /* per-star duration 2–5 s, delay 0–3 s (random) */

@keyframes scroll { 0% { transform: translateY(0); } 30% { transform: translateY(8px); } 60% { transform: translateY(0); } }
.animate-scroll { animation: scroll 2s ease-in-out infinite; }   /* the mouse-icon scroll cue */

@keyframes breathe { from { transform: scale(1); opacity: .75; } to { transform: scale(1.25); opacity: 1; } }
.animate-breathe      { animation: breathe 6s ease-in-out infinite alternate; }
.animate-breathe-late { animation: breathe 7s 1.5s ease-in-out infinite alternate; }

@keyframes marquee { to { transform: translateX(-50%); } }
.animate-marquee { animation: marquee 38s linear infinite; }   /* outlined type band on Websites */
```

### Interaction motion

- **Count-up** (`CountUp.tsx`): 1400 ms, ease-out quart `1 - (1 - t)^4`. It counts once, when its stats come into view.
- **Tilt** (`Tilt.tsx`, desktop only):
  - max 4°, `perspective(1000px)`;
  - follows the cursor with `transform 0.15s ease-out`;
  - returns with `transform 0.6s cubic-bezier(0.2, 0.7, 0.2, 1)`.
- **Card spotlight:** a thin cyan light on a card's border follows the cursor (`--sx`/`--sy` set on `pointermove`). It fades in over `opacity 0.35s ease`. Only with `(hover: hover) and (pointer: fine)`.

  ```css
  .spotlight::before {
    content: ''; position: absolute; inset: 0; z-index: 2; border-radius: inherit; padding: 1px;
    background: radial-gradient(260px circle at var(--sx, 50%) var(--sy, 0%),
      rgb(var(--c-accent) / 0.9), rgb(var(--c-accent-2) / 0.35) 40%, transparent 70%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask: linear-gradient(#000 0 0) content-box exclude, linear-gradient(#000 0 0);
    opacity: 0; transition: opacity 0.35s ease; pointer-events: none;
  }
  ```

- **Scroll-lit text** (`ScrollText.tsx`): words light up one after another as the paragraph crosses the screen.

  ```ts
  useScrollVar(ref, '--read', (el) => (innerHeight * 0.85 - el.getBoundingClientRect().top) / (innerHeight * 0.5));
  // each word: opacity: clamp(0.22, calc(var(--read, 1) * (total + 4) - n), 1); transition-opacity 300ms
  ```

- **Hover lifts (Tailwind):**
  - Project cards: `hover:-translate-y-1 transition-all duration-300`, image `group-hover:scale-110 duration-500`.
  - Website tiles: `group-hover:-translate-y-1.5 group-hover:scale-[1.04] duration-700 ease-out`.
  - Buttons: `hover:-translate-y-0.5`.
- **Scroll story text** on Websites: an incoming site's words slide from `translateY(d * 60px)`. Screens slide in from 100% below, and the outgoing one drifts up 28% and dims to 0.75.

---

## 7. Other things about the site that matter for matching its feel

- **Stack:**
  - React 18.3 + TypeScript + Vite 5 + Tailwind 3.4;
  - lucide-react icons;
  - its own tiny History-API router;
  - hosted on Vercel Hobby, with an SPA rewrite in `vercel.json`;
  - no CMS or backend.
- **Theme:** dark by default, plus a real light theme (`html.light`), saved in `localStorage` and applied before first paint.
- **Font:** Inter 300–900 from Google Fonts. Large display type uses `font-black` with tight tracking (`letter-spacing: -0.04em` to `-0.05em`), sized with `clamp()`. Examples:
  - `clamp(76px, 16.5vw, 228px)` for the Websites title;
  - `clamp(38px, 6vw, 72px)` for case-study titles.
- **Colour tokens** (dark), in RGB channels so Tailwind's `/opacity` works:

  ```css
  --c-page: 3 7 18;          /* #030712 page */
  --c-section: 17 24 39;     /* #111827 */
  --c-deep: 10 10 10;        /* #0a0a0a hero/header */
  --c-card: 31 41 55;        /* #1f2937, used at /30–/50 as glass */
  --c-glass: 10 15 31;       /* #0A0F1F */
  --c-line: 55 65 81;        /* #374151 borders */
  --c-ink: 255 255 255;
  --c-body: 209 213 219;
  --c-muted: 156 163 175;
  --c-subtle: 107 114 128;
  --c-accent: 0 216 255;     /* #00d8ff the cyan */
  --c-accent-2: 0 123 255;   /* #007bff the blue */
  --c-violet: 108 99 255;    /* #6c63ff */
  --c-signal: 16 185 129;    /* green for live/verified */
  /* gradient: linear-gradient(90deg, #00d8ff, #007bff) */
  ```

- **Visual language:**
  - glass cards: `bg-card/30 backdrop-blur-sm border border-line rounded-xl/2xl`;
  - cyan-to-blue gradient for headings and primary buttons;
  - big soft blurred glows behind heroes;
  - gradient headings with a short gradient bar underneath (`w-24 h-1`);
  - pill buttons with a cyan glow shadow `0 10px 34px rgba(0,216,255,0.28–0.32)`.
- **Pages:**
  - Home: pinned hero story, then a sheet slides over with featured work and a CTA.
  - Websites: pinned 3D laptop story, then the gallery.
  - `/websites/:slug` detail pages.
  - Projects: filter and search.
  - `/projects/:slug` case studies, with inline SVG diagrams.
  - About, Contact, 404.
- **Header:** fixed. On phones from 340 px wide, the five page links are a second row instead of a hamburger menu.
- **Franklin's taste notes** (from the redesign log):
  - **Likes:** Apple's AirPods Pro page (a pinned product that moves with the scroll), Igloo Inc (dark, icy mood), Cuberto, Find Real Estate.
  - **Wants variety between scroll moves, not repetition.** That is why the laptop has 8 different moves.
  - **Dislikes:** Locomotive-style scroll and cursor-chasing effects. A big cursor glow was removed and replaced with the quiet mouse depth above.
  - Metalab felt "too smart for a normal user"; Dennis Snellenberg was too minimal and white.
  - No placeholders, nothing that looks templated or AI-generated, restrained gradients.
  - Honest content: no invented testimonials or claims.

---

## 8. Where to read the full source

| What | File in FranklinMburu/my-portfolio |
|---|---|
| Smooth scroll, spotlight, `useScrollVar` | `src/lib/motion.ts` |
| Started in | `src/App.tsx` |
| Home hero story | `src/components/Hero.tsx` |
| Sheet over hero | `src/pages/HomePage.tsx` |
| Websites laptop story | `src/components/websites/WebsitesStory.tsx` |
| Reveal on scroll | `src/components/Reveal.tsx` |
| Count-up, tilt, scroll-lit text | `src/components/motion/` |
| All motion CSS and tokens | `src/index.css` |
| Router scrolling | `src/lib/router.ts` |
