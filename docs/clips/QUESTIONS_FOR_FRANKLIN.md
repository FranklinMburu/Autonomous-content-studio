# Questions for Franklin (clipping engine)

These are the only things that need you: rights, accounts, keys, downloads and publishing. Everything else is built
and tested on the `clips-engine` branch (PR, not merged).

## Q1. A free YouTube Data API key, for the winners-vs-baseline dataset

**What:** an API key ("YouTube Data API v3") in the studio's existing Google Cloud project (`content-studio`), saved
as the GitHub secret `YOUTUBE_API_KEY`.

**Why:**
- the research needs 60+ winning and 60+ weak recent clips from the same channels, with views and age;
- the API is the only permitted way to get those numbers. YouTube blocks its feeds to bots, and scraping breaks its
  terms.

**Cost:** $0. The free quota is 10,000 units a day; the collector uses about 1 unit per 50 videos. No card is needed.

**Steps if yes:**
1. console.cloud.google.com → APIs & Services → Credentials → Create credentials → API key.
2. Restrict it to "YouTube Data API v3".
3. In the studio repo → Settings → Secrets → Actions → New secret `YOUTUBE_API_KEY`.

I add a manual "Clips dataset" workflow next. Options: yes / no / later.

## Q2. Picture and sound features of other people's clips

The dataset can measure views, length and titles with the key alone. Cut rate, caption style and hook timing need the
video files. YouTube's terms forbid downloading them. Options:

- **a)** You save clips you choose, as you did for `video-ideas/refs`, into a folder on your computer. I measure them
  from there. (This is how the 14 references were measured.)
- **b)** We measure only Kick clips, through Kick's own download button (official), for channels in campaigns we join.
- **c)** Metadata only (no picture features), which is weaker.

## Q3. Which stream(s) may we clip? (the real proof)

The engine refuses any stream without `rights.json`. To prove it on a real stream, I need **one** of:

- **a)** A clipping campaign you join (e.g. on Content Rewards / Whop) whose terms allow clipping that streamer.
  Joining means creating an account and accepting terms, so only you can do it. Then you'd download a VOD the
  campaign provides (or a Kick clip through Kick's download button) and put it in a connected folder. I run the
  engine.
- **b)** A streamer's written permission (an email or DM screenshot is enough as proof).
- **c)** Your own stream, if you stream.

Rule I will keep: no gambling or casino streams, even when a campaign pays for them. They count as gambling ads in
some countries, and Kick's campaigns are tied to Stake.

## Q4. A Twitch developer app (optional, makes moment-finding stronger)

Twitch's `Get Clips` API gives us where viewers clipped a stream, and how many views each clip got. That is the
strongest moment signal. It needs a free Twitch developer app (an account plus a client ID and secret as GitHub
secrets). Options: yes / no / later.

## Q5. Notion and the project docs

The Notion workspace connected to this session is not the studio's: searching it finds no "YouTube Creator Studio"
page. The claude.ai project-doc tool was not available to me either. So I could not create:
- the Notion page under YouTube Creator Studio (research report + engine, with system changes on the parent page);
- the project doc.

Their text is ready: `docs/clips/RESEARCH.md` and `docs/CLIPS_ENGINE.md`. A session with the studio's Notion
connected can paste them.

## Q6. Merge the PR?

The engine is isolated: own folder, workflow, cache key and label. Every existing test passes. Merging adds the
manual workflow "Make clips (live streams)". Nothing runs on a schedule and nothing is published. Options: merge /
wait for the first real-stream proof.

## Q7. Publishing

No clip has been uploaded anywhere. Before any upload: YouTube's 1 Oct 2026 change down-ranks re-uploads "without
significant changes". Every clip has our hook, cold open, captions and framing, but you decide whether a clip goes up,
and on which channel.
