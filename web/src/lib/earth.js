// Candela hero globe v3 (6 Nov 2026: sub-pixel dots, a real sunrise; see dots() and the sun): a dotted Earth lit by a sun rising over its rim. Canvas 2D only (no WebGL,
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
// Film mode (11 Nov 2026, opt-in): opts.film = a paused <video> of the Blender Earth (lab/kaggle/earth_film, same camera
// maths, frame i = eased progress i/(N-1)). The film replaces the drawn planet (ring, body, dots); the approved sun,
// limb light, bloom, arcs and story lights are still drawn on top. The page's silver ring replaces the film's own air
// (render 7's air shell shows as a separate pale band). Instead of the dot sway, the film picture rolls slowly about
// the globe centre and the lights/arcs get the same roll, so they stay on their cities. Desktop only.
// onPlace(places) is called every frame with [{...story, year, x, y}] (x, y in CSS px): position HTML cards and
// tags imperatively from it (do NOT put it in React state: that re-renders 60 times a second).

// Approved values: top of page -> scrolled
const SUN_FROM = -0.55, SUN_TO = 0.12;   // angle on the rim, radians from the top (+ = right)
const RISE_FROM = 0.8, RISE_TO = 1.0;    // sun strength
const LON_FROM = -10, LON_TO = -6;       // the globe turns 4 degrees east while you scroll
const LAT0 = -6;
const SWAY_DEG = 3.5, SWAY_SECONDS = 48;
const FILM_ROLL_DEG = 1.6;
const MOON = 0.7;    // film mode: how bright the moonlit continents are (0 = pure black night, as rendered)   // film mode: the picture turns gently about the globe centre (the film itself can't sway) // living planet: a slow sway, Europe always stays in view

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
const FILM_FPS = opts.filmFps || 24, FILM_N = opts.filmFrames || 72;
  // Film frames are copied into `still` once decoded and always drawn from there. Drawing the <video> itself failed
  // while it was seeking (readyState drops below 2), so the page flipped between dots and Earth on every scroll step.
  let filmOk = false, filmIdx = -1, filmSeeking = false, filmWant = -1;
  const still = document.createElement("canvas");
  const grab = v => { still.width = v.videoWidth; still.height = v.videoHeight; still.getContext("2d").drawImage(v, 0, 0); };
  const useFilm = () => filmOk && W >= 640;   // once ready, film mode never drops back to the dots
  // moonlight: the render's night side is pure black (pixel values 1-2), so the page adds faint, soft continents
  // (the dot globe's land points, plotted small and drawn up-scaled = blurred) and a dim blue body underneath the lights
  const moon = document.createElement("canvas"), moonTmp = document.createElement("canvas"); let moonKey = "";
  if (opts.film) {
    const v = opts.film;
    const next = () => { if (filmWant >= 0 && filmWant !== filmIdx) { filmIdx = filmWant; filmSeeking = true; v.currentTime = (filmIdx + 0.5) / FILM_FPS; } };
    v.addEventListener("seeked", () => { grab(v); filmOk = true; filmSeeking = false; request(); next(); });
    const ready = () => { grab(v); filmOk = true; filmIdx = 0; request(); };
    if (v.readyState >= 2) setTimeout(ready, 0); else v.addEventListener("loadeddata", ready, { once: true });
    var seekFilm = i => { filmWant = i; if (!filmSeeking) next(); };
  }
  function moonland(rot, cx, cy, R) {
    const S = 3.5, mw = Math.ceil(2 * R / S) + 2, mh = Math.ceil(R / S) + 2;   // only the top half of the disc is on screen
    moon.width = mw; moon.height = mh;
    const mc = moon.getContext("2d"), im = mc.createImageData(mw, mh), d = im.data;
    for (let i = 0; i < land.length; i += 3) {
      const [x, y, z] = rot(land[i], land[i + 1], land[i + 2]); if (z <= 0) continue;
      const px = Math.round((R * x + R) / S), py = Math.round((R - R * y) / S); if (px < 0 || py < 0 || px >= mw || py >= mh) continue;
      const o = (py * mw + px) * 4, a = 150 * Math.min(1, z * 1.6);
      if (a > d[o + 3]) { d[o] = 92; d[o + 1] = 112; d[o + 2] = 150; d[o + 3] = a; }
    }
    // soften: the land points sit on a lattice, so blur them once into smooth landmasses (small canvas: cheap)
    moonTmp.width = mw; moonTmp.height = mh; moonTmp.getContext("2d").putImageData(im, 0, 0);
    mc.filter = "blur(1.4px)"; mc.drawImage(moonTmp, 0, 0); mc.filter = "none";
    return { x: cx - R, y: cy - R, w: mw * S, h: mh * S };
  }
  let moonBox = null;

  let acc = null;   // the pixel buffer's bytes (r, g, b, a): dots are blended straight into it, see dots()
  function size() {
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g = geom(W, H);
    // only the part of the canvas the globe can cover gets a pixel buffer
    const top = Math.max(0, Math.floor((g.cy - g.R - 4) * dpr)), left = Math.max(0, Math.floor((g.cx - g.R - 4) * dpr));
    const right = Math.min(canvas.width, Math.ceil((g.cx + g.R + 4) * dpr)), bottom = canvas.height;
    box = { x: left, y: top, w: Math.max(1, right - left), h: Math.max(1, bottom - top) };
    buf.width = box.w; buf.height = box.h;
    img = buf.getContext("2d").createImageData(box.w, box.h); px = new Uint32Array(img.data.buffer); acc = img.data;
  }

  function rotation(lonDeg) {   // world -> view: turn by -lon around north, then tilt by LAT0
    const lo = -lonDeg * Math.PI / 180, la = LAT0 * Math.PI / 180;
    const cl = Math.cos(lo), sl = Math.sin(lo), ca = Math.cos(la), sa = Math.sin(la);
    // x' = x cl + z sl ; z1 = -x sl + z cl ; then y'' = y ca - z1 sa ; z'' = y sa + z1 ca
    return (x, y, z) => { const xr = x * cl + z * sl, z1 = -x * sl + z * cl; return [xr, y * ca - z1 * sa, y * sa + z1 * ca]; };
  }

  // v3 (6 Nov): dots are drawn with SUB-PIXEL precision. v2 snapped every dot to whole pixels and switched between
  // two dot sizes, so as the globe turned the dots jumped a pixel at a time and popped in size (a shimmer a
  // perfectionist sees). Now each dot is a square of any size at any position; it covers each pixel by exactly the area
  // it overlaps (box filter), so it glides smoothly. Sizes change continuously with depth.
  function dots(rot, sun, rise) {
    px.fill(0);
    const { R, cx, cy } = g, s = dpr, ox = box.x, oy = box.y, bw = box.w, bh = box.h;
    const plot = (vx, vy, size, r, gg, b, a) => {
      const fx = (cx + R * vx) * s - ox - size / 2, fy = (cy - R * vy) * s - oy - size / 2;
      if (fx < 0 || fy < 0 || fx + size + 1 >= bw || fy + size + 1 >= bh) return;
      const x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.floor(fx + size), y1 = Math.floor(fy + size);
      for (let j = y0; j <= y1; j++) {
        const cyv = Math.min(j + 1, fy + size) - Math.max(j, fy); if (cyv <= 0) continue;
        let k = (j * bw + x0) * 4;
        for (let i = x0; i <= x1; i++, k += 4) {
          const cov = (Math.min(i + 1, fx + size) - Math.max(i, fx)) * cyv; if (cov <= 0) continue;
          const w = a * cov, ea = acc[k + 3] / 255;   // "over" blend into the 8-bit pixel (only pixels a dot touches)
          if (ea === 0) { acc[k] = r; acc[k + 1] = gg; acc[k + 2] = b; acc[k + 3] = w * 255; continue; }
          const oa = w + ea * (1 - w), f = w / oa;
          acc[k] += (r - acc[k]) * f; acc[k + 1] += (gg - acc[k + 1]) * f; acc[k + 2] += (b - acc[k + 2]) * f; acc[k + 3] = oa * 255;
        }
      }
    };
    // ocean: a few faint scattered dots, only on the face of the planet (none near the rim)
    const os = 1.1 * s;
    for (let i = 0; i < ocean.length; i += 3) {
      const [x, y, z] = rot(ocean[i], ocean[i + 1], ocean[i + 2]); if (z < 0.35) continue;
      plot(x, y, os, 190, 195, 210, 0.05 * smooth(0.35, 0.75, z));
    }
    // land: cool silver in the shade, warm white where the sun's light falls (real 3D lighting)
    const small = 1.1 * s, big = 1.6 * s;
    for (let i = 0; i < land.length; i += 3) {
      const [x, y, z] = rot(land[i], land[i + 1], land[i + 2]); if (z < 0.04) continue;
      const lit = Math.max(0, x * sun[0] + y * sun[1] + z * sun[2]) * rise;      // light from the sun's direction
      const glow = Math.min(1, lit * 1.25);
      const a = (0.30 + 0.62 * glow) * smooth(0.04, 0.42, z);                       // fade at the rim: no ripple rings
      plot(x, y, small + (big - small) * smooth(0.25, 0.8, z), 200 + 55 * glow, 206 + 30 * glow, 222 - 22 * glow, a);
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
    const sway = reduce || useFilm() ? 0 : SWAY_DEG * Math.sin(((now - t0) / 1000) * (2 * Math.PI / SWAY_SECONDS));
    const lon0 = lerp(LON_FROM, LON_TO, t) + sway;
    // film mode: a slow roll of the whole planet picture about its centre; lights and arcs get the same roll (see P)
    const roll = reduce || !useFilm() ? 0 : (FILM_ROLL_DEG * Math.PI / 180) * Math.sin(((now - t0) / 1000) * (2 * Math.PI / SWAY_SECONDS));
    const rc = Math.cos(roll), rs = Math.sin(roll);
    // the sun sits on the planet's limb and rises over it as you scroll (its centre goes from 6 px below to 9 px above)
    const { R, cx, cy } = g, sd = R + lerp(-6, 9, t) * g.k, sx = cx + sd * Math.sin(sa), sy = cy - sd * Math.cos(sa);
    // the sun sits just behind the rim: its direction in view space (y up, z towards the viewer)
    const sv = [Math.sin(sa), Math.cos(sa), -0.18], sl = Math.hypot(...sv), sun = sv.map(v => v / sl);
    const rot = rotation(lon0);
    const P = (lat, lon) => {
      const la = lat * Math.PI / 180, lo = lon * Math.PI / 180, c = Math.cos(la);
      const [x, y, z] = rot(c * Math.sin(lo), Math.sin(la), c * Math.cos(lo));
      const X = R * x, Y = -R * y;
      return [cx + X * rc - Y * rs, cy + X * rs + Y * rc, z];
    };
    const tStart = performance.now();
    const c = canvas.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, W, H);
    // sky glow from behind the rim
    let gr = c.createRadialGradient(sx, sy, 0, sx, sy, R * 1.1);
    gr.addColorStop(0, `rgba(255,214,150,${0.34 * rise})`); gr.addColorStop(0.18, `rgba(245,165,36,${0.16 * rise})`);
    gr.addColorStop(0.5, `rgba(140,90,60,${0.06 * rise})`); gr.addColorStop(1, "rgba(0,0,0,0)");
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
    // atmosphere: a smooth silver haze + a crisp rim that turns gold near the sun
    const filmOn = useFilm();
    {
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
    }
    // the sun BEHIND the planet: corona and core first, so the planet's body hides the part below the limb (v2 drew it
    // on top of the planet, with a hard horizontal streak through it: not how a real sunrise over a planet looks)
    const k = g.k;
    gr = c.createRadialGradient(sx, sy, 0, sx, sy, 150 * k);
    gr.addColorStop(0, `rgba(255,252,242,${rise})`); gr.addColorStop(0.07, `rgba(255,236,196,${0.85 * rise})`);
    gr.addColorStop(0.22, `rgba(255,190,110,${0.32 * rise})`); gr.addColorStop(0.55, `rgba(240,140,60,${0.08 * rise})`);
    gr.addColorStop(1, "rgba(240,140,60,0)");
    c.fillStyle = gr; c.beginPath(); c.arc(sx, sy, 150 * k, 0, 7); c.fill();
    c.fillStyle = `rgba(255,253,247,${rise})`; c.beginPath(); c.arc(sx, sy, 7.5 * k, 0, 7); c.fill();   // the disc itself
    if (filmOn) {
      // the film frame for this scroll position (the encode has a keyframe every 4 frames, so seeks are quick)
      seekFilm(Math.round(t * (FILM_N - 1)));
      const fw = W, fh = W / 1.6, fy = cy - 1370 * g.k;   // the film is the 1440x900 reference frame, globe centre (720, 1370)
      const mk = `${lon0.toFixed(2)}|${W}|${H}`;
      if (mk !== moonKey) { moonKey = mk; moonBox = moonland(rot, cx, cy, R); }
      c.save(); c.beginPath(); c.arc(cx, cy, R, 0, 7); c.clip();
      c.translate(cx, cy); c.rotate(roll); c.translate(-cx, -cy);
      c.drawImage(still, 0, fy, fw, fh);                                   // the real planet, opaque (hides the sun)
      c.globalCompositeOperation = "lighter";                              // + moonlight, never darkens the film
      gr = c.createRadialGradient(cx, cy - R * 0.55, R * 0.1, cx, cy, R);
      gr.addColorStop(0, "rgba(22,30,48,.9)"); gr.addColorStop(0.7, "rgba(14,20,34,.7)"); gr.addColorStop(1, "rgba(8,12,22,.4)");
      c.fillStyle = gr; c.fillRect(cx - R, cy - R, 2 * R, R + 4);
      c.globalAlpha = MOON; c.imageSmoothingQuality = "high";
      c.drawImage(moon, moonBox.x, moonBox.y, moonBox.w, moonBox.h);
      c.restore();
    } else {
    // planet body, warmer on the sun's side
    gr = c.createRadialGradient(sx, sy, R * 0.05, cx, cy, R * 1.1);
    gr.addColorStop(0, "#2A2420"); gr.addColorStop(0.35, "#15151A"); gr.addColorStop(1, "#0B0B0F");
    c.fillStyle = gr; c.beginPath(); c.arc(cx, cy, R, 0, 7); c.fill();
    // every dot, this frame
    dots(rot, sun, rise);
    c.setTransform(1, 0, 0, 1, 0, 0); c.drawImage(buf, box.x, box.y); c.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    // sunlight scattered through the air along the limb: a thin bright arc, white at the sun, warm, then gone ~25 deg away
    const limb = c.createConicGradient(-Math.PI / 2 + sa - 0.45, cx, cy);
    limb.addColorStop(0, "rgba(255,170,90,0)"); limb.addColorStop(0.035, `rgba(255,190,120,${0.55 * rise})`);
    limb.addColorStop(0.0716, `rgba(255,248,232,${rise})`); limb.addColorStop(0.11, `rgba(255,190,120,${0.55 * rise})`);
    limb.addColorStop(0.143, "rgba(255,170,90,0)"); limb.addColorStop(1, "rgba(255,170,90,0)");
    c.save(); c.globalCompositeOperation = "lighter";
    for (const [w, al] of [[9 * k, 0.18], [3.2 * k, 0.45], [1.3 * k, 0.9]]) {
      c.globalAlpha = al; c.strokeStyle = limb; c.lineWidth = w; c.beginPath(); c.arc(cx, cy, R, sa - Math.PI / 2 - 0.45, sa - Math.PI / 2 + 0.45); c.stroke();
    }
    // camera bloom: the sun is far brighter than anything else, so its glow spills softly over the limb
    c.globalAlpha = 1;
    gr = c.createRadialGradient(sx, sy, 0, sx, sy, 60 * k);
    gr.addColorStop(0, `rgba(255,246,226,${0.55 * rise})`); gr.addColorStop(0.3, `rgba(255,214,160,${0.18 * rise})`); gr.addColorStop(1, "rgba(255,200,140,0)");
    c.fillStyle = gr; c.beginPath(); c.arc(sx, sy, 60 * k, 0, 7); c.fill();
    c.restore();
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
      if (filmOn) {   // over the real Earth the hopping light needs a brighter core and a short tail to read
        for (let j = 1; j <= 6; j++) {
          const u = Math.max(0, q - j * 0.018), ux = (1 - u) ** 2 * A[0] + 2 * (1 - u) * u * mx + u * u * B[0], uy = (1 - u) ** 2 * A[1] + 2 * (1 - u) * u * my + u * u * B[1];
          c.fillStyle = `rgba(255,214,140,${0.5 * fade * (1 - j / 7)})`; c.beginPath(); c.arc(ux, uy, 2.2 - j * 0.25, 0, 7); c.fill();
        }
        const hg = c.createRadialGradient(qx, qy, 0, qx, qy, 16); hg.addColorStop(0, `rgba(255,236,190,${0.55 * fade})`); hg.addColorStop(1, "rgba(255,200,97,0)");
        c.fillStyle = hg; c.beginPath(); c.arc(qx, qy, 16, 0, 7); c.fill();
        c.fillStyle = `rgba(255,250,236,${fade})`; c.beginPath(); c.arc(qx, qy, 2.4, 0, 7); c.fill();
      }
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
