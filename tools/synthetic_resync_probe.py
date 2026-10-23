#!/usr/bin/env python3
"""Synthetic perturbation controls for #300; no ORF grammar or camera inference.

Original stateless grammars: fixed4 stores unsigned 0..15 in four MSB-first
bits; rice0/rice2 store q zero bits, one stop bit, then k MSB-first remainder
bits, where value = (q << k) + remainder. There is no adaptive state.

The frozen experiment uses 256 values from an explicitly specified integer LCG,
three original-bit edit anchors (17, 61, 127), flip/insert-one/delete, and 128
original bits of observation after each anchor. Each of three generators is
parsed with all three grammars, including six deliberately nonmatching cells.
All parses start at bit zero. A common boundary is distinct from a run of
three consecutive common token intervals. Distances use original coordinates.
Failure to observe a run is right-censoring, never infinite recovery distance.
No statistical codec classification or confusion matrix is claimed.

Stdlib CPU only. No file reads/writes, network, samples, or image data.
"""
import argparse
import json
import time
import tracemalloc
import unittest

GRAMMARS = ('fixed4', 'rice0', 'rice2')
ANCHORS = (17, 61, 127)
WINDOW = 128
RUN = 3


def values():
    """LCG state starts at 300; update modulo 2**32; take high nibble."""
    state = 300
    out = []
    for _ in range(256):
        state = (1664525 * state + 1013904223) % (1 << 32)
        out.append(state >> 28)
    return out


def encode(data, grammar):
    if grammar not in GRAMMARS:
        raise ValueError('unknown grammar')
    out = []
    for value in data:
        if not 0 <= value < 16:
            raise ValueError('value outside 0..15')
        if grammar == 'fixed4':
            out.append(format(value, '04b'))
        else:
            k = int(grammar[-1])
            out.append('0' * (value >> k) + '1')
            if k:
                out.append(format(value % (1 << k), '0%db' % k))
    return ''.join(out)


def parse(bits, grammar):
    """Return complete (start,end,value) tokens and unconsumed tail length."""
    if grammar not in GRAMMARS or any(b not in '01' for b in bits):
        raise ValueError('invalid grammar/bits')
    tokens = []
    pos = 0
    while pos < len(bits):
        start = pos
        if grammar == 'fixed4':
            end = pos + 4
            if end > len(bits):
                break
            value = int(bits[pos:end], 2)
        else:
            stop = bits.find('1', pos)
            k = int(grammar[-1])
            if stop < 0 or stop + 1 + k > len(bits):
                break
            end = stop + 1 + k
            remainder = int(bits[stop + 1:end], 2) if k else 0
            value = ((stop - pos) << k) + remainder
        tokens.append((start, end, value))
        pos = end
    return tokens, len(bits) - pos


def perturb(bits, anchor, operation):
    if not 0 <= anchor < len(bits):
        raise ValueError('anchor outside stream')
    if operation == 'flip':
        return bits[:anchor] + str(1 - int(bits[anchor])) + bits[anchor + 1:]
    if operation == 'insert':
        return bits[:anchor] + '1' + bits[anchor:]
    if operation == 'delete':
        return bits[:anchor] + bits[anchor + 1:]
    raise ValueError('unknown operation')


def forward(coordinate, anchor, operation):
    """Map original boundaries strictly AFTER edit to perturbed boundaries."""
    if coordinate <= anchor:
        raise ValueError('mapping requires boundary strictly after edit')
    return coordinate + {'flip': 0, 'insert': 1, 'delete': -1}[operation]


def measure(bits, grammar, anchor, operation, window=WINDOW, run=RUN):
    if window < 1 or run < 1:
        raise ValueError('positive window/run required')
    limit = min(len(bits), anchor + window)
    original, tail = parse(bits[:limit], grammar)
    changed_bits = perturb(bits, anchor, operation)
    changed_limit = forward(limit, anchor, operation)
    changed, changed_tail = parse(changed_bits[:changed_limit], grammar)
    changed_by_span = {(s, e): v for s, e, v in changed}
    changed_boundaries = {0} | {e for _, e, _ in changed}
    common = [e for _, e, _ in original if e > anchor and
              forward(e, anchor, operation) in changed_boundaries]
    eligible = [(s, e, v) for s, e, v in original if s > anchor]
    consecutive = 0
    recovery = None
    mismatches = 0
    comparable = 0
    for index, (s, e, value) in enumerate(eligible):
        span = (forward(s, anchor, operation), forward(e, anchor, operation))
        if span in changed_by_span:
            comparable += 1
            mismatches += value != changed_by_span[span]
            consecutive += 1
            if consecutive == run and recovery is None:
                recovery = eligible[index - run + 1][0] - anchor
        else:
            consecutive = 0
    return {
        'first_common_boundary_distance': common[0] - anchor if common else None,
        'sustained_boundary_distance': recovery,
        'right_censored': recovery is None,
        'observed_original_bits': limit - anchor,
        'eof_shortened_window': limit < anchor + window,
        'original_complete_tokens': len(original),
        'changed_complete_tokens': len(changed),
        'original_consumed_bits': limit - tail,
        'changed_consumed_bits': changed_limit - changed_tail,
        'original_tail_bits': tail,
        'changed_tail_bits': changed_tail,
        'comparable_token_spans': comparable,
        'value_mismatches_on_comparable_spans': mismatches,
    }


