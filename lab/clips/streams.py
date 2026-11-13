"""The scripts of our own two test streams (made by the studio, so we own every frame and every word).

Why synthetic: the clipping engine must be proven end to end, but we may only clip streams we have the rights to,
and this sandbox cannot (and must not, without Franklin's OK) download anyone's VOD. So the lab makes two streams of
its own with everything a real one has: long dull stretches, a few real moments with setup and payoff, a live chat
that reacts a few seconds late (with spam that is NOT a highlight), donation alerts and viewer-made clips.
The engine is never told where the moments are; `truth` below is only used to score the moment finder.

Each line: (speaker, text, energy 0-1, event or None). energy drives loudness/speed and the avatar's face.
"""

FILLER_A = [
    "okay okay, level six, this one is pretty chill",
    "chat, how is everybody doing tonight",
    "I need to drink some water, hold on",
    "this music is kind of a vibe, not gonna lie",
    "someone in chat asked what keyboard I use. it's just a normal one",
    "alright, coins, coins, more coins",
    "I feel like this level is longer than the last one",
    "we are just cruising right now, nothing crazy",
    "if you're new here, welcome, we're trying to beat level nine tonight",
    "my hands are cold, that's my excuse for later",
    "jump, jump, okay, nice",
    "I don't even know what this power up does",
    "chat says I'm bad. chat is correct",
    "we're vibing, we're vibing",
    "okay, slow section, let me fix my chair",
    "somebody asked if I eat breakfast. no. next question",
    "this little guy keeps following me. stop it",
    "I think I've played this game for like forty hours",
    "honestly the graphics are nice in this part",
    "okay we keep going",
]

FILLER_B = [
    ("maya", "okay we're back, welcome back everybody"),
    ("dev", "chat is moving fast tonight, hi everyone"),
    ("maya", "did you eat before the show? you look tired"),
    ("dev", "I had cereal. at six pm. I'm an adult"),
    ("maya", "somebody asked what mic we use. it's the cheap one"),
    ("dev", "honestly it sounds fine, nobody can tell"),
    ("maya", "let me read some chat, hold on"),
    ("dev", "people want the dog on camera again. the dog is asleep"),
    ("maya", "okay what's next on the list"),
    ("dev", "we have like three topics and zero plan"),
    ("maya", "that's the show, that's always the show"),
    ("dev", "drink some water, everybody, stay hydrated"),
    ("maya", "my coffee is cold, that's my whole personality now"),
    ("dev", "chat says the lighting is better today. thank you, I moved a lamp"),
]

# --- Stream A: "Neon Dash" gaming stream, streamer Zed (one voice) ---------------------------------------------
MOMENTS_A = [
    ("fail", [
        ("zed", "okay chat, level nine. I have never beaten level nine", 0.5, None),
        ("zed", "forty minutes on this level. forty. but this run feels different", 0.55, None),
        ("zed", "easy jump. easy jump. okay, the double jump, here it comes", 0.7, "approach"),
        ("zed", "no. no no no no", 0.95, "fail"),
        ("zed", "are you serious? I pressed it! I pressed the button!", 1.0, None),
        ("zed", "chat, you saw me press it. tell me you saw me press it", 0.9, None),
        ("zed", "forty minutes of my life. gone. on the last jump", 0.8, None),
    ]),
    ("funny", [
        ("zed", "oh, a donation. thank you so much", 0.5, "donation:Mike_T:$5:press the jump button earlier"),
        ("zed", "Mike says, press the jump button earlier", 0.55, None),
        ("zed", "Mike. Mike. thank you for the five dollars, Mike", 0.75, None),
        ("zed", "but I will find you, Mike. I know where you live. not really. but I will find you", 0.9, None),
    ]),
    ("clutch", [
        ("zed", "okay, one life left, low health, this is it", 0.6, "approach"),
        ("zed", "that gap is huge, that gap is actually huge, I can't make that", 0.75, None),
        ("zed", "here goes nothing", 0.8, "clutch"),
        ("zed", "no way. NO WAY! did you see that?", 1.0, None),
        ("zed", "clip it! somebody clip that right now!", 1.0, None),
        ("zed", "that is the cleanest thing I have ever done in my entire life", 0.85, None),
    ]),
    ("story", [
        ("zed", "okay real talk, yesterday I was screaming at this exact level", 0.5, None),
        ("zed", "and my mom walks in, and she goes, are you okay?", 0.55, None),
        ("zed", "and I said, no. I am not okay. I am losing to a square", 0.7, None),
        ("zed", "she didn't say anything. she just left. and came back with soup", 0.6, None),
        ("zed", "that's love, chat. that's what love is. soup", 0.8, None),
    ]),
    ("reveal", [
        ("zed", "wait. wait. chat, I need to tell you something", 0.6, None),
        ("zed", "I just opened the settings", 0.55, None),
        ("zed", "jump has been on the left trigger this whole time", 0.8, None),
        ("zed", "the whole time. three weeks. I have been pressing the wrong button for three weeks", 1.0, None),
        ("zed", "Mike was right. Mike was right the entire time", 0.9, None),
    ]),
]

