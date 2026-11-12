"""Check the printed exercise against exact phases and an independent Cartesian model."""
import cmath
import math
import re
import unittest
from fractions import Fraction
from pathlib import Path


EXERCISES = Path(__file__).resolve().parents[1] / "assets" / "challenges"


class RotationChallengeTests(unittest.TestCase):
    def test_main_key_lists_every_candidate_and_every_camera_option(self):
        question = (EXERCISES / "rotation.md").read_text(encoding="utf-8")
        key = (EXERCISES / "rotation-key.md").read_text(encoding="utf-8")
        cap = int(re.search(r"at most (\d+) turns per second", question)[1])
        period = Fraction(re.search(r"every (1/\d+) s", question)[1])
        step = Fraction(re.search(r"advances by (1/\d+) turn", question)[1])
        rates = []
        for whole_turns in range(math.floor(cap * period) + 1):
            rate = (whole_turns + step) / period
            if rate <= cap:
                rates.append(rate)
        self.assertEqual(rates, [5, 25, 45])
        times = [Fraction(t) for t in re.findall(r"(1/\d+) s", question.split("choose from")[1])]
        self.assertEqual(len(times), 3)
        rows = re.findall(r"^\| (1/\d+) \| ([\d/]+) \| ([\d/]+) \| ([\d/]+) \|$", key, re.M)
        self.assertEqual([Fraction(row[0]) for row in rows], times)
        unique_counts = []
        for row, time in zip(rows, times):
            phases = list(map(Fraction, row[1:]))
            self.assertEqual(phases, [(f * time) % 1 for f in rates])
            unique_counts.append(len(set(phases)))
        self.assertEqual(unique_counts, [1, 2, 3])
        self.assertIn("Only 1/60 s", key)
        slow, fast = map(int, re.search(r"For example, (\d+) and (\d+) turns/s", key).groups())
        self.assertLessEqual(slow, cap)
        self.assertGreater(fast, cap)
        self.assertEqual((fast - slow) * period % 1, 0)
        self.assertEqual((fast - slow) * times[-1] % 1, 0)
        self.assertNotIn("rotation-key", question)

    def test_transfer_changes_the_observable(self):
        question = (EXERCISES / "rotation-transfer.md").read_text(encoding="utf-8")
        key = (EXERCISES / "rotation-transfer-key.md").read_text(encoding="utf-8")
        f1, f2 = map(int, re.search(r"either (\d+) or (\d+) turns per second", question).groups())
        fs = int(re.search(r"at (\d+) samples per second", question)[1])
        self.assertEqual(f1 + f2, fs)
        for n in range(fs):
            z1, z2 = [cmath.exp(2j * math.pi * f * n / fs) for f in (f1, f2)]
            self.assertAlmostEqual(z1.real, z2.real)
            self.assertAlmostEqual(z1.imag, -z2.imag)
            if n == 1:
                self.assertGreater(z1.imag, 0)
                self.assertLess(z2.imag, 0)
        self.assertIn("positive for 6 and negative for 14", key)
        self.assertNotIn("rotation-transfer-key", question)
