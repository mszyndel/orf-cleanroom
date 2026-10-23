#!/usr/bin/env python3
"""Original synthetic controls for #300; no camera codec model is asserted.

Both models use zero-unary Rice2 wire words, independently of semantic state.
Each wire word is reduced modulo 16 before updating a four-bit state. The
previous-code model emits wire XOR state, then stores wire. The accumulator
model emits and stores (state + wire) modulo 16. Initial state is zero.
Encoders invert those rules on generated four-bit desired values.

This deliberately separates syntax boundaries from semantic adaptive state;
it does not test a grammar whose state changes its token lengths. Original
code only, built for radialmonster; CC0. Outputs contain aggregates only.
"""

import argparse
import json
import time
import tracemalloc
import unittest


MODELS = ("previous-code", "accumulator")
ANCHORS = (17, 61, 127)
EDITS = ("flip", "insert1", "delete")
WINDOW = 128
SUSTAIN = 3


def advance(model, state, wire):
    wire %= 16
    if model == "previous-code":
        return wire, wire ^ state
    if model == "accumulator":
        state = (state + wire) % 16
        return state, state
    raise ValueError("unknown model")


def values(seed, count):
    result = []
    for _ in range(count):
        seed = (1664525 * seed + 1013904223) % (1 << 32)
        result.append(seed >> 28)
    return result


