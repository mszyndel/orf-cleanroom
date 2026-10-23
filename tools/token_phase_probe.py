#!/usr/bin/env python3
"""Report candidate token-phase contingency tables for lead #30 (builds on #11).

Stdlib Python 3.8+. Aggregate JSON only; no decoding or preview access.
Fixed design: first 262144 complete candidate tokens from payload bit zero,
escape-extra=0. Omit q>=17 symbols without renumbering absolute indices.
For every modulus 2..8, report counts of phase by joint symbol 2*b4+b2,
H(symbol), H(symbol|phase), and plug-in I(symbol;phase), all in bits.
No shuffle, bias correction, significance threshold or physical row/column
interpretation is supplied. Finite samples can have positive MI under a null;
zero MI does not exclude context-dependent or other phase effects. This is
not the historical conditional-context gain metric or its private cohort.
The candidate parse and post-escape framing remain unverified.

Licence-check public samples separately before use. A single contiguous,
in-bounds, variable-size strip is required; compression tag alone is not a
variant selector. The source hashes pin this tool and its repository imports.
Exit 1 for any input failure or nonzero prefix_shortfall; available short-prefix
statistics remain visible but do not fulfill the declared fixed-prefix design.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class  # noqa: E402
from suffix_joint_probe import LIMIT, scan_prefix  # noqa: E402

MODULI = tuple(range(2, 9))


def entropy(counts):
    total = sum(counts)
    if not total:
        return None
    return -sum(c / total * math.log2(c / total) for c in counts if c)


def phase_statistics(tokens):
    """Keep original indices, including positions occupied by omitted escapes."""
    tables = {m: [[0] * 4 for _ in range(m)] for m in MODULI}
    omitted = 0
    for index, (q, suffix) in enumerate(tokens):
        if type(q) is not int or q < 0 or type(suffix) is not int or not 0 <= suffix < 32:
            raise ValueError("invalid candidate token")
        if q >= 17:
            omitted += 1
            continue
        symbol = 2 * ((suffix >> 4) & 1) + ((suffix >> 2) & 1)
        for m, table in tables.items():
            table[index % m][symbol] += 1
    retained = len(tokens) - omitted
    results = []
    for m, table in tables.items():
        totals = [sum(row) for row in table]
        symbols = [sum(row[s] for row in table) for s in range(4)]
        h = entropy(symbols)
        conditional = (sum(n / retained * entropy(row) for n, row in zip(totals, table) if n)
                       if retained else None)
        # Direct contingency expression independently exposes the MI definition.
        mi = (sum(c / retained * math.log2(c * retained / (totals[p] * symbols[s]))
                  for p, row in enumerate(table) for s, c in enumerate(row) if c)
              if retained else None)
        results.append({"modulus": m, "phase_by_symbol_00_01_10_11": table,
                        "phase_counts": totals, "symbol_counts": symbols,
                        "symbol_entropy_bits": h,
                        "conditional_symbol_entropy_bits": conditional,
                        "plugin_mi_bits": mi})
    return {"parsed_tokens": len(tokens), "escape_omitted_tokens": omitted,
            "retained_tokens": retained, "moduli": results}


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
            "statistics": phase_statistics(tokens)}


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
    for filename in ("token_phase_probe.py", "suffix_joint_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), filename), "rb") as handle:
            sources[filename] = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps({"source_sha256": sources, "python_version": sys.version.split()[0],
                      "escape_extra_bits": 0, "requested_prefix_tokens": LIMIT,
                      "samples": reports, "failures": failures}, indent=2, allow_nan=False))
    return 1 if failures or any(r["prefix_shortfall"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
