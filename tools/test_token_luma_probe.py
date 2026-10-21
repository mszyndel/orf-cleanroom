"""Synthetic checks for token_luma_probe (no sample files)."""

import os
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


class SelfTest(unittest.TestCase):
    def test_builtin(self):
        p.self_test()


if __name__ == "__main__":
    unittest.main()