def encode(data, model):
    state = 0
    pieces = []
    for value in data:
        wire = value ^ state if model == "previous-code" else (value - state) % 16
        pieces.append("0" * (wire // 4) + "1" + format(wire % 4, "02b"))
        state, recovered = advance(model, state, wire)
        if recovered != value:
            raise AssertionError("encoder inversion")
    return "".join(pieces)


def parse(bits, model):
    """Return complete (start,end,state-before,wire,value) tokens and consumed bits.

    An incomplete unary prefix or remainder consumes no part of its token.
    There is no unary cap; malformed wires still have defined modulo16 semantics.
    """
    tokens = []
    position = 0
    state = 0
    while position < len(bits):
        start = position
        while position < len(bits) and bits[position] == "0":
            position += 1
        quotient = position - start
        if position + 3 > len(bits):
            return tokens, start
        wire = quotient * 4 + int(bits[position + 1:position + 3], 2)
        position += 3
        before = state
        state, value = advance(model, state, wire)
        tokens.append((start, position, before, wire, value))
    return tokens, position


def perturb(bits, anchor, edit):
    if not 0 <= anchor < len(bits):
        raise ValueError("anchor outside stream")
    if edit == "flip":
        return bits[:anchor] + str(1 - int(bits[anchor])) + bits[anchor + 1:]
    if edit == "insert1":
        return bits[:anchor] + "1" + bits[anchor:]
    if edit == "delete":
        return bits[:anchor] + bits[anchor + 1:]
    raise ValueError("unknown edit")


def mapped_interval(start, end, anchor, edit):
    """Only wholly unchanged post-edit token intervals may be compared.

    Original edit extent is [anchor,anchor+1) for flip/delete, empty for insert.
    A token containing inserted content is excluded even when endpoints map.
    """
    if edit == "insert1":
        return (start - 1, end - 1) if start >= anchor + 1 else None
    if edit == "delete":
        return (start + 1, end + 1) if start >= anchor else None
    return (start, end) if start >= anchor + 1 else None


def first_run(pairs, require_state):
    """Three consecutive matching intervals in BOTH token sequences.

    State recovery also requires equal state-before and emitted value. Equal
    future wires then preserve agreement for these particular update rules.
    """
    run = []
    for original_index, changed_index, original, changed in pairs:
        contiguous = (not run or
                      (original_index == run[-1][0] + 1 and
                       changed_index == run[-1][1] + 1))
        equal = not require_state or (original[2] == changed[2] and
                                     original[4] == changed[4])
        if not contiguous or not equal:
            run = []
        if equal:
            run.append((original_index, changed_index, original, changed))
            if len(run) == SUSTAIN:
                return run[0][2][0]
    return None


def trial(bits, model, anchor, edit, window=WINDOW):
    original, consumed = parse(bits, model)
    changed_bits = perturb(bits, anchor, edit)
    changed, changed_consumed = parse(changed_bits, model)
    limit = min(len(bits), anchor + window)
    lookup = {(token[0], token[1]): (index, token)
              for index, token in enumerate(original)}
    pairs = []
    for index, token in enumerate(changed):
        mapped = mapped_interval(token[0], token[1], anchor, edit)
        if mapped is not None and mapped[1] <= limit and mapped in lookup:
            original_index, other = lookup[mapped]
            pairs.append((original_index, index, other, token))
    boundary = first_run(pairs, False)
    state = first_run(pairs, True)
    return {
        "model": model, "anchor": anchor, "edit": edit,
        "observation_end_original": limit,
        "eof_shortened": limit < anchor + window,
        "original_complete_tokens": len(original),
        "changed_complete_tokens": len(changed),
        "original_consumed_bits": consumed,
        "changed_consumed_bits": changed_consumed,
        "original_incomplete_tail_bits": len(bits) - consumed,
        "changed_incomplete_tail_bits": len(changed_bits) - changed_consumed,
        "aligned_complete_intervals": len(pairs),
        "state_before_mismatches": sum(a[2] != b[2] for _, _, a, b in pairs),
        "value_mismatches": sum(a[4] != b[4] for _, _, a, b in pairs),
        "boundary_recovery_distance": None if boundary is None else boundary - anchor,
        "state_recovery_distance": None if state is None else state - anchor,
        "boundary_right_censored": boundary is None,
        "state_right_censored": state is None,
    }


def benchmark():
    trials = []
    # Frozen seeds provide discovery-style and second synthetic controls, without
    # fitting any classifier or choosing anchors after seeing outcomes.
    for seed in (300, 301):
        data = values(seed, 256)
        for generator in MODELS:
            bits = encode(data, generator)
            for parser in MODELS:
                for anchor in ANCHORS:
                    for edit in EDITS:
                        result = trial(bits, parser, anchor, edit)
                        result.update(seed=seed, generator=generator, source_bits=len(bits))
                        trials.append(result)
    return trials


class Controls(unittest.TestCase):
    def test_hand_encoders(self):
        self.assertEqual(encode([1, 2, 3], "previous-code"), "101111100")
        self.assertEqual(encode([1, 2, 3], "accumulator"), "101101101")

    def test_roundtrip(self):
        for model in MODELS:
            data = values(300, 256)
            bits = encode(data, model)
            tokens, consumed = parse(bits, model)
            self.assertEqual([token[4] for token in tokens], data)
            self.assertEqual(consumed, len(bits))

    def test_incomplete_and_large_wire(self):
        for bits in ("000", "1", "10", "00001"):
            self.assertEqual(parse(bits, "accumulator"), ([], 0))
        self.assertEqual(parse("0000111", "accumulator")[0][0], (0, 7, 0, 19, 3))

    def test_coordinates(self):
        self.assertIsNone(mapped_interval(4, 8, 5, "insert1"))
        self.assertEqual(mapped_interval(6, 9, 5, "insert1"), (5, 8))
        self.assertEqual(mapped_interval(5, 8, 5, "delete"), (6, 9))
        self.assertIsNone(mapped_interval(5, 8, 5, "flip"))

    def test_hand_boundary_without_accumulator_state(self):
        # Eight wire-zero words: flip the low remainder of the first word to 1.
        # Subsequent boundaries match at 3,6,9,...; accumulator differs by one
        # forever, whereas previous-code state recovers after one intact word.
        bits = "100" * 8
        accumulator = trial(bits, "accumulator", 2, "flip")
        previous = trial(bits, "previous-code", 2, "flip")
        self.assertEqual(accumulator["boundary_recovery_distance"], 1)
        self.assertIsNone(accumulator["state_recovery_distance"])
        self.assertEqual(accumulator["aligned_complete_intervals"], 7)
        self.assertEqual(accumulator["state_before_mismatches"], 7)
        self.assertEqual(accumulator["value_mismatches"], 7)
        self.assertEqual(previous["state_recovery_distance"], 4)
        self.assertEqual(previous["state_before_mismatches"], 1)

    def test_missing_intervals_are_censored_not_unequal(self):
        result = trial("100100", "accumulator", 2, "flip")
        self.assertTrue(result["eof_shortened"])
        self.assertTrue(result["boundary_right_censored"])
        self.assertEqual(result["aligned_complete_intervals"], 1)
        self.assertTrue(result["state_right_censored"])
        missing = trial("100", "accumulator", 2, "flip")
        self.assertEqual(missing["aligned_complete_intervals"], 0)
        self.assertEqual(missing["state_before_mismatches"], 0)
        self.assertTrue(missing["state_right_censored"])

    def test_consecutive_in_both_sequences(self):
        token = (3, 6, 0, 0, 0)
        pairs = [(0, 0, token, token), (2, 1, token, token), (3, 2, token, token)]
        self.assertIsNone(first_run(pairs, False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run deterministic controls")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
        return 0 if unittest.TextTestRunner().run(suite).wasSuccessful() else 1
    tracemalloc.start()
    started = time.perf_counter()
    trials = benchmark()
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(json.dumps({
        "scope": "original synthetic only; no camera or syntax-adaptive-state evidence",
        "generator": "LCG32: (1664525*s+1013904223) modulo 2**32; take s>>28",
        "seeds": [300, 301], "values_per_stream": 256, "anchors": ANCHORS,
        "window_original_bits": WINDOW, "sustained_complete_intervals": SUSTAIN,
        "state_bits": 4, "wire_semantics": "modulo16 before state update",
        "state_models": {
            "previous-code": "emit wire XOR state; store wire",
            "accumulator": "emit and store (state+wire) modulo16",
        },
        "baseline": "each parser compared against its own original-stream parse",
        "count_scope": "token/consumed/tail counts cover full stream; aligned counts and recovery cover observation window",
        "precision": "exact Python integers; CPU only; RTX3090 unnecessary for tiny pilot",
        "pilot_seconds": elapsed, "tracemalloc_peak_bytes": peak,
        "trial_count": len(trials),
        "boundary_recovered": sum(not row["boundary_right_censored"] for row in trials),
        "state_recovered": sum(not row["state_right_censored"] for row in trials),
        "trials": trials,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