def experiment():
    rows = []
    for generator in GRAMMARS:
        bits = encode(values(), generator)
        for parser in GRAMMARS:
            for operation in ('flip', 'insert', 'delete'):
                trials = [measure(bits, parser, anchor, operation) for anchor in ANCHORS]
                rows.append({'generator': generator, 'parser': parser,
                             'operation': operation, 'anchors': list(ANCHORS),
                             'recovered': sum(not t['right_censored'] for t in trials),
                             'censored': sum(t['right_censored'] for t in trials),
                             'trials': trials})
    return {'protocol': {'values': 256, 'lcg_seed': 300,
                         'lcg_multiplier': 1664525, 'lcg_increment': 1013904223,
                         'lcg_modulus': 1 << 32, 'value_extraction': 'state >> 28',
                         'window_original_bits': WINDOW, 'run_intervals': RUN,
                         'adaptive_state': 'none; not tested', 'backend': 'stdlib CPU'},
            'rows': rows}


class Tests(unittest.TestCase):
    def test_known_encodings(self):
        self.assertEqual(encode([0, 1, 4, 15], 'fixed4'), '0000000101001111')
        self.assertEqual(encode([0, 1, 4], 'rice0'), '10100001')
        self.assertEqual(encode([0, 1, 4], 'rice2'), '1001010100')

    def test_roundtrip_and_eof(self):
        for grammar in GRAMMARS:
            bits = encode(values(), grammar)
            tokens, tail = parse(bits, grammar)
            self.assertEqual([v for _, _, v in tokens], values())
            self.assertEqual(tail, 0)
        self.assertEqual(parse('000', 'rice0'), ([], 3))
        self.assertEqual(parse('10', 'rice2'), ([], 2))
        self.assertEqual(parse('000', 'fixed4'), ([], 3))

    def test_mapping(self):
        bits = '010110'
        self.assertEqual(perturb(bits, 2, 'flip'), '011110')
        self.assertEqual(perturb(bits, 2, 'insert'), '0110110')
        self.assertEqual(perturb(bits, 2, 'delete'), '01110')
        for operation in ('flip', 'insert', 'delete'):
            changed = perturb(bits, 2, operation)
            for boundary in range(3, len(bits) + 1):
                self.assertEqual(changed[forward(boundary, 2, operation):], bits[boundary:])
        with self.assertRaises(ValueError):
            forward(2, 2, 'delete')

    def test_fixed_phase_and_values(self):
        bits = encode([3] * 40, 'fixed4')
        flip = measure(bits, 'fixed4', 5, 'flip')
        self.assertEqual(flip['first_common_boundary_distance'], 3)
        self.assertEqual(flip['sustained_boundary_distance'], 3)
        self.assertEqual(flip['value_mismatches_on_comparable_spans'], 0)
        for operation in ('insert', 'delete'):
            result = measure(bits, 'fixed4', 5, operation)
            self.assertTrue(result['right_censored'])
            self.assertIsNone(result['first_common_boundary_distance'])

    def test_single_boundary_not_sustained(self):
        result = measure('00010001', 'fixed4', 1, 'flip', window=3)
        self.assertEqual(result['first_common_boundary_distance'], 3)
        self.assertTrue(result['right_censored'])
        self.assertEqual(result['observed_original_bits'], 3)

    def test_eof_censoring(self):
        result = measure('00010001', 'fixed4', 6, 'delete')
        self.assertTrue(result['eof_shortened_window'])
        self.assertTrue(result['right_censored'])
        self.assertEqual(result['observed_original_bits'], 2)
        self.assertEqual(result['changed_tail_bits'], 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='run synthetic regression tests')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    tracemalloc.start()
    start = time.perf_counter()
    report = experiment()
    report['benchmark'] = {'elapsed_seconds': time.perf_counter() - start,
                           'peak_traced_cpu_bytes': tracemalloc.get_traced_memory()[1],
                           'precision': 'exact Python integers; time/memory descriptive only'}
    tracemalloc.stop()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
