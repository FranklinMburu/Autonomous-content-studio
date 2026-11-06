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
// keep the file small: drop what the site never reads (people, nested repos, API links)
const DROP = new Set(["author", "uploader", "user", "actor", "triggering_actor", "head_commit", "repository", "head_repository",
  "reactions", "performed_via_github_app", "assignee", "assignees", "milestone", "closed_by", "pull_requests", "referenced_workflows",
  "node_id", "body_html", "body_text", "labels_url", "sub_issues_summary", "issue_dependencies_summary", "check_suite_id"]);
const KEEP_URL = new Set(["html_url", "browser_download_url"]);
const prune = v => Array.isArray(v) ? v.map(prune) : v && typeof v === "object"
  ? Object.fromEntries(Object.entries(v).filter(([k]) => !DROP.has(k) && !(k.endsWith("_url") && !KEEP_URL.has(k)) && k !== "url").map(([k, x]) => [k, prune(x)]))
  : v;
for (const k of Object.keys(responses)) responses[k] = prune(responses[k]);
const feed = { built: new Date().toISOString(), note: "Built by the Site feed workflow. Public data only.", responses, memory };
writeFileSync(out, JSON.stringify(feed));
console.log(`feed: ${Object.keys(responses).length} answers, ${(JSON.stringify(feed).length / 1024).toFixed(0)} KB`);
