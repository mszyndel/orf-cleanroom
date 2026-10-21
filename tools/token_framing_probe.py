#!/usr/bin/env python3
"""Corrected k=5 q0 null comparison for lead #197, building on PR #198.

The bounded q+stop+5 parser is a candidate grammar, not established symbols.
Short residuals are diagnostics only. Bernoulli draws use the measured prefix
ones fraction as p (density is preserved in expectation, not exactly).
Byte shuffling preserves the exact byte histogram. Run shuffling independently
permutes zero-run and one-run lengths, retaining their alternating value order,
first/last values and exact per-value maximal-run length multisets. Neither null
preserves all local statistics or proves entropy-code boundaries.

Optional --markov fits adjacent-bit transition probabilities without wraparound
or pseudocounts, starts with measured ones probability p and falls back to p for
a state without outgoing observations. Its finite generated counts, density and
run histograms are not preserved exactly; no stationarity assumption is made.

Optional --local-byte-block shuffles bytes independently inside consecutive
fixed-size prefix blocks (including the final short block). This preserves each
block's exact byte histogram and ones density, but not within-block ordering,
bit adjacency or maximal runs. Blocks are diagnostic windows, not camera rows.

Optional --offset-bytes selects an exact-length window of the logical strip payload.
The parser restarts at window bit zero; all nulls fit that window independently.
This anchor is not an established whole-stream token boundary. A short requested
window fails before any model statistics, including at the default zero offset.

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


def local_byte_shuffle(buf, block_bytes, rng):
    if block_bytes <= 0:
        raise ValueError('nonpositive byte block size')
    return b''.join(byte_shuffle(buf[start:start + block_bytes], rng)
                    for start in range(0, len(buf), block_bytes))


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


def fit_markov(buf):
    bits = bit_list(buf)
    if not bits:
        raise ValueError('empty Markov input')
    counts = [[0, 0], [0, 0]]
    for previous, following in zip(bits, bits[1:]):
        counts[previous][following] += 1
    p = sum(bits) / len(bits)
    outgoing = [sum(row) for row in counts]
    return {'transition_counts': counts, 'initial_one_probability': p,
            'next_one_probabilities': [counts[v][1] / outgoing[v] if outgoing[v] else p
                                       for v in (0, 1)],
            'fallback_states': [v for v in (0, 1) if not outgoing[v]]}


def markov_bytes(nbytes, fit, rng):
    if nbytes < 0:
        raise ValueError('negative Markov output length')
    if not nbytes:
        return b''
    bits = [int(rng.random() < fit['initial_one_probability'])]
    for _ in range(nbytes * 8 - 1):
        p = fit['next_one_probabilities'][bits[-1]]
        bits.append(int(rng.random() < p))
    return pack_bits(bits)


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


def compare_prefix(prefix, seed, include_markov=False, local_byte_block=None):
    if not prefix:
        raise ValueError('empty payload prefix')
    p = sum(bin(byte).count('1') for byte in prefix) / (len(prefix) * 8)
    generators = (
        ('real', lambda rng: prefix),
        ('bernoulli', lambda rng: bernoulli_bytes(len(prefix), p, rng)),
        ('byte_shuffle', lambda rng: byte_shuffle(prefix, rng)),
        ('run_shuffle', lambda rng: run_shuffle(prefix, rng)))
    result = {'bernoulli_p': p, 'prefix_bytes': len(prefix),
              'models': {name: parse_stats(make(random.Random(seed)))
                         for name, make in generators}}
    if include_markov:
        fit = fit_markov(prefix)
        result['markov_fit'] = fit
        result['models']['markov'] = parse_stats(markov_bytes(len(prefix), fit, random.Random(seed)))
    if local_byte_block is not None:
        result['models']['local_byte_shuffle'] = parse_stats(
            local_byte_shuffle(prefix, local_byte_block, random.Random(seed)))
        result['local_byte_shuffle'] = {
            'block_bytes': local_byte_block,
            'complete_blocks': len(prefix) // local_byte_block,
            'tail_bytes': len(prefix) % local_byte_block}
    return result


class WindowShortfall(ValueError):
    def __init__(self, offset, requested, payload_bytes):
        super().__init__('requested window exceeds payload')
        self.window = {'offset_bytes': offset, 'requested_bytes': requested,
                       'actual_bytes': max(0, payload_bytes - offset),
                       'payload_bytes': payload_bytes,
                       'shortfall_bytes': requested - max(0, payload_bytes - offset)}


def measure(path, nbytes, seed, include_markov=False, local_byte_block=None, offset_bytes=0):
    if nbytes <= 0:
        raise ValueError('nonpositive window length')
    if offset_bytes < 0:
        raise ValueError('negative window offset')
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
    if offset_bytes > len(payload) or nbytes > len(payload) - offset_bytes:
        raise WindowShortfall(offset_bytes, nbytes, len(payload))
    window = payload[offset_bytes:offset_bytes + nbytes]
    result = compare_prefix(window, seed, include_markov=include_markov,
                            local_byte_block=local_byte_block)
    result.update({'input_sha256': hashlib.sha256(data).hexdigest(),
                   'width': width, 'height': height, 'payload_bytes': len(payload),
                   'compression_tag': first(best, 0x103),
                   'size_class': size_class(len(payload), width, height),
                   'requested_prefix_bytes': nbytes,
                   'window': {'offset_bytes': offset_bytes, 'start_bit': 8 * offset_bytes,
                              'end_bit_exclusive': 8 * (offset_bytes + nbytes),
                              'requested_bytes': nbytes, 'actual_bytes': len(window),
                              'parser_origin': 'window_bit_zero'}})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', nargs=3, action='append', required=True,
                        metavar=('ID', 'PUBLIC_NAME', 'PATH'))
    parser.add_argument('--bytes', type=int, default=131072)
    parser.add_argument('--offset-bytes', type=int, default=0,
                        help='byte offset in logical strip payload; restart parsing at window bit zero')
    parser.add_argument('--seed', type=int, default=20261021)
    parser.add_argument('--markov', action='store_true',
                        help='also compare a fitted first-order binary Markov null')
    parser.add_argument('--local-byte-block', type=int,
                        help='also shuffle bytes within fixed-size prefix blocks')
    args = parser.parse_args(argv)
    if args.bytes <= 0:
        parser.error('--bytes must be positive')
    if args.offset_bytes < 0:
        parser.error('--offset-bytes must be nonnegative')
    if args.local_byte_block is not None and args.local_byte_block <= 0:
        parser.error('--local-byte-block must be positive')
    ids = [sid for sid, _, _ in args.sample]
    if any(not sid.isascii() or not sid.isdigit() or int(sid) <= 0 for sid in ids):
        parser.error('sample IDs must be positive ASCII integers')
    if len(set(ids)) != len(ids):
        parser.error('duplicate sample IDs')
    samples, failures = [], 0
    for sid, name, path in args.sample:
        record = {'pixls_id': sid, 'pixls_name': name,
                  'requested_window': {'offset_bytes': args.offset_bytes, 'bytes': args.bytes}}
        try:
            record.update(measure(path, args.bytes, args.seed, include_markov=args.markov,
                                  local_byte_block=args.local_byte_block, offset_bytes=args.offset_bytes))
            record['status'] = 'ok'
        except WindowShortfall as shortfall:
            failures += 1
            record.update({'status': 'failed', 'error': 'requested window exceeds payload',
                           'window': shortfall.window})
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
