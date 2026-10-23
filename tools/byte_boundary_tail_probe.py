#!/usr/bin/env python3
"""Empirical byte-boundary trailing-one reference for lead #87.

Count runs ending at every payload byte boundary, including runs across bytes.
Compare the final run to all earlier boundaries in that SAME payload. This
descriptive reference assumes no independence or exchangeability and supplies
no calibrated p-value, padding rule, token framing or decoder result.
Standard library, Python 3.8+. Reads inputs and prints aggregates only.
Licence/hash verification against retained CC0 records is a prerequisite.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class


def byte_tail(value):
    count = 0
    while value & 1:
        count += 1
        value >>= 1
    return count


BYTE_TAIL = tuple(byte_tail(value) for value in range(256))


def boundary_report(payload):
    """Count capped byte tails, then restore runs crossing each 0xff byte."""
    if not payload:
        raise ValueError("empty payload")
    counts = Counter()
    for value, frequency in Counter(payload).items():
        counts[BYTE_TAIL[value]] += frequency
    previous_index, previous_run = -2, 0
    position = payload.find(b"\xff")
    while position >= 0:
        if position == previous_index + 1:
            run = previous_run + 8
        else:
            run = (BYTE_TAIL[payload[position-1]] if position else 0) + 8
        counts[8] -= 1
        counts[run] += 1
        previous_index, previous_run = position, run
        position = payload.find(b"\xff", position + 1)
    final = previous_run if previous_index == len(payload)-1 else BYTE_TAIL[payload[-1]]
    all_counts = {k: v for k, v in sorted(counts.items()) if v}
    counts[final] -= 1
    earlier = {k: v for k, v in sorted(counts.items()) if v}
    n = len(payload)-1
    less = sum(v for k, v in earlier.items() if k < final)
    equal = earlier.get(final, 0)
    greater = sum(v for k, v in earlier.items() if k > final)
    positive = n - earlier.get(0, 0)
    return {"payload_bytes": len(payload), "final_trailing_ones": final,
            "all_boundary_histogram": all_counts,
            "earlier_boundary_histogram": earlier,
            "earlier_boundaries": n, "earlier_less": less,
            "earlier_equal": equal, "earlier_greater": greater,
            "earlier_positive": positive,
            "earlier_positive_fraction": positive / n if n else None,
            "earlier_at_least_final": equal + greater,
            "earlier_at_least_final_fraction": (equal+greater) / n if n else None}


def report(sid, name, path):
    with open(path, "rb") as stream:
        data = stream.read()
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("requires one contiguous strip")
    offset, count = offsets[0], lengths[0]
    width, height = best[0x100][0], best[0x101][0]
    if offset < 0 or count <= 0 or offset+count > len(data):
        raise ValueError("payload out of bounds or empty")
    if width <= 0 or height <= 0 or size_class(count, width, height) != "variable":
        raise ValueError("requires positive variable-size geometry")
    return {"pixls_id": sid, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "payload_width": width, "payload_height": height,
            "payload_offset": offset, "size_class": "variable",
            "variant": "unassigned", "compression_tag": (best.get(0x103) or [None])[0],
            "statistics": boundary_report(data[offset:offset+count])}


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
    for source in ("byte_boundary_tail_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), source), "rb") as stream:
            sources[source] = hashlib.sha256(stream.read()).hexdigest()
    print(json.dumps({"source_sha256": sources, "python_version": sys.version.split()[0],
                      "samples": samples, "errors": errors}, indent=2, allow_nan=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
