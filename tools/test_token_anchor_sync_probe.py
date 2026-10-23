#!/usr/bin/env python3
"""Original CPU reference and synthetic tests for the #197 anchor diagnostic."""
import contextlib
import hashlib
import io
import json
import os
import random
import struct
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_anchor_sync_probe as probe


def reference(buf):
    bits = ''.join(format(value, '08b') for value in buf)
    paths = []
    for anchor in range(8):
        starts, pos, q0 = [], anchor, 0
        while True:
            stop = bits.find('1', pos)
            if stop < 0 or stop + 6 > len(bits):
                break
            starts.append(pos)
            q0 += stop == pos
            pos = stop + 6
        paths.append((starts, pos, q0))
    common_set = set(paths[0][0]).intersection(*(set(path[0]) for path in paths[1:]))
    common = min(common_set) if common_set else None
    return common, paths


def fixture(endian='<'):
    data = (b'II' if endian == '<' else b'MM') + struct.pack(endian + 'HIH', 42, 8, 5)
    for tag, value in ((256, 1), (257, 1), (259, 1), (273, 74), (279, 8)):
        data += struct.pack(endian + 'HHII', tag, 4, 1, value)
    return data + struct.pack(endian + 'I', 0) + b'\x84' * 8


class FixtureBytes(io.BytesIO):
    def fileno(self):
        return 0


