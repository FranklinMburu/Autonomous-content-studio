// Smooth scroll for the landing site (not inside the app panel). Lenis, MIT, ~4 KB. Version: "lenis": "^1.3.0".
// Feel: weighty and calm (Apple / Stripe), never floaty. Respects reduced motion (Lenis does nothing then).
import Lenis from "lenis";

export function startSmoothScroll(onScroll) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    addEventListener("scroll", () => onScroll && onScroll(scrollY), { passive: true });
    return null;
  }
  const lenis = new Lenis({
    lerp: 0.085,            // approved feel: lower = smoother; do not go below 0.07 or above 0.12
    wheelMultiplier: 0.9,
    smoothWheel: true,
    syncTouch: false,       // phones keep native momentum scrolling (feels right, costs nothing)
  });
  lenis.on("scroll", ({ scroll }) => onScroll && onScroll(scroll));
  const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
  return lenis;
}
// Inside the app panel (section 2) add the attribute data-lenis-prevent on the panel's scroll areas,
// so scrolling inside the demo app scrolls the app, not the page.
