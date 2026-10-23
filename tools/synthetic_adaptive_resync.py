#!/usr/bin/env python3
"""Original syntax-adaptive Rice controls for #300; no camera inference.

Builds on synthetic_resync_probe.py and synthetic_state_resync.py accounting,
but here current state selects k BEFORE parsing the next Rice word.
State initially zero. previous-wire sets state=wire%4; accumulating sets
state=(state+wire)%4. Both emit the unsigned wire value, without truncation.
fixed2 is a stateless mismatched control (k=2, state always zero).
Matching encoders invert these declared grammars on values 0..15.

All seeds/anchors/window/run lengths are frozen constants. Each parser compares
its changed parse with its OWN original parse, including nonmatching cells.
Only complete unchanged post-edit intervals are aligned in original coordinates.
Recovery is three consecutive aligned intervals in BOTH token sequences;
state recovery additionally requires equal state-before AND decoded wire value.
These are finite-window observed runs, not a guarantee of permanent recovery.
For these grammars state equals k injectively: on unchanged bits, matching
complete intervals force the same unary stop, k, state and wire value. Thus
boundary/state recovery coincide by construction, not as independent evidence.
No generator classifier, matched null or camera experiment is implemented.
Stdlib CPU only; no input/output files, network, raw samples or images. CC0.
"""

import argparse
import json
import time
import tracemalloc
import unittest


GENERATORS = ("previous-wire", "accumulating")
PARSERS = GENERATORS + ("fixed2",)
ANCHORS = (17, 61, 127)
EDITS = ("flip", "insert1", "delete")
WINDOW = 128
SUSTAIN = 3


def update(model, state, wire):
    if model == "previous-wire":
        return wire % 4
    if model == "accumulating":
        return (state + wire) % 4
    if model == "fixed2":
        return 0
    raise ValueError("unknown model")


def rice_k(model, state):
    if model not in PARSERS:
        raise ValueError("unknown model")
    return 2 if model == "fixed2" else state


def values(seed, count=256):
    out = []
    for _ in range(count):
        seed = (1664525 * seed + 1013904223) % (1 << 32)
        out.append(seed >> 28)
    return out


def encode(data, model):
    state = 0
    out = []
    for wire in data:
        if not isinstance(wire, int) or not 0 <= wire < 16:
            raise ValueError("encoder values must be integers 0..15")
        k = rice_k(model, state)
        out.append("0" * (wire >> k) + "1")
        if k:
            out.append(format(wire % (1 << k), "0%db" % k))
        state = update(model, state, wire)
    return "".join(out)


def parse(bits, model):
    """Complete (start,end,state-before,wire) tokens; total consumed bits.

    No unary cap or modulo reduction of decoded values. Incomplete final words
    consume none of their bits and do not change state.
    """
    if model not in PARSERS or any(b not in "01" for b in bits):
        raise ValueError("invalid model/bits")
    position = state = 0
    out = []
    while position < len(bits):
        start = position
        k = rice_k(model, state)
        stop = bits.find("1", start)
        if stop < 0 or stop + 1 + k > len(bits):
            return out, start
        end = stop + 1 + k
        remainder = int(bits[stop + 1:end], 2) if k else 0
        wire = ((stop - start) << k) + remainder
        out.append((start, end, state, wire))
        state = update(model, state, wire)
        position = end
    return out, position


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
    if edit == "insert1":
        return (start - 1, end - 1) if start >= anchor + 1 else None
    if edit == "delete":
        return (start + 1, end + 1) if start >= anchor else None
    if edit == "flip":
        return (start, end) if start >= anchor + 1 else None
    raise ValueError("unknown edit")


def first_run(pairs, state_required):
    run = []
    for oi, ci, original, changed in pairs:
        consecutive = (not run or
                       (oi == run[-1][0] + 1 and ci == run[-1][1] + 1))
        equal = not state_required or original[2:] == changed[2:]
        if not consecutive or not equal:
            run = []
        if equal:
            run.append((oi, ci, original, changed))
            if len(run) == SUSTAIN:
                return run[0][2][0]
    return None


def trial(bits, parser, anchor, edit, window=WINDOW):
    if window <= 0:
        raise ValueError("positive window required")
    original, consumed = parse(bits, parser)
    changed_bits = perturb(bits, anchor, edit)
    changed, changed_consumed = parse(changed_bits, parser)
    limit = min(len(bits), anchor + window)
    lookup = {(t[0], t[1]): (i, t) for i, t in enumerate(original)}
    pairs = []
    for ci, token in enumerate(changed):
        span = mapped_interval(token[0], token[1], anchor, edit)
        if span is not None and span[1] <= limit and span in lookup:
            oi, other = lookup[span]
            pairs.append((oi, ci, other, token))
    boundary = first_run(pairs, False)
    state = first_run(pairs, True)
    return {
        "parser": parser, "anchor": anchor, "edit": edit,
        "observation_end_original": limit,
        "eof_shortened_window": limit < anchor + window,
        "original_complete_tokens": len(original),
        "changed_complete_tokens": len(changed),
        "original_consumed_bits": consumed,
        "changed_consumed_bits": changed_consumed,
        "original_incomplete_tail_bits": len(bits) - consumed,
        "changed_incomplete_tail_bits": len(changed_bits) - changed_consumed,
        "aligned_complete_intervals": len(pairs),
        "state_before_mismatches": sum(a[2] != b[2] for _, _, a, b in pairs),
        "wire_value_mismatches": sum(a[3] != b[3] for _, _, a, b in pairs),
        "boundary_recovery_distance": None if boundary is None else boundary - anchor,
        "state_recovery_distance": None if state is None else state - anchor,
        "boundary_right_censored": boundary is None,
        "state_right_censored": state is None,
    }


