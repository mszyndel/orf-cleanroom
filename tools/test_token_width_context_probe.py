#!/usr/bin/env python3
"""Independent table/scoring and selection controls for #29 width contexts."""
import collections
import contextlib
import io
import json
import math
import os
import random
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_width_context_probe as probe


class Tests(unittest.TestCase):
    def test_independent_enumeration(self):
        rng = random.Random(23)
        tokens = [(0, rng.randrange(32)) for _ in range(1600)]
        for index in (1, 150, 255, 256, 450, 1599):
            tokens[index] = (17, tokens[index][1])
        width = 7
        result = probe.measure(tokens, width)
        # Explicitly specified design, independent of production model generator.
        local = [(4, 1), (2, 2), (4, 3), (2, 4), (4, 5)]
        remote = [7, 14, 12, 16]
        specs = [local]
        for shift in (0, 128):
            specs += [local + [(2, lag + shift)] for lag in remote]
            specs += [local + [(2, lag + shift) for lag in remote]]
        required = {0, 1, 2, 3, 4, 5, 7, 12, 14, 16, 135, 140, 142, 144}
        eligible = [i for i in range(144, len(tokens))
                    if all(tokens[i - lag][0] < 17 for lag in required)]
        self.assertEqual(result["selection"]["retained_train_test_targets"],
                         [sum((i // 128) % 2 == s for i in eligible) for s in (0, 1)])
        for row, taps in zip(result["models"], specs):
            counters = [collections.Counter(), collections.Counter()]
            for i in eligible:
                key = "".join(str((tokens[i - lag][1] >> bit) % 2) for bit, lag in taps)
                counters[(i // 128) % 2][(int(key, 2), (tokens[i][1] >> 2) % 2)] += 1
            for split, field in enumerate(("training_counts_context_by_outcome", "test_counts_context_by_outcome")):
                expected = [[counters[split][(c, y)] for y in (0, 1)] for c in range(2 ** len(taps))]
                self.assertEqual(row[field], expected)
            train = row["training_counts_context_by_outcome"]
            test = row["test_counts_context_by_outcome"]
            ntest = sum(map(sum, test))
            loss = sum(test[c][y] * (math.log2(sum(train[c]) + 1) - math.log2(train[c][y] + .5))
                       for c in range(len(train)) for y in (0, 1)) / ntest
            self.assertAlmostEqual(row["heldout_log_loss_bits"], loss, places=12)
        base = result["models"][0]["heldout_log_loss_bits"]
        for row in result["models"]:
            self.assertAlmostEqual(row["gain_vs_local_bits"], base - row["heldout_log_loss_bits"], places=14)

    def test_negative_increment(self):
        rng = random.Random(71)
        result = probe.measure([(0, rng.randrange(32)) for _ in range(1300)], 9)
        self.assertLess(result["models"][5]["gain_vs_local_bits"], 0)

    def test_planted_remote(self):
        rng = random.Random(51)
        tokens = []
        for i in range(9000):
            bit = rng.randrange(2) if i < 14 else ((tokens[i - 14][1] >> 2) & 1) ^ (rng.random() < .1)
            tokens.append((0, (rng.randrange(32) & ~4) | (bit << 2)))
        rows = probe.measure(tokens, 7)["models"]
        self.assertGreater(rows[2]["gain_vs_local_bits"], .25)

    def test_no_bridge_or_compaction(self):
        tokens = [(0, 0)] * 500
        tokens[300] = (17, 0)
        result = probe.measure(tokens, 7)
        omitted = {300 + lag for lag in (0, 1, 2, 3, 4, 5, 7, 12, 14, 16, 135, 140, 142, 144)}
        expected = [sum(i in omitted for i in range(144, 500) if (i // 128) % 2 == s) for s in (0, 1)]
        self.assertEqual(result["selection"]["escape_omitted_train_test_targets"], expected)
        # An intervening escape outside all taps must not remove that target.
        self.assertNotIn(310, omitted)
        self.assertEqual(sum(result["selection"]["retained_train_test_targets"]), 356 - len(omitted))

    def test_empty_unseen_and_validation(self):
        result = probe.measure([], 7)
        self.assertTrue(all(row["gain_vs_local_bits"] is None for row in result["models"]))
        score = probe.score_tables([[0, 0], [2, 0]], [[1, 2], [0, 1]])
        self.assertEqual(score["test_targets_in_unseen_contexts"], 3)
        self.assertAlmostEqual(score["heldout_log_loss_bits"], (3 + math.log2(6)) / 4)
        for tokens, width in (([(0, 32)], 7), ([(-1, 0)], 7), ([], 5), ([], True)):
            with self.assertRaises(ValueError):
                probe.measure(tokens, width)

    def test_cli_failure_accounting(self):
        with mock.patch.object(sys, "argv", ["probe", "--sample", "1", "public", "missing", "--sample", "2", "public", "ok"]), \
                mock.patch.object(probe, "report", side_effect=[OSError("private path"), {"pixls_id": "2", "prefix_shortfall": 0}]), \
                contextlib.redirect_stdout(io.StringIO()) as stream:
            code = probe.main()
        self.assertEqual(code, 1)
        self.assertNotIn("private path", stream.getvalue())
        self.assertIn('"pixls_id": "2"', stream.getvalue())
        with mock.patch.object(sys, "argv", ["probe", "--sample", "01", "n", "p", "--sample", "1", "n", "p"]), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                probe.main()
        self.assertEqual(error.exception.code, 2)

    def test_cli_prefix_shortfall_status(self):
        # A real source-built TIFF with one complete token in a one-byte strip.
        tags = [(256, 7), (257, 1), (273, 62), (279, 1)]
        data = (b'II' + struct.pack('<HIH', 42, 8, len(tags))
                + b''.join(struct.pack('<HHII', tag, 4, 1, value) for tag, value in tags)
                + struct.pack('<I', 0) + bytes([0x80]))
        with mock.patch('builtins.open', return_value=io.BytesIO(data)):
            short = probe.report('1', 'synthetic', 'synthetic')
        self.assertEqual(short['returned_tokens'], 1)
        self.assertEqual(short['prefix_shortfall'], probe.LIMIT - 1)
        complete = dict(short, pixls_id='2', returned_tokens=probe.LIMIT, prefix_shortfall=0)
        for records, expected in (([short], 1), ([complete, short], 1), ([complete], 0)):
            argv = ['probe']
            for row in records:
                argv.extend(['--sample', row['pixls_id'], 'synthetic', 'synthetic'])
            with mock.patch.object(sys, 'argv', argv), \
                    mock.patch.object(probe, 'report', side_effect=records), \
                    contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(probe.main(), expected)
            result = json.loads(stream.getvalue())
            self.assertEqual(result['samples'], records)
            self.assertEqual(result['failures'], [])


if __name__ == "__main__":
    unittest.main()
