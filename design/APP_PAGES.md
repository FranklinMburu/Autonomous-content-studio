# Every page, every route, every flow

> Build exactly these pages and nothing else. If a page is not listed here, it does not exist. Every page uses the
> components and styles of the mockups (`design/mockups/`, `design/reference/pages/`) and the data rules of
> `DATA_CONTRACT.md` (no seed data).

## 1. Sitemap

```
/                     Landing (sections 1-6 + footer, BUILD_SPEC §4)
/films                Public film gallery (finished films only)
/films/:id            Public film page (player, the story's sources, made-with timeline)
/how-it-works         Same content as landing section 4, as its own page (for the nav link)
/pricing              "Free while we build" page (planned plans listed as Planned, no prices invented)
/docs                 Redirect to the repo README on GitHub
/app                  → /app/films
/app/films            Films (mockup 08 / 11 light)                 WORKSPACE
/app/films/:id        Film detail
/app/runs             Runs (mockup 09)
/app/runs/:id         Run detail (same as the right panel of 09, full width on phone)
/app/review           Review queue → first item open (mockup 10)
/app/review/:issue    Review one film
/app/polish           Polish queue + the copy / paste flow
/app/upload           Ready to upload queue
/app/channels         Channels                                      STUDIO
/app/channels/:code   One channel
/app/topics           Topic queue
/app/schedule         The 5 daily slots and what will run in them
/app/memory           What earlier films used (cast, places, music)
/app/brain            The free AI models                            ENGINE
/app/lab              GPU experiments and the painting engine
/app/guard            The checks (fact check, picture checker, review gate, alerts)
/app/analytics        Planned (template 13)                         GROW (all "Soon")
/app/trends           Planned
/app/publish          Planned
/app/thumbnails       Planned
/app/voices           Planned
/app/languages        Planned
/app/settings         Settings (theme, data source, about)
*                     404: "This page doesn't exist." + links to / and /app (same style as template 13)
```

The **landing live panel** (section 2) renders `/app/*` pages inside the browser frame, read-only, with the same
components (no iframe). Inside the panel, links to GitHub are shown but open in a new tab.

## 2. Navigation (app)

### Sidebar (desktop ≥ 1024 px): exactly this, in this order
| Group | Item | Phosphor icon (duotone, 19 px) | Badge (live) |
|---|---|---|---|
| WORKSPACE | Films | `FilmStrip` | — |
| | Runs | `Path` | number of runs in progress (hidden if 0) |
| | Review | `Eye` | open review issues |
| | Polish | `MagicWand` | open polish issues |
| | Upload | `UploadSimple` | open ready-to-upload issues |
| STUDIO | Channels | `Broadcast` | — |
| | Topics | `LightbulbFilament` | topics queued |
| | Schedule | `CalendarDots` | — |
| | Memory | `Archive` | — |
| ENGINE | Brain | `Brain` | — |
| | Lab | `Flask` | — |
| | Guard | `ShieldCheck` | open alerts (red dot only, no number) |
| GROW (collapsed, header shows "6 soon") | Analytics | `ChartLineUp` | "Soon" |
| | Trends | `TrendUp` | "Soon" |
| | Publish | `PaperPlaneTilt` | "Soon" |
| | Thumbnails | `ImageSquare` | "Soon" |
| | Voices | `MicrophoneStage` | "Soon" |
| | Languages | `Translate` | "Soon" |

- Top of the sidebar: mark + **Candela** + `Studio` (muted) + `CaretUpDown` (channel/workspace switcher, menu lists the
  channels from `DEFAULTS.channels`), then the search field "Search or jump to…" with `⌘K`.
