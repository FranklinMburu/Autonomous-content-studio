"""Layout: where the facecam, the gameplay and the speakers are, and which 9:16 layout fits the moment.

Layouts (all 1080x1920):
  stack     facecam on top (40%), gameplay below (60%): game streams with a facecam overlay
  split2    two speakers stacked (50/50): talk streams / podcasts with two people on screen
  speaker   one speaker followed by a smooth 9:16 crop: IRL / just chatting with one person
  letterbox the 16:9 picture whole in the middle on a blurred copy of itself: anything else (never crops away
            what matters; the classic stream-clip look, also the hook layout of the Kick references we measured)

Detection uses only OpenCV (Apache-2.0) and numpy, CPU, no downloads at run time:
  1. faces: OpenCV's bundled Haar cascade (frontal face), voted over frames;
  2. facecam overlay: a persistent rectangle (border) in a corner, from edges of the median frame;
  3. people that move: temporal-variance blobs (catches faces Haar misses, e.g. drawn avatars or side views).
"""
import os, subprocess
from pathlib import Path

import numpy as np


def sample_frames(video, start, end, n=24, w=640):
    """n frames evenly spread over [start, end], scaled to width w (RGB uint8)."""
    import cv2
    cap = cv2.VideoCapture(str(video))
    W0, H0 = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    h = int(round(w * H0 / W0 / 2) * 2) if W0 else 360
    frames = []
    for t in np.linspace(start, max(start, end - 0.1), n):
        cap.set(cv2.CAP_PROP_POS_MSEC, float(t) * 1000)
        ok, f = cap.read()
        if ok:
            frames.append(cv2.resize(f, (w, h))[:, :, ::-1])
    cap.release()
    return frames, (int(W0), int(H0))


def cascade():
    import cv2
    if not hasattr(cv2, "CascadeClassifier"):   # OpenCV 5 moved it out; the workflow pins 4.10 which has it
        return None
    for p in [Path(getattr(cv2, "data", None).haarcascades if hasattr(cv2, "data") else "") / "haarcascade_frontalface_default.xml",
              Path(os.environ.get("CLIPS_HAAR", "/nonexistent"))]:   # CLIPS_HAAR: a copy, where cv2 ships none
        if p.exists():
            c = cv2.CascadeClassifier(str(p))
            if not c.empty():
                return c
    return None


