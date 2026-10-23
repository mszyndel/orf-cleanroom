#!/usr/bin/env python3
"""Whole-interior arithmetic ambiguity census for lead #79.

Builds on #146/#190/#215/#261. Use diagonal-1 at equal stored-coordinate
parity, axial-2 otherwise, excluding a two-pixel boundary for both. Split
all parity denominators by zero/nonzero low4. Separate exact means from
floor-only means. For zero-low4 exact candidates count marked neighbours.
Candidates can be accidental scene equalities; they do not identify mapped
pixels, processing order, original sensor values or a camera mechanism.
No row-layout transformation, images, preview access or decoder change.
Stdlib only, reads exact packed16 strips and prints aggregate JSON.
"""
import argparse
import array
import hashlib
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, first


def empty_cell():
    return {'words': 0, 'exact_means': 0, 'floor_only_means': 0,
            'nonmatching': 0}


def census(words, width, height):
    if (not isinstance(width, int) or not isinstance(height, int)
            or width < 5 or height < 5 or len(words) != width * height):
        raise ValueError('requires exact dimensions >=5')
    if any(not isinstance(v, int) or not 0 <= v <= 65535 for v in words):
        raise ValueError('requires uint16 words')
    strata = {}
    for yp in range(2):
        for xp in range(2):
            strata['%d,%d' % (yp, xp)] = {
                'family': 'diagonal1' if yp == xp else 'axial2',
                'zero_low4': empty_cell(), 'nonzero_low4': empty_cell(),
                'zero_low4_exact_marked_neighbour_histogram':
                    {str(i): 0 for i in range(5)}}
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            i = y * width + x
            v = words[i]
            if y % 2 == x % 2:
                ns = (i-width-1, i-width+1, i+width-1, i+width+1)
            else:
                ns = (i-2*width, i+2*width, i-2, i+2)
            total = sum(words[j] for j in ns)
            r = total - 4 * v
            group = strata['%d,%d' % (y % 2, x % 2)]
            cell = group['nonzero_low4' if v & 15 else 'zero_low4']
            cell['words'] += 1
            if r == 0:
                cell['exact_means'] += 1
                if not v & 15:
                    count = sum(bool(words[j] & 15) for j in ns)
                    group['zero_low4_exact_marked_neighbour_histogram'][str(count)] += 1
            elif 1 <= r <= 3:
                cell['floor_only_means'] += 1
            else:
                cell['nonmatching'] += 1
    return {'interior_words': (width - 4) * (height - 4),
            'excluded_boundary_words': width * height - (width - 4) * (height - 4),
            'strata': strata}


def measure(path, expected_sha256):
    with open(path, 'rb') as source:
        data = source.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256.lower():
        raise ValueError('input hash mismatch')
    tiff = Tiff(data)
    best = max(tiff.all_ifds(), key=lambda tags: sum(tags.get(0x117) or [0]))
    width, height = first(best, 0x100), first(best, 0x101)
    strips, counts = best.get(0x111) or [], best.get(0x117) or []
    if (not isinstance(width, int) or not isinstance(height, int)
            or width < 5 or height < 5
            or not strips or len(strips) != len(counts)
            or sum(counts) != 2 * width * height
            or first(best, 0x102) != 16 or first(best, 0x103) != 1):
        raise ValueError('requires exact packed16 dimensions/tags/strips')
    ranges = sorted(zip(strips, counts))
    for i, (offset, count) in enumerate(ranges):
        if offset < 0 or count <= 0 or offset + count > len(data):
            raise ValueError('invalid strip bounds')
        if i and ranges[i - 1][0] + ranges[i - 1][1] > offset:
            raise ValueError('overlapping strips')
    payload = b''.join(data[o:o+c] for o, c in zip(strips, counts))
    words = array.array('H')
    if words.itemsize != 2:
        raise ValueError('requires two-byte unsigned short')
    words.frombytes(payload)
    byte_order = 'little' if tiff.e == '<' else 'big'
    if byte_order != sys.byteorder:
        words.byteswap()
    result = census(words, width, height)
    result.update(lead=79, sha256=actual, width=width, height=height,
                  byte_order=byte_order, size_class='packed-16')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='retained CC0/hash-verified packed16 input')
    parser.add_argument('--sha256', required=True, help='retained verified hash')
    args = parser.parse_args()
    try:
        result = measure(args.file, args.sha256)
    except (OSError, ValueError, TypeError, struct.error):
        print('measurement failed: unreadable, hash-mismatched or unsupported input', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
