// Overlay layer: captions, callout labels pinned to 3D points, counters, cards, tags.
// Pure DOM/SVG so text stays razor sharp; driven by time t like everything else (deterministic).
const W = () => window.__W, H = () => window.__H;
const css = `
.ov{position:absolute;inset:0;pointer-events:none;font-family:Inter,'Inter Display',sans-serif;overflow:hidden}
.cap{position:absolute;left:50%;transform:translate(-50%,-50%);top:73.5%;max-width:84%;text-align:center;
 padding:.18em .42em;border-radius:.32em;background:rgba(18,16,20,.58);backdrop-filter:blur(6px);
 font-size:calc(var(--u)*4.25);line-height:1.18;letter-spacing:-.01em;white-space:normal}
.cap .w{display:inline-block;margin:0 .13em;color:rgb(160,162,168);font-weight:500;position:relative;transition:none}
.cap .w.on{color:#fbfbfd;font-weight:750}
.cap .w.key{color:#fbfbfd;font-weight:800}
.cap .box{position:absolute;inset:-.06em -.14em;border:calc(var(--u)*.22) solid var(--acc);border-radius:.08em}
.cap .box:before,.cap .box:after{content:'';position:absolute;width:calc(var(--u)*.9);height:calc(var(--u)*.9);border-radius:50%;background:var(--acc)}
.cap .box:before{left:calc(var(--u)*-.55);top:calc(var(--u)*-.55)}.cap .box:after{right:calc(var(--u)*-.55);bottom:calc(var(--u)*-.55)}
.lbl{position:absolute;font-family:'JetBrains Mono','DejaVu Sans Mono',monospace;font-size:calc(var(--u)*1.85);letter-spacing:.06em;
 color:#f4f4f6;text-transform:uppercase;white-space:nowrap;text-shadow:0 0 calc(var(--u)*.8) rgba(0,0,0,.9)}
.lbl small{display:block;font-size:.72em;opacity:.7;letter-spacing:.04em;text-transform:none}
.cnt{position:absolute;left:50%;transform:translateX(-50%);font-family:'Inter Display',Inter,sans-serif;font-weight:700;
 font-variant-numeric:tabular-nums;color:#fff;font-size:calc(var(--u)*9.5);letter-spacing:-.02em;white-space:nowrap;
 text-shadow:0 calc(var(--u)*.3) calc(var(--u)*2.4) rgba(0,0,0,.65)}
.cnt .unit{font-size:.42em;color:var(--acc2);margin-left:.18em;font-weight:700}
.cnt .sub{display:block;text-align:center;font-family:'JetBrains Mono','DejaVu Sans Mono',monospace;font-weight:500;font-size:.2em;letter-spacing:.12em;color:#cfd2d8;text-transform:uppercase}
.card{position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:calc(var(--u)*2);
 padding:calc(var(--u)*1.6) calc(var(--u)*2.4);border-radius:calc(var(--u)*1.6);background:rgba(16,16,20,.82);border:1px solid rgba(255,255,255,.12);
 box-shadow:0 calc(var(--u)*1) calc(var(--u)*4) rgba(0,0,0,.5);color:#fff;white-space:nowrap}
.quote{position:absolute;left:8%;right:8%;text-align:center;color:#fff;font-weight:650;font-size:calc(var(--u)*3.4);line-height:1.22}
.quote small{display:block;margin-top:.6em;font-family:'JetBrains Mono',monospace;font-size:.45em;letter-spacing:.2em;color:#bfc3ca;font-weight:500}
.tag{position:absolute;font-size:calc(var(--u)*1.55);color:rgba(255,255,255,.55);letter-spacing:.02em}
.src{position:absolute;left:5%;bottom:17.5%;font-family:'JetBrains Mono',monospace;font-size:calc(var(--u)*1.35);color:rgba(255,255,255,.5)}
`;
export function mount(accent = '#E8FF3A', accent2 = '#5fe3c0') {
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const ov = document.createElement('div'); ov.className = 'ov';
  ov.style.setProperty('--u', (W() / 100) + 'px'); ov.style.setProperty('--acc', accent); ov.style.setProperty('--acc2', accent2);
  ov.innerHTML = `<svg id=lines width="${W()}" height="${H()}" style="position:absolute;inset:0"></svg><div id=dyn></div><div class=cap id=cap></div>`;
  document.body.appendChild(ov);
  return ov;
}

