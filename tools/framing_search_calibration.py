#!/usr/bin/env python3
"""Synthetic full-search surrogate diagnostic, Part of #297.

No camera inputs or held-out capture result. All candidates are repeated for
every surrogate; this demonstrates accounting, not camera exchangeability.
Byte permutations preserve byte histograms, not transition or run multisets.
Protocol: two 2048-bit windows, widths 2..12, all phases (154 candidates).
Score is phase-vs-rest Pearson 2x2; ties choose first; constant scores are 0.
Each model uses 127 fixed replicates with seed 297000+r, no early stopping.
This small development budget has worst-case raw-fraction SE about 0.044;
it is not intended to resolve rare tails. Local blocks are 32 bytes.
Synthetic bytes use Random(297); second case forces every byte's LSB to one.
That effect survives both byte nulls by construction: a large raw score alone
does not imply separation. Every observed candidate and surrogate maximum is
reported. Wilson uncertainty is conditional on the surrogate model, not a
familywise camera false-positive guarantee. There is no untouched validation.
Stdlib only; no files written; aggregate JSON only. Original clean-room code.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import random
import sys

WIDTHS = tuple(range(2, 13))
WINDOWS = ((0, 2048), (2048, 4096))
REPLICATES = 127
SEED = 297000
BLOCK = 32


def search(data, widths=WIDTHS, windows=WINDOWS):
    """Enumerate window/width/phase order; MSB-first; Pearson 2x2 score."""
    if not isinstance(data, bytes):
        raise ValueError("bytes required")
    if not widths or any(type(w) is not int or w < 2 for w in widths):
        raise ValueError("widths must be integers >= 2")
    if not windows or any(type(a) is not int or type(b) is not int or
                          not 0 <= a < b <= 8*len(data) for a, b in windows):
        raise ValueError("invalid bit window")
    rows = []
    for start, stop in windows:
        bits = [(data[i//8] >> (7-i % 8)) & 1 for i in range(start, stop)]
        n, ones = len(bits), sum(bits)
        for width in widths:
            for phase in range(width):
                selected = bits[phase::width]
                count, hits = len(selected), sum(selected)
                denominator = count*(n-count)*ones*(n-ones)
                score = (n*(hits*n-ones*count)**2 / denominator
                         if denominator else 0.0)
                rows.append({"window_bits": [start, stop], "width": width,
                             "phase": phase, "positions": count, "ones": hits,
                             "window_ones": ones, "score": score})
    return rows


def surrogate(data, model, rng, block=BLOCK):
    if type(block) is not int or block <= 0:
        raise ValueError("positive block size required")
    if model not in ("global_byte", "local_byte"):
        raise ValueError("unknown surrogate model")
    size = len(data) if model == "global_byte" else block
    result = bytearray()
    for start in range(0, len(data), max(size, 1)):
        values = list(data[start:start+size])
        rng.shuffle(values)
        result.extend(values)
    output = bytes(result)
    if Counter(output) != Counter(data):
        raise AssertionError("byte histogram changed")
    if model == "local_byte":
        for start in range(0, len(data), block):
            if Counter(data[start:start+block]) != Counter(output[start:start+block]):
                raise AssertionError("local byte histogram changed")
    return output


def wilson(exceedances, replicates):
    """95% Wilson interval for raw Bernoulli exceedance fraction, not rank."""
    if type(replicates) is not int or replicates < 1 or type(exceedances) is not int or not 0 <= exceedances <= replicates:
        raise ValueError("invalid exceedance count")
    z = 1.959963984540054
    p = exceedances / replicates
    divisor = 1 + z*z/replicates
    center = (p + z*z/(2*replicates))/divisor
    radius = z*math.sqrt(p*(1-p)/replicates+z*z/(4*replicates**2))/divisor
    return [max(0.0, center-radius), min(1.0, center+radius)]


def calibrate(data, replicates=REPLICATES, widths=WIDTHS, windows=WINDOWS):
    if type(replicates) is not int or replicates < 1:
        raise ValueError("positive replicate count required")
    observed = search(data, widths, windows)
    winner = max(range(len(observed)), key=lambda i: observed[i]["score"])
    maximum = observed[winner]["score"]
    models = []
    for model in ("global_byte", "local_byte"):
        maxima = []
        for replicate in range(replicates):
            transformed = surrogate(data, model, random.Random(SEED+replicate))
            rows = search(transformed, widths, windows)
            index = max(range(len(rows)), key=lambda i: rows[i]["score"])
            maxima.append({"replicate": replicate, "winner_index": index,
                           "maximum": rows[index]["score"],
                           "candidates_evaluated": len(rows)})
        exceedances = sum(row["maximum"] >= maximum for row in maxima)
        models.append({"model": model, "replicate_maxima": maxima,
                       "exceedances_ge": exceedances,
                       "raw_exceedance_fraction": exceedances/replicates,
                       "model_tail_wilson_95": wilson(exceedances, replicates),
                       "plus_one_rank_diagnostic": (exceedances+1)/(replicates+1)})
    return {"synthetic_sha256": hashlib.sha256(data).hexdigest(),
            "byte_count": len(data), "candidate_count": len(observed),
            "observed_candidates": observed, "observed_winner_index": winner,
            "observed_maximum": maximum, "models": models}


def development_cases():
    rng = random.Random(297)
    uniform = bytes(rng.randrange(256) for _ in range(512))
    return [("uniform_development", uniform),
            ("forced_byte_lsb_development", bytes(x | 1 for x in uniform))]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print(json.dumps({"python_version": sys.version.split()[0],
                      "protocol": "#297 synthetic development only; no held-out capture",
                      "seed": SEED, "rng": "random.Random MT19937; Fisher-Yates shuffle",
                      "replicates_per_model": REPLICATES, "local_block_bytes": BLOCK,
                      "tie_rule": "first maximum in window/width/phase order",
                      "inference_boundary": "Surrogate-model diagnostic only; no camera p-value. Wilson interval describes Monte Carlo tail uncertainty, not model correctness.",
                      "cases": [dict(case=name, **calibrate(data))
                                for name, data in development_cases()]}, indent=2,
                     allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
