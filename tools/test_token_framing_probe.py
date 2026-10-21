#!/usr/bin/env python3
"""Synthetic null-preservation, bounded-parser and failure tests for #197."""
from collections import Counter
import contextlib
import io
from itertools import groupby
import json
import os
import random
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_framing_probe as probe


def fixture(endian='<', truncated=False):
    # Tiny original TIFF with four LONG tags and eight payload bytes.
    data = (b'II' if endian == '<' else b'MM') + struct.pack(endian + 'HIH', 42, 8, 4)
    for tag, value in ((256, 8), (257, 1), (273, 62), (279, 8)):
        data += struct.pack(endian + 'HHII', tag, 4, 1, value)
    data += struct.pack(endian + 'I', 0) + b'\x84' * 8
    return data[:-1] if truncated else data


class FramingTests(unittest.TestCase):
    def test_markov_fit_exact_adjacent_counts_without_wraparound(self):
        fit = probe.fit_markov(b'\x39\xc7')  # 0011100111000111
        self.assertEqual(fit['transition_counts'], [[4, 3], [2, 6]])
        self.assertEqual(fit['initial_one_probability'], 9 / 16)
        self.assertEqual(fit['next_one_probabilities'], [3 / 7, 6 / 8])
        self.assertEqual(fit['fallback_states'], [])

    def test_markov_generator_conditions_on_previous_generated_bit(self):
        class Draws:
            def __init__(self):
                self.draws = iter([0.1, 0.2, 0.9, 0.3, 0.1, 0.9, 0.1, 0.9])

            def random(self):
                return next(self.draws)

        fit = {'initial_one_probability': 0.5, 'next_one_probabilities': [0.2, 0.8]}
        self.assertEqual(probe.markov_bytes(1, fit, Draws()), b'\xca')

    def test_markov_distinguishes_equal_density_alternation_and_persistence(self):
        alternating = probe.fit_markov(b'\x55' * 8)
        persistent = probe.fit_markov(b'\x00' * 4 + b'\xff' * 4)
        self.assertEqual(alternating['initial_one_probability'], persistent['initial_one_probability'])
        self.assertEqual(alternating['next_one_probabilities'], [1, 0])
        self.assertEqual(persistent['next_one_probabilities'], [1 / 32, 1])
        self.assertIn(probe.markov_bytes(8, alternating, random.Random(7)), (b'\x55' * 8, b'\xaa' * 8))

    def test_markov_equal_transition_rows_reduce_to_iid(self):
        fit = {'initial_one_probability': 0.3, 'next_one_probabilities': [0.3, 0.3]}
        self.assertEqual(probe.markov_bytes(256, fit, random.Random(7)),
                         probe.bernoulli_bytes(256, 0.3, random.Random(7)))

    def test_markov_degenerate_short_empty_and_length_edges(self):
        for source, state in ((b'\x00', 0), (b'\xff', 1)):
            fit = probe.fit_markov(source)
            self.assertEqual(fit['fallback_states'], [1 - state])
            self.assertEqual(fit['next_one_probabilities'], [state, state])
            self.assertEqual(probe.markov_bytes(3, fit, random.Random(7)), source * 3)
            self.assertEqual(probe.markov_bytes(0, fit, random.Random(7)), b'')
            with self.assertRaises(ValueError):
                probe.markov_bytes(-1, fit, random.Random(7))
        # State 1 is seen only at the final bit; its outgoing row falls back to p.
        self.assertEqual(probe.fit_markov(b'\x01')['next_one_probabilities'], [1 / 7, 1 / 8])
        with self.assertRaises(ValueError):
            probe.fit_markov(b'')

    def test_markov_opt_in_retains_all_legacy_model_results(self):
        source = bytes(range(64))
        default = probe.compare_prefix(source, 7)
        extended = probe.compare_prefix(source, 7, include_markov=True)
        self.assertEqual(set(default['models']), {'real', 'bernoulli', 'byte_shuffle', 'run_shuffle'})
        self.assertNotIn('markov_fit', default)
        self.assertEqual(extended['models'].pop('markov'),
                         probe.parse_stats(probe.markov_bytes(len(source), extended['markov_fit'], random.Random(7))))
        extended.pop('markov_fit')
        self.assertEqual(default, extended)

    def test_markov_cli_option_forwarded(self):
        with patch.object(probe, 'measure', return_value={}) as measure, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(probe.main(['--sample', '1', 'public', 'unused', '--markov']), 0)
        measure.assert_called_once_with('unused', 131072, 20261021, include_markov=True)

    def test_bounded_parser_exact_and_unfinished_tokens(self):
        result = probe.parse_stats(probe.pack_bits([1, 0, 0, 0, 0, 0] * 4))
        self.assertEqual((result['tokens'], result['q0_count'], result['residual_bits']), (4, 4, 0))
        # Last stop has fewer than five following bits: no phantom token.
        result = probe.parse_stats(b'\x01')
        self.assertEqual((result['tokens'], result['consumed_bits'], result['residual_bits']), (0, 0, 8))
        self.assertIsNone(result['q0_fraction'])
        self.assertEqual(probe.parse_stats(b'\x00')['tokens'], 0)

    def test_bernoulli_uses_p_and_one_draw_per_bit(self):
        class Draws:
            def __init__(self):
                self.draws = iter([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])

            def random(self):
                return next(self.draws)

        self.assertEqual(probe.bernoulli_bytes(1, 0.25, Draws()), b'\xe0')
        self.assertEqual(probe.bernoulli_bytes(4, 0, random.Random(1)), bytes(4))
        self.assertEqual(probe.bernoulli_bytes(4, 1, random.Random(1)), b'\xff' * 4)

    def test_comparison_supplies_measured_nonhalf_density(self):
        with patch.object(probe, 'bernoulli_bytes', wraps=probe.bernoulli_bytes) as generate:
            result = probe.compare_prefix(b'\x01' * 64, 7)
        self.assertEqual(generate.call_args.args[:2], (64, 0.125))
        self.assertEqual(result['bernoulli_p'], 0.125)

    def test_run_shuffle_exact_maximal_run_multisets(self):
        # Reported old regression plus mixed lengths, endpoints and degeneracies.
        for source in (b'\x39\xc7', b'\x00\x17\x81\xf0\xff', b'', b'\x00' * 3, b'\xff' * 3):
            original = [(bit, len(list(group))) for bit, group in groupby(probe.bit_list(source))]
            for seed in range(12):
                shuffled = probe.run_shuffle(source, random.Random(seed))
                actual = [(bit, len(list(group))) for bit, group in groupby(probe.bit_list(shuffled))]
                self.assertEqual(Counter(actual), Counter(original))
                self.assertEqual(len(shuffled), len(source))
                self.assertEqual(sum(probe.bit_list(shuffled)), sum(probe.bit_list(source)))
                if original:
                    self.assertEqual((actual[0][0], actual[-1][0]), (original[0][0], original[-1][0]))

    def test_run_preservation_exhaustive_one_byte_inputs(self):
        for byte in range(256):
            source = bytes([byte])
            expected = Counter((bit, len(list(group)))
                               for bit, group in groupby(probe.bit_list(source)))
            for seed in (0, 7, 20261021):
                result = probe.run_shuffle(source, random.Random(seed))
                actual = Counter((bit, len(list(group)))
                                 for bit, group in groupby(probe.bit_list(result)))
                self.assertEqual(expected, actual)

    def test_run_shuffle_changes_order_when_possible(self):
        source = b'\x00\x17\x81\xf0\xff'
        self.assertTrue(any(probe.run_shuffle(source, random.Random(seed)) != source for seed in range(12)))

    def test_byte_shuffle_exact_histogram_and_seeded_rerun(self):
        source = bytes(range(256)) * 2
        result = probe.byte_shuffle(source, random.Random(3))
        self.assertEqual(Counter(result), Counter(source))
        self.assertNotEqual(result, source)
        self.assertEqual(probe.compare_prefix(source, 3), probe.compare_prefix(source, 3))

    def test_container_both_byte_orders_and_invalid_strip(self):
        for endian in ('<', '>'):
            with patch('builtins.open', return_value=io.BytesIO(fixture(endian))):
                result = probe.measure('fixture', 8, 7)
            self.assertEqual((result['width'], result['height'], result['prefix_bytes']), (8, 1, 8))
        with patch('builtins.open', return_value=io.BytesIO(fixture(truncated=True))):
            with self.assertRaises(ValueError):
                probe.measure('fixture', 8, 7)

    def test_cli_mixed_failure_accounting_and_no_paths(self):
        with patch.object(probe, 'measure', side_effect=[{'tokens': 3}, OSError('PRIVATE_PATH')]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = probe.main(['--sample', '1', 'public-one', 'PRIVATE_PATH_ONE',
                                     '--sample', '2', 'public-two', 'PRIVATE_PATH_TWO'])
        result = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual((result['input_count'], result['success_count'], result['failure_count']), (2, 1, 1))
        self.assertFalse(result['complete'])
        self.assertEqual([r['status'] for r in result['samples']], ['ok', 'failed'])
        self.assertNotIn('PRIVATE_PATH', output.getvalue())

    def test_cli_rejects_nonpositive_bytes_before_reading(self):
        for value in ('0', '-1'):
            with patch.object(probe, 'measure') as measure, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as failure:
                    probe.main(['--sample', '1', 'public', 'unused', '--bytes', value])
            self.assertEqual(failure.exception.code, 2)
            measure.assert_not_called()

    def test_empty_prefix_and_partial_byte_rejected(self):
        with self.assertRaises(ValueError):
            probe.compare_prefix(b'', 7)
        with self.assertRaises(ValueError):
            probe.pack_bits([1])


if __name__ == '__main__':
    unittest.main()
