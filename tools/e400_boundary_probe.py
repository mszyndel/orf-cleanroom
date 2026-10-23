#!/usr/bin/env python3
"""Fixed boundary-policy comparisons for the untested edge word in lead #79.

Select every nonzero-low4 word within two pixels of a stored-raster boundary.
Test axial-2 and diagonal-1 under available-only, coordinate clamp, and
reflect-without-repeating-edge policies; floor, ceiling and nearest-half-up.
Remapping retains four terms including duplicates. Available-only divides by
the retained count. Clamp may change colour parity: this is only arithmetic.
No row-layout detection, fitting, camera-policy inference or decoder change. Builds on
#79/#146/#190/#215. Stdlib; reads exact packed-16, prints aggregates only.
"""
import argparse
import hashlib
import json
import os
import struct
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decoder'))
import orf_decode as od

FAMILIES = {'axial2': ((-2, 0), (2, 0), (0, -2), (0, 2)),
            'diagonal1': ((-1, -1), (-1, 1), (1, -1), (1, 1))}
POLICIES = ('available', 'clamp', 'reflect')
MODES = ('floor', 'ceiling', 'nearest_half_up')


def coordinate(i, size, policy):
    if size < 1:
        raise ValueError('empty axis')
    if policy == 'available':
        return i if 0 <= i < size else None
    if policy == 'clamp':
        return min(size - 1, max(0, i))
    if policy == 'reflect':
        if size == 1:
            return 0
        j = i % (2 * (size - 1))
        return j if j < size else 2 * (size - 1) - j
    raise ValueError('unknown policy')


def positions(y, x, h, w, family, policy):
    result = []
    for dy, dx in FAMILIES[family]:
        yy, xx = coordinate(y + dy, h, policy), coordinate(x + dx, w, policy)
        if yy is not None and xx is not None:
            result.append((yy, xx))
    return result


def empty_group():
    return {'words': 0, 'unsupported_words': 0, 'denominator_histogram': {},
            'sum_minus_count_word_range': None,
            'rounding': {m: {'matches': 0, 'prediction_minus_word_range': None} for m in MODES}}


def extend(bounds, value):
    return [value, value] if bounds is None else [min(bounds[0], value), max(bounds[1], value)]


def add(group, value, total, count):
    group['words'] += 1
    key = str(count)
    group['denominator_histogram'][key] = group['denominator_histogram'].get(key, 0) + 1
    if not count:
        group['unsupported_words'] += 1
        return
    key = 'sum_minus_count_word_range'
    group[key] = extend(group[key], total - count * value)
    predictions = (total // count, (total + count - 1) // count, (2 * total + count) // (2 * count))
    for mode, prediction in zip(MODES, predictions):
        cell = group['rounding'][mode]
        difference = prediction - value
        cell['matches'] += difference == 0
        key = 'prediction_minus_word_range'
        cell[key] = extend(cell[key], difference)


def measure(path, expected_sha256):
    digest = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1048576), b''):
            digest.update(chunk)
    if digest.hexdigest() != expected_sha256.lower():
        raise ValueError('input hash mismatch')
    payload = od.Payload(path)
    sig = payload.sig
    w, h = sig['payload_w'], sig['payload_h']
    if (sig['size_class'] != 'packed-16' or w < 5 or h < 5 or not payload.in_file
            or payload.nbytes != 2 * w * h):
        raise ValueError('requires exact packed-16 dimensions and strips')
    order = 'le' if payload.header.startswith('II') else 'be'
    groups, nonzero, edge = {}, 0, 0
    with open(path, 'rb') as source:
        rows = {}
        def row(y):
            if y not in rows:
                raw = payload.read(source, y * w * 2, w * 2)
                if len(raw) != w * 2:
                    raise ValueError('short row')
                rows[y] = od.unpack_row('packed-16', order, raw, w)[0]
            return rows[y]
        for y in range(h):
            rows = {yy: values for yy, values in rows.items() if y - 2 <= yy <= y + 2}
            for x, value in enumerate(row(y)):
                if not value & 15:
                    continue
                nonzero += 1
                if 2 <= y < h - 2 and 2 <= x < w - 2:
                    continue
                edge += 1
                for family in FAMILIES:
                    for policy in POLICIES:
                        pts = positions(y, x, h, w, family, policy)
                        total = sum(row(yy)[xx] for yy, xx in pts)
                        group = groups.setdefault(str(value & 15), {}).setdefault(family, {}).setdefault(policy, empty_group())
                        add(group, value, total, len(pts))
    return {'lead': 79, 'sha256': digest.hexdigest(), 'width': w, 'height': h,
            'byte_order': order, 'nonzero_low4_words': nonzero,
            'boundary_nonzero_low4_words': edge, 'by_low4': groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='previously CC0/hash-verified packed-16 ORF')
    parser.add_argument('--sha256', required=True, help='retained verified input hash')
    args = parser.parse_args()
    try:
        result = measure(args.file, args.sha256)
    except (OSError, ValueError, struct.error, od.NotSpecified):
        print('measurement failed: unreadable, hash-mismatched or unsupported input', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
