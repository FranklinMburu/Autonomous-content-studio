// The channels of the studio: one list, used by every page (sidebar, Home, Board, Library, Make, Guide).
// Only what is true in the code: each channel names the workflows that really make its videos.

export type LaneCode = 'HR' | 'TE' | 'SC' | 'WC' | 'BS';

export interface ChannelStep { name: string; who: 'ai' | 'you' | 'laptop'; text: string }

export interface Channel {
  code: LaneCode;
  name: string;
  short: string;            // one line: what the channel is
  makes: string;            // what one video is
  format: string;           // Short / film / explainer
  status: string;           // where the channel is today (honest)
  cadence: string;          // how often it makes videos
  color: string;            // a quiet tint for its badge only
  makeWorkflow?: string;    // the workflow the Make page starts
  ideasLabel: string;       // what "what's next" is called for this channel
  steps: ChannelStep[];     // how one video is made, in order (Guide + channel page)
}

export const CHANNELS: Channel[] = [
  {
    code: 'HR', name: 'Hidden Reasons', short: "True stories behind history's strangest acts",
    makes: 'a 1-minute animated history film', format: 'Film', status: 'Running on a schedule',
    cadence: 'Up to 5 films a day, on a timer', color: '#F5A524', makeWorkflow: 'make-story.yml', ideasLabel: 'Topic queue',
    steps: [
      { name: 'Topic', who: 'you', text: 'A topic waits in the queue (you can add or remove topics).' },
      { name: 'Draft', who: 'ai', text: 'Free AI models research the story, write the script and check every fact against sources.' },
      { name: 'Polish', who: 'you', text: 'You paste the draft into Claude and paste its answer back (one copy, one paste).' },
      { name: 'Film', who: 'ai', text: 'About 30 shots are painted on a free GPU, animated, voiced and scored with music.' },
      { name: 'Checks', who: 'ai', text: 'A picture checker and the final gates look at every shot and the sound.' },
      { name: 'Review', who: 'you', text: 'If a shot looks weak, you approve it or ask for a repaint of just those shots.' },
      { name: 'Upload', who: 'you', text: 'The finished film waits in "Ready to upload" until you post it.' },
    ],
  },
  {
    code: 'TE', name: 'Tech Education', short: 'Build Basics: how software really works',
    makes: 'a motion explainer with real-looking software in a moving 3D world: a Short, or a long 16:9 video with chapters', format: 'Explainer',
    status: 'Engine approved; videos made when you start them', cadence: 'When you start one',
    color: '#58A6FF', makeWorkflow: 'make-motion.yml', ideasLabel: 'Radar',
    steps: [
      { name: 'Topic', who: 'you', text: 'You give a topic, or pick one from the Radar (what tech viewers reward right now).' },
      { name: 'Script', who: 'ai', text: 'The AI writes the script and a visual plan, one scene per line. A long video gets an outline first: a story opening, a promise, something teased for the end, then 3-5 chapters written one at a time.' },
      { name: 'Voice', who: 'ai', text: "The channel's locked voice (Qwen3, chosen 13 Nov) reads every line; 6 machines share the work." },
      { name: 'Motion', who: 'ai', text: 'The motion engine draws every scene (real-looking apps, code, 3D layers, zooms into screens), split across up to 16 machines.' },
      { name: 'Checks', who: 'ai', text: 'Loudness, movement, layout and variety checks. A failed check opens a review.' },
      { name: 'Review', who: 'you', text: 'Watch it here and decide.' },
    ],
  },
  {
    code: 'SC', name: 'Streamer Clips', short: "The best moments of today's hottest streams, as Shorts",
    makes: 'a 15-40 s vertical Short of one real stream moment', format: 'Short',
    status: 'Engine working; first Shorts in review', cadence: 'When you start one (daily runs later, with your yes)',
    color: '#A371F7', makeWorkflow: 'clips-stream.yml', ideasLabel: "Who's hot",
    steps: [
      { name: "Who's hot", who: 'ai', text: 'Every run ranks streamers by what is getting views right now (and skips gambling).' },
      { name: 'Find', who: 'ai', text: 'The whole stream is read: sound, picture, chat and subtitles; an AI watches every candidate moment.' },
      { name: 'Edit', who: 'ai', text: 'An AI editor sets the start, the peak and the end, and writes the title.' },
      { name: 'Make', who: 'ai', text: 'Each Short is cut in 1080p in the look of the top clip channels (zoomed band, title box).' },
      { name: 'Reviewer', who: 'ai', text: 'A second AI watches the finished Short, runs 7 checks and scores it out of 10.' },
      { name: 'Review', who: 'you', text: 'Shorts scoring 6 or more wait for you: approve or skip. Rights are checked before posting.' },
      { name: 'Post', who: 'you', text: 'You post approved Shorts on the channel and mark them Posted.' },
    ],
  },
  {
    code: 'WC', name: 'World Clips', short: 'What the world is talking about: CEOs, news, culture',
    makes: 'a Short from a show or interview that is spiking today', format: 'Short',
    status: 'Working when your laptop is on', cadence: 'When you start one (needs the laptop on)',
    color: '#3FB950', makeWorkflow: 'clips-world.yml', ideasLabel: "Who's hot",
    steps: [
      { name: "Who's hot", who: 'ai', text: '27 shows, Google Trends and Wikipedia are read; videos far above their usual views are picked.' },
      { name: 'Details', who: 'laptop', text: "Your laptop reads each picked video's public details: YouTube's \"most replayed\" curve and subtitles." },
      { name: 'Find', who: 'ai', text: 'The moments viewers replay most, with what is said there, go to the AI judge, which picks and titles the best.' },
      { name: 'Fetch', who: 'laptop', text: 'Your laptop downloads only those minutes (YouTube blocks cloud servers).' },
      { name: 'Make', who: 'ai', text: 'The same Short maker as Streamer Clips: edit, render, AI reviewer.' },
      { name: 'Review', who: 'you', text: 'Approve or skip on the board.' },
    ],
  },
  {
    code: 'BS', name: 'Body Science', short: 'Pilot: quick explainers about the human body',
    makes: 'a short explainer with icons and captions', format: 'Explainer', status: 'Pilot (the first pipeline); paused',
    cadence: 'Paused', color: '#8B949E', ideasLabel: 'Topics',
    steps: [
      { name: 'Draft', who: 'ai', text: 'The first, older pipeline: research, script and fact check.' },
      { name: 'Render', who: 'ai', text: 'Icons, captions and a voice-over.' },
      { name: 'Upload', who: 'you', text: 'Finished videos wait in "Ready to upload".' },
    ],
  },
];

export const LANES: LaneCode[] = ['HR', 'TE', 'SC', 'WC', 'BS'];
export const channelOf = (code?: string | null) => CHANNELS.find(c => c.code === code) || null;

// The board's stages: the same words as the Notion Studio Board
export const STAGES = ['Picked', 'Making', 'Review', 'Approved', 'Posted', 'Skipped'] as const;
export type Stage = typeof STAGES[number];
export const STAGE_HELP: Record<Stage, string> = {
  Picked: 'Chosen to make next',
  Making: 'Being made, or waiting for one step from you',
  Review: 'Made: watch it and decide',
  Approved: 'Good to post',
  Posted: 'On YouTube',
  Skipped: 'Not good enough or not for us',
};

// Hidden Reasons film status -> board stage (the same mapping the feed uses for the Notion mirror)
export const FILM_STAGE: Record<string, Stage> = {
  draft: 'Making', polish: 'Making', polished: 'Making', review: 'Review', ready: 'Approved', finished: 'Approved', uploaded: 'Posted',
};
