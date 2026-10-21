#!/usr/bin/env python3
"""Independent synthetic parsing/count/entropy checks; no samples required."""
import collections
import contextlib
import io
import json
import math
import os
import random
import stat
import struct
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suffix_width_lag_probe as probe


def reference(data, k, stop, limit):
    bits = "".join(format(x, "08b") for x in data)
    pos, tokens = 0, []
    while pos < len(bits) and len(tokens) < limit:
        end = bits.find(str(stop), pos)
        if end < 0 or end + k + 1 > len(bits):
            break
        tokens.append((end - pos, int(bits[end + 1:end + 1 + k], 2)))
        pos = end + 1 + k
    return tokens, pos


def entropy(counts):
    total = sum(counts)
    return -sum(n / total * math.log2(n / total) for n in counts if n)


class Tests(unittest.TestCase):
    def test_all_bytes_and_random_against_string_parser(self):
        rng = random.Random(20261021)
        buffers = [bytes([i]) for i in range(256)]
        buffers += [b"", bytes(32), b"\xff" * 32,
                    bytes(32) + b"\xff\xff", b"\xff" * 32 + bytes(2)]
        buffers += [bytes(rng.randrange(256) for _ in range(80)) for _ in range(10)]
        for k in range(2, 9):
            for stop in (0, 1):
                for data in buffers:
                    for limit in (0, 3, 500):
                        self.assertEqual(probe.parse(data, k, stop, limit),
                                         reference(data, k, stop, limit))
        for k, stop, limit in ((1, 1, 2), (9, 0, 2), (5, 2, 2), (5, 1, -1)):
            with self.assertRaises(ValueError):
                probe.parse(b"\xff", k, stop, limit)

    def test_counts_orientation_omissions_and_entropy_identity(self):
        rng = random.Random(1234)
        tokens = [(rng.randrange(20), rng.randrange(256)) for _ in range(100)]
        for cell in probe.measures(tokens):
            lag = cell["lag"]
            pairs = [(tokens[t - lag], tokens[t]) for t in range(lag, len(tokens))]
            kept = [(a, b) for a, b in pairs if a[0] < 17 and b[0] < 17]
            self.assertEqual(cell["candidate_pairs"], len(pairs))
            self.assertEqual(cell["retained_pairs"], len(kept))
            self.assertEqual(cell["omitted_escape_endpoint_pairs"], len(pairs) - len(kept))
            for key, fn, n in (("q_positive", lambda t: int(t[0] > 0), 2),
                               ("suffix_low2", lambda t: t[1] & 3, 4)):
                counts = collections.Counter((fn(a), fn(b)) for a, b in kept)
                table = [[counts[i, j] for j in range(n)] for i in range(n)]
                self.assertEqual(cell[key + "_table"], table)
                expected = entropy(list(map(sum, table))) + entropy(
                    [sum(row[j] for row in table) for j in range(n)]) - entropy(
                    [x for row in table for x in row])
                self.assertAlmostEqual(cell[key + "_mi_bits"], expected, places=12)

    def test_no_compaction_intervening_escapes_and_directed_tables(self):
        tokens = [(0, 0), (17, 1), (1, 3), (0, 2)]
        cells = probe.measures(tokens)
        self.assertEqual(cells[0]["retained_pairs"], 1)
        self.assertEqual(cells[0]["suffix_low2_table"][3][2], 1)
        self.assertEqual(cells[1]["retained_pairs"], 1)
        self.assertEqual(cells[1]["suffix_low2_table"][0][3], 1)
        self.assertEqual(cells[2]["suffix_low2_table"][0][2], 1)
        self.assertIsNone(cells[3]["q_positive_mi_bits"])
        self.assertEqual(probe.mi([[5, 0], [0, 5]]), 1)
        self.assertEqual(probe.mi([[1, 1], [1, 1]]), 0)
        self.assertEqual(probe.mi([[8, 0], [0, 0]]), 0)
        self.assertTrue(all(c["retained_pairs"] == 0 for c in probe.measures([])))

    def test_real_container_both_endians_and_truncated_strip(self):
        class Input(io.BytesIO):
            def fileno(self):
                return 123
        regular = types.SimpleNamespace(st_mode=stat.S_IFREG)
        for endian, marker in (("<", b"II"), (">", b"MM")):
            entries = [(0x100, 10), (0x101, 10), (0x103, 1), (0x111, 74), (0x117, 2)]
            data = marker + struct.pack(endian + "HIH", 0x4f52, 8, 5)
            data += b"".join(struct.pack(endian + "HHII", tag, 4, 1, value)
                             for tag, value in entries) + bytes(4) + b"\x8b\x81"
            with mock.patch.object(probe.os, "stat", return_value=regular), mock.patch.object(probe.os, "fstat", return_value=regular):
                with mock.patch("builtins.open", return_value=Input(data)):
                    result = probe.report("1", "public", "input")
                self.assertEqual((result["payload_w"], result["payload_h"], result["payload_bytes"]), (10, 10, 2))
                self.assertEqual(len(result["cells"]), 14)
                for cell in result["cells"]:
                    tokens, end = reference(data[-2:], cell["k"], cell["stop_bit"], probe.TOKENS)
                    self.assertEqual(cell["tokens"], len(tokens))
                    self.assertEqual(cell["token_shortfall"], probe.TOKENS - len(tokens))
                    self.assertEqual(cell["bits_consumed"], end)
                    self.assertEqual(cell["remaining_payload_bits"], 16 - end)
                    self.assertEqual(cell["q_ge_17"], sum(q >= 17 for q, _ in tokens))
                    self.assertEqual(cell["lags"], probe.measures(tokens))
                with mock.patch("builtins.open", return_value=Input(data[:-1])):
                    with self.assertRaises(ValueError):
                        probe.report("1", "public", "input")

    def test_cli_validation_failure_sanitization_and_retained_success(self):
        output = io.StringIO()
        with mock.patch.object(probe, "report", side_effect=[{"pixls_id": "1"}, ValueError("secret path")]):
            with contextlib.redirect_stdout(output):
                status = probe.main(["--sample", "1", "one", "file1", "--sample", "2", "two", "file2"])
        self.assertEqual(status, 1)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["samples"], [{"pixls_id": "1"}])
        self.assertEqual(parsed["failures"], [{"pixls_id": "2", "error": "invalid_or_unreadable_input"}])
        self.assertNotIn("secret", output.getvalue())
        for args in (["--sample", "0", "x", "f"], ["--sample", "1", "x", "f", "--sample", "1", "y", "g"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                probe.main(args)


if __name__ == "__main__":
    unittest.main()
