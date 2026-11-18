// Usage: node render.mjs <scene> <out.mp4> [fps=30] [from=0] [to=duration] [W=1080] [H=1920] [step=1]
// Serves this folder over http, opens index.html?scene=<scene>, calls window.renderAt(t) per frame,
// screenshots the page and pipes JPEGs into ffmpeg. Deterministic: no clock is read inside the page.
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const [scene, out, fpsA = '30', fromA = '0', toA = '', WA = '1080', HA = '1920', stepA = '1'] = process.argv.slice(2);
const fps = +fpsA, W = +WA, H = +HA, step = +stepA;
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.wav': 'audio/wav', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((q, r) => {
  const p = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r);
}).listen(0);
const port = srv.address().port;

const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
const page = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error' || m.text().startsWith('[scene]')) console.log('page:', m.text()); });
page.on('pageerror', e => console.log('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${port}/engine/index.html?scene=${scene}&w=${W}&h=${H}`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
const dur = await page.evaluate(() => window.__duration);
const from = +fromA, to = toA ? +toA : dur;
const n = Math.ceil((to - from) * fps / step);
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps / step), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps / step), out], { stdio: ['pipe', 'inherit', 'inherit'] });
const t0 = Date.now();
for (let i = 0; i < n; i++) {
  const t = from + i * step / fps;
  await page.evaluate(t => window.renderAt(t), t);
  const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) console.log(`frame ${i}/${n} t=${t.toFixed(2)} ${((Date.now() - t0) / (i + 1)).toFixed(0)} ms/frame`);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
console.log(`done ${n} frames in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
await b.close(); srv.close();
