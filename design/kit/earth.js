// Candela hero globe v2 (6 Nov 2026): a dotted Earth lit by a sun rising over its rim. Canvas 2D only (no WebGL,
// no three.js). Approved look: design/mockups/02_landing_hero.png and 02b_landing_hero_scrolled.png.
//
// Why v2: v1 cached the dot layer and redrew it only every 0.5 degrees of turn, so while scrolling the continents moved
// in small steps under smoothly moving lights and arcs ("it feels wrong"), and dots crowded at the rim made ripple rings.
// v2 redraws every dot every frame straight into a pixel buffer (each dot is a real 3D point, lit by the real direction
// of the sun), fades dots smoothly towards the rim, and sways the globe slowly like a living planet.
//
//   const { stories, arcs } = buildGlobe(films, topics, places);        // github-data.js (real data, no seed)
//   const earth = createEarth(canvas, data, stories, { arcs, onPlace }); // data = await (await fetch('/earth.json')).json()
//   earth.setProgress(p)   // 0 at the top of the page, 1 when the hero has scrolled away (the sun rises)
//   earth.setActive(bool)  // pause when the hero is off-screen (IntersectionObserver)
//   earth.destroy()
// onPlace(places) is called every frame with [{...story, year, x, y}] (x, y in CSS px): position HTML cards and
// tags imperatively from it (do NOT put it in React state: that re-renders 60 times a second).

// Approved values: top of page -> scrolled
const SUN_FROM = -0.55, SUN_TO = 0.12;   // angle on the rim, radians from the top (+ = right)
const RISE_FROM = 0.8, RISE_TO = 1.0;    // sun strength
const LON_FROM = -10, LON_TO = -6;       // the globe turns 4 degrees east while you scroll
const LAT0 = -6;
const SWAY_DEG = 3.5, SWAY_SECONDS = 48; // living planet: a slow sway, Europe always stays in view

const lerp = (a, b, t) => a + (b - a) * t;
const ease = t => 1 - Math.pow(1 - t, 3);
const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

export function geom(W, H) {   // 1440x900 reference: R 860, centre (720, 1370)
  const k = W / 1440;
  if (W < 640) return { R: 520, cx: W * 0.423, cy: H + 160, k: 0.6 };   // phone: framing of 12_mobile
  return { R: 860 * k, cx: 720 * k, cy: 1370 * k + (H - 900 * k) * 0.5, k };
}

function unitVectors(pairs, jitterDeg = 0.14) {   // lat/lon pairs -> Float32Array x, y, z (y = north)
  // a tiny fixed jitter breaks the perfectly regular lattice, which otherwise makes ripple (moire) rings at the rim
  const n = pairs.length / 2, v = new Float32Array(n * 3);
  let seed = 7;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647 - 0.5; };
  for (let i = 0; i < n; i++) {
    const la = (pairs[2 * i] + rnd() * 2 * jitterDeg) * Math.PI / 180, lo = (pairs[2 * i + 1] + rnd() * 2 * jitterDeg) * Math.PI / 180, c = Math.cos(la);
    v[3 * i] = c * Math.sin(lo); v[3 * i + 1] = Math.sin(la); v[3 * i + 2] = c * Math.cos(lo);
  }
  return v;
}

