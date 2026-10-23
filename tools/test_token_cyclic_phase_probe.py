#!/usr/bin/env python3
"""Synthetic controls for the cyclic within-row profile; no real data."""
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_cyclic_phase_probe import cyclic_profile
from token_band_profile import profile


class CyclicTests(unittest.TestCase):
    def test_exact_brute_force_and_phase_zero(self):
        qs = [0, 2, 17, 4, 1, 5, 3, 2, 8, 0, 1, 4, 5, 2, 3, 7, 2, 1]
        got = cyclic_profile(qs, 6, 0, 3, 2)
        for p in range(6):
            heads, aa = [], []
            for r in range(3):
                row = qs[r * 6:(r + 1) * 6]
                hs = sum(row[(p + j) % 6] for j in range(2))
                heads.append(hs)
                aa.append(hs * 4 - (sum(row) - hs) * 2)
            self.assertEqual(got["sum_head_q_by_phase"][p], sum(heads))
            self.assertEqual(got["sum_contrast_numerator_by_phase"][p], sum(aa))
            self.assertEqual(got["sum_squared_contrast_numerator_by_phase"][p], sum(x*x for x in aa))
        ref = profile(bytes(qs), 6, 0, 3, 2)
        self.assertEqual(got["sum_contrast_numerator_by_phase"][0], ref["sum_contrast_numerator"])
        self.assertEqual(got["signed_mean_over_se_by_phase"][0], ref["signed_mean_over_se"])
        self.assertEqual(got["escape_tokens"], 1)
        self.assertEqual(sum(got["sum_head_q_by_phase"]), 2 * sum(qs))
        self.assertEqual(sum(got["sum_contrast_numerator_by_phase"]), 0)

    def test_wrap_stays_inside_original_row(self):
        got = cyclic_profile([10, 0, 0, 20, 1, 0, 0, 2], 4, 0, 2, 2)
        self.assertEqual(got["sum_head_q_by_phase"][3], 33)

    def test_rotation_equivariance(self):
        rows = [[1, 0, 2, 0, 4], [2, 0, 3, 0, 7], [3, 0, 4, 0, 9]]
        a = cyclic_profile(sum(rows, []), 5, 0, 3, 2)
        b = cyclic_profile(sum([r[2:] + r[:2] for r in rows], []), 5, 0, 3, 2)
        for key in ("sum_head_q_by_phase", "sum_contrast_numerator_by_phase",
                    "sum_squared_contrast_numerator_by_phase", "signed_mean_over_se_by_phase"):
            self.assertEqual(b[key], a[key][2:] + a[key][:2])

    def test_signed_and_constant(self):
        got = cyclic_profile([3, 0, 0, 4, 0, 0, 5, 0, 0], 3, 0, 3, 1)
        self.assertGreater(got["signed_mean_over_se_by_phase"][0], 0)
        self.assertLess(got["signed_mean_over_se_by_phase"][1], 0)
        constant = cyclic_profile([7] * 12, 4, 0, 3, 2)
        self.assertEqual(constant["signed_mean_over_se_by_phase"], [None] * 4)
        self.assertEqual(constant["mean_head_minus_rest_by_phase"], [0] * 4)
        self.assertEqual(constant["mean_extrema"]["max_phases"], list(range(4)))

    def test_partial_empty_and_validation(self):
        got = cyclic_profile([1] * 11, 4, 1, 3, 2)
        self.assertEqual(got["complete_rows"], 1)
        self.assertFalse(got["complete"])
        empty = cyclic_profile([], 4, 0, 3, 2)
        self.assertEqual(empty["mean_head_minus_rest_by_phase"], [None] * 4)
        self.assertEqual(empty["score_extrema"]["max_phases"], [])
        for values in [(4, 0, 3, 4), (4, -1, 3, 2), (4, 0, 1, 2)]:
            with self.assertRaises(ValueError):
                cyclic_profile([], *values)


if __name__ == "__main__":
    unittest.main()
