#!/usr/bin/env python3
"""Synthetic quantization, precision and TIFF-byte-order tests for #79."""
import io
import os
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e400_high12_probe import compare, summarize, measure


def synthetic_tiff(endian, words, width=5, height=5):
    # Original tiny TIFF fixture: four LONG tags, followed by packed words.
    offset = 8 + 2 + 4 * 12 + 4
    data = (b'II' if endian == '<' else b'MM') + struct.pack(endian + 'HI', 42, 8)
    data += struct.pack(endian + 'H', 4)
    for tag, value in ((256, width), (257, height), (273, offset), (279, len(words) * 2)):
        data += struct.pack(endian + 'HHII', tag, 4, 1, value)
    return data + struct.pack(endian + 'I', 0) + struct.pack(endian + str(len(words)) + 'H', *words)


def synthetic_strips(words, overlap=False, mismatch=False):
    arrays_at = 62
    first_at = 78
    second_at = first_at + 24 + 7
    offsets = (first_at, first_at + 22 if overlap else second_at)
    data = b'II' + struct.pack('<HIH', 42, 8, 4)
    for tag, count, value in ((256, 1, 5), (257, 1, 5),
                              (273, 2, arrays_at),
                              (279, 1 if mismatch else 2, 50 if mismatch else arrays_at + 8)):
        data += struct.pack('<HHII', tag, 4, count, value)
    data += struct.pack('<I', 0) + struct.pack('<4I', *(offsets + (24, 26)))
    data += struct.pack('<12H', *words[:12]) + b'padding' + struct.pack('<13H', *words[12:])
    return data


class High12Tests(unittest.TestCase):
    def test_exact_quarters_and_fractional_neighbour(self):
        quarter = compare(20, [0, 16, 16, 48])
        self.assertTrue(quarter['full_mean_equals_word'])
        self.assertTrue(quarter['high12_neighbours_mean_equals_word'])
        fractional = compare(23, [0, 16, 28, 48])
        self.assertTrue(fractional['full_mean_equals_word'])
        self.assertTrue(fractional['high12_mean_equals_high12'])
        self.assertEqual(fractional['high12_neighbours_mean_minus_word'], -3)

    def test_high12_mean_can_cross_integer_boundary(self):
        result = compare(16, [15, 15, 15, 19])
        self.assertTrue(result['full_mean_equals_word'])
        self.assertFalse(result['high12_mean_equals_high12'])
        self.assertEqual(result['high12_neighbours_mean_minus_word'], -12)

    def test_uint16_extremes_and_loss_histogram(self):
        for value in (0, 16, 65520, 65535):
            self.assertEqual(compare(value, [value] * 4)['full_mean_equals_word'], True)
            self.assertEqual(compare(value, [value] * 4)['high12_mean_equals_high12'], True)
        result = summarize([65535] * 25, 5, 5)
        self.assertEqual(result['changed_by_clearing_low4'], 25)
        self.assertEqual(result['sum_lost_stored_units'], 375)
        self.assertEqual(result['excluded_edge_nonzero_words'], 24)
        self.assertEqual(result['families']['axial2']['tested'], 1)
        self.assertEqual(result['cleared_low4_loss_histogram'], {'15': 25})

    def test_endianness_and_real_container_path(self):
        words = [16] * 25
        words[12] = 20
        words[2] = 32
        for endian, name in (('<', 'little'), ('>', 'big')):
            data = synthetic_tiff(endian, words)
            with patch('builtins.open', return_value=io.BytesIO(data)):
                result = measure('synthetic')
            self.assertEqual(result['byte_order'], name)
            self.assertEqual(result['words'], 25)
            self.assertEqual(result['changed_by_clearing_low4'], 1)
            self.assertEqual(result['families']['axial2']['full_mean_equals_word'], 1)
            self.assertEqual(result['families']['axial2']['high12_neighbours_mean_equals_word'], 1)

    def test_discontiguous_strips_and_invalid_tables(self):
        words = [16] * 25
        words[12] = 20
        words[2] = 32
        with patch('builtins.open', return_value=io.BytesIO(synthetic_strips(words))):
            result = measure('synthetic')
        self.assertEqual(result['words'], 25)
        self.assertEqual(result['families']['axial2']['full_mean_equals_word'], 1)
        for flags in ({'overlap': True}, {'mismatch': True}):
            with patch('builtins.open', return_value=io.BytesIO(synthetic_strips(words, **flags))):
                with self.assertRaises(ValueError):
                    measure('synthetic')

    def test_invalid_shape_and_truncated_payload(self):
        with self.assertRaises(ValueError):
            summarize([0] * 24, 5, 5)
        data = synthetic_tiff('<', [0] * 25)[:-1]
        with patch('builtins.open', return_value=io.BytesIO(data)):
            with self.assertRaises(ValueError):
                measure('synthetic')


if __name__ == '__main__':
    unittest.main()
