"""Starter scene for a short tutorial video: one worked example of the beat order in references/manim.md.

Copy this file into the active project and edit the copy. It is a silent preview scene, not a finished
lesson: a finished teaching video also needs narration and synchronized captions.

    python lesson_beats.py --check        # checks the model against hand-derived values; needs no Manim
    python check_scene.py                # checks objects in the seven held states; requires Manim
    manim render -ql --fps 30 --save_sections lesson_beats.py SameSamples

Patterns shown: a pure model with no Manim objects in it; hand-derived expected values; one ValueTracker;
objects created once and moved by updaters; updaters removed before a hold; one section per beat.
It uses Text only, so it needs no LaTeX install. Tested with Manim Community 0.22.1.
"""
import math
import sys

R = 2.0           # drawn radius, in scene units
FREQ_A = 1.0      # turns per second; fixed, never tied to the camera
FREQ_B = 11.0
RATE = 10         # photographs per second in the main case
EXTRA_T = 0.05    # the one extra photograph, seconds
OPENING_T = 0.17  # where the opening hold stops; not a photograph time, so A and B are visibly apart


def position(freq, t):
    """Unit-circle position for `freq` turns per second at time `t` seconds."""
    if not (math.isfinite(freq) and math.isfinite(t)):
        raise ValueError("frequency and time must be finite")
    angle = 2 * math.pi * freq * t
    return math.cos(angle), math.sin(angle)


def gap(t):
    """Distance between the two candidates at time t, in radii."""
    return math.dist(position(FREQ_A, t), position(FREQ_B, t))


# Hand-derived, independent of position(): see references/aliasing-certificate.md.
EXPECTED = (
    ("every photograph at 10 per second agrees", lambda: max(gap(n / RATE) for n in range(RATE)), 0.0),
    ("the extra photograph at 0.05 s is 2 radii apart", lambda: gap(EXTRA_T), 2.0),
    ("at 12 per second, t = 1/12 is 1 radius apart", lambda: gap(1 / 12), 1.0),
    ("A at t = 1/12 has x = sqrt(3)/2", lambda: position(FREQ_A, 1 / 12)[0], math.sqrt(3) / 2),
    ("B at t = 1/12 has y = -1/2", lambda: position(FREQ_B, 1 / 12)[1], -0.5),
    ("the opening hold shows A and B apart by 2 sin(0.3 pi) radii", lambda: gap(OPENING_T), 2 * math.sin(0.3 * math.pi)),
)


def check():
    failures = []
    for name, observed, expected in EXPECTED:
        value = observed()
        ok = abs(value - expected) <= 1e-9
        print(f"{'pass' if ok else 'FAIL'}  {name}: expected {expected:.6f}, observed {value:.6f}")
        if not ok:
            failures.append(name)
    return failures


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(1 if check() else 0)
    print(__doc__)
    sys.exit(0)

from manim import (  # noqa: E402  (imported late so --check runs without Manim)
    BLUE, DOWN, LEFT, ORANGE, PURPLE, RIGHT, UP, WHITE, Circle, Create, Dot, FadeIn, FadeOut, LaggedStart, Line, Scene,
    Square, Text, ValueTracker, VGroup, Write, linear,
)

CENTER = LEFT * 3.2
CAPTION_AT = DOWN * 3.2          # captions always go here; nothing else may be placed in this strip
SIDE = RIGHT * 3.0


def at(freq, t):
    x, y = position(freq, t)
    return CENTER + R * (x * RIGHT + y * UP)


