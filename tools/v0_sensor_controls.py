#!/usr/bin/env python3
"""Packed-16 V0 window diagnostics and unchanged synthetic-envelope stress test.

Builds on #301/#310 and specs/V0.md S1/S4: largest strip total, contiguous
natural rows, TIFF byte-order mark. These selectors agree on the three public
packed-16 bodies; general layout selection and physical row origin are open.
No preview access, threshold fitting, black subtraction or CFA interpretation.
Stored words are reported separately; only explicit floor(word/16) controls
are compared to the frozen 12-bit toy envelope. This discards low nibbles and
does not establish effective precision, black level or sensor truth.
All output is aggregate; original and transformed windows remain in memory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import struct
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sensor_rejection_controls as controls

MAX_BYTES = 128 * 1024 * 1024
WINDOW_W, WINDOW_H = 32, 24
RELEVANT = {256, 257, 273, 279, 330}


def require(condition):
    if not condition:
        raise ValueError("unsupported or malformed packed-16 input")


def geometry(data):
    """Bounded TIFF integer descriptors only; irrelevant tags never decoded."""
    require(8 <= len(data) <= MAX_BYTES and data[:2] in (b"II", b"MM"))
    endian = "<" if data[:2] == b"II" else ">"

    def integer(pos, size):
        require(0 <= pos <= len(data) - size)
        return int.from_bytes(data[pos:pos + size], "little" if endian == "<" else "big")

    require(integer(2, 2) in (0x4f52, 0x5352))
    pending, seen, candidates = [integer(4, 4)], set(), []
    while pending:
        offset = pending.pop()
        if not offset:
            continue
        require(offset not in seen and len(seen) < 128)
        seen.add(offset)
        count = integer(offset, 2)
        require(count <= 4096 and offset + 2 + 12 * count + 4 <= len(data))
        fields = {}
        for index in range(count):
            pos = offset + 2 + 12 * index
            tag = integer(pos, 2)
            if tag not in RELEVANT:
                continue
            typ, n = integer(pos + 2, 2), integer(pos + 4, 4)
            require(tag not in fields and typ in (3, 4, 13) and 0 < n <= 4096)
            require(tag == 330 or typ != 13)
            require(tag not in (256, 257) or n == 1)
            size = 2 if typ == 3 else 4
            start = pos + 8 if n * size <= 4 else integer(pos + 8, 4)
            require(start + n * size <= len(data))
            fields[tag] = [integer(start + size * j, size) for j in range(n)]
        pending.extend(fields.get(330, []))
        pending.append(integer(offset + 2 + 12 * count, 4))
        require(len(pending) + len(seen) <= 128)
        if 279 in fields:
            candidates.append(fields)
    require(bool(candidates))
    total = max(sum(f[279]) for f in candidates)
    best = [f for f in candidates if sum(f[279]) == total]
    require(len(best) == 1)
    fields = best[0]
    require(all(tag in fields for tag in (256, 257, 273, 279)))
    width, height = fields[256][0], fields[257][0]
    offsets, counts = fields[273], fields[279]
    require(WINDOW_W <= width <= 20000 and WINDOW_H <= height <= 20000)
    require(total == width * height * 2 and len(offsets) == len(counts))
    for index, (start, length) in enumerate(zip(offsets, counts)):
        require(length > 0 and start >= 8 and start + length <= len(data))
        if index:
            require(start == offsets[index - 1] + counts[index - 1])
    return {"width": width, "height": height, "payload_offset": offsets[0],
            "payload_bytes": total, "strips": len(counts), "layout": "natural",
            "packing": "packed-16", "byte_order": "little" if endian == "<" else "big"}


def windows(data, info):
    width, height = info["width"], info["height"]
    x = (width - WINDOW_W) // 2
    for label, y in (("top", 0), ("middle", (height - WINDOW_H) // 2),
                     ("bottom", height - WINDOW_H)):
        values = []
        for row in range(y, y + WINDOW_H):
            start = info["payload_offset"] + 2 * (row * width + x)
            raw = data[start:start + 2 * WINDOW_W]
            require(len(raw) == 2 * WINDOW_W)
            values.extend(int.from_bytes(raw[i:i + 2], info["byte_order"])
                          for i in range(0, len(raw), 2))
        yield label, x, y, values


def diagnostic(data, limits):
    info = geometry(data)
    rows = []
    for label, x, y, stored in windows(data, info):
        base = [value >> 4 for value in stored]
        trials = []
        for mapping in controls.MAPPINGS:
            changed = controls.transform(base, mapping)
            feature = controls.features(changed, WINDOW_W, WINDOW_H)
            trials.append({"mapping": mapping, "features": feature,
                           "rejected_by": controls.classify(feature, limits),
                           "changed_values": sum(a != b for a, b in zip(base, changed))})
        rows.append({"window": label, "x": x, "y": y,
                     "width": WINDOW_W, "height": WINDOW_H,
                     "stored_word_features": controls.features(stored, WINDOW_W, WINDOW_H),
                     "stored_min": min(stored), "stored_max": max(stored),
                     "nonzero_low_nibbles": sum(bool(v & 15) for v in stored),
                     "shift4_min": min(base), "shift4_max": max(base), "trials": trials})
    counts = {"identity_accepted": 0, "identity_rejected": 0,
              "nonidentity_accepted": 0, "nonidentity_rejected": 0}
    by_mapping = {m: {"accepted": 0, "rejected": 0} for m in controls.MAPPINGS}
    for row in rows:
        for trial in row["trials"]:
            outcome = "rejected" if trial["rejected_by"] else "accepted"
            label = "identity" if trial["mapping"] == "identity" else "nonidentity"
            counts[label + "_" + outcome] += 1
            by_mapping[trial["mapping"]][outcome] += 1
    return {"geometry": info, "windows": rows, "construction_confusion": counts,
            "by_mapping": by_mapping}


def read_verified(path, expected):
    require(stat.S_ISREG(path.stat().st_mode) and path.stat().st_size <= MAX_BYTES)
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES and hashlib.sha256(data).hexdigest() == expected)
    return data


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "invalid command line; use --help\n")


def main(argv=None):
    parser = SafeParser(description=__doc__)
    parser.add_argument("--sample", nargs=4, action="append", required=True,
                        metavar=("ID", "PUBLIC_NAME", "VERIFIED_SHA256", "FILE"))
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args(argv)
    for sid, name, digest, path in args.sample:
        if not (re.fullmatch(r"[1-9][0-9]{0,11}", sid) and
                re.fullmatch(r"[0-9a-f]{64}", digest) and
                1 <= len(name) <= 512 and not any(ord(c) < 32 or ord(c) == 127 or
                                                 c in "/\\" for c in name)):
            parser.error("invalid public identity")
    if len({s[0] for s in args.sample}) != len(args.sample):
        parser.error("duplicate ID")
    start = time.perf_counter()
    development = controls.cohort(controls.DEVELOPMENT_SEEDS)
    limits = controls.envelope([r for r in development if r["mapping"] == "identity"])
    report = {"protocol": {"window_width": WINDOW_W, "window_height": WINDOW_H,
                           "x": "floor((width-32)/2)",
                           "y": "0, floor((height-24)/2), height-24",
                           "raw_word_classified": False,
                           "stored_word_domain": [0, 65535],
                           "stored_feature_outside_reference": "0..4095 toy range only; not raw-word overflow",
                           "classification_input": "floor(stored_word/16), no black subtraction",
                           "thresholds": "unchanged synthetic identity development envelope from #310",
                           "labels": "identity/nonidentity construction only; not sensor truth",
                           "limits": "3 windows/file; no exposure/noise/CFA/black calibration or universal threshold; no GPU claim"},
              "development_limits": limits, "samples": []}
    failed = False
    for sid, name, digest, path in args.sample:
        row = {"pixls_id": sid, "public_name": name, "sha256": digest}
        try:
            row.update(diagnostic(read_verified(Path(path), digest), limits), status="ok")
        except (OSError, ValueError, struct.error):
            row.update(status="error", category="file_access_hash_or_layout_rejected")
            failed = True
        report["samples"].append(row)
    if args.benchmark:
        report["cpu_seconds"] = time.perf_counter() - start
    print(json.dumps(report, sort_keys=True, indent=2))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
