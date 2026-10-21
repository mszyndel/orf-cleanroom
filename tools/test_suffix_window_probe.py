#!/usr/bin/env python3
"""Independent synthetic counts/entropy, selection and CLI checks for #11."""
import collections
import contextlib
import io
import json
import math
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suffix_window_probe as probe


def entropy(values):
    n = len(values)
    return -sum(c / n * math.log2(c / n) for c in collections.Counter(values).values()) if n else 0


class WindowTests(unittest.TestCase):
    def test_all_tables_independent_enumeration(self):
        tokens = [(17 if i % 11 == 0 else i % 5, (7 * i + i // 3) % 32) for i in range(77)]
        with mock.patch.object(probe, "WINDOW", 20):
            reports = probe.measure(tokens)
        self.assertEqual(len(reports), 4)
        for index, r in enumerate(reports):
            selected = tokens[index * 20:(index + 1) * 20]
            self.assertEqual(r["start_token"], index * 20)
            self.assertEqual(r["returned_tokens"], len(selected))
            self.assertEqual(r["escape_tokens"], sum(q >= 17 for q, s in selected))
            for lag_report in r["lags"]:
                lag = lag_report["lag_tokens"]
                same, cross = [], []
                for cell in lag_report["pairings"]:
                    pairs = []
                    for i in range(lag, len(selected)):
                        if selected[i - lag][0] >= 17 or selected[i][0] >= 17:
                            continue
                        a, b = selected[i - lag][1], selected[i][1]
                        pairs.append((a // 8 if cell["source"] == "H" else a % 8,
                                      b // 8 if cell["target"] == "H" else b % 8))
                    counts = collections.Counter(pairs)
                    table = cell["joint_source_rows_target_columns"]
                    self.assertEqual(table, [[counts[x, y] for y in range(len(table[0]))]
                                             for x in range(len(table))])
                    self.assertEqual(lag_report["retained_pairs"], len(pairs))
                    expected = entropy([a for a, b in pairs]) + entropy([b for a, b in pairs]) - entropy(pairs)
                    self.assertAlmostEqual(cell["plugin_mi_bits"], expected, places=12)
                    (same if cell["source"] == cell["target"] else cross).append(expected)
                stronger, weaker = (same, cross) if lag == 2 else (cross, same)
                self.assertEqual(lag_report["strict_alternating_order"],
                                 all(a > b for a in stronger for b in weaker))

    def test_report_signature_bounds_and_short_input(self):
        data = bytes([255]) * 64
        tags = {0x111: [16], 0x117: [8], 0x100: [5], 0x101: [4], 0x103: [1]}
        fake_tiff = mock.Mock()
        fake_tiff.all_ifds.return_value = [tags]
        with mock.patch.object(probe, "Tiff", return_value=fake_tiff), mock.patch(
                "builtins.open", mock.mock_open(read_data=data)):
            result = probe.report("1", "public", "local")
            self.assertEqual(result["returned_tokens"], 10)
            self.assertEqual(result["bits_consumed"], 60)
            self.assertEqual(result["windows"][0]["shortfall_tokens"], probe.WINDOW - 10)
            tags[0x117] = [1000]
            with self.assertRaises(ValueError):
                probe.report("1", "public", "local")
            tags[0x117] = [8]
            tags[0x103] = [7]
            with self.assertRaises(ValueError):
                probe.report("1", "public", "local")

    def test_escapes_do_not_join_or_exclude_intervening_pair(self):
        tokens = [(0, 0), (17, 31), (0, 31)]
        report = probe.measure(tokens)[0]
        self.assertEqual(report["lags"][0]["retained_pairs"], 0)
        self.assertEqual(report["lags"][1]["retained_pairs"], 1)
        self.assertIsNone(report["all_lags_strict_alternating_order"])

    def test_no_cross_window_pairs_and_shortfalls(self):
        with mock.patch.object(probe, "WINDOW", 4):
            reports = probe.measure([(0, 0)] * 4 + [(0, 31)] * 4 + [(0, 12)])
        self.assertEqual([r["shortfall_tokens"] for r in reports], [0, 0, 3, 4])
        for r in reports[:2]:
            self.assertFalse(r["all_lags_strict_alternating_order"])
            for lag in r["lags"]:
                self.assertEqual(lag["retained_pairs"], 4 - lag["lag_tokens"])
                self.assertTrue(all(p["plugin_mi_bits"] == 0 for p in lag["pairings"]))

    def test_cli_partial_failure_and_sanitizing(self):
        output = io.StringIO()
        argv = ["probe", "--sample", "1", "public", "local", "--sample", "2", "bad", "secret-path"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(probe, "report", side_effect=[{"pixls_id": "1"}, OSError("secret-path")]):
            with contextlib.redirect_stdout(output):
                code = probe.main()
        result = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(result["samples"], [{"pixls_id": "1"}])
        self.assertEqual(result["failures"], [{"pixls_id": "2", "error": "OSError"}])
        self.assertNotIn("secret-path", output.getvalue())

    def test_id_alias_rejected(self):
        with mock.patch.object(sys, "argv", ["probe", "--sample", "1", "a", "a", "--sample", "01", "b", "b"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                probe.main()
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
