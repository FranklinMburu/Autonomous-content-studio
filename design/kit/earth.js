// Candela hero globe: a dotted Earth lit by a sun rising over its rim. Canvas 2D only (no WebGL, no three.js).
// This is the same drawing as the approved mockups (design/reference/pages/02_landing_hero.html), split into two
// layers for speed and driven by scroll. Plain ES module: works in React/TS (`import { createEarth } from './earth.js'`).
//
//   const { stories, arcs } = buildGlobe(films, topics, places);      // kit/github-data.js (real data)
//   const earth = createEarth(canvas, data, stories, { arcs, onPlace }); // data = await (await fetch('/earth.json')).json()
//   earth.setProgress(p)    // p = 0 at the top of the page, 1 when the hero has scrolled away (sun rises)
//   earth.destroy()
//
// Layout constants are for a 1440 x 900 hero and scale with the canvas width (see `geom`).

// No built-in places: pass the real ones from github-data.js buildGlobe() -> { stories, arcs }.
// story = { n: "London", y: 1854, lat, lon, kind: "made" | "queued", card?: "left" | "right" }

// Approved values (do not change): top of page -> scrolled
const SUN_FROM = -0.55, SUN_TO = 0.12;   // angle on the rim, radians from the top (+ = right)
const RISE_FROM = 0.8, RISE_TO = 1.0;    // sun strength
const LON_FROM = -10, LON_TO = -6;        // the globe turns 4 degrees east while you scroll
const LAT0 = -6;

const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => 1 - Math.pow(1 - t, 3);

export function geom(W, H) {   // 1440x900 reference: R 860, centre (720, 1370)
  const k = W / 1440;
  if (W < 640) return { R: 520, cx: W * 0.423, cy: H + 160, k: 0.6 };   // phone: same framing as 12_mobile (globe top ~H-360)
  return { R: 860 * k, cx: 720 * k, cy: 1370 * k + (H - 900 * k) * 0.5, k };
}

