"""Synthetic checks for token_luma_probe (no sample files)."""

import contextlib
import io
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_luma_probe as p  # noqa: E402


class BoxTests(unittest.TestCase):
    def test_box_mean_clamped(self):
        v = [0, 1, 2, 3, 4, 5, 6, 7]
        out = p.box_mean_rows(v, 2, 4, 3)
        self.assertEqual(list(out), [0.5, 1.0, 2.0, 2.5, 4.5, 5.0, 6.0, 6.5])

    def test_block_mean(self):
        v = [float(i) for i in range(16)]
        out = p.block_mean(v, 4, 4, 2, 2)
        self.assertEqual(out, [[2.5, 4.5], [10.5, 12.5]])

    def test_corr_rows(self):
        a = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        self.assertAlmostEqual(p.corr_rows(a, a), 1.0)
        b = [[3.0, 2.0, 1.0], [6.0, 5.0, 4.0]]
        self.assertAlmostEqual(p.corr_rows(a, b), -1.0)


class MappingTests(unittest.TestCase):
    def test_all_translation_entries_and_escapes(self):
        for value in range(256):
            b2 = int(value < 32 and bool(value & 4))
            b4 = int(value < 32 and bool(value & 16))
            self.assertEqual(p.MAPPINGS["b2"][value], b2)
            self.assertEqual(p.MAPPINGS["b4"][value], b4)
            self.assertEqual(p.MAPPINGS["sum"][value], b2 + b4)
        self.assertEqual(p.MAPPINGS["sum"], p.DENSITY)

    def test_orthogonal_single_bit_grids(self):
        # Each four-column row exhausts the independent b2/b4 bit pairs.
        suffix = bytes([0, 4, 16, 20] * 2)
        target_b2 = [[0, 1, 0, 1]] * 2
        target_b4 = [[0, 0, 1, 1]] * 2
        for own, other, target in (("b2", "b4", target_b2),
                                   ("b4", "b2", target_b4)):
            self.assertAlmostEqual(p.score(suffix, 2, 4, 1, 2, target, own), 1)
            self.assertAlmostEqual(p.score(suffix, 2, 4, 1, 2, target, other), 0)
            self.assertAlmostEqual(p.score(suffix, 2, 4, 1, 2, target, "sum"), 2 ** -0.5)
        self.assertEqual(p.score(suffix, 2, 4, 1, 2, target_b2),
                         p.score(suffix, 2, 4, 1, 2, target_b2, "sum"))

    def test_paired_shuffles_preserve_whole_suffix_rows(self):
        suffix = bytes([0, 4, 16, 20, 32, 0, 4, 20] * 2)
        before = bytes(suffix)
        first = p.shuffle_rows(suffix, 2, 8, random.Random(19))
        second = p.shuffle_rows(suffix, 2, 8, random.Random(19))
        self.assertEqual(first, second)
        self.assertEqual(suffix, before)
        for row in range(2):
            part = slice(row * 8, (row + 1) * 8)
            self.assertEqual(sorted(first[part]), sorted(suffix[part]))
        b2 = first.translate(p.MAPPINGS["b2"])
        b4 = first.translate(p.MAPPINGS["b4"])
        combined = first.translate(p.MAPPINGS["sum"])
        self.assertEqual(list(combined), [a + b for a, b in zip(b2, b4)])

    def test_invalid_cli_map_before_file_read(self):
        old_argv = sys.argv
        sys.argv = ["token_luma_probe.py", "--map", "unknown", "missing.orf"]
        try:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                p.main()
            self.assertEqual(exc.exception.code, 2)
        finally:
            sys.argv = old_argv


class SelfTest(unittest.TestCase):
    def test_builtin(self):
        p.self_test()


if __name__ == "__main__":
    unittest.main()
