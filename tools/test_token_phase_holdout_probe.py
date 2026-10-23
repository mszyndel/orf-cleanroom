#!/usr/bin/env python3
"""Synthetic held-out phase and conditional-rotation checks; no real data."""
import contextlib
import io
import json
import os
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_phase_holdout_probe import holdout, moments, main, measure


class HoldoutTests(unittest.TestCase):
    def test_planted_and_test_does_not_select(self):
        qs = [0, 0, 5, 0, 0, 0, 6, 0, 9, 0, 1, 0, 8, 0, 2, 0]
        got = holdout(qs, 4, 0, 4, 1)
        self.assertEqual(got["selected_phase"], 2)
        self.assertEqual(got["train_maximum_mean_phases"], [2])
        # Test has a larger phase-zero maximum; frozen phase remains two.
        self.assertLess(got["test_selected"]["mean_head_minus_rest"], 0)
        self.assertGreater(got["test_phase_zero"]["mean_head_minus_rest"], 0)
        self.assertEqual(got["test_selected"]["sum_contrast_numerator"], -8)

    def test_brute_train_moments_and_rotation_sequence(self):
        qs = [1, 0, 2, 8, 3, 0, 0, 2, 7, 4, 1, 4, 3, 0, 2, 2, 1, 5, 4, 0]
        got = holdout(qs, 5, 0, 4, 2)
        sums, squares = [], []
        for p in range(5):
            aa = []
            for row in (qs[:5], qs[5:10]):
                hs = row[p] + row[(p + 1) % 5]
                aa.append(hs * 3 - (sum(row) - hs) * 2)
            sums.append(sum(aa))
            squares.append(sum(a * a for a in aa))
        self.assertEqual(got["train_sum_contrast_numerator_by_phase"], sums)
        self.assertEqual(got["train_sum_squared_contrast_numerator_by_phase"], squares)
        phase = sums.index(max(sums))
        rng = random.Random(20261021)
        controls = []
        for _ in range(99):
            total = 0
            for row in (qs[10:15], qs[15:20]):
                p = (phase + rng.randrange(5)) % 5
                hs = row[p] + row[(p + 1) % 5]
                total += 5 * hs - 2 * sum(row)
            controls.append(total)
        self.assertEqual(got["rotation_sum_contrast_numerators"], controls)
        observed = got["test_selected"]["sum_contrast_numerator"]
        self.assertEqual(got["rotation_greater_or_equal_count"], sum(c >= observed for c in controls))

    def test_wrap_ties_zero_variance_and_signed(self):
        qs = [5, 0, 0, 4, 6, 0, 0, 3] * 2
        self.assertEqual(holdout(qs, 4, 0, 4, 2)["selected_phase"], 3)
        constant = holdout([7] * 16, 4, 0, 4, 2)
        self.assertEqual(constant["train_maximum_mean_phases"], [0, 1, 2, 3])
        self.assertEqual(constant["selected_phase"], 0)
        self.assertIsNone(constant["test_selected"]["signed_mean_over_se"])
        self.assertEqual(constant["rotation_greater_or_equal_count"], 99)
        self.assertLess(moments([-3, -1], 2)["signed_mean_over_se"], 0)

    def test_band_separation_and_incomplete_rejected(self):
        qs = [40, 17, 40, 17] * 4 + [0, 0, 5, 0] * 4
        got = holdout(qs, 4, 4, 4, 1)
        self.assertEqual(got["selected_phase"], 2)
        self.assertEqual(got["train_escape_tokens"], 0)
        short = holdout(qs[:-1], 4, 4, 4, 1)
        self.assertFalse(short["complete"])
        self.assertNotIn("selected_phase", short)
        for values in [(4, -1, 4, 1), (4, 0, 3, 1), (4, 0, 4, 4)]:
            with self.assertRaises(ValueError):
                holdout([], *values)

    def test_cli_sanitized_failure_and_incomplete_exit(self):
        sample = ["--sample", "1", "public", "0" * 64, "PRIVATE_PATH", "--stride", "4", "--head", "1"]
        for result in (ValueError("PRIVATE_PATH"), dict(token_shortfall=1)):
            out = io.StringIO()
            kwargs = dict(side_effect=result) if isinstance(result, Exception) else dict(return_value=result)
            with patch("token_phase_holdout_probe.measure", **kwargs), contextlib.redirect_stdout(out):
                self.assertEqual(main(sample), 1)
            self.assertNotIn("PRIVATE_PATH", out.getvalue())
            self.assertFalse(json.loads(out.getvalue())["samples"][0]["ok"])

    def test_hash_before_tiff_and_duplicate_ids(self):
        with patch("builtins.open", return_value=io.BytesIO(b"not a sample")), \
                patch("token_phase_holdout_probe.Tiff") as tiff:
            with self.assertRaises(ValueError):
                measure("unused", "0" * 64, 4, [0], 4, 1)
            tiff.assert_not_called()
        sample = ["--sample", "1", "public", "0" * 64, "unused"]
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main(sample + sample + ["--stride", "4", "--head", "1"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
