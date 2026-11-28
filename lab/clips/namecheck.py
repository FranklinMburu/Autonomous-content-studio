"""Name check for judge titles (Clipping Lab, 28 Nov 2026).

The judge sometimes writes a title around a celebrity nobody said ("LeBron James dressed as Deadpool" when Kai said
"I got this dead booth fit"). Shipping that title breaks "real, not fake". This finds the proper names in a title and
says which of them nothing in the stream supports. Zero AI calls, stdlib only.

A name (a title word that starts with a capital and has lowercase letters, not the first word, not the streamer, not a
template word) counts as SUPPORTED when any of these holds (rule fixed before testing, 28 Nov):
  1. it matches a word, or two adjacent words joined, said in the watched window (candidate t +- 75 s): difflib ratio
     >= 0.8, or the same Soundex code with ratio >= 0.6 (speech-to-text errors on names);
  2. it is said 3+ times in the whole stream (places and people the stream is about: Japan, Tokyo);
  3. it shares a 4+ letter stem with a word of the stream's own title (JAPAN -> Japanese).
Titles written in Title Case (more than 60% of words capitalised) are skipped: capitals carry no signal there.
"""
import difflib, re, unicodedata
from collections import Counter

TEMPLATE = {"the", "moment", "no", "way", "when", "this", "that", "his", "her", "a", "an", "i"}
RATIO, SOUNDEX_RATIO, STREAM_COUNT, WINDOW = 0.8, 0.6, 3, 75


def norm(w):
    w = unicodedata.normalize("NFKD", w)
    w = "".join(c for c in w if not unicodedata.combining(c)).lower()
    w = re.sub(r"['’]s$", "", w)
    return re.sub(r"[^a-z0-9]", "", w)


def soundex(w):
    w = norm(w)
    if not w or not w[0].isalpha():
        return w
    codes = {**dict.fromkeys("bfpv", "1"), **dict.fromkeys("cgjkqsxz", "2"), **dict.fromkeys("dt", "3"),
             "l": "4", **dict.fromkeys("mn", "5"), "r": "6"}
    out, last = w[0].upper(), codes.get(w[0], "")
    for c in w[1:]:
        d = codes.get(c, "")
        if d and d != last:
            out += d
        if c not in "hw":
            last = d
    return (out + "000")[:4]


def names(title, streamer=""):
    """Proper-name tokens of a title (original spelling)."""
    toks = re.findall(r"[A-Za-zÀ-ɏ][\wÀ-ɏ'’-]*", title or "")
    if not toks:
        return []
    caps = [t for t in toks if t[0].isupper()]
    if len(toks) >= 4 and len(caps) / len(toks) > 0.6:
        return []                                   # Title Case: capitals mean nothing
    skip = {norm(x) for x in (streamer or "").split()} | TEMPLATE
    out = []
    for i, t in enumerate(toks):
        if i == 0 or not t[0].isupper() or not any(c.islower() for c in t):
            continue                                # first word, lowercase word, or ALL-CAPS emphasis (SHOCKED, GTR)
        if norm(t) in skip or not norm(t):
            continue
        out.append(t)
    return out


class Checker:
    def __init__(self, words, streamer="", stream_title=""):
        self.words = sorted(((float(w["start"]), norm(w["w"])) for w in words if w.get("w") is not None), key=lambda x: x[0])
        self.count = Counter(w for _, w in self.words if w)
        self.streamer = streamer
        self.title_words = [norm(x) for x in re.findall(r"\w+", stream_title or "") if len(norm(x)) >= 4]

    def window(self, t):
        ws = [w for s, w in self.words if t - WINDOW <= s <= t + WINDOW and w]
        return set(ws) | {a + b for a, b in zip(ws, ws[1:])}

    def supported(self, name, win):
        n = norm(name)
        if self.count.get(n, 0) >= STREAM_COUNT:
            return True
        if any(len(n) >= 4 and (n.startswith(tw[:4]) and tw.startswith(n[:4])) for tw in self.title_words):
            return True
        sx = soundex(n)
        for w in win:
            r = difflib.SequenceMatcher(None, n, w).ratio()
            if r >= RATIO or (r >= SOUNDEX_RATIO and soundex(w) == sx):
                return True
        return False

    def unsupported(self, title, t):
        """Names in the title that nothing supports (empty list = title is fine)."""
        ns = names(title, self.streamer)
        if not ns:
            return []
        win = self.window(float(t))
        return [x for x in ns if not self.supported(x, win)]


if __name__ == "__main__":
    ws = [{"w": w, "start": i} for i, w in enumerate("So I got this dead booth fit Sebastian Japan Japan Japan".split())]
    c = Checker(ws, "Kai Cenat", "JAPAN NIGHT LIFE STREAM")
    for ti in ("The moment Kai Cenat realized LeBron James was dressed as Deadpool",
               "The moment Kai Cenat realized his cameraman Sebastian quit on stream",
               "The moment Kai Cenat REALIZED what happens at a Japanese muscle bar",
               "The moment Kai Cenat was SHOCKED by an 800 horsepower GTR in Tokyo"):
        print(c.unsupported(ti, 5), "|", ti)
