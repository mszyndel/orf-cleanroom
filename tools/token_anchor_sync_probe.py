#!/usr/bin/env python3
"""Arbitrary-bit-anchor synchronization diagnostic for lead #197.

For each exact logical-payload byte window, restart the candidate q zeros,
stop 1, five suffix bits parser at bit anchors 0..7. Retain only complete
accepted token starts. Report the earliest start shared by all eight paths,
plus counts/q0/endpoints and accepted tokens strictly before that common start.
Once paths meet their futures coincide by determinism; this is not proof of
camera framing. No common accepted start is a censored observation, not zero.
The final unaccepted cursor/end-of-window is never counted as a shared start.

Six models use the existing framing probe's real/Bernoulli/byte/run/Markov/
local-byte256 definitions. Fresh Random(seed) per model; four seeds are not
independent captures or calibrated significance. Reused known-profile files
are exploratory. Every window restarts independently, not a whole-stream parse.
Read-only, stdlib, aggregate JSON only; hashes are checked before TIFF parsing.
"""
import argparse
from array import array
from bisect import bisect_left
import hashlib
import json
import os
import platform
import random
import stat
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_framing_probe as framing
from orf_signature import Tiff, first, size_class

MAX_FILE = 512 * 1024 * 1024
MAX_WINDOW = 1024 * 1024


def path_stats(buf, anchor):
    if anchor not in range(8):
        raise ValueError('invalid bit anchor')
    nbits, pos, q0 = len(buf) * 8, anchor, 0
    starts = array('I')
    while pos + 6 <= nbits:
        stop = pos
        while stop < nbits and not ((buf[stop >> 3] >> (7 - (stop & 7))) & 1):
            stop += 1
        if stop + 6 > nbits:
            break
        starts.append(pos)
        q0 += stop == pos
        pos = stop + 6
    return starts, {'anchor_bit': anchor, 'tokens': len(starts), 'q0_count': q0,
                    'end_bit': pos, 'consumed_from_anchor_bits': pos - anchor,
                    'residual_bits': max(0, nbits - pos)}


def synchronization(buf):
    if not buf or len(buf) > MAX_WINDOW:
        raise ValueError('invalid window length')
    paths = [path_stats(buf, anchor) for anchor in range(8)]
    starts = [path[0] for path in paths]
    indices = [0] * 8
    common = None
    while all(index < len(values) for index, values in zip(indices, starts)):
        target = max(values[index] for index, values in zip(indices, starts))
        indices = [bisect_left(values, target, index)
                   for index, values in zip(indices, starts)]
        if all(index < len(values) and values[index] == target
               for index, values in zip(indices, starts)):
            common = target
            break
    reports = [path[1] for path in paths]
    for values, report in zip(starts, reports):
        report['tokens_before_common'] = (bisect_left(values, common)
                                          if common is not None else None)
    return {'window_bits': len(buf) * 8, 'first_common_accepted_start_bit': common,
            'common_start_observed': common is not None, 'anchors': reports}


def compare(buf, seed):
    p = sum(bin(byte).count('1') for byte in buf) / (len(buf) * 8)
    fit = framing.fit_markov(buf)
    generators = (
        ('real', lambda rng: buf),
        ('bernoulli', lambda rng: framing.bernoulli_bytes(len(buf), p, rng)),
        ('byte_shuffle', lambda rng: framing.byte_shuffle(buf, rng)),
        ('run_shuffle', lambda rng: framing.run_shuffle(buf, rng)),
        ('markov', lambda rng: framing.markov_bytes(len(buf), fit, rng)),
        ('local_byte_shuffle', lambda rng: framing.local_byte_shuffle(buf, 256, rng)))
    return {'seed': seed, 'bernoulli_p': p, 'markov_fit': fit,
            'local_byte_block': 256,
            'models': {name: synchronization(make(random.Random(seed)))
                       for name, make in generators}}


