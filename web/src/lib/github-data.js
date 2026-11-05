// Candela data layer: reads the REAL studio from its public GitHub repo. No seed data, no sample data, no keys.
// The backend already exists (GitHub Actions + Releases + Issues + episode files). The site only READS it.
// Every screen gets its data from these functions; if a value is not available, the screen shows "—" or an empty
// state (see design/DATA_CONTRACT.md). Never invent values.
//
// Plain ES module (works in React/TS). Tested against the live repo on 2 Nov 2026 (kit/github-data.test.mjs).
//
//   import { createStudio } from "./github-data.js";
//   const studio = createStudio();               // defaults below
//   const films = await studio.films();         // [{ id, title, status, video, contact, ... }]

export const DEFAULTS = {
  owner: "FranklinMburu",
  repo: "Autonomous-content-studio",
  branch: "story-style",                  // episode files + topics live here until PR #10 is merged; then "main"
  channels: [{ code: "HR", name: "Hidden Reasons", dir: "episodes/hidden_reasons",
               niche: "True stories behind history's strangest acts", perDay: 5,
               scheduleWorkflow: "story-schedule.yml", makeWorkflow: "make-story.yml" }],
  cacheSeconds: 120,                      // GitHub allows 60 unauthenticated API calls per hour per visitor
};

const API = "https://api.github.com";
const RAW = "https://raw.githubusercontent.com";

// ---------- low level (cached; sessionStorage when available, memory otherwise) ----------
const mem = new Map();
function cacheGet(k, ttl) {
  try {
    const s = typeof sessionStorage !== "undefined" && sessionStorage.getItem(k);
    const v = s ? JSON.parse(s) : mem.get(k);
    if (v && Date.now() - v.t < ttl * 1000) return v.d;
  } catch { /* storage may be blocked: fine */ }
  return undefined;
}
function cacheSet(k, d) {
  const v = { t: Date.now(), d }; mem.set(k, v);
  try { typeof sessionStorage !== "undefined" && sessionStorage.setItem(k, JSON.stringify(v)); } catch { /* full or blocked */ }
}

export class StudioError extends Error {
  constructor(kind, message) { super(message); this.kind = kind; } // kind: "rate-limit" | "not-found" | "network"
}

