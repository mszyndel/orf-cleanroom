#!/usr/bin/env python3
"""Measure geometry and token-value candidates against the embedded preview.

Supports: lead #11 (token parse, row alignment, geometry), lead #32 (ways of
turning token fields into a value) and specs/V1.md gaps G1-G3. Standard library
only, Python 3.8+. Reads sample files and prints aggregate numbers; it writes no
images and no pixel data.

Subcommands
-----------
bands
    For consecutive bands of token rows, map the fixed b2+b4 density to the
    preview's luma DC grid and report the row-centred correlation per band.
    This tests whether the b2+b4 proxy is stationary over the frame.

scale
    Compare the nominal vertical mapping (N token rows -> the preview rows they
    cover at the payload/crop scale) with a whole-preview mapping (N token rows
    -> all preview rows). A stream that starts with a small base image would
    score higher under the second.

table
    Fit a value table f(q, s) on one file, then predict the preview's luma DC
    grid on a held-out file. The block mean of the fitted value is a linear
    function of the per-block symbol histogram, so the table is a least-squares
    solve. The null shuffles whole tokens within each row of the test file and
    re-fits nothing: the table is fixed and only the test correspondence is
    destroyed. This measures a statistical token-to-luma mapping, not a decode.

The preview DC grid comes from tools/jpeg_dc.py (DC coefficient of each 8x8
block). Escape tokens (q >= 17) keep their parsed suffix; they are rare and are
not repaired. Rows are fixed token blocks of the payload width; no physical row
marker is known.

Usage
-----
    python -I tools/token_value_probe.py bands FILE [--band 300] [--max-rows 3900]
    python -I tools/token_value_probe.py scale FILE [--rows 300]
    python -I tools/token_value_probe.py table --train FILE --test FILE
        [--rows 600] [--mode s|qs] [--lam 1] [--smooth 10] [--perms 4]
    python -I tools/token_value_probe.py --self-test
"""
import argparse
import array
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jpeg_dc  # noqa: E402
import orf_tokens as T  # noqa: E402

DENSITY = bytes((((v >> 2) & 1) + ((v >> 4) & 1)) if v < 32 else 0
                for v in range(256))


# ---------------------------------------------------------------- token/preview

def read_tokens(path, rows):
    w, h, buf = T.locate(path)
    qa, sa = array.array("B"), array.array("B")
    T.scan(buf, rows * w, w, 0, None, qa, sa, 40, None, 32)
    n = min(len(sa), rows * w)
    rows = n // w
    if rows < 2:
        raise ValueError("not enough tokens")
    return w, h, qa[:rows * w], sa[:rows * w], rows


def read_preview(path, rows, h):
    with open(path, "rb") as f:
        data = f.read()
    best = jpeg_dc.find_preview(data)
    if best is None:
        raise ValueError("no embedded baseline preview")
    wb, hb, dc = jpeg_dc.decode(data, best[1])
    nd = max(2, min(hb, round(rows * hb / h)))
    return wb, hb, dc, nd


