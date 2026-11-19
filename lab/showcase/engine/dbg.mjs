import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [scene, t, out, camJson] = process.argv.slice(2);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': p.endsWith('.js') ? 'text/javascript' : p.endsWith('.html') ? 'text/html' : 'application/json' }); fs.createReadStream(p).pipe(r); }).listen(0);
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await b.newPage({ viewport: { width: 540, height: 960 } }); page.on('pageerror', e => console.log('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${srv.address().port}/engine/index.html?scene=${scene}&w=540&h=960`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
const cams = JSON.parse(camJson); let i = 0;
for (const c of cams) { await page.evaluate(c => { window.__camO = c; }, c); await page.evaluate(t => window.renderAt(t), +t); await page.screenshot({ path: `${out}_${i++}.jpg`, quality: 85, type: 'jpeg' }); }
await b.close(); srv.close();
