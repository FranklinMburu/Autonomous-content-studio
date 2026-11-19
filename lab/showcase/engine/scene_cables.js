// Video 2: "The internet lives at the bottom of the sea". Hero object: one pulse of light (your message).
import { THREE, RoundedBoxGeometry, makeStage, camRig, toScreen, M, canvasTex, redraw, woodTex, starfield, dust, rbox, box, trail, clamp, lerp, ease, easeOut, smooth, ramp, win, rng } from './core.js';
import * as O from './overlay.js';

const CY = 0x5ff3ff, CY_CSS = '#5ff3ff', GOLD = 0xffc66b;

export async function build(timing) {
  const W = window.__W, H = window.__H;
  const st = makeStage(W, H, { fov: 32, envI: .25, exposure: 1.1, bg: 0x02050a });
  const { scene, camera, composer, grade, bloom } = st;
  O.mount(CY_CSS, '#ffc66b');
  const norm = s => s.toLowerCase().replace(/[^a-z0-9']/g, '');
  const words = timing.words;
  const T = (w, n = 1) => { let c = 0; for (const x of words) if (norm(x.w) === norm(w) && ++c === n) return x.start; console.log('[scene] missing cue ' + w + n); return 0; };
  const dur = timing.duration + 1.4;
  const display = { 'ninety-nine percent': '99%', 'more than forty times': 'more than 40 times', 'two hundred': '200', 'three or four': '3 or 4', 'about sixty': 'about 60', 'a quarter': '25%' };
  const keys = new Set(['space', 'down', 'ocean', 'seafloor', 'earth', 'hose', 'glass', 'light', 'breaks', 'shark', 'zero', 'anchors', 'gear', 'week', 'ships', 'hook', 'daylight', 'europe', 'asia', 'second', 'sea', 'culprits']);
  const caps = O.buildCaptions(words, display, keys);
  const c = {
    sent: T('sent'), space: T('space'), down: T('down'), bottom: T('bottom', 1), more: T('more', 1), seafloor: T('seafloor'), laid: T('laid'), earth: T('earth'), forty: T('forty'),
    deep: T('deep'), hose: T('hose', 1), inside: T('inside'), glass: T('glass'), flashes: T('flashes'), so: T('so', 1), shark: T('shark'), but: T('but'), zero: T('zero'),
    real: T('real'), anchors: T('anchors'), around: T('around'), week: T('week'), only: T('only'), sixty: T('sixty'), drop: T('drop'), drag: T('drag'), haul: T('haul'), daylight: T('daylight'),
    in2024: T('2024,'), quarter: T('quarter'), europe: T('europe'), next: T('next'), arrives: T('arrives'), remember: T('remember'), hose2: T('hose', 2), sea: T('sea', 1)
  };
  if (!c.in2024) c.in2024 = T('2024');

  // ================= SET A: night pier by the sea (origin) =================
  const A = new THREE.Group(); scene.add(A);
  const wood = woodTex(6, [70, 48, 34]); wood.wrapS = wood.wrapT = THREE.RepeatWrapping; wood.repeat.set(1, 4);
  for (let i = 0; i < 9; i++) { const pl = rbox(.9, .14, 16, .03, M.std(0xffffff, .7, 0, { map: wood })); pl.position.set(-4 + i * .96, 0, -2); A.add(pl); }
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(400, 400, 1, 1), M.phys(0x06121c, .12, 0, { clearcoat: 1, clearcoatRoughness: .25 })); sea.rotation.x = -Math.PI / 2; sea.position.y = -1.6; A.add(sea);
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(300, 120), new THREE.MeshBasicMaterial({ map: canvasTex(512, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#03060c'); gr.addColorStop(.7, '#0c1a2c'); gr.addColorStop(1, '#1b2e44'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }), toneMapped: false }));
  sky.position.set(0, 30, -140); A.add(sky);
  const moonDisc = new THREE.Mesh(new THREE.CircleGeometry(4, 48), M.basic(0xe8eeff, { toneMapped: false })); moonDisc.position.set(-30, 26, -135); A.add(moonDisc);
  const stars = starfield(1600, 110, 3, .3); stars.position.set(0, 0, -20); A.add(stars);
  const sat = new THREE.Group(); { const b = box(.5, .5, .8, M.phys(0xd8c38a, .3, .9)); sat.add(b); for (const s of [-1, 1]) { const p = box(1.6, .02, .6, M.std(0x1c2e5a, .3, .6, { emissive: 0x0a1430 })); p.position.x = s * 1.1; sat.add(p); } } sat.position.set(4, 14, -16); A.add(sat);
  const phone = new THREE.Group(); { const body = rbox(.75, .07, 1.55, .09, M.phys(0x1b1c20, .25, .6, { clearcoat: 1 })); phone.add(body);
    const scr = canvasTex(400, 840, (g, w, h) => { g.fillStyle = '#0b0e14'; g.fillRect(0, 0, w, h); g.fillStyle = '#20252f'; g.beginPath(); g.roundRect(150, 420, 220, 90, 30); g.fill(); g.fillStyle = '#e9eef6'; g.font = '30px Inter'; g.fillText('See you at 8?', 172, 476);
      g.fillStyle = '#5ff3ff'; g.beginPath(); g.roundRect(40, 560, 250, 90, 30); g.fill(); g.fillStyle = '#062028'; g.font = '600 30px Inter'; g.fillText('On my way!', 70, 616); g.fillStyle = '#7b8494'; g.font = '22px Inter'; g.fillText('Delivered', 210, 690); });
    const s = new THREE.Mesh(new THREE.PlaneGeometry(.69, 1.47), new THREE.MeshBasicMaterial({ map: scr, toneMapped: false })); s.rotation.x = -Math.PI / 2; s.position.y = .037; phone.add(s);
    phone.userData.light = new THREE.PointLight(0x9fdcff, 2, 3, 2); phone.userData.light.position.y = .5; phone.add(phone.userData.light); }
  phone.position.set(0, .1, 0); phone.rotation.y = .35; A.add(phone);
  const moonL = new THREE.DirectionalLight(0x9cb8ff, 1.2); moonL.position.set(-8, 10, -12); A.add(moonL);
  const warm = new THREE.SpotLight(0xffc99a, 25, 16, .5, .7, 1.5); warm.position.set(3, 5, 4); warm.target.position.set(0, 0, 0); warm.castShadow = true; A.add(warm, warm.target);
  scene.add(new THREE.HemisphereLight(0x2a3b55, 0x05080c, .4));

  // ================= SET B: the deep seafloor (x=200), shared by shark, anchors and the hook =================
  const B = new THREE.Group(); B.position.x = 200; scene.add(B);
  const sandTex = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#4a5560'; g.fillRect(0, 0, w, h); const r = rng(41); for (let i = 0; i < 30000; i++) { const v = 60 + r() * 80; g.fillStyle = `rgba(${v},${v + 8},${v + 14},.25)`; g.fillRect(r() * w, r() * h, 2, 2); }
    for (let i = 0; i < 40; i++) { g.strokeStyle = 'rgba(20,30,40,.18)'; g.lineWidth = 6; g.beginPath(); const y = r() * h; for (let x = 0; x < w; x += 20) g.lineTo(x, y + Math.sin(x * .02 + i) * 14); g.stroke(); } });
  sandTex.wrapS = sandTex.wrapT = THREE.RepeatWrapping; sandTex.repeat.set(6, 6);
  const sg = new THREE.PlaneGeometry(160, 160, 160, 160); { const p = sg.attributes.position; for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i); p.setZ(i, Math.sin(x * .12) * .5 + Math.sin(y * .09 + x * .05) * .7 + Math.sin(x * .4 + y * .3) * .12); } sg.computeVertexNormals(); }
  const sand = new THREE.Mesh(sg, M.std(0xffffff, .95, 0, { map: sandTex })); sand.rotation.x = -Math.PI / 2; sand.receiveShadow = true; B.add(sand);
  const rocks = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(.5, 1), M.std(0x2b3238, .9), 70); { const r = rng(5), o = new THREE.Object3D(); for (let i = 0; i < 70; i++) { o.position.set((r() - .5) * 60, -.1, -r() * 60 + 10); o.scale.set(.4 + r() * 1.6, .3 + r() * .8, .4 + r() * 1.4); o.rotation.set(r(), r(), r()); o.updateMatrix(); rocks.setMatrixAt(i, o.matrix); } B.add(rocks); }
  const cablePts = []; for (let i = 0; i <= 40; i++) { const z = 14 - i * 2.2; cablePts.push(new THREE.Vector3(Math.sin(i * .35) * 1.2, .25 + Math.sin(i * .9) * .03, z)); }
  const cableCurve = new THREE.CatmullRomCurve3(cablePts);
  const cable = new THREE.Mesh(new THREE.TubeGeometry(cableCurve, 400, .12, 16), M.phys(0x0d0f12, .35, .1, { clearcoat: .6 })); cable.castShadow = true; B.add(cable);
  const cableGlow = new THREE.Mesh(new THREE.TubeGeometry(cableCurve, 400, .03, 8), new THREE.MeshBasicMaterial({ color: CY, transparent: true, opacity: 0, toneMapped: false })); cableGlow.position.y = .13; B.add(cableGlow);
  const brokenGap = .52; // where the anchor breaks the cable (fraction along the curve)
  const rays = []; for (let i = 0; i < 7; i++) { const r = new THREE.Mesh(new THREE.ConeGeometry(2.5 + i % 3, 40, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0x5fb7ff, transparent: true, opacity: .035, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending })); r.position.set(-14 + i * 5, 18, -10 - i * 3); r.rotation.z = .15; B.add(r); rays.push(r); }
  const snow = dust(1400, [40, 26, 40], [0, 10, -6], 7, .05, 0xbfe6ff); B.add(snow);
  const blueL = new THREE.DirectionalLight(0x5ba7ff, 1.4); blueL.position.set(-10, 30, 5); B.add(blueL);
  const spotB = new THREE.SpotLight(0x9fd6ff, 120, 40, .5, .8, 1.5); spotB.position.set(4, 12, 10); spotB.target.position.set(0, 0, -2); spotB.castShadow = true; spotB.shadow.mapSize.set(1024, 1024); B.add(spotB, spotB.target);
  // shark (stylised, procedural)
  const shark = new THREE.Group(); { const bodyM = M.phys(0x4f5d6b, .45, .1, { clearcoat: .3 }); const body = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), bodyM); body.scale.set(.55, .5, 2.4); shark.add(body);
    const belly = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), M.std(0xc9cfd4, .6)); belly.scale.set(.48, .3, 2.1); belly.position.y = -.16; shark.add(belly);
    const dorsal = new THREE.Mesh(new THREE.ConeGeometry(.35, .9, 3), bodyM); dorsal.position.set(0, .7, -.1); dorsal.rotation.x = -.35; shark.add(dorsal);
    const tail = new THREE.Group(); const tu = new THREE.Mesh(new THREE.ConeGeometry(.22, 1.1, 3), bodyM); tu.position.y = .45; tu.rotation.x = .5; const tl = tu.clone(); tl.position.y = -.35; tl.rotation.x = Math.PI - .5; tl.scale.y = .7; tail.add(tu, tl); tail.position.z = -2.4; shark.add(tail); shark.userData.tail = tail;
    for (const s of [-1, 1]) { const f = new THREE.Mesh(new THREE.ConeGeometry(.2, 1.0, 3), bodyM); f.position.set(s * .55, -.25, .4); f.rotation.z = s * 1.9; f.rotation.x = .4; shark.add(f); }
    for (const s of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(.06, 8, 8), M.basic(0x050505)); e.position.set(s * .38, .12, 1.7); shark.add(e); } }
  shark.scale.setScalar(.62); B.add(shark);
  // ship above (seen from below) + anchor chain + anchor
  const hull = new THREE.Mesh(new THREE.CapsuleGeometry(3, 18, 8, 16), M.std(0x05070a, .9)); hull.rotation.x = Math.PI / 2; hull.scale.set(1, 1, .5); B.add(hull);
  const surf = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshBasicMaterial({ color: 0x4aa8d8, transparent: true, opacity: .22, side: THREE.DoubleSide, toneMapped: false })); surf.rotation.x = Math.PI / 2; surf.position.y = 30; B.add(surf);
  const anchor = new THREE.Group(); { const am = M.phys(0x8a9099, .35, .9); const shank = box(.18, 1.6, .18, am); shank.position.y = .8; anchor.add(shank); const arm = new THREE.Mesh(new THREE.TorusGeometry(.75, .09, 8, 24, Math.PI), am); arm.rotation.z = Math.PI; arm.position.y = .2; anchor.add(arm);
    for (const s of [-1, 1]) { const fl = new THREE.Mesh(new THREE.ConeGeometry(.2, .45, 4), am); fl.position.set(s * .78, .32, 0); anchor.add(fl); } } anchor.scale.setScalar(2.2); B.add(anchor); const anchorL = new THREE.PointLight(0xbfe0ff, 30, 12, 2); B.add(anchorL);
  const chainM = M.phys(0x50545b, .4, .9); const chain = new THREE.Mesh(new THREE.CylinderGeometry(.11, .11, 1, 8), chainM); B.add(chain);
  // the grapnel hook of the repair ship
  const hook = new THREE.Group(); { const hm = M.phys(0xb8bcc4, .3, 1); const sh = box(.12, 1.2, .12, hm); sh.position.y = .6; hook.add(sh); for (let i = 0; i < 4; i++) { const p = new THREE.Mesh(new THREE.TorusGeometry(.35, .05, 8, 16, Math.PI * .9), hm); p.rotation.y = i * Math.PI / 2; p.position.y = .3; hook.add(p); } } B.add(hook);
  const line = new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, 1, 6), M.std(0xcfc8b8, .6)); B.add(line);

  // ================= SET C: the cable up close, next to a garden hose (x=300) =================
  const C = new THREE.Group(); C.position.x = 300; scene.add(C);
  const studio = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), M.std(0x101318, .7, .2)); studio.rotation.x = -Math.PI / 2; studio.receiveShadow = true; C.add(studio);
  const hoseCurve = new THREE.CatmullRomCurve3(Array.from({ length: 60 }, (_, i) => { const a = i * .42, r = 1.2 + i * .012; return new THREE.Vector3(Math.cos(a) * r - 2.2, .1 + i * .004, Math.sin(a) * r - .5); }));
  const hose = new THREE.Mesh(new THREE.TubeGeometry(hoseCurve, 300, .1, 16), M.phys(0x2f8f3a, .35, 0, { clearcoat: .5 })); hose.castShadow = true; C.add(hose);
  const layers = [ // outer -> inner: radius, length, material, label
    [.1, 3.2, M.phys(0x0c0d0f, .4, 0, { clearcoat: .6 }), 'Polyethylene jacket'],
    [.082, 3.5, M.phys(0xc8763d, .3, 1), 'Copper (powers the repeaters)'],
    [.066, 3.8, M.phys(0xb9bec6, .25, 1), 'Steel wires (strength)'],
    [.045, 4.1, M.phys(0x9fd3ff, .05, 0, { transmission: .7, transparent: true, opacity: .55 }), 'Gel (keeps water out)']];
  const layerMeshes = layers.map(([r, l, m]) => { const g = new THREE.Mesh(new THREE.CylinderGeometry(r, r, l, 40, 1, true), m); g.material.side = THREE.DoubleSide; g.rotation.z = Math.PI / 2; g.castShadow = true; C.add(g); return g; });
  const fibers = []; for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; const f = new THREE.Mesh(new THREE.CylinderGeometry(.006, .006, 4.6, 6), new THREE.MeshBasicMaterial({ color: CY, toneMapped: false })); f.rotation.z = Math.PI / 2; f.position.set(0, Math.cos(a) * .02, Math.sin(a) * .02); C.add(f); fibers.push(f); }
  const cK = new THREE.SpotLight(0xffffff, 60, 20, .5, .6, 1.4); cK.position.set(-2, 6, 4); cK.target.position.set(0, 0, 0); cK.castShadow = true; C.add(cK, cK.target);
  const cRim = new THREE.PointLight(CY, 4, 6, 2); cRim.position.set(1, .8, -1.2); C.add(cRim);
  const cD = dust(200, [8, 3, 8], [0, 1, 0], 11, .015, 0xd8f6ff); C.add(cD);

  // ================= SET E: the Earth wrapped in cable (x=400) =================
  const E = new THREE.Group(); E.position.x = 400; scene.add(E);
  const earthTex = canvasTex(1024, 512, (g, w, h) => { g.fillStyle = '#071526'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(95,243,255,.12)'; g.lineWidth = 1.5; for (let i = 1; i < 12; i++) { g.beginPath(); g.moveTo(0, i * h / 12); g.lineTo(w, i * h / 12); g.stroke(); } for (let i = 0; i < 24; i++) { g.beginPath(); g.moveTo(i * w / 24, 0); g.lineTo(i * w / 24, h); g.stroke(); } });
  const earth = new THREE.Mesh(new THREE.SphereGeometry(3, 64, 32), M.std(0xffffff, .6, .1, { map: earthTex, emissive: 0x071a2c, emissiveIntensity: .6 })); E.add(earth);
  const atmo = new THREE.Mesh(new THREE.SphereGeometry(3.25, 64, 32), new THREE.MeshBasicMaterial({ color: 0x3fa9ff, transparent: true, opacity: .08, side: THREE.BackSide, toneMapped: false })); E.add(atmo);
  const wraps = []; { const r = rng(3); for (let i = 0; i < 42; i++) { const ring = new THREE.Mesh(new THREE.TorusGeometry(3.02 + i * .004, .006, 6, 160), new THREE.MeshBasicMaterial({ color: CY, transparent: true, opacity: .85, toneMapped: false })); ring.rotation.set(r() * Math.PI, r() * Math.PI, 0); E.add(ring); wraps.push(ring); } }
  const eL = new THREE.DirectionalLight(0xbfe0ff, 2); eL.position.set(-6, 4, 6); E.add(eL);
  const eS = starfield(1400, 80, 9, .2); E.add(eS);

  // ================= SET F: the repair ship at dawn (x=500): surface above the seafloor's twin =================
  const F = new THREE.Group(); F.position.x = 900; scene.add(F);
  const dawnSky = new THREE.Mesh(new THREE.PlaneGeometry(400, 160), new THREE.MeshBasicMaterial({ map: canvasTex(512, 512, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#0d1a33'); gr.addColorStop(.55, '#5d4a6e'); gr.addColorStop(.8, '#f08a5d'); gr.addColorStop(1, '#ffd29a'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }), toneMapped: false })); dawnSky.position.set(0, 40, -160); F.add(dawnSky);
  const sun = new THREE.Mesh(new THREE.CircleGeometry(7, 48), M.basic(0xffe2a8, { toneMapped: false })); sun.position.set(18, 12, -155); F.add(sun);
  const fsea = new THREE.Mesh(new THREE.PlaneGeometry(500, 500), M.phys(0x1f3a52, .15, 0, { clearcoat: 1, clearcoatRoughness: .2 })); fsea.rotation.x = -Math.PI / 2; F.add(fsea);
  const ship = new THREE.Group(); { const hm = M.std(0x1d2a38, .6, .2); const h1 = box(16, 2.4, 4, hm); h1.position.y = .6; ship.add(h1); const bow = new THREE.Mesh(new THREE.ConeGeometry(2, 4, 4), hm); bow.rotation.z = -Math.PI / 2; bow.rotation.x = Math.PI / 4; bow.position.set(10, .6, 0); ship.add(bow);
    const deck = box(15.6, .2, 3.8, M.std(0xb34a33, .7)); deck.position.y = 1.85; ship.add(deck); const br = box(4, 3, 3.2, M.std(0xb9bbbe, .75)); br.position.set(-3, 3.4, 0); ship.add(br);
    for (let i = 0; i < 6; i++) { const w = box(.5, .4, .05, M.glow(0xfff0c8, .6)); w.position.set(-4.6 + i * .65, 3.9, 1.62); ship.add(w); }
    const crane = box(.25, 6, .25, M.std(0xf2c230, .5, .3)); crane.position.set(6, 4.8, 0); crane.rotation.z = -.5; ship.add(crane); const sheave = new THREE.Mesh(new THREE.TorusGeometry(.5, .12, 8, 20), M.std(0x333, .4, .7)); sheave.position.set(7.6, 7.4, 0); ship.add(sheave); }
  ship.position.set(0, 0, -6); F.add(ship);
  const fsun = new THREE.DirectionalLight(0xffc8a0, 1.1); fsun.position.set(20, 12, -40); F.add(fsun);
  const fline = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 1, 6), M.std(0xe9e1cf, .6)); F.add(fline);
  const liftCable = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(-6, -2, 0), new THREE.Vector3(-1, .4, 0), new THREE.Vector3(0, 1.2, 0), new THREE.Vector3(1, .4, 0), new THREE.Vector3(6, -2, 0)]), 80, .12, 12), M.phys(0x0d0f12, .3, .1, { clearcoat: .7 })); F.add(liftCable);
  const fD = dust(200, [30, 10, 30], [0, 4, 0], 15, .04, 0xffe4c2); F.add(fD);

  // ================= SET G: Red Sea schematic (x=600) =================
  const Gs = new THREE.Group(); Gs.position.x = 600; scene.add(Gs);
  const gfloor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), M.std(0x0a0d12, .8)); gfloor.rotation.x = -Math.PI / 2; Gs.add(gfloor);
  const land = (x, z, w, d) => { const m = rbox(w, .6, d, .2, M.std(0x1c2430, .8)); m.position.set(x, .3, z); Gs.add(m); return m; };
  land(-6, -1, 6, 8); land(6, -1, 6, 8); land(0, -4.3, 4.6, 1.6); land(0, 2.3, 4.6, 1.6);
  const lanes = []; for (let i = 0; i < 4; i++) { const z = -1.8 + i * 1.2; const tube = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 18, 12), new THREE.MeshStandardMaterial({ color: 0x0b0d10, emissive: CY, emissiveIntensity: 1.6 })); tube.rotation.z = Math.PI / 2; tube.position.set(0, .7, z); Gs.add(tube); lanes.push(tube); }
  const gK = new THREE.PointLight(0xffffff, 30, 30, 2); gK.position.set(0, 8, 6); Gs.add(gK);

  // ---------- hero pulse ----------
  const pulse = new THREE.Group(); { const core = new THREE.Mesh(new THREE.SphereGeometry(.09, 16, 16), M.basic(0xeaffff, { toneMapped: false })); pulse.add(core); const halo = new THREE.Mesh(new THREE.SphereGeometry(.22, 16, 16), new THREE.MeshBasicMaterial({ color: CY, transparent: true, opacity: .35, toneMapped: false, blending: THREE.AdditiveBlending, depthWrite: false })); pulse.add(halo);
    const pl = new THREE.PointLight(CY, 6, 6, 2); pulse.add(pl); pulse.userData.pl = pl; } scene.add(pulse);
  const pPath = trail([[0, .2, 0], [.2, 1.2, -2], [.4, 2.6, -5], [.6, 1.2, -9], [.6, -1.6, -11]], CY, .018); A.add(pPath);
  const pulses = []; for (let i = 0; i < 6; i++) { const p = new THREE.Mesh(new THREE.SphereGeometry(.06, 10, 10), M.basic(0xd8ffff, { toneMapped: false })); B.add(p); pulses.push(p); }

  // ---------- camera ----------
  const X = (s, p) => [p[0] + s, p[1], p[2]];
  const keysCam = [
    { t: 0, p: [1.1, .9, 2.6], l: [0, .1, -.2], fov: 30 },                              // 1 phone on the pier at night
    { t: c.sent, p: [.8, 1.3, 2.0], l: [0, .3, -1], fov: 32 },
    { t: c.space - .1, p: [.4, 1.6, 2.2], l: [3.4, 12, -15], fov: 44 },                 // tilt up to space (the satellite)
    { t: c.down - .05, p: [.4, 2.2, 1.0], l: [.6, -1.4, -10], fov: 42 },                // ...and down to the water
    { t: c.bottom, p: X(200, [3, 9, 22]), l: X(200, [0, 1, 0]), fov: 38, cut: 1 },      // 2 dive: the seafloor
    { t: c.seafloor, p: X(200, [2.2, 2.4, 10]), l: X(200, [0, .3, -2]), fov: 34 },
    { t: c.laid - .05, p: X(400, [0, 1.5, 12]), l: X(400, [0, 0, 0]), fov: 34, cut: 1 }, // 3 the Earth, wrapped 40 times
    { t: c.deep - .3, p: X(400, [-2.5, 1.2, 9]), l: X(400, [0, 0, 0]), fov: 34 },
    { t: c.deep + .1, p: X(300, [.6, 2.6, 4.4]), l: X(300, [-.8, .1, 0]), fov: 30, cut: 1 }, // 4 cable vs garden hose
    { t: c.inside - .1, p: X(300, [.9, 1.0, 2.6]), l: X(300, [.2, .1, 0]), fov: 30 },
    { t: c.glass, p: X(300, [2.6, .45, .9]), l: X(300, [1.8, .1, 0]), fov: 32 },        // the cut end, fibers glowing
    { t: c.so - .05, p: X(200, [-3, 2.0, 6]), l: X(200, [0, .6, 1]), fov: 34, cut: 1 }, // 5 shark myth
    { t: c.zero, p: X(200, [-1.4, 1.4, 4.4]), l: X(200, [0, .7, 1]), fov: 32 },
    { t: c.real - .05, p: X(200, [3, 3.5, 2]), l: X(200, [0, 3, -9]), fov: 40, cut: 1 }, // 6 anchors from above
    { t: c.anchors + .5, p: X(200, [2.2, 1.6, -4]), l: X(200, [0, .3, -11.5]), fov: 34 },
    { t: c.week, p: X(200, [1.6, 1.2, -8.5]), l: X(200, [0, .2, -11.6]), fov: 32 },
    { t: c.only - .05, p: X(900, [26, 6, 18]), l: X(900, [0, 3, -6]), fov: 32, cut: 1 },  // 7 repair ship at dawn
    { t: c.drop, p: X(200, [2.5, 3, 4]), l: X(200, [0, 1, -2]), fov: 34, cut: 1 },        // the hook comes down
    { t: c.haul, p: X(200, [2.5, 4.5, 4]), l: X(200, [0, 5, -2]), fov: 36 },
    { t: c.daylight - .2, p: X(900, [4, 1.6, 9]), l: X(900, [0, 2.2, 0]), fov: 34, cut: 1 }, // up into the daylight
    { t: c.in2024 - .05, p: X(600, [0, 11, 8]), l: X(600, [0, 0, -.6]), fov: 34, cut: 1 }, // 8 Red Sea schematic
    { t: c.europe, p: X(600, [0, 9, 6.4]), l: X(600, [0, 0, -.6]), fov: 34 },
    { t: c.next - .05, p: [.9, 1.1, 2.2], l: [0, .1, -.2], fov: 30, cut: 1 },            // 9 home: the message arrives
    { t: c.remember, p: X(200, [3.5, 1.6, 7]), l: X(200, [0, .3, -4]), fov: 32, cut: 1 },
    { t: dur, p: X(200, [2.2, 1.0, 4.5]), l: X(200, [0, .3, -6]), fov: 30 }
  ];
  for (const k of keysCam) { const x = k.l[0]; const f = x < 100 ? 1.7 : x < 250 ? 1.75 : x < 350 ? 1.3 : x < 450 ? 2.0 : x < 650 ? 1.8 : 1.0; k.p = k.p.map((v, i) => k.l[i] + (v - k.l[i]) * f); }
  const cam = camRig(camera, keysCam, .015);
  const V = (...a) => new THREE.Vector3(...a);
  const cutTimes = keysCam.filter(k => k.cut).map(k => k.t);
  const underwater = t => (t > c.bottom && t < c.laid) || (t > c.so && t < c.only) || (t > c.drop && t < c.daylight - .2) || t > c.remember;

  const render = t => {
    cam(t);
    if (window.__camO) { const o = window.__camO; camera.position.set(...o.p); camera.lookAt(...o.l); camera.fov = o.fov || 40; camera.updateProjectionMatrix(); }
    for (const d of [snow, cD, fD]) d.userData.tick(t);
    scene.fog = underwater(t) ? new THREE.FogExp2(0x041a2b, .045) : null;
    scene.background.set(underwater(t) ? 0x041a2b : ((t > c.only && t < c.drop) || (t > c.daylight - .2 && t < c.in2024)) ? 0x3a3150 : 0x02050a);
    // pulse: leaves the phone on "sent", rises (not to space), dives on "down"; then races along the seabed cable
    let pp = V(0, .2, 0), pv = 0;
    if (t >= c.sent && t < c.bottom) { const k = ease((t - c.sent) / (c.bottom - c.sent)); pp = pPath.userData.curve.getPointAt(k); pv = 1; pPath.userData.set(k); } else pPath.userData.set(0);
    if (t >= c.bottom && t < c.laid) { const k = ((t - c.bottom) * .18) % 1; pp = cableCurve.getPointAt(k).clone().add(V(200, .14, 0)); pv = 1; cableGlow.material.opacity = .5; }
    else cableGlow.material.opacity = t > c.remember ? .55 : 0;
    if (t > c.remember) { const k = ((t - c.remember) * .2) % 1; pp = cableCurve.getPointAt(k).clone().add(V(200, .14, 0)); pv = 1; }
    pulse.position.copy(pp); pulse.scale.setScalar(pv ? 1 + .25 * Math.sin(t * 20) : .0001);
    pulses.forEach((p, i) => { const k = ((t * .22 + i / 6) % 1); p.position.copy(cableCurve.getPointAt(k)).add(V(0, .14, 0)); p.visible = underwater(t) && (t < c.real || t > c.remember); });
    // satellite turns away: the message did not go there
    sat.rotation.y = t * .2; sat.visible = t < c.down + .5;
    // Earth wrapped: rings appear one by one up to "forty"
    const nW = Math.floor(42 * ramp(t, c.laid, c.forty + .5)); wraps.forEach((r, i) => r.visible = i < nW); earth.rotation.y = t * .15;
    // cable cross-section: layers slide apart on "inside", fibers flash on "flashes"
    const kx = ease((t - c.inside) / 1.2); layerMeshes.forEach((m, i) => { m.position.x = lerp(0, 1.0 + i * .35, kx) * -1 + kx * 2.2; });
    fibers.forEach((f, i) => { f.position.x = kx * 2.6; f.material.color.set(CY).multiplyScalar(t > c.glass ? .35 + .65 * (Math.sin(t * 14 + i * 2.3) > .2 ? 1 : .15) : .4); });
    // shark swims up to the cable and "bites", then turns grey on "zero"
    const ks = clamp((t - c.so) / (c.zero - c.so + .6));
    shark.position.set(lerp(-6, -.4, ease(ks)), lerp(1.8, .7, ease(ks)), lerp(-2, 1.2, ease(ks))); shark.rotation.y = lerp(1.2, .5, ease(ks)); shark.userData.tail.rotation.y = Math.sin(t * 8) * .35;
    shark.visible = t > c.so - .1 && t < c.real; shark.children[0].material.color.set(t > c.zero ? 0x3a3f45 : 0x4f5d6b);
    // anchor drags across the seabed and snags the cable on "anchors"
    const ka = clamp((t - c.real) / (c.week - c.real + .5));
    anchor.position.set(lerp(-2.6, 1.4, ease(ka)), lerp(6, .35, ease(Math.min(1, ka * 2))), -11.6); anchorL.position.copy(anchor.position).add(V(2, 3, 3)); anchorL.intensity = anchor.visible ? 30 : 0; anchor.rotation.z = -.4 + ka * .4; anchor.visible = t > c.real - .1 && t < c.only;
    const top = V(-10, 30, -11.6), ap = anchor.position.clone().add(V(0, 1.6, 0)); chain.position.copy(top.clone().lerp(ap, .5)); chain.scale.y = top.distanceTo(ap); chain.lookAt(ap); chain.rotateX(Math.PI / 2); chain.visible = anchor.visible;
    hull.position.set(-10, 30.8, -11.6); hull.visible = anchor.visible;
    // hook: descends on "drop", drags, lifts the cable on "haul"
    const kh = clamp((t - c.drop) / (c.haul - c.drop)), ku = clamp((t - c.haul) / (c.daylight - c.haul));
    hook.position.set(lerp(-3, 0, ease(kh)), lerp(14, .5, ease(Math.min(1, kh * 1.6))) + ku * 12, lerp(-2, -2.3, kh)); hook.visible = t > c.drop - .1 && t < c.daylight;
    const lt = V(hook.position.x, 40, hook.position.z), lb = hook.position.clone().add(V(0, 1.2, 0)); line.position.copy(lt.clone().lerp(lb, .5)); line.scale.y = lt.distanceTo(lb); line.visible = hook.visible;
    // the cable itself lifts with the hook (bend near the gap)
    cable.position.y = ku * 6; cableGlow.position.y = .13 + ku * 6;
    // repair ship scene: line from crane into the sea, the lifted cable rises into frame
    liftCable.position.set(7.6, lerp(-3.5, 2.2, ramp(t, c.daylight - .2, c.daylight + 1.2)), -6); fline.position.set(7.6, 4.6, -6); fline.scale.y = 5.6; ship.position.y = Math.sin(t * .8) * .08;
    // Red Sea: one lane in four goes dark red on "quarter"
    lanes.forEach((l, i) => { const bad = i === 1 && t > c.quarter; l.material.emissive.set(bad ? 0xff3b30 : CY); l.material.emissiveIntensity = bad ? .9 + .5 * Math.sin(t * 9) : 1.6; });
    // grade
    grade.uniforms.seed.value = Math.floor(t * 30);
    const nearCut = cutTimes.map(x => Math.abs(t - x)).reduce((a, b) => Math.min(a, b), 9);
    grade.uniforms.dip.value = nearCut < .06 ? .5 : 0;
    grade.uniforms.flash.value = Math.max(0, 1 - Math.abs(t - c.bottom) / .2) * .8 + Math.max(0, 1 - Math.abs(t - (c.daylight - .2)) / .25) * .9;
    grade.uniforms.flashCol.value.set(t > c.haul ? 1 : .6, t > c.haul ? .95 : .95, t > c.haul ? .85 : 1);
    grade.uniforms.tint.value.set(1, 1, 1); grade.uniforms.focusY.value = .47; grade.uniforms.band.value = .15;
    bloom.strength = underwater(t) ? .75 : .55;
    composer.render();
    // overlays
    const S = v => toScreen(v, camera, W, H); const items = [];
    const L = (txt, a, b, anchorV, off, sub) => { const al = win(t, a, b, .2); if (al <= 0) return; const q = S(anchorV); if (!q) return; items.push(() => O.callout(txt, q, [q[0] + off[0] * W, q[1] + off[1] * H], al, sub)); };
    L('Not via satellite', c.space, c.down, V(4, 14, -16), [-.2, .1]);
    L('Seafloor cable', c.seafloor, c.laid, V(200, .3, 4), [.15, -.15]);
    L('Garden hose', c.hose - .2, c.inside, V(298.6, .2, -.5), [-.05, -.16]);
    L('Deep-sea cable', c.hose, c.inside, V(300, .2, 0), [.12, -.2], '≈ 17–21 mm across');
    ['Polyethylene', 'Copper', 'Steel wires', 'Gel'].forEach((nm, i) => L(nm, c.inside + .4 + i * .25, c.glass + .2, V(300 + layerMeshes[i].position.x - .6, .12, 0), [-.05 - i * .02, -.1 - i * .05]));
    L('Glass fibers', c.glass, c.so - .1, V(302.6, .1, 0), [-.18, -.14], 'thinner than a hair');
    L('Fish-caused faults', c.zero + .2, c.real, V(200, .7, 1.2), [.12, -.18], 'ICPC records, 2007–2014');
    L('Anchor', c.anchors - .1, c.week + .3, V(200 + 1.4, 1.6, -11.6), [.14, -.12]);
    L('Repair ship', c.only, c.drop, V(900 + 7.6, 7.4, -6), [-.3, -.1]);
    L('Grapnel hook', c.drop + .4, c.haul, V(200, 1, -2.3), [.14, -.14]);
    L('Europe', c.europe, c.next, V(594, 1, -1), [-.04, -.1]); L('Asia', c.europe + .2, c.next, V(606, 1, -1), [.02, -.1]); L('Red Sea', c.in2024, c.next, V(600, 1, -3.5), [.1, -.08]);
    const cnt = (val, a, b, y, unit, sub, fmt) => { const al = win(t, a, b, .2); if (al > 0) items.push(() => O.counter(val, al, y, unit, sub, fmt)); };
    cnt(lerp(0, 99, ramp(t, c.more, c.more + 1.2)), c.more, c.laid, .09, '%', 'of data between continents', v => '>' + Math.round(v));
    cnt(lerp(0, 40, ramp(t, c.laid, c.forty + .3)), c.laid, c.deep - .2, .09, '×', 'around the Earth');
    cnt(0, c.zero, c.real, .09, '', 'breaks caused by fish');
    cnt(lerp(0, 200, ramp(t, c.around, c.around + 1)), c.around, c.week + .8, .09, '/yr', '≈ 3–4 every week');
    cnt(lerp(0, 60, ramp(t, c.sixty - .2, c.sixty + .8)), c.only, c.drop, .09, '', 'cable ships worldwide', v => '≈' + Math.round(v));
    cnt(lerp(0, 25, ramp(t, c.quarter - .3, c.quarter + .5)), c.quarter - .3, c.next, .09, '%', 'Europe–Asia traffic hit, 2024');
    const src = (txt, a, b) => { if (t > a && t < b) items.push(() => O.html(`<div class=src style="opacity:$A">${txt}</div>`, win(t, a, b))); };
    src('Sources: TeleGeography, ITU (2026) · Illustration', c.more, c.deep);
    src('Sources: ICPC, TeleGeography FAQ · Illustration', c.hose, c.only);
    src('Sources: ICPC, UN/ITU (2026), Scientific American · Illustration', c.only, c.next);
    if (t > c.remember + 1.2) items.push(() => O.html(`<div class=card style="top:${.07 * H}px;opacity:$A"><div style="width:${W * .07}px;height:${W * .07}px;border-radius:50%;background:${CY_CSS};display:grid;place-items:center;color:#032;font-weight:800;font-size:${W * .03}px">BB</div><div><div style="font-weight:700;font-size:${W * .032}px">Build Basics</div><div style="opacity:.6;font-size:${W * .022}px">tech, made clear</div></div><div style="background:${CY_CSS};color:#032;font-weight:800;padding:${W * .012}px ${W * .03}px;border-radius:${W * .02}px;font-size:${W * .026}px">Follow</div></div>`, ramp(t, c.remember + 1.2, c.remember + 1.7)));
    O.frameOverlay(items); O.drawCaption(caps, t);
  };
  return { duration: dur, render };
}
