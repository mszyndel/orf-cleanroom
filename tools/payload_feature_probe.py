#!/usr/bin/env python3
"""Parser-independent raw-bit window features, a bounded first step for #299.

Reads files and prints aggregate JSON only. No token parser, pixels, clustering,
normalization or variant assignment. Each --sample is ID PUBLIC_NAME SHA256 PATH;
SHA256 must come from a retained verified licence record. A matching hash proves
content identity, not licence: the caller must establish provenance separately.
Windows are disjoint, byte-aligned, equal-sized and evenly spaced including both
payload endpoints. Run spectra include window-clipped edge runs, capped at 16.
Transitions count adjacent MSB-first bits inside each window, never across gaps.
Use file/capture counts, not windows or bits, as independent replication.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, first, size_class


def features(buf):
    """Exact integer aggregates plus plug-in byte entropy in bits/byte."""
    if not buf:
        raise ValueError("empty window")
    hist = Counter(buf)
    ones = sum(bin(value).count("1") * n for value, n in hist.items())
    transitions = [0] * 4  # 00, 01, 10, 11
    runs = [[0] * 16 for _ in range(2)]
    previous, length, first_length = None, 0, None
    maximum = [0, 0]
    for byte in buf:
        for shift in range(7, -1, -1):
            bit = (byte >> shift) & 1
            if previous is not None:
                transitions[2 * previous + bit] += 1
            if bit == previous:
                length += 1
            else:
                if previous is not None:
                    runs[previous][min(length, 16) - 1] += 1
                    maximum[previous] = max(maximum[previous], length)
                    if first_length is None:
                        first_length = length
                previous, length = bit, 1
    runs[previous][min(length, 16) - 1] += 1
    maximum[previous] = max(maximum[previous], length)
    if first_length is None:
        first_length = length
    bits = len(buf) * 8
    return {
        "bytes": len(buf), "ones": ones, "one_fraction": ones / bits,
        "transition_counts_00_01_10_11": transitions,
        "transition_fraction": (transitions[1] + transitions[2]) / (bits - 1),
        "byte_entropy_bits": -sum((n / len(buf)) * math.log2(n / len(buf))
                                  for n in hist.values()),
        "run_counts_by_bit_length_1_to_15_then_ge16": runs,
        "longest_run_by_bit": maximum,
        "first_bit": buf[0] >> 7, "first_run_bits": first_length,
        "last_bit": previous, "last_run_bits": length,
    }


def window_starts(payload_bytes, window_bytes, windows):
    if windows < 2 or window_bytes < 1 or payload_bytes < windows * window_bytes:
        raise ValueError("need at least two full disjoint windows")
    return [i * (payload_bytes - window_bytes) // (windows - 1)
            for i in range(windows)]


def report(sample_id, name, expected_sha256, path, window_bytes, windows):
    with open(path, "rb") as stream:
        data = stream.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256:
        raise ValueError("retained hash mismatch")
    ifds = list(Tiff(data).all_ifds())
    if not ifds:
        raise ValueError("no image IFD")
    best = max(ifds, key=lambda tags: sum(tags.get(0x117) or [0]))
    offsets, lengths = best.get(0x111), best.get(0x117)
    if not isinstance(offsets, list) or not isinstance(lengths, list):
        raise ValueError("missing strip geometry")
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("only one contiguous strip supported")
    offset, count = offsets[0], lengths[0]
    width, height = first(best, 0x100), first(best, 0x101)
    if not isinstance(width, int) or not isinstance(height, int) or min(width, height) < 1:
        raise ValueError("invalid dimensions")
    if offset < 0 or count < 1 or offset + count > len(data):
        raise ValueError("invalid strip extent")
    starts = window_starts(count, window_bytes, windows)
    return {
        "pixls_id": sample_id, "pixls_name": name, "sha256": digest,
        "payload_width": width, "payload_height": height,
        "payload_bytes": count, "payload_offset": offset,
        "payload_bits_per_pixel": count * 8 / (width * height),
        "size_class": size_class(count, width, height),
        "windows": [{"payload_byte_start": start,
                     "features": features(data[offset + start:offset + start + window_bytes])}
                    for start in starts],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", nargs=4, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "SHA256", "PATH"))
    parser.add_argument("--window-bytes", type=int, default=65536)
    parser.add_argument("--windows", type=int, default=3)
    args = parser.parse_args(argv)
    if args.window_bytes < 1 or args.windows < 2:
        parser.error("positive window size and at least two windows required")
    ids, hashes = set(), set()
    for sample_id, name, digest, path in args.sample:
        if not re.fullmatch(r"[1-9][0-9]*", sample_id) or sample_id in ids:
            parser.error("sample IDs must be unique positive integers")
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or digest in hashes:
            parser.error("sample hashes must be unique lowercase SHA256 values")
        if not name or any(ord(ch) < 32 for ch in name):
            parser.error("public name required without control characters")
        ids.add(sample_id)
        hashes.add(digest)
    rows, errors = [], []
    for sample_id, name, digest, path in args.sample:
        try:
            rows.append(report(sample_id, name, digest, path,
                               args.window_bytes, args.windows))
        except (OSError, ValueError, TypeError, KeyError, IndexError, OverflowError, struct.error) as exc:
            errors.append({"pixls_id": sample_id, "error_type": type(exc).__name__})
    sources = {}
    for filename in ("payload_feature_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), filename), "rb") as stream:
            sources[filename] = hashlib.sha256(stream.read()).hexdigest()
    print(json.dumps({"schema": "raw-bit-window-features-v1", "sources_sha256": sources,
                      "window_bytes": args.window_bytes, "window_count": args.windows,
                      "samples": rows, "errors": errors}, sort_keys=True, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
