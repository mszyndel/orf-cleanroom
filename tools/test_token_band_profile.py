#!/usr/bin/env python3
"""Synthetic checks for token_band_profile.py (no sample or image data)."""
import contextlib
import io
import json
import math
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_band_profile as P


def packed(qs):
    bits = "".join("0" * q + "1" + "00000" for q in qs)
    bits += "0" * (-len(bits) % 8)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


class Tests(unittest.TestCase):
    def test_scanner_caps_escapes_and_complete_guard(self):
        values = [0, 1, 17, 41, 100, 3]
        actual, end = P.scan_q(packed(values), len(values))
        self.assertEqual(list(actual), [0, 1, 17, 40, 40, 3])
        self.assertEqual(end, sum(q + 6 for q in values))
        # 11 zeros then 1 and only five total remaining bits: incomplete suffix.
        self.assertEqual(P.scan_q(bytes([0, 16]), 9), (P.array.array("B"), 0))

    def test_signed_and_zero_variance(self):
        for qs, sign in [([3, 0, 4, 0, 5, 0], 1), ([0, 3, 0, 4, 0, 5], -1)]:
            out = P.profile(P.array.array("B", qs), 2, 0, 3, 1)
            self.assertAlmostEqual(out["signed_mean_over_se"], sign * 4 * math.sqrt(3))
            self.assertAlmostEqual(out["mean_head_minus_rest"], sign * 4)
        for qs in ([2, 2] * 3, [3, 0] * 3, [0, 3] * 3):
            out = P.profile(P.array.array("B", qs), 2, 0, 3, 1)
            self.assertIsNone(out["signed_mean_over_se"])
            self.assertFalse(out["score_defined"])

    def test_absolute_band_and_incomplete(self):
        qs = P.array.array("B", [9, 0, 8, 0, 1, 0, 2, 0, 3, 0])
        out = P.profile(qs, 2, 2, 4, 1)
        self.assertEqual(out["start_token"], 4)
        self.assertEqual(out["complete_rows"], 3)
        self.assertFalse(out["complete"])
        self.assertEqual(out["mean_head_minus_rest"], 2)
        empty = P.profile(qs, 2, 9, 4, 1)
        self.assertEqual(empty["complete_rows"], 0)
        self.assertIsNone(empty["mean_head_minus_rest"])

    def test_exact_moments_against_float_reference(self):
        qs = P.array.array("B", [((i * 7) ^ (i // 5)) % 41 for i in range(220)])
        out = P.profile(qs, 11, 3, 10, 3)
        ds = [sum(qs[r*11:r*11+3])/3 - sum(qs[r*11+3:(r+1)*11])/8 for r in range(3,13)]
        mean = sum(ds)/10
        var = sum((d-mean)**2 for d in ds)/9
        self.assertAlmostEqual(out["mean_head_minus_rest"], mean)
        self.assertAlmostEqual(out["signed_mean_over_se"], mean/math.sqrt(var/10))
        self.assertEqual(out["escape_tokens"], sum(q>=17 for q in qs[33:143]))

    def test_cli_keeps_all_failures_and_nonzero_exit(self):
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            result = P.main(["--stride", "40", "--sample", "1", "synthetic missing", "0"*64,
                             "missing-synthetic-file.ORF", "--sample", "bad", "invalid", "x", "unused"])
        self.assertEqual(result, 1)
        samples = json.loads(sink.getvalue())["samples"]
        self.assertEqual(len(samples), 2)
        self.assertTrue(all(not x["ok"] for x in samples))
        self.assertNotIn("missing-synthetic-file", sink.getvalue())

    def test_validation(self):
        for args in [(2, 0, 3, 2), (3, -1, 3, 1), (3, 0, 1, 1)]:
            with self.assertRaises(ValueError):
                P.profile(P.array.array("B"), *args)


if __name__ == "__main__":
    unittest.main()