export function createStudio(opts = {}) {
  const cfg = { ...DEFAULTS, ...opts };
  const repoPath = `${cfg.owner}/${cfg.repo}`;
  const pending = new Map();

  async function get(url, { text = false, ttl = cfg.cacheSeconds } = {}) {
    const key = "candela:" + url;
    const hit = cacheGet(key, ttl); if (hit !== undefined) return hit;
    if (pending.has(key)) return pending.get(key);
    const p = (async () => {
      let r;
      try { r = await fetch(url, { headers: url.startsWith(API) ? { Accept: "application/vnd.github+json" } : {} }); }
      catch (e) { throw new StudioError("network", "Could not reach GitHub"); }
      if (r.status === 403 || r.status === 429) {
        const reset = Number(r.headers.get("x-ratelimit-reset")) * 1000;
        throw new StudioError("rate-limit", reset ? `GitHub limit reached. Fresh data after ${new Date(reset).toLocaleTimeString()}.` : "GitHub limit reached.");
      }
      if (r.status === 404) throw new StudioError("not-found", "Not found: " + url);
      if (!r.ok) throw new StudioError("network", `GitHub answered ${r.status}`);
      const d = text ? await r.text() : await r.json();
      cacheSet(key, d); return d;
    })();
    pending.set(key, p);
    try { return await p; } finally { pending.delete(key); }
  }
  const api = (path, o) => get(`${API}/repos/${repoPath}${path}`, o);
  const raw = (path, o) => get(`${RAW}/${repoPath}/${cfg.branch}/${path}`, { text: true, ...o });

  // ---------- releases: every video the pipeline has made ----------
  // Tag kinds (from tools/film_produce.sh and the workflows):
  //   film-<episode>-run<N>   film style. prerelease + title "REVIEW: …" = held for review; normal = finished
  //   story-<episode>-run<N>  storyboard style, finished
  //   draft-<episode>-run<N>  written and checked, waiting for the polish (prerelease, episode-files.zip only)
  //   video-<date>-<slug>     explainer style, finished
  //   lab-run<N>              GPU experiments (Lab page only)
  //   channel-memory          what earlier videos used (used.json; not readable from a browser, see DATA_CONTRACT)
  async function releases() {
    const all = [];
    for (let page = 1; page <= 3; page++) {
      const batch = await api(`/releases?per_page=100&page=${page}`);
      all.push(...batch); if (batch.length < 100) break;
    }
    return all.map(parseRelease).filter(Boolean);
  }

  function parseRelease(r) {
    const tag = r.tag_name;
    const m = tag.match(/^(film|story|draft)-(.+)-run(\d+)$/) || tag.match(/^(video)-(\d{8})-(.+)$/) || tag.match(/^(lab)-run(\d+)$/);
    const kind = m ? m[1] : (tag === "channel-memory" ? "memory" : "other");
    const asset = (re) => r.assets.find(a => re.test(a.name));
    const video = asset(/\.mp4$/i), contact = asset(/^contact\.png$/i);
    const title = (r.name || tag).replace(/^(Film|REVIEW|Story|Draft|Lab):\s*/i, "").trim();
    const notes = r.body || "";
    const line = (label) => (notes.match(new RegExp("^" + label + ":\\s*(.+)$", "mi")) || [])[1] || "";
    return {
      tag, kind, title, url: r.html_url, at: r.published_at || r.created_at,
      episode: kind === "video" ? `video-${m[2]}-${m[3]}` : (m && m[2]) || null,
      run: kind === "video" ? null : (m && Number(m[3] || m[2])) || null,
      held: !!r.prerelease && /^REVIEW:/i.test(r.name || ""),
      prerelease: !!r.prerelease,
      video: video ? { url: video.browser_download_url, bytes: video.size, name: video.name } : null,
      contact: contact ? contact.browser_download_url : null,
      zip: (asset(/^episode-files\.zip$/) || {}).browser_download_url || null,
      checks: line("Checks"), problems: line("NEEDS REVIEW"),
      sources: parseSources(notes),
      assets: r.assets.map(a => ({ name: a.name, url: a.browser_download_url, bytes: a.size })),
    };
  }

  // ---------- issues: the owner's to-do list (review, polish, ready to upload, alerts, status) ----------
  async function issues(label, state = "open") {
    const list = await api(`/issues?labels=${encodeURIComponent(label)}&state=${state}&per_page=100`);
    return list.filter(i => !i.pull_request).map(i => {
      const marker = (i.body || "").match(/<!--\s*(review|polish):([^>]*)-->/);
      const fields = {};
      if (marker) for (const [, k, v] of marker[2].matchAll(/(\w+)=(\S*)/g)) fields[k] = v;
      const prompt = ((i.body || "").match(/`{3,}text\n([\s\S]*?)\n`{3,}/) || [])[1] || null;
      return {
        number: i.number, title: i.title.replace(/^(Review needed|Polish needed|Ready to upload):\s*/i, ""),
        state: i.state, url: i.html_url, at: i.created_at, updated: i.updated_at, closedAt: i.closed_at,
        comments: i.comments, body: i.body || "", tag: fields.tag || fields.draft || null,
        episode: fields.episode || null, failedShots: fields.failed ? fields.failed.split(",").filter(Boolean) : [],
        polishPrompt: prompt,
      };
    });
  }
  const reviewQueue = () => issues("review");
  const polishQueue = () => issues("polish");
  const uploadQueue = () => issues("ready-to-upload");
  const uploaded = () => issues("ready-to-upload", "closed");   // closed = the owner uploaded it
  async function alerts() {
    const [issue] = await issues("pipeline-alert");
    if (!issue) return [];
    const comments = issue.comments ? await api(`/issues/${issue.number}/comments?per_page=30`) : [];
    return [{ at: issue.at, text: issue.body, url: issue.url }, ...comments.map(c => ({ at: c.created_at, text: c.body, url: c.html_url }))].reverse();
  }
  async function statusBoard() {   // issue labelled studio-status, rewritten by the explainer pipeline
    const [issue] = await issues("studio-status");
    if (!issue) return null;
    const rows = [...issue.body.matchAll(/^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|$/gm)].map(m => ({ stage: m[1], count: Number(m[2]), meaning: m[3] }));
    const updated = (issue.body.match(/_Updated ([^_]+)_/) || [])[1] || issue.updated;
    return { rows, updated, url: issue.url };
  }

  // ---------- films: one row per episode, newest run wins ----------
  // status: "ready" (finished, ready-to-upload issue open) | "uploaded" (that issue closed) | "finished" (no issue)
  //         "review" (held) | "polish" (draft + open polish issue) | "draft"
  async function films() {
    const [rels, ready, done, review, polish] = await Promise.all([releases(), uploadQueue(), uploaded(), reviewQueue(), polishQueue()]);
    const byEp = new Map();
    for (const r of rels) {
      if (!["film", "story", "draft", "video"].includes(r.kind)) continue;
      const prev = byEp.get(r.episode);
      const rank = x => (x.kind === "draft" ? 0 : 1) * 1e6 + (x.run || 0);   // a made video beats a draft, then newest run
      if (!prev || rank(r) > rank(prev)) byEp.set(r.episode, r);
    }
    const sameTitle = (a, b) => a && b && a.toLowerCase().replace(/[^a-z0-9]/g, "") === b.toLowerCase().replace(/[^a-z0-9]/g, "");
    return [...byEp.values()].map(r => {
      let status;
      if (r.kind === "draft") status = polish.some(p => p.tag === r.tag || (p.episode || "").endsWith(r.episode)) ? "polish" : "draft";
      else if (r.held) status = "review";
      else if (ready.some(i => sameTitle(i.title, r.title))) status = "ready";
      else if (done.some(i => sameTitle(i.title, r.title))) status = "uploaded";
      else status = "finished";
      const rev = review.find(i => i.tag === r.tag);
      const pol = polish.find(p => p.tag === r.tag);
      const style = r.kind === "film" ? "film" : r.kind === "story" ? "storyboard" : r.kind === "video" ? "explainer" : "draft";
      const title = r.kind === "draft" ? (pol ? pol.title : humanize(r.episode)) : r.title;
      return { id: r.episode, title, status, style, at: r.at, run: r.run, release: r, video: r.video, contact: r.contact,
               reviewIssue: rev || null, polishIssue: pol || null, weakShots: rev ? rev.failedShots : [] };
    }).sort((a, b) => b.at.localeCompare(a.at));
  }

  // ---------- runs: GitHub Actions runs = the "Runs" page (live state + step timings) ----------
  // Every workflow except the code tests ("Pipeline tests") is a studio run.
  async function runs(limit = 30) {
    const d = await api(`/actions/runs?per_page=${limit}`, { ttl: 30 });
    return d.workflow_runs.filter(r => r.name !== "Pipeline tests")
      .map(r => ({
        id: r.id, workflow: r.name, title: r.display_title, status: r.status, conclusion: r.conclusion,
        // state: "running" | "queued" | "success" | "failure" | "cancelled"
        state: r.status !== "completed" ? (r.status === "in_progress" ? "running" : "queued") : (r.conclusion || "failure"),
        event: r.event, branch: r.head_branch, number: r.run_number,
        started: r.run_started_at || r.created_at, updated: r.updated_at, url: r.html_url,
        minutes: Math.round((new Date(r.status === "completed" ? r.updated_at : Date.now()) - new Date(r.run_started_at || r.created_at)) / 60000),
      }));
  }
  async function runSteps(runId) {   // the timeline of one run (job steps with times)
    const d = await api(`/actions/runs/${runId}/jobs`, { ttl: 20 });
    return d.jobs.flatMap(j => j.steps.map(s => ({
      job: j.name, name: s.name, number: s.number,
      state: s.status !== "completed" ? (s.status === "in_progress" ? "running" : "waiting") : (s.conclusion === "skipped" ? "skipped" : s.conclusion === "success" ? "done" : "failed"),
      started: s.started_at, finished: s.completed_at,
      seconds: s.started_at && s.completed_at ? Math.round((new Date(s.completed_at) - new Date(s.started_at)) / 1000) : null,
    }))).filter(s => !/^(Set up job|Complete job|Post )/.test(s.name));
  }

  // ---------- channel files (raw, no API quota) ----------
  async function topics(channel = cfg.channels[0]) {
    const t = await raw(`${channel.dir}/topics.txt`);
    return t.split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"));
  }
  async function schedule(channel = cfg.channels[0]) {   // the 5 daily start times, read from the workflow's cron
    const y = await raw(`.github/workflows/${channel.scheduleWorkflow}`);
    const cron = (y.match(/cron:\s*"([^"]+)"/) || [])[1];
    if (!cron) return { cron: null, utc: [] };
    const [min, hours] = cron.split(/\s+/);
    const utc = hours.split(",").map(h => `${h.padStart(2, "0")}:${min.padStart(2, "0")}`);
    return { cron, utc };   // show in the viewer's local time with nextSlots()
  }
  function nextSlots(utc, count = 5, from = new Date()) {
    const out = [];
    for (let day = 0; out.length < count && day < 3; day++) for (const hm of utc) {
      const [h, m] = hm.split(":").map(Number);
      const d = new Date(Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate() + day, h, m));
      if (d > from) out.push(d);
    }
    return out.sort((a, b) => a - b).slice(0, count);
  }
  async function episode(dir) {   // script, film plan and sources of one episode folder
    const [script, film, sources] = await Promise.all([
      raw(`${dir}/script.json`).then(JSON.parse).catch(() => null),
      raw(`${dir}/film.json`).then(JSON.parse).catch(() => null),
      raw(`${dir}/sources.md`).then(parseSources).catch(() => []),
    ]);
    return { dir, script, film, sources };
  }
  async function memorySeed(channel = cfg.channels[0]) {
    return raw(`${channel.dir}/memory_seed.json`).then(JSON.parse).catch(() => null);
  }
  async function models() {   // pipeline/config.json: which free models write the scripts
    return raw("pipeline/config.json").then(JSON.parse).catch(() => null);
  }
  async function labRuns() { return (await releases()).filter(r => r.kind === "lab"); }

  // ---------- links for actions (the site never writes; the owner acts on GitHub) ----------
  const links = {
    repo: `https://github.com/${repoPath}`,
    newFilm: (channel = cfg.channels[0]) => `https://github.com/${repoPath}/actions/workflows/${channel.makeWorkflow}`,
    runNow: (channel = cfg.channels[0]) => `https://github.com/${repoPath}/actions/workflows/${channel.scheduleWorkflow}`,
    topicsFile: (channel = cfg.channels[0]) => `https://github.com/${repoPath}/edit/${cfg.branch}/${channel.dir}/topics.txt`,
    issue: n => `https://github.com/${repoPath}/issues/${n}`,
    release: tag => `https://github.com/${repoPath}/releases/tag/${tag}`,
  };

  return { cfg, releases, films, runs, runSteps, reviewQueue, polishQueue, uploadQueue, uploaded, alerts, statusBoard,
           topics, schedule, nextSlots, episode, memorySeed, models, labRuns, links };
}

