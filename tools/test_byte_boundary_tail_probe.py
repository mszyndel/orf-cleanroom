#!/usr/bin/env python3
"""Independent direct bit-string checks of byte-boundary counts (#87)."""
from collections import Counter
import contextlib
import io
import itertools
import json
import os
import random
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from byte_boundary_tail_probe import boundary_report, main, report


def direct(payload):
    bits = "".join(format(value, "08b") for value in payload)
    tails = []
    for end in range(8, len(bits)+1, 8):
        cursor = end
        while cursor and bits[cursor-1] == "1":
            cursor -= 1
        tails.append(end-cursor)
    return tails


class BoundaryTests(unittest.TestCase):
    def check_payload(self, payload):
        tails = direct(payload)
        got = boundary_report(payload)
        self.assertEqual(got["all_boundary_histogram"], Counter(tails))
        self.assertEqual(got["earlier_boundary_histogram"], Counter(tails[:-1]))
        self.assertEqual(got["final_trailing_ones"], tails[-1])
        self.assertEqual(got["earlier_less"], sum(t < tails[-1] for t in tails[:-1]))
        self.assertEqual(got["earlier_equal"], sum(t == tails[-1] for t in tails[:-1]))
        self.assertEqual(got["earlier_greater"], sum(t > tails[-1] for t in tails[:-1]))
        self.assertEqual(got["earlier_positive"], sum(t > 0 for t in tails[:-1]))
        self.assertEqual(got["earlier_at_least_final"], sum(t >= tails[-1] for t in tails[:-1]))
        self.assertEqual(got["earlier_boundaries"], len(payload)-1)

    def test_all_two_byte_inputs(self):
        for a, b in itertools.product(range(256), repeat=2):
            self.check_payload(bytes((a, b)))

    def test_ff_chains(self):
        for prefix in (b"", b"\x00", b"\x7f", b"\x03\xff\x01"):
            for suffix in (b"", b"\x00", b"\xff", b"\x01\xff"):
                for n in (1, 2, 8, 17):
                    self.check_payload(prefix+b"\xff"*n+suffix)

    def test_random_strings(self):
        rng = random.Random(87)
        for n in (3, 17, 256, 4096):
            self.check_payload(bytes(rng.randrange(256) for _ in range(n)))

    def test_single_empty_and_ties(self):
        with self.assertRaises(ValueError):
            boundary_report(b"")
        for value in range(256):
            got = boundary_report(bytes((value,)))
            self.assertIsNone(got["earlier_positive_fraction"])
            self.assertIsNone(got["earlier_at_least_final_fraction"])
            self.check_payload(bytes((value,)))
        got = boundary_report(b"\x00"*4)
        self.assertEqual(got["earlier_equal"], 3)
        self.assertEqual(got["earlier_at_least_final_fraction"], 1)

    def test_id_rejection(self):
        for args in (["--sample", "0", "name", "missing"],
                     ["--sample", "1", "a", "missing", "--sample", "01", "b", "missing"]):
            with self.assertRaises(SystemExit) as raised:
                main(args)
            self.assertEqual(raised.exception.code, 2)

    def test_container_both_byte_orders(self):
        payload = b"\x03\xff\xff\x00\x01"
        for order, mark in (("<", b"II"), (">", b"MM")):
            offset = 8+2+5*12+4
            data = mark + struct.pack(order+"HIH", 0x4f52, 8, 5)
            for tag, value in ((0x100, 3), (0x101, 2), (0x103, 1),
                               (0x111, offset), (0x117, len(payload))):
                data += struct.pack(order+"HHII", tag, 4, 1, value)
            data += struct.pack(order+"I", 0)+payload
            with patch("builtins.open", return_value=io.BytesIO(data)):
                got = report("1", "synthetic", "ignored")
            self.assertEqual(got["statistics"], boundary_report(payload))
            self.assertEqual(got["payload_width"], 3)
            self.assertEqual(got["payload_height"], 2)

    def test_missing_file_sanitized(self):
        output = io.StringIO()
        # Patch only the per-sample report; source hashes still read real code.
        with patch("byte_boundary_tail_probe.report", side_effect=OSError("PRIVATE_PATH")):
            with contextlib.redirect_stdout(output):
                code = main(["--sample", "1", "synthetic", "PRIVATE_PATH"])
        self.assertEqual(code, 1)
        self.assertNotIn("PRIVATE_PATH", output.getvalue())
        self.assertEqual(json.loads(output.getvalue())["errors"],
                         [{"pixls_id": "1", "error_type": "OSError"}])

    def test_payload_rejections(self):
        base = {0x100: [3], 0x101: [2], 0x111: [0], 0x117: [5]}
        cases = [dict(base, **{}) for _ in range(4)]
        cases[0][0x111] = [0, 1]  # Unsupported multistrip.
        cases[1][0x117] = [9]     # Beyond the supplied data.
        cases[2][0x117] = [0]     # Empty payload.
        cases[3][0x100], cases[3][0x101], cases[3][0x117] = [2], [2], [8]  # packed-16.
        for tags in cases:
            with patch("builtins.open", return_value=io.BytesIO(b"12345678")):
                with patch("byte_boundary_tail_probe.Tiff") as tiff:
                    tiff.return_value.all_ifds.return_value = [tags]
                    with self.assertRaises(ValueError):
                        report("1", "synthetic", "ignored")

    def test_mixed_cli_preserves_success(self):
        output = io.StringIO()
        with patch("byte_boundary_tail_probe.report", side_effect=[{"pixls_id": "1"}, OSError("PRIVATE")]):
            with contextlib.redirect_stdout(output):
                code = main(["--sample", "1", "synthetic", "ok",
                             "--sample", "2", "synthetic", "PRIVATE"])
        parsed = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(parsed["samples"], [{"pixls_id": "1"}])
        self.assertEqual(parsed["errors"], [{"pixls_id": "2", "error_type": "OSError"}])
        self.assertNotIn("PRIVATE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
