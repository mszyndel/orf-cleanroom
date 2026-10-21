#!/usr/bin/env python3
"""Synthetic checks of lead #32 b4 descriptive tables; stdlib only."""
import contextlib
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
