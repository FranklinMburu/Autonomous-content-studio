// Core of the showcase 3D engine: renderer, cinematic post chain, environment light, camera rig, asset kit.
// Deterministic: everything is a function of t (and fixed seeds). Three.js r180, vendored by the lab workflow.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
export { THREE, RoundedBoxGeometry };

export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const smooth = k => { k = clamp(k); return k * k * (3 - 2 * k); };
export const ease = k => { k = clamp(k); return k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
export const easeOut = k => 1 - Math.pow(1 - clamp(k), 3);
export const ramp = (t, a, b) => smooth((t - a) / (b - a));
export const win = (t, a, b, f = .3) => clamp((t - a) / f) * clamp((b - t) / f);
export function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---------------- renderer + post ----------------
const TiltGrade = {
  uniforms: {
    tDiffuse: { value: null }, res: { value: new THREE.Vector2() }, focusY: { value: .5 }, band: { value: .16 }, blur: { value: 1.0 },
    vignette: { value: .38 }, grain: { value: .045 }, seed: { value: 0 }, lift: { value: new THREE.Vector3(0, 0, 0) },
    tint: { value: new THREE.Vector3(1, 1, 1) }, ca: { value: .0012 }, dip: { value: 0 }, flash: { value: 0 }, flashCol: { value: new THREE.Vector3(1, 1, .7) },
    sat: { value: 1.0 }
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform vec2 res; uniform float focusY, band, blur, vignette, grain, seed, ca, dip, flash, sat;
    uniform vec3 lift, tint, flashCol; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233))+seed*.0137)*43758.5453); }
    vec3 tap(vec2 uv){ return texture2D(tDiffuse, uv).rgb; }
    void main(){
      float d = max(0., abs(vUv.y-focusY)-band); float r = clamp(d*blur*9., 0., 1.) * 9.;
      vec3 c = vec3(0.); float wsum = 0.;
      // 12-tap golden-angle disc blur, radius grows away from the focus band (tilt-shift lens)
      for(int i=0;i<12;i++){ float a=float(i)*2.39996; float rr=sqrt(float(i)/12.)*r; vec2 o=vec2(cos(a),sin(a))*rr/res;
        float w = 1.; c += tap(vUv+o)*w; wsum += w; }
      c /= wsum;
      if(ca>0.){ vec2 dir=(vUv-.5); c.r = mix(c.r, tap(vUv+dir*ca).r, .8); c.b = mix(c.b, tap(vUv-dir*ca).b, .8); }
      float l = dot(c, vec3(.2126,.7152,.0722)); c = mix(vec3(l), c, sat);
      c = c*tint + lift*(1.-c);
      vec2 q = vUv-.5; q.x *= res.x/res.y; float v = smoothstep(.95, .2, length(q)); c *= mix(1.-vignette, 1., v);
      c += (h(vUv*res)-.5)*grain;
      c = mix(c, flashCol, flash); c *= (1.-dip);
      gl_FragColor = vec4(c,1.);
    }`
};

export function makeStage(W, H, opts = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1); renderer.setSize(W, H);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = opts.exposure ?? 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const scene = new THREE.Scene(); scene.background = new THREE.Color(opts.bg ?? 0x0b0c0f);
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = opts.envI ?? .35;
  const camera = new THREE.PerspectiveCamera(opts.fov ?? 32, W / H, .15, 900);
  const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: opts.msaa ?? 4 });
  const composer = new EffectComposer(renderer, rt);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), .5, .5, .92); composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const grade = new ShaderPass(TiltGrade); grade.uniforms.res.value.set(W, H); composer.addPass(grade);
  return { renderer, scene, camera, composer, bloom, grade, W, H };
}

// ---------------- camera rig: keys {t, p:[x,y,z], l:[x,y,z], fov} with eased segments ----------------
export function camRig(camera, keys, shake = .0) {
  const V = (a) => new THREE.Vector3(...a);
  return (t, frame) => {
    let i = keys.findIndex(k => k.t > t); if (i < 0) i = keys.length; const a = keys[Math.max(0, i - 1)], b = keys[Math.min(keys.length - 1, i)];
    const k = a === b ? 0 : (b.cut ? 0 : (b.e ?? ease)((t - a.t) / (b.t - a.t)));
    const P = V(a.p).lerp(V(b.p), k), L = V(a.l).lerp(V(b.l), k);
    if (b.arc && a !== b) { const m = Math.sin(Math.PI * k) * b.arc; P.x += m; }
    const s = (a.shake ?? shake);
    if (s) { P.x += Math.sin(t * 1.3) * s + Math.sin(t * 2.9) * s * .4; P.y += Math.sin(t * 1.7 + 1) * s * .7; }
    camera.position.copy(P); camera.lookAt(L);
    if (a.roll || b.roll) camera.rotateZ(lerp(a.roll ?? 0, b.roll ?? 0, k));
    const f = lerp(a.fov ?? camera.fov, b.fov ?? a.fov ?? camera.fov, k); if (f !== camera.fov) { camera.fov = f; camera.updateProjectionMatrix(); }
  };
}
export function toScreen(v, camera, W, H) {
  const p = v.clone().project(camera); if (p.z > 1) return null;
  return [(p.x * .5 + .5) * W, (-p.y * .5 + .5) * H];
}

// ---------------- materials + textures ----------------
export const M = {
  std: (color, rough = .5, metal = 0, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal, ...o }),
  phys: (color, rough = .3, metal = 0, o = {}) => new THREE.MeshPhysicalMaterial({ color, roughness: rough, metalness: metal, ...o }),
  glow: (color, i = 2) => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: color, emissiveIntensity: i, roughness: 1 }),
  basic: (color, o = {}) => new THREE.MeshBasicMaterial({ color, ...o })
};
export function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.userData = { c, g, draw }; return t;
}
export function redraw(tex, draw) { const { c, g } = tex.userData; g.clearRect(0, 0, c.width, c.height); draw(g, c.width, c.height); tex.needsUpdate = true; }
export function woodTex(seed = 3, base = [92, 52, 32]) {
  const r = rng(seed);
  return canvasTex(1024, 1024, (g, w, h) => {
    g.fillStyle = `rgb(${base})`; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 260; i++) {
      const y = r() * h, a = .03 + r() * .07, th = 1 + r() * 5, d = r() < .5 ? -1 : 1;
      g.strokeStyle = `rgba(${d > 0 ? '255,210,170' : '20,8,2'},${a})`; g.lineWidth = th; g.beginPath();
      for (let x = 0; x <= w; x += 16) g.lineTo(x, y + Math.sin(x * .004 + i) * 6 + Math.sin(x * .02 + i * 3) * 1.5);
      g.stroke();
    }
    for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(0,0,0,${r() * .05})`; g.fillRect(r() * w, r() * h, 1 + r() * 3, 1); }
  });
}
export function noiseTex(seed = 7, size = 256, lo = 0, hi = 255) {
  const r = rng(seed);
  return canvasTex(size, size, (g, w, h) => { const im = g.createImageData(w, h); for (let i = 0; i < w * h; i++) { const v = lo + r() * (hi - lo); im.data.set([v, v, v, 255], i * 4); } g.putImageData(im, 0, 0); }, false);
}

