#!/usr/bin/env python3
"""Held-out nominal-width context increment, #29 item 5; builds on #11/#169/#180.

First 262144 complete q-zero/one/five-suffix candidate tokens, zero extra
escape bits. Predict b2 from five local alternating taps, then add b2 at W,
2W,2W-2,2W+2 separately/jointly. Descriptive matched-size controls add 128 to
those remote lags. W is payload width, not established token-row stride.
All eleven models share target indices t>=2W+130. Exclude targets with q>=17
at target or ANY local/remote/control tap, without compacting indices.
Train targets in even original 128-token blocks, test odd. Contexts cross
block boundaries; adjacent splits and reused donors can remain dependent.
Jeffreys half-count binary fits; unseen contexts predict .5. Print all exact
train/test tables, losses, signed gains versus local-only and unseen counts.

Deterministic +128 shifts may retain width structure; they are not exchangeable
nulls, significance tests or uncertainty estimates. Sparse contexts, selective
omissions and dependence limit inference. Omission cannot repair unknown
framing. This is not the historical greedy340-feature search/private estimator,
a physical-row/CFA claim, a finding or a decoder. Read-only, aggregate JSON,
Python3.8+ stdlib. Reuse retained verified CC0 records after local hash matching.
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
from suffix_joint_probe import LIMIT, scan_prefix

BLOCK = 128
LOCAL = ((4, 1), (2, 2), (4, 3), (2, 4), (4, 5))


def model_taps(width):
    if type(width) is not int or width <= 5:
        raise ValueError("width must exceed five")
    remote = (width, 2 * width, 2 * width - 2, 2 * width + 2)
    models = [("local", LOCAL)]
    for shift, label in ((0, "width"), (128, "shift128")):
        taps = tuple((2, lag + shift) for lag in remote)
        models.extend((label + "_" + str(i), LOCAL + (tap,))
                      for i, tap in enumerate(taps))
        models.append((label + "_joint", LOCAL + taps))
    return models


def score_tables(train, test):
    nt, nv = sum(map(sum, train)), sum(map(sum, test))
    unseen = sum(sum(b) for a, b in zip(train, test) if not sum(a))
    loss = None
    if nv:
        loss = math.fsum(-b[y] * math.log2((a[y] + .5) / (sum(a) + 1))
                         for a, b in zip(train, test) for y in (0, 1)) / nv
    return {"training_targets": nt, "test_targets": nv,
            "fitted_transfer": bool(nt and nv),
            "test_targets_in_unseen_contexts": unseen,
            "heldout_log_loss_bits": loss}


def measure(tokens, width):
    models = model_taps(width)
    for q, suffix in tokens:
        if type(q) is not int or q < 0 or type(suffix) is not int or not 0 <= suffix < 32:
            raise ValueError("invalid token")
    start = 2 * width + 130
    required_lags = sorted({0} | {lag for _, taps in models for _, lag in taps})
    tables = [[[[0, 0] for _ in range(1 << len(taps))] for _ in range(2)]
              for _, taps in models]
    candidates, omitted, retained = [0, 0], [0, 0], [0, 0]
    for t in range(start, len(tokens)):
        split = (t // BLOCK) % 2
        candidates[split] += 1
        if any(tokens[t - lag][0] >= 17 for lag in required_lags):
            omitted[split] += 1
            continue
        retained[split] += 1
        y = (tokens[t][1] >> 2) & 1
        for (_, taps), table in zip(models, tables):
            context = 0
            for bit, lag in taps:
                context = (context << 1) | ((tokens[t - lag][1] >> bit) & 1)
            table[split][context][y] += 1
    results = []
    baseline = None
    for (name, taps), (train, test) in zip(models, tables):
        row = score_tables(train, test)
        if name == "local" and row["fitted_transfer"]:
            baseline = row["heldout_log_loss_bits"]
        row.update({"name": name, "target_bit": 2,
                    "taps_first_is_msb": [list(tap) for tap in taps],
                    "training_counts_context_by_outcome": train,
                    "test_counts_context_by_outcome": test,
                    "gain_vs_local_bits": baseline - row["heldout_log_loss_bits"]
                    if baseline is not None and row["fitted_transfer"] else None})
        results.append(row)
    return {"selection": {"target_start_inclusive": start,
                           "target_end_exclusive": len(tokens),
                           "required_lags_including_target": required_lags,
                           "candidate_train_test_targets": candidates,
                           "escape_omitted_train_test_targets": omitted,
                           "retained_train_test_targets": retained,
                           "parsed_escapes": sum(q >= 17 for q, _ in tokens)},
            "models": results}


def report(sample_id, name, path):
    with open(path, "rb") as handle:
        data = handle.read()
    best = max(Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or []))
    offsets, lengths = best[0x111], best[0x117]
    if len(offsets) != 1 or len(lengths) != 1:
        raise ValueError("one contiguous strip required")
    off, count = offsets[0], lengths[0]
    if off < 0 or count <= 0 or off + count > len(data):
        raise ValueError("invalid payload bounds")
    w, h = best[0x100][0], best[0x101][0]
    if w <= 5 or h <= 0 or size_class(count, w, h) != "variable":
        raise ValueError("variable-size payload with width>5 required")
    tokens, end = scan_prefix(data[off:off + count], LIMIT)
    return {"pixls_id": sample_id, "pixls_name": name,
            "sha256": hashlib.sha256(data).hexdigest(), "variant": "unassigned",
            "payload_w": w, "payload_h": h, "payload_offset": off,
            "payload_bytes": count, "compression_tag": best.get(0x103),
            "size_class": "variable", "requested_tokens": LIMIT,
            "returned_tokens": len(tokens), "prefix_shortfall": LIMIT - len(tokens),
            "bits_consumed": end, "statistics": measure(tokens, w)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", nargs=3, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "FILE"))
    args = parser.parse_args()
    ids = [s[0] for s in args.sample]
    if any(not i.isascii() or not i.isdecimal() or int(i) <= 0 for i in ids) or len(set(map(int, ids))) != len(ids):
        parser.error("sample IDs must be distinct positive ASCII decimals")
    reports, failures = [], []
    for sample_id, name, path in args.sample:
        try:
            reports.append(report(sample_id, name, path))
        except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
            failures.append({"pixls_id": sample_id, "error": type(exc).__name__})
    sources = {}
    for filename in ("token_width_context_probe.py", "suffix_joint_probe.py", "orf_signature.py"):
        with open(os.path.join(os.path.dirname(__file__), filename), "rb") as handle:
            sources[filename] = hashlib.sha256(handle.read()).hexdigest()
    print(json.dumps({"source_sha256": sources, "python_version": sys.version.split()[0],
                      "target_block_size": BLOCK, "smoothing_per_outcome": .5,
                      "escape_extra_bits": 0, "samples": reports, "failures": failures},
                     indent=2, allow_nan=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
