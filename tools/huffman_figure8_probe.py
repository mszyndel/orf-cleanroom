#!/usr/bin/env python3
"""Test the US8218885B2 Figure 8 Huffman codebooks against compressed ORF.

Supports: the P0 test of public Olympus patent US8218885B2 Figure 8; lead #11.
The codewords below are a transcription of Figure 8 (category mappings), not a
verified decoder specification. The patent says adjacent-pixel differences are
Huffman coded with one of two tables; the figure does not give a full residual
mapping, so this tool tests the natural category-plus-magnitude-bit convention.

The transcription is a complete-looking Huffman table except that the 9-bit
code 111111111 is unassigned (Kraft sum 0.998047). The figure also prints a
code-length column: rows 1-6 match their visible codewords, but rows 7-12 are
listed one bit longer than the visible codeword (for example 11111110 at length
9 and 111111110 at length 10). The figure is therefore internally inconsistent
from row 7. This tool uses the literal visible codewords; the stated lengths do
not form a valid prefix code for those strings, so the result applies to that
literal reading only, not to every interpretation of Figure 8.

Standard library only. Prints aggregate numbers; writes nothing.

Usage:
    python -I tools/huffman_figure8_probe.py FILE [FILE ...] [--rows 156]
        [--start 45] [--missing-category 5] [--sign extend|separate] [--reset]
    python -I tools/huffman_figure8_probe.py --self-test
"""
import argparse
import array
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpeg_dc  # noqa: E402
import orf_tokens as T  # noqa: E402

# Figure 8 transcription: codeword -> category.
TABLE1 = {
    "00": 3, "01": 2, "100": 4, "101": 1, "1100": 5, "1101": 0,
    "1110": 6, "11110": 7, "111110": 9, "1111110": 8,
    "11111110": 10, "111111110": 11,
}
TABLE2 = {
    "00": 11, "01": 10, "100": 9, "101": 8, "1100": 7, "1101": 6,
    "1110": 5, "11110": 4, "111110": 3, "1111110": 2,
    "11111110": 1, "111111110": 0,
}
# Code-length column printed in Figure 8. Rows 7-12 are one greater than the
# visible codeword length; the figure is internally inconsistent from row 7.
LENGTHS = {
    "00": 2, "01": 2, "100": 3, "101": 3, "1100": 4, "1101": 4,
    "1110": 5, "11110": 6, "111110": 7, "1111110": 8,
    "11111110": 9, "111111110": 10,
}


def build(codes):
    tree = {}
    for code, cat in codes.items():
        v = 0
        for ch in code:
            v = (v << 1) | (ch == "1")
        tree[(len(code), v)] = cat
    return tree, max(len(c) for c in codes)


class Bits:
    def __init__(self, buf, pos):
        self.buf = buf
        self.pos = pos
        self.n = len(buf) * 8

    def bit(self):
        if self.pos >= self.n:
            raise EOFError
        b = (self.buf[self.pos >> 3] >> (7 - (self.pos & 7))) & 1
        self.pos += 1
        return b

    def bits(self, k):
        v = 0
        for _ in range(k):
            v = (v << 1) | self.bit()
        return v


def read_code(r, tree, maxlen):
    code = 0
    for length in range(1, maxlen + 1):
        code = (code << 1) | r.bit()
        cat = tree.get((length, code))
        if cat is not None:
            return cat
    return None


def extend(v, n):
    return v if v >= (1 << (n - 1)) else v - (1 << n) + 1


def prefix_stats(codes):
    keys = list(codes)
    prefix_free = not any(b.startswith(a) and a != b for a in keys for b in keys)
    kraft = sum(2.0 ** -len(c) for c in keys)
    return prefix_free, kraft


def parse_rows(buf, start, codes, rows, w, sign, missing):
    codes = dict(codes)
    if missing is not None:
        codes["111111111"] = missing
    tree, maxlen = build(codes)
    r = Bits(buf, start)
    vals = []
    marks = []
    cats = collections.Counter()
    invalid = 0
    while len(vals) < rows * w:
        if len(vals) % w == 0:
            marks.append(r.pos)
        try:
            cat = read_code(r, tree, maxlen)
            if cat is None:
                invalid += 1
                break
            cats[cat] += 1
            n = cat
            if n:
                mag = r.bits(n)
                if sign == "extend":
                    v = extend(mag, n)
                else:
                    v = -mag if r.bit() else mag
            else:
                v = 0
            vals.append(v)
        except EOFError:
            break
    return vals, marks, cats, invalid, r.pos


