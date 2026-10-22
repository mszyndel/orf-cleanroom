#!/usr/bin/env python3
"""Disjoint raw-bit lag screening with a discovery-frozen validation lag.

Part of #296. Original stdlib CPU code; no candidate token parser or row claim.
Reads one explicitly bounded byte extent after full-file SHA-256 verification.
Licence/provenance and identification of the extent are caller responsibilities.
Only aggregate JSON is printed. Byte-local shuffles preserve each block's byte
multiset, including within-byte bit structure; they are a diagnostic null, not a
validated camera exchangeability model. No significance or physical rows follow.
"""
import argparse
import hashlib
import json
import math
import random
import sys

POPCOUNT = tuple(bin(i).count('1') for i in range(256))


def popcount(value):
    return sum(POPCOUNT[b] for b in value.to_bytes((value.bit_length()+7)//8, 'big'))


def lag_map(data, lags):
    """MSB-first binary Pearson phi. No pairs cross a window boundary."""
    nbits = len(data)*8
    value = int.from_bytes(data, 'big')
    output = []
    for lag in lags:
        if lag < 1 or lag >= nbits:
            raise ValueError('lag outside window')
        n = nbits-lag
        x = value >> lag
        y = value & ((1 << n)-1)
        a, b, both = popcount(x), popcount(y), popcount(x & y)
        denom2 = a*(n-a)*b*(n-b)
        phi = (n*both-a*b)/math.sqrt(denom2) if denom2 else None
        output.append({'lag_bits': lag, 'pairs': n, 'left_ones': a,
                       'right_ones': b, 'both_ones': both, 'phi': phi})
    return output


def winner(rows):
    valid = [r for r in rows if r['phi'] is not None]
    if not valid:
        return {'lag_bits': None, 'phi': None, 'ties': [], 'range_boundary': None}
    best = max(r['phi'] for r in valid)
    ties = [r['lag_bits'] for r in valid if r['phi'] == best]
    lag = min(ties)
    return {'lag_bits': lag, 'phi': best, 'ties': ties,
            'range_boundary': lag in (rows[0]['lag_bits'], rows[-1]['lag_bits'])}


def shuffle_blocks(data, block_bytes, rng):
    result = bytearray()
    for start in range(0, len(data), block_bytes):
        block = list(data[start:start+block_bytes])
        rng.shuffle(block)
        result.extend(block)
    return bytes(result)


def analyze(payload, starts, window_bytes, lags, replicates=15, block_bytes=64,
            seed=296, absolute_offset=0):
    if window_bytes < 1 or block_bytes < 2 or replicates < 1:
        raise ValueError('invalid window, null block size or replicate count')
    if len(starts) < 2 or starts != sorted(set(starts)):
        raise ValueError('need ordered distinct discovery and validation windows')
    if not lags or lags != sorted(set(lags)):
        raise ValueError('lags must be increasing and distinct')
    for i, start in enumerate(starts):
        if start < 0 or start+window_bytes > len(payload):
            raise ValueError('window outside payload')
        if i and starts[i-1]+window_bytes > start:
            raise ValueError('overlapping windows')
    bands = []
    rng = random.Random(seed)
    selected = None
    for index, start in enumerate(starts):
        data = payload[start:start+window_bytes]
        rows = lag_map(data, lags)
        peak = winner(rows)
        if index == 0:
            selected = peak['lag_bits']
        fixed = next((r['phi'] for r in rows if r['lag_bits']==selected), None)
        maxima, fixed_null = [], []
        for unused in range(replicates):
            nr = lag_map(shuffle_blocks(data, block_bytes, rng), lags)
            maxima.append(winner(nr)['phi'])
            fixed_null.append(next((r['phi'] for r in nr if r['lag_bits']==selected), None))
        bands.append({'role': 'discovery' if index==0 else 'validation',
                      'payload_start_bit': start*8,
                      'absolute_start_bit': (absolute_offset+start)*8,
                      'payload_end_bit_exclusive': (start+window_bytes)*8,
                      'absolute_end_bit_exclusive': (absolute_offset+start+window_bytes)*8,
                      'window_bits': window_bytes*8, 'map': rows, 'winner': peak,
                      'frozen_lag_bits': selected, 'frozen_phi': fixed,
                      'null_search_maxima': maxima, 'null_frozen_phi': fixed_null,
                      'search_max_ge_observed': None if peak['phi'] is None else
                      sum(v is not None and v>=peak['phi'] for v in maxima),
                      'null_undefined_maxima': sum(v is None for v in maxima)})
    return {'method': 'raw-bit-binary-phi-v1', 'selected_from_band': 0,
            'selection': 'maximum signed phi (may be negative); lowest lag breaks exact ties',
            'seed': seed, 'rng': 'Python random.Random MT19937; band-major then replicate-major; shuffle byte lists block-major',
            'python': sys.version.split()[0], 'replicates': replicates,
            'null_block_bytes': block_bytes, 'lags_bits': lags,
            'payload_bytes': len(payload), 'covered_bytes': len(starts)*window_bytes,
            'omitted_bytes': len(payload)-len(starts)*window_bytes, 'bands': bands,
            'limits': 'screening only; sparse windows, overlapping lag pairs; no calibrated p-value, phase/row inference or change-point fit'}


def load_extent(path, expected_sha256, offset, length):
    with open(path, 'rb') as source:
        data = source.read()
    if hashlib.sha256(data).hexdigest() != expected_sha256.lower():
        raise ValueError('SHA-256 mismatch')
    if offset < 0 or length < 1 or offset+length > len(data):
        raise ValueError('invalid payload extent')
    return data[offset:offset+length]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--sample-id', required=True)
    parser.add_argument('--sample-name', required=True)
    parser.add_argument('--offset', type=int, required=True)
    parser.add_argument('--length', type=int, required=True)
    parser.add_argument('--starts', type=int, nargs='+', required=True,
                        help='payload byte offsets; first window discovery, rest validation')
    parser.add_argument('--window-bytes', type=int, default=4096)
    parser.add_argument('--lag-min', type=int, default=120)
    parser.add_argument('--lag-max', type=int, default=200)
    parser.add_argument('--lag-step', type=int, default=1)
    parser.add_argument('--replicates', type=int, default=15)
    parser.add_argument('--block-bytes', type=int, default=64)
    parser.add_argument('--seed', type=int, default=296)
    args = parser.parse_args()
    try:
        if len(args.sha256)!=64 or any(c not in '0123456789abcdefABCDEF' for c in args.sha256):
            raise ValueError('invalid SHA-256')
        if args.lag_step<1 or args.lag_min<1 or args.lag_max<args.lag_min:
            raise ValueError('invalid lag grid')
        payload = load_extent(args.file, args.sha256, args.offset, args.length)
        report = analyze(payload, args.starts, args.window_bytes,
                         list(range(args.lag_min,args.lag_max+1,args.lag_step)),
                         args.replicates,args.block_bytes,args.seed,args.offset)
        report.update({'sample_id':args.sample_id,'sample_name':args.sample_name,
                       'sha256':args.sha256.lower(),'payload_offset':args.offset,
                       'source_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest()})
        print(json.dumps(report,sort_keys=True,allow_nan=False))
        return 0
    except (OSError,ValueError,OverflowError):
        print('error: invalid input, extent, parameters or SHA-256',file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