def faces(frames):
    """Face boxes (x, y, w, h, votes) in sampled-frame pixels, voted across frames."""
    import cv2
    c = cascade()
    if c is None or not frames:
        return []
    hits = []
    for f in frames:
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        for (x, y, w, h) in c.detectMultiScale(g, 1.1, 6, minSize=(max(24, g.shape[1] // 30),) * 2):
            hits.append((x, y, w, h))
    groups = []
    for b in hits:
        for g in groups:
            if abs(g[0][0] + g[0][2] / 2 - b[0] - b[2] / 2) < b[2] and abs(g[0][1] + g[0][3] / 2 - b[1] - b[3] / 2) < b[3]:
                g.append(b)
                break
        else:
            groups.append([b])
    out = []
    for g in groups:
        if len(g) >= max(2, 0.25 * len(frames)):
            a = np.median(np.array(g), axis=0)
            out.append((*[float(v) for v in a], len(g)))
    return sorted(out, key=lambda b: -b[4])


def _runs(mask, axis):
    """Longest run of True along `axis` for every row/column."""
    m = mask if axis == 0 else mask.T
    best = np.zeros(m.shape[1], int)
    cur = np.zeros(m.shape[1], int)
    for row in m:
        cur = np.where(row, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def overlay_rect(frames):
    """A facecam overlay: four straight edges that stay put for the whole clip (a border or a hard picture edge),
    forming a box of 2-25% of the frame in a corner. Found from the median frame's edges, line by line."""
    import cv2
    if len(frames) < 4:
        return None
    med = np.median(np.stack(frames), axis=0).astype(np.uint8)
    H, W = med.shape[:2]
    e = cv2.Canny(cv2.cvtColor(med, cv2.COLOR_RGB2GRAY), 50, 150) > 0
    ev = cv2.dilate(e.astype(np.uint8), np.ones((1, 3), np.uint8)) > 0     # tolerate 1 px wobble
    eh = cv2.dilate(e.astype(np.uint8), np.ones((3, 1), np.uint8)) > 0
    vr, hr = ev.sum(axis=0), eh.sum(axis=1)

    def lines(counts, need, k=40):
        out = []
        for i in np.argsort(-counts):
            if counts[i] < need or len(out) >= k:
                break
            if all(abs(int(i) - j) > 2 for j in out):
                out.append(int(i))
        return sorted(out)
    xs, ys = lines(vr, 0.12 * H), lines(hr, 0.12 * W)
    best, bscore = None, 0.0
    for i, x1 in enumerate(xs):
        for x2 in xs[i + 1:]:
            w = x2 - x1
            if not 0.12 * W <= w <= 0.5 * W:
                continue
            for j, y1 in enumerate(ys):
                for y2 in ys[j + 1:]:
                    h = y2 - y1
                    area = w * h / (W * H)
                    if not 0.02 <= area <= 0.25 or not 0.8 <= w / max(h, 1) <= 2.4:
                        continue
                    cx, cy = (x1 + w / 2) / W, (y1 + h / 2) / H
                    if not ((cx < 0.35 or cx > 0.65) and (cy < 0.4 or cy > 0.6)):
                        continue
                    cov = (ev[y1:y2, x1].mean() + ev[y1:y2, x2].mean() + eh[y1, x1:x2].mean() + eh[y2, x1:x2].mean()) / 4
                    if cov >= 0.85 and cov * area > bscore:
                        best, bscore = (x1, y1, w, h), cov * area
    return best


def movers(frames, k=2):
    """Up to k regions where the picture keeps changing (people talking, gesturing), largest first."""
    import cv2
    if len(frames) < 4:
        return []
    g = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32) for f in frames])
    v = cv2.GaussianBlur(g.std(axis=0), (0, 0), 6)
    thr = np.percentile(v, 96)
    if thr < 2:
        return []
    m = (v >= thr).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(m)
    comps = sorted([(stats[i][4], *stats[i][:4]) for i in range(1, n)], reverse=True)[:k]
    return [(float(x), float(y), float(w), float(h)) for _, x, y, w, h in comps if _ > 0.002 * m.size]


def choose(video, start, end, kind_hint=None):
    """Pick the layout for one clip window. Returns a dict in SOURCE pixel coordinates."""
    frames, (W0, H0) = sample_frames(video, start, end)
    if not frames:
        return {"kind": "letterbox", "src": [W0, H0], "why": "no frames"}
    fh, fw = frames[0].shape[:2]
    sx = W0 / fw
    S = lambda b: [round(v * sx) for v in b[:4]]  # noqa: E731
    fc = faces(frames)
    ov = overlay_rect(frames)
    mv = movers(frames)
    # game stream: a facecam overlay in a corner -> stack
    if ov is not None:
        cam = list(ov)
        # where the action is: horizontal centre of the picture change outside the facecam
        import cv2
        g = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32) for f in frames]).std(axis=0)
        g[int(cam[1]):int(cam[1] + cam[3]), int(cam[0]):int(cam[0] + cam[2])] = 0
        g[: int(0.12 * fh)] = 0                       # HUD / score bar
        col = g.sum(axis=0)
        ax = float((col * np.arange(fw)).sum() / col.sum()) if col.sum() > 0 else fw / 2
        inside = [f for f in fc if cam[0] <= f[0] + f[2] / 2 <= cam[0] + cam[2] and cam[1] <= f[1] + f[3] / 2 <= cam[1] + cam[3]]
        return {"kind": "stack", "src": [W0, H0], "cam": S(cam), "face": S(inside[0]) if inside else None,
                "action_x": round(ax * sx),
                "why": "facecam overlay found in a corner" + (" (face inside)" if inside else "")}
    people = [f[:4] for f in fc[:2]] if len(fc) >= 1 else []
    if len(people) < 2 and len(mv) >= 2 and kind_hint != "single":
        a, b = mv[:2]
        if abs((a[0] + a[2] / 2) - (b[0] + b[2] / 2)) > 0.25 * fw:
            people = [a, b]
    if len(people) >= 2:
        people = sorted(people, key=lambda b: b[0])
        return {"kind": "split2", "src": [W0, H0], "people": [S(p) for p in people],
                "why": "two people on screen" + (" (faces)" if len(fc) >= 2 else " (moving regions)")}
    if len(people) == 1 or fc:
        p = people[0] if people else fc[0][:4]
        return {"kind": "speaker", "src": [W0, H0], "people": [S(p)], "why": "one person on screen"}
    return {"kind": "letterbox", "src": [W0, H0], "why": "no facecam or person found: keep the whole picture"}


def _ffprobe_wh(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


def active_person(video, people, a, b, n=8):
    """Which of `people` (source-pixel boxes) is talking in [a, b]: the one whose mouth area changes most."""
    if len(people) < 2:
        return 0
    frames, (W0, H0) = sample_frames(video, a, max(a + 0.3, b), n=n, w=480)
    if len(frames) < 2:
        return 0
    k = 480 / W0
    g = np.stack([f.mean(axis=2) for f in frames])
    d = np.abs(np.diff(g, axis=0)).mean(axis=0)
    act = []
    for x, y, w, h in people:
        # the person's box and a margin around it: a talking mouth moves it far more than a listener's blinks
        y0, y1 = int((y - h * 0.25) * k), int((y + h * 1.25) * k)
        x0, x1 = int((x - w * 0.25) * k), int((x + w * 1.25) * k)
        act.append(float(d[max(0, y0):y1, max(0, x0):x1].mean()) if y1 > y0 and x1 > x0 else 0.0)
    return int(np.argmax(act))
