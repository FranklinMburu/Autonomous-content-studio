# Data contract: where every value on the site comes from

> **No seed data. No sample data. No mock data. No fake numbers. Ever.**
> The studio's backend already exists and is running: GitHub Actions makes the films, GitHub Releases hold the
> videos, GitHub Issues hold the owner's to-do list, and the repo holds the episode files. The website **only reads
> that**, through `design/kit/github-data.js` (tested live on 2 Nov 2026 by `design/kit/github-data.test.mjs`).
>
> If a value is not available, show an **empty state** or "—". Never fill a gap with an invented value, a
> placeholder number, "Lorem ipsum", example films, or demo users. Do not create a `mock`, `seed`, `fixtures`,
> `sample` or `demo-data` file anywhere in `web/`.

The numbers, titles and pictures inside the app mockups (08–11, 02c, the right phone in 12) show the **layout and
the shape** of the content. In the built app they come from the functions below. Labels, headings, buttons and empty
states are fixed copy (take them from the mockups and `APP_PAGES.md`).

## 1. Sources (all public, no keys)

| Source | How it is read | Rate limit |
|---|---|---|
| GitHub REST API `api.github.com/repos/FranklinMburu/Autonomous-content-studio/…` (releases, issues, comments, Actions runs and jobs) | `fetch`, CORS allowed | 60 calls / hour / visitor without sign-in. `github-data.js` caches every answer for 120 s (30 s for runs) in `sessionStorage` and de-duplicates calls. One full app load ≈ 6 calls. |
| Repo files `raw.githubusercontent.com/<repo>/<branch>/…` (topics, episode files, workflow schedule, model config, memory seed) | `fetch`, CORS allowed | no API quota |
| Videos (`.mp4`) and contact sheets (`contact.png`) on Releases | `<video src>` / `<img src>` with the release asset URL. **Never `fetch()` them** (no CORS), never add `crossorigin`. | none |
| `channel-memory/used.json` (release asset) | **Not readable from a browser** (no CORS on release assets). Use `memorySeed()` (repo file) and mark the live memory as "updated by the pipeline after each film" with a link to the release. | — |

