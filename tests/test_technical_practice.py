"""Independent exact oracles for the published exercises and their printed answers."""
import itertools
import re
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

PACK = Path(__file__).resolve().parents[1] / "assets" / "challenges" / "technical-practice"


def read(topic, name):
    return (PACK / topic / (name + ".md")).read_text(encoding="utf-8")


def value(key, label):
    """Read one numeric result from an examiner's answer table."""
    pattern = rf"^\| {re.escape(label)} \| ([0-9./-]+) \|$"
    return F(re.search(pattern, key, re.MULTILINE)[1])


def distance_cost(dock, station_calls, length=4, station=1):
    """Exact Simpson integration of x*abs(x-dock) on its quadratic pieces."""
    def f(x):
        return x * abs(x - dock)

    continuous = F(0)
    for left, right in ((0, dock), (dock, length)):
        middle = F(left + right, 2)
        continuous += F(right - left, 6) * (f(left) + 4 * f(middle) + f(right))
    return continuous + station_calls * abs(dock - station)


def stream_trace(source, ready_bits, drop_replacement=False):
    waiting = list(source)
    queue = []
    rows = []
    delivered_frames = 0
    level_count = 0
    for edge, ready in enumerate(ready_bits, 1):
        head = queue[0] if queue else "-"
        pop = bool(queue and ready)
        accept = bool(waiting) and (not queue or pop)
        offered = waiting.pop(0) if accept else "-"
        delivered = queue.pop(0) if pop else "-"
        if accept and not (pop and drop_replacement):
            queue.append(offered)
        delivered_frames += delivered.endswith("*")
        level_count += head.endswith("*")
        rows.append((edge, offered, delivered, queue[0] if queue else "-",
                     delivered_frames, level_count))
    return rows


def possible_corners(views, focal, error):
    """Intersect original pixel bounds in (X,Z), without computing disparities."""
    # Each observation bounds X between two lines, X = b + slope * Z.
    lines = [(b, (column + sign * error) / focal)
             for b, column in views for sign in (-1, 1)]
    corners = set()
    for (b1, s1), (b2, s2) in itertools.combinations(lines, 2):
        if s1 == s2:
            continue
        z = (b2 - b1) / (s1 - s2)
        if z <= 0:
            continue
        x = b1 + s1 * z
        if all(abs(focal * (x - b) / z - column) <= error for b, column in views):
            corners.add((x, z))
    return corners


def depth_interval(views, focal, error):
    depths = [z for x, z in possible_corners(views, focal, error)]
    return min(depths), max(depths)


