#!/usr/bin/env python3
"""Original synthetic controls and independent direct mean reference."""
import hashlib
import io
import os
import random
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e400_zero_low4_probe as p


def tiff_bytes(words, width, height, endian='<', counts=None, offsets=None):
    # Original minimal TIFF fixture. Two strips in reverse physical order.
    raw = struct.pack(endian + '%dH' % len(words), *words)
    if counts is None:
        counts = [len(raw)]
    if offsets is None:
        offsets = [128]
    tags = [(256, 4, width), (257, 4, height), (258, 3, 16),
            (259, 3, 1), (273, 4, offsets), (279, 4, counts)]
    data = bytearray(256 + len(raw))
    data[:8] = (b'II' if endian == '<' else b'MM') + struct.pack(endian+'HI', 42, 8)
    struct.pack_into(endian+'H', data, 8, len(tags))
    for n, (tag, typ, value) in enumerate(tags):
        values = value if isinstance(value, list) else [value]
        off = 10 + n * 12
        struct.pack_into(endian+'HHI', data, off, tag, typ, len(values))
        packed = struct.pack(endian+('%dH' if typ == 3 else '%dI') % len(values), *values)
        if len(packed) <= 4:
            data[off+8:off+8+len(packed)] = packed
        else:
            loc = 88 if tag == 273 else 104
            struct.pack_into(endian+'I', data, off+8, loc)
            data[loc:loc+len(packed)] = packed
    cursor = 0
    for off, count in zip(offsets, counts):
        data[off:off+count] = raw[cursor:cursor+count]
        cursor += count
    return bytes(data)


class CensusTests(unittest.TestCase):
    def test_constant_and_affine_scene_ambiguity(self):
        for words in ([160] * 99, [16*(2*y+3*x+1) for y in range(9) for x in range(11)]):
            r = p.census(words, 11, 9)
            self.assertEqual(r['interior_words'], 35)
            self.assertEqual(sum(g['zero_low4']['exact_means'] for g in r['strata'].values()), 35)
            self.assertEqual(sum(g['nonzero_low4']['words'] for g in r['strata'].values()), 0)
            self.assertEqual(sum(g['zero_low4_exact_marked_neighbour_histogram']['0'] for g in r['strata'].values()), 35)

    def test_floor_only_and_marked_neighbours(self):
        words = [160] * 81
        words[3*9+3] = 161
        r = p.census(words, 9, 9)
        self.assertEqual(r['strata']['0,0']['zero_low4']['floor_only_means'], 4)
        self.assertEqual(r['strata']['1,1']['nonzero_low4']['nonmatching'], 1)
        # Zero-low4 exact centre with two fractional neighbours cancelling.
        words[5*9+5] = 159
        r = p.census(words, 9, 9)
        self.assertEqual(r['strata']['0,0']['zero_low4_exact_marked_neighbour_histogram']['2'], 1)

    def test_independent_seeded_reference(self):
        rng = random.Random(79)
        for w, h in ((5, 5), (8, 9), (11, 10)):
            words = [rng.randrange(120, 137) for _ in range(w*h)]
            r = p.census(words, w, h)
            for yp in range(2):
                for xp in range(2):
                    group = r['strata']['%d,%d' % (yp, xp)]
                    for marked, key in ((False, 'zero_low4'), (True, 'nonzero_low4')):
                        observed = []
                        hist = [0]*5
                        for y in range(2, h-2):
                            for x in range(2, w-2):
                                v = words[y*w+x]
                                if (y%2, x%2) != (yp, xp) or bool(v%16) != marked:
                                    continue
                                offsets = ((-1,-1), (-1,1), (1,-1), (1,1)) if yp == xp else ((-2,0), (2,0), (0,-2), (0,2))
                                neighbours = [words[(y+dy)*w+x+dx] for dy, dx in offsets]
                                quotient, remainder = divmod(sum(neighbours), 4)
                                status = 'nonmatching' if quotient != v else ('exact_means' if remainder == 0 else 'floor_only_means')
                                observed.append(status)
                                if not marked and status == 'exact_means':
                                    hist[sum(bool(a%16) for a in neighbours)] += 1
                        self.assertEqual(group[key], dict(words=len(observed), **{s:observed.count(s) for s in ('exact_means','floor_only_means','nonmatching')}))
                        if not marked:
                            self.assertEqual(group['zero_low4_exact_marked_neighbour_histogram'], {str(i):v for i,v in enumerate(hist)})

    def test_hash_before_tiff_and_sanitized_cli(self):
        with patch('builtins.open', return_value=io.BytesIO(b'bad')):
            with patch.object(p, 'Tiff') as t:
                with self.assertRaises(ValueError):
                    p.measure('private-name', '0'*64)
                t.assert_not_called()
        with patch.object(sys, 'argv', ['probe', 'private-name', '--sha256', '0'*64]):
            with patch.object(p, 'measure', side_effect=ValueError('private-name')):
                output = io.StringIO()
                with patch('sys.stderr', output):
                    self.assertEqual(p.main(), 1)
                self.assertNotIn('private-name', output.getvalue())

    def test_tiff_orders_gap_and_reverse_strip_order(self):
        for endian in ('<', '>'):
            words = [16*(2*y+3*x+1) for y in range(5) for x in range(7)]
            words[2*7+3] += 1
            expected = p.census(words, 7, 5)
            raw = tiff_bytes(words, 7, 5, endian, [28, 42], [220, 128])
            with patch('builtins.open', return_value=io.BytesIO(raw)):
                r = p.measure('fixture', hashlib.sha256(raw).hexdigest())
            self.assertEqual(r['interior_words'], 3)
            self.assertEqual({k: r[k] for k in expected}, expected)
            self.assertEqual(sum(g['nonzero_low4']['words'] for g in r['strata'].values()), 1)
            swapped = [((v & 255) << 8) | (v >> 8) for v in words]
            self.assertNotEqual(expected, p.census(swapped, 7, 5))
            self.assertNotEqual(expected, p.census(words[14:]+words[:14], 7, 5))
            self.assertEqual(r['byte_order'], 'little' if endian == '<' else 'big')

    def test_rejections_and_boundary_exclusion(self):
        for words,w,h in (([0]*25,4,5), ([0]*24,5,5), ([65536]*25,5,5), ([-1]*25,5,5)):
            with self.assertRaises(ValueError):
                p.census(words,w,h)
        words = [160]*49
        words[0] = 161
        r = p.census(words,7,7)
        self.assertEqual(r['excluded_boundary_words'],40)
        self.assertEqual(sum(g['nonzero_low4']['words'] for g in r['strata'].values()),0)
        for counts,offsets in (([70],[10000]), ([40,30],[128,130]), ([68],[128])):
            raw = tiff_bytes([160]*35,7,5,counts=counts,offsets=offsets)
            with patch('builtins.open',return_value=io.BytesIO(raw)):
                with self.assertRaises(ValueError):
                    p.measure('fixture',hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    unittest.main()