class AnchorTests(unittest.TestCase):
    def assert_reference(self, buf):
        actual = probe.synchronization(buf)
        common, paths = reference(buf)
        self.assertEqual(actual['first_common_accepted_start_bit'], common)
        self.assertEqual(actual['common_start_observed'], common is not None)
        for anchor, ((starts, pos, q0), row) in enumerate(zip(paths, actual['anchors'])):
            self.assertEqual(row, {'anchor_bit': anchor, 'tokens': len(starts), 'q0_count': q0,
                                  'end_bit': pos, 'consumed_from_anchor_bits': pos - anchor,
                                  'residual_bits': len(buf) * 8 - pos,
                                  'tokens_before_common': (sum(s < common for s in starts)
                                                           if common is not None else None)})

    def test_independent_string_parser_all_bytes_and_seeded_longer_inputs(self):
        for value in range(256):
            self.assert_reference(bytes([value]))
        rng = random.Random(721)
        for size in (2, 3, 8, 31, 128):
            for _ in range(20):
                self.assert_reference(bytes(rng.randrange(256) for _ in range(size)))

    def test_no_common_on_fixed_length_ones_and_empty_paths(self):
        for source in (b'\xff' * 24, b'\x00' * 24, b'\x01'):
            result = probe.synchronization(source)
            self.assertIsNone(result['first_common_accepted_start_bit'])
            self.assertFalse(result['common_start_observed'])
            self.assertTrue(all(row['tokens_before_common'] is None for row in result['anchors']))
        self.assertTrue(all(row['tokens'] == 0 for row in probe.synchronization(b'\x01')['anchors']))

    def test_long_zero_prefix_gives_known_shared_start_and_deterministic_future(self):
        # Every anchor's first token stops at bit16 and ends at22. Start22
        # is accepted by every path because a further token fits there.
        source = b'\x00\x00\xff\xff'
        result = probe.synchronization(source)
        self.assertEqual(result['first_common_accepted_start_bit'], 22)
        self.assertTrue(all(row['tokens_before_common'] == 1 for row in result['anchors']))
        paths = [list(probe.path_stats(source, anchor)[0]) for anchor in range(8)]
        suffixes = [values[values.index(22):] for values in paths]
        self.assertTrue(all(values == suffixes[0] for values in suffixes))

    def test_unaccepted_common_endpoint_is_not_common_start(self):
        # All first tokens end at22 but no complete token starts there.
        result = probe.synchronization(b'\x00\x00\x80')
        self.assertEqual([row['end_bit'] for row in result['anchors']], [22] * 8)
        self.assertIsNone(result['first_common_accepted_start_bit'])

    def test_models_match_independent_reference_and_each_seed_is_reset(self):
        source = bytes(range(64))
        for seed in (7, 8):
            result = probe.compare(source, seed)
            p = sum(bin(b).count('1') for b in source) / (len(source) * 8)
            generators = {'real': lambda rng: source,
                          'bernoulli': lambda rng: probe.framing.bernoulli_bytes(len(source), p, rng),
                          'byte_shuffle': lambda rng: probe.framing.byte_shuffle(source, rng),
                          'run_shuffle': lambda rng: probe.framing.run_shuffle(source, rng),
                          'markov': lambda rng: probe.framing.markov_bytes(len(source), probe.framing.fit_markov(source), rng),
                          'local_byte_shuffle': lambda rng: probe.framing.local_byte_shuffle(source, 256, rng)}
            for name, generate in generators.items():
                buf = generate(random.Random(seed))
                self.assertEqual(result['models'][name], probe.synchronization(buf))
                self.assert_reference(buf)
            self.assertEqual(result, probe.compare(source, seed))

    def test_hash_before_tiff_and_byte_orders(self):
        for endian in ('<', '>'):
            data = fixture(endian)
            with patch.object(probe.os, 'stat') as stat, patch('builtins.open', return_value=FixtureBytes(data)), patch.object(probe.os, 'fstat') as fstat:
                stat.return_value.st_mode = fstat.return_value.st_mode = 0o100644
                with patch.object(probe, 'Tiff') as tiff:
                    with self.assertRaises(ValueError):
                        probe.read_payload('fixture', '0' * 64)
                    tiff.assert_not_called()
            with patch.object(probe.os, 'stat') as stat, patch('builtins.open', return_value=FixtureBytes(data)), patch.object(probe.os, 'fstat') as fstat:
                stat.return_value.st_mode = fstat.return_value.st_mode = 0o100644
                payload, metadata = probe.read_payload('fixture', hashlib.sha256(data).hexdigest())
            self.assertEqual(payload, b'\x84' * 8)
            self.assertEqual(metadata['payload_bytes'], 8)

    def test_cli_complete_short_and_mixed_failures_retained_sanitized(self):
        def read(path, sha):
            if path == 'PRIVATE_BAD':
                raise ValueError('PRIVATE_MESSAGE')
            return b'\x84' * 8, {'payload_bytes': 8}
        output = io.StringIO()
        with patch.object(probe, 'read_payload', side_effect=read), contextlib.redirect_stdout(output):
            status = probe.main(['--bytes', '4', '--offset-bytes', '0', '--offset-bytes', '6', '--seed', '7',
                                 '--sample', '1', 'public-good', '0' * 64, 'PRIVATE_GOOD',
                                 '--sample', '2', 'public-bad', '1' * 64, 'PRIVATE_BAD'])
        report = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertFalse(report['complete'])
        self.assertEqual(report['failure_count'], 2)
        self.assertEqual(report['samples'][0]['status'], 'incomplete')
        self.assertEqual(report['samples'][0]['windows'][0]['status'], 'ok')
        self.assertEqual(report['samples'][0]['windows'][1]['actual_bytes'], 2)
        self.assertEqual(report['samples'][1]['status'], 'failed')
        self.assertNotIn('PRIVATE', output.getvalue())

    def test_multistrip_logical_order_gaps_and_cross_window(self):
        for endian in ('<', '>'):
            data = bytearray(110)
            data[:10] = (b'II' if endian == '<' else b'MM') + struct.pack(endian + 'HIH', 42, 8, 5)
            for index, (tag, count, value) in enumerate(
                    ((256, 1, 1), (257, 1, 1), (259, 1, 1), (273, 2, 74), (279, 2, 82))):
                struct.pack_into(endian + 'HHII', data, 10 + 12 * index, tag, 4, count, value)
            struct.pack_into(endian + 'II', data, 74, 106, 90)
            struct.pack_into(endian + 'II', data, 82, 4, 4)
            data[90:94], data[94:106], data[106:110] = b'wxyz', b'GAPGAPGAPGAP', b'ABCD'
            with patch.object(probe.os, 'stat') as stat, patch('builtins.open', return_value=FixtureBytes(data)), patch.object(probe.os, 'fstat') as fstat:
                stat.return_value.st_mode = fstat.return_value.st_mode = 0o100644
                payload, metadata = probe.read_payload('fixture', hashlib.sha256(data).hexdigest())
            self.assertEqual(payload, b'ABCDwxyz')
            self.assertEqual(metadata['payload_bytes'], 8)
            self.assertEqual(probe.compare(payload[2:6], 7), probe.compare(b'CDwx', 7))
            # Overlap physical ranges despite valid bounds.
            struct.pack_into(endian + 'II', data, 74, 92, 90)
            with patch.object(probe.os, 'stat') as stat, patch('builtins.open', return_value=FixtureBytes(data)), patch.object(probe.os, 'fstat') as fstat:
                stat.return_value.st_mode = fstat.return_value.st_mode = 0o100644
                with self.assertRaises(ValueError):
                    probe.read_payload('fixture', hashlib.sha256(data).hexdigest())

    def test_wrong_compression_and_fixed_packing_rejected(self):
        for compression, width in ((2, 1), (1, 4)):
            data = bytearray(fixture())
            struct.pack_into('<I', data, 18, width)
            struct.pack_into('<I', data, 42, compression)
            with patch.object(probe.os, 'stat') as stat, patch('builtins.open', return_value=FixtureBytes(data)), patch.object(probe.os, 'fstat') as fstat:
                stat.return_value.st_mode = fstat.return_value.st_mode = 0o100644
                with self.assertRaises(ValueError):
                    probe.read_payload('fixture', hashlib.sha256(data).hexdigest())

    def test_validation_before_reads(self):
        base = ['--sample', '1', 'public', '0' * 64, 'unused']
        for extra in (['--bytes', '0'], ['--offset-bytes', '-1'], ['--bytes', str(probe.MAX_WINDOW + 1)],
                      ['--seed', '7', '--seed', '7']):
            with patch.object(probe, 'read_payload') as read, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as failure:
                    probe.main(base + extra)
                self.assertEqual(failure.exception.code, 2)
                read.assert_not_called()
        for source in (b'', b'\0' * (probe.MAX_WINDOW + 1)):
            with self.assertRaises(ValueError):
                probe.synchronization(source)


if __name__ == '__main__':
    unittest.main()
