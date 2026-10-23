#!/usr/bin/env python3
"""Original synthetic checks for boundary arithmetic and complete scanning."""
import hashlib
import io
import os
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e400_boundary_probe as p


class BoundaryTests(unittest.TestCase):
    def test_coordinate_policies_and_degenerate_axis(self):
        self.assertIsNone(p.coordinate(-1, 5, 'available'))
        self.assertEqual([p.coordinate(i, 5, 'clamp') for i in (-2, -1, 4, 5, 6)], [0, 0, 4, 4, 4])
        self.assertEqual([p.coordinate(i, 5, 'reflect') for i in (-2, -1, 4, 5, 6)], [2, 1, 4, 3, 2])
        for i in range(-20, 21):
            self.assertEqual(p.coordinate(i, 1, 'reflect'), 0)
        with self.assertRaises(ValueError):
            p.coordinate(0, 0, 'reflect')
        with self.assertRaises(ValueError):
            p.coordinate(0, 5, 'unknown')

    def test_corner_multiplicity_and_available_support(self):
        self.assertEqual(p.positions(0, 0, 5, 5, 'diagonal1', 'available'), [(1, 1)])
        self.assertEqual(p.positions(0, 0, 5, 5, 'diagonal1', 'reflect'), [(1, 1)] * 4)
        self.assertEqual(p.positions(0, 0, 5, 5, 'axial2', 'available'), [(2, 0), (0, 2)])
        self.assertEqual(p.positions(0, 0, 1, 1, 'diagonal1', 'available'), [])

    def test_rounding_residual_and_unsupported(self):
        group = p.empty_group()
        p.add(group, 10, 31, 3)
        self.assertEqual(group['sum_minus_count_word_range'], [1, 1])
        self.assertEqual(group['rounding']['floor']['matches'], 1)
        self.assertEqual(group['rounding']['ceiling']['prediction_minus_word_range'], [1, 1])
        p.add(group, 10, 32, 3)
        self.assertEqual(group['rounding']['nearest_half_up']['matches'], 1)
        p.add(group, 10, 0, 0)
        self.assertEqual(group['unsupported_words'], 1)
        self.assertEqual(group['denominator_histogram'], {'3': 2, '0': 1})
        tie = p.empty_group()
        p.add(tie, 10, 21, 2)
        self.assertEqual(tie['rounding']['floor']['matches'], 1)
        self.assertEqual(tie['rounding']['nearest_half_up']['prediction_minus_word_range'], [1, 1])
        self.assertEqual(tie['rounding']['ceiling']['prediction_minus_word_range'], [1, 1])

    def test_complete_scan_both_byte_orders(self):
        words = [16] * 49
        words[10] = 10
        words[24] = 20
        for header, endian, order in [('IIRO', '<', 'le'), ('MMOR', '>', 'be')]:
            data = struct.pack(endian + '49H', *words)
            class SyntheticPayload:
                sig = {'payload_w': 7, 'payload_h': 7, 'size_class': 'packed-16'}
                nbytes, in_file = len(data), True
                def read(self, source, pos, count):
                    source.seek(pos)
                    return source.read(count)
            payload = SyntheticPayload()
            payload.header = header
            with patch.object(p.od, 'Payload', return_value=payload):
                with patch('builtins.open', side_effect=lambda *args: io.BytesIO(data)):
                    result = p.measure('synthetic', hashlib.sha256(data).hexdigest())
            self.assertEqual(result['byte_order'], order)
            self.assertEqual(result['nonzero_low4_words'], 2)
            self.assertEqual(result['boundary_nonzero_low4_words'], 1)
            group = result['by_low4']['10']['axial2']['available']
            self.assertEqual(group['denominator_histogram'], {'3': 1})
            self.assertEqual(group['sum_minus_count_word_range'], [22, 22])

    def test_hash_failure_precedes_parser(self):
        with patch('builtins.open', side_effect=lambda *args: io.BytesIO(b'input')):
            with patch.object(p.od, 'Payload') as parser:
                with self.assertRaises(ValueError):
                    p.measure('synthetic', '0' * 64)
                parser.assert_not_called()


if __name__ == '__main__':
    unittest.main()
