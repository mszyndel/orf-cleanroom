"""Synthetic checks for token_row_stride.stride_scores (no sample files)."""

import os
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
