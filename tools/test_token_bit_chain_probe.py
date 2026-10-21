#!/usr/bin/env python3
"""Independent synthetic checks for #29 item-4 pairwise lag probe."""
import collections
import contextlib
import io
import json
import math
import os
import random
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_bit_chain_probe import BITS, LAGS, measure, tables  # noqa: E402
import token_bit_chain_probe as probe  # noqa: E402
from suffix_joint_probe import BLOCK, REPLICATES, select_blocks  # noqa: E402


def entropy(labels):
    counts = collections.Counter(labels)
    n = len(labels)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


class ChainTests(unittest.TestCase):
    def test_every_ordered_table_and_entropy(self):
        blocks = [[(7 * i + i // 3) % 32 for i in range(31)], [0, 4, 16, 20] * 7]
        results = measure(blocks)
        self.assertEqual(len(results), 20)
        for r in results:
            pairs = []
            for block in blocks:
                lag = r["lag_tokens"]
                pairs.extend(((block[i - lag] >> r["source_bit"]) % 2,
                              (block[i] >> r["target_bit"]) % 2) for i in range(lag, len(block)))
            counter = collections.Counter(pairs)
            expected = [[counter[(a, b)] for b in (0, 1)] for a in (0, 1)]
            self.assertEqual(r["joint_source_rows_target_columns"], expected)
            self.assertEqual(r["pair_count"], len(pairs))
            mi = entropy([a for a, b in pairs]) + entropy([b for a, b in pairs]) - entropy(pairs)
            self.assertAlmostEqual(r["plugin_mi_bits"], mi, places=12)

    def test_direction_and_planted_delayed_copy(self):
        rng = random.Random(8801)
        blocks = []
        for _ in range(8):
            bits = [rng.randrange(2) for _ in range(BLOCK + 1)]
            blocks.append([4 * bits[i + 1] + 16 * bits[i] for i in range(BLOCK)])
        report = {(r["lag_tokens"], r["source_bit"], r["target_bit"]): r for r in measure(blocks)}
        planted = report[(1, 2, 4)]
        self.assertGreater(planted["plugin_mi_bits"], .99)
        self.assertEqual(planted["pearson"], 1)
        self.assertLess(max(planted["permuted_plugin_mi_bits"]), .03)
        self.assertLess(report[(1, 4, 2)]["plugin_mi_bits"], .03)

    def test_no_boundary_or_escape_gap_pairs(self):
        tokens = [(0, 0)] * BLOCK + [(17, 20)] * BLOCK + [(0, 20)] * BLOCK + [(0, 4)] * 3
        blocks, counts = select_blocks(tokens)
        self.assertEqual(counts["escape_omitted_blocks"], 1)
        self.assertEqual(counts["tail_tokens"], 3)
        for (lag, source, target), table in tables(blocks).items():
            self.assertEqual(table, [[BLOCK - lag, 0], [0, BLOCK - lag]])

    def test_permutation_marginals_and_input_unchanged(self):
        blocks = [[0] * BLOCK, [20] * BLOCK]
        original = [list(b) for b in blocks]
        result = measure(blocks)
        self.assertEqual(blocks, original)
        self.assertEqual(result, measure(blocks))
        for r in result:
            self.assertEqual(r["plugin_mi_bits"], 1)
            self.assertEqual(r["permuted_plugin_mi_bits"], [1] * REPLICATES)

    def test_empty_short_and_degenerate(self):
        self.assertEqual(LAGS, (1, 2, 3, 4, 5))
        self.assertEqual(BITS, (2, 4))
        for r in measure([[], [20]]):
            self.assertEqual(r["pair_count"], 0)
            self.assertIsNone(r["plugin_mi_bits"])
            self.assertIsNone(r["pearson"])
            self.assertEqual(r["permuted_plugin_mi_bits"], [None] * REPLICATES)
            self.assertIsNone(r["permuted_mi_mean_bits"])
        for r in measure([[20] * BLOCK]):
            self.assertEqual(r["plugin_mi_bits"], 0)
            self.assertIsNone(r["pearson"])

    def test_cli_retains_success_and_sanitizes_failure(self):
        output = io.StringIO()
        argv = ["probe", "--sample", "1", "public-good", "local-good",
                "--sample", "2", "public-bad", "private-missing-path"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
                probe, "report", side_effect=[{"pixls_id": "1"}, OSError("private-missing-path")]):
            with contextlib.redirect_stdout(output):
                status = probe.main()
        self.assertEqual(status, 1)
        self.assertNotIn("private-missing-path", output.getvalue())
        result = json.loads(output.getvalue())
        self.assertEqual(result["samples"], [{"pixls_id": "1"}])
        self.assertEqual(result["failures"], [{"pixls_id": "2", "error": "OSError"}])


if __name__ == "__main__":
    unittest.main()
