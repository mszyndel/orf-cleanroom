#!/usr/bin/env python3
"""Exploratory lead #32 suffix bridge energies in an explicit token window.

This is separate from the frozen six-file prefix experiment. Select a start
that is a multiple of 128 tokens; blocks retain absolute indices and parity.
The original candidate parser scans from payload bit zero, including escapes,
and only the requested window is retained. This does not establish row starts
or repair possible escape misalignment. CC0-check each public sample first.
Prints aggregates only, with no local paths, token dumps or image data.
"""

import argparse
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import value_map_probe as base

MAX_END = 100000000


class WindowSink:
    """Append-only scanner sink; discarded prefix values are never retained."""
    def __init__(self, start, unary=False):
        self.start = start
        self.unary = unary
        self.count = 0
        self.prefix_bits = 0
        self.values = []

    def append(self, value):
        if self.count < self.start:
            if self.unary:
                self.prefix_bits += value + 6
        else:
            self.values.append(value)
        self.count += 1


def parse_window(payload, start, count):
    if (type(start) is not int or start < 0 or start % base.BLOCK_SIZE
            or type(count) is not int or not 1 <= count <= base.MAX_TOKENS
            or start + count > MAX_END):
        raise base.ProbeError("invalid token window")
    qs, ss = WindowSink(start, True), WindowSink(start)
    _, consumed = base.orf_tokens.scan(payload, start + count, 0, 0, None,
                                      qs, ss, 1 << 62)
    if consumed < 0 or consumed > len(payload) * 8:
        raise base.ProbeError("candidate parser consumed beyond payload; no results emitted")
    if qs.count != ss.count or qs.count < start or not qs.values:
        raise base.ProbeError("requested window starts beyond parsed tokens")
    return qs.values, ss.values, qs.prefix_bits, consumed


def measure(sample_id, name, path, start, count):
    sig = base.orf_signature.signature(path)
    if sig["size_class"] != "variable" or sig["compression_tag"] != 1:
        raise base.ProbeError("expected variable-size payload with compression tag 1")
    offset, size = sig["payload_offset"], sig["payload_bytes"]
    if (type(offset) is not int or offset < 0 or type(size) is not int or size <= 0
            or offset + size > os.path.getsize(path)):
        raise base.ProbeError("payload locator returned invalid or truncated bounds")
    w, h, payload = base.orf_tokens.locate(path)
    if len(payload) != size or (w, h) != (sig["payload_w"], sig["payload_h"]):
        raise base.ProbeError("payload locator disagrees with signature")
    if base.file_hash(path) != sig["sha256"]:
        raise base.ProbeError("sample changed while being read")
    sig["file"] = name
    qs, ss, first_bit, end_bit = parse_window(payload, start, count)
    result = base.token_aggregates(qs, ss)
    for cell in result["cells"]:
        for block in cell["blocks"]:
            block["block_index"] += start // base.BLOCK_SIZE
    return {"raw_pixls_us_id": sample_id, "raw_pixls_us_name": name,
            "sha256": sig["sha256"], "measured_signature": sig,
            "window_start_token": start, "window_end_token_exclusive": start + len(qs),
            "requested_tokens": count, "returned_tokens": len(qs),
            "window_start_bit": first_bit, "window_end_bit_exclusive": end_bit,
            "payload_bytes": size, "token_limit_reached": len(qs) == count, **result}


def main(argv=None):
    ap = base.PrivateArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", nargs=3, required=True, metavar=("ID", "PUBLIC_NAME", "FILE"))
    ap.add_argument("--measured-by", required=True)
    ap.add_argument("--start-token", type=int, required=True,
                    help="absolute token start, multiple of 128; end at most 100000000")
    ap.add_argument("--max-tokens", type=int, default=base.MAX_TOKENS,
                    help="window length, 1..262144 (default: 262144)")
    args = ap.parse_args(argv)
    raw_id, name, path = args.sample
    handle = args.measured_by.lstrip("@")
    if (not raw_id.isascii() or not raw_id.isdigit() or int(raw_id) <= 0
            or not name or not name.isprintable() or any(c in name for c in "/\\")
            or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", handle)
            or args.start_token < 0 or args.start_token % base.BLOCK_SIZE
            or not 1 <= args.max_tokens <= base.MAX_TOKENS
            or args.start_token + args.max_tokens > MAX_END):
        ap.error("invalid sample, handle or token window")
    try:
        sample = measure(int(raw_id), name, path, args.start_token, args.max_tokens)
        provenance = base.provenance()
        provenance["base_tool_version"] = provenance["tool_version"]
        provenance["tool_version"] = "lead32-exploratory-window-v1"
        provenance["source_sha256"]["value_map_window_probe.py"] = base.file_hash(__file__)
        result = {"schema": "orf-lead32-exploratory-window-v1", "builds_on": [32, 11],
                  "exploratory": True, "measured_by": handle,
                  "settings": {"block_tokens": base.BLOCK_SIZE,
                               "absolute_block_start_token": args.start_token,
                               "mappings": list(base.MAPPINGS), "lane_counts": [1, 2],
                               "lane_selection": "absolute token index modulo lane count",
                               "escape_q_min": base.ESCAPE_Q, "escape_extra": 0,
                               "bit_order": "MSB-first", "pooling": "sum(E)/sum(N)"},
                  "provenance": provenance,
                  "limitations": [x for x in base.LIMITATIONS if "fixed prefix" not in x] + [
                      "Exploratory selected window; not the frozen six-file experiment.",
                      "Suffix-only mappings and selected window/block sizes limit interpretation.",
                      "The discarded prefix is parsed without resynchronization; escapes may misalign later windows."],
                  "sample": sample}
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except base.ProbeError as exc:
        print("measurement failed: " + str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, IndexError, struct.error, OverflowError):
        print("measurement failed: input, locator, signature or parser error; no results emitted", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