- Bottom: the **Next film** card (time from `schedule()`, bar = films started today / 5, line "N of 5 started today ·
  $0"), then the owner row ("Franklin · Owner", `GearSix` → /app/settings). No sign-out (there is no sign-in).
- States: default (icon `#8A93A8`, text `--tx2`); hover (row `rgba(255,255,255,.04)`, icon `--tx`); active (amber 3 px
  bar on the left edge, amber duotone icon with a soft glow, row gradient `rgba(245,165,36,.16)→.04` + 1 px amber
  ring at 22%). GROW expands automatically when one of its pages is open (mockup 13). The sidebar scrolls if the
  window is short (the Next film card stays pinned at the bottom).
- Icons are **Phosphor only** (`@phosphor-icons/react`), duotone in the sidebar and on feature tiles, `bold` 11–15 px
  for carets/arrows, `regular` for inputs. No other icon set, no emoji, no brand logos except `GithubLogo` on GitHub links.

### Top bar (every app page)
Breadcrumb `Broadcast` icon + channel name + `/` + page name (bold). Right: bell (`Bell`, red dot when alerts are open;
menu lists the latest 5 alerts) and silver **+ New film** (opens GitHub, see DATA_CONTRACT §4).

### ⌘K command palette
Opens with ⌘K / Ctrl K or the search field. Groups: **Go to** (every sidebar page), **Films** (titles from `films()`),
**Topics** (from `topics()`), **Actions** (New film ↗, Run next now ↗, Edit topics ↗, Toggle theme). Arrow keys +
Enter. Esc closes. Style: 640 px wide dialog, `--s1`, radius 16, ring `--line2`, rows 40 px.

### Phone (< 640 px)
No sidebar. Bottom tab bar (mockup 12 right): Films, Runs, Review, Channels + **More** (`DotsThreeOutline`) opening a
sheet with every other page. Top: page title, channel chip.

## 3. Pages (what each one shows)

Copy below is final. "Data" points to `DATA_CONTRACT.md` §2.

### WORKSPACE

**Films** (mockup 08). Title "Films", subtitle "Hidden Reasons · 5 films a day · next at {next slot}". Filter tabs
All / Ready / Review / Making (counts). Four stat tiles: *Films this week* (releases last 7 days), *Passed every check*
(finished vs review this week, with %), *Next film* (time + "in 2 h"), *Cost* "$0" + "always". Film cards grid:
poster = the video's first frame (`<video preload="metadata" muted playsinline src="{video.url}#t=0.5">`), or for a
draft a neutral tile with the `FilmStrip` icon; status chip top-left; duration bottom-right when known. Right column:
**Making now** (the running run with its steps from `runSteps`; if none: "Nothing is being made right now. Next film
at 13:23.") and **Coming up** (next 3 slots × next 3 topics). **Films per day** bar chart: last 7 days, made vs
passed (silver-blue bars, no gold). Click a card → Film detail.

**Film detail** `/app/films/:id`. Left: 9:16 player (the release video, native controls, poster first frame), below it
"Download video ↗". Right: title, status chip, style chip (Film / Storyboard / Explainer), the checks line from the
release notes, **Sources behind every line** (`sourceSummary`, each with claim count and a link), **Script** (beats and
lines from `episode().script`), **Cast** (names from `film.cast`), **Shots** (count + era from `film.json`), **All runs**
(every release of this episode, newest first, each with its status and date). Actions: the ones that fit the status
(Approve/Repaint → issue ↗, Polish → issue ↗, Mark uploaded → issue ↗).

**Runs** (mockup 09). List: one row per Actions run (title, workflow, started, duration, state chip, segmented step bar
from `runSteps` when opened). Filter: All / Making / Needs you / Failed ("Needs you" = runs whose film is in review or
polish). Below the list: **Scheduled** rows for the next slots (time + topic + "Scheduled"). Right panel: the selected
run's timeline (step name, state dot, seconds), "Open on GitHub ↗". Running runs refresh every 30 s while the page is
visible.

**Review** (mockup 10). Left: list of open review issues (title, date, weak shots). Main: the film player, "Held for
review" badge, title, the failed checks (release notes "NEEDS REVIEW"), the weak shots by name (from the issue marker
`failed=`), **Approve** and **Repaint N shots** (both open the issue ↗ with a tooltip "Comment approve / repaint"),
sources list, and "Or polish with Claude" only if a polish issue exists for the same episode.

**Polish**. Left: open polish issues. Main: a 4-step guide (the same steps as the issue: Copy → claude.ai → Copy answer →
Paste as a comment), the prompt in a read-only box with **Copy** (copies `polishPrompt`), **Open claude.ai ↗**, and
**Paste Claude's answer on GitHub ↗** (the issue). Empty: "No polish needed right now."

**Upload**. Cards for open ready-to-upload issues: player, title, suggested title and description (from the issue
body), **Download video ↗**, **Open YouTube Studio ↗** (`https://studio.youtube.com`), **Mark uploaded ↗** (the issue).
A second list "Uploaded" (closed issues, last 20).

### STUDIO

**Channels**. One card per channel in `DEFAULTS.channels`: name, code chip, niche line, style (Film), "5 films a day",
counts (made / review / polish / queued). The explainer pipeline's `statusBoard()` table is shown as a second card
"Explainer pipeline (Body Science pilot)". **Add a channel** = planned (disabled button with "Soon").

**Channel** `/app/channels/:code`. Header with the channel name; tabs Films / Topics / Schedule / Memory filtered to
this channel (same components).

**Topics**. The queue in order (number, topic, place + year from `places.json` if known, "made"/"queued" chip if the
topic already has a film). Note: "When fewer than 5 are left, the free models suggest new ones." **Edit topics ↗**.

**Schedule**. Today and the next two days as three columns × 5 slots (local time), each slot shows the topic it will
take (queue order) or the film it made (runs of that slot). Line: "Times come from the story schedule on GitHub."

**Memory**. Three lists from `memorySeed()` (cast already used, places used, music used) with "Latest memory (updated
after each film) ↗" linking to the `channel-memory` release.

