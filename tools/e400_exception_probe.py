#!/usr/bin/env python3
"""Bounded neighbour tests for the remaining E-400 exception in lead #79.

Design fixed before this tool's first run, after reading lead #79:
scan every stored packed-16 word in TIFF byte order.
For each nonzero-low-nibble word at least two pixels from every edge, test
axial-2 and diagonal-1 families, every nonempty subset of each family, and
floor / ceiling / nearest-half-up means of stored words. Also test the
floor mean after clearing neighbour low nibbles. Report counts grouped by
low nibble, never individual pixels, neighbourhood arrays or images.

These are descriptive exact-equality tests, with no fitted coefficients or
causal inference. Searching subsets can produce chance matches. This tool
cannot establish the camera's processing order or the origin of a defect.
Supports lead #79 and specs/V0.md G3. Standard library only; read-only.
"""
import argparse
import collections
import itertools
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decoder'))
import orf_decode as od

FAMILIES = {
    'axial2': ((-2, 0), (2, 0), (0, -2), (0, 2)),
    'diagonal1': ((-1, -1), (-1, 1), (1, -1), (1, 1)),
}


def rounded_mean(total, count, mode):
    if mode == 'floor':
        return total // count
    if mode == 'ceiling':
        return (total + count - 1) // count
    if mode == 'nearest_half_up':
        return (2 * total + count) // (2 * count)
    raise ValueError('unknown rounding mode')


def score_word(value, neighbours):
    """Counts candidate subset matches; includes full-family residuals only."""
    result = {}
    for family, values in neighbours.items():
        total = sum(values)
        result[family + '_four_sum_minus_4word'] = total - 4 * value
        result[family + '_nonzero_nibble_neighbours'] = sum(bool(v & 15) for v in values)
        for mode in ('floor', 'ceiling', 'nearest_half_up'):
            for size in range(1, 5):
                key = '%s_%s_subset%d' % (family, mode, size)
                result[key] = sum(rounded_mean(sum(subset), size, mode) == value
                                  for subset in itertools.combinations(values, size))
        result[family + '_cleared_low4_floor'] = sum(v & ~15 for v in values) // 4 == value
    return result


def add_scores(groups, nibble, scored, neighbours):
    """Accumulate a fixed-size summary per low nibble, regardless of word count."""
    group = groups.setdefault(nibble, {'words': 0, 'candidate_matching_words': {},
                                      'full_family_residual_range': {},
                                      'nonzero_neighbour_histograms': {},
                                      'neighbour_low_nibble_histograms': {}})
    group['words'] += 1
    for name, values in neighbours.items():
        hist = group['neighbour_low_nibble_histograms'].setdefault(name, {})
        for value in values:
            key = str(value & 15)
            hist[key] = hist.get(key, 0) + 1
    for key, count in scored.items():
        if key.endswith('_four_sum_minus_4word'):
            bounds = group['full_family_residual_range'].setdefault(key, [count, count])
            bounds[0], bounds[1] = min(bounds[0], count), max(bounds[1], count)
        elif key.endswith('_nonzero_nibble_neighbours'):
            hist = group['nonzero_neighbour_histograms'].setdefault(key, {})
            hist[str(count)] = hist.get(str(count), 0) + 1
        else:
            matches = group['candidate_matching_words']
            matches[key] = matches.get(key, 0) + bool(count)


def measure(path):
    payload = od.Payload(path)
    sig = payload.sig
    if sig['size_class'] != 'packed-16':
        raise ValueError('requires exact packed-16 payload')
    w, h = sig['payload_w'], sig['payload_h']
    if w < 5 or h < 5 or not payload.in_file or payload.nbytes != w * h * 2:
        raise ValueError('invalid packed-16 dimensions or strips')
    order = 'le' if payload.header.startswith('II') else 'be'
    bad = []
    with open(path, 'rb') as source:
        for y in range(h):
            row = od.unpack_row('packed-16', order, payload.read(source, y * w * 2, w * 2), w)[0]
            bad.extend((y, x, v) for x, v in enumerate(row) if v & 15)
        # Bounded row cache: at most five full rows at any one time.
        rows = {}
        grouped = {}
        family_matches = collections.Counter()
        edge = collections.Counter()
        unmatched = {}
        for y, x, value in bad:
            if not (2 <= y < h - 2 and 2 <= x < w - 2):
                edge[str(value & 15)] += 1
                continue
            rows = {yy: row for yy, row in rows.items() if y - 2 <= yy <= y + 2}
            for yy in range(y - 2, y + 3):
                if yy not in rows:
                    rows[yy] = od.unpack_row('packed-16', order,
                        payload.read(source, yy * w * 2, w * 2), w)[0]
            neighbours = {name: [rows[y + dy][x + dx] for dy, dx in offsets]
                          for name, offsets in FAMILIES.items()}
            scored = score_word(value, neighbours)
            a = scored['axial2_floor_subset4'] > 0
            d = scored['diagonal1_floor_subset4'] > 0
            family_matches['both' if a and d else 'axial2' if a else 'diagonal1' if d else 'neither'] += 1
            nibble = str(value & 15)
            if not (a or d):
                add_scores(unmatched, nibble, scored, neighbours)
            add_scores(grouped, nibble, scored, neighbours)
    return {'lead': 79, 'input_sha256': sig['sha256'], 'model': sig['model'],
            'width': w, 'height': h, 'byte_order': order,
            'nonzero_low_nibble_words': len(bad), 'excluded_edge_words': sum(edge.values()),
            'edge_low_nibble_histogram': dict(edge), 'unmatched_interior_by_low_nibble': unmatched,
            'interior_floor_family_counts': dict(family_matches), 'by_low_nibble': grouped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='licence-checked packed-16 ORF')
    args = parser.parse_args()
    try:
        result = measure(args.file)
    except (OSError, ValueError, struct.error, od.NotSpecified):
        print('measurement failed: unreadable or unsupported packed-16 input', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
