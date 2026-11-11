// Draws every frame of a motion video with headless Chromium and pipes them into ffmpeg.
//   node render.js data.json out.mp4 [fps] [t0] [t1]      -> silent video
//   node render.js data.json --stills t1,t2,... outdir     -> JPEG stills
//   node render.js data.json --cues cues.json              -> sound cues + music sections only (fast)
// data.json = {timing, script, plan, style}; see studio/motion/__main__.py. Time is stepped, never read from a clock.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
(async () => {
  const [dataPath, a2, a3, a4, a5] = process.argv.slice(2);
  const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto('file://' + path.join(__dirname, 'web', 'engine.html'));
  await p.evaluate(() => document.fonts.ready);
  const info = await p.evaluate(d => window.init(d), data);
  await p.evaluate(() => document.fonts.ready);
  let code = 0;
  if (a2 === '--cues') {
    fs.writeFileSync(a3, JSON.stringify({ cues: info.cues, sections: info.sections, duration: info.duration }));
  } else if (a2 === '--stills') {
    fs.mkdirSync(a4, { recursive: true });
    for (const s of a3.split(',')) { const t = +s; await p.evaluate(t => render(t), t); await p.screenshot({ path: path.join(a4, `still_${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 88 }); }
  } else {
    const out = a2, fps = +(a3 || 30), t0 = +(a4 || 0), t1 = +(a5 || info.duration);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round((t1 - t0) * fps), st = Date.now();
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => render(t), t0 + i / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log(`  frame ${i}/${n} (${((Date.now() - st) / 1000).toFixed(0)} s)`);
    }
    ff.stdin.end(); code = await new Promise(r => ff.on('close', r));
  }
  if (errs.length) { console.error('page errors:', errs.slice(0, 5).join(' | ')); code = code || 3; }
  await b.close(); process.exit(code);
})();
