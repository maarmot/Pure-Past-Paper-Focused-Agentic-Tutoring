"""Check the geometric objects selected by the SameSamples scene. Requires Manim Community.

Run `python check_scene.py` from this directory. The check constructs the real scene,
skips intermediate frames and compares its held objects with unit-circle reference points.
Use a rendered preview to assess legibility and transitions.
"""
import math
import tempfile

from manim import Circle, Dot, Line, Square, VGroup, tempconfig

from lesson_beats import SameSamples


def one(items, label):
    if len(items) != 1:
        raise ValueError(f"{label}: expected one object, found {len(items)}")
    return items[0]


def verify_hold(objects, beat):
    orbit = one([m for m in objects if type(m) is Circle], "orbit")
    center, radius = orbit.get_center(), orbit.width / 2

    def check_location(point, turns, label):
        # Both coordinates come from the actual scene object and the drawn orbit.
        observed = ((point[0] - center[0]) / radius, (point[1] - center[1]) / radius)
        angle = math.tau * turns
        expected = (math.cos(angle), math.sin(angle))
        if math.dist(observed, expected) > 1e-6:
            raise ValueError(f"Beat {beat}, {label}: expected {expected}, observed {observed}")

    dots = [m for m in objects if type(m) is Dot]
    squares = [m for m in objects if type(m) is Square]
    if beat in (1, 7):
        # t=17/100 seconds: 1 turn/s has advanced 17/100 turns; 11 turns/s has
        # advanced 187/100 turns, which has the same position as 87/100 turns.
        check_location(one(dots, "moving dot").get_center(), 17 / 100, "moving dot")
        check_location(one(squares, "moving square").get_center(), 87 / 100, "moving square")
        return

    pairs = [m for m in objects if type(m) is VGroup and len(m) == 2
             and {type(child) for child in m} == {Dot, Square}]
    if len(pairs) != 10:
        raise ValueError(f"Beat {beat}: expected ten pairs of sampled positions, found {len(pairs)}")
    regular = set()
    for n, pair in enumerate(pairs):
        for marker in pair:
            regular.add(id(marker))
            # The faster dot gains n whole turns by t=n/10, so both end at n/10 turns.
            check_location(marker.get_center(), n / 10, f"sample {n}, {type(marker).__name__}")
    extras_a = [m for m in dots if id(m) not in regular]
    extras_b = [m for m in squares if id(m) not in regular]
    if beat in (2, 3):
        if extras_a or extras_b:
            raise ValueError(f"Beat {beat}: extra photograph revealed before the prediction")
        return

    # t=1/20: 1/20 and 11/20 turns differ by half of a complete turn.
    check_location(one(extras_a, "extra dot").get_center(), 1 / 20, "extra photograph A")
    check_location(one(extras_b, "extra square").get_center(), 11 / 20, "extra photograph B")
    chord = one([m for m in objects if type(m) is Line], "separation line")
    check_location(chord.get_start(), 1 / 20, "separation line start")
    check_location(chord.get_end(), 11 / 20, "separation line end")


class InspectedScene(SameSamples):
    def construct(self):
        self.beats_checked = 0
        super().construct()
        if self.beats_checked != 7:
            raise ValueError(f"Expected seven held beats, inspected {self.beats_checked}")

    def wait(self, *args, **kwargs):
        super().wait(*args, **kwargs)
        self.beats_checked += 1
        verify_hold(self.get_mobject_family_members(), self.beats_checked)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as scratch, tempconfig({
        "dry_run": True, "disable_caching": True, "media_dir": scratch,
        "progress_bar": "none", "verbosity": "ERROR",
    }):
        InspectedScene(skip_animations=True).render()
    print("All seven held states match the independent geometric references.")