def score(vals, rows, w, path, reset):
    rec = [0] * (rows * w)
    for i, v in enumerate(vals):
        prev = 0 if (reset and i % w == 0) or i == 0 else rec[i - 1]
        rec[i] = prev + v
    with open(path, "rb") as f:
        data = f.read()
    best = jpeg_dc.find_preview(data)
    if best is None:
        raise ValueError("no embedded baseline preview")
    wb, hb, dc = jpeg_dc.decode(data, best[1])
    nd = max(1, min(hb, round(rows * hb / 3912)))
    target = [dc[r * wb:(r + 1) * wb] for r in range(nd)]
    grid = []
    for rr in range(nd):
        r0 = rr * rows // nd
        r1 = max(r0 + 1, (rr + 1) * rows // nd)
        row = []
        for c in range(wb):
            c0 = c * w // wb
            c1 = max(c0 + 1, (c + 1) * w // wb)
            acc = 0.0
            for t in range(r0, r1):
                base = t * w
                for x in range(c0, c1):
                    acc += rec[base + x]
            row.append(acc / ((r1 - r0) * (c1 - c0)))
        grid.append(row)
    sa = sb = saa = sbb = sab = 0.0
    for ra, rb in zip(grid, target):
        ma = sum(ra) / len(ra)
        mb = sum(rb) / len(rb)
        for x, y in zip(ra, rb):
            x -= ma
            y -= mb
            sa += x
            sb += y
            saa += x * x
            sbb += y * y
            sab += x * y
    return sab / math.sqrt(saa * sbb) if saa > 0 and sbb > 0 else float("nan")


def run(path, rows, start, missing, sign, reset):
    w, h, buf = T.locate(path)
    print("%s payload %dx%d rows=%d start=%d sign=%s reset=%d missing=%s" % (
        os.path.basename(path), w, h, rows, start, sign, reset, missing))
    for name, codes in (("table1", TABLE1), ("table2", TABLE2)):
        pf, kraft = prefix_stats(codes)
        print("  %s prefix_free=%s kraft=%.6f codes=%d" % (
            name, pf, kraft, len(codes)))
        lk = sum(2.0 ** -LENGTHS[c] for c in codes)
        mis = sum(1 for c in codes if LENGTHS[c] != len(c))
        print("    stated length column: kraft=%.6f mismatched_codes=%d" % (lk, mis))
        vals, marks, cats, inv, end = parse_rows(
            buf, start, codes, rows, w, sign, None)
        print("    transcribed: values=%d invalid=%d endbit=%d categories=%s" % (
            len(vals), inv, end, dict(cats.most_common(5))))
        vals, marks, cats, inv, end = parse_rows(
            buf, start, codes, rows, w, sign, missing)
        if len(vals) < rows * w:
            print("    completed: values=%d invalid=%d (short)" % (len(vals), inv))
            continue
        r = score(vals, rows, w, path, reset)
        mod = collections.Counter(m % 8 for m in marks)
        print("    completed: values=%d invalid=%d r=%+.5f row_mod8=%s categories=%s" % (
            len(vals), inv, r, dict(sorted(mod.items())), dict(cats.most_common(5))))


def self_test():
    for codes in (TABLE1, TABLE2):
        pf, kraft = prefix_stats(codes)
        assert pf
        assert abs(kraft - 0.998046875) < 1e-9
    # encode a short known sequence with Table 1 and decode it
    rev = {v: k for k, v in TABLE1.items()}
    seq = [(0, 0), (1, 1), (1, -1), (2, 3), (2, -3), (3, 4)]
    bits = ""
    for cat, val in seq:
        bits += rev[cat]
        if cat:
            if val >= 0:
                mag = val
            else:
                mag = val + (1 << cat) - 1
            bits += format(mag, "0%db" % cat)
    raw = bytearray((len(bits) + 7) // 8)
    for i, ch in enumerate(bits):
        if ch == "1":
            raw[i >> 3] |= 1 << (7 - (i & 7))
    vals, marks, cats, inv, end = parse_rows(bytes(raw), 0, TABLE1, 1, len(seq),
                                             "extend", None)
    assert vals == [v for _, v in seq], vals
    assert inv == 0
    print("self-test ok: prefix/Kraft and a known category+extend sequence")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--rows", type=int, default=156)
    ap.add_argument("--start", type=int, default=45)
    ap.add_argument("--missing-category", type=int, default=5)
    ap.add_argument("--sign", default="extend", choices=["extend", "separate"])
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.files:
        ap.error("no files (or use --self-test)")
    for p in a.files:
        try:
            run(p, a.rows, a.start, a.missing_category, a.sign, a.reset)
        except (ValueError, IndexError, KeyError, OSError) as exc:
            print("%s: %s" % (p, exc), file=sys.stderr)


if __name__ == "__main__":
    main()