// ---------------- particles: stars + drifting dust (deterministic) ----------------
export function starfield(n = 1400, R = 120, seed = 11, size = .5) {
  const r = rng(seed), p = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const u = r() * 2 - 1, th = r() * Math.PI * 2, s = Math.sqrt(1 - u * u); p.set([s * Math.cos(th) * R, u * R, s * Math.sin(th) * R], i * 3); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ color: 0xcfd8ff, size, sizeAttenuation: true, transparent: true, opacity: .8, depthWrite: false }));
}
export function dust(n = 500, box = [8, 6, 8], center = [0, 1, 0], seed = 5, size = .018, color = 0xfff1d6) {
  const r = rng(seed), base = new Float32Array(n * 3), ph = new Float32Array(n);
  for (let i = 0; i < n; i++) { base.set([(r() - .5) * box[0] + center[0], (r() - .5) * box[1] + center[1], (r() - .5) * box[2] + center[2]], i * 3); ph[i] = r() * 100; }
  const g = new THREE.BufferGeometry(); const pos = new Float32Array(base); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity: .55, depthWrite: false, blending: THREE.AdditiveBlending }));
  pts.userData.tick = t => {
    for (let i = 0; i < n; i++) { const q = ph[i]; pos[i * 3] = base[i * 3] + Math.sin(t * .13 + q) * .25; pos[i * 3 + 1] = base[i * 3 + 1] + Math.sin(t * .09 + q * 1.7) * .18 + ((t * .02 + q) % 1) * .05; pos[i * 3 + 2] = base[i * 3 + 2] + Math.cos(t * .11 + q) * .25; }
    g.attributes.position.needsUpdate = true;
  };
  return pts;
}

// ---------------- reusable assets ----------------
export function rbox(w, h, d, r, mat, seg = 4) { const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, seg, r), mat); m.castShadow = m.receiveShadow = true; return m; }
export function box(w, h, d, mat) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.castShadow = m.receiveShadow = true; return m; }

