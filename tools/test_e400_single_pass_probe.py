#!/usr/bin/env python3
"""Synthetic inversion, replay, component selection and TIFF-order tests."""
import io
import os
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e400_single_pass_probe import initial_candidates, score_pair, summarize, measure


class SinglePassTests(unittest.TestCase):
    def test_inverse_matches_exhaustive_uint16_domain(self):
        for value in (0, 1, 4, 20, 16383, 32768, 65535):
            for other_sum in (0, 3, 48, 49152, 196605):
                expected = [c for c in range(0, 65536, 16)
                            if (other_sum + c) // 4 == value]
                self.assertEqual(initial_candidates(value, other_sum), expected)

    def test_exact_replay_and_order_direction(self):
        self.assertEqual(score_pair(20, 17, 48, 48), {
            'latest_equation_holds': True, 'initial_candidate_count': 1,
            'replay_matching_candidates': 1, 'compatible': True})
        reverse = score_pair(17, 20, 48, 48)
        self.assertFalse(reverse['compatible'])
        self.assertEqual(reverse['replay_matching_candidates'], 0)
        # A candidate for the earlier equation alone is insufficient.
        fail = score_pair(20, 18, 48, 48)
        self.assertEqual(fail['initial_candidate_count'], 1)
        self.assertFalse(fail['latest_equation_holds'])
        self.assertFalse(fail['compatible'])

    def test_pair_graph_and_global_order(self):
        words = [16] * 121
        words[4 * 11 + 4] = 20
        words[5 * 11 + 5] = 17
        r = summarize(words, 11, 11)
        self.assertEqual(r['component_size_histogram'], {2: 1})
        self.assertEqual(r['tested_pairs'], 1)
        self.assertEqual(r['orders']['increasing_raster']['compatible_pairs'], 1)
        self.assertEqual(r['orders']['decreasing_raster']['compatible_pairs'], 0)

    def test_singleton_and_contradicting_singleton(self):
        words = [16] * 121
        words[4 * 11 + 4] = 20
        words[3 * 11 + 3] = 32
        self.assertEqual(summarize(words, 11, 11)['singleton_matches'], 1)
        words[4 * 11 + 4] = 24
        r = summarize(words, 11, 11)
        self.assertEqual(r['singleton_matches'], 0)
        self.assertFalse(r['orders']['increasing_raster']['all_tested_components_compatible'])
        # Unequal parity uses axial2, not diagonal1.
        words = [16] * 121
        words[4 * 11 + 5] = 20
        words[2 * 11 + 5] = 32
        self.assertEqual(summarize(words, 11, 11)['singleton_matches'], 1)

    def test_edges_large_components_and_empty(self):
        words = [16] * 169
        words[1 * 13 + 1] = 20
        words[2 * 13 + 2] = 20
        for y in (5, 6, 7):
            words[y * 13 + y] = 20
        r = summarize(words, 13, 13)
        self.assertEqual(r['excluded_boundary_components'], 1)
        self.assertEqual(r['excluded_boundary_words'], 2)
        self.assertEqual(r['unsupported_large_components'], 1)
        self.assertEqual(r['unsupported_large_words'], 3)
        self.assertEqual(r['tested_pairs'], 0)
        empty = summarize([16] * 25, 5, 5)
        self.assertEqual(empty['marked_words'], 0)
        self.assertEqual(empty['components'], 0)
        for bad in ([16] * 24, [65536] * 25, [-1] * 25):
            with self.assertRaises(ValueError):
                summarize(bad, 5, 5)

    def test_measure_both_byte_orders_and_reject_strips(self):
        words = [16] * 49
        words[3 * 7 + 3] = 20
        words[2 * 7 + 2] = 32
        for endian, order in [('<', 'little'), ('>', 'big')]:
            raw = struct.pack(endian + '49H', *words)
            class SyntheticTiff:
                e = endian
                def all_ifds(self):
                    return iter([{0x100: [7], 0x101: [7], 0x111: [0], 0x117: [98]}])
            with patch('e400_single_pass_probe.Tiff', return_value=SyntheticTiff()):
                with patch('builtins.open', return_value=io.BytesIO(raw)):
                    r = measure('synthetic')
            self.assertEqual(r['byte_order'], order)
            self.assertEqual(r['singleton_matches'], 1)
            with patch('e400_single_pass_probe.Tiff', return_value=SyntheticTiff()):
                with patch('builtins.open', return_value=io.BytesIO(raw[:-1])):
                    with self.assertRaises(ValueError):
                        measure('synthetic')


if __name__ == '__main__':
    unittest.main()
