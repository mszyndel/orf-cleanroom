#!/usr/bin/env python3
"""Synthetic reporting regressions for the predictor probe (leads #31/#32).

No sample files, network or filesystem writes.
"""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_predictor_probe as probe


class CommandTests(unittest.TestCase):
    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = probe.main(args)
        return status, out.getvalue(), err.getvalue()

    def test_missing_input_fails(self):
        with mock.patch("builtins.open", side_effect=FileNotFoundError):
            status, out, err = self.invoke(["missing.orf"])
        self.assertEqual(status, 1)
        self.assertIn("requested=1 complete=0 failed=1", out)
        self.assertIn("report incomplete", err)

    def test_non_orf_input_fails(self):
        with mock.patch("builtins.open", mock.mock_open(read_data=b"not an ORF")):
            status, out, _ = self.invoke(["invalid.orf"])
        self.assertEqual(status, 1)
        self.assertIn("status=incomplete", out)

    def test_mixed_inputs_keep_success_and_count_every_failure(self):
        def run(path, *_args):
            if path == "bad.orf":
                raise ValueError("bad input")
            print("synthetic successful report")
        with mock.patch.object(probe, "run_file", side_effect=run):
            status, out, _ = self.invoke(["good.orf", "bad.orf", "last.orf"])
        self.assertEqual(status, 1)
        self.assertEqual(out.count("synthetic successful report"), 2)
        self.assertIn("requested=3 complete=2 failed=1", out)

    def test_failure_after_output_is_incomplete(self):
        def run(*_args):
            print("partial experimental output")
            raise ValueError("measurement failed")
        with mock.patch.object(probe, "run_file", side_effect=run):
            status, out, _ = self.invoke(["partial.orf"])
        self.assertEqual(status, 1)
        self.assertIn("partial experimental output", out)
        self.assertIn("partial.orf status=incomplete", out)

    def test_success_returns_zero(self):
        with mock.patch.object(probe, "run_file"):
            status, out, _ = self.invoke(["good.orf"])
        self.assertEqual(status, 0)
        self.assertIn("requested=1 complete=1 failed=0", out)

    def test_bad_options_rejected_before_input(self):
        for opts in (["--rows", "0"], ["--perms", "0"], ["--perms", "-1"],
                     ["--kinds", "unknown"], ["--preds", "unknown"],
                     ["--kinds", ""], ["--preds", ""]):
            with self.subTest(opts=opts), mock.patch.object(probe, "run_file") as run:
                with self.assertRaises(SystemExit) as exc:
                    self.invoke(["input.orf"] + opts)
                self.assertEqual(exc.exception.code, 2)
                run.assert_not_called()

    def test_complete_report_preserves_ordered_rng_and_all_combinations(self):
        qa, sa = bytearray([0] * 8), bytearray(range(8))
        kinds, preds = list(probe.KINDS), list(probe.PREDS)
        out = io.StringIO()
        with mock.patch.object(probe, "read_tokens", return_value=(4, 2, qa, sa, 2)), \
                mock.patch.object(probe, "read_preview", return_value=(2, 2, [0, 1, 1, 0], 2)), \
                mock.patch.object(probe, "score", return_value=0.25), \
                contextlib.redirect_stdout(out):
            probe.run_file("synthetic.orf", 2, 2, kinds, preds)
        report = out.getvalue()
        self.assertEqual(report.count(" r="), len(kinds) * len(preds))
        self.assertIn("kinds=" + ",".join(kinds), report)
        self.assertIn("preds=" + ",".join(preds), report)
        self.assertIn("rng=shared-ordered", report)
        self.assertIn("not calibrated significance", report)


if __name__ == "__main__":
    unittest.main()
