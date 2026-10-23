#!/usr/bin/env python3
"""Exact length/popcount/token-count matched synthetic source-label control.

Builds on #300 and #330, using their reviewed stateless parsers and frozen
classifier features. Balanced decks are fixed4=(1,2,4,8)*64,
rice0=(0,2,4,6)*64, rice2=(0,4,4,8)*64. Deck symbols are deterministically
permuted with the explicit Fisher-Yates/LCG32 implementation in
synthetic_resync_classify.shuffle, starting at the value seed, then encoded.
Every original stream has exactly 256 complete generator tokens, 1024 bits
and 256 ones by algebra, without padding, truncation or outcome rejection.

Training seeds400..403 and held-out500..507, features, centroids, tie order,
edit anchors, windows and shuffled-bit controls are unchanged from #330.
Separate real/shuffle models cross both held-out groups. All failures remain
in the features, with failure distance encoded129/129; no model selection.

Labels identify source recipes, not grammars: a string may parse under several
grammars. Label-specific symbol distributions and local codeword arrangements
remain confounds. Equal length/density removes that baseline's discrimination
by construction, not as an empirical test. Seed transfer within this deterministic
family is not distribution transfer, significance or camera-codec evidence.
CPU stdlib only; no input/output files, samples, images or pixel data. RTX3090
available but unnecessary for this tiny exact-integer/fraction pilot.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time
import tracemalloc
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import synthetic_resync_classify as baseline

probe = baseline.probe
DECKS = {'fixed4': (1, 2, 4, 8), 'rice0': (0, 2, 4, 6),
         'rice2': (0, 4, 4, 8)}


def source_values(seed, generator):
    """Permute a balanced single-digit symbol deck; preserve exact multiplicities."""
    deck = ''.join(str(v) for v in DECKS[generator]) * 64
    return [int(v) for v in baseline.shuffle(deck, seed)]


def cohort(seeds):
    rows = []
    for seed in seeds:
        for generator_index, generator in enumerate(probe.GRAMMARS):
            symbols = source_values(seed, generator)
            original = probe.encode(symbols, generator)
            if (len(original), original.count('1')) != (1024, 256):
                raise ValueError('balanced construction invariant failed')
            shuffled = baseline.shuffle(original, seed + 10000 + generator_index * 1000)
            for kind, bits in (('real', original), ('shuffle', shuffled)):
                vector, tails = baseline.features(bits)
                rows.append({'seed': seed, 'generator': generator, 'kind': kind,
                             'bits': len(bits), 'ones': bits.count('1'),
                             'source_symbols': len(symbols),
                             'source_symbol_histogram': dict(Counter(symbols)),
                             'parse_tail_bits_sum': tails, 'features': vector})
    return rows


def experiment():
    training, validation = cohort(baseline.TRAIN), cohort(baseline.VALIDATE)
    reports = []
    for feature in baseline.FEATURES:
        for training_kind in baseline.KINDS:
            model = baseline.fit(training, feature, training_kind)
            for validation_kind in baseline.KINDS:
                matrix = [[0] * 3 for _ in range(3)]
                predictions = []
                for row in validation:
                    if row['kind'] != validation_kind:
                        continue
                    predicted, scores = baseline.predict(model, row['features'][feature])
                    matrix[probe.GRAMMARS.index(row['generator'])][
                        probe.GRAMMARS.index(predicted)] += 1
                    predictions.append({'seed': row['seed'], 'source': row['generator'],
                                        'predicted': predicted, 'squared_distances': scores})
                reports.append({'feature': feature, 'training_kind': training_kind,
                                'validation_kind': validation_kind, 'centroids': model,
                                'confusion_rows_source_columns_prediction': matrix,
                                'correct_source_labels': sum(matrix[i][i] for i in range(3)),
                                'total': len(predictions), 'predictions': predictions})
    return {'protocol': {'training_seeds': baseline.TRAIN,
                         'validation_seeds': baseline.VALIDATE,
                         'class_order': probe.GRAMMARS, 'decks_repeated_64': DECKS,
                         'deck_permutation_seed': 'value seed',
                         'shuffle_seed': 'value seed + 10000 + 1000 * generator index',
                         'source_tokens': 256, 'bits': 1024, 'ones': 256,
                         'anchors': probe.ANCHORS, 'window_bits': probe.WINDOW,
                         'recovery_run': probe.RUN, 'precision': 'exact fractions',
                         'feature_order': 'parser, operation(flip/insert/delete), anchor',
                         'limits': 'balanced-deck source labels only; symbol distributions differ; '
                                   'no grammar identification, distribution transfer or camera evidence'},
            'cohorts': {'training': training, 'validation': validation},
            'classifications': reports}


class Tests(unittest.TestCase):
    def test_exact_matching_and_roundtrips(self):
        for seed in baseline.TRAIN + baseline.VALIDATE:
            for generator in probe.GRAMMARS:
                symbols = source_values(seed, generator)
                self.assertEqual(Counter(symbols), Counter(DECKS[generator] * 64))
                self.assertEqual(symbols, source_values(seed, generator))
                bits = probe.encode(symbols, generator)
                self.assertEqual((len(symbols), len(bits), bits.count('1')), (256, 1024, 256))
                tokens, tail = probe.parse(bits, generator)
                self.assertEqual([v for _, _, v in tokens], symbols)
                self.assertEqual(tail, 0)

    def test_seed_changes_order(self):
        for generator in probe.GRAMMARS:
            self.assertNotEqual(source_values(400, generator), source_values(401, generator))

    def test_baseline_ties_structural(self):
        rows = cohort((400,))
        for kind in baseline.KINDS:
            model = baseline.fit(rows, 'length_density', kind)
            for row in rows:
                label, scores = baseline.predict(model, row['features']['length_density'])
                self.assertEqual(label, 'fixed4')
                self.assertEqual(set(scores.values()), {0})

    def test_frozen_cohort_shape_and_null(self):
        rows = cohort((400,))
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertEqual((row['bits'], row['ones'], row['source_symbols']), (1024, 256, 256))
            for feature in baseline.FEATURES[:2]:
                self.assertEqual(len(row['features'][feature]), 27)
        self.assertFalse(set(baseline.TRAIN) & set(baseline.VALIDATE))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
        return 0 if result.wasSuccessful() else 1
    tracemalloc.start()
    start = time.perf_counter()
    report = experiment()
    report['benchmark'] = {'elapsed_seconds': time.perf_counter() - start,
                           'peak_traced_cpu_bytes': tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop()
    print(json.dumps(report, default=str, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