Branch for repo files: `story-style` (PR #10). When PR #10 is merged, change `DEFAULTS.branch` to `main`. That is the only
line to change.

## 2. Functions → screens

| Function (`createStudio()`) | Returns | Used on |
|---|---|---|
| `films()` | one row per episode, newest run wins: `{ id, title, status, style, at, run, video, contact, release, reviewIssue, polishIssue, weakShots }` | Films, Film detail, landing panel, hero cards, "films made" count |
| `releases()` | every release, typed by tag (`film`, `story`, `draft`, `video`, `lab`, `memory`) | Film detail (all runs of an episode), Lab |
| `runs(limit)` | Actions runs (except code tests): `{ id, workflow, title, state, started, minutes, url }` | Runs, Films "Making now", sidebar "Next film" ("started today") |
| `runSteps(runId)` | the steps of one run with state and seconds | Run detail timeline |
| `reviewQueue()` | open `review` issues: `{ number, title, tag, episode, failedShots, url }` | Review, badges |
| `polishQueue()` | open `polish` issues with the full `polishPrompt` text | Polish, badges |
| `uploadQueue()` / `uploaded()` | open / closed `ready-to-upload` issues | Upload, film status `ready` / `uploaded` |
| `alerts()` | the `pipeline-alert` issue and its comments, newest first | bell menu, Guard |
| `statusBoard()` | the `studio-status` issue table (explainer pipeline stages and counts) | Channels (explainer channel card) |
| `topics()` | the queued topics (`topics.txt`, comments removed) | Topics, Schedule, hero "stories queued" |
| `schedule()` + `nextSlots(utc, n)` | the cron of `story-schedule.yml` → the next start times, shown in the viewer's time zone | Schedule, sidebar "Next film", Films subtitle |
| `episode(dir)` | `{ script, film, sources }` of one episode folder | Film detail (script, cast, shots plan, sources), How-it-works counts |
| `memorySeed()` | cast, places and music already used | Memory |
| `models()` | `pipeline/config.json` (which free models write scripts) | Brain |
| `labRuns()` | `lab-run<N>` releases | Lab |
| `links.*` | GitHub URLs for every action (see section 4) | all action buttons |
| `buildGlobe(films, topics, places)` | `{ stories, arcs }` for the hero globe (with `kit/places.json`) | Hero |
| `parseSources`, `sourceSummary` | claims and links from a sources table | Film detail, Review |

## 3. Status vocabulary (use exactly these labels and chip colours)

| `status` | Chip label | Chip class | Meaning (from the backend) |
|---|---|---|---|
| `ready` | Ready to upload | `ok` | finished release + open `ready-to-upload` issue |
| `uploaded` | Uploaded | `ok` (muted) | that issue was closed by the owner |
| `finished` | Finished | `ok` | finished release, no upload issue |
| `review` | Review | `rev` (amber) | release is a pre-release titled "REVIEW: …" (a final check failed) |
| `polish` | Needs your polish | `rev` (amber) | draft release + open `polish` issue |
| `draft` | Draft | neutral | draft release, no polish issue |
| run `running` / `queued` | Making / Queued | `run` (blue, with dot) | Actions run in progress / waiting |
| run `failure` / `cancelled` | Failed / Cancelled | `bad` | Actions run ended badly |
| run `success` | Done | `ok` | |

## 4. Writing: the site never writes

The site is **read-only**. It has no token, no sign-in and no server. Every action opens the right page on GitHub, where
the owner (signed in to GitHub) does it the way the pipeline already expects:

| Button | Opens | What the owner does there |
|---|---|---|
| **New film** | `links.newFilm()` (Actions → "Make a story video") | Run workflow, type a topic |
| **Run next now** | `links.runNow()` (Actions → "Story schedule") | Run workflow |
| **Approve** / **Repaint** | `links.issue(reviewIssue.number)` | comment `approve` or `repaint` (the `review-reply` workflow acts) |
| **Copy prompt** (Polish) | copies `polishPrompt` to the clipboard (browser API, no network) | paste in claude.ai |
| **Paste Claude's answer** | `links.issue(polishIssue.number)` | paste as a comment (the `polish-return` workflow acts) |
| **Download video** | the release asset URL | — |
| **Mark uploaded** | `links.issue(uploadIssue.number)` | close the issue |
| **Edit topics** | `links.topicsFile()` (GitHub editor) | edit and commit |

Each such button shows a small "↗ GitHub" mark so it is clear it leaves the site. In-app writes ("Sign in with
GitHub") are a planned feature (see `APP_PAGES.md`, Roadmap): show nothing for them now.

## 5. Loading, empty and error states (required on every data view)

- **Loading:** skeleton blocks with the exact size of the real content (`--s2` surface, 1.2 s shimmer). Never spinners in
  the middle of the page. Never layout shift when data arrives.
- **Empty:** one line of plain text + one action. Examples: Review "Nothing to review. Every film passed its checks.";
  Polish "No polish needed right now."; Upload "Nothing waiting. Finished films appear here."; Runs "No runs yet today.
  Next film starts at 13:23." (time from `schedule()`).
- **Rate limit** (`StudioError.kind === "rate-limit"`): keep showing the last cached data and a thin bar at the top:
  "GitHub limit reached. Fresh data after 14:05." Never a blank page.
- **Network error:** same bar: "Can't reach GitHub right now. Showing the last data we had." + Retry.
- **Not found** (a file moved): hide that block, never crash the page.

## 6. Numbers on the landing page (all computed, never typed)

| Where | Number | Computed as |
|---|---|---|
| Hero numbers row | films made | `films()` with status in ready, uploaded, finished, review |
| Hero numbers row | facts checked | sum of `release.sources.length` over those films |
| Hero numbers row | stories queued | `topics().length` |
| Hero numbers row | $0 to run | fixed fact (the studio runs on free tiers only) |
| Hero cards | the two newest made films that have a place | `buildGlobe(...)` cards (left = newest) |
| Studio World (section 5) | films made this week, shots painted, facts checked, $0 | releases of the last 7 days; shots = sum of `film.shots.length` of those episodes (`episode()`); facts as above |
| Live panel (section 2) | everything | the same `<AppShell>` with the same data, read-only |

If a number cannot be computed (rate limit before first load), show "—" in its place. Never a default number.

## 7. What the backend does not provide yet (show nothing, or a planned state)

| Missing | Where it would show | Do now |
|---|---|---|
| Kaggle GPU hours used | Lab, sidebar | do not show GPU hours; the sidebar card shows "Next film" instead |
| YouTube views, retention | Analytics | "Planned" page (template 13) |
| Live channel memory in the browser (`used.json`) | Memory | show the memory seed + link "latest memory (updated after each film) ↗" |
| A place for each episode in `film.json` | Hero globe | `kit/places.json` (real places for real episodes and queued topics) |
| One fast status file for the site (fewer API calls) | everywhere | roadmap item "Studio feed" (APP_PAGES.md) |
