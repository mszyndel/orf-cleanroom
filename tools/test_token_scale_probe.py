#!/usr/bin/env python3
"""Independent synthetic checks for token_scale_probe; stdlib, no sample files."""
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
import token_scale_probe as probe


class ScaleTests(unittest.TestCase):
    def test_independent_tables_and_loss(self):
        rng = random.Random(83)
        blocks = [(index, [rng.randrange(2) for _ in range(29)]) for index in (0, 3, 4, 9)]
        scores = probe.fitted_scores(blocks)
        for result in scores:
            counts = [collections.Counter(), collections.Counter()]
            window = result["window"]
            for index, bits in blocks:
                text = "".join(map(str, bits))
                for t in range(16, len(text)):
                    key = text[t-window:t].count("1") if window else 0
                    if result["joint_lag1"]:
                        key += int(text[t-1]) * (window + 1)
                    counts[index % 2][key, int(text[t])] += 1
            for label, counter in zip(("train", "test"), counts):
                actual = result[label + "_context_by_target"]
                self.assertEqual(actual, [[counter[c, y] for y in range(2)] for c in range(len(actual))])
            expected = 0
            for (context, y), n in counts[1].items():
                total = sum(counts[0][context, other] for other in (0, 1))
                expected += n * (math.log2(total + 1) - math.log2(counts[0][context, y] + .5))
            expected /= sum(counts[1].values())
            self.assertAlmostEqual(result["loss_bits"], expected, places=13)
            self.assertEqual(result["train_targets"], 26)
            self.assertEqual(result["test_targets"], 26)
            self.assertAlmostEqual(result["gain_vs_frequency_bits"], scores[0]["loss_bits"] - expected, places=13)
            self.assertAlmostEqual(result["gain_vs_lag1_bits"], scores[1]["loss_bits"] - expected, places=13)

    def test_selection_preserves_split_and_censors_boundaries(self):
        tokens = [(0, 0)] * (4 * probe.BLOCK + 7)
        tokens[probe.BLOCK] = (17, 0)
        tokens[-1] = (19, 0)
        blocks, counts = probe.select_blocks(tokens)
        self.assertEqual([index for index, _ in blocks], [0, 2, 3])
        self.assertEqual(counts["train_blocks"], 2)
        self.assertEqual(counts["test_blocks"], 1)
        self.assertEqual(counts["escape_omitted_test_blocks"], 1)
        self.assertEqual(counts["tail_tokens"], 7)
        self.assertEqual(counts["tail_escapes"], 1)
        self.assertEqual(counts["parsed_escapes"], 2)
        for model in probe.fitted_scores(blocks):
            self.assertEqual(model["train_targets"], 224)
            self.assertEqual(model["test_targets"], 112)

    def test_long_count_helps_slow_mixture(self):
        rng = random.Random(195)
        blocks = []
        for index in range(1024):
            p = .12 if (index // 2) % 2 else .88
            blocks.append((index, [int(rng.random() < p) for _ in range(probe.BLOCK)]))
        scores = {r["model"]: r for r in probe.fitted_scores(blocks)}
        self.assertGreater(scores["lag1_count8"]["gain_vs_lag1_bits"], .1)
        self.assertGreater(scores["lag1_count16"]["gain_vs_lag1_bits"], .1)

    def test_long_count_does_not_help_independent_or_markov(self):
        rng = random.Random(311)
        iid, markov = [], []
        for index in range(1024):
            iid.append((index, [rng.randrange(2) for _ in range(probe.BLOCK)]))
            bits = [rng.randrange(2)]
            for _ in range(1, probe.BLOCK):
                bits.append(bits[-1] if rng.random() < .8 else 1 - bits[-1])
            markov.append((index, bits))
        for blocks in (iid, markov):
            scores = {r["model"]: r for r in probe.fitted_scores(blocks)}
            for name in ("lag1_count8", "lag1_count16"):
                self.assertLess(scores[name]["gain_vs_lag1_bits"], .005)
        self.assertGreater(probe.fitted_scores(markov)[1]["gain_vs_frequency_bits"], .2)

    def test_empty_unseen_and_negative_transfer(self):
        for blocks in ([], [(0, [0] * 128)], [(1, [0] * 128)]):
            for row in probe.fitted_scores(blocks):
                self.assertIsNone(row["loss_bits"])
                self.assertIsNone(row["gain_vs_frequency_bits"])
        result = probe.score([[2, 0], [0, 0]], [[0, 0], [1, 3]])
        self.assertEqual(result["loss_bits"], 1)
        self.assertEqual(result["test_targets_with_unseen_context"], 4)
        # The long context's learned law reverses on the holdout.
        train = [(i, [0] * 64 + [1] * 64) for i in range(0, 32, 2)]
        test = [(i, [i % 2, (i + 1) % 2] * 64) for i in range(1, 32, 2)]
        self.assertLess(probe.fitted_scores(train + test)[3]["gain_vs_frequency_bits"], 0)

    def test_permutations_deterministic_preserve_input_and_mixture(self):
        blocks = [(i, [i // 2 % 2] * probe.BLOCK) for i in range(8)]
        before = [(i, bits[:]) for i, bits in blocks]
        measured = probe.measure(blocks)
        self.assertEqual(blocks, before)
        self.assertEqual(measured, probe.measure(blocks))
        for replicate in measured["permutations"]:
            for original, permuted in zip(measured["observed"], replicate):
                self.assertEqual(original["loss_bits"], permuted["loss_bits"])
        self.assertEqual(len(measured["permutations"]), 16)
        self.assertEqual(measured["permutation_means"][5]["loss_bits"], measured["observed"][5]["loss_bits"])

    def test_cli_rejects_invalid_and_duplicate_ids(self):
        for ids in (("0",), ("\u00b2",), ("\u0662",), ("1", "1"), ("1", "01")):
            args = [value for sid in ids for value in ("--sample", sid, "public", "unused")]
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                probe.main(args)
            self.assertEqual(caught.exception.code, 2)

    def test_mixed_cli_keeps_success_and_sanitizes_errors(self):
        def fake_report(sid, name, path):
            if sid == "2":
                raise OSError("private/path/should/not/appear")
            return {"pixls_id": sid, "statistics": {}}
        output = io.StringIO()
        with mock.patch.object(probe, "report", side_effect=fake_report), contextlib.redirect_stdout(output):
            code = probe.main(["--sample", "1", "public", "unused", "--sample", "2", "public", "unused"])
        self.assertEqual(code, 1)
        self.assertNotIn("private", output.getvalue())
        report = json.loads(output.getvalue())
        self.assertEqual(report["samples"], [{"pixls_id": "1", "statistics": {}}])
        self.assertEqual(report["errors"], [{"pixls_id": "2", "error_type": "OSError"}])
        self.assertEqual(len(report["source_sha256"]), 3)


if __name__ == "__main__":
    unittest.main()
