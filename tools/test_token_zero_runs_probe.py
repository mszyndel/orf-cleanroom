#!/usr/bin/env python3
"""Synthetic tests for complete runs, censoring, escapes and exact moments."""
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_zero_runs_probe import measure, scan_window
from suffix_joint_probe import scan_prefix


def tokens(bits):
    return [(0, 4 * int(bit)) for bit in bits]


class RunTests(unittest.TestCase):
    def test_hand_moments(self):
        result = measure(tokens("10010001"))
        self.assertEqual(result["histogram"], [{"length": 2, "count": 1}, {"length": 3, "count": 1}])
        self.assertEqual(result["sum_run_lengths"], 5)
        self.assertEqual(result["sum_squared_run_lengths"], 13)
        self.assertEqual(result["population_mean"], 2.5)
        self.assertEqual(result["population_variance"], 0.25)
        self.assertEqual(result["fitted_positive_geometric_variance"], 3.75)

    def test_censoring(self):
        r = measure(tokens("001001000"))
        self.assertEqual(r["leading_censored_zeros"], 2)
        self.assertEqual(r["trailing_censored_zeros"], 3)
        self.assertEqual(r["sum_run_lengths"], 2)
        self.assertEqual(r["zero_tokens"], 7)

    def test_empty_degenerate(self):
        for bits in ("", "111", "000", "001", "100"):
            r = measure(tokens(bits))
            self.assertEqual(r["complete_positive_runs"], 0)
            self.assertIsNone(r["population_mean"])
            self.assertIsNone(r["population_variance"])
        r = measure(tokens("000"))
        self.assertEqual(r["all_zero_segment_zeros"], 3)
        self.assertEqual(r["leading_censored_zeros"], 0)
        self.assertEqual(r["trailing_censored_zeros"], 0)
        self.assertIsNone(measure(tokens("10101"))["variance_ratio"])

    def test_escape_splits(self):
        r = measure(tokens("10") + [(17, 0), (18, 4)] + tokens("01"))
        self.assertEqual(r["complete_positive_runs"], 0)
        self.assertEqual(r["segments"], 2)
        self.assertEqual(r["omitted_escape_tokens"], 2)
        self.assertEqual(r["trailing_censored_zeros"], 1)
        self.assertEqual(r["leading_censored_zeros"], 1)
        self.assertEqual(measure([(17, 0)])["segments"], 0)

    def test_scanner_end_boundary(self):
        # A late stop without all five suffix bits must contribute no token.
        self.assertEqual(scan_prefix(bytes([1])), ([], 0))
        self.assertEqual(scan_prefix(bytes([0x81])), ([(0, 0)], 6))
        self.assertEqual(measure(scan_prefix(bytes([1]))[0])["retained_tokens"], 0)

    def test_exhaustive_string_oracle(self):
        # Independent oracle: trim at first/last one and split on ones.
        for length in range(10):
            for bits in itertools.product("01", repeat=length):
                text = "".join(bits)
                runs = ([len(s) for s in text[text.find("1"):text.rfind("1")+1].split("1") if s]
                        if "1" in text else [])
                r = measure(tokens(text))
                self.assertEqual(r["complete_positive_runs"], len(runs))
                self.assertEqual(r["sum_run_lengths"], sum(runs))
                self.assertEqual(r["sum_squared_run_lengths"], sum(x*x for x in runs))

    def test_windows_against_independent_encoder(self):
        expected = [(q, (3*q + i) % 32) for i, q in enumerate((0, 1, 17, 7, 96, 2, 18, 0))]
        encoded = ["0"*q + "1" + format(s, "05b") for q, s in expected]
        text = "".join(encoded)
        padded = text + "0"*((-len(text)) % 8)
        payload = int(padded, 2).to_bytes(len(padded)//8, "big")
        for start in range(len(expected)+3):
            for count in (1, 3, 20):
                window, meta = scan_window(payload, start, count)
                end_index = min(start+count, len(expected))
                skipped = min(start, len(expected))
                self.assertEqual(window, expected[start:start+count])
                self.assertEqual(meta["bits_consumed"], sum(map(len, encoded[:end_index])))
                self.assertEqual(meta["window_start_bit"], sum(map(len, encoded[:skipped])))
                self.assertEqual(meta["skipped_tokens"], skipped)
                self.assertEqual(meta["skipped_escape_tokens"], sum(q >= 17 for q, _ in expected[:skipped]))
                self.assertEqual(meta["start_shortfall"], start-skipped)
                self.assertEqual(meta["window_bits_consumed"], sum(map(len, encoded[skipped:end_index])))
        window, meta = scan_window(payload)
        self.assertEqual((window, meta["bits_consumed"]), scan_prefix(payload))

    def test_window_boundaries_are_censored_independently(self):
        # The full run has length five. A window containing its middle cannot
        # inherit either external bounding one, and must not count that run.
        text = "1000001"
        encoded = "".join("1" + format(s, "05b") for _, s in tokens(text))
        payload = int(encoded + "0"*((-len(encoded)) % 8), 2).to_bytes((len(encoded)+7)//8, "big")
        r = measure(scan_window(payload, 2, 3)[0])
        self.assertEqual(r["complete_positive_runs"], 0)
        self.assertEqual(r["all_zero_segment_zeros"], 3)
        self.assertEqual(measure(scan_window(payload, 0, 4)[0])["trailing_censored_zeros"], 3)
        self.assertEqual(measure(scan_window(payload, 3, 4)[0])["leading_censored_zeros"], 3)

    def test_window_truncation_and_validation(self):
        for payload in (b"", bytes([1]), bytes(20), bytes([0x81])):
            baseline, end = scan_prefix(payload)
            for start in (0, 1, 2):
                got, meta = scan_window(payload, start, 3)
                self.assertEqual(got, baseline[start:])
                self.assertEqual(meta["bits_consumed"], end)
        for start, count in ((-1, 1), (0, 0), (0, -1)):
            with self.assertRaises(ValueError):
                scan_window(b"", start, count)


if __name__ == "__main__":
    unittest.main()