def read_payload(path, expected_hash):
    if not stat.S_ISREG(os.stat(path).st_mode):
        raise ValueError('regular file required')
    with open(path, 'rb') as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError('regular file required')
        data = handle.read(MAX_FILE + 1)
    if len(data) > MAX_FILE or hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError('input hash mismatch or size limit')
    best = max(Tiff(data).all_ifds(), key=lambda tags: sum(tags.get(0x117) or [0]))
    w, h = first(best, 0x100), first(best, 0x101)
    offsets, counts = best.get(0x111) or [], best.get(0x117) or []
    if (not isinstance(w, int) or not isinstance(h, int) or min(w, h) <= 0
            or not offsets or len(offsets) != len(counts)):
        raise ValueError('invalid geometry')
    ranges = sorted(zip(offsets, counts))
    for i, (off, count) in enumerate(ranges):
        if off < 0 or count <= 0 or off + count > len(data):
            raise ValueError('invalid strip bounds')
        if i and ranges[i - 1][0] + ranges[i - 1][1] > off:
            raise ValueError('overlapping strips')
    payload = b''.join(data[off:off + count] for off, count in zip(offsets, counts))
    if first(best, 0x103) != 1 or size_class(len(payload), w, h) != 'variable':
        raise ValueError('variable-size compression-tag1 input required')
    return payload, {'sha256': expected_hash, 'payload_w': w, 'payload_h': h,
                     'payload_bytes': len(payload), 'size_class': 'variable',
                     'compression_tag': 1, 'variant': 'unassigned'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', nargs=4, action='append', required=True,
                        metavar=('ID', 'PUBLIC_NAME', 'VERIFIED_SHA256', 'FILE'))
    parser.add_argument('--bytes', type=int, default=131072)
    parser.add_argument('--offset-bytes', type=int, action='append')
    parser.add_argument('--seed', type=int, action='append')
    args = parser.parse_args(argv)
    offsets = args.offset_bytes if args.offset_bytes is not None else [0, 1048576]
    seeds = args.seed if args.seed is not None else list(range(20261021, 20261025))
    ids = [entry[0] for entry in args.sample]
    if (not 1 <= args.bytes <= MAX_WINDOW or any(off < 0 for off in offsets)
            or len(set(offsets)) != len(offsets) or len(set(seeds)) != len(seeds)):
        parser.error('invalid or duplicate window/seed parameters')
    if (len(set(ids)) != len(ids)
            or any(not sid.isascii() or not sid.isdecimal() or int(sid) <= 0 for sid in ids)
            or any(len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha)
                   for _, _, sha, _ in args.sample)):
        parser.error('distinct positive ASCII IDs and lowercase SHA256 required')
    samples, failed = [], 0
    for sid, name, sha, path in args.sample:
        sample = {'pixls_id': sid, 'pixls_name': name, 'expected_sha256': sha, 'windows': []}
        try:
            payload, metadata = read_payload(path, sha)
            sample.update(metadata)
            for off in offsets:
                record = {'offset_bytes': off, 'start_bit': 8 * off,
                          'requested_bytes': args.bytes}
                if off > len(payload) or args.bytes > len(payload) - off:
                    record.update({'status': 'failed', 'error': 'window_shortfall',
                                   'actual_bytes': max(0, len(payload) - off)})
                    failed += 1
                else:
                    buf = payload[off:off + args.bytes]
                    record.update({'status': 'ok', 'actual_bytes': len(buf),
                                   'replicates': [compare(buf, seed) for seed in seeds]})
                sample['windows'].append(record)
            sample['status'] = 'ok' if all(w['status'] == 'ok' for w in sample['windows']) else 'incomplete'
        except (OSError, ValueError, TypeError, IndexError, KeyError, struct.error):
            sample.update({'status': 'failed', 'error': 'invalid_or_unreadable_input'})
            failed += 1
        samples.append(sample)
    hashes = {}
    for filename in ('token_anchor_sync_probe.py', 'token_framing_probe.py', 'orf_signature.py'):
        with open(os.path.join(os.path.dirname(__file__), filename), 'rb') as source:
            hashes[filename] = hashlib.sha256(source.read()).hexdigest()
    print(json.dumps({'lead': 197, 'complete': failed == 0, 'failure_count': failed,
                      'source_sha256': hashes, 'python_version': platform.python_version(),
                      'samples': samples}, indent=2, sort_keys=True, allow_nan=False))
    return int(failed != 0)


if __name__ == '__main__':
    sys.exit(main())