// Laptop: aluminium unibody, real keyboard (instanced keys), trackpad, lid on a hinge with a live canvas screen.
export function laptop(opts = {}) {
  const W = opts.w ?? 3.2, D = opts.d ?? 2.2, T = .09;
  const alu = M.phys(opts.color ?? 0xb9bcc2, .32, .9, { clearcoat: .3, clearcoatRoughness: .4 });
  const dark = M.std(0x16171a, .55, .2);
  const g = new THREE.Group();
  const base = rbox(W, T, D, .05, alu); base.position.y = T / 2; g.add(base);
  const deck = box(W * .9, .006, D * .5, M.std(0x0f1012, .7, .1)); deck.position.set(0, T + .002, -D * .13); g.add(deck);
  const keyGeo = new RoundedBoxGeometry(.16, .025, .15, 2, .02); const kM = M.std(0x1c1d21, .6, .1);
  const cols = 15, rows = 5, keys = new THREE.InstancedMesh(keyGeo, kM, cols * rows); const o = new THREE.Object3D(); let k = 0;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) { o.position.set(-W * .43 + c * (W * .86 / (cols - 1)), T + .012, -D * .33 + r * .2); o.updateMatrix(); keys.setMatrixAt(k++, o.matrix); }
  keys.castShadow = true; g.add(keys);
  const pad = rbox(W * .32, .004, D * .26, .02, M.phys(0x9ea2a8, .25, .8)); pad.position.set(0, T + .001, D * .27); g.add(pad);
  const hinge = new THREE.Group(); hinge.position.set(0, T, -D / 2 + .02); g.add(hinge);
  const lid = rbox(W, T * .7, D * .98, .05, alu); lid.position.set(0, 0, 0); const lidG = new THREE.Group(); lidG.add(lid); lid.position.z = -D * .49; hinge.add(lidG);
  const bezel = box(W * .97, .004, D * .93, dark); bezel.position.set(0, T * .36, -D * .49); lidG.add(bezel);
  const tex = canvasTex(1280, 832, opts.screen ?? ((g2, w, h) => { g2.fillStyle = '#0d0f14'; g2.fillRect(0, 0, w, h); }));
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(W * .92, D * .86), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  screen.rotation.x = -Math.PI / 2; screen.position.set(0, T * .36 + .012, -D * .49); screen.material.polygonOffset = true; screen.material.polygonOffsetFactor = -2; lidG.add(screen);
  const glowLight = new THREE.PointLight(opts.screenGlow ?? 0x8fb3ff, 0, 5, 2); glowLight.position.set(0, .6, -D * .5); lidG.add(glowLight);
  g.userData = { hinge: lidG, tex, screen, glowLight, base, W, D, T, keys, deck };
  g.userData.open = a => { lidG.rotation.x = Math.PI - a * Math.PI * .59; };   // a = 0 closed, 1 open (~106 degrees)
  g.userData.open(opts.open ?? 1);
  return g;
}

// Chip package: substrate, ceramic stiffener frame, CPU core tiles + a GPU die whose cells can light up (instanced).
export function chip(opts = {}) {
  const g = new THREE.Group(); const S = opts.size ?? 1.6;
  const sub = rbox(S, .05, S * 1.25, .03, M.std(0x16301f, .6, .2)); g.add(sub);
  const frame = rbox(S * .92, .06, S * 1.15, .04, M.phys(0xb9b4aa, .45, 0, { clearcoat: .4 })); frame.position.y = .05; g.add(frame);
  const well = box(S * .78, .02, S * 1.0, M.std(0x0a0b0d, .4, .3)); well.position.y = .075; g.add(well);
  // GPU die (top) with a grid of cells
  const gx = 64, gy = 96, gw = S * .66, gh = S * .58, cell = new THREE.BoxGeometry(gw / gx * .82, .01, gh / gy * .82);
  const cellsM = new THREE.MeshStandardMaterial({ color: 0x0d120c, emissive: 0xffffff, emissiveIntensity: 0, roughness: .5, metalness: .2 });
  const cells = new THREE.InstancedMesh(cell, cellsM, gx * gy); const o = new THREE.Object3D(); const col = new THREE.Color();
  let i = 0; for (let y = 0; y < gy; y++) for (let x = 0; x < gx; x++) { o.position.set(-gw / 2 + (x + .5) * gw / gx, .09, -S * .45 + (y + .5) * gh / gy); o.updateMatrix(); cells.setMatrixAt(i, o.matrix); cells.setColorAt(i, col.set(0x101410)); i++; }
  g.add(cells);
  // CPU tiles (bottom): 20 cores in a 5x4 grid
  const cores = []; const cM = M.phys(0x9fb2cf, .35, .7);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 5; c++) { const m = rbox(S * .12, .025, S * .085, .006, cM.clone()); m.position.set(-S * .3 + c * S * .15, .095, S * .23 + r * S * .1); g.add(m); cores.push(m); }
  g.userData = { cells, cores, gx, gy, cellsM, S };
  g.userData.lightCells = (n, color = 0x9cff3a, t = 0) => {   // light the first n cells, sweeping row by row
    const c1 = new THREE.Color(color), c0 = new THREE.Color(0x0c100b);
    for (let j = 0; j < gx * gy; j++) { const on = j < n; const flick = on ? .55 + .45 * Math.sin(j * 12.989 + t * 6) ** 2 : 0; cells.setColorAt(j, on ? c1.clone().multiplyScalar(.35 + .65 * flick) : c0); }
    cells.instanceColor.needsUpdate = true; cellsM.emissiveIntensity = n > 0 ? 1.4 : 0;
    cellsM.emissive.set(0xffffff);
  };
  // emissive driven by instance colour: use the colour as emissive via onBeforeCompile
  cellsM.onBeforeCompile = s => { s.fragmentShader = s.fragmentShader.replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n totalEmissiveRadiance *= vColor;'); };
  cellsM.vertexColors = false; cells.instanceColor && (cells.instanceColor.needsUpdate = true);
  return g;
}

