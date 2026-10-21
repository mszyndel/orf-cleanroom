#!/usr/bin/env python3
"""Synthetic controls for token_phase_context_probe; stdlib, no file writes."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_phase_context_probe as probe


class PhaseContextTests(unittest.TestCase):
    def test_balanced_xor(self):
        table = [[[0, 0] for _ in range(2)] for _ in range(4)]
        for c in range(4):
            for p in range(2):
                table[c][p][(c & 1) ^ p] = 10
        result = probe.table_statistics(table)
        self.assertEqual(result['plugin_phase_mi_bits'], 0)
        self.assertEqual(result['plugin_conditional_phase_mi_bits'], 1)
        self.assertEqual(result['context_counts'], [20] * 4)

    def test_context_only_and_independent(self):
        table = [[[10 if y == (c & 1) else 0 for y in range(2)]
                  for _ in range(3)] for c in range(4)]
        self.assertEqual(probe.table_statistics(table)['plugin_conditional_phase_mi_bits'], 0)
        table = [[[5, 5] for _ in range(3)] for _ in range(4)]
        self.assertEqual(probe.table_statistics(table)['plugin_conditional_phase_mi_bits'], 0)

    def test_direct_contingency_identity(self):
        table = [[[(c + p) % 5, (2 * c + p + 1) % 7] for p in range(7)] for c in range(4)]
        n = sum(count for stratum in table for row in stratum for count in row)
        expected = 0
        for stratum in table:
            nc = sum(map(sum, stratum))
            for row in stratum:
                for y, count in enumerate(row):
                    if count:
                        ny = sum(pair[y] for pair in stratum)
                        expected += count / n * math.log2(count * nc / (sum(row) * ny))
        self.assertAlmostEqual(probe.table_statistics(table)['plugin_conditional_phase_mi_bits'], expected, places=13)

    def test_selection_absolute_indices_and_context(self):
        tokens = [(0, s) for s in [0, 16, 4, 20, 0, 4, 16, 20]]
        tokens[3] = (17, 20)
        result = probe.phase_context_statistics(tokens)
        self.assertEqual(result['initial_context_unavailable'], 2)
        self.assertEqual(result['escape_omitted_triples'], 3)
        self.assertEqual(result['retained_triples'], 3)
        # Retained absolute targets 2,6,7; contexts 2,0,3 and targets 1,0,1.
        table = result['moduli'][0]['context_by_phase_by_target']
        self.assertEqual(table[2][0][1], 1)
        self.assertEqual(table[0][0][0], 1)
        self.assertEqual(table[3][1][1], 1)
        self.assertEqual(sum(result['moduli'][0]['context_counts']), 3)

    def test_empty_and_short(self):
        for tokens in ([], [(0, 0)], [(0, 0), (0, 0)], [(17, 0)] * 5):
            result = probe.phase_context_statistics(tokens)
            self.assertEqual(result['retained_triples'], 0)
            self.assertTrue(all(x['plugin_conditional_phase_mi_bits'] is None for x in result['moduli']))

    def test_invalid(self):
        for tokens in ([(True, 0)], [(0, 32)], [(-1, 0)], [(0, False)]):
            with self.assertRaises(ValueError):
                probe.phase_context_statistics(tokens)
        for table in ([], [[[1, 2]]] * 3, [[[1, -1]]] * 4):
            with self.assertRaises(ValueError):
                probe.table_statistics(table)


if __name__ == '__main__':
    unittest.main()
