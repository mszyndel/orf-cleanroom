#!/usr/bin/env python3
"""Synthetic numerical checks for token_phase_probe.py (#30); no sample files."""
import itertools
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_phase_probe import phase_statistics  # noqa: E402
from suffix_joint_probe import scan_prefix  # noqa: E402


class PhaseTests(unittest.TestCase):
    def test_balanced_controls(self):
        # Each phase gets each symbol exactly once, for every declared modulus.
        period = 840  # lcm(2..8)
        tokens = [(0, suffix) for suffix in (0, 4, 16, 20) for _ in range(period)]
        for result in phase_statistics(tokens)["moduli"]:
            expected = period // result["modulus"]
            self.assertEqual(result["phase_by_symbol_00_01_10_11"],
                             [[expected] * 4 for _ in range(result["modulus"])])
            self.assertEqual(result["plugin_mi_bits"], 0)
            self.assertEqual(result["symbol_entropy_bits"], 2)
            self.assertEqual(result["conditional_symbol_entropy_bits"], 2)

    def test_planted_phase_lock(self):
        tokens = [(0, (0, 4, 16, 20)[i % 4]) for i in range(800)]
        results = {r["modulus"]: r for r in phase_statistics(tokens)["moduli"]}
        self.assertEqual(results[4]["plugin_mi_bits"], 2)
        self.assertEqual(results[2]["plugin_mi_bits"], 1)
        self.assertEqual(results[4]["conditional_symbol_entropy_bits"], 0)

    def test_escape_indices_not_compacted(self):
        result = phase_statistics([(0, 0), (17, 20), (0, 4), (0, 16)])
        self.assertEqual(result["escape_omitted_tokens"], 1)
        self.assertEqual(result["retained_tokens"], 3)
        self.assertEqual(result["moduli"][0]["phase_by_symbol_00_01_10_11"],
                         [[1, 1, 0, 0], [0, 0, 1, 0]])

    def test_entropy_identity_exhaustive(self):
        # A separate empirical entropy oracle builds joint labels and marginals.
        def oracle(values):
            return math.fsum(-(values.count(v) / len(values)) * math.log(values.count(v) / len(values)) / math.log(2) for v in set(values))
        for suffixes in itertools.product((0, 4, 16), repeat=5):
            results = phase_statistics([(0, s) for s in suffixes])
            for r in results["moduli"]:
                m = r["modulus"]
                symbols = [(s >> 4) * 2 + ((s >> 2) & 1) for s in suffixes]
                phases = [i % m for i in range(5)]
                expected = oracle(symbols) + oracle(phases) - oracle(list(zip(phases, symbols)))
                self.assertAlmostEqual(r["plugin_mi_bits"], expected, places=12)
                self.assertAlmostEqual(r["symbol_entropy_bits"] - r["conditional_symbol_entropy_bits"], expected, places=12)

    def test_degenerate_and_validation(self):
        for tokens in ([], [(17, 4), (96, 20)]):
            for r in phase_statistics(tokens)["moduli"]:
                self.assertIsNone(r["plugin_mi_bits"])
                self.assertIsNone(r["symbol_entropy_bits"])
                self.assertIsNone(r["conditional_symbol_entropy_bits"])
        for r in phase_statistics([(0, 20)] * 23)["moduli"]:
            self.assertEqual(r["plugin_mi_bits"], 0)
        for token in ((-1, 0), (True, 0), (0, 32), (0, -1), (0, False)):
            with self.assertRaises(ValueError):
                phase_statistics([token])

    def test_count_accounting(self):
        tokens = [(17 if i % 13 == 0 else i % 3, i % 32) for i in range(100)]
        original = list(tokens)
        result = phase_statistics(tokens)
        self.assertEqual(tokens, original)
        self.assertEqual(result["parsed_tokens"], 100)
        self.assertEqual(result["escape_omitted_tokens"], 8)
        for r in result["moduli"]:
            self.assertEqual(sum(r["phase_counts"]), 92)
            self.assertEqual(sum(r["symbol_counts"]), 92)
            self.assertEqual(sum(map(sum, r["phase_by_symbol_00_01_10_11"])), 92)

    def test_parser_roundtrip_and_truncation(self):
        expected = [(q, s) for q, s in zip((0, 17, 96, 1, 3), (0, 4, 16, 20, 31))]
        bits = "".join("0" * q + "1" + format(s, "05b") for q, s in expected)
        padded = bits + "0" * (-len(bits) % 8)
        payload = int(padded, 2).to_bytes(len(padded) // 8, "big")
        self.assertEqual(scan_prefix(payload), (expected, len(bits)))
        self.assertEqual(scan_prefix(bytes([0x81])), ([(0, 0)], 6))
        self.assertEqual(scan_prefix(bytes(20)), ([], 0))
        self.assertEqual(scan_prefix(bytes([1])), ([], 0))


if __name__ == "__main__":
    unittest.main()
