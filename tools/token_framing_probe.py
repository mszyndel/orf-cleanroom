#!/usr/bin/env python3
"""Compare the k=5 token framing against null bitstreams.

Supports: lead #197 (establish entropy-code framing independently of the
assumed k=5 parser). The bounded parser's 0-7 residual bits are not evidence;
this tool measures a different property: the share of tokens with q=0 (the
stop bit is the first bit of the token). A genuine unary framing should put a 1
at the token start far more often than a null stream with the same local
statistics.

Nulls, all over the same prefix length:

- random: independent bits at approximately the prefix's ones density;
- byte_shuffle: the prefix's exact byte histogram, byte order destroyed;
- run_shuffle: the prefix's exact bit-run lengths and values, run order shuffled.

Standard library only. Prints aggregate numbers; writes nothing.

Usage:
    python -I tools/token_framing_probe.py FILE [FILE ...] [--bytes 131072]
        [--seed 20261021]
    python -I tools/token_framing_probe.py --self-test
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orf_tokens as T  # noqa: E402


def parse_stats(buf):
    # Bounded local parse: only count a token when its q + 6 bits fit.
    nbits = len(buf) * 8
    pos = 0
    tokens = 0
    q0 = 0
    while pos + 6 <= nbits:
        p = pos
        while p < nbits and not ((buf[p >> 3] >> (7 - (p & 7))) & 1):
            p += 1
        if p + 6 > nbits:
            break
        q = p - pos
        tokens += 1
        if q == 0:
            q0 += 1
        pos = p + 6
    ones = sum(bin(b).count("1") for b in buf) / (8.0 * len(buf)) if buf else 0.0
    return (q0 / tokens if tokens else 0.0), ones, tokens, nbits - pos


def random_bytes(n, rng):
    return bytes(rng.getrandbits(8) for _ in range(n))


def bit_list(buf):
    out = []
    for byte in buf:
        for k in range(7, -1, -1):
            out.append((byte >> k) & 1)
    return out


def pack_bits(bits):
    out = bytearray((len(bits) + 7) // 8)
    for i, v in enumerate(bits):
        if v:
            out[i >> 3] |= 1 << (7 - (i & 7))
    return bytes(out)


def run_shuffle(buf, rng):
    bits = bit_list(buf)
    runs = []
    cur = bits[0]
    length = 1
    for b in bits[1:]:
        if b == cur:
            length += 1
        else:
            runs.append((cur, length))
            cur = b
            length = 1
    runs.append((cur, length))
    rng.shuffle(runs)
    out = []
    for v, length in runs:
        out.extend([v] * length)
        if len(out) >= len(bits):
            break
    return pack_bits(out[:len(bits)])


def report(path, nbytes, seed):
    w, h, buf = T.locate(path)
    prefix = buf[:nbytes]
    print("%s payload %dx%d prefix=%d bytes seed=%d" % (
        os.path.basename(path), w, h, len(prefix), seed))
    print("  model          ones    q0      tokens   residual")
    for name, data in (("real", prefix),
                       ("random", None),
                       ("byte_shuffle", None),
                       ("run_shuffle", None)):
        rng = random.Random(seed)
        if name == "random":
            data = random_bytes(len(prefix), rng)
        elif name == "byte_shuffle":
            b = bytearray(prefix)
            rng.shuffle(b)
            data = bytes(b)
        elif name == "run_shuffle":
            data = run_shuffle(prefix, rng)
        q0, ones, n, residual = parse_stats(data)
        print("  %-13s %.4f  %.4f  %8d  %d" % (name, ones, q0, n, residual))


def self_test():
    # synthetic q=0 tokens: 1 stop bit then 5 zero suffix bits
    tokens = 20000
    bits = []
    for _ in range(tokens):
        bits.append(1)
        bits.extend([0] * 5)
    q0, ones, n, residual = parse_stats(pack_bits(bits))
    assert abs(q0 - 1.0) < 1e-9, q0
    assert n == tokens, (n, tokens)
    rng = random.Random(7)
    rb = random_bytes(8192, rng)
    q0, ones, n, residual = parse_stats(rb)
    assert 0.40 < q0 < 0.60, q0
    # byte shuffle keeps the ones density
    b = bytearray(8192)
    for i in range(8192):
        b[i] = rng.getrandbits(8)
    q0a, ones_a, _, _ = parse_stats(bytes(b))
    rng.shuffle(b)
    q0b, ones_b, _, _ = parse_stats(bytes(b))
    assert abs(ones_a - ones_b) < 1e-12
    # run shuffle keeps the ones density
    src = random_bytes(4096, rng)
    q0a, ones_a, _, _ = parse_stats(src)
    q0b, ones_b, _, _ = parse_stats(run_shuffle(src, rng))
    assert abs(ones_a - ones_b) < 1e-9, (ones_a, ones_b)
    print("self-test ok: q=0 framing, random null, byte and run shuffles preserve density")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--bytes", type=int, default=131072)
    ap.add_argument("--seed", type=int, default=20261021)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.files:
        ap.error("no files (or use --self-test)")
    for p in a.files:
        try:
            report(p, a.bytes, a.seed)
        except (ValueError, IndexError, KeyError, OSError) as exc:
            print("%s: %s" % (p, exc), file=sys.stderr)


if __name__ == "__main__":
    main()
