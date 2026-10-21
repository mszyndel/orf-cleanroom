#!/usr/bin/env python3
"""Corrected k=5 q0 null comparison for lead #197, building on PR #198.

The bounded q+stop+5 parser is a candidate grammar, not established symbols.
Short residuals are diagnostics only. Bernoulli draws use the measured prefix
ones fraction as p (density is preserved in expectation, not exactly).
Byte shuffling preserves the exact byte histogram. Run shuffling independently
permutes zero-run and one-run lengths, retaining their alternating value order,
first/last values and exact per-value maximal-run length multisets. Neither null
preserves all local statistics or proves entropy-code boundaries.

Read-only, stdlib, aggregate JSON only; no paths or exception text are emitted.
Every input has an explicit success/failure record. Any failure exits nonzero
and the enclosing report is marked incomplete. Each model resets the seeded
Python random.Random generator; record Python version for seeded reruns.
"""
import argparse
import hashlib
import json
import os
import platform
import random
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, first, size_class


def bit_list(buf):
    return [(byte >> k) & 1 for byte in buf for k in range(7, -1, -1)]


def pack_bits(bits):
    if len(bits) % 8:
        raise ValueError('requires a whole number of bytes')
    out = bytearray(len(bits) // 8)
    for i, bit in enumerate(bits):
        out[i >> 3] |= bit << (7 - (i & 7))
    return bytes(out)


def runs(buf):
    out = []
    for bit in bit_list(buf):
        if out and out[-1][0] == bit:
            out[-1] = (bit, out[-1][1] + 1)
        else:
            out.append((bit, 1))
    return out


def bernoulli_bytes(nbytes, p, rng):
    if nbytes < 0 or not 0 <= p <= 1:
        raise ValueError('invalid Bernoulli parameters')
    return pack_bits([int(rng.random() < p) for _ in range(nbytes * 8)])


def byte_shuffle(buf, rng):
    out = bytearray(buf)
    rng.shuffle(out)
    return bytes(out)


def run_shuffle(buf, rng):
    source = runs(buf)
    lengths = {v: [length for bit, length in source if bit == v] for v in (0, 1)}
    for v in (0, 1):
        rng.shuffle(lengths[v])
    positions = {0: 0, 1: 0}
    out = []
    for bit, _ in source:
        out.extend([bit] * lengths[bit][positions[bit]])
        positions[bit] += 1
    return pack_bits(out)


def parse_stats(buf):
    nbits, pos, tokens, q0 = len(buf) * 8, 0, 0, 0
    while pos + 6 <= nbits:
        stop = pos
        while stop < nbits and not ((buf[stop >> 3] >> (7 - (stop & 7))) & 1):
            stop += 1
        if stop + 6 > nbits:
            break
        tokens += 1
        q0 += stop == pos
        pos = stop + 6
    ones = sum(bin(byte).count('1') for byte in buf)
    return {'bits': nbits, 'ones_count': ones,
            'ones_fraction': ones / nbits if nbits else None,
            'tokens': tokens, 'q0_count': q0,
            'q0_fraction': q0 / tokens if tokens else None,
            'consumed_bits': pos, 'residual_bits': nbits - pos}


def compare_prefix(prefix, seed):
    if not prefix:
        raise ValueError('empty payload prefix')
    p = sum(bin(byte).count('1') for byte in prefix) / (len(prefix) * 8)
    generators = (
        ('real', lambda rng: prefix),
        ('bernoulli', lambda rng: bernoulli_bytes(len(prefix), p, rng)),
        ('byte_shuffle', lambda rng: byte_shuffle(prefix, rng)),
        ('run_shuffle', lambda rng: run_shuffle(prefix, rng)))
    return {'bernoulli_p': p, 'prefix_bytes': len(prefix),
            'models': {name: parse_stats(make(random.Random(seed)))
                       for name, make in generators}}


def measure(path, nbytes, seed):
    if nbytes <= 0:
        raise ValueError('nonpositive prefix length')
    with open(path, 'rb') as source:
        data = source.read()
    tiff = Tiff(data)
    best = max(tiff.all_ifds(), key=lambda tags: sum(tags.get(0x117) or [0]))
    width, height = first(best, 0x100), first(best, 0x101)
    offsets, counts = best.get(0x111) or [], best.get(0x117) or []
    if not isinstance(width, int) or not isinstance(height, int) or min(width, height) <= 0:
        raise ValueError('invalid dimensions')
    if not offsets or len(offsets) != len(counts):
        raise ValueError('invalid strip tables')
    ranges = sorted(zip(offsets, counts))
    for i, (offset, count) in enumerate(ranges):
        if offset < 0 or count <= 0 or offset + count > len(data):
            raise ValueError('invalid strip bounds')
        if i and ranges[i - 1][0] + ranges[i - 1][1] > offset:
            raise ValueError('overlapping strips')
    payload = b''.join(data[offset:offset + count] for offset, count in zip(offsets, counts))
    result = compare_prefix(payload[:nbytes], seed)
    result.update({'input_sha256': hashlib.sha256(data).hexdigest(),
                   'width': width, 'height': height, 'payload_bytes': len(payload),
                   'compression_tag': first(best, 0x103),
                   'size_class': size_class(len(payload), width, height),
                   'requested_prefix_bytes': nbytes})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', nargs=3, action='append', required=True,
                        metavar=('ID', 'PUBLIC_NAME', 'PATH'))
    parser.add_argument('--bytes', type=int, default=131072)
    parser.add_argument('--seed', type=int, default=20261021)
    args = parser.parse_args(argv)
    if args.bytes <= 0:
        parser.error('--bytes must be positive')
    ids = [sid for sid, _, _ in args.sample]
    if any(not sid.isascii() or not sid.isdigit() or int(sid) <= 0 for sid in ids):
        parser.error('sample IDs must be positive ASCII integers')
    if len(set(ids)) != len(ids):
        parser.error('duplicate sample IDs')
    samples, failures = [], 0
    for sid, name, path in args.sample:
        record = {'pixls_id': sid, 'pixls_name': name}
        try:
            record.update(measure(path, args.bytes, args.seed))
            record['status'] = 'ok'
        except (OSError, ValueError, TypeError, IndexError, KeyError, struct.error):
            failures += 1
            record.update({'status': 'failed', 'error': 'unreadable or invalid TIFF payload'})
        samples.append(record)
    print(json.dumps({'lead': 197, 'seed': args.seed, 'python_version': platform.python_version(),
                      'complete': failures == 0, 'input_count': len(samples),
                      'success_count': len(samples) - failures,
                      'failure_count': failures, 'samples': samples}, indent=2, sort_keys=True))
    return int(failures != 0)


if __name__ == '__main__':
    sys.exit(main())
