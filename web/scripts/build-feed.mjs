// Builds the studio feed (feed.json): every GitHub API answer the website needs, so visitors read ONE file from
// raw.githubusercontent.com instead of calling the API (60 calls/hour limit). Run by .github/workflows/site-feed.yml
// with the workflow's own token (read-only use). Usage: node web/scripts/build-feed.mjs <out-file>
import { writeFileSync } from "node:fs";
import { createStudio } from "../src/lib/github-data.js";

const out = process.argv[2] || "feed.json";
const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || "";
const responses = {};
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, opts = {}) => {   // record every API answer; the token never goes into the file
  const headers = { ...(opts.headers || {}) };
  if (String(url).startsWith("https://api.github.com") && token) headers.Authorization = `Bearer ${token}`;
  const r = await realFetch(url, { ...opts, headers });
  if (String(url).startsWith("https://api.github.com") && r.ok) {
    const body = await r.clone().json();
    responses[url] = body;
  }
  return r;
};

const s = createStudio({ feedBranch: "", cacheSeconds: 0 });
await s.films();
await Promise.all([s.reviewQueue(), s.polishQueue(), s.uploadQueue(), s.uploaded(), s.statusBoard(), s.alerts(), s.labRuns()]);
const runs = await s.runs(50);
await s.runs(30);
for (const r of runs.slice(0, 12)) await s.runSteps(r.id);
// what earlier films used (topics, cast, music): the pipeline's own memory, so the site knows which topics are done
let memory = null;
try {
  const rels = await s.releases();
  const asset = (rels.find(r => r.tag === "channel-memory")?.assets || []).find(a => a.name === "used.json");
  if (asset) { const r = await realFetch(asset.url); if (r.ok) memory = await r.json(); }
} catch (e) { console.log("memory: not included (" + e.message + ")"); }
// ---- the clips lanes (SC/WC) and the Studio Board ----
// Shorts: each "shorts-*" release carries posts.json (titles, scores, checks, notes). Release downloads have no CORS,
// so the feed carries them for the browser.
const clips = {};
let hot = null;
try {
  const rels = await s.releases();
  for (const r of rels.filter(r => /^shorts-/.test(r.tag)).slice(0, 40)) {
    const a = r.assets.find(x => x.name === "posts.json");
    if (!a) continue;
    try { const x = await realFetch(a.url); if (x.ok) clips[r.tag] = await x.json(); } catch { /* one bad file: skip */ }
  }
  const h = rels.find(r => r.tag === "clips-hot");
  if (h) {
    hot = { at: h.at };
    for (const [k, name] of [["streamers", "hot_streamers.json"], ["world", "hot_world.json"]]) {
      const a = h.assets.find(x => x.name === name);
      if (a) try { const x = await realFetch(a.url); if (x.ok) hot[k] = await x.json(); } catch { /* skip */ }
    }
  }
} catch (e) { console.log("clips: " + e.message); }

// Lab videos: made in Claude's workspace before the workflows existed, kept in releases lab-archive-<lane> with a list
const lab = {};
try {
  for (const r of (await s.releases()).filter(r => /^lab-archive-/.test(r.tag))) {
    const a = r.assets.find(x => /^lab-[a-z]+\.json$/.test(x.name));
    if (a) try { const x = await realFetch(a.url); if (x.ok) lab[r.tag] = await x.json(); } catch { /* skip */ }
  }
} catch (e) { console.log("lab: " + e.message); }

// Tech radar (release tech-radar): ranked topics for Tech Education
let radar = null;
try {
  const r = (await s.releases()).find(r => r.tag === "tech-radar");
  const a = r && r.assets.find(x => x.name === "tech_radar.json");
  if (a) { const x = await realFetch(a.url); if (x.ok) { const d = await x.json(); radar = { built: d.built, topics: d.topics || [] }; } }
} catch (e) { console.log("radar: " + e.message); }

