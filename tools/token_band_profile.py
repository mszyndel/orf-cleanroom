#!/usr/bin/env python3
"""Fixed-stride later-band q profiles for lead #144; aggregate JSON only.

Candidate boundaries are absolute token indices r*S from payload bit zero.
No phase refit, later-band stride search, physical row inference or calibrated
significance is performed. q is capped at 40; q>=17 tokens remain in profiles.
The candidate unary-plus-five syntax (#11) uses zero extra escape bits, whose
actual meaning is unresolved. Signed standardized means are descriptive only.
Reads files and prints numbers; standard library only, Python 3.8+.
"""
import argparse
import array
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class


def scan_q(buf, limit):
    """Bounded independent bit reader: retain complete q-zero/one/5-bit tokens."""
    qs = array.array("B")
    pos, nbits = 0, len(buf) * 8
    while len(qs) < limit and pos + 6 <= nbits:
        start = pos
        while pos < nbits and not ((buf[pos >> 3] >> (7 - (pos & 7))) & 1):
            pos += 1
        if pos + 6 > nbits:
            pos = start
            break
        qs.append(min(pos - start, 40))
        pos += 6
    return qs, pos


def profile(qs, stride, start_row, rows, head):
    """Integer moments of A=head_sum*(S-head)-rest_sum*head, per row."""
    if stride <= head or head < 1 or rows < 2 or start_row < 0:
        raise ValueError("require stride>head>=1, rows>=2 and start-row>=0")
    available = min(rows, max(0, len(qs) // stride - start_row))
    sum_a = sum_a2 = sum_head = sum_rest = escapes = 0
    view = memoryview(qs)
    for row in range(start_row, start_row + available):
        lo = row * stride
        h = view[lo:lo + head]
        r = view[lo + head:lo + stride]
        hs, rs = sum(h), sum(r)
        a = hs * (stride - head) - rs * head
        sum_a += a
        sum_a2 += a * a
        sum_head += hs
        sum_rest += rs
        escapes += sum(q >= 17 for q in h) + sum(q >= 17 for q in r)
    den = head * (stride - head)
    numerator = available * sum_a2 - sum_a * sum_a
    score = (sum_a * math.sqrt(available - 1) / math.sqrt(numerator)
             if available >= 2 and numerator > 0 else None)
    return dict(stride=stride, start_candidate_row=start_row,
                start_token=start_row * stride,
                requested_rows=rows, complete_rows=available,
                complete=available == rows, head=head,
                sum_head_q_capped40=sum_head, sum_rest_q_capped40=sum_rest,
                escape_tokens=escapes, sum_contrast_numerator=sum_a,
                sum_squared_contrast_numerator=sum_a2,
                contrast_denominator=den,
                mean_head_minus_rest=(sum_a / (available * den) if available else None),
                signed_mean_over_se=score,
                score_defined=score is not None)


def measure(path, expected_sha256, strides, starts, rows, head):
    with open(path, "rb") as source:
        data = source.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256.lower():
        raise ValueError("SHA-256 does not match supplied verified record")
    t = Tiff(data)
    best = max(t.all_ifds(), key=lambda d: sum(d.get(0x117) or [0]))
    w, h = best[0x100][0], best[0x101][0]
    offsets, sizes = best[0x111], best[0x117]
    if len(offsets) != 1 or len(sizes) != 1:
        raise ValueError("only a single contiguous strip is supported")
    off, size = offsets[0], sizes[0]
    if off < 0 or size <= 0 or off + size > len(data):
        raise ValueError("payload strip is outside file")
    if size_class(size, w, h) != "variable":
        raise ValueError("fixed-size payload is outside this candidate-token probe")
    limit = max((start + rows) * stride for start in starts for stride in strides)
    qs, bits = scan_q(data[off:off + size], limit)
    bands = [profile(qs, stride, start, rows, head)
             for stride in strides for start in starts]
    return dict(sha256=actual, payload_width=w, payload_height=h,
                payload_bytes=size, size_class="variable",
                compression_tag=best.get(0x103), requested_tokens=limit,
                parsed_tokens=len(qs), consumed_bits=bits,
                token_shortfall=limit - len(qs), bands=bands)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", nargs=4, action="append", required=True,
                    metavar=("ID", "NAME", "SHA256", "FILE"),
                    help="supply public identity and retained verified hash")
    ap.add_argument("--stride", type=int, action="append", required=True)
    ap.add_argument("--start-row", type=int, action="append", default=None)
    ap.add_argument("--rows", type=int, default=300)
    ap.add_argument("--head", type=int, default=32)
    args = ap.parse_args(argv)
    starts = sorted(set(args.start_row if args.start_row is not None else [0, 1000, 2000]))
    strides = sorted(set(args.stride))
    if args.rows < 2 or args.head < 1 or min(starts) < 0 or min(strides) <= args.head:
        ap.error("require rows>=2, head>=1, start-row>=0, stride>head")
    samples, failed = [], False
    for sid, name, digest, path in args.sample:
        entry = dict(pixls_id=sid, pixls_name=name)
        try:
            if not sid.isdecimal() or len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
                raise ValueError("invalid public ID or SHA-256")
            entry.update(measure(path, digest, strides, starts, args.rows, args.head))
            entry["ok"] = entry["token_shortfall"] == 0
        except (OSError, ValueError, KeyError, TypeError, IndexError, struct.error) as exc:
            # No local path in aggregate output; every supplied identity is retained.
            entry.update(ok=False, error=type(exc).__name__)
        failed = failed or not entry["ok"]
        samples.append(entry)
    print(json.dumps(dict(schema_version=1, method="fixed-absolute-token-phase-q40",
                          escape_extra_bits=0, samples=samples), indent=2, allow_nan=False))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
