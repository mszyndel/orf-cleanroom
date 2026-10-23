"""Synthetic checks for jpeg_dc marker parsing and arithmetic (no sample files)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpeg_dc as j  # noqa: E402


def sof0(width, height):
    # marker + length + precision + height + width + 3 components
    seg = bytes([8, height >> 8, height & 255, width >> 8, width & 255, 3,
                 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1])
    return b"\xff\xc0" + bytes([0, len(seg) + 2]) + seg


class JpegTests(unittest.TestCase):
    def test_extend(self):
        self.assertEqual(j.extend(0b101, 3), 5)
        self.assertEqual(j.extend(0b001, 3), -6)
        self.assertEqual(j.extend(0b1111, 4), 15)
        self.assertEqual(j.extend(0b0000, 4), -15)

    def test_huffman(self):
        table = j.build_huffman([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [7, 8])
        self.assertEqual(table[(1, 0)], 7)
        self.assertEqual(table[(2, 2)], 8)

    def test_find_preview(self):
        data = b"\xff\xd8" + sof0(3200, 2400) + b"\xff\xda\x00\x02" + b"\xff\xd9"
        best = j.find_preview(data)
        self.assertIsNotNone(best)
        self.assertEqual(best[0], 3200 * 2400)
        self.assertEqual((best[3], best[4]), (3200, 2400))

    def test_thumbnail_ignored(self):
        thumb = b"\xff\xd8" + sof0(160, 120) + b"\xff\xda\x00\x02" + b"\xff\xd9"
        full = b"\xff\xd8" + sof0(3200, 2400) + b"\xff\xda\x00\x02" + b"\xff\xd9"
        best = j.find_preview(thumb + full)
        self.assertEqual((best[3], best[4]), (3200, 2400))


if __name__ == "__main__":
    unittest.main()
