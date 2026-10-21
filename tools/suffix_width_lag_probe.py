#!/usr/bin/env python3
"""Candidate-grammar neighbour tables, supporting #29 and specs/V1.md G8.

All k=2..8, stop=0,1, first 262144 complete tokens from payload bit zero.
q counts opposite bits before stop; k suffix bits follow; q>=17 has no extra
skip. At lags 1..5, report binary q>0 and fixed low-two suffix bits (s&3).
Omit only pairs with q>=17 at either endpoint; preserve absolute indices.
Intervening escapes remain. Omission cannot repair unknown escape framing.
Unsmoothed plug-in MI is descriptive, biased by finite sample, marginal and
selection effects, without a null/significance test. Equal alphabet sizes do
not justify ranking grammars. No physical rows, historical reproduction,
padding, codec selection or decoding is established. Licence-check inputs.
Reads regular files and prints aggregates only; stdlib Python 3.8+.
"""
import argparse
import hashlib
import json
import math
import os
import stat
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class

TOKENS = 262144
MAX_BYTES = 512 * 1024 * 1024


def parse(payload, k, stop, limit=TOKENS):
    """Return candidate q/suffix pairs, consuming only complete tokens."""
    if k not in range(2, 9) or stop not in (0, 1) or limit < 0:
        raise ValueError("invalid candidate")
    nbits, pos, tokens = len(payload) * 8, 0, []
    flip = 0 if stop else 255
    while pos < nbits and len(tokens) < limit:
        start = pos
        while pos < nbits:
            shift = pos & 7
            candidate = (payload[pos >> 3] ^ flip) & (255 >> shift)
            if candidate:
                pos += (8 - shift) - candidate.bit_length()
                break
            pos += 8 - shift
        if pos + 1 + k > nbits:
            pos = start
            break
        q = pos - start
        pos += 1
        suffix = 0
        for _ in range(k):
            suffix = (suffix << 1) | ((payload[pos >> 3] >> (7 - (pos & 7))) & 1)
            pos += 1
        tokens.append((q, suffix))
    return tokens, pos


def mi(table):
    """Unsmoothed plug-in mutual information in bits; empty is undefined."""
    n = sum(map(sum, table))
    if not n:
        return None
    rows = list(map(sum, table))
    cols = [sum(row[j] for row in table) for j in range(len(table[0]))]
    return sum(count / n * math.log2(count * n / (rows[i] * cols[j]))
               for i, row in enumerate(table) for j, count in enumerate(row) if count)


def measures(tokens):
    result = []
    for lag in range(1, 6):
        qtable, stable = [[0] * 2 for _ in range(2)], [[0] * 4 for _ in range(4)]
        omitted = 0
        for t in range(lag, len(tokens)):
            q0, s0 = tokens[t - lag]
            q1, s1 = tokens[t]
            if q0 >= 17 or q1 >= 17:
                omitted += 1
                continue
            qtable[int(q0 > 0)][int(q1 > 0)] += 1
            stable[s0 & 3][s1 & 3] += 1
        candidates = max(0, len(tokens) - lag)
        result.append({"lag": lag, "candidate_pairs": candidates,
                       "omitted_escape_endpoint_pairs": omitted,
                       "retained_pairs": candidates - omitted,
                       "q_positive_table": qtable, "q_positive_mi_bits": mi(qtable),
                       "suffix_low2_table": stable, "suffix_low2_mi_bits": mi(stable)})
    return result


def report(sample_id, name, path):
    if not stat.S_ISREG(os.stat(path).st_mode):
        raise ValueError("regular file required")
    with open(path, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("regular file required")
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("input too large")
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("single strip required")
    off, count = offsets[0], lengths[0]
    w, h = best[0x100][0], best[0x101][0]
    if (off < 0 or count <= 0 or off + count > len(data) or w <= 0 or h <= 0
            or size_class(count, w, h) != "variable" or best.get(0x103) != [1]):
        raise ValueError("positive variable payload, compression tag 1 required")
    payload = data[off:off + count]
    cells = []
    for stop in (0, 1):
        for k in range(2, 9):
            tokens, end = parse(payload, k, stop)
            cells.append({"k": k, "stop_bit": stop, "tokens": len(tokens),
                          "token_shortfall": TOKENS - len(tokens),
                          "bits_consumed": end, "remaining_payload_bits": count * 8 - end,
                          "q_ge_17": sum(q >= 17 for q, _ in tokens),
                          "lags": measures(tokens)})
    return {"pixls_id": sample_id, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(), "variant": "unassigned",
            "size_class": "variable", "compression_tag": 1,
            "payload_w": w, "payload_h": h, "payload_bytes": count, "cells": cells}


def source_hashes():
    result = {}
    for name in ("suffix_width_lag_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), name), "rb") as handle:
            result[name] = hashlib.sha256(handle.read()).hexdigest()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "FILE"))
    args = parser.parse_args(argv)
    ids = [entry[0] for entry in args.sample]
    if any(not value.isascii() or not value.isdecimal() or int(value) <= 0 for value in ids):
        parser.error("sample IDs must be positive ASCII decimals")
    if len(set(ids)) != len(ids):
        parser.error("sample IDs must be distinct")
    reports, failures = [], []
    for sample_id, name, path in args.sample:
        try:
            reports.append(report(sample_id, name, path))
        except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error):
            failures.append({"pixls_id": sample_id, "error": "invalid_or_unreadable_input"})
    print(json.dumps({"source_sha256": source_hashes(), "requested_tokens": TOKENS,
                      "python_version": sys.version.split()[0],
                      "samples": reports, "failures": failures}, indent=2, allow_nan=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
