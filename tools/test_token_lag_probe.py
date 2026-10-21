#!/usr/bin/env python3
"""Synthetic tests for lead #29 lag probe; no external inputs or outputs."""
import collections
import math
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_lag_probe as probe


class LagTests(unittest.TestCase):
    def test_independent_pair_enumeration(self):
        blocks = [[(i % 4, (i * 7) % 32) for i in range(128)],
                  [(i % 3, (i * 5) % 32) for i in range(128)]]
        for cell in probe.lag_tables(blocks):
            lag = cell["lag"]
            for name, field in (("q_positive", 0), ("low3", 1)):
                counts = collections.Counter()
                for block in blocks:
                    for j in range(lag, len(block)):
                        a, b = block[j - lag][field], block[j][field]
                        if field == 0:
                            a, b = int(a > 0), int(b > 0)
                        else:
                            a, b = a & 7, b & 7
                        counts[a, b] += 1
                table = cell[name + "_counts"]
                self.assertEqual(sum(counts.values()), 2 * (128 - lag))
                for a in range(len(table)):
                    for b in range(len(table)):
                        self.assertEqual(table[a][b], counts[a, b])
                def entropy(values):
                    total = sum(values)
                    return -sum(c / total * math.log2(c / total) for c in values if c)
                rows, cols = collections.Counter(), collections.Counter()
                for (a, b), count in counts.items():
                    rows[a] += count
                    cols[b] += count
                expected = entropy(rows.values()) + entropy(cols.values()) - entropy(counts.values())
                self.assertAlmostEqual(cell[name + "_mi_bits"], expected, places=12)

    def test_no_cross_block_or_escape_pairs(self):
        tokens = [(0, 0)] * 128 + [(17, 7)] * 128 + [(1, 7)] * 128 + [(18, 4)]
        blocks, counts = probe.select_blocks(tokens)
        self.assertEqual(counts["retained_tokens"], 256)
        self.assertEqual(counts["escape_omitted_blocks"], 1)
        self.assertEqual(counts["tail_tokens"], 1)
        self.assertEqual(counts["tail_escapes"], 1)
        self.assertEqual(counts["parsed_escapes"], 129)
        for cell in probe.measure(blocks):
            self.assertEqual(cell["pairs"], 2 * (128 - cell["lag"]))
            self.assertEqual(cell["q_positive_counts"][0][1], 0)
            self.assertEqual(cell["q_positive_mi_bits"], 1)
            self.assertEqual(cell["q_positive_permuted_mi_bits"], [1] * 16)

    def test_null_permutation_and_input_preservation(self):
        blocks = [[(i % 2, i % 8) for i in range(128)]]
        before = [list(block) for block in blocks]
        first = probe.measure(blocks)
        self.assertEqual(blocks, before)
        self.assertEqual(first, probe.measure(blocks))
        self.assertEqual(first[0]["q_positive_mi_bits"], probe.mutual_information([[0, 64], [63, 0]]))
        self.assertLess(first[0]["q_positive_permuted_mean_bits"], 0.1)

    def test_empty_and_degenerate(self):
        for cell in probe.measure([]):
            self.assertEqual(cell["pairs"], 0)
            self.assertIsNone(cell["q_positive_mi_bits"])
            self.assertIsNone(cell["low3_permuted_mean_bits"])
        for cell in probe.measure([[(0, 0)] * 128]):
            self.assertEqual(cell["q_positive_mi_bits"], 0)
            self.assertEqual(cell["low3_mi_bits"], 0)

    def test_mixed_failure_cli(self):
        with mock.patch.object(sys, "argv", ["probe", "--sample", "1", "a", "a",
                                             "--sample", "2", "b", "b"]):
            with mock.patch.object(probe, "report", side_effect=[{"pixls_id": "1"}, ValueError("private")]):
                with mock.patch("builtins.print") as printer:
                    self.assertEqual(probe.main(), 1)
                    payload = printer.call_args[0][0]
                    self.assertIn('"pixls_id": "1"', payload)
                    self.assertIn('"error": "ValueError"', payload)
                    self.assertNotIn("private", payload)


if __name__ == "__main__":
    unittest.main()