// "004-why-john-snow-removed-a-london-pump-hand" -> "Why john snow removed a london pump hand" (last resort only)
export function humanize(slug) {
  const t = String(slug || "").replace(/^\d+-/, "").replace(/-+/g, " ").trim();
  return t.charAt(0).toUpperCase() + t.slice(1);
}

// "| claim | https://… |" markdown tables (release notes and sources.md)
export function parseSources(md) {
  return [...String(md).matchAll(/^\|\s*(.+?)\s*\|\s*(https?:\/\/\S+?)\s*\|\s*$/gm)]
    .filter(m => !/^-+$/.test(m[1]) && m[1].toLowerCase() !== "claim in the script")
    .map(m => ({ claim: m[1], url: m[2], host: m[2].replace(/^https?:\/\/(www\.)?/, "").split("/")[0] }));
}

// Group sources by link for the "Sources behind every line" list: [{ url, host, claims: n }]
export function sourceSummary(sources) {
  const m = new Map();
  for (const s of sources) { const v = m.get(s.url) || { url: s.url, host: s.host, claims: 0 }; v.claims++; m.set(s.url, v); }
  return [...m.values()].sort((a, b) => b.claims - a.claims);
}

// ---------- the hero globe: real episodes + real queued topics, placed with places.json ----------
// Returns { stories, arcs } for kit/earth.js.
//   stories: made films (bright light; the two newest get a card) and queued topics (small dim light + name tag)
//   arcs:    the made films joined in the order they were made, then the newest made film to the next two queued
//            places that are in a different city (what the channel is about to visit).
export function buildGlobe(films, topics, places) {
  const made = films.filter(f => places.episodes[f.id])
    .sort((a, b) => a.at.localeCompare(b.at))
    .map(f => ({ ...places.episodes[f.id], n: places.episodes[f.id].name, y: places.episodes[f.id].year, kind: "made", film: f }));
  const madeCities = new Set(made.map(m => m.n));
  const queued = [];
  for (const t of topics) {
    const p = places.topics.find(x => t.toLowerCase().includes(x.match.toLowerCase()));
    if (!p || !p.name) continue;
    if (made.some(m => t.toLowerCase().includes((m.film.title || "").toLowerCase().split(" ").slice(1, 3).join(" ")))) continue;
    if (madeCities.has(p.name)) continue;                     // that city already has a made film's light
    if (queued.some(q => q.n === p.name)) continue;                                                // one light per city
    queued.push({ ...p, n: p.name, y: p.year, kind: "queued", topic: t });
  }
  const newest = made[made.length - 1];
  const cards = made.slice(-2).reverse();                 // newest → left card, the one before → right card
  cards.forEach((c, i) => { c.card = i === 0 ? "left" : "right"; });
  const arcs = [];
  for (let i = 1; i < made.length; i++) arcs.push([made[i - 1].n, made[i].n, 60 + 30 * i]);
  const onGlobe = q => q.lon > -110 && q.lon < 90 && q.lat > -20;   // the hemisphere the hero shows
  if (newest) queued.filter(onGlobe).slice(0, 2)
    .forEach((q, i) => arcs.push([newest.n, q.n, 120 + 60 * i]));
  return { stories: [...made, ...queued], arcs };
}