### ENGINE

**Brain**. The script models from `models()` (`story_script_models`) as rows: provider, model, role (writer / checker),
"free tier" chip. Copy: "Four free models write each script; the best draft wins." No usage numbers (not available).

**Lab**. Painting engine summary (Kaggle T4 × 2, SDXL + face lock, LTX-Video clips, picture checker: text only from
the docs), and the list of `labRuns()` (tag, date, file count, link ↗).

**Guard**. Three cards: **Fact check** (claims supported across made films, from release notes), **Picture checker**
(weak shots in open reviews), **Review gate** (films held = open review issues). Below: **Alerts** (from `alerts()`,
newest first, each with a link ↗).

### GROW (planned pages: use template 13 exactly, change icon, title, line, three rows and "What it needs")

| Page | Line | Three rows | What it needs |
|---|---|---|---|
| Analytics | See how every film performs on YouTube, and let the studio learn what your audience loves. | Views and watch time per film · Learns from results · Weekly digest | a read-only YouTube Analytics connection (free) |
| Trends | Find true stories people are searching for, before you run out of topics. | Rising history searches · Checked against the channel memory · One click to queue | a free trends source and a topic-scoring step in the pipeline |
| Publish | Upload finished films to YouTube for you, after you approve them. | Approve once, upload automatically · Title, description and sources filled in · Never posts without you | the YouTube Data API upload scope and a sign-in |
| Thumbnails | A cover for every film, painted from its strongest shot. | Three options per film · Same faces as the film · Text kept short and readable | a thumbnail step in the Lab |
| Voices | Choose and test narrator voices for each channel. | Listen side by side · One voice per channel · Free, open models only | a voice library page in the Lab |
| Languages | The same film in more languages, with the same facts. | Translated and re-checked script · New narration · Subtitles included | a translation step + voice per language |

Rule for every planned page: **no numbers, no fake charts, no sample content.** Only the template.

### Settings
Theme (Dark / Light / System), Data source (repo and branch, read-only text + "Change in code: DEFAULTS"), Cache
("Clear cached data" button), About (version, links to GitHub and the docs). Nothing else.

## 4. Public pages

**/films**: grid of finished films (`ready`, `uploaded`, `finished`) with the same cards as section 6 of the landing
(poster = first frame, title, place + year if known). **/films/:id**: player, title, the story in one paragraph
(first two script lines), **Sources** list, "Made with Candela" strip (research → script → fact check → painted →
checked). **/pricing**: title "Free while we build.", line "Candela runs on free tiers. Plans for teams are planned.",
one card "Studio — Free" with the real limits (5 films a day per channel, GitHub + Kaggle free tiers), a second card
"Teams — Planned" (no price). **/how-it-works**: landing section 4 as a page.

## 5. Flows (from the owner's point of view)

1. **A film is made on schedule:** Schedule shows the slot → at the time, Runs shows a new *Making* row → steps fill in →
   the film appears in Films as *Ready to upload*, *Review* or *Needs your polish*; the matching badge goes up.
2. **Needs your polish:** badge on Polish → open → Copy → claude.ai → paste the answer on the GitHub issue ↗ → the run
   continues by itself (a new *Making* row appears in Runs).
3. **Review:** badge on Review → watch the film, see the weak shots → Approve ↗ (becomes *Ready to upload*) or Repaint ↗
   (a new run repaints only those shots).
4. **Upload:** Upload page → Download → YouTube Studio ↗ → Mark uploaded ↗ (moves to *Uploaded*).
5. **Make one now:** + New film ↗ (topic) or Schedule → Run next now ↗.
6. **Visitor on the landing:** hero (sun rises) → live panel (clicks around the real studio, read-only) → family →
   how it works → Studio World → films → Start free (goes to /app).

## 6. Roadmap placeholders (backend work, shown only as "Planned"; never fake them)

- **Studio feed:** the pipeline writes one `status.json` (films, runs, GPU hours, memory) to a `site-data` branch after
  every run, so the site needs one request instead of six and can show GPU hours and live memory.
- **Place in film.json:** each episode stores where and when its story happened (replaces `kit/places.json`).
- **Sign in with GitHub:** approve, repaint, polish and add topics from the app itself (a GitHub App, read/write issues
  and dispatch workflows only).
- **Notifications:** web push when a film needs you.
- **Multi-channel:** Body Science and the six ranked channel ideas as channels in the switcher.
- Plus the six GROW pages above.
