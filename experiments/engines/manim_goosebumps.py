"""Manim test: the goosebumps script, vertical 1080x1920, timed to the shared Kokoro narration."""
import json
from pathlib import Path

from manim import *

config.pixel_width, config.pixel_height, config.frame_rate = 1080, 1920, 30
config.frame_width, config.frame_height = 9, 16
config.background_color = "#14213d"

T = json.loads((Path(__file__).parent.parent / "shared" / "timing.json").read_text())
LINES = T["lines"]
INK, ACC, ACC2, SOFT = "#f8f4ec", "#fca311", "#4cc9f0", "#8d99ae"


class Goosebumps(Scene):
    def setup(self):
        self.t = 0.0
        self.cap = None

    def play_t(self, *anims, run_time=0.8):
        self.play(*anims, run_time=run_time)
        self.t += run_time

    def until(self, ts):
        if ts > self.t + 0.02:
            self.wait(ts - self.t)
            self.t = ts

    def caption(self, i):
        line = LINES[i]
        self.until(line["start"])
        words = line["text"].split()
        rows, cur = [], ""
        for w in words:
            if len(cur) + len(w) > 26:
                rows.append(cur.strip()); cur = ""
            cur += w + " "
        rows.append(cur.strip())
        txt = VGroup(*[Text(r, font_size=40, color=INK, weight=BOLD) for r in rows]).arrange(DOWN, buff=0.15)
        txt.to_edge(DOWN, buff=1.2)
        box = BackgroundRectangle(txt, color="#000000", fill_opacity=0.35, buff=0.25)
        new = VGroup(box, txt)
        if self.cap is None:
            self.play_t(FadeIn(new, shift=UP * 0.2), run_time=0.3)
        else:
            self.play_t(FadeOut(self.cap, run_time=0.2), FadeIn(new, run_time=0.3), run_time=0.3)
        self.cap = new

    def skin(self, width=7, bumps=0, y=0):
        base = Line(LEFT * width / 2, RIGHT * width / 2, color=ACC, stroke_width=8).shift(UP * y)
        g = VGroup(base)
        for k in range(bumps):
            x = -width / 2 + (k + 0.5) * width / bumps
            g.add(Arc(radius=0.25, start_angle=0, angle=PI, color=ACC, stroke_width=8).move_to([x, y + 0.12, 0]))
        return g

    def construct(self):
        # beat 0: hook
        self.caption(0)
        star = Star(n=5, outer_radius=1.6, color=ACC, fill_opacity=0.9).shift(UP * 3)
        win = Text("a big win", font_size=64, color=INK, weight=BOLD).next_to(star, DOWN, buff=0.6)
        self.play_t(GrowFromCenter(star), FadeIn(win, shift=UP * 0.3), run_time=0.8)
        flat = self.skin(bumps=0, y=-1.5)
        bumpy = self.skin(bumps=7, y=-1.5)
        self.play_t(Create(flat), run_time=0.6)
        self.until(2.6)
        self.play_t(Transform(flat, bumpy), Indicate(star, color=WHITE), run_time=1.0)
        hook = VGroup(star, win, flat)

        # beat 1: triggers + mechanism
        self.caption(1)
        self.play_t(FadeOut(hook), run_time=0.4)
        labels = ["cold", "fear", "music", "horror film"]
        chips = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.3, width=3.6, height=1.0, color=ACC2, fill_opacity=0.15),
                                Text(l, font_size=44, color=INK)) for l in labels]).arrange_in_grid(2, 2, buff=0.4).shift(UP * 2)
        for c in chips:
            c[1].move_to(c[0])
        title = Text("Goosebumps start with...", font_size=46, color=SOFT).next_to(chips, UP, buff=0.6)
        self.play_t(FadeIn(title), LaggedStart(*[FadeIn(c, scale=0.8) for c in chips], lag_ratio=0.25), run_time=1.6)
        self.caption(2)
        self.play_t(FadeOut(chips), FadeOut(title), run_time=0.4)
        surface = Line(LEFT * 4, RIGHT * 4, color=ACC, stroke_width=8).shift(UP * 1)
        follicle = Line(DOWN * 1.2, UP * 1, color=SOFT, stroke_width=6).shift(UP * 0.0)
        hair = Line(ORIGIN, RIGHT * 2.2 + UP * 0.6, color=INK, stroke_width=7).shift(UP * 1)
        muscle = Line(RIGHT * 1.6 + DOWN * 0.4, DOWN * 0.6, color="#e63946", stroke_width=12)
        mlabel = Text("tiny muscle", font_size=36, color="#e63946").next_to(muscle, DOWN, buff=0.3)
        nerve = VGroup(RoundedRectangle(corner_radius=0.3, width=5.4, height=1.0, color=ACC2),
                       Text("fight-or-flight nerves", font_size=36, color=ACC2)).shift(UP * 4.3)
        nerve[1].move_to(nerve[0])
        self.play_t(Create(surface), Create(follicle), Create(hair), run_time=1.0)
        self.play_t(Create(muscle), FadeIn(mlabel), run_time=0.8)
        self.until(LINES[2]["start"] + 3.0)
        self.play_t(Rotate(hair, angle=PI / 2 - 0.27, about_point=hair.get_start()),
                    muscle.animate.put_start_and_end_on(RIGHT * 0.8 + DOWN * 0.2, DOWN * 0.6), run_time=1.2)
        self.until(LINES[2]["start"] + 5.0)
        arrow = Arrow(nerve.get_bottom(), hair.get_end() + UP * 0.2, color=ACC2, buff=0.2)
        self.play_t(FadeIn(nerve, shift=DOWN * 0.2), GrowArrow(arrow), run_time=1.0)
        mech = VGroup(surface, follicle, hair, muscle, mlabel, nerve, arrow)

        # beat 2: twist, feeling vs measured
        self.caption(3)
        self.play_t(FadeOut(mech), run_time=0.4)
        twist = Text("the twist", font_size=56, color=ACC, weight=BOLD).shift(UP * 5)
        left = VGroup(RoundedRectangle(corner_radius=0.3, width=3.6, height=3.0, color=ACC2, fill_opacity=0.12),
                      Text("feeling\nchills", font_size=44, color=INK)).shift(LEFT * 2.1 + UP * 1.8)
        right = VGroup(RoundedRectangle(corner_radius=0.3, width=3.6, height=3.0, color=ACC, fill_opacity=0.12),
                       Text("getting\nbumps", font_size=44, color=INK)).shift(RIGHT * 2.1 + UP * 1.8)
        for c in (left, right):
            c[1].move_to(c[0])
        neq = Text("≠", font_size=110, color="#e63946").move_to(UP * 1.8)
        self.play_t(Write(twist), FadeIn(left, shift=RIGHT), FadeIn(right, shift=LEFT), run_time=1.0)
        self.play_t(GrowFromCenter(neq), run_time=0.5)
        self.caption(4)
        note = Text("reported ≠ measured", font_size=42, color=SOFT).shift(DOWN * 1.2)
        self.play_t(FadeIn(note, shift=UP * 0.2), run_time=0.6)
        twistg = VGroup(twist, left, right, neq, note)

        # beat 3: animals
        self.caption(5)
        self.play_t(FadeOut(twistg), run_time=0.4)
        rows = ["traps warm air", "looks bigger", "quills up"]
        who = ["furry animals", "cats & chimps", "porcupines"]
        cards = VGroup()
        for w, r, col in zip(who, rows, (ACC2, ACC, "#e63946")):
            box = RoundedRectangle(corner_radius=0.3, width=7.4, height=1.6, color=col, fill_opacity=0.12)
            t1 = Text(w, font_size=42, color=INK, weight=BOLD).move_to(box).shift(UP * 0.3)
            t2 = Text(r, font_size=36, color=col).move_to(box).shift(DOWN * 0.35)
            cards.add(VGroup(box, t1, t2))
        cards.arrange(DOWN, buff=0.45).shift(UP * 2)
        self.play_t(FadeIn(cards[0], shift=UP * 0.3), run_time=0.7)
        self.caption(6)
        self.play_t(FadeIn(cards[1], shift=UP * 0.3), run_time=0.7)
        self.caption(7)
        self.play_t(FadeIn(cards[2], shift=UP * 0.3), run_time=0.7)

        # beat 4: on purpose
        self.caption(8)
        self.play_t(FadeOut(cards), run_time=0.4)
        big = Text("on purpose", font_size=84, color=ACC, weight=BOLD).shift(UP * 4)
        skin = self.skin(bumps=0, y=1)
        bumpy = self.skin(bumps=9, y=1)
        sub = Text("no trigger needed", font_size=44, color=SOFT).shift(DOWN * 0.4)
        self.play_t(Write(big), Create(skin), run_time=1.0)
        self.play_t(Transform(skin, bumpy), FadeIn(sub), run_time=0.8)
        self.caption(9)
        notall = Text("not everyone can", font_size=50, color="#e63946", weight=BOLD).shift(DOWN * 2)
        self.play_t(FadeIn(notall, scale=1.2), run_time=0.6)
        purpose = VGroup(big, skin, sub, notall)

        # beat 5: payoff
        self.caption(10)
        self.play_t(FadeOut(purpose), run_time=0.4)
        heart = VGroup(Circle(radius=0.9, color="#e63946", fill_opacity=1).shift(LEFT * 0.62),
                       Circle(radius=0.9, color="#e63946", fill_opacity=1).shift(RIGHT * 0.62),
                       Square(side_length=1.75, color="#e63946", fill_opacity=1).rotate(PI / 4).shift(DOWN * 0.7)
                       ).shift(UP * 3)
        moved = Text("you were moved", font_size=70, color=INK, weight=BOLD).shift(UP * 0.4)
        self.play_t(GrowFromCenter(heart), run_time=0.8)
        self.until(LINES[10]["start"] + 2.6)
        self.play_t(Write(moved), heart.animate.scale(1.12), run_time=1.0)
        self.until(T["duration"] + 0.4)
