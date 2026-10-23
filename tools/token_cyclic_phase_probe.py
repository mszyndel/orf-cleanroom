#!/usr/bin/env python3
"""Cyclic within-candidate-row q profiles for lead #144; aggregates only.

For every phase p, the head is positions (p+j) mod S for j=0..head-1
WITHIN each original row r*S..(r+1)*S-1. Thus every phase uses exactly
the same tokens. This differs from shifting contiguous row boundaries.
All phases and extrema/ties are descriptive: no null, significance, stride
search, physical rows, true grammar or decode is established. q>=17 is
retained, q is capped at 40, and no extra escape bits are skipped.
Original code, standard library only, Python 3.8+. Reads/prints only.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_band_profile import scan_q
from orf_signature import Tiff, size_class


def cyclic_profile(qs, stride, start_row, rows, head):
    """All phase-wise exact moments of A=S*head_sum-head*row_sum."""
    if not (stride > head >= 1 and start_row >= 0 and rows >= 2):
        raise ValueError("require stride>head>=1, start-row>=0, rows>=2")
    count = min(rows, max(0, len(qs) // stride - start_row))
    heads, sums, squares = [0] * stride, [0] * stride, [0] * stride
    total = escapes = 0
    for r in range(start_row, start_row + count):
        row = qs[r * stride:(r + 1) * stride]
        row_sum = sum(row)
        total += row_sum
        escapes += sum(q >= 17 for q in row)
        hs = sum(row[:head])
        for p in range(stride):
            a = stride * hs - head * row_sum
            heads[p] += hs
            sums[p] += a
            squares[p] += a * a
            hs += row[(p + head) % stride] - row[p]
    den = head * (stride - head)
    means, scores = [], []
    for a, a2 in zip(sums, squares):
        variance_num = count * a2 - a * a
        means.append(a / (count * den) if count else None)
        scores.append(a * math.sqrt(count - 1) / math.sqrt(variance_num)
                      if count >= 2 and variance_num > 0 else None)
    def extrema(values):
        finite = [x for x in values if x is not None]
        if not finite:
            return dict(minimum=None, maximum=None, min_phases=[], max_phases=[])
        lo, hi = min(finite), max(finite)
        return dict(minimum=lo, maximum=hi,
                    min_phases=[p for p, x in enumerate(values) if x == lo],
                    max_phases=[p for p, x in enumerate(values) if x == hi])
    return dict(stride=stride, head=head, start_candidate_row=start_row,
                start_token=start_row * stride, requested_rows=rows,
                complete_rows=count, complete=count == rows,
                total_q_capped40=total, escape_tokens=escapes,
                contrast_denominator=den, sum_head_q_by_phase=heads,
                sum_rest_q_by_phase=[total - h for h in heads],
                sum_contrast_numerator_by_phase=sums,
                sum_squared_contrast_numerator_by_phase=squares,
                mean_head_minus_rest_by_phase=means,
                signed_mean_over_se_by_phase=scores,
                mean_extrema=extrema(means), score_extrema=extrema(scores))


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
    if size_class(size, w, h) != "variable" or best.get(0x103) != [1]:
        raise ValueError("require variable-size compression-tag-1 payload")
    limit = (max(starts) + rows) * stride
    qs, bits = scan_q(data[off:off + size], limit)
    return dict(sha256=actual, payload_width=w, payload_height=h,
                payload_bytes=size, size_class="variable", compression_tag=1,
                requested_tokens=limit, parsed_tokens=len(qs), consumed_bits=bits,
                token_shortfall=limit - len(qs),
                bands=[cyclic_profile(qs, stride, start, rows, head) for start in starts])


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
    if args.rows < 2 or args.head < 1 or args.stride <= args.head or min(starts) < 0:
        ap.error("require rows>=2, stride>head>=1, start-row>=0")
    ids = [sample[0] for sample in args.sample]
    if len(ids) != len(set(ids)):
        ap.error("duplicate public sample IDs")
    samples = []
    for sid, name, digest, path in args.sample:
        entry = dict(pixls_id=sid, pixls_name=name)
        try:
            if not sid.isdecimal() or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
                raise ValueError("invalid public ID or SHA-256")
            entry.update(measure(path, digest, args.stride, starts, args.rows, args.head))
            entry["ok"] = entry["token_shortfall"] == 0
        except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error) as exc:
            entry.update(ok=False, error=type(exc).__name__)
        samples.append(entry)
    source_hashes = {}
    for name in ("token_cyclic_phase_probe.py", "token_band_profile.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), name), "rb") as source:
            source_hashes[name] = hashlib.sha256(source.read()).hexdigest()
    print(json.dumps(dict(schema_version=1, method="cyclic-within-fixed-row-q40",
                          escape_extra_bits=0, source_sha256=source_hashes,
                          samples=samples), indent=2, allow_nan=False))
    return int(any(not sample["ok"] for sample in samples))


if __name__ == "__main__":
    sys.exit(main())
