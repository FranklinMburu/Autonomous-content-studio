// Video 1: "Your AI just moved out of the cloud" (NVIDIA RTX Spark / N1X). Every cue is anchored to a spoken word.
import { THREE, RoundedBoxGeometry, makeStage, camRig, toScreen, M, canvasTex, redraw, woodTex, starfield, dust, rbox, box, laptop, chip, rack, token, trail, clamp, lerp, ease, easeOut, smooth, ramp, win, rng } from './core.js';
import * as O from './overlay.js';

const ACC = 0xE8FF3A, ACC_CSS = '#E8FF3A', TEAL = 0x4fe0bf, RED = 0xff4d4d;

export async function build(timing) {
  const W = window.__W, H = window.__H;
  const st = makeStage(W, H, { fov: 30, envI: .28, exposure: 1.05 });
  const { scene, camera, composer, grade, bloom } = st;
  O.mount(ACC_CSS, '#5fe3c0');
  // ---------- word cues ----------
  const norm = s => s.toLowerCase().replace(/[^a-z0-9']/g, '');
  const words = timing.words;
  const T = (w, n = 1, from = 0) => { let c = 0; for (const x of words) { if (x.start < from) continue; if (norm(x.w) === norm(w) && ++c === n) return x.start; } console.log('[scene] missing cue ' + w + ' ' + n); return 0; };
  const E = (w, n = 1, from = 0) => { let c = 0; for (const x of words) { if (x.start < from) continue; if (norm(x.w) === norm(w) && ++c === n) return x.end; } return 0; };
  const dur = timing.duration + 1.4;
  const display = { 'october sixteenth,': 'OCT 16,', 'october sixteenth': 'OCT 16', 'twenty grace': '20 Grace', 'six thousand one hundred forty-four': '6,144',
    'one petaflop': '1 petaflop', 'a million billion': '1,000,000,000,000,000', 'a hundred and twenty-eight gigabytes': '128 GB', 'a hundred and twenty billion': '120 billion',
    'two thousand five hundred ninety-nine dollars': '$2,599' };
  const keys = new Set(['ai', 'leave', 'laptop', 'data', 'line', 'back', 'lag', 'subscription', 'private', 'chip', 'mediatek', 'cores', 'memory', 'pool', 'lap', 'arm', 'prism', 'brands', 'cloud', 'here', 'speed', 'math', 'translator']);
  const caps = O.buildCaptions(words, display, keys);

  // ---------- cue times ----------
  const c = {
    words: T('words'), leave: T('leave'), october: T('october'), dont: T("don't"), today: T('today'), center: T('center', 1), waits: T('waits'), someone: T('someone'),
    answer: T('answer'), back: T('back'), lag: T('lag'), subscription: T('subscription'), private: T('private'), ride: T('ride'),
    nvidia: T("nvidia's"), puts: T('puts'), chipW: T('chip', 1), inside: T('inside'), twenty: T('twenty', 1), mediatek: T('mediatek'), six: T('six', 1), petaflop: T('petaflop'),
    paper: T('paper'), million: T('million'), every: T('every', 2), but: T('but'), trick: T('trick'), memory: T('memory', 1), gaming: T('gaming'), two: T('two', 1),
    here1: T('here', 1), pool: T('pool'), says: T('says'), runs: T('runs'), lap: T('lap'), catchW: T('catch'), arm: T('arm'), older: T('older'), prism: T('prism'),
    starts: T('starts'), sixB: T('six', 2), next: T('next'), cloud: T('cloud'), live2: T('live', 2), here2: T('here', 2)
  };

  // ======================= SET A: the desk by the window (origin) =======================
  const A = new THREE.Group(); scene.add(A);
  const wood = woodTex(4); wood.wrapS = wood.wrapT = THREE.RepeatWrapping; wood.repeat.set(2, 1);
  const desk = new THREE.Mesh(new THREE.BoxGeometry(16, .3, 9), M.std(0xffffff, .55, 0, { map: wood })); desk.position.y = -.15; desk.receiveShadow = true; A.add(desk);
  const floorDark = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), M.std(0x07080a, .9)); floorDark.rotation.x = -Math.PI / 2; floorDark.position.y = -3; A.add(floorDark);
  // back wall with a big window
  const wallM = M.std(0x15161a, .9);
  const wl = box(8, 9, .3, wallM); wl.position.set(-9.5, 2.5, -4.6); A.add(wl); const wr = wl.clone(); wr.position.x = 9.5; A.add(wr);
  const wt = box(30, 3, .3, wallM); wt.position.set(0, 7.2, -4.6); A.add(wt); const wb = box(30, 1.4, .3, wallM); wb.position.set(0, -.5, -4.6); A.add(wb);
  for (const x of [-5.5, -1.85, 1.85, 5.5]) { const m = box(.12, 5.6, .2, M.std(0x24262b, .5, .5)); m.position.set(x, 3.0, -4.5); A.add(m); }
  const sill = box(11.2, .12, .5, M.std(0x24262b, .5, .5)); sill.position.set(0, .25, -4.4); A.add(sill);
  // outside: night sky, layered hills with snow and pines, distant city lights (all procedural)
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(140, 60), new THREE.MeshBasicMaterial({ map: canvasTex(512, 512, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#05070d'); gr.addColorStop(.55, '#0f1a2e'); gr.addColorStop(.8, '#1f2c44'); gr.addColorStop(1, '#2a3550');
    g.fillStyle = gr; g.fillRect(0, 0, w, h); const r = rng(9); for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(220,230,255,${r() * .8})`; const s = r() < .05 ? 1.6 : .8; g.fillRect(r() * w, r() * h * .7, s, s); }
  }), toneMapped: false })); sky.position.set(0, 14, -60); A.add(sky);
  const hillM = (col) => new THREE.MeshBasicMaterial({ color: col });
  const mkHills = (z, y, amp, col, seed, pines) => {
    const r = rng(seed), sh = new THREE.Shape(); sh.moveTo(-70, -10); for (let x = -70; x <= 70; x += 2) sh.lineTo(x, Math.sin(x * .07 + seed) * amp + Math.sin(x * .19 + seed * 2) * amp * .4 + y); sh.lineTo(70, -10);
    const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), hillM(col)); m.position.z = z; A.add(m);
    if (pines) { const pg = new THREE.ConeGeometry(.35, 1.3, 5); const pm = new THREE.InstancedMesh(pg, hillM(0x06090d), pines); const o = new THREE.Object3D();
      for (let i = 0; i < pines; i++) { const x = (r() - .5) * 60; o.position.set(x, Math.sin(x * .07 + seed) * amp + Math.sin(x * .19 + seed * 2) * amp * .4 + y + .4, z + .1); o.scale.setScalar(.6 + r() * .9); o.updateMatrix(); pm.setMatrixAt(i, o.matrix); } A.add(pm); }
  };
  mkHills(-50, 2.2, 1.6, 0x1a2234, 3, 0); mkHills(-34, 1.0, 1.0, 0x111827, 5, 120); mkHills(-20, -.6, .7, 0x0b0f17, 8, 90);
  const cityN = 260, city = new THREE.InstancedMesh(new THREE.SphereGeometry(.05, 4, 4), M.basic(0xffd59a, { toneMapped: false }), cityN); { const r = rng(21), o = new THREE.Object3D();
    for (let i = 0; i < cityN; i++) { o.position.set((r() - .5) * 40, -.2 + r() * 1.2, -27 - r() * 5); o.updateMatrix(); city.setMatrixAt(i, o.matrix); } A.add(city); }
  const stars = starfield(900, 70, 4, .18); stars.position.set(0, 20, -60); A.add(stars);
  // props: mug, laptop, router
  const mug = new THREE.Group(); const mugB = new THREE.Mesh(new THREE.CylinderGeometry(.32, .29, .72, 32), M.phys(0xe8e6e1, .3, 0, { clearcoat: .7 })); mugB.position.y = .36; mugB.castShadow = true; mug.add(mugB);
  const coffee = new THREE.Mesh(new THREE.CircleGeometry(.29, 32), M.std(0x2a1608, .2)); coffee.rotation.x = -Math.PI / 2; coffee.position.y = .66; mug.add(coffee);
  const handle = new THREE.Mesh(new THREE.TorusGeometry(.17, .05, 12, 24), mugB.material); handle.position.set(.36, .38, 0); mug.add(handle); mug.position.set(-2.6, 0, -.6); A.add(mug);
  // screen UI drawer: an assistant app, typing, and states
  let screenState = { type: 0, mode: 'chat', answer: 0, spinner: 0, files: 1 };
  const drawScreen = (g, w, h) => {
    const s = screenState; g.fillStyle = '#0c0e13'; g.fillRect(0, 0, w, h);
    g.fillStyle = '#171b24'; g.fillRect(0, 0, 300, h); g.fillStyle = '#c3cad6'; g.font = '700 44px Inter'; g.fillText('Assistant', 30, 70);
    ['Today', 'Notes', 'Plans', 'Ideas'].forEach((x, i) => { g.fillStyle = i === 1 ? '#2b3140' : 'rgba(0,0,0,0)'; g.fillRect(16, 120 + i * 80, 268, 64); g.fillStyle = '#98a2b3'; g.font = '36px Inter'; g.fillText(x, 34, 164 + i * 80); });
    if (s.mode === 'chat') {
      g.fillStyle = '#222836'; g.beginPath(); g.roundRect(340, h - 170, w - 390, 110, 55); g.fill();
      const q = 'Summarise my notes from this week'; g.fillStyle = '#eef1f6'; g.font = '44px Inter'; g.fillText(q.slice(0, Math.floor(q.length * s.type)) + (s.type < 1 ? '|' : ''), 384, h - 100);
      if (s.spinner > 0) { g.save(); g.translate(w / 2 + 110, h / 2 - 40); g.rotate(s.spinner * 9); g.strokeStyle = '#ff6b6b'; g.lineWidth = 8; g.beginPath(); g.arc(0, 0, 46, 0, Math.PI * 1.4); g.stroke(); g.restore();
        g.fillStyle = '#ff8a8a'; g.font = '600 26px Inter'; g.textAlign = 'center'; g.fillText('Waiting for the server…', w / 2 + 110, h / 2 + 50); g.textAlign = 'left'; }
      if (s.answer > 0) {
        g.globalAlpha = s.answer; g.fillStyle = '#eef1f6'; g.font = '700 46px Inter'; g.fillText('Your notes, summarised:', 360, 130);
        ['1. Launch moves to Friday', '2. Budget approved', '3. Send draft to Sam'].forEach((x, i) => { g.font = '42px Inter'; g.fillStyle = '#d3d9e4'; g.fillText(x, 360, 220 + i * 76); });
        g.globalAlpha = 1;
      }
      g.fillStyle = ACC_CSS; g.beginPath(); g.arc(w - 110, h - 115, 36, 0, 7); g.fill();
    }
  };
  const lap = laptop({ screen: drawScreen, screenGlow: 0x9db8ff }); lap.position.set(0, 0, 0); A.add(lap);
  const lapScr = lap.userData.tex;
  const router = new THREE.Group(); const rb = rbox(1.1, .22, .7, .06, M.std(0xe9e7e2, .45)); rb.position.y = .11; router.add(rb);
  for (const x of [-.4, .4]) { const ant = new THREE.Mesh(new THREE.CylinderGeometry(.03, .035, 1.1, 10), M.std(0x222, .5)); ant.position.set(x, .7, -.28); ant.rotation.z = x * .25; router.add(ant); }
  const rl = new THREE.InstancedMesh(new THREE.SphereGeometry(.025, 6, 6), M.basic(0x5dff8a, { toneMapped: false }), 5); { const o = new THREE.Object3D(); for (let i = 0; i < 5; i++) { o.position.set(-.3 + i * .15, .13, .355); o.updateMatrix(); rl.setMatrixAt(i, o.matrix); } } router.add(rl);
  router.position.set(3.4, 0, -2.4); router.rotation.y = -.4; A.add(router);
  // lights
  const key = new THREE.SpotLight(0xffd2a1, 34, 30, .5, .6, 1.6); key.position.set(-4, 7, 4); key.target.position.set(0, 0, -.5); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -.0004; A.add(key, key.target);
  const moon = new THREE.DirectionalLight(0x7d9cff, .9); moon.position.set(2, 6, -10); A.add(moon);
  const hemi = new THREE.HemisphereLight(0x33405e, 0x120c08, .35); scene.add(hemi);
  const dA = dust(420, [12, 6, 8], [0, 2.5, -1], 3); A.add(dA);

  // the hero token
  const tok = token(ACC); scene.add(tok);
  const others = []; for (let i = 0; i < 6; i++) { const o = token(0x8a8f99); o.userData.light.intensity = 0; o.children[0].material = o.children[0].material.clone(); o.children[0].material.emissiveIntensity = .15; o.children[0].material.color.set(0x5c6270); others.push(o); scene.add(o); }

  // ======================= SET B: data center exterior (x=200) and aisle (x=300) =======================
  const B = new THREE.Group(); B.position.x = 200; scene.add(B);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), M.std(0x0c0f15, .95)); ground.rotation.x = -Math.PI / 2; B.add(ground);
  const bld = box(16, 5, 7, M.std(0x2b313c, .7, .2)); bld.position.set(0, 2.5, -6); B.add(bld);
  const winTex = canvasTex(1024, 256, (g, w, h) => { g.fillStyle = '#1d222b'; g.fillRect(0, 0, w, h); for (let r = 0; r < 3; r++) for (let i = 0; i < 22; i++) { g.fillStyle = (i * 7 + r * 3) % 9 ? '#dfe9ff' : '#2b3340'; g.fillRect(24 + i * 45, 40 + r * 70, 30, 34); } });
  const facade = new THREE.Mesh(new THREE.PlaneGeometry(15.6, 4), new THREE.MeshBasicMaterial({ map: winTex, toneMapped: false })); facade.position.set(0, 2.6, -2.49); B.add(facade);
  for (let i = 0; i < 8; i++) { const u = box(1.2, .8, 1.2, M.std(0x3a414d, .6, .4)); u.position.set(-6 + i * 1.7, 5.4, -6); B.add(u); }
  const lamp = new THREE.PointLight(0xbfd6ff, 30, 30, 2); lamp.position.set(0, 7, 4); B.add(lamp);
  const bs = starfield(800, 60, 8, .16); bs.position.set(0, 10, -20); B.add(bs);
  const bDust = dust(200, [20, 8, 20], [0, 3, 0], 9, .03, 0xbcd0ff); B.add(bDust);

  const C = new THREE.Group(); C.position.x = 300; scene.add(C);
  const tiles = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#c9ced6'; g.fillRect(0, 0, w, h); g.strokeStyle = '#8c939e'; g.lineWidth = 6; for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(i * w / 4, 0); g.lineTo(i * w / 4, h); g.stroke(); g.beginPath(); g.moveTo(0, i * h / 4); g.lineTo(w, i * h / 4); g.stroke(); } g.fillStyle = '#6d7480'; for (let i = 0; i < 2; i++) g.fillRect(140 + i * 256, 40, 100, 180); });
  tiles.wrapS = tiles.wrapT = THREE.RepeatWrapping; tiles.repeat.set(3, 12);
  const cf = new THREE.Mesh(new THREE.PlaneGeometry(6, 48), M.std(0xffffff, .35, .1, { map: tiles })); cf.rotation.x = -Math.PI / 2; cf.position.z = -18; C.add(cf);
  const racks = []; for (let i = 0; i < 12; i++) for (const s of [-1, 1]) { const r = rack(4.2, i * 2 + (s > 0)); r.position.set(s * 2.0, 0, -i * 1.5 - 1); r.rotation.y = -s * Math.PI / 2; C.add(r); racks.push(r); }
  for (let i = 0; i < 6; i++) { const strip = box(.25, .05, 5, M.glow(0xdbe8ff, 3)); strip.position.set(0, 5.2, -4 - i * 6); C.add(strip); }
  const ceil = box(6, .1, 48, M.std(0x1a1d22, .8)); ceil.position.set(0, 5.4, -18); C.add(ceil);
  const aisleL = new THREE.PointLight(0xdbe8ff, 70, 26, 2); aisleL.position.set(0, 4.6, -8); C.add(aisleL); const aisleL2 = aisleL.clone(); aisleL2.position.z = -22; C.add(aisleL2);

  // ======================= SET D: the chip, macro (x=400) =======================
  const D = new THREE.Group(); D.position.x = 400; scene.add(D);
  const pcb = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#101317'; g.fillRect(0, 0, w, h); const r = rng(31); g.strokeStyle = 'rgba(120,140,160,.18)'; g.lineWidth = 3;
    for (let i = 0; i < 90; i++) { let x = r() * w, y = r() * h; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 4; k++) { if (r() < .5) x += (r() - .5) * 300; else y += (r() - .5) * 300; g.lineTo(x, y); } g.stroke(); g.fillStyle = 'rgba(150,170,190,.25)'; g.beginPath(); g.arc(x, y, 6, 0, 7); g.fill(); } });
  const board = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), M.std(0xffffff, .55, .4, { map: pcb })); board.rotation.x = -Math.PI / 2; board.receiveShadow = true; D.add(board);
  const ch = chip({ size: 2.2 }); ch.position.y = .02; D.add(ch);
  const pipes = []; for (const s of [-1, 1]) { const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(s * .5, .2, -1.6), new THREE.Vector3(s * .5, .35, -2.8), new THREE.Vector3(s * 1.6, .35, -3.6), new THREE.Vector3(s * 3.4, .35, -3.4)]);
    const p = new THREE.Mesh(new THREE.TubeGeometry(curve, 60, .12, 14), M.phys(0xd27a43, .28, 1)); p.castShadow = true; D.add(p); pipes.push(p); }
  const dk = new THREE.SpotLight(0xffffff, 18, 20, .55, .5, 1.5); dk.position.set(-3, 7, 3); dk.target.position.set(0, 0, 0); dk.castShadow = true; dk.shadow.mapSize.set(1024, 1024); D.add(dk, dk.target);
  const drim = new THREE.PointLight(ACC, 0, 8, 2); drim.position.set(0, 1.5, 0); D.add(drim);
  const dD = dust(260, [10, 4, 10], [0, 1.5, 0], 13, .02, 0xe6ffd0); D.add(dD);
  // the "data center shrinks into a chip" proxy: a mini building that scales down onto the chip
  const mini = new THREE.Group(); { const b = box(3.2, 1, 1.4, M.std(0x2b313c, .7, .2)); b.position.y = .5; mini.add(b); const f = new THREE.Mesh(new THREE.PlaneGeometry(3.1, .8), new THREE.MeshBasicMaterial({ map: winTex, toneMapped: false })); f.position.set(0, .52, .71); mini.add(f); } D.add(mini);

  // ======================= SET E: memory board (x=500) =======================
  const Eg = new THREE.Group(); Eg.position.x = 500; scene.add(Eg);
  const board2 = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), M.std(0xffffff, .55, .4, { map: pcb })); board2.rotation.x = -Math.PI / 2; Eg.add(board2);
  const cpuB = rbox(1.2, .18, 1.2, .05, M.phys(0x9fb2cf, .35, .7)); cpuB.position.set(-2.2, .09, 0); Eg.add(cpuB);
  const gpuB = rbox(1.5, .18, 1.5, .05, M.phys(0x9cff3a, .35, .3, { emissive: 0x2a4410 })); gpuB.position.set(2.2, .09, 0); Eg.add(gpuB);
  const mk = (n, x, z0, col) => { const a = []; for (let i = 0; i < n; i++) { const m = rbox(.7, .14, .38, .03, M.phys(col, .3, .4, { emissive: col, emissiveIntensity: .12 })); m.position.set(x, .07, z0 + i * .5); Eg.add(m); a.push(m); } return a; };
  const memA = mk(4, -2.2, -2.9, 0xe9e9ee), memB = mk(4, 2.2, -2.9, 0xf2b7c4);
  const wall = box(.12, .9, 7, M.phys(0x30343c, .3, .2, { transparent: true, opacity: .9 })); wall.position.set(0, .45, -1); Eg.add(wall);
  const pool = rbox(5.6, .16, 2.1, .06, M.phys(TEAL, .25, .1, { emissive: TEAL, emissiveIntensity: .22, transparent: true, opacity: .92 })); pool.position.set(0, .08, -2.2); Eg.add(pool);
  const model = new THREE.Group(); { const cub = new THREE.InstancedMesh(new RoundedBoxGeometry(.13, .13, .13, 2, .02), M.phys(ACC, .3, 0, { emissive: ACC, emissiveIntensity: .3 }), 216); const o = new THREE.Object3D(); let i = 0;
    for (let x = 0; x < 9; x++) for (let y = 0; y < 3; y++) for (let z = 0; z < 8; z++) { o.position.set(-.72 + x * .18, y * .18, -.63 + z * .18); o.updateMatrix(); cub.setMatrixAt(i++, o.matrix); } model.add(cub); } Eg.add(model);
  const ek = new THREE.SpotLight(0xffffff, 16, 22, .6, .5, 1.4); ek.position.set(-2, 8, 4); ek.target.position.set(0, 0, -1); ek.castShadow = true; Eg.add(ek, ek.target);
  const eD = dust(200, [10, 4, 10], [0, 1.5, -1], 17, .02, 0xd6fff4); Eg.add(eD);

  // ======================= SET F: Prism, the catch (x=600) =======================
  const F = new THREE.Group(); F.position.x = 600; scene.add(F);
  const ff = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), M.std(0x0d0b0c, .6, .3)); ff.rotation.x = -Math.PI / 2; F.add(ff);
  const grid = new THREE.GridHelper(40, 40, 0x3a2224, 0x231416); grid.position.y = .01; F.add(grid);
  const plinth = rbox(1.6, .5, 1.6, .06, M.std(0x18191c, .4, .6)); plinth.position.set(0, .25, 0); F.add(plinth);
  const armChip = chip({ size: 1.1 }); armChip.position.set(0, .52, 0); F.add(armChip);
  const gate = new THREE.Group(); { const fr = new THREE.Mesh(new THREE.TorusGeometry(1.25, .045, 12, 64), M.glow(0xff8a7a, .7)); gate.add(fr); const glass = new THREE.Mesh(new THREE.CircleGeometry(1.2, 64), M.phys(0xffc9c0, .05, 0, { transmission: .9, transparent: true, opacity: .25, roughness: .1 })); gate.add(glass); }
  gate.position.set(-2.4, 1.6, 0); gate.rotation.y = Math.PI / 2; F.add(gate);
  const appTex = (lines, title) => canvasTex(640, 420, (g, w, h) => { g.fillStyle = '#d4d0c8'; g.fillRect(0, 0, w, h); g.fillStyle = '#0a246a'; g.fillRect(0, 0, w, 40); g.fillStyle = '#fff'; g.font = '600 22px Inter'; g.fillText(title, 14, 28);
    g.fillStyle = '#fff'; g.fillRect(12, 56, w - 24, h - 70); g.fillStyle = '#111'; g.font = '30px "DejaVu Sans Mono"'; lines.forEach((l, i) => g.fillText(l, 30, 110 + i * 56)); });
  const appX86 = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.45), new THREE.MeshBasicMaterial({ map: appTex(['MOV EAX, 5', 'ADD EAX, EBX', 'CMP EAX, 9', 'JNE loop'], 'old_app.exe  ·  x86'), toneMapped: false }));
  const appArm = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.45), new THREE.MeshBasicMaterial({ map: appTex(['MOV W0, #5', 'ADD W0, W0, W1', 'CMP W0, #9', 'B.NE loop'], 'old_app.exe  ·  translated'), toneMapped: false, transparent: true }));
  F.add(appX86, appArm);
  const redL = new THREE.PointLight(0xff3b30, 14, 16, 2); redL.position.set(0, 4, 2); F.add(redL);
  const fD = dust(200, [10, 5, 10], [0, 2, 0], 19, .025, 0xffc4bd); F.add(fD);

  // ======================= SET G: six laptops + the hero close (x=700) =======================
  const G = new THREE.Group(); G.position.x = 700; scene.add(G);
  const gf = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), M.std(0x2a2b2f, .65, .1)); gf.rotation.x = -Math.PI / 2; gf.receiveShadow = true; G.add(gf);
  const row = []; const brands = ['ASUS', 'Dell', 'HP', 'Lenovo', 'Microsoft', 'MSI'];
  const rr = rng(77); for (let i = 0; i < 6; i++) { const l = laptop({ open: 1, color: [0xb9bcc2, 0x2d2f33, 0xc9c3b8, 0x55585f, 0xa9b0bb, 0x1f2023][i], screen: (g, w, h) => { g.fillStyle = '#10131a'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a3140'; for (let k = 0; k < 6; k++) g.fillRect(80, 90 + k * 90, 600 + rr() * 400, 36); } });
    l.position.set((i % 3 - 1) * 4.2, 0, -Math.floor(i / 3) * 4.2 - 1); l.rotation.y = (rr() - .5) * .5; l.scale.setScalar(.9); G.add(l); row.push(l); }
  const hero = laptop({ open: 1, screen: drawScreen }); hero.position.set(0, 0, 4.5); G.add(hero);
  const xchip = chip({ size: .62 }); xchip.position.set(0, .05, 4.3); G.add(xchip);
  const gk = new THREE.SpotLight(0xffffff, 40, 30, .5, .7, 1.4); gk.position.set(0, 9, 7); gk.target.position.set(0, 0, 3); gk.castShadow = true; gk.shadow.mapSize.set(1024, 1024); G.add(gk, gk.target);
  const gfill = new THREE.PointLight(0x9db8ff, 10, 20, 2); gfill.position.set(-4, 3, 0); G.add(gfill);
  const gD = dust(260, [14, 5, 14], [0, 2, 0], 23); G.add(gD);

  // ---------- token flight paths ----------
  const pOut = [[0, 1.25, -.8], [.6, 2.2, -2.8], [1.4, 3.0, -4.6], [3, 3.4, -12], [6, 4, -30]];
  const trOut = trail(pOut, ACC, .025); A.add(trOut);
  const pBack = [[6, 4, -30], [-2, 4.5, -12], [-1, 3.1, -4.6], [-.4, 2, -2.2], [0, 1.25, -.8]];
  const trBack = trail(pBack, TEAL, .025); A.add(trBack);
  const pToRouter = [[0, 1.25, -.8], [1.8, 1.4, -1.8], [3.3, 1.1, -2.4]];

  // ---------- the camera: shot list (keys anchored to words) ----------
  const X = (set, p) => [p[0] + set, p[1], p[2]];
  const keysCam = [
    { t: 0, p: [0.9, 1.15, 3.6], l: [0, 1.0, -.5], fov: 28 },                                  // 1 low, warm close on the laptop
    { t: c.words - .2, p: [0.5, 1.5, 3.0], l: [0, 1.3, -1.2], fov: 30 },
    { t: c.leave + .5, p: [-0.2, 2.2, 2.0], l: [1.4, 2.8, -6], fov: 34 },                         // follow token toward the window
    { t: c.october, p: [0.6, 1.6, 4.4], l: [0, 1.3, -1.5], fov: 30 },                              // pull back: the token is called home
    { t: c.today - .2, p: [0.4, 1.9, 3.4], l: [0, 1.5, -2], fov: 32 },
    { t: c.today + .9, p: [0.2, 2.6, 0.8], l: [3, 3.5, -14], fov: 40 },                            // look out of the window along the trail
    { t: c.center - .15, p: [1.5, 3.3, -6], l: [5.5, 3.9, -28], fov: 42 },
    { t: c.center + .25, p: X(200, [0, 2.2, 22]), l: X(200, [0, 2.6, -4]), fov: 34, cut: 1 },     // 2 the data center at night (glow cut)
    { t: c.waits - .2, p: X(200, [0, 2.0, 7]), l: X(200, [0, 2.3, -4]), fov: 34 },
    { t: c.waits + .05, p: X(300, [.5, 1.8, 3]), l: X(300, [0, 1.6, -14]), fov: 38, cut: 1 },      // 3 inside: the queue in the aisle
    { t: c.someone, p: X(300, [-.6, 1.5, -7]), l: X(300, [1.6, 2.2, -9.5]), fov: 36 },
    { t: c.answer, p: X(300, [-.4, 1.7, -8.2]), l: X(300, [1.6, 2.0, -9.8]), fov: 32 },
    { t: c.back - .1, p: [-0.4, 3.2, -1.2], l: [0, 1.2, -.8], fov: 36, cut: 1 },                  // 4 back home (whip)
    { t: c.lag, p: [1.2, 1.7, 3.2], l: [0, 1.2, -1], fov: 30 },
    { t: c.private, p: [2.0, 2.0, 2.6], l: [.6, 1.3, -1.3], fov: 30 },
    { t: c.nvidia - .1, p: [1.0, 2.6, 4.0], l: [0, 1.1, -1], fov: 30 },
    { t: c.nvidia + .05, p: X(400, [0, 6.5, 6.5]), l: X(400, [0, .4, 0]), fov: 30, cut: 1 },       // 5 a data center shrinks into a chip
    { t: c.inside + .3, p: X(400, [0, 4.6, 3.4]), l: X(400, [0, .1, .2]), fov: 30 },
    { t: c.twenty, p: X(400, [0, 3.6, 1.6]), l: X(400, [0, 0, .55]), fov: 30 },                   // CPU cores, top-down macro
    { t: c.six - .1, p: X(400, [0, 3.2, .4]), l: X(400, [0, 0, -.35]), fov: 32 },                 // GPU cells
    { t: c.petaflop - .1, p: X(400, [-.2, 1.1, 1.2]), l: X(400, [0, .1, -.6]), fov: 40, roll: .1 },// dive low across the cells
    { t: c.every + .2, p: X(400, [.3, .55, -.1]), l: X(400, [0, .1, -1.2]), fov: 46, roll: -.05 },
    { t: c.but - .05, p: X(400, [0, 7, 2.5]), l: X(400, [0, 0, 0]), fov: 30 },                    // 6 rise up and out: the real trick
    { t: c.gaming - .1, p: X(500, [0, 7.5, 6]), l: X(500, [0, 0, -1.2]), fov: 30, cut: 1 },       // 7 memory board
    { t: c.here1, p: X(500, [0, 6.2, 4.6]), l: X(500, [0, 0, -1.6]), fov: 30 },
    { t: c.says, p: X(500, [2.5, 4.2, 3.2]), l: X(500, [0, .2, -1.9]), fov: 32 },
    { t: c.lap + .2, p: X(500, [1.2, 3.2, 2.2]), l: X(500, [0, .2, -2]), fov: 32 },
    { t: c.catchW - .05, p: X(600, [3.4, 2.4, 6.5]), l: X(600, [0, 1, 0]), fov: 30, cut: 1 },     // 8 the catch, red light
    { t: c.older, p: X(600, [.6, 2.0, 5.5]), l: X(600, [-1.6, 1.4, 0]), fov: 32 },
    { t: c.starts, p: X(600, [-.5, 1.8, 4.6]), l: X(600, [-2.6, 1.5, 0]), fov: 32 },
    { t: c.sixB - .05, p: X(700, [0, 6.0, 12]), l: X(700, [0, .6, -2]), fov: 34, cut: 1 },        // 9 six brands, then home
    { t: c.next, p: X(700, [0, 3.2, 10]), l: X(700, [0, .8, 3]), fov: 32 },
    { t: c.here2, p: X(700, [.6, 2.0, 7.6]), l: X(700, [0, .5, 4.2]), fov: 30 },
    { t: dur, p: X(700, [.4, 1.7, 7.0]), l: X(700, [0, .4, 4.2]), fov: 29 }
  ];
  for (const k of keysCam) { const f = k.l[0] < 100 ? 2.4 : k.l[0] > 350 && k.l[0] < 650 ? 2.0 : k.l[0] >= 650 ? 1.35 : 1; k.p = k.p.map((v, i) => k.l[i] + (v - k.l[i]) * f); }
  const cam = camRig(camera, keysCam, .012);

  // ---------- per-frame state ----------
  const V = (...a) => new THREE.Vector3(...a);
  const at = (curve, k) => curve.getPointAt(clamp(k));
  const cutTimes = keysCam.filter(k => k.cut).map(k => k.t);
  const render = (t) => {
    cam(t);
    if (window.__camO) { const o = window.__camO; camera.position.set(...o.p); camera.lookAt(...o.l); camera.fov = o.fov || 40; camera.updateProjectionMatrix(); }
    for (const d of [dA, bDust, dD, eD, fD, gD]) d.userData.tick(t);
    racks.forEach((r, i) => i % 3 === 0 && r.userData.tick(t + i));
    // ----- SET A behaviour -----
    const typing = clamp((t - .3) / Math.max(.5, c.words - .5));
    screenState = { mode: 'chat', type: typing, answer: clamp((t - c.back - .4) / .5) * (t < c.lag ? 1 : 0) + (t > c.next ? clamp((t - c.next) / .6) : 0), spinner: t > c.lag && t < c.subscription ? t : 0 };
    if (Math.floor(t * 15) !== lapScr.userData.f) { lapScr.userData.f = Math.floor(t * 15); redraw(lapScr, drawScreen); if (t > c.sixB) redraw(hero.userData.tex, drawScreen); }
    lap.userData.glowLight.intensity = 1.6;
    // the token: pops out of the screen on "words", flies toward the window on "leave", is called home on "october",
    // then on "today" leaves for real along the trail; returns as the answer (teal) on "back".
    let tp = V(0, 1.25, -.8), ts = 0, tcol = ACC;
    if (t >= c.words - .1 && t < c.october) { const k = easeOut((t - c.words + .1) / .5); ts = k; const k2 = ease((t - c.leave) / (c.october - c.leave)); tp = at(trOut.userData.curve, .32 * k2).clone(); tp.y += .15 * Math.sin(t * 3); }
    if (t >= c.october && t < c.today) { const k = ease((t - c.october) / .8); const p0 = at(trOut.userData.curve, .32); tp = p0.lerp(V(0, 1.25, -.8), k); ts = 1 - .3 * k; }
    if (t >= c.today && t < c.center + .25) { const k = ease((t - c.today) / (c.center + .2 - c.today)); tp = at(trOut.userData.curve, k); ts = 1; trOut.userData.set(k); }
    else if (t < c.today) trOut.userData.set(t > c.leave ? clamp((t - c.leave) / .6) * .32 * (t < c.october ? 1 : 1 - clamp((t - c.october) / .8)) : 0);
    else trOut.userData.set(1, clamp((t - c.center) / .2));
    if (t >= c.back - .1 && t < c.lag + .3) { tcol = TEAL; const k = ease((t - c.back + .1) / .9); tp = at(trBack.userData.curve, .55 + .45 * k); ts = 1; trBack.userData.set(.55 + .45 * k, .55); } else trBack.userData.set(0);
    // in the data center: our token joins a queue of other people's requests
    const inB = t >= c.center + .25 && t < c.waits + .05, inC = t >= c.waits + .05 && t < c.back - .1;
    if (inB) { const k = ease((t - c.center - .25) / (c.waits - c.center)); tp = V(200 + lerp(-3, 0, k), lerp(5, 2.6, k), lerp(12, -1.5, k)); ts = 1.4; }
    if (inC) {
      const q0 = c.waits + .05, k = clamp((t - q0) / (c.someone - q0));
      others.forEach((o, i) => { o.visible = true; o.position.set(300 + .15 * Math.sin(i * 3), 1.6, -2.5 - i * .9 - k * .9 * Math.min(i, 1)); o.rotation.y = Math.PI / 2; o.scale.setScalar(.9); });
      tp = V(300, 1.6, lerp(1.5, -1.6, ease(k * 1.4))); ts = 1;
      if (t > c.someone) { const k2 = ease((t - c.someone) / .8); tp = V(300 + lerp(0, 1.25, k2), lerp(1.6, 2.1, k2), lerp(-1.6, -9.5, k2)); }
      if (t > c.answer) { tcol = TEAL; const k3 = ease((t - c.answer) / (c.back - c.answer)); tp = V(300 + lerp(1.25, 0, k3), lerp(2.1, 3.5, k3), lerp(-9.5, 4, k3)); }
    } else others.forEach(o => o.visible = false);
    tok.position.copy(tp); tok.scale.setScalar(Math.max(.001, ts * (t > c.nvidia ? 0 : 1))); tok.lookAt(camera.position);
    tok.userData.card.material.color.set(t > c.lag && t < c.subscription ? RED : tcol); tok.userData.card.material.emissive.set(t > c.lag && t < c.subscription ? RED : tcol); tok.userData.light.color.set(tcol);
    // files fly out on "private"
    // ----- SET D: shrink + chip -----
    const kS = ease((t - c.puts) / Math.max(.4, c.inside - c.puts)); mini.scale.setScalar(Math.max(.001, lerp(1.6, .05, kS))); mini.position.set(0, lerp(1.4, .2, kS), 0); mini.visible = t < c.inside + .3;
    ch.scale.setScalar(easeOut((t - c.chipW) / .5) * (t > c.chipW ? 1 : 0) + .0001);
    ch.userData.cores.forEach((m, i) => { const on = t > c.twenty + i * .06; m.material.emissive.set(on ? 0x9ec5ff : 0x000000); m.material.emissiveIntensity = on ? .9 : 0; });
    const nCells = Math.floor(6144 * easeOut((t - c.six) / 2.2)); if (ch.userData.n !== nCells) { ch.userData.n = nCells; ch.userData.lightCells(nCells, ACC, t); }
    if (t > c.petaflop && Math.floor(t * 10) !== ch.userData.f) { ch.userData.f = Math.floor(t * 10); ch.userData.lightCells(6144, ACC, t); }
    drim.intensity = t > c.six ? 2.5 : 0;
    // ----- SET E: memory merge -----
    const kM = ease((t - c.here1) / 1.0);
    memA.forEach((m, i) => { m.position.x = 500 - 500 + lerp(-2.2, -1.8 + i * .0, 0); m.position.set(lerp(-2.2, -2.4 + i * 1.1, kM), .07 + .4 * Math.sin(Math.PI * kM), lerp(-2.9 + i * .5, -2.2, kM)); m.visible = kM < .98; });
    memB.forEach((m, i) => { m.position.set(lerp(2.2, -.2 + i * 1.1 - 1.2, kM) + 1.2 * kM, .07 + .4 * Math.sin(Math.PI * kM), lerp(-2.9 + i * .5, -2.2, kM)); m.visible = kM < .98; });
    wall.scale.y = Math.max(.001, 1 - kM); pool.scale.set(Math.max(.001, ramp(t, c.here1 + .6, c.here1 + 1.2)), 1, 1); pool.visible = t > c.here1 + .6;
    const kMod = ease((t - c.says) / 1.1); model.position.set(0, lerp(3.5, .24, kMod), -2.2); model.visible = t > c.says - .1; model.scale.setScalar(.95);
    // ----- SET F: Prism -----
    const kP = clamp((t - c.older) / (c.starts - c.older + .3));
    appX86.position.set(lerp(-6.5, -2.4, ease(kP * 1.6)), 1.6, 0); appX86.rotation.y = Math.PI / 2 * .0; appX86.lookAt(camera.position);
    appArm.position.set(lerp(-2.4, 1.6, ease((kP - .55) * 2.4)), 1.6, .02); appArm.lookAt(camera.position); appArm.material.opacity = clamp((kP - .5) * 4);
    appX86.visible = kP < .62; armChip.rotation.y = t * .2;
    // ----- SET G -----
    hero.userData.glowLight.intensity = 2; xchip.visible = t > c.here2 - .3; xchip.position.y = .12; hero.userData.base.material.transparent = true; hero.userData.base.material.opacity = t > c.here2 ? lerp(1, .25, ramp(t, c.here2, c.here2 + .6)) : 1;
    // ----- post: lens, flashes, dips, grade per set -----
    const nearCut = cutTimes.map(x => Math.abs(t - x)).reduce((a, b) => Math.min(a, b), 9);
    grade.uniforms.seed.value = Math.floor(t * 30);
    grade.uniforms.flash.value = (Math.abs(t - (c.center + .25)) < .18 ? 1 - Math.abs(t - (c.center + .25)) / .18 : 0) * .85;
    grade.uniforms.dip.value = nearCut < .06 ? .6 : 0;
    const inRed = t > c.catchW - .05 && t < c.sixB - .05;
    grade.uniforms.tint.value.set(inRed ? 1.12 : 1, inRed ? .9 : 1, inRed ? .9 : 1.02);
    grade.uniforms.focusY.value = .47; grade.uniforms.band.value = t > c.nvidia && t < c.gaming ? .1 : .15; grade.uniforms.blur.value = 1;
    bloom.strength = t > c.six && t < c.gaming ? .6 : .45;
    composer.render();
    // ----- overlays -----
    const S = v => toScreen(v, camera, W, H);
    const items = [];
    const L = (txt, a, b, anchor, off, sub) => { const al = win(t, a, b, .2); if (al <= 0) return; const q = S(anchor); if (!q) return; items.push(() => O.callout(txt, q, [q[0] + off[0] * W, q[1] + off[1] * H], al, sub)); };
    L('Your laptop', c.words - .2, c.leave, V(0, .9, .4), [-.18, -.12]);
    L('Data center', c.center + .3, c.waits, V(200, 4.2, -2.6), [-.2, -.14]);
    L("Someone else's computer", c.someone + .3, c.answer + .3, V(301.6, 2.6, -9.6), [-.16, -.16]);
    L('Lag', c.lag, c.subscription + .1, V(0, 1.6, -1.2), [.2, -.1]);
    L('Grace CPU', c.twenty, c.six, V(400, .1, .75), [.2, -.18], '20 cores · built with MediaTek');
    L('Blackwell GPU', c.six + .1, c.petaflop, V(400, .1, -.4), [-.22, -.16], '6,144 CUDA cores');
    L('CPU memory', c.gaming + .3, c.here1, V(497.8, .2, -2.7), [-.12, -.2]);
    L('GPU memory', c.gaming + .5, c.here1, V(502.2, .2, -2.7), [.08, -.2]);
    L('One pool', c.pool, c.says, V(500, .2, -2.2), [.16, -.16], 'shared by CPU and GPU');
    L('AI model · 120B parameters', c.says + .8, c.catchW, V(500, .6, -2.2), [-.1, -.2]);
    L('Arm', c.arm, c.older + .4, V(600, .9, 0), [.16, -.16]);
    L('Prism', c.prism - .1, c.starts + .3, V(597.6, 2.9, 0), [.1, -.12], "Microsoft's translator");
    brands.forEach((bn, i) => { const p = row[i].position; L(bn, c.sixB + i * .12, c.next, V(700 + p.x, 2.0, p.z - .8), [0, -.07]); });
    L('Here', c.here2, dur, V(700, .3, 4.3), [.2, -.12], 'the AI, on the chip');
    // counters
    const cnt = (val, a, b, y, unit, sub, fmt) => { const al = win(t, a, b, .2); if (al > 0) items.push(() => O.counter(val, al, y, unit, sub, fmt)); };
    cnt(16, c.october, c.today - .1, .1, '', 'October 2026', () => 'OCT 16');
    cnt(lerp(0, 20, ramp(t, c.twenty, c.twenty + 1.1)), c.twenty, c.six, .085, '', 'CPU cores');
    cnt(lerp(0, 6144, ramp(t, c.six, c.six + 2.2)), c.six, c.petaflop, .085, '', 'GPU cores');
    cnt(1, c.petaflop, c.million, .085, '', 'petaflop · FP4, peak', () => '1');
    cnt(lerp(1e12, 1e15, ramp(t, c.million, c.every + .4)), c.million, c.but, .09, '', 'calculations per second', v => Math.round(v / 1e9).toLocaleString('en-US') + ',000,000,000');
    cnt(lerp(0, 128, ramp(t, c.pool + .1, c.pool + 1.2)), c.pool, c.says, .09, 'GB', 'unified memory');
    cnt(2599, c.starts, c.sixB - .1, .1, '', 'starting price', () => '$2,599');
    // tags + source line + end card
    if (t > c.nvidia && t < c.catchW) items.push(() => O.html(`<div class=src style="opacity:$A">Specs: NVIDIA (FP4 peak) · Illustration</div>`, win(t, c.nvidia, c.catchW)));
    if (t > c.catchW && t < c.sixB) items.push(() => O.html(`<div class=src style="opacity:$A">Prism: Microsoft · Price: NVIDIA launch release · Illustration</div>`, win(t, c.catchW, c.sixB)));
    if (t > c.live2 + .2) items.push(() => O.html(`<div class=card style="top:${.07 * H}px;opacity:$A"><div style="width:${W * .07}px;height:${W * .07}px;border-radius:50%;background:${ACC_CSS};display:grid;place-items:center;color:#111;font-weight:800;font-size:${W * .03}px">BB</div><div><div style="font-weight:700;font-size:${W * .032}px">Build Basics</div><div style="opacity:.6;font-size:${W * .022}px">tech, made clear</div></div><div style="background:${ACC_CSS};color:#111;font-weight:800;padding:${W * .012}px ${W * .03}px;border-radius:${W * .02}px;font-size:${W * .026}px">Follow</div></div>`, ramp(t, c.live2 + .2, c.live2 + .7)));
    O.frameOverlay(items);
    O.drawCaption(caps, t);
  };
  return { duration: dur, render };
}