export function createEarth(canvas, data, stories = [], opts = {}) {
  const ARCS = opts.arcs || [];
  const dpr = Math.min(window.devicePixelRatio || 1, opts.maxDpr || 2);
  const land = unitVectors(data.land), ocean = unitVectors(data.ocean, 0.8);
  const buf = document.createElement("canvas");   // the dot layer, drawn into pixels every frame
  let W = 0, H = 0, g, progress = 0, raf = 0, active = true, img = null, px = null, box = null, slow = 0;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const t0 = performance.now();

  function size() {
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g = geom(W, H);
    // only the part of the canvas the globe can cover gets a pixel buffer
    const top = Math.max(0, Math.floor((g.cy - g.R - 4) * dpr)), left = Math.max(0, Math.floor((g.cx - g.R - 4) * dpr));
    const right = Math.min(canvas.width, Math.ceil((g.cx + g.R + 4) * dpr)), bottom = canvas.height;
    box = { x: left, y: top, w: Math.max(1, right - left), h: Math.max(1, bottom - top) };
    buf.width = box.w; buf.height = box.h;
    img = buf.getContext("2d").createImageData(box.w, box.h); px = new Uint32Array(img.data.buffer);
  }

  function rotation(lonDeg) {   // world -> view: turn by -lon around north, then tilt by LAT0
    const lo = -lonDeg * Math.PI / 180, la = LAT0 * Math.PI / 180;
    const cl = Math.cos(lo), sl = Math.sin(lo), ca = Math.cos(la), sa = Math.sin(la);
    // x' = x cl + z sl ; z1 = -x sl + z cl ; then y'' = y ca - z1 sa ; z'' = y sa + z1 ca
    return (x, y, z) => { const xr = x * cl + z * sl, z1 = -x * sl + z * cl; return [xr, y * ca - z1 * sa, y * sa + z1 * ca]; };
  }

  function dots(rot, sun, rise) {
    px.fill(0);
    const { R, cx, cy } = g, s = dpr, ox = box.x, oy = box.y, bw = box.w, bh = box.h;
    const plot = (vx, vy, vz, size, r, gg, b, a) => {   // one square dot, keep the brighter one where dots overlap
      const X = Math.round((cx + R * vx) * s - ox - size / 2), Y = Math.round((cy - R * vy) * s - oy - size / 2);
      if (X < 0 || Y < 0 || X + size > bw || Y + size > bh) return;
      const A = Math.round(a * 255), col = (A << 24) | (b << 16) | (gg << 8) | r;
      for (let j = 0; j < size; j++) { let k = (Y + j) * bw + X; for (let i = 0; i < size; i++, k++) if ((px[k] >>> 24) < A) px[k] = col; }
    };
    // ocean: a few faint scattered dots, only on the face of the planet (none near the rim)
    for (let i = 0; i < ocean.length; i += 3) {
      const [x, y, z] = rot(ocean[i], ocean[i + 1], ocean[i + 2]); if (z < 0.35) continue;
      plot(x, y, z, Math.max(1, Math.round(1.1 * s)), 190, 195, 210, 0.05 * smooth(0.35, 0.75, z));
    }
    // land: cool silver in the shade, warm white where the sun's light falls (real 3D lighting)
    const big = Math.max(2, Math.round(1.55 * s)), small = Math.max(1, Math.round(1.15 * s));
    for (let i = 0; i < land.length; i += 3) {
      const [x, y, z] = rot(land[i], land[i + 1], land[i + 2]); if (z < 0.04) continue;
      const lit = Math.max(0, x * sun[0] + y * sun[1] + z * sun[2]) * rise;      // light from the sun's direction
      const glow = Math.min(1, lit * 1.25);
      const a = (0.30 + 0.62 * glow) * smooth(0.04, 0.42, z);                       // fade at the rim: no ripple rings
      plot(x, y, z, z > 0.55 ? big : small, (200 + 55 * glow) | 0, (206 + 30 * glow) | 0, (222 - 22 * glow) | 0, a);
    }
    buf.getContext("2d").putImageData(img, 0, 0);
  }

  let lastFrame = 0;
  function frame(now) {
    raf = 0;
    if (slow && now - lastFrame < 30) { request(); return; }   // fps watchdog: 30 fps on slow machines
    const dt = lastFrame ? now - lastFrame : 16; lastFrame = now;
    const t = reduce ? 0 : ease(progress);
    const sa = lerp(SUN_FROM, SUN_TO, t), rise = lerp(RISE_FROM, RISE_TO, t);
    const sway = reduce ? 0 : SWAY_DEG * Math.sin(((now - t0) / 1000) * (2 * Math.PI / SWAY_SECONDS));
    const lon0 = lerp(LON_FROM, LON_TO, t) + sway;
    const { R, cx, cy } = g, sx = cx + R * Math.sin(sa), sy = cy - R * Math.cos(sa);
    // the sun sits just behind the rim: its direction in view space (y up, z towards the viewer)
    const sv = [Math.sin(sa), Math.cos(sa), -0.18], sl = Math.hypot(...sv), sun = sv.map(v => v / sl);
    const rot = rotation(lon0);
    const P = (lat, lon) => {
      const la = lat * Math.PI / 180, lo = lon * Math.PI / 180, c = Math.cos(la);
      const [x, y, z] = rot(c * Math.sin(lo), Math.sin(la), c * Math.cos(lo));
      return [cx + R * x, cy - R * y, z];
    };
    const tStart = performance.now();
    const c = canvas.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, W, H);
    // sky glow from behind the rim
    let gr = c.createRadialGradient(sx, sy, 0, sx, sy, R * 1.1);
    gr.addColorStop(0, `rgba(255,214,150,${0.34 * rise})`); gr.addColorStop(0.18, `rgba(245,165,36,${0.16 * rise})`);
    gr.addColorStop(0.5, `rgba(140,90,60,${0.06 * rise})`); gr.addColorStop(1, "rgba(0,0,0,0)");
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    // atmosphere: a smooth silver haze + a crisp rim that turns gold near the sun
    const ring = c.createRadialGradient(cx, cy, R - 2, cx, cy, R + 46);
    ring.addColorStop(0, "rgba(205,210,228,.28)"); ring.addColorStop(0.1, "rgba(190,198,222,.15)");
    ring.addColorStop(0.4, "rgba(170,180,210,.05)"); ring.addColorStop(1, "rgba(160,170,200,0)");
    c.fillStyle = ring; c.beginPath(); c.arc(cx, cy, R + 46, 0, 7); c.fill();
    for (const [w, al] of [[5, 0.22], [1.6, 0.6]]) {
      const cg = c.createConicGradient(-Math.PI / 2 + sa - Math.PI, cx, cy);
      cg.addColorStop(0, `rgba(150,160,190,${al * 0.35})`); cg.addColorStop(0.38, `rgba(170,180,210,${al * 0.6})`);
      cg.addColorStop(0.5, `rgba(255,226,170,${al * (0.6 + rise)})`); cg.addColorStop(0.62, `rgba(170,180,210,${al * 0.6})`);
      cg.addColorStop(1, `rgba(150,160,190,${al * 0.35})`);
      c.strokeStyle = cg; c.lineWidth = w; c.beginPath(); c.arc(cx, cy, R + w / 2 - 1, 0, 7); c.stroke();
    }
    // planet body, warmer on the sun's side
    gr = c.createRadialGradient(sx, sy, R * 0.05, cx, cy, R * 1.1);
    gr.addColorStop(0, "#2A2420"); gr.addColorStop(0.35, "#15151A"); gr.addColorStop(1, "#0B0B0F");
    c.fillStyle = gr; c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
    // the sun peeking over the rim + faint lens streak
    gr = c.createRadialGradient(sx, sy, 0, sx, sy, 90);
    gr.addColorStop(0, `rgba(255,250,235,${0.95 * rise})`); gr.addColorStop(0.12, `rgba(255,220,160,${0.7 * rise})`); gr.addColorStop(1, "rgba(245,165,36,0)");
    c.fillStyle = gr; c.beginPath(); c.arc(sx, sy, 90, 0, 7); c.fill();
    c.fillStyle = `rgba(255,236,200,${0.18 * rise})`; c.fillRect(sx - 260, sy - 0.6, 520, 1.2);
    // every dot, this frame
    dots(rot, sun, rise);
    c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(buf, box.x, box.y); c.setTransform(dpr, 0, 0, dpr, 0, 0);
    // arcs between story places, with a light travelling along each (6 s loop)
    const by = n => stories.find(s => s.n === n);
    const travel = reduce ? 0.62 : ((now - t0) / 6000) % 1;
    for (const [a, b, h] of ARCS) {
      if (!by(a) || !by(b)) continue;
      const A = P(by(a).lat, by(a).lon), B = P(by(b).lat, by(b).lon); if (A[2] < 0.05 || B[2] < 0.05) continue;
      const mx = (A[0] + B[0]) / 2, my = (A[1] + B[1]) / 2 - h * g.k;
      const lg = c.createLinearGradient(A[0], A[1], B[0], B[1]);
      lg.addColorStop(0, "rgba(255,200,97,0)"); lg.addColorStop(0.5, "rgba(255,200,97,.75)"); lg.addColorStop(1, "rgba(255,200,97,.05)");
      c.strokeStyle = lg; c.lineWidth = 1.3; c.beginPath(); c.moveTo(A[0], A[1]); c.quadraticCurveTo(mx, my, B[0], B[1]); c.stroke();
      const q = travel, qx = (1 - q) ** 2 * A[0] + 2 * (1 - q) * q * mx + q * q * B[0], qy = (1 - q) ** 2 * A[1] + 2 * (1 - q) * q * my + q * q * B[1];
      const fade = Math.sin(Math.PI * q);
      const pg = c.createRadialGradient(qx, qy, 0, qx, qy, 9); pg.addColorStop(0, `rgba(255,220,150,${fade})`); pg.addColorStop(1, "rgba(255,200,97,0)");
      c.fillStyle = pg; c.beginPath(); c.arc(qx, qy, 9, 0, 7); c.fill();
    }
    // story lights; report screen positions so the page can place the cards and name tags (HTML, not canvas)
    const places = [];
    for (const s of stories) {
      const p = P(s.lat, s.lon); if (p[2] < 0.05) continue;
      const madeOne = s.kind !== "queued", r = madeOne ? 26 : 12, q = madeOne ? 1 : 0.55;
      const sg = c.createRadialGradient(p[0], p[1], 0, p[0], p[1], r);
      sg.addColorStop(0, `rgba(255,214,140,${0.95 * q})`); sg.addColorStop(0.25, `rgba(245,165,36,${0.45 * q})`); sg.addColorStop(1, "rgba(245,165,36,0)");
      c.fillStyle = sg; c.beginPath(); c.arc(p[0], p[1], r, 0, 7); c.fill();
      c.fillStyle = madeOne ? "#FFF4DD" : "rgba(255,244,221,.75)"; c.beginPath(); c.arc(p[0], p[1], madeOne ? 2.6 : 1.6, 0, 7); c.fill();
      if (madeOne) { c.strokeStyle = "rgba(255,200,97,.35)"; c.lineWidth = 1; c.beginPath(); c.arc(p[0], p[1], 9, 0, 7); c.stroke(); }
      places.push({ ...s, year: s.y, x: p[0], y: p[1] });
    }
    // fade the bottom into the page
    gr = c.createLinearGradient(0, H - 200, 0, H); gr.addColorStop(0, "rgba(11,11,15,0)"); gr.addColorStop(1, "rgba(11,11,15,1)");
    c.fillStyle = gr; c.fillRect(0, H - 200, W, 200);
    opts.onPlace && opts.onPlace(places);
    // fps watchdog: if frames take too long, drop to 30 fps (looks the same, half the work)
    const cost = performance.now() - tStart; slow = cost > 22 ? Math.min(slow + 1, 3) : Math.max(0, slow - (cost < 10 ? 1 : 0));
    if (active && !reduce) request();     // the planet sways and the arc lights travel: keep drawing while visible
    void dt;
  }

  const request = () => { if (!raf) raf = requestAnimationFrame(frame); };
  const ro = new ResizeObserver(() => { size(); request(); }); ro.observe(canvas);
  size(); request();
  return {
    setProgress(p) { const v = Math.max(0, Math.min(1, p)); if (Math.abs(v - progress) > 0.0005) { progress = v; request(); } },
    setActive(on) { active = !!on; if (active) request(); },
    destroy() { ro.disconnect(); cancelAnimationFrame(raf); raf = 0; active = false; },
  };
}

// Name tags without collisions: made films first, then queued topics in queue order; a tag whose box would overlap
// an earlier tag, a card or another city's light is skipped (its light stays). Returns tags with left/top in px.
//   pickTags(places, { blocked: [cardRects], maxY: 820, width: W })
export function pickTags(places, { blocked = [], maxY = 820, width = 1440, font = 6.4 } = {}) {
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
