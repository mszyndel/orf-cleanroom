"""Round-trip checks for decoder/orf_decode.py on synthetic bytes (no sample files)."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "decoder"))
import orf_decode as d  # noqa: E402


def pack12(vals):          # finding: MSB first, two values per three bytes
    out = bytearray()
    for a, b in zip(vals[0::2], vals[1::2]):
        out += bytes([a >> 4, (a & 15) << 4 | b >> 8, b & 255])
    return bytes(out)


def pack128(vals):         # lead #70: 5 LSB-first 3-byte units + pad byte, per 10 pixels
    out = bytearray()
    for g in range(0, len(vals), 10):
        for a, b in zip(vals[g:g + 10:2], vals[g + 1:g + 10:2]):
            out += bytes([a & 255, a >> 8 | (b & 15) << 4, b >> 4])
        out.append(0)
    return bytes(out)


def pack16(vals, big):     # lead #71: 12-bit << 4 in a u16 word
    return b"".join((v << 4).to_bytes(2, "big" if big else "little") for v in vals)


def rev4(raw):
    return b"".join(raw[i:i + 4][::-1] for i in range(0, len(raw), 4))


class RoundTrip(unittest.TestCase):
    def setUp(self):
        r = random.Random(7)
        self.w = 40
        self.vals = [r.randrange(4096) for _ in range(self.w)]

    def test_packed12_plain(self):
        raw = pack12(self.vals)
        self.assertEqual(len(raw), d.row_bytes("packed-12", self.w))
        out, pad = d.unpack_row("packed-12", "plain", raw, self.w)
        self.assertEqual(list(out), self.vals)

    def test_packed12_word_reversed(self):
        raw = rev4(pack12(self.vals))
        out, _ = d.unpack_row("packed-12", "word4-reversed", raw, self.w)
        self.assertEqual(list(out), self.vals)

    def test_packed128(self):
        raw = pack128(self.vals)
        self.assertEqual(len(raw), d.row_bytes("packed-12.8", self.w))
        out, pad = d.unpack_row("packed-12.8", "lsb", raw, self.w)
        self.assertEqual(list(out), self.vals)
        self.assertEqual(pad, 0)

    def test_packed128_pad_counted(self):
        raw = bytearray(pack128(self.vals))
        raw[15] = 9
        _, pad = d.unpack_row("packed-12.8", "lsb", bytes(raw), self.w)
        self.assertEqual(pad, 1)

    def test_packed16_both_orders(self):
        for big in (False, True):
            raw = pack16(self.vals, big)
            out, _ = d.unpack_row("packed-16", "be" if big else "le", raw, self.w)
            self.assertEqual([v >> 4 for v in out], self.vals)

    def test_widths_rejected(self):
        with self.assertRaises(d.NotSpecified):
            d.row_bytes("packed-12", 3)
        with self.assertRaises(d.NotSpecified):
            d.row_bytes("packed-12.8", 15)
        with self.assertRaises(d.NotSpecified):
            d.row_bytes("nope", 10)


if __name__ == "__main__":
    unittest.main()