export function createEarth(canvas, data, stories = [], opts = {}) {
  const ARCS = opts.arcs || [];
  const dpr = Math.min(window.devicePixelRatio || 1, opts.maxDpr || 2);
  // cached layers: dots are drawn once per few degrees of turn, never per frame
  const dots = document.createElement("canvas");    // all land/ocean dots, cool silver
  const lit = document.createElement("canvas");     // the same dots, warm and bright (shown only near the sun)
  const scratch = document.createElement("canvas"); // lit dots masked to the sun's glow
  let W = 0, H = 0, g, lastLon = null, progress = 0, raf = 0, step = opts.step || 1;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function size() {
    W = canvas.clientWidth; H = canvas.clientHeight;
    for (const c of [canvas, dots, lit, scratch]) { c.width = W * dpr; c.height = H * dpr; }
    g = geom(W, H); lastLon = null;
    // phones keep every dot (R is smaller, cost is fine); pass { step: 2 } only if the fps watchdog asks for it
  }

  function projector(lon0) {
    const la0 = LAT0 * Math.PI / 180, lo0 = lon0 * Math.PI / 180, { R, cx, cy } = g;
    return (lat, lon) => {
      lat *= Math.PI / 180; lon *= Math.PI / 180; const d = lon - lo0;
      const x = Math.cos(lat) * Math.sin(d), y = Math.cos(la0) * Math.sin(lat) - Math.sin(la0) * Math.cos(lat) * Math.cos(d);
      const z = Math.sin(la0) * Math.sin(lat) + Math.cos(la0) * Math.cos(lat) * Math.cos(d);
      return [cx + R * x, cy - R * y, z];
    };
  }

  function drawDots(P) {
    const c = dots.getContext("2d"), l = lit.getContext("2d");
    for (const x of [c, l]) { x.setTransform(dpr, 0, 0, dpr, 0, 0); x.clearRect(0, 0, W, H); }
    c.fillStyle = "rgb(190,195,210)";
    for (let i = 0; i < data.ocean.length; i += 2 * step) {
      const p = P(data.ocean[i], data.ocean[i + 1]); if (p[2] < 0.02) continue;
      c.globalAlpha = 0.08 * p[2]; c.fillRect(p[0] - 0.6, p[1] - 0.6, 1.2, 1.2);
    }
    c.fillStyle = "rgb(200,206,222)"; l.fillStyle = "rgb(255,236,202)";
    for (let i = 0; i < data.land.length; i += 2 * step) {
      const p = P(data.land[i], data.land[i + 1]); if (p[2] < 0.02 || p[1] > H + 4) continue;
      const d = Math.min(1, p[2] * 2.4), s = (1.05 + 0.6 * p[2]) * (step > 1 ? 1.1 : 1);
      c.globalAlpha = 0.34 * d; c.fillRect(p[0] - s / 2, p[1] - s / 2, s, s);
      l.globalAlpha = 0.96 * d; l.fillRect(p[0] - s / 2, p[1] - s / 2, s, s);
    }
    c.globalAlpha = 1; l.globalAlpha = 1;
  }

  function frame() {
    raf = 0;
    const t = reduce ? 0 : ease(progress);
    const sa = lerp(SUN_FROM, SUN_TO, t), rise = lerp(RISE_FROM, RISE_TO, t), lon0 = lerp(LON_FROM, LON_TO, t);
    const { R, cx, cy } = g, sx = cx + R * Math.sin(sa), sy = cy - R * Math.cos(sa), P = projector(lon0);
    if (lastLon === null || Math.abs(lon0 - lastLon) > 0.5) { drawDots(P); lastLon = lon0; }
    const c = canvas.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, W, H);
    // sky glow from behind the rim
    let gr = c.createRadialGradient(sx, sy, 0, sx, sy, R * 1.1);
    gr.addColorStop(0, `rgba(255,214,150,${0.34 * rise})`); gr.addColorStop(0.18, `rgba(245,165,36,${0.16 * rise})`);
    gr.addColorStop(0.5, `rgba(140,90,60,${0.06 * rise})`); gr.addColorStop(1, "rgba(0,0,0,0)");
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    // atmosphere: one smooth silver haze ring + a crisp rim that turns gold near the sun (no blur filter: it is slow)
    const ring = c.createRadialGradient(cx, cy, R - 2, cx, cy, R + 46);
    ring.addColorStop(0, "rgba(205,210,228,.30)"); ring.addColorStop(0.1, "rgba(190,198,222,.16)");
    ring.addColorStop(0.4, "rgba(170,180,210,.05)"); ring.addColorStop(1, "rgba(160,170,200,0)");
    c.fillStyle = ring; c.beginPath(); c.arc(cx, cy, R + 46, 0, 7); c.fill();
    for (const [w, al] of [[5, 0.22], [1.6, 0.6]]) {
      const cg = c.createConicGradient(-Math.PI / 2 + sa - Math.PI, cx, cy);
      cg.addColorStop(0, `rgba(150,160,190,${al * 0.35})`); cg.addColorStop(0.38, `rgba(170,180,210,${al * 0.6})`);
      cg.addColorStop(0.5, `rgba(255,226,170,${al * (0.6 + rise)})`); cg.addColorStop(0.62, `rgba(170,180,210,${al * 0.6})`);
      cg.addColorStop(1, `rgba(150,160,190,${al * 0.35})`);
      c.strokeStyle = cg; c.lineWidth = w; c.beginPath(); c.arc(cx, cy, R + w / 2 - 1, 0, 7); c.stroke();
    }
    // planet body
    gr = c.createRadialGradient(sx, sy, R * 0.05, cx, cy, R * 1.1);
    gr.addColorStop(0, "#2A2420"); gr.addColorStop(0.35, "#15151A"); gr.addColorStop(1, "#0B0B0F");
    c.fillStyle = gr; c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
    // the sun peeking over the rim + faint lens streak
    gr = c.createRadialGradient(sx, sy, 0, sx, sy, 90);
    gr.addColorStop(0, `rgba(255,250,235,${0.95 * rise})`); gr.addColorStop(0.12, `rgba(255,220,160,${0.7 * rise})`); gr.addColorStop(1, "rgba(245,165,36,0)");
    c.fillStyle = gr; c.beginPath(); c.arc(sx, sy, 90, 0, 7); c.fill();
    c.fillStyle = `rgba(255,236,200,${0.18 * rise})`; c.fillRect(sx - 260, sy - 0.6, 520, 1.2);
    // dots: cool layer everywhere, warm layer only inside the sun's glow
    const m = scratch.getContext("2d"); m.setTransform(1, 0, 0, 1, 0, 0); m.globalCompositeOperation = "copy"; m.drawImage(lit, 0, 0);
    m.globalCompositeOperation = "destination-in"; m.setTransform(dpr, 0, 0, dpr, 0, 0);
    const mg = m.createRadialGradient(sx, sy, 0, sx, sy, R * 1.15); mg.addColorStop(0, "rgba(0,0,0,1)"); mg.addColorStop(1, "rgba(0,0,0,0)");
    m.fillStyle = mg; m.fillRect(0, 0, W, H); m.globalCompositeOperation = "source-over";
    c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(dots, 0, 0); c.drawImage(scratch, 0, 0); c.setTransform(dpr, 0, 0, dpr, 0, 0);
    // arcs between story places
    const by = n => stories.find(s => s.n === n);
    for (const [a, b, h] of ARCS) {
      if (!by(a) || !by(b)) continue;
      const A = P(by(a).lat, by(a).lon), B = P(by(b).lat, by(b).lon); if (A[2] < 0.05 || B[2] < 0.05) continue;
      const mx = (A[0] + B[0]) / 2, my = (A[1] + B[1]) / 2 - h * g.k;
      const lg = c.createLinearGradient(A[0], A[1], B[0], B[1]);
      lg.addColorStop(0, "rgba(255,200,97,0)"); lg.addColorStop(0.5, "rgba(255,200,97,.75)"); lg.addColorStop(1, "rgba(255,200,97,.05)");
      c.strokeStyle = lg; c.lineWidth = 1.3; c.beginPath(); c.moveTo(A[0], A[1]); c.quadraticCurveTo(mx, my, B[0], B[1]); c.stroke();
      const q = 0.62, qx = (1 - q) ** 2 * A[0] + 2 * (1 - q) * q * mx + q * q * B[0], qy = (1 - q) ** 2 * A[1] + 2 * (1 - q) * q * my + q * q * B[1];
      const pg = c.createRadialGradient(qx, qy, 0, qx, qy, 9); pg.addColorStop(0, "rgba(255,220,150,1)"); pg.addColorStop(1, "rgba(255,200,97,0)");
      c.fillStyle = pg; c.beginPath(); c.arc(qx, qy, 9, 0, 7); c.fill();
    }
    // story lights; report screen positions so the page can place the cards and name tags (HTML, not canvas)
    const places = [];
    for (const s of stories) {
      const p = P(s.lat, s.lon); if (p[2] < 0.05) continue;
      const madeOne = s.kind !== "queued", big = madeOne, r = madeOne ? 26 : 12, q = madeOne ? 1 : 0.55;
      const sg = c.createRadialGradient(p[0], p[1], 0, p[0], p[1], r);
      sg.addColorStop(0, `rgba(255,214,140,${0.95 * q})`); sg.addColorStop(0.25, `rgba(245,165,36,${0.45 * q})`); sg.addColorStop(1, "rgba(245,165,36,0)");
      c.fillStyle = sg; c.beginPath(); c.arc(p[0], p[1], r, 0, 7); c.fill();
      c.fillStyle = madeOne ? "#FFF4DD" : "rgba(255,244,221,.75)"; c.beginPath(); c.arc(p[0], p[1], madeOne ? 2.6 : 1.6, 0, 7); c.fill();
      if (big) { c.strokeStyle = "rgba(255,200,97,.35)"; c.lineWidth = 1; c.beginPath(); c.arc(p[0], p[1], 9, 0, 7); c.stroke(); }
      places.push({ ...s, year: s.y, x: p[0], y: p[1] });
    }
    // fade the bottom into the page
    gr = c.createLinearGradient(0, H - 200, 0, H); gr.addColorStop(0, "rgba(11,11,15,0)"); gr.addColorStop(1, "rgba(11,11,15,1)");
    c.fillStyle = gr; c.fillRect(0, H - 200, W, 200);
    opts.onPlace && opts.onPlace(places);
  }

  const request = () => { if (!raf) raf = requestAnimationFrame(frame); };
  const ro = new ResizeObserver(() => { size(); request(); }); ro.observe(canvas);
  size(); request();
  return {
    setProgress(p) { const v = Math.max(0, Math.min(1, p)); if (Math.abs(v - progress) > 0.002) { progress = v; request(); } },
    destroy() { ro.disconnect(); cancelAnimationFrame(raf); },
  };
}

