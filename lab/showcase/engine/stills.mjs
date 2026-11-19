import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [scene, W, H, ...ts] = process.argv.slice(2);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((q, r) => { const p = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r); }).listen(0);
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await b.newPage({ viewport: { width: +W, height: +H } });
page.on('console', m => console.log('page:', m.text().slice(0, 300))); page.on('pageerror', e => console.log('PAGEERROR', e.message));
await page.goto(`http://127.0.0.1:${srv.address().port}/engine/index.html?scene=${scene}&w=${W}&h=${H}`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
console.log('duration', await page.evaluate(() => window.__duration));
for (const t of ts) { const t0 = Date.now(); await page.evaluate(t => window.renderAt(t), +t); await page.screenshot({ path: `/tmp/st_${scene}_${t}.jpg`, type: 'jpeg', quality: 85 }); console.log(t, Date.now() - t0, 'ms'); }
await b.close(); srv.close();
