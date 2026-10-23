#!/usr/bin/env python3
"""Synthetic rounding, subset and residual checks for lead #79's probe."""
import io
import struct
from unittest.mock import patch
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e400_exception_probe import rounded_mean, score_word, measure, add_scores


class NeighbourTests(unittest.TestCase):
    def test_integer_rounding_against_quotient_and_remainder(self):
        for count in range(1, 5):
            for total in range(0, 65536 * count, 37):
                quotient, remainder = divmod(total, count)
                self.assertEqual(rounded_mean(total, count, 'floor'), quotient)
                self.assertEqual(rounded_mean(total, count, 'ceiling'), quotient + (remainder > 0))
                self.assertEqual(rounded_mean(total, count, 'nearest_half_up'),
                                 quotient + (2 * remainder >= count))

    def test_quarter_step_and_clearing_neighbour_fraction(self):
        actual = score_word(20, {'test': [0, 16, 16, 48]})
        self.assertEqual(actual['test_floor_subset4'], 1)
        self.assertEqual(actual['test_four_sum_minus_4word'], 0)
        self.assertTrue(actual['test_cleared_low4_floor'])
        actual = score_word(20, {'test': [0, 16, 19, 48]})
        self.assertEqual(actual['test_floor_subset4'], 1)
        self.assertEqual(actual['test_ceiling_subset4'], 0)
        self.assertEqual(actual['test_nearest_half_up_subset4'], 0)
        self.assertEqual(actual['test_four_sum_minus_4word'], 3)
        self.assertEqual(actual['test_nonzero_nibble_neighbours'], 1)

    def test_subsets_count_combinations_and_do_not_reorder_values(self):
        actual = score_word(20, {'test': [10, 30, 70, 90]})
        self.assertEqual(actual['test_floor_subset2'], 1)
        self.assertEqual(actual['test_floor_subset1'], 0)
        self.assertEqual(actual['test_floor_subset3'], 0)
        self.assertEqual(actual['test_floor_subset4'], 0)
        self.assertEqual(actual['test_four_sum_minus_4word'], 120)
        self.assertEqual(score_word(20, {'test': [20] * 4})['test_floor_subset2'], 6)

    def test_output_size_is_bounded_by_nibble_groups(self):
        groups = {}
        for value in range(4, 1000, 16):
            neighbours = {'axial2': [0, 16, 32, 48]}
            add_scores(groups, '4', score_word(value, neighbours), neighbours)
        self.assertEqual(set(groups), {'4'})
        group = groups['4']
        self.assertEqual(group['words'], 63)
        self.assertEqual(group['full_family_residual_range']['axial2_four_sum_minus_4word'], [-3888, 80])
        self.assertEqual(group['neighbour_low_nibble_histograms']['axial2'], {'0': 252})

    def test_full_scan_edge_exclusion_and_tiff_byte_order(self):
        words = [16] * 49
        words[0] = 10
        words[3 * 7 + 3] = 20
        words[1 * 7 + 3] = 32
        for header, endian, expected_order in [('IIRO', '<', 'le'), ('MMOR', '>', 'be')]:
            data = struct.pack(endian + '49H', *words)
            class SyntheticPayload:
                sig = {'size_class': 'packed-16', 'payload_w': 7, 'payload_h': 7,
                       'sha256': 'synthetic', 'model': 'synthetic'}
                nbytes = len(data)
                in_file = True
                def read(self, source, pos, count):
                    source.seek(pos)
                    return source.read(count)
            payload = SyntheticPayload()
            payload.header = header
            with patch('e400_exception_probe.od.Payload', return_value=payload):
                with patch('builtins.open', return_value=io.BytesIO(data)):
                    result = measure('unused-synthetic-input')
            self.assertEqual(result['byte_order'], expected_order)
            self.assertEqual(result['nonzero_low_nibble_words'], 2)
            self.assertEqual(result['excluded_edge_words'], 1)
            self.assertEqual(result['edge_low_nibble_histogram'], {'10': 1})
            self.assertEqual(result['interior_floor_family_counts'], {'axial2': 1})
            self.assertEqual(result['unmatched_interior_by_low_nibble'], {})
            self.assertEqual(result['by_low_nibble']['4']['words'], 1)


if __name__ == '__main__':
    unittest.main()
