// The journey of a run, in plain words. GitHub step names are written for engineers; these lines say what is
// happening to the video. Unknown steps keep their own name (never hidden), setup steps are folded away.

export interface WorkflowInfo { lane: string | null; what: string; plain: Record<string, string> }

const SETUP = /^(Set up job|Complete job|Post |Run actions\/|actions\/|Tools$|Install|Restore |Speech model cache|Voice model cache|Get the brain|Setup check|Upload saved|Save finished|Resume saved|Run python3? - <<)/i;

export const WORKFLOWS: Record<string, WorkflowInfo> = {
  'Clips, a fresh stream to Shorts (find -> make -> review)': {
    lane: 'SC', what: 'Turns one stream into Shorts: find the best moments, make each Short, put them up for review',
    plain: {
      'The request (from the Studio app or the Actions form)': 'Reading your request',
      'Which stream': 'Choosing the stream (no gambling, long enough)',
      'Chat replay (in the background while the media downloads)': 'Downloading the chat',
      'Media (160p with sound, whole stream) and audio': 'Downloading the whole stream (small copy for finding)',
      "What was said (Kick's own subtitles; Whisper if there are none)": 'Reading what was said',
      'AI eyes (Gemini on one low-res frame every 6 s)': 'AI looks at the picture every 6 seconds',
      'Candidates (every signal family) and the AI judge (watches and hears each one)': 'AI judge watches every candidate moment and picks the best',
      'Make Short': 'Making this Short (download in 1080p, edit, render, review)',
      'Publish for review (GitHub pre-release, not YouTube)': 'Putting the Shorts up for your review (not on YouTube)',
      'Cards on the Studio Board (Review)': 'Adding cards to the Studio Board',
    },
  },
  'Clips, make Shorts from chosen moments': {
    lane: 'SC', what: 'Makes Shorts from moments already chosen',
    plain: { 'Make Short': 'Making this Short', 'Publish for review (GitHub pre-release, not YouTube)': 'Putting the Shorts up for review',
             'Cards on the Studio Board (Review)': 'Adding cards to the Studio Board' },
  },
  "Clips, who's hot today": {
    lane: 'SC', what: "Ranks today's streamers and world stories by what is getting views",
    plain: { 'Streamers lane': 'Ranking streamers', 'World lane': 'Ranking world stories (shows, trends, Wikipedia)',
             "Today's picks onto the Studio Board (Notion)": 'Adding the top picks to the board',
             'Keep the latest lists for the Studio app (release "clips-hot", replaced each run)': 'Saving the lists for the app' },
  },
  'Clips, World Clips Shorts (needs the laptop on)': {
    lane: 'WC', what: "World Clips: today's world picks to Shorts (your laptop fetches from YouTube)",
    plain: { "Today's world picks": "Reading today's world picks", "Ask the laptop for each video's details": 'Asking your laptop for each video\'s details',
             'Wait for the details (the laptop picks requests up every 10 minutes while it is on)': 'Waiting for your laptop (it checks every 10 minutes)',
             'Pick the moments (most replayed + what was said + the AI judge)': 'Finding the moments viewers replay most',
             'Ask the laptop for just those minutes, then wait for them': 'Your laptop downloads just those minutes',
             'Make Short': 'Making this Short', 'Publish for review (GitHub pre-release, not YouTube)': 'Putting the Shorts up for review',
             'Cards on the Studio Board (Review)': 'Adding cards to the Studio Board' },
  },
  'Clips, review Shorts again': { lane: 'SC', what: 'The AI reviewer watches Shorts it never reviewed', plain: { 'Review again': 'Reviewing the Shorts again' } },
  'Tech radar (what Tech Education should make next)': {
    lane: 'TE', what: 'Reads what tech viewers reward right now and ranks topics for Tech Education',
    plain: { 'Read the market and rank topics': 'Reading tech channels, GitHub, Hacker News, Hugging Face and Google Trends',
             'Keep it for the Studio app (release "tech-radar", replaced each run)': 'Saving the topics for the app',
             'Top topics onto the Studio Board (Picked, lane TE)': 'Adding the top 5 to the board' },
  },
  'Make a story video': {
    lane: 'HR', what: 'Makes one Hidden Reasons film (or its draft for your polish)',
    plain: { 'Choose what to make': 'Choosing the topic', 'AI writes a new episode': 'AI researches and writes the episode',
             'Use the given episode': 'Using the chosen episode', 'Check the episode': 'Checking facts and structure',
             'Make the film video (Kaggle GPU + assembly) and publish it': 'Painting the shots on a free GPU and putting the film together',
             'Make the video': 'Putting the video together', 'Publish as a release': 'Publishing the video',
             'Publish the draft for the polish step': 'Draft ready: waiting for your polish', 'Tell the owner if this run failed': 'Telling you if something failed',
             "Show the writer's report": "Writer's report" },
  },
  'Make a motion video (Tech Education)': {
    lane: 'TE', what: 'Makes one Tech Education motion video',
    plain: { 'Write a new episode (AI)': 'AI writes the script and the visual plan', 'Choose the episode': 'Choosing the episode',
             'Check the plan (offline)': 'Checking the plan', 'Make the video': 'Rendering the motion scenes, voice and music',
             'Publish as a release': 'Publishing the video' },
  },
  'Story schedule': {
    lane: 'HR', what: 'The timer: starts the next Hidden Reasons film when one is due',
    plain: { "Guardrails (don't pile up, stay inside the free GPU week)": 'Checking it is safe to start (free GPU hours, no pile-up)',
             'Pick the topic': 'Picking the next topic' },
  },
  'Story clock (wakes the schedule on time)': { lane: 'HR', what: 'Wakes the schedule on time', plain: {} },
  'Film queue (make accepted polishes into videos)': {
    lane: 'HR', what: 'Turns accepted polishes into films',
    plain: { 'Anything to make?': 'Looking for accepted polishes', 'Make the video': 'Making the film' },
  },
  'Review reply (approve or repaint)': {
    lane: 'HR', what: 'Acts on your review answer',
    plain: { 'Read the reply and the issue': 'Reading your answer', Approve: 'Approving: the film becomes ready to upload',
             'Repaint the weak shots and remake the video': 'Repainting the weak shots and remaking the film', 'Report a failure': 'Reporting a failure' },
  },
  "Polish return (paste Claude's answer)": {
    lane: 'HR', what: "Checks your polish and makes the film",
    plain: { 'Collect the answers': 'Reading your polish', 'Check each answer, then make the video or ask for fixes': 'Checking the polish, then making the film',
             'Tell the pull request what happened': 'Reporting back', 'Report a failure': 'Reporting a failure' },
  },
  'Studio action (from the Studio app)': {
    lane: null, what: 'A change you made in the app (board card or topic queue)',
    plain: { 'Check the request': 'Checking your request', 'Move the board card (Notion)': 'Moving the card on the Studio Board',
             'Change the topic queue': 'Updating the topic queue' },
  },
  'Site feed (data for the website)': {
    lane: null, what: 'Refreshes what this app shows (every 30 minutes and after each run)',
    plain: { 'Build the feed': 'Collecting the latest state', 'Mirror Hidden Reasons and Tech Education onto the Studio Board (Notion)': 'Updating the Notion board',
             'Publish it on the site-data branch (one commit, replaced each time)': 'Publishing it for the app' },
  },
  'Pipeline 1: draft': { lane: 'BS', what: 'Body Science pilot: drafts an explainer', plain: {} },
  'Pipeline 3: produce': { lane: 'BS', what: 'Body Science pilot: renders an explainer', plain: {} },
  'Make a video': { lane: 'BS', what: 'Body Science pilot: makes an explainer', plain: {} },
  'Lab (Kaggle GPU)': { lane: null, what: 'An experiment on the free GPU', plain: {} },
  'Website (GitHub Pages)': { lane: null, what: 'Publishes this website', plain: {} },
};

