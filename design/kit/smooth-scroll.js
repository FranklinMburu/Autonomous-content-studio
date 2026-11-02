// Candela scroll and motion feel = Franklin's portfolio (FranklinMburu/my-portfolio @125a257, src/lib/motion.ts),
// copied value for value. No library: no Lenis, no GSAP, no framer-motion. Full notes: design/reference/portfolio-scroll.md
//
//   const stop = startSmoothScroll();      // once, on app mount; returns a cleanup
//   const off = scrollVar(el, "--hp", el => ...0..1...);   // scroll-linked CSS variable, one write per frame
//   reveal(el, { delay })                  // section reveal (also see the .reveal CSS below)
//
// Feel: the wheel glides toward its target with lerp 0.1 per 60 fps frame (frame-time corrected). Mouse wheel and
// trackpad only: touch, keyboard, scrollbar and links stay native. Off for reduced motion and on touch-only devices.

export const EASE = "cubic-bezier(0.2, 0.7, 0.2, 1)";   // the house curve: reveals, entrances, tilt return

export const prefersReducedMotion = () =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export const hasFinePointer = () =>
  typeof window !== "undefined" && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));

/** True when the wheel event should scroll an inner scrollable box (e.g. the live studio panel) instead of the page. */
const scrollsInside = (target, deltaY) => {
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

  const tick = (time) => {
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
    window.scrollTo({ top: current, behavior: "instant" });
    lastWritten = window.scrollY;
    frame = current === target ? 0 : requestAnimationFrame(tick);
  };

  const onWheel = (event) => {
    if (event.defaultPrevented || event.ctrlKey || event.metaKey) return;
    if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (document.body.style.overflow === "hidden") return;      // a dialog / ⌘K palette / mobile menu is open
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

  window.addEventListener("wheel", onWheel, { passive: false });
  return () => {
    window.removeEventListener("wheel", onWheel);
    cancelAnimationFrame(frame);
  };
};

/**
 * Writes a 0..1 number into a CSS variable once per animation frame (portfolio `useScrollVar`).
 * Skipped with reduced motion, so the CSS fallback value applies (e.g. var(--hp, 0)). Returns a cleanup.
 * React: call it in useEffect with ref.current.
 */
export const scrollVar = (element, name, compute) => {
  if (!element || prefersReducedMotion()) return () => undefined;
  let frame = 0;
  const update = () => { frame = 0; element.style.setProperty(name, clamp(compute(element)).toFixed(4)); };
  const request = () => { if (!frame) frame = requestAnimationFrame(update); };
  update();
  window.addEventListener("scroll", request, { passive: true });
  window.addEventListener("resize", request);
  return () => {
    window.removeEventListener("scroll", request);
    window.removeEventListener("resize", request);
    cancelAnimationFrame(frame);
  };
};

/**
 * Section reveal (portfolio Reveal.tsx): adds .is-visible once, when 12% is on screen (60 px early margin).
 * CSS (in candela.css):
 *   .reveal { opacity:0; transform:translateY(60px) scale(.98);
 *             transition: opacity .9s cubic-bezier(.2,.7,.2,1), transform .9s cubic-bezier(.2,.7,.2,1); }
 *   .reveal.is-visible { opacity:1; transform:none; }
 *   .reveal.reveal-grow { transform:scale(.92); }  .reveal.reveal-grow.is-visible { transform:none; }
 */
export const reveal = (element, { delay = 0 } = {}) => {
  if (!element) return () => undefined;
  if (prefersReducedMotion()) { element.classList.add("is-visible"); return () => undefined; }
  if (delay) element.style.transitionDelay = `${delay}ms`;
  const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) { element.classList.add("is-visible"); observer.disconnect(); }
  }, { threshold: 0.12, rootMargin: "0px 0px -60px 0px" });
  observer.observe(element);
  return () => observer.disconnect();
};

/** Count-up (portfolio CountUp.tsx): 1400 ms, ease-out quart, once. onFrame(value) writes the text. */
export const countUp = (to, onFrame, ms = 1400) => {
  if (prefersReducedMotion()) { onFrame(to); return; }
  const start = performance.now();
  const step = (t) => {
    const p = Math.min(1, (t - start) / ms);
    onFrame(Math.round(to * (1 - Math.pow(1 - p, 4))));
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};
