#!/usr/bin/env python3
"""Measure within-token suffix dependence under the candidate parse (#11, #29).

Stdlib, Python 3.8+. Reads files and prints aggregate JSON only. No decode.
Fixed design: first 262144 tokens, complete consecutive 128-token blocks from
index zero; omit any block containing q>=17. Escapes consume q+6 bits, with
no extra skip. Omission cannot repair unknown post-escape framing. b4 is the
suffix MSB and b0 its LSB. Blocks are not established camera rows.

MI is the unsmoothed empirical plug-in estimate sum p(x,y) log2[p(x,y)/(p(x)p(y))].
Pearson uses exact integer count sums before its final square root. Undefined
MI, correlations and conditional probabilities are null. The comparison uses
16 permutations: shuffle b2 within each retained block, pairing it with the
unchanged b1b0. A local Random(seed+replicate) instance is consumed in original
block order; seed=20261021. This preserves block marginals, not temporal
dependence. Report every comparison MI, not a significance test or p-value.
It differs from #29's historical smoothed/held-out estimates and unknown rows.

Usage: python -I -B tools/suffix_joint_probe.py --sample ID PUBLIC_NAME FILE
Repeat --sample for multiple files. Check licences separately before use.
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import random
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orf_signature import Tiff, size_class  # noqa: E402

LIMIT = 262144
BLOCK = 128
REPLICATES = 16
SEED = 20261021


def scan_prefix(payload, limit=LIMIT):
    """Original bounded bit-reader: append only complete q-zero/one/5-bit tokens."""
    out = []
    pos = 0
    nbits = len(payload) * 8
    while len(out) < limit and pos < nbits:
        start = pos
        q = 0
        while pos < nbits and not ((payload[pos >> 3] >> (7 - (pos & 7))) & 1):
            q += 1
            pos += 1
        if pos + 6 > nbits:
            pos = start
            break
        suffix = 0
        for j in range(1, 6):
            suffix = (suffix << 1) | ((payload[(pos + j) >> 3] >> (7 - ((pos + j) & 7))) & 1)
        pos += 6
        out.append((q, suffix))
    return out, pos


def joint_table(pairs, nx, ny):
    table = [[0] * ny for _ in range(nx)]
    for x, y in pairs:
        table[x][y] += 1
    return table


def mutual_information(table):
    rows = [sum(row) for row in table]
    cols = [sum(col) for col in zip(*table)]
    n = sum(rows)
    if not n:
        return None
    return sum(c / n * math.log2(c * n / (rows[x] * cols[y]))
               for x, row in enumerate(table) for y, c in enumerate(row) if c)


def correlation(table):
    """2x2 table for binary x and y. Degenerate marginals give null."""
    n = sum(map(sum, table))
    sx = sum(table[1])
    sy = table[0][1] + table[1][1]
    vx, vy = sx * (n - sx), sy * (n - sy)
    return (n * table[1][1] - sx * sy) / math.sqrt(vx * vy) if vx and vy else None


def select_blocks(tokens):
    complete = len(tokens) // BLOCK
    retained = []
    omitted = 0
    for i in range(complete):
        block = tokens[i * BLOCK:(i + 1) * BLOCK]
        if any(q >= 17 for q, _ in block):
            omitted += 1
        else:
            retained.append([s for _, s in block])
    tail = tokens[complete * BLOCK:]
    counts = {"complete_blocks": complete, "retained_blocks": len(retained),
              "escape_omitted_blocks": omitted, "tail_tokens": len(tail),
              "parsed_escapes": sum(q >= 17 for q, _ in tokens),
              "tail_escapes": sum(q >= 17 for q, _ in tail),
              "retained_tokens": len(retained) * BLOCK,
              "escape_omitted_tokens": omitted * BLOCK}
    return retained, counts


def measure(blocks):
    suffixes = list(itertools.chain.from_iterable(blocks))
    low = joint_table((((s >> 2) & 1, s & 3) for s in suffixes), 2, 4)
    corr, corr_tables = {}, {}
    for a, b in ((2, 1), (2, 0), (3, 4)):
        key = "b%d_b%d" % (a, b)
        corr_tables[key] = joint_table(
            (((s >> a) & 1, (s >> b) & 1) for s in suffixes), 2, 2)
        corr[key] = correlation(corr_tables[key])
    conditional = []
    for j in range(4):
        n = low[0][j] + low[1][j]
        conditional.append(low[1][j] / n if n else None)
    null_mi = []
    for replicate in range(REPLICATES):
        rng = random.Random(SEED + replicate)
        table = [[0] * 4 for _ in range(2)]
        for block in blocks:
            bits = [(s >> 2) & 1 for s in block]
            rng.shuffle(bits)
            for bit, s in zip(bits, block):
                table[bit][s & 3] += 1
        null_mi.append(mutual_information(table))
    return {"joint_b2_by_b1b0": low, "pearson": corr,
            "pearson_joint_counts_first_bit_rows_second_bit_columns": corr_tables,
            "low3_counts_000_to_111": [low[b][j] for b in range(2) for j in range(4)],
            "p_b2_one_given_b1b0_00_01_10_11": conditional,
            "plugin_mi_bits": mutual_information(low),
            "permuted_plugin_mi_bits": null_mi,
            "permuted_mi_mean_bits": sum(null_mi) / len(null_mi) if suffixes else None}


def report(sample_id, name, path):
    with open(path, "rb") as handle:
        data = handle.read()
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("this probe requires one contiguous strip")
    off, count = offsets[0], lengths[0]
    if off < 0 or count <= 0 or off + count > len(data):
        raise ValueError("payload is out of bounds")
    w, h = best[0x100][0], best[0x101][0]
    if w <= 0 or h <= 0 or size_class(count, w, h) != "variable":
        raise ValueError("this probe requires a positive variable-size payload")
    tokens, end = scan_prefix(data[off:off + count])
    blocks, counts = select_blocks(tokens)
    return {"pixls_id": sample_id, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(), "variant": "unassigned",
            "payload_w": w, "payload_h": h, "payload_bytes": count,
            "payload_offset": off, "size_class": "variable", "bits_consumed": end,
            "requested_tokens": LIMIT, "returned_tokens": len(tokens),
            "selection": counts, "statistics": measure(blocks)}


def self_test():
    # Independent entropy identity, enumeration of every suffix, and hand tables.
    def entropy(values):
        total = sum(values)
        return -sum(x / total * math.log2(x / total) for x in values if x)
    for table in ([[4, 0], [0, 4]], [[2, 2], [2, 2]], [[2, 1, 0, 3], [1, 0, 4, 1]]):
        expected = (entropy(list(map(sum, table)))
                    + entropy(list(map(sum, zip(*table))))
                    - entropy(list(itertools.chain.from_iterable(table))))
        assert math.isclose(mutual_information(table), expected, abs_tol=1e-12)
    assert correlation([[4, 0], [0, 4]]) == 1
    assert correlation([[0, 4], [4, 0]]) == -1
    assert correlation([[2, 2], [2, 2]]) == 0
    assert correlation([[4, 0], [0, 0]]) is None
    assert mutual_information([[0] * 4 for _ in range(2)]) is None
    result = measure([list(range(32)) * 4])
    assert result["joint_b2_by_b1b0"] == [[16] * 4 for _ in range(2)]
    assert result["plugin_mi_bits"] == 0
    assert result["p_b2_one_given_b1b0_00_01_10_11"] == [0.5] * 4
    assert all(x == 0 for x in result["pearson"].values())
    assert measure([])["permuted_mi_mean_bits"] is None
    assert measure([[0] * BLOCK])["p_b2_one_given_b1b0_00_01_10_11"] == [0, None, None, None]
    # Permuting within constant-b2 blocks must preserve their conditional mixture.
    mixed = measure([[0] * BLOCK, [7] * BLOCK])
    assert mixed["plugin_mi_bits"] == 1
    assert mixed["permuted_plugin_mi_bits"] == [1] * REPLICATES
    tokens = [(0, 3)] * (3 * BLOCK + 1)
    tokens[BLOCK] = (17, 5)
    tokens[-1] = (18, 2)
    blocks, counts = select_blocks(tokens)
    assert len(blocks) == 2 and counts["escape_omitted_blocks"] == 1
    assert counts["tail_tokens"] == counts["tail_escapes"] == 1
    assert counts["parsed_escapes"] == 2
    # An independent string encoder checks byte boundaries and long unary runs.
    expected = [(q, (3 * q) % 32) for q in (0, 1, 7, 17, 96, 2)]
    bits = "".join("0" * q + "1" + format(s, "05b") for q, s in expected)
    padded = bits + "0" * ((-len(bits)) % 8)
    buf = int(padded, 2).to_bytes(len(padded) // 8, "big")
    parsed, end = scan_prefix(buf)
    assert parsed == expected and end == len(bits)
    assert scan_prefix(buf, 2) == (expected[:2], 13)
    assert scan_prefix(bytes([1])) == ([], 0)  # stop with no complete suffix
    assert scan_prefix(bytes(20)) == ([], 0)  # no stop bit
    # Truncated suffix: complete tokens followed by a stop at the last bit.
    assert scan_prefix(bytes([0x81])) == ([(0, 0)], 6)
    print("self-test: entropy/table, null/degenerate, selection and bounded parser checks passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", metavar=("ID", "PUBLIC_NAME", "FILE"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        if args.sample:
            parser.error("--self-test and --sample are separate modes")
        self_test()
        return
    if not args.sample:
        parser.error("provide --sample or --self-test")
    reports = []
    for sample_id, name, path in args.sample:
        if not sample_id.isdigit():
            parser.error("sample ID must be numeric")
        try:
            reports.append(report(sample_id, name, path))
        except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
            parser.exit(1, "sample %s: %s\n" % (sample_id, type(exc).__name__))
    with open(__file__, "rb") as handle:
        source_hash = hashlib.sha256(handle.read()).hexdigest()
    with open(os.path.join(os.path.dirname(__file__), "orf_signature.py"), "rb") as handle:
        locator_hash = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps({"tool_sha256": source_hash, "locator_sha256": locator_hash,
                      "python_version": sys.version.split()[0],
                      "block_tokens": BLOCK, "permutation_replicates": REPLICATES,
                      "seed": SEED, "samples": reports}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