// ---------- captions ----------
// timing.words: [{w,start,end,line,beat}] ; display: {"spoken phrase": "SHOWN"} ; keys: Set of lowercase words to box
export function buildCaptions(words, display = {}, keys = new Set()) {
  // 1) apply display map over the word stream (phrase -> one token spanning several spoken words)
  const toks = []; const norm = s => s.toLowerCase().replace(/[^a-z0-9']/g, '');
  const phrases = Object.entries(display).map(([k, v]) => [k.split(/\s+/).map(norm), v]).sort((a, b) => b[0].length - a[0].length);
  for (let i = 0; i < words.length;) {
    let hit = null;
    for (const [p, v] of phrases) {
      if (i + p.length <= words.length && p.every((x, j) => norm(words[i + j].w) === x)) { hit = [p.length, v]; break; }
    }
    if (hit) {
      const last = words[i + hit[0] - 1]; const trail = (last.w.match(/[.,?!:]+$/) || [''])[0];
      toks.push({ t: hit[1] + trail, start: words[i].start, end: last.end, line: words[i].line, key: true }); i += hit[0];
    } else { const w = words[i]; toks.push({ t: w.w, start: w.start, end: w.end, line: w.line, key: keys.has(norm(w.w)) }); i++; }
  }
  // 2) group into captions of 1-4 words: break on line change, after punctuation, or when long
  const groups = []; let g = [];
  for (const k of toks) {
    const len = g.reduce((a, x) => a + x.t.length + 1, 0);
    if (g.length && (k.line !== g[0].line || g.length >= 4 || len + k.t.length > 20)) { groups.push(g); g = []; }
    g.push(k);
    if (/[.?!,:]$/.test(k.t) && g.length >= 2) { groups.push(g); g = []; }
  }
  if (g.length) groups.push(g);
  groups.forEach((gr, i) => { gr.start = gr[0].start - 0.04; gr.end = i + 1 < groups.length ? groups[i + 1][0].start - 0.04 : gr.at(-1).end + 0.6; });
  return groups;
}
export function drawCaption(groups, t, hidden = false) {
  const el = document.getElementById('cap');
  const g = hidden ? null : groups.find(x => t >= x.start && t < x.end);
  if (!g) { el.style.display = 'none'; return; }
  el.style.display = 'block';
  let html = '';
  for (const k of g) {
    if (t < k.start - 0.02) continue;                       // words appear as they are spoken (karaoke build)
    const on = t >= k.start - 0.02 && (t < k.end + 0.08 || k === g.at(-1) || g.indexOf(k) === g.findLastIndex(x => x.start <= t));
    const age = Math.min(1, (t - k.start + 0.02) / 0.09);  // short slide-in with blur
    const sty = `transform:translateY(${(1 - age) * 0.18}em);filter:blur(${(1 - age) * 3}px);opacity:${0.35 + 0.65 * age}`;
    const txt = k.t.replace(/[,]$/, ',');
    html += `<span class="w${on ? ' on' : ''}${k.key ? ' key' : ''}" style="${sty}">${txt}${k.key && on ? '<i class=box></i>' : ''}</span>`;
  }
  el.innerHTML = html;
}

// ---------- callouts, counters, cards ----------
// Each call returns an HTML string for #dyn plus SVG paths for #lines; scene composes them per frame.
export function frameOverlay(items) {
  let html = '', svg = '';
  for (const it of items) { const r = it(); if (!r) continue; html += r.html || ''; svg += r.svg || ''; }
  document.getElementById('dyn').innerHTML = html;
  document.getElementById('lines').innerHTML = svg;
}
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const fade = (t, a, b, f = 0.25) => clamp((t - a) / f) * clamp((b - t) / f);
// label at screen point p (pixels) with an elbow leader to anchor q; side: label offset direction
export function callout(text, q, p, alpha, sub = '') {
  if (alpha <= 0 || !q) return null;
  const u = W() / 100, draw = clamp(alpha * 1.6);
  const mx = p[0], my = q[1] + (p[1] - q[1]);   // elbow: vertical from anchor, then horizontal to label
  const path = `M${q[0]},${q[1]} L${q[0]},${p[1] + u * 1.2} L${mx},${p[1] + u * 1.2}`;
  const len = Math.abs(p[1] + u * 1.2 - q[1]) + Math.abs(mx - q[0]) + 1;
  return {
    svg: `<path d="${path}" fill="none" stroke="rgba(255,255,255,${0.85 * alpha})" stroke-width="${Math.max(1, u * .14)}" stroke-dasharray="${len}" stroke-dashoffset="${len * (1 - draw)}"/>` +
      `<circle cx="${q[0]}" cy="${q[1]}" r="${u * .45}" fill="var(--acc)" opacity="${alpha}"/>`,
    html: `<div class=lbl style="left:${p[0] - (p[0] > W() / 2 ? 0 : 0)}px;top:${p[1] - u * 1.5}px;opacity:${alpha};transform:translateX(${p[0] > q[0] ? '0' : '-100%'})">${text}${sub ? `<small>${sub}</small>` : ''}</div>`
  };
}
export function counter(value, alpha, y = 0.085, unit = '', sub = '', fmt = v => Math.round(v).toLocaleString('en-US')) {
  if (alpha <= 0) return null;
  return { html: `<div class=cnt style="top:${y * H()}px;opacity:${alpha};transform:translateX(-50%) scale(${0.94 + 0.06 * alpha})">${fmt(value)}${unit ? `<span class=unit>${unit}</span>` : ''}${sub ? `<span class=sub>${sub}</span>` : ''}</div>` };
}
export function html(str, alpha) { return alpha > 0 ? { html: str.replace('$A', alpha.toFixed(3)) } : null; }
