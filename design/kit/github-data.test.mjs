// Live test of github-data.js against the real repo. Run: node design/kit/github-data.test.mjs
// (Behind a proxy: NODE_EXTRA_CA_CERTS=... node --import ./proxy.mjs …). Read-only; uses ~8 API calls.
import { createStudio, sourceSummary } from "./github-data.js";
const s = createStudio();
const ok = (c, m) => { if (!c) { console.error("FAIL", m); process.exitCode = 1; } else console.log("ok  ", m); };
const films = await s.films();
ok(films.length > 0, `films: ${films.length}`);
for (const f of films.slice(0, 8)) console.log("     ", f.status.padEnd(8), f.style.padEnd(10), f.title);
ok(films.every(f => ["ready","uploaded","finished","review","polish","draft"].includes(f.status)), "every film has a known status");
const rq = await s.reviewQueue(); ok(Array.isArray(rq), `review queue: ${rq.length}`);
const pq = await s.polishQueue(); ok(pq.every(p => p.polishPrompt), `polish queue: ${pq.length}, each with a prompt`);
const uq = await s.uploadQueue(); ok(Array.isArray(uq), `ready to upload: ${uq.length}`);
const runs = await s.runs(); ok(runs.length > 0, `runs: ${runs.length} (latest: ${runs[0].workflow} · ${runs[0].state})`);
const steps = await s.runSteps(runs[0].id); ok(steps.length > 0, `steps of latest run: ${steps.map(x => x.name).slice(0, 6).join(" | ")}`);
const t = await s.topics(); ok(t.length > 0, `topics queued: ${t.length}`);
const sch = await s.schedule(); ok(sch.utc.length === 5, `schedule UTC: ${sch.utc.join(", ")}`);
const ep = await s.episode("episodes/hidden_reasons/002-why-doctors-were-ordered-to-wash-their-h");
ok(ep.script && ep.film && ep.sources.length > 0, `episode 002: ${ep.film.shots.length} shots, ${ep.sources.length} sourced claims, ${sourceSummary(ep.sources).length} links`);
const st = await s.statusBoard(); ok(st === null || st.rows.length > 0, `status board rows: ${st ? st.rows.length : 0}`);
const al = await s.alerts(); ok(Array.isArray(al), `alerts: ${al.length}`);
