#!/usr/bin/env python3
"""Finite iid terminal-residual diagnostic for independently anchored windows.

Part of #87. This is an original candidate-grammar null, not a decoder.
Token: q zeros, stop1, five suffix bits; accept only if all q+6 bits fit.
No extra escape skip. First/last 4096 payload bits each restart at bit zero
of that window. They are NOT whole-payload token endpoints or physical rows.

Under iid Bernoulli(p), complete-token length q+6 has probability p*(1-p)^q.
U(s) is the probability of a renewal boundary at s: U(0)=1, U(1..5)=0,
U(6)=p, U(s)=(1-p)*U(s-1)+p*U(s-6) thereafter. For N bits, residual length r
has mass U(N-r)*S(r), where S(r)=1 for r<6 and (1-p)^(r-5) otherwise.
A nonempty all-one residual can only have r=1..5; its joint mass is
U(N-r)*p^r. These finite distributions are exact mathematically, evaluated
in floating point. Both fixed p=.5 and in-sample fitted p are descriptive;
neither supplies calibrated significance, framing or padding evidence.

Stdlib Python 3.8+. Reads files and prints aggregates only. Licence/hash
verification is a separate prerequisite. Repeat --sample ID PUBLIC_NAME FILE.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class

WINDOW_BITS = 4096


def residual_null(n, p):
    """Finite residual PMF and nonempty-all-one event, including p=0/1."""
    if type(n) is not int or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("p must be finite and between zero and one")
    z = 1 - p
    renewal = [0.0] * (n + 1)
    renewal[0] = 1.0
    for s in range(6, n + 1):
        renewal[s] = p * renewal[s - 6]
        if s > 6:
            renewal[s] += z * renewal[s - 1]
    pmf = [renewal[n - r] * (1.0 if r < 6 else z ** (r - 5))
           for r in range(n + 1)]
    all_one = math.fsum(renewal[n-r] * p ** r for r in range(1, min(n, 5) + 1))
    nonempty = math.fsum(pmf[1:])
    return {"p_one": p, "residual_length_pmf": pmf,
            "probability_sum": math.fsum(pmf),
            "nonempty_probability": nonempty,
            "nonempty_all_one_probability": all_one,
            "all_one_given_nonempty": all_one / nonempty if nonempty else None}


def scan_window(bits):
    """Accept complete candidates only; report no bit values or payload bytes."""
    pos, count, escapes = 0, 0, 0
    while pos < len(bits):
        stop = bits.find("1", pos)
        if stop < 0 or stop + 6 > len(bits):
            break
        escapes += stop - pos >= 17
        pos = stop + 6
        count += 1
    tail = bits[pos:]
    return {"complete_tokens": count, "candidate_escapes": escapes,
            "consumed_bits": pos, "residual_length": len(tail),
            "nonempty_all_one_residual": bool(tail) and all(b == "1" for b in tail)}


def window_report(payload, start):
    # Windows are byte-aligned and fixed at 512 bytes; never emit their bits.
    bits = "".join(format(b, "08b") for b in payload[start // 8:(start + WINDOW_BITS) // 8])
    if len(bits) != WINDOW_BITS:
        raise ValueError("incomplete window")
    ones = bits.count("1")
    return {"start_bit": start, "end_bit_exclusive": start + WINDOW_BITS,
            "window_bits": WINDOW_BITS, "one_bits": ones,
            "candidate_parse": scan_window(bits),
            "fair_null": residual_null(WINDOW_BITS, 0.5),
            "fitted_in_sample_null": residual_null(WINDOW_BITS, ones / WINDOW_BITS)}


def report(sid, name, path):
    with open(path, "rb") as handle:
        data = handle.read()
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("requires one contiguous strip")
    off, count = offsets[0], lengths[0]
    w, h = best[0x100][0], best[0x101][0]
    if off < 0 or count < WINDOW_BITS // 8 or off + count > len(data):
        raise ValueError("payload out of bounds or too short")
    if w <= 0 or h <= 0 or size_class(count, w, h) != "variable":
        raise ValueError("requires positive variable-size payload")
    payload = data[off:off+count]
    return {"pixls_id": sid, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(), "variant": "unassigned",
            "payload_w": w, "payload_h": h, "payload_bytes": count,
            "payload_offset": off, "size_class": "variable",
            "compression_tag": (best.get(0x103) or [None])[0],
            "windows": {"prefix": window_report(payload, 0),
                        "tail": window_report(payload, count * 8 - WINDOW_BITS)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "FILE"))
    args = parser.parse_args(argv)
    ids = [sid for sid, _, _ in args.sample]
    if any(not sid.isascii() or not sid.isdecimal() or int(sid) <= 0 for sid in ids):
        parser.error("sample IDs must be positive ASCII decimal integers")
    if len(set(map(int, ids))) != len(ids):
        parser.error("sample IDs must be distinct")
    samples, errors = [], []
    for sid, name, path in args.sample:
        try:
            samples.append(report(sid, name, path))
        except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
            errors.append({"pixls_id": sid, "error_type": type(exc).__name__})
    sources = {}
    for source in ("terminal_residual_null_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), source), "rb") as handle:
            sources[source] = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps({"source_sha256": sources, "python_version": sys.version.split()[0],
                      "window_bits": WINDOW_BITS, "samples": samples, "errors": errors},
                     indent=2, allow_nan=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
