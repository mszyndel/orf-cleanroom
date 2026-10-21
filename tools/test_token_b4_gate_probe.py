#!/usr/bin/env python3
"""Synthetic checks of lead #32 b4 descriptive tables; stdlib only."""
import contextlib
from fractions import Fraction
import io
import json
import math
import os
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_b4_gate_probe as probe


class GateTests(unittest.TestCase):
    def test_stratified_exact_enumeration_and_default_compatibility(self):
        tokens = [(q, s) for q in range(17) for s in range(32)
                  for _ in range(1 + (q + 3 * s) % 5)] + [(17, 31), (20, 3)]
        default = probe.measure(tokens)
        extended = probe.measure(tokens, q_stratified=True)
        strata = extended.pop("q_stratified_fields")
        self.assertEqual(default, extended)
        for field, mask in (("low3", 7), ("low4", 15)):
            differences = []
            pooled = [[0] * (mask + 1) for _ in range(2)]
            for q, row in enumerate(strata[field]["strata"]):
                groups = [[s & mask for tq, s in tokens if tq == q and s >> 4 == b]
                          for b in range(2)]
                for b, values in enumerate(groups):
                    self.assertEqual(row["counts_b4_0_1"][b], len(values))
                    self.assertEqual(row["integer_sums_b4_0_1"][b], sum(values))
                    self.assertEqual(row["b4_rows_value_columns"][b],
                                     [values.count(v) for v in range(mask + 1)])
                    pooled[b] = [a + c for a, c in zip(pooled[b], row["b4_rows_value_columns"][b])]
                expected = Fraction(sum(groups[0]), len(groups[0])) - Fraction(sum(groups[1]), len(groups[1]))
                actual = row["mean_b4_0_minus_b4_1"]
                self.assertEqual(Fraction(actual["numerator"], actual["denominator"]), expected)
                differences.append(expected)
            self.assertEqual(pooled, default["fields"][field]["b4_rows_value_columns"])
            adjusted = strata[field]["equal_weight_mean_b4_0_minus_b4_1"]
            self.assertEqual(Fraction(adjusted["numerator"], adjusted["denominator"]), sum(differences) / 17)
            self.assertEqual(strata[field]["support_q"], list(range(17)))

    def test_stratified_simpson_reversal(self):
        tokens = [(0, 1)] * 100 + [(0, 16)] + [(1, 15)] + [(1, 30)] * 100
        result = probe.measure(tokens, True)
        means = result["fields"]["low4"]["means_b4_0_1"]
        self.assertLess(means[0], means[1])
        adjusted = result["q_stratified_fields"]["low4"]
        self.assertEqual(adjusted["support_q"], [0, 1])
        self.assertEqual(adjusted["excluded_q"], list(range(2, 17)))
        self.assertEqual(adjusted["equal_weight_mean_b4_0_minus_b4_1"],
                         {"numerator": 1, "denominator": 1, "approx": 1.0})

    def test_stratified_sparse_empty_and_cli_forwarding(self):
        for tokens in ([], [(17, 0)], [(16, 15)]):
            fields = probe.measure(tokens, True)["q_stratified_fields"]
            for field in fields.values():
                self.assertEqual(len(field["strata"]), 17)
                self.assertEqual(field["support_strata"], 0)
                self.assertEqual(field["excluded_q"], list(range(17)))
                self.assertIsNone(field["equal_weight_mean_b4_0_minus_b4_1"])
                self.assertTrue(all(r["mean_b4_0_minus_b4_1"] is None for r in field["strata"]))
        tokens = [(0, 0), (0, 19), (1, 5), (1, 16), (1, 16), (2, 7)]
        field = probe.measure(tokens, True)["q_stratified_fields"]["low4"]
        self.assertEqual(field["support_q"], [0, 1])
        self.assertEqual(field["equal_weight_mean_b4_0_minus_b4_1"]["numerator"], 1)
        with patch.object(probe, "report", return_value={"ok": 1}) as mocked:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(["--q-stratified", "--sample", "1", "a", "hidden"]), 0)
            mocked.assert_called_once_with("1", "a", "hidden", True)

    def test_all_suffixes_and_empty(self):
        result = probe.measure([(0, s) for s in range(32)])
        for field, width in (("low3", 8), ("low4", 16)):
            rows = result["fields"][field]
            self.assertEqual(rows["b4_rows_value_columns"], [[16 // width] * width] * 2)
            self.assertEqual(rows["means_b4_0_1"], [(width - 1) / 2] * 2)
        self.assertEqual(result["current_q_current_b4"]["plugin_mi_bits"], 0)
        empty = probe.measure([])
        self.assertIsNone(empty["current_q_current_b4"]["plugin_mi_bits"])
        self.assertEqual(empty["fields"]["low4"]["means_b4_0_1"], [None, None])

    def test_exact_lag_and_escape_omissions(self):
        # Only pairs 0->1 and 4->5 survive. Neither end bridges an escape.
        tokens = [(1, 0), (2, 31), (17, 7), (18, 8), (3, 16), (4, 2)]
        result = probe.measure(tokens)
        self.assertEqual(result["ordinary_tokens"], 4)
        self.assertEqual(result["escape_tokens_omitted"], 2)
        self.assertEqual(result["lag1_candidate_pairs"], 5)
        self.assertEqual(result["lag1_escape_endpoint_omitted_pairs"], 3)
        expected = [[0, 0] for _ in range(17)]
        expected[1][1], expected[3][0] = 1, 1
        self.assertEqual(result["previous_q_current_b4"]["q_by_b4_counts"], expected)
        self.assertEqual(result["fields"]["low4"]["integer_sums_b4_0_1"], [2, 15])

    def test_planted_q_dependence_and_entropy_oracle(self):
        tokens = [(q, 16 * (q % 2)) for q in range(16)] * 4
        result = probe.measure(tokens)["current_q_current_b4"]
        self.assertEqual(result["plugin_mi_bits"], 1)
        table = [[3, 1], [2, 6]] + [[0, 0] for _ in range(15)]
        def entropy(values):
            n = sum(values)
            return -sum(x / n * math.log2(x / n) for x in values if x)
        expected = (entropy(list(map(sum, table))) + entropy(list(map(sum, zip(*table))))
                    - entropy([x for row in table for x in row]))
        self.assertAlmostEqual(probe.summarize(table)["plugin_mi_bits"], expected, places=14)
        self.assertIsNone(probe.summarize(table)["p_b4_one_given_q"][2])

    def test_edges_degenerate_and_validation(self):
        for tokens in ([(17, 0)], [(17, 0), (18, 31)], [(0, 0)]):
            result = probe.measure(tokens)
            self.assertEqual(result["previous_q_current_b4"]["retained"], 0)
        for tokens in ([(True, 0)], [(-1, 0)], [(0, 32)], [(0, False)]):
            with self.assertRaises(ValueError):
                probe.measure(tokens)

    def test_synthetic_tiff_both_orders(self):
        # Four complete tokens: q=0..3, suffix 0,17,2,31. Zero padding has no stop.
        tokens = [(0, 0), (1, 17), (2, 2), (3, 31)]
        bits = "".join("0" * q + "1" + format(s, "05b") for q, s in tokens)
        padded = bits + "0" * (-len(bits) % 8)
        payload = int(padded, 2).to_bytes(len(padded) // 8, "big")
        for endian, mark in (("<", b"II"), (">", b"MM")):
            entries = ((256, 3), (257, 3), (273, 62), (279, len(payload)))
            data = mark + struct.pack(endian + "HIH", 42, 8, len(entries))
            data += b"".join(struct.pack(endian + "HHII", tag, 4, 1, value) for tag, value in entries)
            data += struct.pack(endian + "I", 0) + payload
            path = "synthetic.orf"
            with patch("builtins.open", return_value=io.BytesIO(data)):
                result = probe.report("1", "synthetic", path)
            self.assertEqual(result["returned_tokens"], 4)
            self.assertEqual(result["bits_consumed"], len(bits))
            self.assertEqual(result["statistics"], probe.measure(tokens))

    def test_cli_mixed_failure_sanitized(self):
        with patch.object(probe, "report", side_effect=[OSError("private-path"), {"ok": 1}]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = probe.main(["--sample", "1", "a", "hidden", "--sample", "2", "b", "hidden"])
            self.assertEqual(code, 1)
            self.assertNotIn("private-path", output.getvalue())
            self.assertNotIn("hidden", output.getvalue())
            self.assertEqual(json.loads(output.getvalue())["samples"], [{"ok": 1}])
        for ids in (("1", "01"), ("0", "2"), ("\u0661", "2")):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                probe.main(["--sample", ids[0], "a", "x", "--sample", ids[1], "b", "y"])


if __name__ == "__main__":
    unittest.main()
