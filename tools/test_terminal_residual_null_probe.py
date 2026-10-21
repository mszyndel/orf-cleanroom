#!/usr/bin/env python3
"""Independent exhaustive-string checks for the finite terminal null (#87)."""
import itertools
import contextlib
import io
import json
import math
import os
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from terminal_residual_null_probe import fixed_density_null, main, residual_null, scan_window, window_report


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
    def test_fixed_density_exhaustive(self):
        # Enumerate strings once by length; directly parse and bucket by ones.
        # No production boundary counter, scanner or combinatorial formula.
        for n in range(16):
            counts = [[0, 0, 0] for _ in range(n+1)]
            for values in itertools.product((0, 1), repeat=n):
                position = 0
                while position < n:
                    stop = position
                    while stop < n and values[stop] == 0:
                        stop += 1
                    if stop + 6 > n:
                        break
                    position = stop + 6
                row = counts[sum(values)]
                row[0] += 1
                row[1] += position == n
                row[2] += position < n and all(values[position:])
            for ones, (total, empty, event) in enumerate(counts):
                got = fixed_density_null(n, ones)
                self.assertEqual(got["total_strings"], total)
                self.assertEqual(got["empty_residual_strings"], empty)
                self.assertEqual(got["nonempty_residual_strings"], total-empty)
                self.assertEqual(got["nonempty_all_one_residual_strings"], event)
                self.assertEqual(got["nonempty_probability"], (total-empty)/total)
                self.assertEqual(got["nonempty_all_one_probability"], event/total)
                self.assertEqual(got["all_one_given_nonempty"],
                                 event/(total-empty) if total != empty else None)

    def test_fixed_density_extremes_and_long_rejected_candidate(self):
        for n in (0, 1, 5, 6, 7, 4092, 4096):
            zero = fixed_density_null(n, 0)
            self.assertEqual(zero["total_strings"], 1)
            self.assertEqual(zero["nonempty_residual_strings"], int(n > 0))
            self.assertEqual(zero["nonempty_all_one_residual_strings"], 0)
            one = fixed_density_null(n, n)
            self.assertEqual(one["total_strings"], 1)
            self.assertEqual(one["empty_residual_strings"], int(n % 6 == 0))
            self.assertEqual(one["nonempty_all_one_residual_strings"], int(n % 6 != 0))
        # Only a stop at position 94 gives an exact boundary; every other
        # position leaves residual zeros or a rejected short-suffix candidate.
        self.assertEqual(fixed_density_null(100, 1)["nonempty_residual_strings"], 99)

    def test_fixed_density_validation(self):
        for n, ones in ((-1, 0), (2, -1), (2, 3), (True, 0), (2, True), (2., 1), (2, 1.)):
            with self.assertRaises(ValueError):
                fixed_density_null(n, ones)

    def test_fixed_density_binomial_mixture_matches_iid(self):
        for n in range(25):
            for p in (.25, .5, .75):
                event, nonempty = [], []
                for ones in range(n+1):
                    got = fixed_density_null(n, ones)
                    weight = p**ones * (1-p)**(n-ones)
                    event.append(got["nonempty_all_one_residual_strings"] * weight)
                    nonempty.append(got["nonempty_residual_strings"] * weight)
                iid = residual_null(n, p)
                self.assertAlmostEqual(math.fsum(event), iid["nonempty_all_one_probability"], places=14)
                self.assertAlmostEqual(math.fsum(nonempty), iid["nonempty_probability"], places=14)

    def test_fixed_density_cli_opt_in_and_sanitized_mixed_failure(self):
        # Real TIFF locator and CLI; virtual inputs only, no subprocess or files.
        entries = [(0x100, 100), (0x101, 100), (0x103, 1), (0x111, 74), (0x117, 512)]
        data = b"II" + struct.pack("<HIH", 0x4F52, 8, 5)
        data += b"".join(struct.pack("<HHII", tag, 4, 1, value) for tag, value in entries)
        data += struct.pack("<I", 0) + bytes([255])*512
        real_open = open

        def virtual_open(path, *args, **kwargs):
            if path == "virtual-sample":
                return io.BytesIO(data)
            if path == "missing-private-path":
                raise FileNotFoundError("must not expose missing-private-path")
            return real_open(path, *args, **kwargs)

        def run(options):
            out = io.StringIO()
            with patch("builtins.open", virtual_open), contextlib.redirect_stdout(out):
                code = main(options)
            return code, json.loads(out.getvalue()), out.getvalue()

        args = ["--sample", "1", "Synthetic", "virtual-sample"]
        code, default, _ = run(args)
        self.assertEqual(code, 0)
        code, optional, _ = run(["--fixed-density"] + args)
        self.assertEqual(code, 0)
        for name in ("prefix", "tail"):
            baseline = optional["samples"][0]["windows"][name].pop("fixed_density_null")
            self.assertEqual(baseline["total_strings"], 1)
            self.assertEqual(baseline["nonempty_all_one_residual_strings"], 1)
        self.assertEqual(default, optional)
        code, mixed, raw = run(["--fixed-density"] + args +
                               ["--sample", "2", "Missing", "missing-private-path"])
        self.assertEqual(code, 1)
        self.assertEqual(len(mixed["samples"]), 1)
        self.assertEqual(mixed["errors"], [{"pixls_id": "2", "error_type": "FileNotFoundError"}])
        self.assertNotIn("missing-private-path", raw)

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
