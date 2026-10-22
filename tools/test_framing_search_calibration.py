#!/usr/bin/env python3
"""Independent synthetic checks for #297; stdlib, no writes."""
from collections import Counter
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import framing_search_calibration as probe


class CalibrationTests(unittest.TestCase):
    def test_forced_byte_bit_survives_both_nulls(self):
        _, data = probe.development_cases()[1]
        for model in ('global_byte', 'local_byte'):
            transformed = probe.surrogate(data, model, random.Random(9))
            rows = probe.search(transformed, (8,), ((0, 2048), (2048, 4096)))
            for row in rows:
                if row['phase'] == 7:
                    self.assertEqual(row['ones'], row['positions'])
                    self.assertGreater(row['score'], 100)

    def test_pearson_against_cell_formula(self):
        data = bytes([18, 36, 219, 128, 255, 7, 96])
        bits = [int(c) for byte in data for c in format(byte, '08b')]
        for row in probe.search(data, (2, 3, 8), ((3, 53),)):
            seq = bits[3:53]
            picked = [v for i, v in enumerate(seq) if i % row['width'] == row['phase']]
            a, m, n, t = sum(picked), len(picked), len(seq), sum(seq)
            cells = ((a, m*t/n), (m-a, m*(n-t)/n),
                     (t-a, (n-m)*t/n), (n-m-t+a, (n-m)*(n-t)/n))
            expected = sum((o-e)**2/e for o, e in cells if e)
            self.assertAlmostEqual(row['score'], expected, places=12)
            self.assertEqual((row['positions'], row['ones']), (m, a))

    def test_invariants_and_determinism(self):
        data = bytes(range(70)) + bytes([0, 0, 255])
        for model in ('global_byte', 'local_byte'):
            result = probe.surrogate(data, model, random.Random(7))
            self.assertEqual(Counter(data), Counter(result))
            self.assertEqual(result, probe.surrogate(data, model, random.Random(7)))
            if model == 'local_byte':
                for start in range(0, len(data), 32):
                    self.assertEqual(Counter(data[start:start+32]), Counter(result[start:start+32]))

    def test_entire_search_repeated_and_winners_can_move(self):
        data = bytes(range(32))
        widths, windows = (2, 3, 7), ((0, 128), (128, 256))
        report = probe.calibrate(data, 7, widths, windows)
        self.assertEqual(report['candidate_count'], 24)
        for model in report['models']:
            for row in model['replicate_maxima']:
                transformed = probe.surrogate(data, model['model'], random.Random(probe.SEED+row['replicate']))
                # Independent event-wise oracle scans every window, width and phase.
                values = []
                for start, stop in windows:
                    bits = [(transformed[i//8] >> (7-i % 8)) & 1 for i in range(start, stop)]
                    n, t = len(bits), sum(bits)
                    for w in widths:
                        for p in range(w):
                            picked = [v for i, v in enumerate(bits) if i % w == p]
                            a, m = sum(picked), len(picked)
                            cells = ((a, m*t/n), (m-a, m*(n-t)/n),
                                     (t-a, (n-m)*t/n), (n-m-t+a, (n-m)*(n-t)/n))
                            values.append(sum((o-e)**2/e for o, e in cells if e))
                self.assertAlmostEqual(row['maximum'], max(values), places=10)
                self.assertEqual(row['candidates_evaluated'], 24)
            self.assertGreater(len({r['winner_index'] for r in model['replicate_maxima']}), 1)
            e = sum(r['maximum'] >= report['observed_maximum'] for r in model['replicate_maxima'])
            self.assertEqual(model['exceedances_ge'], e)
            self.assertEqual(model['plus_one_rank_diagnostic'], (e+1)/8)

    def test_constant_ties_and_finite_tail_uncertainty(self):
        report = probe.calibrate(bytes(8), 3, (2, 3), ((0, 64),))
        self.assertEqual(report['observed_winner_index'], 0)
        for model in report['models']:
            self.assertEqual(model['exceedances_ge'], 3)
            self.assertEqual(model['plus_one_rank_diagnostic'], 1)
        low, high = probe.wilson(0, 127)
        self.assertAlmostEqual(low, 0, places=15)
        self.assertGreater(high, 0.02)
        self.assertAlmostEqual(high, 1-probe.wilson(127, 127)[0], places=14)

    def test_invalid_and_accounting(self):
        with self.assertRaises(ValueError):
            probe.calibrate(b'', 0)
        with self.assertRaises(ValueError):
            probe.search(b'', (2,), ((0, 1),))
        with self.assertRaises(ValueError):
            probe.search(bytes(4), (True,), ((0, 8),))
        with self.assertRaises(ValueError):
            probe.surrogate(b'abc', 'unknown', random.Random(0))
        for _, data in probe.development_cases():
            rows = probe.search(data)
            self.assertEqual(len(rows), 154)
            for start, stop in probe.WINDOWS:
                for width in probe.WIDTHS:
                    subset = [r for r in rows if r['width'] == width and r['window_bits'] == [start, stop]]
                    self.assertEqual(sum(r['positions'] for r in subset), stop-start)
                    self.assertEqual(sum(r['ones'] for r in subset), subset[0]['window_ones'])


if __name__ == '__main__':
    unittest.main()