class TechnicalPracticeTests(unittest.TestCase):
    def test_rail_global_and_absolute_cost(self):
        prompt = read("rail-dock", "problem")
        self.assertIn("integral of \x60x dx\x60", prompt)
        self.assertIn("4 m rail", prompt)
        self.assertIn("four calls per shift", prompt)
        self.assertIn("station at coordinate 1", prompt)
        key = read("rail-dock", "key")
        dock = value(key, "Best dock (m)")
        best = distance_cost(dock, 4)
        self.assertEqual(value(key, "Least travel (m/shift)"), best)
        self.assertNotEqual(value(key, "Least travel (m/shift)"), 2 * best)
        for pos in (0, 1, 4):
            self.assertEqual(value(key, f"Travel at {pos} m (m/shift)"), distance_cost(pos, 4))
        total = F(4**2, 2) + 4
        left = F(dock**2, 2) + (4 if dock > 1 else 0)
        right = F(4**2 - dock**2, 2) + (4 if dock < 1 else 0)
        self.assertTrue(0 <= dock <= 4 and max(left, right) <= total / 2)
        for p in range(65):
            s = F(p, 16)
            if s != dock:
                self.assertGreater(distance_cost(s, 4), best)

    def test_station_threshold(self):
        key = read("rail-dock", "key")
        threshold = value(key, "Smallest station load (calls/shift)")
        left, right = F(1, 2), F(15, 2)
        self.assertEqual(left + threshold, right)
        # A very close neighbor to the right beats the dock below threshold.
        step = F(1, 100)
        station = F(1)
        self.assertLess(distance_cost(station + step, threshold - 1),
                        distance_cost(station, threshold - 1))
        for load in (threshold, threshold + 1):
            for neighbor in (station - step, station + step):
                self.assertGreater(distance_cost(neighbor, load), distance_cost(station, load))

    def test_changed_rail_objective(self):
        prompt = read("rail-dock", "transfer")
        self.assertIn("2 m/s, rightward travel at 1 m/s", prompt)
        self.assertIn("[0, 2] m and [3.5, 4] m", prompt)
        key = read("rail-dock", "transfer-key")
        def worst(s):
            return max(s / 2, 4 - s)
        ideal = value(key, "Unrestricted dock (m)")
        self.assertEqual(ideal / 2, 4 - ideal)
        options = [F(i, 60) for i in range(241) if i <= 120 or i >= 210]
        chosen = value(key, "Legal dock (m)")
        self.assertEqual([p for p in options if worst(p) == min(map(worst, options))], [chosen])
        self.assertEqual(value(key, "Worst time at legal dock (s)"), worst(chosen))
        nearest = min(options, key=lambda p: abs(p - ideal))
        self.assertGreater(worst(nearest), worst(chosen))

    def test_register_trace_and_faults(self):
        prompt = read("stream-register", "problem")
        source = re.search(r"^Source order: (.+)$", prompt, re.M)[1].split()
        ready = list(map(int, re.search(r"^Sink ready: +(.+)$", prompt, re.M)[1].split()))
        intended = stream_trace(source, ready)
        key = read("stream-register", "key")
        trace = re.findall(r"^\| (\d+) \| ([-A-E*]+) \| ([-A-E*]+) \| ([-A-E*]+) \| (\d+) \|$",
                           key, re.M)
        printed = [(int(k), a, d, q, int(frames)) for k, a, d, q, frames in trace]
        self.assertEqual(printed, [row[:5] for row in intended])
        accepted = []
        delivered = []
        for _, a, d, q, _ in printed:
            if a != "-":
                accepted.append(a)
            if d != "-":
                delivered.append(d)
            self.assertEqual(accepted, delivered + ([] if q == "-" else [q]))
        broken = stream_trace(source, ready, drop_replacement=True)
        divergence = next(a[0] for a, b in zip(intended, broken) if a[3] != b[3])
        self.assertEqual(value(key, "First storage error (edge)"), divergence)
        first_bad_count = next(row[0] for row in intended if row[4] != row[5])
        self.assertEqual(value(key, "First counter error (edge)"), first_bad_count)
        self.assertEqual(value(key, "Faulty final count (frames)"), intended[-1][5])
        self.assertNotEqual(intended[-1][4], intended[-1][5])

    def test_software_wrap_bound(self):
        prompt = read("stream-register", "transfer")
        period = int(re.search(r"wraps modulo (\d+)", prompt)[1])
        edges = int(re.search(r"exactly (\d+) potentially", prompt)[1])
        start, end = map(int, re.search(r"read (\d+) and then (\d+)", prompt).groups())
        mhz = int(re.search(r"At (\d+) MHz", prompt)[1])
        key = read("stream-register", "transfer-key")
        counts = [n for n in range(edges + 1) if (start + n) % period == end]
        self.assertEqual(counts, [value(key, "Smaller feasible count"), value(key, "Larger feasible count")])
        bound = int(value(key, "Largest universally safe gap (edges)"))
        for old in range(period):
            snapshots = [(old + n) % period for n in range(bound + 2)]
            self.assertEqual(len(set(snapshots[:-1])), bound + 1)
            self.assertLess(len(set(snapshots)), len(snapshots))
        self.assertEqual(value(key, "Largest aligned gap (microseconds)"), F(bound, mhz))
        width = value(key, "Minimum width for ten edges (bits)")
        self.assertEqual(width, min(k for k in range(1, edges + 1) if 2**k > edges))

    def test_two_camera_geometry(self):
        prompt = read("stereo-depth", "problem")
        rows = re.findall(r"^\| (?:Left|Right) \| ([\d.]+) \| (\d+) \| (\d+) \|$", prompt, re.M)
        self.assertEqual(len(rows), 2)
        views = [(F(b), F(u) - F(c)) for b, c, u in rows]
        focal = F(re.search(r"focal length (\d+) pixels", prompt)[1])
        error = F(re.search(r"within ([\d.]+) px", prompt)[1])
        key = read("stereo-depth", "key")
        lo, hi = depth_interval(views, focal, error)
        self.assertEqual((value(key, "Minimum depth (m)"), value(key, "Maximum depth (m)")), (lo, hi))
        center = value(key, "Nominal depth (m)")
        self.assertEqual(depth_interval(views, focal, F(0)), (center, center))
        self.assertTrue(lo < 5 < hi)
        for label, z in (("Near", lo), ("Far", hi)):
            x = value(key, f"{label} witness X (m)")
            self.assertTrue(all(abs(focal * (x - b) / z - u) <= error for b, u in views))
        raw = F(rows[0][2]) - F(rows[1][2])
        self.assertFalse(lo <= focal * views[1][0] / raw <= hi)
        floor = value(key, "Minimum depth for 1 px report (m)")
        # Report centered at (1,0). With these chosen true columns, both errors
        # stay within half a pixel even for depths with no finite upper bound.
        for factor in (1, 10, 100, 10**6):
            z = factor * floor
            x = views[1][0] / 2 + F(1, 2) * z / focal
            for b, u in ((F(0), F(1)), (views[1][0], F(0))):
                self.assertLessEqual(abs(focal * (x - b) / z - u), error)
        self.assertEqual(focal * views[1][0] / floor, 2)

    def test_three_camera_compatibility(self):
        prompt = read("stereo-depth", "transfer")
        rows = re.findall(r"^\| ([\d.]+) \| ([\d.]+) \|$", prompt, re.M)
        views = [(F(b), F(u)) for b, u in rows]
        self.assertEqual(len(views), 3)
        focal = F(re.search(r"focal length is (\d+) px", prompt)[1])
        error = F(re.search(r"within ([\d.]+) px", prompt)[1])
        key = read("stereo-depth", "transfer-key")
        lo, hi = depth_interval(views, focal, error)
        self.assertEqual((value(key, "Minimum joint depth (m)"), value(key, "Maximum joint depth (m)")), (lo, hi))
        for label, z in (("Near", lo), ("Far", hi)):
            x = value(key, f"{label} witness X (m)")
            self.assertIn((x, z), possible_corners(views, focal, error))
        pair_bounds = [depth_interval([views[0], v], focal, error) for v in views[1:]]
        pair_lo = max(p[0] for p in pair_bounds)
        pair_hi = min(p[1] for p in pair_bounds)
        self.assertEqual((value(key, "Two-pair lower bound (m)"), value(key, "Two-pair upper bound (m)")),
                         (pair_lo, pair_hi))
        self.assertLess(pair_lo, lo)
        changed = F(re.search(r"third report changes to ([\d.]+) px", prompt)[1])
        self.assertEqual(possible_corners(views[:2] + [(views[2][0], changed)], focal, error), set())

    def test_learner_files_keep_examiner_material_separate(self):
        for topic in ("rail-dock", "stream-register", "stereo-depth"):
            for filename in ("problem", "transfer"):
                body = read(topic, filename)
                self.assertIn("original generated", body.lower())
                self.assertNotRegex(body.lower(), r"key\.md|## (solution|answer|rubric)")
            for heading in ("## Graduated hints", "## Oral follow-ups", "## Partial credit",
                            "## Interpreting an attempt"):
                self.assertIn(heading, read(topic, "key"))


