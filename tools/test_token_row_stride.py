"""Synthetic checks for token_row_stride.stride_scores (no sample files)."""

import os
import sys
import unittest
import contextlib
import io
import math
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_row_stride as r  # noqa: E402


class StrideTests(unittest.TestCase):
    def test_known_stride(self):
        head, rows, s0 = 24, 80, 137
        q = []
        for i in range(rows):
            q.extend([3 + (i % 2)] * head)
            q.extend([0] * (s0 - head))
        best = r.stride_scores(q, s0 - 5, s0 + 5, rows, head)[0]
        self.assertEqual(best[2], s0)
        self.assertGreater(best[0], 10)

    def test_flat_has_no_peak(self):
        q = [0] * (60 * 100)
        scores = r.stride_scores(q, 98, 102, 60, 8)
        self.assertEqual(scores[0][0], 0.0)

    def test_too_few_rows(self):
        # 8 tokens per stride and 12 rows cannot make the 20-row minimum.
        self.assertEqual(r.stride_scores([1] * 96, 8, 8, 12, 2), [])

    def test_head_must_fit(self):
        # stride <= head is skipped rather than dividing by zero.
        self.assertEqual(r.stride_scores([1] * 400, 4, 4, 50, 8), [])

    def test_constant_elevation_preserves_sign(self):
        for head_q, rest_q, expected in ((2, 0, math.inf), (0, 2, -math.inf), (2, 2, 0.0)):
            q = ([head_q] * 10 + [rest_q] * 40) * 40
            with self.subTest(head=head_q, rest=rest_q):
                self.assertEqual(r.stride_scores(q, 50, 50, 40, 10)[0][0], expected)

    def test_nonpositive_head_rejected_before_input(self):
        for head in (0, -1):
            with self.subTest(head=head), patch.object(sys, "argv", ["token_row_stride.py", "synthetic.ORF", "--head", str(head)]):
                with patch.object(r, "scan_file") as scan_file, contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as raised:
                        r.main()
                    self.assertEqual(raised.exception.code, 2)
                    scan_file.assert_not_called()

    def test_failed_input_sets_status_and_continues(self):
        with patch.object(sys, "argv", ["token_row_stride.py", "bad.ORF", "good.ORF"]):
            with patch.object(r, "scan_file", side_effect=[OSError("unreadable"), None]) as scan_file:
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(r.main(), 1)
                self.assertEqual([call.args[0] for call in scan_file.call_args_list], ["bad.ORF", "good.ORF"])


if __name__ == "__main__":
    unittest.main()