// The Notion Studio Board (read with the NOTION_TOKEN secret; the token never goes into the file)
const NOTION = process.env.NOTION_TOKEN || "";
const BOARD_DB = process.env.STUDIO_BOARD_DB || "654c7f0514f0448f8c8e79752c604dbc";
let board = null;
if (NOTION) {
  try {
    const rows = []; let cursor;
    for (let i = 0; i < 10; i++) {
      const r = await realFetch(`https://api.notion.com/v1/databases/${BOARD_DB}/query`, { method: "POST",
        headers: { Authorization: `Bearer ${NOTION}`, "Notion-Version": "2022-06-28", "Content-Type": "application/json" },
        body: JSON.stringify(cursor ? { page_size: 100, start_cursor: cursor } : { page_size: 100 }) });
      if (!r.ok) throw new Error("Notion " + r.status);
      const d = await r.json(); rows.push(...d.results); if (!d.has_more) break; cursor = d.next_cursor;
    }
    const txt = v => (v?.title || v?.rich_text || []).map(t => t.plain_text).join("");
    board = rows.map(pg => { const P = pg.properties || {}; return {
      title: txt(P["Title"]), lane: P["Lane"]?.select?.name || "", stage: P["Stage"]?.status?.name || P["Stage"]?.select?.name || "",
      videoId: txt(P["Video ID"]), who: txt(P["Who / topic"]), why: txt(P["Why now"]), note: txt(P["Before you post"]),
      source: P["Source"]?.url || "", clip: P["Clip file"]?.url || "", youtube: P["YouTube link"]?.url || "",
      score: P["Score"]?.number ?? null, views: P["Views"]?.number ?? null, band: P["Predicted views"]?.select?.name || "",
      date: P["Date"]?.date?.start || "", edited: pg.last_edited_time, url: pg.url }; });
  } catch (e) { console.log("board: not included (" + e.message + ")"); }
}

// Mirror: Hidden Reasons and Tech Education live on GitHub (issues + releases); their cards on the board follow them.
// A card's stage is written only when the GitHub state CHANGED since the last feed, so a move made in Notion stays
// until something real happens on GitHub (no tug of war).
const STAGE = { draft: "Making", polish: "Making", polished: "Making", review: "Review", ready: "Approved", finished: "Approved", uploaded: "Posted" };
let prevMirror = {};
try {
  const r = await realFetch(`https://raw.githubusercontent.com/FranklinMburu/Autonomous-content-studio/site-data/feed.json`);
  if (r.ok) for (const m of (await r.json()).mirror || []) prevMirror[m.video_id] = m.stage;
} catch { /* first run */ }
const mirror = [];
try {
  for (const f of await s.films()) {
    const stage = STAGE[f.status]; if (!stage) continue;
    const note = { polish: "Needs your polish (Studio app: Hidden Reasons -> Polish).", review: "Needs your review: approve or repaint.",
                   ready: "Ready to upload.", draft: "Written and checked; waiting for the polish." }[f.status] || "";
    if (f.lane !== "HR") continue;   // Body Science explainers stay off the board (paused pilot; BS is not a board lane)
    mirror.push({ lane: "HR", video_id: `HR-${f.id}`, title: f.title, stage, note, clip: f.video?.url || "", source: f.release?.url || "" });
  }
  for (const r of (await s.releases()).filter(r => r.kind === "motion")) {
    mirror.push({ lane: "TE", video_id: `TE-${r.episode}-run${r.run}`, title: r.title, stage: r.held ? "Review" : "Approved",
                  note: r.held ? "A check failed: see the release notes." : "", clip: r.video?.url || "", source: r.url });
  }
  for (const m of mirror) m.changed = prevMirror[m.video_id] !== m.stage;
} catch (e) { console.log("mirror: " + e.message); }

// keep the file small: drop what the site never reads (people, nested repos, API links)
const DROP = new Set(["author", "uploader", "user", "actor", "triggering_actor", "head_commit", "repository", "head_repository",
  "reactions", "performed_via_github_app", "assignee", "assignees", "milestone", "closed_by", "pull_requests", "referenced_workflows",
  "node_id", "body_html", "body_text", "labels_url", "sub_issues_summary", "issue_dependencies_summary", "check_suite_id"]);
const KEEP_URL = new Set(["html_url", "browser_download_url"]);
const prune = v => Array.isArray(v) ? v.map(prune) : v && typeof v === "object"
  ? Object.fromEntries(Object.entries(v).filter(([k]) => !DROP.has(k) && !(k.endsWith("_url") && !KEEP_URL.has(k)) && k !== "url").map(([k, x]) => [k, prune(x)]))
  : v;
for (const k of Object.keys(responses)) responses[k] = prune(responses[k]);
const feed = { built: new Date().toISOString(), note: "Built by the Site feed workflow. Public data only.", responses, memory, clips, hot, board, mirror, lab, radar };
writeFileSync(out, JSON.stringify(feed));
writeFileSync("mirror.json", JSON.stringify(mirror));
console.log(`clips releases ${Object.keys(clips).length}, hot ${hot ? "yes" : "no"}, board ${board ? board.length + " cards" : "not read"}, mirror ${mirror.length} (${mirror.filter(m => m.changed).length} changed)`);
console.log(`feed: ${Object.keys(responses).length} answers, ${(JSON.stringify(feed).length / 1024).toFixed(0)} KB`);