class PrintedKeyMutationTests(unittest.TestCase):
    def test_checks_reject_three_faulty_printed_keys(self):
        # Exercise the same checks against in-memory copies of the public files.
        cases = (
            ("rail-dock", "key", "| Least travel (m/shift) | 12 |",
             "| Least travel (m/shift) | 24 |", "test_rail_global_and_absolute_cost"),
            ("stream-register", "key", "| 2 | B* | A | B* | 0 |",
             "| 2 | B* | A | - | 0 |", "test_register_trace_and_faults"),
            ("stereo-depth", "transfer-key", "| Minimum joint depth (m) | 72/13 |",
             "| Minimum joint depth (m) | 36/7 |", "test_three_camera_compatibility"),
        )
        real_read = read
        for topic, filename, original, altered, method in cases:
            with self.subTest(topic=topic):
                key = real_read(topic, filename)
                self.assertEqual(key.count(original), 1)

                def read_mutation(requested_topic, requested_filename):
                    if (requested_topic, requested_filename) == (topic, filename):
                        return key.replace(original, altered)
                    return real_read(requested_topic, requested_filename)

                with patch(__name__ + ".read", side_effect=read_mutation):
                    with self.assertRaises(AssertionError):
                        getattr(TechnicalPracticeTests(), method)()
