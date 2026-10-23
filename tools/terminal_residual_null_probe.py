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

Optional --fixed-density adds exact counts under a uniform permutation of the
window's N bits with K ones. This conditions density exactly but assumes
exchangeable bit order, which is not established for camera payloads. Its
event probabilities are descriptive baselines, not inferential p-values.

Separate --fixed-density-lengths emits all N+1 exact residual-length counts
and floating probabilities. Counts normalize exactly; tiny floating entries
may underflow to zero. Integer coefficient recurrence uses O(N*K) integer
operations and O(N+K) stored integers (integer sizes grow with N). This
slower option preserves default and --fixed-density reports unchanged.

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


def boundary_count(n, ones):
    """Count N-bit/K-one strings ending at a complete candidate boundary.

    With t tokens, n-6t zeros are distributed over t unary prefixes in
    choose(n-5t-1,t-1) ways; the t stops are one and the 5t suffix positions
    contain ones-t ones in choose(5t,ones-t) ways. Every such string has a
    unique parse, so sum over t. The empty boundary contributes one at (0,0).
    Uses O(n) binomial evaluations and O(1) retained big integers; binomial
    arithmetic cost and integer storage grow with n.
    """
    if n == 0:
        return int(ones == 0)
    if n < 0 or ones < 0 or ones > n:
        return 0
    return sum(math.comb(n - 5*t - 1, t - 1) * math.comb(5*t, ones - t)
               for t in range(1, n // 6 + 1) if 0 <= ones - t <= 5*t)


def fixed_density_null(n, ones):
    """Exact finite uniform-fixed-one-count event counts, including extremes.

    Nonempty residual is the complement of a boundary at N, including long
    rejected candidates. An all-one residual must have length 1..5; six ones
    would complete a token. Its prefix must end at a complete boundary.
    """
    if type(n) is not int or type(ones) is not int or not 0 <= ones <= n:
        raise ValueError("require integer n >= 0 and 0 <= ones <= n")
    total = math.comb(n, ones)
    empty = boundary_count(n, ones)
    nonempty = total - empty
    all_one = sum(boundary_count(n-r, ones-r) for r in range(1, min(n, 5) + 1))
    return {"window_bits": n, "one_bits": ones, "total_strings": total,
            "empty_residual_strings": empty, "nonempty_residual_strings": nonempty,
            "nonempty_all_one_residual_strings": all_one,
            "nonempty_probability": nonempty / total,
            "nonempty_all_one_probability": all_one / total,
            "all_one_given_nonempty": all_one / nonempty if nonempty else None}


def fixed_density_lengths(n, ones):
    """Exact length counts under uniform N-bit/K-one permutations.

    B(x,y)=(1-x)/(1-x-x**6*y*(1+y)**5) counts complete boundaries,
    where x marks bits and y marks ones. Its coefficient recurrence is
    B[n,k]=B[n-1,k]+sum(comb(5,j)*B[n-6,k-1-j], j=0..5), except
    B[0,0]=1 and B[1,k]=0. Seven rolling coefficient rows suffice.
    A rejected residual r has r-min(r,5) forced leading zeros and
    min(r,5) arbitrary final bits. Convolution gives every length count.
    O(n*ones) integer operations, O(ones+n) stored integers; integer
    arithmetic/storage costs grow with n. No arrays of sample bits used.
    """
    if type(n) is not int or type(ones) is not int or not 0 <= ones <= n:
        raise ValueError("require integer n >= 0 and 0 <= ones <= n")
    if ones in (0, n):
        counts = [0] * (n + 1)
        counts[n if ones == 0 else n % 6] = 1
        return {"window_bits": n, "one_bits": ones, "total_strings": 1,
                "residual_length_strings": counts,
                "residual_length_pmf": [float(value) for value in counts],
                "count_sum": 1}
    rows = [[0] * (ones + 1) for _ in range(7)]
    counts = [0] * (n + 1)
    coefficients = (1, 5, 10, 10, 5, 1)
    for length in range(n + 1):
        current = rows[length % 7]
        if length == 0:
            current[0] = 1
        elif length == 1:
            current[:] = [0] * (ones + 1)
        else:
            previous = rows[(length - 1) % 7]
            current[:] = previous
            if length >= 6:
                earlier = rows[(length - 6) % 7]
                for k in range(1, min(ones, length) + 1):
                    current[k] += sum(coefficients[j] * earlier[k-1-j]
                                      for j in range(min(5, k-1) + 1))
        r = n - length
        free = min(r, 5)
        counts[r] = sum(math.comb(free, j) * current[ones-j]
                        for j in range(min(free, ones) + 1))
    total = math.comb(n, ones)
    if sum(counts) != total:
        raise ArithmeticError("fixed-density length counts do not normalize")
    return {"window_bits": n, "one_bits": ones, "total_strings": total,
            "residual_length_strings": counts,
            "residual_length_pmf": [value / total for value in counts],
            "count_sum": sum(counts)}


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


def window_report(payload, start, fixed_density=False, fixed_density_length=False):
    # Windows are byte-aligned and fixed at 512 bytes; never emit their bits.
    bits = "".join(format(b, "08b") for b in payload[start // 8:(start + WINDOW_BITS) // 8])
    if len(bits) != WINDOW_BITS:
        raise ValueError("incomplete window")
    ones = bits.count("1")
    result = {"start_bit": start, "end_bit_exclusive": start + WINDOW_BITS,
            "window_bits": WINDOW_BITS, "one_bits": ones,
            "candidate_parse": scan_window(bits),
            "fair_null": residual_null(WINDOW_BITS, 0.5),
            "fitted_in_sample_null": residual_null(WINDOW_BITS, ones / WINDOW_BITS)}
    if fixed_density:
        result["fixed_density_null"] = fixed_density_null(WINDOW_BITS, ones)
    if fixed_density_length:
        result["fixed_density_lengths"] = fixed_density_lengths(WINDOW_BITS, ones)
    return result


def report(sid, name, path, fixed_density=False, fixed_density_length=False):
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
            "windows": {"prefix": window_report(payload, 0, fixed_density, fixed_density_length),
                        "tail": window_report(payload, count * 8 - WINDOW_BITS, fixed_density, fixed_density_length)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "FILE"))
    parser.add_argument("--fixed-density", action="store_true",
                        help="Add exact uniform-fixed-one-count event probabilities")
    parser.add_argument("--fixed-density-lengths", action="store_true",
                        help="Add exact uniform-fixed-one-count residual-length PMF")
    args = parser.parse_args(argv)
    ids = [sid for sid, _, _ in args.sample]
    if any(not sid.isascii() or not sid.isdecimal() or int(sid) <= 0 for sid in ids):
        parser.error("sample IDs must be positive ASCII decimal integers")
    if len(set(map(int, ids))) != len(ids):
        parser.error("sample IDs must be distinct")
    samples, errors = [], []
    for sid, name, path in args.sample:
        try:
            samples.append(report(sid, name, path, args.fixed_density, args.fixed_density_lengths))
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