class SameSamples(Scene):
    def caption(self, text):
        """Replace the caption line. Kept short enough to read during the hold that follows."""
        new = Text(text, font_size=28).move_to(CAPTION_AT)
        if getattr(self, "_caption", None) is not None:
            self.remove(self._caption)
        self.play(FadeIn(new), run_time=0.4)
        self._caption = new

    def construct(self):
        if check():
            raise ValueError("model disagrees with the hand-derived values; do not render")
        self._caption = None
        t = ValueTracker(0.0)
        circle = Circle(radius=R, color=WHITE).move_to(CENTER)
        dot_a = Dot(at(FREQ_A, 0), color=BLUE, radius=0.10)
        dot_b = Square(0.30, color=ORANGE).move_to(at(FREQ_B, 0))
        spoke_a = Line(CENTER, at(FREQ_A, 0), color=BLUE)
        spoke_b = Line(CENTER, at(FREQ_B, 0), color=ORANGE).set_stroke(opacity=0.6)
        movers = (dot_a, dot_b, spoke_a, spoke_b)

        def follow():
            dot_a.add_updater(lambda m: m.move_to(at(FREQ_A, t.get_value())))
            dot_b.add_updater(lambda m: m.move_to(at(FREQ_B, t.get_value())))
            spoke_a.add_updater(lambda m: m.put_start_and_end_on(CENTER, at(FREQ_A, t.get_value())))
            spoke_b.add_updater(lambda m: m.put_start_and_end_on(CENTER, at(FREQ_B, t.get_value())))

        def release():
            for mob in movers:
                mob.clear_updaters()

        legend = VGroup(
            Text("A: 1 turn per second (dot)", font_size=26, color=BLUE),
            Text("B: 11 turns per second (square)", font_size=26, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(SIDE + UP * 2.2)
        slow_motion = Text("Slow-motion replay", font_size=22).next_to(legend, DOWN, buff=0.3)

        # Beat 1. Object and aim: the case is already moving; one sentence says what will be settled.
        self.next_section("1 object and aim")
        self.add(circle, spoke_a, spoke_b, dot_a, dot_b)
        follow()
        self.play(Write(legend), FadeIn(slow_motion), t.animate.set_value(OPENING_T), run_time=2.5, rate_func=linear)
        release()
        self.caption("Can a camera tell these two motions apart?")
        self.wait(2)

        # Beat 2. Case: one reference state, one condition (the camera) and nothing else changes.
        self.next_section("2 case")
        self.caption("The camera photographs 10 times each second.")
        marks = VGroup()
        for n in range(RATE):
            a = Dot(at(FREQ_A, n / RATE), color=BLUE, radius=0.07)
            b = Square(0.26, color=ORANGE).move_to(at(FREQ_B, n / RATE))
            marks.add(VGroup(b, a))
        self.play(FadeOut(VGroup(*movers)), FadeOut(slow_motion), run_time=0.4)
        self.play(LaggedStart(*(FadeIn(m) for m in marks), lag_ratio=0.6), run_time=3)
        note = Text("Every photograph\nshows A and B in\nthe same place.", font_size=28).move_to(SIDE)
        self.play(FadeIn(note), run_time=0.6)
        self.wait(2.5)

        # Beat 3. Predict: a held frame with the question. The answer is in no caption, label, or frame.
        self.next_section("3 predict")
        self.caption("Pause here. What one extra photograph would settle it?")
        self.wait(4)

        # Beat 4. Reveal and name: the outcome first, then a name for what is on screen.
        self.next_section("4 reveal and name")
        self.caption("One more photograph, halfway between the first two.")
        extra_a = Dot(at(FREQ_A, EXTRA_T), color=BLUE, radius=0.11)
        extra_b = Square(0.34, color=ORANGE).move_to(at(FREQ_B, EXTRA_T))
        across = Line(at(FREQ_A, EXTRA_T), at(FREQ_B, EXTRA_T), color=PURPLE)
        self.play(FadeIn(extra_a), FadeIn(extra_b), run_time=0.8)
        self.play(Create(across), run_time=1.2)
        measured = Text(f"Extra photo at {EXTRA_T:g} s\nA and B are {gap(EXTRA_T):.0f} radii apart.", font_size=28).move_to(SIDE)
        self.remove(note)
        self.play(FadeIn(measured), run_time=0.6)
        self.wait(3)

        # Beat 5. Formal statement beside the unchanged diagram, with its condition.
        self.next_section("5 formal statement")
        self.caption("Why the ten photographs agreed.")
        formal = VGroup(
            Text("B gains 11 − 1 = 10 turns/s.", font_size=25),
            Text("At photo n, the time is n/10 s.", font_size=25),
            Text("Extra turns: 10 × (n/10) = n.", font_size=25),
            Text("Whole turns end at the same point.", font_size=25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(SIDE + DOWN * 0.2)
        self.remove(measured)
        self.play(FadeIn(formal), run_time=0.8)
        self.wait(4)

        # Beat 6. Limit: where the picture stops being a proof.
        self.next_section("6 limit")
        self.caption("This separates these two motions only.")
        limit = Text("Many other motions\nstill fit every dot.", font_size=28).move_to(SIDE)
        self.remove(formal)
        self.play(FadeIn(limit), run_time=0.8)
        self.wait(3)

        # Beat 7. Return: the opening case again, and one task to try away from the video.
        self.next_section("7 return")
        self.play(FadeOut(limit), FadeOut(marks), FadeOut(extra_a), FadeOut(extra_b), FadeOut(across), run_time=0.6)
        changed_camera = Text("Replay shown: t = 0.17 s\nNew camera: 12 photos/s\nFirst photo at t = 0 s", font_size=26).move_to(SIDE)
        self.play(FadeIn(VGroup(*movers)), FadeIn(changed_camera), run_time=0.6)
        self.caption("Which photos in the first second would show the same position?")
        self.wait(4)
