#!/usr/bin/env python3
"""Synthetic exact-rank, affine, orientation and selection controls; no samples."""
import itertools
import contextlib
import io
import os
import random
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_affine_probe as probe  # noqa: E402


def rank_by_span(rows):
    span = {0}
    for row in rows:
        span |= {value ^ row for value in span}
    return (len(span) - 1).bit_length()


def rank(rows):
    basis = probe.Basis()
    for row in rows:
        basis.add(row)
    return basis.rank()


class TestAffine(unittest.TestCase):
    def test_rank_exhaustive_small_and_random(self):
        for rows in itertools.product(range(8), repeat=4):
            self.assertEqual(rank(rows), rank_by_span(rows))
        rng = random.Random(29)
        for _ in range(100):
            rows = [rng.randrange(32) for _ in range(10)]
            self.assertEqual(rank(rows), rank_by_span(rows))

    def test_affine_and_contradiction_bruteforce(self):
        for outputs in itertools.product((0, 1), repeat=4):
            contexts = [4 | value for value in range(4)]
            augmented = [x | (y << 3) for x, y in zip(contexts, outputs)]
            possible = any(all((bin(x & coefficients).count("1") % 2) == y
                               for x, y in zip(contexts, outputs))
                           for coefficients in range(8))
            self.assertEqual(rank(contexts) == rank(augmented), possible)
        self.assertEqual(rank([1, 1]), 1)
        self.assertEqual(rank([1, 3]), 2)  # same input, opposite outputs

    def test_planted_affine_and_parity(self):
        rng = random.Random(1224)
        suffixes = [rng.randrange(32) for _ in range(12)]
        # b2(t)=b4(t-1) XOR b2(t-12) XOR 1. b4 is arbitrary.
        for t in range(12, 500):
            bit = ((suffixes[t - 1] >> 4) ^ (suffixes[t - 12] >> 2) ^ 1) & 1
            suffixes.append((rng.randrange(2) << 4) | (bit << 2))
        result = probe.measure([(0, s) for s in suffixes])
        for cell in result["systems"]:
            self.assertEqual(cell["retained_rows"], 488 if cell["stratum"] == "pooled" else 244)
            if cell["target"] == "b2":
                self.assertTrue(cell["exact_affine_consistent"])
            else:
                self.assertFalse(cell["exact_affine_consistent"])

    def test_window_orientation_selection_independent_lists(self):
        rng = random.Random(2912)
        tokens = [(0, rng.randrange(32)) for _ in range(80)]
        for index in (0, 12, 26, 27, 79):
            tokens[index] = (17, tokens[index][1])
        got = probe.measure(tokens)
        self.assertEqual(got["candidate_windows"], 68)
        self.assertEqual(got["parsed_escapes"], 5)
        for cell in got["systems"]:
            rows, augmented, omitted = [], [], 0
            for t in range(12, len(tokens)):
                if cell["stratum"] != "pooled" and (t % 2 == 1) != (cell["stratum"] == "odd"):
                    continue
                if any(q >= 17 for q, _ in tokens[t - 12:t + 1]):
                    omitted += 1
                    continue
                features = []
                for lag in range(1, 13):
                    features.extend([(tokens[t - lag][1] >> bit) & 1 for bit in (2, 4)])
                features.append(1)
                x = sum(value * 2 ** column for column, value in enumerate(features))
                y = (tokens[t][1] >> int(cell["target"][1:])) & 1
                rows.append(x)
                augmented.append(x + y * 2 ** 25)
            self.assertEqual(cell["retained_rows"], len(rows))
            self.assertEqual(cell["omitted_escape_windows"], omitted)
            self.assertEqual(cell["context_rank"], rank(rows))
            self.assertEqual(cell["augmented_rank"], rank(augmented))

    def test_empty_short_all_escape(self):
        for tokens in ([], [(0, 0)] * 12, [(17, 0)] * 40):
            for cell in probe.measure(tokens)["systems"]:
                self.assertIsNone(cell["exact_affine_consistent"])
                self.assertEqual(cell["context_rank"], 0)
        self.assertRaises(ValueError, probe.Basis().add, -1)

    def test_container_reports_and_bounds(self):
        for order, mark in (("<", b"II"), (">", b"MM")):
            entries = [(0x100, 100), (0x101, 100), (0x111, 74), (0x117, 80)]
            data = mark + struct.pack(order + "HIH", 42, 8, 4)
            data += b"".join(struct.pack(order + "HHII", tag, 4, 1, value)
                             for tag, value in entries)
            data += struct.pack(order + "I", 0)
            data += bytes(74 - len(data)) + bytes([0xff]) * 80
            with mock.patch("builtins.open", side_effect=lambda *args, **kwargs: io.BytesIO(data)):
                report = probe.report("1", "synthetic.ORF", "ignored")
            self.assertEqual(report["payload_w"], 100)
            self.assertEqual(report["returned_tokens"], 106)
            self.assertEqual(report["bits_consumed"], 636)
            self.assertEqual(report["statistics"]["candidate_windows"], 94)
            with mock.patch("builtins.open", side_effect=lambda *args, **kwargs: io.BytesIO(data[:-1])):
                self.assertRaises(ValueError, probe.report, "1", "synthetic.ORF", "ignored")

    def test_cli_validation_and_no_partial_output(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "argv", ["probe", "--sample", "bad", "name", "path"]), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                probe.main()
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(stdout.getvalue(), "")
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "argv", ["probe", "--sample", "1", "n", "a",
                                             "--sample", "2", "n", "private-path"]), \
                mock.patch.object(probe, "report", side_effect=[{"ok": True}, OSError("private-path")]), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as error:
                probe.main()
        self.assertEqual(error.exception.code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "sample 2: OSError\n")


if __name__ == "__main__":
    unittest.main()
