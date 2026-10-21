#!/usr/bin/env python3
"""Measure high12 quantization and neighbour reconstruction for lead #79.

Read-only, stdlib, aggregate output only. Design fixed before first run:
clear the low four bits of every packed-16 word; count the exact losses.
At nonzero-low-nibble words two pixels from all edges, compare axial-2 and
diagonal-1 four-neighbour means before and after dropping neighbour low4.
Report separately the exact stored-word and high12-only equality tests.
Uses TIFF byte order, not a fitted order. No original sensor value, camera
processing order, universal rule, or decoder change is established.
Builds on #79 and its floor-mean finding; supports its high12 Next step.
"""
import argparse
import collections
import hashlib
import json
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, first

FAMILIES = {
    'axial2': ((-2, 0), (2, 0), (0, -2), (0, 2)),
    'diagonal1': ((-1, -1), (-1, 1), (1, -1), (1, 1)),
}


def compare(value, neighbours):
    """Return integer tests; differences are prediction minus stored word."""
    full = sum(neighbours) // 4
    from_high12 = 4 * sum(n >> 4 for n in neighbours)
    return {
        'full_mean_equals_word': full == value,
        'high12_mean_equals_high12': sum(n >> 4 for n in neighbours) // 4 == value >> 4,
        'high12_neighbours_mean_equals_word': from_high12 == value,
        'high12_neighbours_mean_minus_word': from_high12 - value,
    }


def summarize(words, width, height):
    if width < 5 or height < 5 or len(words) != width * height:
        raise ValueError('requires at least 5x5 exact packed-16 words')
    losses = collections.Counter(v & 15 for v in words)
    families = {name: {'tested': 0, 'full_mean_equals_word': 0,
                      'high12_mean_equals_high12': 0,
                      'high12_neighbours_mean_equals_word': 0,
                      'among_full_mean_matches': {
                          'tested': 0, 'high12_mean_equals_high12': 0,
                          'high12_neighbours_mean_equals_word': 0,
                          'prediction_minus_word_histogram': {}}}
                for name in FAMILIES}
    edges = 0
    for pos, value in enumerate(words):
        if not value & 15:
            continue
        y, x = divmod(pos, width)
        if not (2 <= y < height - 2 and 2 <= x < width - 2):
            edges += 1
            continue
        for name, offsets in FAMILIES.items():
            neighbours = [words[(y + dy) * width + x + dx] for dy, dx in offsets]
            result = compare(value, neighbours)
            group = families[name]
            group['tested'] += 1
            for key in ('full_mean_equals_word', 'high12_mean_equals_high12',
                        'high12_neighbours_mean_equals_word'):
                group[key] += result[key]
            if result['full_mean_equals_word']:
                matched = group['among_full_mean_matches']
                matched['tested'] += 1
                for key in ('high12_mean_equals_high12', 'high12_neighbours_mean_equals_word'):
                    matched[key] += result[key]
                hist = matched['prediction_minus_word_histogram']
                delta = str(result['high12_neighbours_mean_minus_word'])
                hist[delta] = hist.get(delta, 0) + 1
    return {'words': len(words), 'changed_by_clearing_low4': len(words) - losses[0],
            'cleared_low4_loss_histogram': {str(k): v for k, v in sorted(losses.items())},
            'sum_lost_stored_units': sum(k * v for k, v in losses.items()),
            'excluded_edge_nonzero_words': edges, 'families': families}


def measure(path):
    with open(path, 'rb') as source:
        data = source.read()
    tiff = Tiff(data)
    best = max(tiff.all_ifds(), key=lambda tags: sum(tags.get(0x117) or [0]))
    width, height = first(best, 0x100), first(best, 0x101)
    offsets, counts = best.get(0x111) or [], best.get(0x117) or []
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError('invalid dimensions')
    if not offsets or len(offsets) != len(counts) or sum(counts) != 2 * width * height:
        raise ValueError('requires exact packed-16 strip total')
    ranges = sorted(zip(offsets, counts))
    for i, (offset, count) in enumerate(ranges):
        if offset < 0 or count <= 0 or offset + count > len(data):
            raise ValueError('out-of-file strip')
        if i and ranges[i - 1][0] + ranges[i - 1][1] > offset:
            raise ValueError('overlapping strips')
    payload = b''.join(data[offset:offset + count] for offset, count in zip(offsets, counts))
    words = [v[0] for v in struct.iter_unpack(tiff.e + 'H', payload)]
    result = summarize(words, width, height)
    result.update({'lead': 79, 'input_sha256': hashlib.sha256(data).hexdigest(),
                   'width': width, 'height': height, 'size_class': 'packed-16',
                   'byte_order': 'little' if tiff.e == '<' else 'big'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    args = parser.parse_args()
    try:
        result = measure(args.file)
    except (OSError, ValueError, TypeError, struct.error):
        print('measurement failed: unsupported or unreadable packed-16 input', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