export const workflowInfo = (name: string): WorkflowInfo =>
  WORKFLOWS[name] || { lane: null, what: name, plain: {} };

/** Plain name of one step; null for setup steps (hidden). */
export function plainStep(workflow: string, step: string): string | null {
  const info = workflowInfo(workflow);
  if (info.plain[step]) return info.plain[step];
  const key = Object.keys(info.plain).find(k => step.startsWith(k));
  if (key) return info.plain[key];
  if (SETUP.test(step)) return null;
  return step;
}

/** Plain name of a job ("short (3)" -> "Short 3"). */
export function plainJob(job: string): string {
  const m = job.match(/^short \((\d+)\)$/);
  if (m) return `Short ${m[1]}`;
  return ({ find: 'Finding the moments', publish: 'Publishing for review', make: 'Making', start: 'Starting', act: 'Doing it',
            feed: 'Refreshing', hot: 'Ranking', reply: 'Answering', continue: 'Continuing' } as Record<string, string>)[job] || job;
}

export const STATE_WORDS: Record<string, string> = {
  queued: 'Waiting to start', running: 'Running', success: 'Done', failure: 'Failed', cancelled: 'Stopped',
  skipped: 'Skipped', waiting: 'Waiting', done: 'Done', failed: 'Failed',
};

export function ago(iso?: string | null): string {
  if (!iso) return '—';
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  if (s < 86400) return `${Math.round(s / 3600)} h ago`;
  return `${Math.round(s / 86400)} d ago`;
}
export function dur(sec?: number | null): string {
  if (sec == null) return '—';
  if (sec < 60) return `${Math.round(sec)} s`;
  if (sec < 3600) return `${Math.round(sec / 60)} min`;
  return `${(sec / 3600).toFixed(1)} h`;
}
