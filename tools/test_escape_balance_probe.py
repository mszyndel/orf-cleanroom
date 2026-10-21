#!/usr/bin/env python3
"""Synthetic tests for #11's first-escape balance split; no sample files."""
import itertools
import os
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import escape_balance_probe as P


class BalanceTests(unittest.TestCase):
    def test_hand_counts(self):
        result = P.measure([(0, 1), (16, 2), (17, 31), (0, 3), (18, 0), (1, 31)])
        self.assertEqual(result["first_escape_token_index_zero_based"], 2)
        self.assertEqual(result["escape_tokens_excluded"], 2)
        self.assertEqual(result["before"]["ones_b4_to_b0"], [0, 0, 0, 1, 1])
        self.assertEqual(result["after"]["ones_b4_to_b0"], [1, 1, 1, 2, 2])
        self.assertEqual(result["after"]["p_one_b4_to_b0"], [.5, .5, .5, 1, 1])

    def test_exhaustive_independent_partition(self):
        alphabet = [(0, 0), (16, 31), (17, 1), (18, 30)]
        for length in range(6):
            for tokens in itertools.product(alphabet, repeat=length):
                indices = [i for i, token in enumerate(tokens) if token[0] >= 17]
                cut = indices[0] if indices else len(tokens)
                expected = [Counter(s for q, s in tokens[:cut] if q < 17),
                            Counter(s for q, s in tokens[cut:] if q < 17)]
                actual = P.measure(tokens)
                self.assertEqual(actual["escape_tokens_excluded"], len(indices))
                for label, counts in zip(("before", "after"), expected):
                    self.assertEqual(actual[label]["suffix_counts_0_to_31"],
                                     [counts[s] for s in range(32)])
                    self.assertEqual(actual[label]["ordinary_tokens"], sum(counts.values()))

    def test_uniform_and_empty(self):
        result = P.measure([(0, s) for s in range(32)])
        self.assertIsNone(result["first_escape_token_index_zero_based"])
        self.assertEqual(result["before"]["p_one_b4_to_b0"], [.5] * 5)
        self.assertEqual(result["after"]["p_one_b4_to_b0"], [None] * 5)
        self.assertEqual(P.measure([(17, 31)])["before"]["ordinary_tokens"], 0)

    def test_incomplete_suffix_and_prefix_limit(self):
        self.assertEqual(P.scan_prefix(bytes([1])), ([], 0))
        self.assertEqual(P.scan_prefix(bytes([0xff, 0xff]), 1), ([(0, 31)], 6))

    def test_string_parser_oracle(self):
        tokens = [(q, (q * 3) % 32) for q in (0, 1, 16, 17, 18, 23, 0)]
        bits = "".join("0" * q + "1" + format(s, "05b") for q, s in tokens)
        padded = bits + "0" * (-len(bits) % 8)
        payload = int(padded, 2).to_bytes(len(padded) // 8, "big")
        self.assertEqual(P.scan_prefix(payload), (tokens, len(bits)))
        self.assertEqual(P.measure(P.scan_prefix(payload)[0]), P.measure(tokens))


if __name__ == "__main__":
    unittest.main()