def benchmark():
    rows = []
    for seed in (300, 301):
        data = values(seed)
        for generator in GENERATORS:
            bits = encode(data, generator)
            for parser in PARSERS:
                for anchor in ANCHORS:
                    for edit in EDITS:
                        row = trial(bits, parser, anchor, edit)
                        row.update(seed=seed, generator=generator, source_bits=len(bits))
                        rows.append(row)
    return rows


class Controls(unittest.TestCase):
    def test_hand_syntax_and_inverse(self):
        self.assertEqual(encode([1, 2, 3], "previous-wire"), "01010111")
        self.assertEqual(encode([1, 2, 3], "accumulating"), "010101011")
        for model in PARSERS:
            data = values(300)
            bits = encode(data, model)
            tokens, consumed = parse(bits, model)
            self.assertEqual([t[3] for t in tokens], data)
            self.assertEqual(consumed, len(bits))

    def test_state_changes_syntax(self):
        # wire1 sets k=1; next zero word now needs stop+one remainder.
        self.assertEqual(parse("011", "previous-wire"), ([(0, 2, 0, 1)], 2))
        self.assertEqual(parse("0110", "previous-wire"),
                         ([(0, 2, 0, 1), (2, 4, 1, 0)], 4))
        self.assertEqual(parse("000", "previous-wire"), ([], 0))

    def test_coordinates(self):
        self.assertIsNone(mapped_interval(4, 8, 5, "insert1"))
        self.assertEqual(mapped_interval(6, 9, 5, "insert1"), (5, 8))
        self.assertEqual(mapped_interval(5, 8, 5, "delete"), (6, 9))
        self.assertIsNone(mapped_interval(5, 8, 5, "flip"))

    def test_consecutive_in_both_sequences_and_state(self):
        a = (3, 4, 0, 0)
        b = (3, 4, 1, 0)
        skipped = [(0, 0, a, a), (2, 1, a, a), (3, 2, a, a)]
        self.assertIsNone(first_run(skipped, False))
        pairs = [(i, i, a, b) for i in range(3)]
        self.assertEqual(first_run(pairs, False), 3)
        self.assertIsNone(first_run(pairs, True))

    def test_eof_censoring(self):
        row = trial("1111", "previous-wire", 2, "flip")
        self.assertTrue(row["eof_shortened_window"])
        self.assertTrue(row["boundary_right_censored"])
        self.assertTrue(row["state_right_censored"])

    def test_corruption_changes_state_and_boundaries(self):
        # Ten zero words at k=0. Flipping first stop produces wire1, then k1
        # words consume pairs of ones; the original consumes individual ones.
        bits = "1" * 10
        row = trial(bits, "previous-wire", 0, "flip")
        self.assertEqual(row["aligned_complete_intervals"], 0)
        self.assertTrue(row["boundary_right_censored"])
        self.assertTrue(row["state_right_censored"])

    def test_no_edit_roundtrip_states(self):
        # Every matched encoder boundary has its pre-encode state.
        for model in GENERATORS:
            state = 0
            data = values(301)
            tokens, _ = parse(encode(data, model), model)
            for token, wire in zip(tokens, data):
                self.assertEqual(token[2], state)
                state = update(model, state, wire)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--self-test", action="store_true", help="run deterministic controls")
    args = cli.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
        return 0 if result.wasSuccessful() else 1
    tracemalloc.start()
    started = time.perf_counter()
    rows = benchmark()
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(json.dumps({
        "scope": "original synthetic syntax-adaptive controls; no camera inference",
        "baseline": "each parser against its own original-stream parse",
        "lcg": "(1664525*s+1013904223) modulo 2**32; take s>>28",
        "seeds": [300, 301], "values_per_stream": 256, "anchors": ANCHORS,
        "window_original_bits": WINDOW, "sustained_complete_intervals": SUSTAIN,
        "grammar": "Rice zero-unary, MSB remainder; k=current two-bit state",
        "updates": {"previous-wire": "wire%4", "accumulating": "(state+wire)%4",
                    "fixed2": "k=2 and state=0"},
        "initial_state": 0,
        "structural_limit": "state=k injectively; shared unchanged complete interval forces equal state/wire; recovery metrics coincide by construction",
        "count_scope": "tokens/consumed/tails full stream; alignment/recovery window only",
        "precision": "exact Python integers; stdlib CPU; RTX3090 unnecessary tiny pilot",
        "pilot_seconds": elapsed, "tracemalloc_peak_bytes": peak,
        "trial_count": len(rows),
        "boundary_recovered": sum(not r["boundary_right_censored"] for r in rows),
        "state_recovered": sum(not r["state_right_censored"] for r in rows),
        "trials": rows,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