// Server rack with blinking LEDs (instanced) and perforated door look.
export function rack(h = 4.2, seed = 1) {
  const g = new THREE.Group(); const r = rng(seed);
  const body = box(1.2, h, 1.4, M.std(0x3a3f48, .4, .6)); body.position.y = h / 2; g.add(body);
  const front = box(1.1, h * .96, .02, M.std(0x0c0d10, .6, .4)); front.position.set(0, h / 2, .71); g.add(front);
  const ledG = new THREE.SphereGeometry(.018, 6, 6); const n = 140; const leds = new THREE.InstancedMesh(ledG, M.basic(0xffffff), n); const o = new THREE.Object3D(); const c = new THREE.Color();
  for (let i = 0; i < n; i++) { o.position.set(-.45 + r() * .9, .2 + r() * (h - .4), .73); o.updateMatrix(); leds.setMatrixAt(i, o.matrix); leds.setColorAt(i, c.set(r() < .7 ? 0x44ff88 : 0x4aa3ff)); }
  g.add(leds);
  for (let s = 0; s < 18; s++) { const u = box(1.06, .015, .03, M.std(0x2a2d33, .5, .5)); u.position.set(0, .2 + s * (h - .3) / 18, .72); g.add(u); }
  g.userData = { leds, n, seed };
  g.userData.tick = t => { const rr = rng(seed + Math.floor(t * 8)); for (let i = 0; i < n; i++) { leds.setColorAt(i, c.set(rr() < .82 ? (i % 5 ? 0x3dff7a : 0x4aa3ff) : 0x050505)); } leds.instanceColor.needsUpdate = true; };
  return g;
}

// A glowing "message" token: rounded glass card with text lines, emissive rim; the hero object of a story.
export function token(color = 0xE8FF3A) {
  const g = new THREE.Group();
  const card = rbox(.62, .4, .06, .08, M.phys(color, .25, 0, { emissive: color, emissiveIntensity: 1.35, clearcoat: 1 })); g.add(card);
  const tail = new THREE.Mesh(new THREE.ConeGeometry(.07, .14, 3), card.material); tail.rotation.z = Math.PI * .8; tail.position.set(-.2, -.22, 0); g.add(tail);
  for (let i = 0; i < 2; i++) { const l = box(i ? .26 : .38, .045, .02, M.basic(0x1a1a10)); l.position.set(-.06 + (i ? -.06 : 0), .06 - i * .1, .035); g.add(l); }
  const light = new THREE.PointLight(color, 2.2, 3.5, 2); g.add(light);
  g.userData = { card, light, color };
  return g;
}

// Glowing trail: a tube along a curve revealed from 0..k (draw-on), with a hot head.
export function trail(points, color = 0xE8FF3A, radius = .02) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const geo = new THREE.TubeGeometry(curve, 240, radius, 8, false);
  const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .95, toneMapped: false });
  const m = new THREE.Mesh(geo, mat); const total = geo.index.count;
  m.userData = { curve, set: (a, b = 0) => { const i0 = Math.floor(clamp(b) * total / 6) * 6, i1 = Math.floor(clamp(a) * total / 6) * 6; geo.setDrawRange(i0, Math.max(0, i1 - i0)); } };
  m.userData.set(0);
  return m;
}
