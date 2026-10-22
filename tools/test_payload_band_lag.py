#!/usr/bin/env python3
"""Independent expanded-bit tests for payload_band_lag (synthetic only)."""
import collections
import hashlib
import importlib.util
from pathlib import Path
import random
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('band_lag', Path(__file__).with_name('payload_band_lag.py'))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class Tests(unittest.TestCase):
    def test_counts_independent_expanded_bits(self):
        for value in range(256):
            data = bytes([value, 255-value])
            bits = [int(c) for c in format(value,'08b')+format(255-value,'08b')]
            for row in probe.lag_map(data,list(range(1,16))):
                lag=row['lag_bits']; pairs=list(zip(bits,bits[lag:]))
                self.assertEqual((row['pairs'],row['left_ones'],row['right_ones'],row['both_ones']),
                                 (len(pairs),sum(x for x,y in pairs),sum(y for x,y in pairs),sum(x*y for x,y in pairs)))
                x=[a for a,b in pairs]; y=[b for a,b in pairs]
                mx=sum(x)/len(x); my=sum(y)/len(y)
                dx=sum((v-mx)**2 for v in x); dy=sum((v-my)**2 for v in y)
                expected=sum((a-mx)*(b-my) for a,b in pairs)/(dx*dy)**0.5 if dx*dy else None
                if expected is None: self.assertIsNone(row['phi'])
                else: self.assertAlmostEqual(row['phi'],expected,places=12)

    def test_stationary_and_drifting(self):
        rng=random.Random(90296)
        def repeated(n):
            motif=bytes(rng.randrange(256) for unused in range(n))
            return (motif*300)[:4096]
        first=repeated(17); second=repeated(23)
        lags=list(range(120,201))
        stable=probe.analyze(first+first,[0,4096],4096,lags,3)
        drift=probe.analyze(first+second,[0,4096],4096,lags,3)
        self.assertEqual([b['winner']['lag_bits'] for b in stable['bands']],[136,136])
        self.assertEqual([b['winner']['lag_bits'] for b in drift['bands']],[136,184])
        self.assertEqual(drift['bands'][1]['frozen_lag_bits'],136)
        self.assertEqual(stable['bands'][1]['frozen_phi'],1.0)
        self.assertLess(drift['bands'][1]['frozen_phi'],0.5)

    def test_null_recomputes_whole_grid(self):
        data=bytes(range(64))*2; lags=[7,8,9,15]
        result=probe.analyze(data,[0,64],64,lags,4,16,123)
        rng=random.Random(123)
        for band in result['bands']:
            expected=[]
            for unused in range(4):
                scrambled=probe.shuffle_blocks(data[:64],16,rng)
                expected.append(max(r['phi'] for r in probe.lag_map(scrambled,lags)))
            self.assertEqual(band['null_search_maxima'],expected)

    def test_local_histogram_and_tail(self):
        data=bytes(range(103))
        changed=probe.shuffle_blocks(data,16,random.Random(37))
        for start in range(0,len(data),16):
            self.assertEqual(collections.Counter(data[start:start+16]),collections.Counter(changed[start:start+16]))
        self.assertNotEqual(data,changed)

    def test_constant_ties_boundary_and_coordinates(self):
        result=probe.analyze(bytes(32),[0,16],16,[1,8],2,8,absolute_offset=40)
        self.assertIsNone(result['bands'][0]['winner']['lag_bits'])
        self.assertEqual(result['bands'][1]['null_undefined_maxima'],2)
        self.assertEqual(result['bands'][1]['absolute_start_bit'],448)
        rows=probe.lag_map(bytes([170])*16,[2,4,6])
        self.assertEqual(probe.winner(rows)['ties'],[2,4,6])
        self.assertTrue(probe.winner(rows)['range_boundary'])

    def test_rejections_and_hash_gate(self):
        for starts in ([0],[2,1],[0,0],[0,7],[0,25]):
            with self.assertRaises(ValueError): probe.analyze(bytes(32),starts,8,[1],1)
        for lags in ([0],[64],[2,1],[]):
            with self.assertRaises(ValueError): probe.analyze(bytes(32),[0,8],8,lags,1)
        with tempfile.NamedTemporaryFile(delete=False) as source:
            source.write(bytes(range(32))); path=Path(source.name)
        try:
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(probe.load_extent(path,digest,8,3),bytes([8,9,10]))
            with self.assertRaises(ValueError): probe.load_extent(path,'0'*64,0,32)
            with self.assertRaises(ValueError): probe.load_extent(path,digest,31,2)
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