// Name tags without collisions: made films first, then queued topics in queue order; a tag whose box would overlap
// an earlier tag (or a card) is skipped (its light stays). Returns the tags to show with their left/top in px.
//   pickTags(places, { blocked: [cardRects], maxY: 820, width: W })
export function pickTags(places, { blocked = [], maxY = 820, width = 1440, font = 6.4 } = {}) {
  // every light is an obstacle too, so a tag never sits on another city's light
  const taken = blocked.slice(), out = [];
  const lights = places.map(p => ({ l: p.x - 8, t: p.y - 8, r: p.x + 8, b: p.y + 8, n: p.n }));
  const order = places.filter(p => !p.card).sort((a, b) => (a.kind === "queued") - (b.kind === "queued"));
  for (const p of order) {
    if (p.y > maxY || p.y < 0) continue;
    const w = (p.n.length + String(p.year || "").length + 1) * font + 6, h = 16;
    const left = p.x > width - w - 24 ? p.x - 12 - w : p.x + 12, top = p.y - 9;
    const box = { l: left - 4, t: top - 3, r: left + w + 4, b: top + h + 3 };
    const hit = o => !(box.r < o.l || box.l > o.r || box.b < o.t || box.t > o.b);
    if (taken.some(hit) || lights.some(o => o.n !== p.n && hit(o))) continue;
    taken.push(box); out.push({ ...p, left, top });
  }
  return out;
}
