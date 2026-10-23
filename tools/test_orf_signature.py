#!/usr/bin/env python3
"""Signature CSV and failure exit status; synthetic TIFF metadata only."""
import contextlib
import csv
import hashlib
import io
import os
import runpy
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orf_signature as S


def fixture(width=2):
    entries = [(256, width), (257, 2), (258, 16), (259, 1),
               (273, 86), (279, width * 4)]
    return (struct.pack("<2sHIH", b"II", 0x5352, 8, len(entries))
            + b"".join(struct.pack("<HHII", tag, 4, 1, value)
                       for tag, value in entries)
            + struct.pack("<I", 0) + bytes(width * 4))


class Tests(unittest.TestCase):
    def call(self, paths, blobs):
        def opening(path, mode):
            self.assertEqual(mode, "rb")
            if path not in blobs:
                raise FileNotFoundError("synthetic missing input")
            return io.BytesIO(blobs[path])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("builtins.open", side_effect=opening), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = S.main(paths)
        return status, out.getvalue(), err.getvalue()

    def test_valid_csv_and_input_order(self):
        a, b = fixture(), fixture(3)
        status, output, error = self.call(["b.orf", "a.orf"],
                                           {"a.orf": a, "b.orf": b})
        self.assertEqual(status, 0)
        self.assertEqual(error, "")
        rows = list(csv.DictReader(io.StringIO(output)))
        self.assertEqual([r["file"] for r in rows], ["b.orf", "a.orf"])
        self.assertEqual(rows[0]["sha256"], hashlib.sha256(b).hexdigest())
        self.assertEqual(rows[0]["payload_w"], "3")
        self.assertEqual(rows[0]["payload_bytes"], "12")
        self.assertEqual(rows[0]["size_class"], "packed-16")
        self.assertEqual(output.count("file,sha256,"), 1)

    def test_all_missing_inputs_fail_without_csv(self):
        status, output, error = self.call(["missing.orf", "absent.orf"], {})
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("missing.orf: synthetic missing input", error)
        self.assertIn("absent.orf: synthetic missing input", error)

    def test_mixed_errors_preserve_successful_rows(self):
        blobs = {"valid.orf": fixture(), "bad.orf": b"not TIFF",
                 "short.orf": b"II", "last.orf": fixture(3)}
        paths = ["missing.orf", "valid.orf", "bad.orf", "short.orf", "last.orf"]
        status, output, error = self.call(paths, blobs)
        self.assertEqual(status, 1)
        rows = list(csv.DictReader(io.StringIO(output)))
        self.assertEqual([r["file"] for r in rows], ["valid.orf", "last.orf"])
        self.assertEqual(len(error.splitlines()), 3)
        self.assertEqual(output.count("file,sha256,"), 1)

    def test_no_ifds_fails(self):
        status, output, error = self.call(["empty.orf"],
            {"empty.orf": struct.pack("<2sHI", b"II", 0x5352, 0)})
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("empty.orf:", error)

    def test_help_and_no_arguments(self):
        for paths, expected in [(["--help"], 0), (["-h"], 0), ([], 2)]:
            status, output, error = self.call(paths, {})
            self.assertEqual(status, expected)
            self.assertIn("Print a measured signature", output)
            self.assertEqual(error, "")

    def test_script_entrypoint_propagates_failure(self):
        # Run the reviewed tool entrypoint in this process; no child programs.
        path = os.path.join(os.path.dirname(__file__), "orf_signature.py")
        with mock.patch.object(sys, "argv", [path, "missing-synthetic.orf"]), \
                mock.patch("builtins.open", side_effect=FileNotFoundError("missing")), \
                contextlib.redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit) as raised:
            runpy.run_path(path, run_name="__main__")
        self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
