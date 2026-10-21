#!/usr/bin/env python3
"""Describe token-index phase given a fixed bit context (#30; #11/#153/#179).

Stdlib Python 3.8+. Aggregate JSON only; no images or decoding. Fixed first
262144 complete candidate tokens, payload bit zero, zero extra escape bits.
For t>=2 retain only triples t-2..t without q>=17; preserve absolute indices.
Target Y=b2(t), context C=2*b4(t-1)+b2(t-2), phase P=t mod m, m=2..8.
Emit complete C-by-P-by-Y tables, stratum sizes, matched marginal I(Y;P),
and unsmoothed plug-in I(Y;P|C). Empty statistics are null. These are
descriptive scores, without null correction, thresholds or significance.
Stratification and sparse cells can increase finite-sample bias. This is
not the historical private context-gain metric or a physical-column test.
The candidate parse and post-escape framing remain unverified; excluding
triples containing escapes cannot repair an incorrect post-escape parse.
Check public sample licences separately before use.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class  # noqa: E402
from suffix_joint_probe import LIMIT, scan_prefix  # noqa: E402
from token_phase_probe import entropy  # noqa: E402

MODULI = tuple(range(2, 9))


def table_statistics(table):
    """Return entropy difference and marginal MI on the exact same observations."""
    if len(table) != 4 or not table[0]:
        raise ValueError("four nonempty context strata required")
    m = len(table[0])
    if any(len(stratum) != m for stratum in table):
        raise ValueError("inconsistent phase dimension")
    if any(len(row) != 2 or any(type(c) is not int or c < 0 for c in row)
           for stratum in table for row in stratum):
        raise ValueError("nonnegative integer binary counts required")
    context_counts = [sum(map(sum, stratum)) for stratum in table]
    n = sum(context_counts)
    pooled = [[sum(table[c][p][y] for c in range(4)) for y in range(2)]
              for p in range(m)]
    h_c = (sum(nc / n * entropy([sum(row[y] for row in stratum) for y in range(2)])
               for nc, stratum in zip(context_counts, table) if nc) if n else None)
    h_cp = (sum(sum(row) / n * entropy(row) for stratum in table
                for row in stratum if sum(row)) if n else None)
    h = entropy([sum(row[y] for row in pooled) for y in range(2)])
    h_p = (sum(sum(row) / n * entropy(row) for row in pooled if sum(row)) if n else None)
    return {"context_by_phase_by_target": table, "observations": n,
            "context_counts": context_counts,
            "context_phase_counts": [[sum(row) for row in stratum] for stratum in table],
            "target_entropy_bits": h, "target_given_phase_entropy_bits": h_p,
            "target_given_context_entropy_bits": h_c,
            "target_given_context_phase_entropy_bits": h_cp,
            "plugin_phase_mi_bits": h - h_p if n else None,
            "plugin_conditional_phase_mi_bits": h_c - h_cp if n else None}


def phase_context_statistics(tokens):
    for q, suffix in tokens:
        if type(q) is not int or q < 0 or type(suffix) is not int or not 0 <= suffix < 32:
            raise ValueError("invalid candidate token")
    tables = {m: [[[0, 0] for _ in range(m)] for _ in range(4)] for m in MODULI}
    omitted = 0
    for t in range(2, len(tokens)):
        if any(tokens[j][0] >= 17 for j in range(t - 2, t + 1)):
            omitted += 1
            continue
        c = 2 * ((tokens[t - 1][1] >> 4) & 1) + ((tokens[t - 2][1] >> 2) & 1)
        y = (tokens[t][1] >> 2) & 1
        for m, table in tables.items():
            table[c][t % m][y] += 1
    return {"parsed_tokens": len(tokens), "initial_context_unavailable": min(2, len(tokens)),
            "escape_tokens": sum(q >= 17 for q, _ in tokens),
            "escape_omitted_triples": omitted,
            "retained_triples": max(0, len(tokens) - 2) - omitted,
            "moduli": [dict(modulus=m, **table_statistics(table)) for m, table in tables.items()]}


def report(sample_id, name, path):
    with open(path, "rb") as handle:
        data = handle.read()
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("one contiguous strip required")
    off, count = offsets[0], lengths[0]
    if off < 0 or count <= 0 or off + count > len(data):
        raise ValueError("payload out of bounds")
    w, h = best[0x100][0], best[0x101][0]
    if w <= 0 or h <= 0 or size_class(count, w, h) != "variable":
        raise ValueError("positive variable-size payload required")
    tokens, end = scan_prefix(data[off:off + count], LIMIT)
    return {"pixls_id": sample_id, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(), "variant": "unassigned",
            "payload_w": w, "payload_h": h, "payload_offset": off,
            "payload_bytes": count, "size_class": "variable",
            "compression_tag": best.get(0x103), "bits_consumed": end,
            "requested_tokens": LIMIT, "prefix_shortfall": LIMIT - len(tokens),
            "statistics": phase_context_statistics(tokens)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", metavar=("ID", "PUBLIC_NAME", "FILE"), required=True)
    args = parser.parse_args()
    ids = [sample[0] for sample in args.sample]
    if any(not x.isascii() or not x.isdecimal() or int(x) <= 0 for x in ids) or len(set(ids)) != len(ids):
        parser.error("sample IDs must be distinct positive ASCII decimal integers")
    reports, failures = [], []
    for sample_id, name, path in args.sample:
        try:
            reports.append(report(sample_id, name, path))
        except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
            failures.append({"pixls_id": sample_id, "error": type(exc).__name__})
    sources = {}
    for filename in ("token_phase_context_probe.py", "token_phase_probe.py", "suffix_joint_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), filename), "rb") as handle:
            sources[filename] = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps({"source_sha256": sources, "python_version": sys.version.split()[0],
                      "escape_extra_bits": 0, "requested_prefix_tokens": LIMIT,
                      "samples": reports, "failures": failures}, indent=2, allow_nan=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
