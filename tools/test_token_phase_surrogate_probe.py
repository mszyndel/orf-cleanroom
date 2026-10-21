#!/usr/bin/env python3
"""Synthetic controls for the phase-offset diagnostic; stdlib, no writes."""
import math
import os
import random
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_phase_surrogate_probe as probe
import token_phase_context_probe as reference


class PhaseSurrogateTests(unittest.TestCase):
    def test_observed_matches_existing_estimator_and_accounting(self):
        tokens = [(0, (t*t+7*t+t//9) % 32) for t in range(4*128+5)]
        tokens[128+50] = (17, 0)
        tokens[-1] = (18, 0)
        result = probe.measure(tokens)
        old = reference.heldout_statistics(tokens)
        for key in result['selection']:
            self.assertEqual(result['selection'][key], old[key])
        for row, expected in zip(result['moduli'], old['moduli']):
            for key in ('training_context_by_phase_by_target', 'test_context_by_phase_by_target',
                        'context_baseline', 'context_plus_phase', 'gain_vs_context_bits'):
                self.assertEqual(row['observed'][key], expected[key])
            for surrogate in row['surrogates']:
                self.assertEqual(surrogate['context_baseline'], expected['context_baseline'])
                self.assertEqual([sum(h) for h in surrogate['offset_histogram_train_test']], [2, 1])

    def test_shift_tables_against_independent_target_oracle(self):
        blocks = [(i % 2, [(i*128+t, (t+t//3) % 4, (t//2) % 2)
                            for t in range(2, 128)]) for i in range(4)]
        for m in range(2, 9):
            offsets = [i % m for i in (1, 3, 6, 9)]
            result = probe.combine(probe.block_tables(blocks, m), m, offsets)
            counts = Counter((split, c, (t+offset) % m, y)
                             for (split, triples), offset in zip(blocks, offsets)
                             for t, c, y in triples)
            for split, key in enumerate(('training_context_by_phase_by_target', 'test_context_by_phase_by_target')):
                for c in range(4):
                    for p in range(m):
                        for y in range(2):
                            self.assertEqual(result[key][c][p][y], counts[split, c, p, y])
            # Independent event-wise log-loss calculation.
            losses = []
            for split, triples in blocks:
                if split:
                    offset = offsets[blocks.index((split, triples))]
                    for t, c, y in triples:
                        p = (t+offset) % m
                        n0, n1 = counts[0,c,p,0], counts[0,c,p,1]
                        losses.append(-math.log2(((n0,n1)[y]+0.5)/(n0+n1+1)))
            self.assertAlmostEqual(sum(losses)/len(losses), result['context_plus_phase']['heldout_log_loss_bits'], places=12)

    def test_planted_phase_and_context_only(self):
        for context_only in (False, True):
            blocks = [(i % 2, [(t, (t//2) % 4,
                               ((t//2) % 4) & 1 if context_only else t % 2)
                              for t in range(128)]) for i in range(64)]
            tables = probe.block_tables(blocks, 2)
            observed = probe.combine(tables, 2, [0]*64)['gain_vs_context_bits']
            # Exactly balanced shifts in each split erase global parity alignment.
            control = probe.combine(tables, 2, [(i//2) % 2 for i in range(64)])['gain_vs_context_bits']
            if context_only:
                self.assertLess(observed, 0)
                self.assertEqual(observed, control)
            else:
                self.assertGreater(observed, 0.99)
                self.assertEqual(control, 0)  # both models predict exactly one half

    def test_seed_determinism_and_rank_accounting(self):
        tokens = [(0, (t*t+t//3) % 32) for t in range(6*128)]
        a, b = probe.measure(tokens), probe.measure(tokens)
        self.assertEqual(a, b)
        blocks, _ = probe.select_blocks(tokens)
        for row in a['moduli']:
            m = row['modulus']
            self.assertEqual(sum(row['descriptive_rank_counts'].values()), probe.REPLICATES)
            for r, surrogate in enumerate(row['surrogates']):
                rng = random.Random(probe.SEED+r)
                offsets = [rng.randrange(m) for _ in blocks]
                expected = [[offsets[split::2].count(p) for p in range(m)] for split in range(2)]
                self.assertEqual(surrogate['offset_histogram_train_test'], expected)

    def test_empty_no_train_no_test_and_invalid(self):
        for tokens in ([], [(0,0)]*128, [(17,0)]*128+[(0,0)]*128):
            for row in probe.measure(tokens)['moduli']:
                self.assertIsNone(row['descriptive_rank_counts'])
                self.assertIsNone(row['observed']['gain_vs_context_bits'])
                self.assertTrue(all(s['gain_vs_context_bits'] is None for s in row['surrogates']))
        for tokens in ([(True,0)], [(0,32)], [(-1,0)], [(0,False)]):
            with self.assertRaises(ValueError):
                probe.measure(tokens)
        for offsets in ([0], [-1,0], [0,2], [False,0]):
            with self.assertRaises(ValueError):
                probe.combine(probe.block_tables([(0,[]),(1,[])], 2), 2, offsets)


if __name__ == '__main__':
    unittest.main()
