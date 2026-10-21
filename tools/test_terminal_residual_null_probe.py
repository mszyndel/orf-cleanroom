#!/usr/bin/env python3
"""Independent exhaustive-string checks for the finite terminal null (#87)."""
import itertools
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terminal_residual_null_probe import residual_null, scan_window, window_report


def brute(n, p):
    pmf = [0.0] * (n + 1)
    ones_event = 0.0
    for values in itertools.product((0, 1), repeat=n):
        weight = p ** sum(values) * (1-p) ** (n-sum(values))
        # Separate direct index parser, no recurrence or production scanner.
        cursor = 0
        while cursor < n:
            start = cursor
            while cursor < n and values[cursor] == 0:
                cursor += 1
            if cursor == n or cursor + 6 > n:
                cursor = start
                break
            cursor += 6
        tail = values[cursor:]
        pmf[len(tail)] += weight
        if tail and all(tail):
            ones_event += weight
    return pmf, ones_event


class TerminalNullTests(unittest.TestCase):
    def test_exhaustive(self):
        for n in range(13):
            for p in (0.0, 0.25, 0.5, 0.75, 1.0):
                expected, event = brute(n, p)
                got = residual_null(n, p)
                for actual, wanted in zip(got["residual_length_pmf"], expected):
                    self.assertAlmostEqual(actual, wanted, places=13)
                self.assertAlmostEqual(got["nonempty_all_one_probability"], event, places=13)
                self.assertAlmostEqual(got["probability_sum"], 1.0, places=13)

    def test_production_scanner_exhaustive(self):
        for n in range(11):
            for values in itertools.product((0, 1), repeat=n):
                bits = "".join(map(str, values))
                # A complete candidate is the first regex-like 0*1..... span.
                position = 0
                while position < n:
                    end = position
                    while end < n and bits[end] == "0":
                        end += 1
                    end += 6
                    if end > n:
                        break
                    position = end
                got = scan_window(bits)
                self.assertEqual(got["consumed_bits"], position)
                self.assertEqual(got["residual_length"], n-position)
                self.assertEqual(got["nonempty_all_one_residual"],
                                 position < n and set(bits[position:]) == {"1"})

    def test_escape_and_truncation(self):
        got = scan_window("0" * 17 + "1" + "10101" + "111")
        self.assertEqual(got, {"complete_tokens": 1, "candidate_escapes": 1,
                              "consumed_bits": 23, "residual_length": 3,
                              "nonempty_all_one_residual": True})
        self.assertEqual(scan_window("0"*20)["residual_length"], 20)

    def test_probability_validation(self):
        for n, p in ((-1, .5), (True, .5), (1, -1), (1, 1.1), (1, math.nan)):
            with self.assertRaises(ValueError):
                residual_null(n, p)

    def test_long_normalization(self):
        for p in (0, .01, .25, .5, .75, .99, 1):
            got = residual_null(4096, p)
            self.assertAlmostEqual(got["probability_sum"], 1, places=12)
            self.assertTrue(all(v >= 0 for v in got["residual_length_pmf"]))

    def test_window_bounds_and_bits_not_emitted(self):
        report = window_report(bytes([255])*512, 0)
        self.assertEqual(report["one_bits"], 4096)
        self.assertEqual(report["candidate_parse"]["residual_length"], 4)
        self.assertEqual(report["fitted_in_sample_null"]["nonempty_all_one_probability"], 1)
        with self.assertRaises(ValueError):
            window_report(b"", 0)


if __name__ == "__main__":
    unittest.main()
