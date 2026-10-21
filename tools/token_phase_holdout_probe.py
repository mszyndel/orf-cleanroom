#!/usr/bin/env python3
"""Held-out cyclic-phase diagnostic for #144; aggregate JSON only.

Select the lowest phase maximizing capped-q mean contrast on the first half
of each fixed-stride band; evaluate that frozen phase on the second half.
99 independent per-row cyclic rotations provide a descriptive conditional
reference, not a p-value, calibrated significance or physical row evidence.
Rows are absolute candidate token blocks; cyclic heads wrap inside each row.
Candidate unary-plus-five syntax, q capped40, escapes retained, no extra skip.
Original stdlib code, Python3.8+. Reads files and prints aggregates only.
"""
import argparse
import hashlib
import json
import math
import os
import random
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_cyclic_phase_probe import cyclic_profile
from token_band_profile import scan_q
from orf_signature import Tiff, size_class


def moments(values, denominator):
    n, total = len(values), sum(values)
    squares = sum(v * v for v in values)
    variance_num = n * squares - total * total
    return dict(rows=n, sum_contrast_numerator=total,
                sum_squared_contrast_numerator=squares,
                contrast_denominator=denominator,
                mean_head_minus_rest=total / (n * denominator) if n else None,
                signed_mean_over_se=(total * math.sqrt(n - 1) / math.sqrt(variance_num)
                                     if n >= 2 and variance_num > 0 else None))


def contrast(row, phase, head):
    hs = sum(row[(phase + j) % len(row)] for j in range(head))
    return len(row) * hs - head * sum(row)


def holdout(qs, stride, start, rows=300, head=32):
    if not (stride > head >= 1 and start >= 0 and rows >= 4 and rows % 2 == 0):
        raise ValueError("require stride>head>=1, start>=0 and even rows>=4")
    available = min(rows, max(0, len(qs) // stride - start))
    out = dict(stride=stride, start_candidate_row=start, start_token=start * stride,
               requested_rows=rows, complete_rows=available, complete=available == rows,
               head=head)
    if available != rows:
        # Do not select on, or silently shorten, an incomplete band.
        return out
    half = rows // 2
    train = cyclic_profile(qs, stride, start, half, head)
    sums = train["sum_contrast_numerator_by_phase"]
    maximum = max(sums)
    ties = [p for p, value in enumerate(sums) if value == maximum]
    phase = ties[0]
    test_rows = [qs[r * stride:(r + 1) * stride]
                 for r in range(start + half, start + rows)]
    denominator = head * (stride - head)
    observed = moments([contrast(row, phase, head) for row in test_rows], denominator)
    baseline = moments([contrast(row, 0, head) for row in test_rows], denominator)
    seed = 20261021 + start
    rng = random.Random(seed)
    controls = []
    for _ in range(99):
        # Replicate-major, then row-major draws; same row content, shifted head.
        controls.append(sum(contrast(row, (phase + rng.randrange(stride)) % stride, head)
                            for row in test_rows))
    out.update(train_rows=half, test_start_candidate_row=start + half,
               train_total_q_capped40=train["total_q_capped40"],
               train_escape_tokens=train["escape_tokens"],
               train_contrast_denominator=denominator,
               train_sum_contrast_numerator_by_phase=sums,
               train_sum_squared_contrast_numerator_by_phase=
               train["sum_squared_contrast_numerator_by_phase"],
               train_maximum_mean_phases=ties, selected_phase=phase,
               test_total_q_capped40=sum(map(sum, test_rows)),
               test_escape_tokens=sum(q >= 17 for row in test_rows for q in row),
               test_selected=observed, test_phase_zero=baseline,
               rotation_seed=seed, rotation_replicates=99,
               rotation_sum_contrast_numerators=controls,
               rotation_greater_or_equal_count=sum(v >= observed["sum_contrast_numerator"]
                                                   for v in controls))
    return out


def measure(path, digest, stride, starts, rows, head):
    with open(path, "rb") as source:
        data = source.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != digest.lower():
        raise ValueError("SHA-256 differs from supplied verified record")
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or [0]))
    w, h = best[0x100][0], best[0x101][0]
    offsets, sizes = best[0x111], best[0x117]
    if len(offsets) != 1 or len(sizes) != 1:
        raise ValueError("require single contiguous strip")
    off, size = offsets[0], sizes[0]
    if off < 0 or size <= 0 or off + size > len(data):
        raise ValueError("payload outside file")
    if w <= 0 or h <= 0 or size_class(size, w, h) != "variable" or best.get(0x103) != [1]:
        raise ValueError("require positive variable-size compression-tag-1 payload")
    limit = (max(starts) + rows) * stride
    qs, bits = scan_q(data[off:off + size], limit)
    return dict(sha256=actual, payload_width=w, payload_height=h,
                payload_bytes=size, size_class="variable", compression_tag=1,
                variant="unassigned", requested_tokens=limit, parsed_tokens=len(qs),
                consumed_bits=bits, token_shortfall=limit - len(qs),
                bands=[holdout(qs, stride, start, rows, head) for start in starts])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", nargs=4, action="append", required=True,
                    metavar=("ID", "NAME", "SHA256", "FILE"))
    ap.add_argument("--stride", type=int, required=True)
    ap.add_argument("--start-row", type=int, action="append")
    ap.add_argument("--rows", type=int, default=300)
    ap.add_argument("--head", type=int, default=32)
    args = ap.parse_args(argv)
    starts = sorted(set(args.start_row if args.start_row is not None else [0, 1000, 2000]))
    if args.rows < 4 or args.rows % 2 or args.head < 1 or args.stride <= args.head or min(starts) < 0:
        ap.error("require even rows>=4, stride>head>=1, start-row>=0")
    ids = [sample[0] for sample in args.sample]
    if len(ids) != len(set(ids)):
        ap.error("duplicate public sample IDs")
    samples = []
    for sid, name, digest, path in args.sample:
        entry = dict(pixls_id=sid, pixls_name=name)
        try:
            if (not sid.isascii() or not sid.isdecimal() or int(sid) <= 0 or len(digest) != 64
                    or any(c not in "0123456789abcdefABCDEF" for c in digest)):
                raise ValueError("invalid public ID or SHA-256")
            entry.update(measure(path, digest, args.stride, starts, args.rows, args.head))
            entry["ok"] = entry["token_shortfall"] == 0
        except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error) as exc:
            entry.update(ok=False, error=type(exc).__name__)
        samples.append(entry)
    hashes = {}
    for name in ("token_phase_holdout_probe.py", "token_cyclic_phase_probe.py",
                 "token_band_profile.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), name), "rb") as source:
            hashes[name] = hashlib.sha256(source.read()).hexdigest()
    print(json.dumps(dict(schema_version=1, method="train-selected-cyclic-phase-q40",
                          python_version=sys.version.split()[0], escape_extra_bits=0,
                          source_sha256=hashes, samples=samples), indent=2, allow_nan=False))
    return int(any(not sample["ok"] for sample in samples))


if __name__ == "__main__":
    sys.exit(main())
