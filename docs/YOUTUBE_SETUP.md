# Automatic YouTube upload: one-time setup

Until this is done, you upload each video by hand from the "Ready to upload" issue (about a minute).
Everything here is free. Do it whenever you're ready; the studio works without it.

## Why there's a wait

YouTube locks videos uploaded through an API project that hasn't passed its compliance audit as **private**, and
those can't be appealed. So the upload workflow stays switched off until Google approves the audit.

## Steps

1. **Google Cloud project** (free, no card): console.cloud.google.com → create a project named `content-studio`.
2. **Enable the API:** APIs & Services → Library → "YouTube Data API v3" → Enable.
3. **Consent screen:** APIs & Services → OAuth consent screen → External. App name `Content Studio`, your email.
   Add the scope `youtube.upload`. Add yourself as a test user.
4. **Avoid weekly expiry:** while the app is in "Testing", Google's sign-in expires every 7 days. Click
   **Publish app** to move it to "In production". For your own channel you can keep using it unverified
   (Google shows an "unverified app" warning that you click through once). Check the screen's current wording.
5. **Credentials:** APIs & Services → Credentials → Create credentials → OAuth client ID → **Desktop app** →
   download the JSON file. Keep it on your computer; never share it.
6. **Sign in once:** in the studio folder on your laptop run
   `python youtube_auth.py C:\path\to\client_secret.json`
   Approve in the browser with the channel's Google account. The script stores three secrets in GitHub
   (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN) without printing them.
7. **Request the audit:** https://support.google.com/youtube/contact/yt_api_form
   - Use case: "A personal tool that uploads my own animated educational Shorts to my own channel after I approve
     each one. No other users, no data collection."
   - Attach a short screen recording: the "Ready to upload" issue, adding the `approve-publish` label, and the
     sign-in screen from step 6.
   - Google says it replies "as soon as possible"; plan for a few weeks.
8. **When approved:** in the studio repo → Settings → Secrets and variables → Actions → **Variables** →
   New variable `YOUTUBE_UPLOADS_APPROVED` = `true`.

## Then, each video

Open its "Ready to upload" issue and add the label **approve-publish**. The video is uploaded publicly with its
title, description, sources and tags, the issue closes, and the video is recorded as published. Only you (the
repo owner) can trigger it.