def block_mean(seq, rows, w, nd, nw):
    """Average seq (rows x w) into nd x nw blocks."""
    out = []
    for r in range(nd):
        r0 = r * rows // nd
        r1 = max(r0 + 1, (r + 1) * rows // nd)
        acc = [0.0] * w
        for tr in range(r0, min(r1, rows)):
            base = tr * w
            for c in range(w):
                acc[c] += seq[base + c]
        prefix = [0.0] * (w + 1)
        s = 0.0
        for c in range(w):
            s += acc[c]
            prefix[c + 1] = s
        row = []
        for c in range(nw):
            c0 = c * w // nw
            c1 = max(c0 + 1, (c + 1) * w // nw)
            row.append((prefix[c1] - prefix[c0]) / ((r1 - r0) * (c1 - c0)))
        out.append(row)
    return out


def box_mean_rows(v, rows, w, window):
    out = array.array("f", [0.0]) * (rows * w)
    half = window // 2
    for r in range(rows):
        base = r * w
        prefix = [0] * (w + 1)
        s = 0
        for c in range(w):
            s += v[base + c]
            prefix[c + 1] = s
        for c in range(w):
            a = c - half
            if a < 0:
                a = 0
            b = c + half + 1
            if b > w:
                b = w
            out[base + c] = (prefix[b] - prefix[a]) / (b - a)
    return out


def corr_rows(a, b):
    n = 0
    sa = sb = saa = sbb = sab = 0.0
    for ra, rb in zip(a, b):
        ma = sum(ra) / len(ra)
        mb = sum(rb) / len(rb)
        for x, y in zip(ra, rb):
            x -= ma
            y -= mb
            n += 1
            sa += x
            sb += y
            saa += x * x
            sbb += y * y
            sab += x * y
    if saa <= 0 or sbb <= 0:
        return float("nan")
    return sab / math.sqrt(saa * sbb)


# ---------------------------------------------------------------------- bands

def proxy_bands(path, band, max_rows, window):
    w, h, qa, sa, rows = read_tokens(path, max_rows)
    wb, hb, dc, _ = read_preview(path, rows, h)
    target_all = [dc[r * wb:(r + 1) * wb] for r in range(hb)]
    seq = bytes(DENSITY[v] for v in sa)
    print("%s  payload %dx%d  preview %dx%d  bands of %d token rows  window %d" % (
        os.path.basename(path), w, h, wb, hb, band, window))
    print("rows_start rows_end preview_start preview_end r")
    for start in range(0, rows - band + 1, band):
        nd = max(1, round(band * hb / h))
        y0 = round(start * hb / h)
        if y0 + nd > hb:
            break
        part = seq[start * w:(start + band) * w]
        boxed = box_mean_rows(part, band, w, window)
        grid = block_mean(boxed, band, w, nd, wb)
        r = corr_rows(grid, target_all[y0:y0 + nd])
        print("%9d %8d %13d %11d %+.5f" % (
            start, start + band, y0, y0 + nd, r))


# ---------------------------------------------------------------------- scale

def proxy_scale(path, rows):
    w, h, qa, sa, rows = read_tokens(path, rows)
    wb, hb, dc, nd_nominal = read_preview(path, rows, h)
    target_all = [dc[r * wb:(r + 1) * wb] for r in range(hb)]
    seq = bytes(DENSITY[v] for v in sa)
    boxed = box_mean_rows(seq, rows, w, 63)
    print("%s  token rows %d  preview %dx%d" % (
        os.path.basename(path), rows, wb, hb))
    for label, nd in (("nominal", nd_nominal), ("whole-preview", hb)):
        grid = block_mean(boxed, rows, w, nd, wb)
        print("  %-13s nd=%3d  r=%+.5f" % (
            label, nd, corr_rows(grid, target_all[:nd])))


# ---------------------------------------------------------------------- table

def features(qa, sa, rows, w, nd, wb, mode, intercept=True):
    """Per-block symbol fractions (and optionally an intercept)."""
    nq = 4 if mode == "qs" else 1
    nf = nq * 32
    X = []
    for r in range(nd):
        r0 = r * rows // nd
        r1 = max(r0 + 1, (r + 1) * rows // nd)
        for c in range(wb):
            c0 = c * w // wb
            c1 = max(c0 + 1, (c + 1) * w // wb)
            counts = [0.0] * nf
            n = 0
            for tr in range(r0, min(r1, rows)):
                base = tr * w
                for tc in range(c0, c1):
                    i = base + tc
                    qc = qa[i] if qa[i] < nq else nq - 1
                    counts[qc * 32 + (sa[i] & 31)] += 1
                    n += 1
            inv = 1.0 / n if n else 0.0
            row = [v * inv for v in counts]
            if intercept:
                row.append(1.0)
            X.append(row)
    return X


def gauss(A, b):
    n = len(b)
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-12:
            continue
        if piv != col:
            A[col], A[piv] = A[piv], A[col]
            b[col], b[piv] = b[piv], b[col]
        pv = A[col][col]
        for j in range(col, n):
            A[col][j] /= pv
        b[col] /= pv
        for r in range(n):
            if r == col:
                continue
            f = A[r][col]
            if f == 0.0:
                continue
            for j in range(col, n):
                A[r][j] -= f * A[col][j]
            b[r] -= f * b[col]
    return b


def solve(X, Y, lam, smooth, nf, intercept=True):
    n = nf + 1 if intercept else nf
    A = [[0.0] * n for _ in range(n)]
    b = [0.0] * n
    for f, y in zip(X, Y):
        for i in range(n):
            fi = f[i]
            if fi == 0.0:
                continue
            b[i] += fi * y
            for j in range(i, n):
                A[i][j] += fi * f[j]
    for i in range(n):
        for j in range(i):
            A[i][j] = A[j][i]
    for i in range(nf):
        A[i][i] += lam
    if smooth > 0:
        nq = nf // 32
        for q in range(nq):
            for s in range(31):
                i = q * 32 + s
                j = i + 1
                A[i][i] += smooth
                A[j][j] += smooth
                A[i][j] -= smooth
                A[j][i] -= smooth
    return gauss(A, b)


def predict(X, w):
    return [sum(fi * wi for fi, wi in zip(f, w)) for f in X]


def stats(y, p):
    n = len(y)
    my = sum(y) / n
    mp = sum(p) / n
    sy = sp = syp = 0.0
    for a, b in zip(y, p):
        a -= my
        b -= mp
        sy += a * a
        sp += b * b
        syp += a * b
    r = syp / math.sqrt(sy * sp) if sy > 0 and sp > 0 else float("nan")
    r2 = 1.0 - sum((a - b) ** 2 for a, b in zip(y, p)) / sy if sy > 0 else float("nan")
    return r, r2


def shuffle_pairs(qa, sa, rows, w, rng):
    qb = bytearray(qa)
    sb = bytearray(sa)
    for r in range(rows):
        idx = list(range(r * w, (r + 1) * w))
        rng.shuffle(idx)
        qpart = [qb[i] for i in idx]
        spart = [sb[i] for i in idx]
        for k, i in enumerate(range(r * w, (r + 1) * w)):
            qb[i] = qpart[k]
            sb[i] = spart[k]
    return qb, sb


def row_center(vals, nd, wb):
    out = []
    for r in range(nd):
        row = vals[r * wb:(r + 1) * wb]
        m = sum(row) / len(row)
        out.extend(v - m for v in row)
    return out


def table(train, test, rows, mode, lam, smooth, perms):
    w, h, qa, sa, rows = read_tokens(train, rows)
    wb, hb, dc, nd = read_preview(train, rows, h)
    Y = row_center([dc[r * wb + c] for r in range(nd) for c in range(wb)], nd, wb)
    X = features(qa, sa, rows, w, nd, wb, mode, intercept=False)
    nf = len(X[0])
    train_mask = [(r % 2 == 0) for r in range(nd)
                  for _ in range(wb)]
    Xtr = [f for f, m in zip(X, train_mask) if m]
    Ytr = [y for y, m in zip(Y, train_mask) if m]
    Xva = [f for f, m in zip(X, train_mask) if not m]
    Yva = [y for y, m in zip(Y, train_mask) if not m]
    wv = solve(Xtr, Ytr, lam, smooth, nf, intercept=False)
    rtr, r2tr = stats(Ytr, predict(Xtr, wv))
    rva, r2va = stats(Yva, predict(Xva, wv))
    print("== train %s  mode=%s rows=%d preview %dx%d used %dx%d lam=%g smooth=%g" % (
        os.path.basename(train), mode, rows, wb, hb, nd, wb, lam, smooth))
    print("  even rows (fit):        corr=%+.5f  R2=%+.5f" % (rtr, r2tr))
    print("  odd rows (held out):    corr=%+.5f  R2=%+.5f" % (rva, r2va))

    w2, h2, qa2, sa2, rows2 = read_tokens(test, rows)
    wb2, hb2, dc2, nd2 = read_preview(test, rows2, h2)
    Yte = row_center([dc2[r * wb2 + c] for r in range(nd2) for c in range(wb2)],
                     nd2, wb2)
    Xte = features(qa2, sa2, rows2, w2, nd2, wb2, mode, intercept=False)
    rte, r2te = stats(Yte, predict(Xte, wv))
    print("  held-out file %s: corr=%+.5f  R2=%+.5f" % (
        os.path.basename(test), rte, r2te))

    rng = random.Random(20261021)
    null = []
    for _ in range(perms):
        qb, sb = shuffle_pairs(qa2, sa2, rows2, w2, rng)
        Xn = features(qb, sb, rows2, w2, nd2, wb2, mode, intercept=False)
        null.append(stats(Yte, predict(Xn, wv))[0])
    if null:
        m = sum(null) / len(null)
        sd = math.sqrt(sum((v - m) ** 2 for v in null) / max(1, len(null) - 1))
        z = (rte - m) / sd if sd else 0.0
        print("  within-row token shuffle: mean=%+.5f +/- %.5f  z=%+.2f  n=%d" % (
            m, sd, z, len(null)))

    nq = nf // 32
    for q in range(min(nq, 4)):
        tab = wv[q * 32:(q + 1) * 32]
        # correlation of the table with symbol order, without numpy
        mt = sum(tab) / 32.0
        ms = 15.5
        cov = sum((s - ms) * (v - mt) for s, v in enumerate(tab))
        vt = sum((v - mt) ** 2 for v in tab)
        vs = sum((s - ms) ** 2 for s in range(32))
        oc = cov / math.sqrt(vt * vs) if vt > 0 else float("nan")
        print("  table q=%d order corr with s: %+.4f" % (q, oc))


# ------------------------------------------------------------------ self-test

def self_test():
    # recover a known 32-entry table from exact block means
    true = [float(s * s % 11) for s in range(32)]
    X, Y = [], []
    rng = random.Random(7)
    for _ in range(200):
        counts = [0] * 32
        for _ in range(50):
            counts[rng.randrange(32)] += 1
        f = [c / 50.0 for c in counts] + [1.0]
        X.append(f)
        Y.append(sum(fi * wi for fi, wi in zip(f, true + [5.0])))
    w = solve(X, Y, 1e-9, 0.0, 32, intercept=True)
    # the table is identifiable only up to an additive constant (the block
    # features sum to one and an intercept is also fitted), so compare shapes
    mw = sum(w[:32]) / 32.0
    mt = sum(true) / 32.0
    for s in range(32):
        assert abs((w[s] - mw) - (true[s] - mt)) < 1e-4, (s, w[s], true[s])
    # a shuffled target must lose the table's fit
    r_real, _ = stats(Y, predict(X, w))
    rng.shuffle(Y)
    r_null, _ = stats(Y, predict(X, w))
    assert r_real > 0.99 and abs(r_null) < 0.3, (r_real, r_null)
    # block-mean of a constant is the constant
    bm = block_mean([3.0] * (10 * 20), 10, 20, 5, 4)
    assert all(abs(v - 3.0) < 1e-9 for row in bm for v in row)
    print("self-test ok: table recovered, shuffled fit lost, block mean exact")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n", 1)[1])
    sub = ap.add_subparsers(dest="cmd")

    b = sub.add_parser("bands", help="band-wise b2+b4 proxy correlation")
    b.add_argument("file")
    b.add_argument("--band", type=int, default=300)
    b.add_argument("--max-rows", type=int, default=3900)
    b.add_argument("--window", type=int, default=63)

    s = sub.add_parser("scale", help="nominal versus whole-preview mapping")
    s.add_argument("file")
    s.add_argument("--rows", type=int, default=300)

    t = sub.add_parser("table", help="fit a value table, test on another file")
    t.add_argument("--train", required=True)
    t.add_argument("--test", required=True)
    t.add_argument("--rows", type=int, default=600)
    t.add_argument("--mode", default="s", choices=["s", "qs"])
    t.add_argument("--lam", type=float, default=1.0)
    t.add_argument("--smooth", type=float, default=10.0)
    t.add_argument("--perms", type=int, default=4)

    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.cmd:
        ap.error("choose a subcommand or use --self-test")
    try:
        if a.cmd == "bands":
            proxy_bands(a.file, a.band, a.max_rows, a.window)
        elif a.cmd == "scale":
            proxy_scale(a.file, a.rows)
        elif a.cmd == "table":
            table(a.train, a.test, a.rows, a.mode, a.lam, a.smooth, a.perms)
    except (ValueError, IndexError, KeyError, OSError) as exc:
        print("%s" % exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