# --- Stream B: "Late Night Couch" talk stream, hosts Maya and Dev (two voices) -------------------------------------
MOMENTS_B = [
    ("argument", [
        ("dev", "okay, settle this for me. is a hot dog a sandwich?", 0.55, None),
        ("maya", "no. absolutely not. next question", 0.6, None),
        ("dev", "it's meat. in bread. that is a sandwich, Maya", 0.75, None),
        ("maya", "then is a taco a sandwich? is a pizza a sandwich?", 0.85, None),
        ("dev", "a pizza is an open face sandwich, yes", 0.9, None),
        ("maya", "I am leaving. I am physically leaving this couch", 1.0, None),
    ]),
    ("shock", [
        ("maya", "okay, I have never told anyone this story", 0.5, None),
        ("maya", "last week I meant to send my sister a voice note", 0.55, None),
        ("maya", "it was me singing in the shower. full concert. eight minutes", 0.65, None),
        ("dev", "oh no. who did you send it to", 0.75, None),
        ("maya", "my boss. I sent it to my boss", 0.95, None),
        ("dev", "no way. what did he say?", 1.0, None),
        ("maya", "he replied, encore", 0.9, None),
    ]),
    ("reveal", [
        ("maya", "Dev, you left your laptop open before the show", 0.5, None),
        ("dev", "okay, and?", 0.5, None),
        ("maya", "your last search was, how to look busy on a podcast", 0.85, None),
        ("dev", "that is not, that is research. that is for a friend", 0.95, None),
        ("maya", "you are the friend, Dev", 0.9, None),
    ]),
    ("wholesome", [
        ("dev", "we got an email from a viewer, I want to read it", 0.45, None),
        ("dev", "she says she watched us every night in the hospital", 0.5, None),
        ("dev", "and the hot dog fight is what made her laugh again", 0.6, None),
        ("maya", "stop. I'm actually going to cry on stream", 0.75, None),
        ("dev", "so I guess a hot dog is a sandwich after all", 0.8, None),
    ]),
]

STREAMS = {
    "neon_dash": {"title": "Neon Dash: beating level nine (own test stream)", "kind": "gaming",
                  "voices": {"zed": ("am_michael", 1.08)}, "filler": FILLER_A, "moments": MOMENTS_A,
                  "gap_s": (65, 95), "chat_rate": 1.4, "seed": 7},
    "late_night_couch": {"title": "Late Night Couch, episode 12 (own test stream)", "kind": "talk",
                         "voices": {"maya": ("af_bella", 1.05), "dev": ("am_adam", 1.0)}, "filler": FILLER_B,
                         "moments": MOMENTS_B, "gap_s": (70, 100), "chat_rate": 1.2, "seed": 11},
}
