# Wide token row-stride scan finds file-specific peaks on new OM-5 and OM-1 files

Author: @radialmonster
Verified by: @radialmonster
Lead: #144
Variant: V1
Builds on: #30, #11
Partial: the wide-scan best-stride and file-specificity part on the new files with a clear profile peak; physical row boundaries, later bands, the meaning of the extra S-W tokens, the 7267 default-window cutoff and the unresolved high-bpp file 7801 are not covered.

## Claim

Part of lead #144. Using the lead's declared row-start q profile (mean q of
the first 32 tokens of a candidate row minus the mean of the rest, one-sample
z over 300 rows, scan W..W+1200), an independent implementation reproduces
the lead's published 1993 and 6343 values exactly and finds the same
qualitative row-stride structure on CC0 files the lead did not use:

- On busy bodies the best stride is wider than the payload width: OM-5 6347
  S=W+300 (z=12.94), OM-1 5286 S=W+758 (z=6.03), OM-1 5287 S=W+640
  (z=5.17), OM-5 6346 S=W+175 (z=10.48, 10400 wide), OM-1 5284 S=W+553
  (z=12.19, 8180 wide).
- On lower-bpp files the best stride is at or a few tokens above W:
  E-M1 Mark II 1994 S=W+5 (z=33.29), 1996 S=W+8 (z=14.83), OM-5 Mark II
  8552 S=W+6 (z=10.63), 8553 S=W+4 (z=11.43).
- S differs between files of the same body and payload width: on 5240-wide
  OM-5, 6343 S=5472 and 6345 S=5533 (lead), 6347 S=5540 (this run); on
  5220-wide OM-1, 5283 S=6010 (lead), 5286 S=5978 and 5287 S=5860 (this
  run).

This supports the lead's "S is not always W" and "file-specific, not
body-specific" statements on these files. It does not establish physical row
boundaries, a constant whole-frame stride, or what the extra S-W tokens are.

## Original evidence

Lead #144 (2026-10-21), found by @radialmonster. Tool:
`tools/token_row_stride.py` at commit 2972c34 (PR #143), standard library
only. The lead used raw.pixls.us CC0 ids 1993, 1995, 1997, 1998
(5240x3912 E-M1 Mark II), 6343 and 6345 (5240x3912 OM-5), 6344
(8200x6132 OM-5 High Res), 8549 (5240x3912 OM-5 Mark II) and 5283
(5220x3912 OM-1); their SHA-256 values are listed in #144. Published best
strides and z: 1993 5240/10.00, 1995 5240/39.77, 1997 5240/43.33, 1998
5240/47.68, 6343 5472/10.59, 6344 8365/11.30, 6345 5533/14.30, 8549
5327/6.21, 5283 6010/6.85. The measure is fixed at 300 rows, head 32 and a
W..W+1200 scan.

## Verification

New run on 2026-10-21 UTC, after the lead was posted. I used an independent
read-only implementation of the declared profile (in Reproduce below), not
the lead's tool. It parses the k=5 token stream with `tools/orf_tokens.py`
at current upstream main d89075d and computes the profile from the q
sequence. On the lead's own files it gives 1993 S=5240 z=10.0022 and 6343
S=5472 z=10.5880, matching the lead's 10.00 and 10.59 and the lead's tool at
2972c34 run locally on the same two files (S=5240 z=10.0022 and S=5472
z=10.5880).

Files: 11 CC0 files the lead did not use. All 13 local inputs (the 11 new
files plus 1993 and 6343) matched the retained verified-CC0 inventory by
SHA-256; no fresh catalogue request was made for unchanged content. Every
file already has a `samples/manifest.csv` row, so no manifest rows were
added. The lead already used all four CC0 5240-wide E-M1 Mark II files
(1993, 1995, 1997, 1998); the only new E-M1 Mark II files are the two
10400-wide High Res files 1994 and 1996, so the calm-5240 "S equals W"
statement is not independently retested here.

New-file identities (raw.pixls.us id and SHA-256):

- 1994 f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23
- 1996 eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2
- 5284 f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf
- 5286 2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1
- 5287 dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2
- 6346 ffd47d5924b65abdd8af761665d67705fe028cfd08e5efbc264b64a20830d9f4
- 6347 062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9
- 7267 5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756
- 7801 8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82
- 8552 4d79adadf1f736cdbd666bc5f750ee75235b365ecb5fa8dcbc6cd7ca461343ed
- 8553 6c34d583e2c98840828fa500e54e47f270f138dfc697a9a7cd084575305d3c9f

Results with the lead's settings (best candidate in W..W+1200; elevation is
the mean head-minus-rest q difference; "at W" is the same z at S=W):

- 1994 E-M1 Mark II 10400x7792, bpp 6.021: S=10405 (W+5), z=33.2886,
  elevation 1.337886; at W z=1.8636.
- 1996 E-M1 Mark II 10400x7792, bpp 6.022: S=10408 (W+8), z=14.8344,
  elevation 0.922571; at W z=1.8955.
- 5284 OM-1 8180x6132, bpp 6.947: S=8733 (W+553), z=12.1906,
  elevation 0.286417; at W z=0.3225.
- 5286 OM-1 5220x3912, bpp 7.813: S=5978 (W+758), z=6.0287,
  elevation 0.155496; at W z=0.3928.
- 5287 OM-1 5220x3912, bpp 7.538: S=5860 (W+640), z=5.1732,
  elevation 0.124737; at W z=-0.3882.
- 6346 OM-5 10400x7792, bpp 6.445: S=10575 (W+175), z=10.4798,
  elevation 0.187412; at W z=-1.0904.
- 6347 OM-5 5240x3912, bpp 7.173: S=5540 (W+300), z=12.9431,
  elevation 0.239122; at W z=-0.0487.
- 8552 OM-5 Mark II 8200x6132, bpp 6.259: S=8206 (W+6), z=10.6340,
  elevation 0.155484; at W z=4.8984.
- 8553 OM-5 Mark II 10400x7792, bpp 6.212: S=10404 (W+4), z=11.4349,
  elevation 0.444826; at W z=1.9989.

Head sensitivity on 6347: S=5540 at head 16, 32 and 64 (z 8.5497, 12.9431
and 17.6515), so the peak position does not depend on the 32-token choice on
this file.

Limitations and non-confirmations. This is a 300-row prefix measurement;
candidate strides are not physical rows, and close competitors exist (for
example 6347 S=5539 z=11.0378 and 5284 S=8731 z=10.4156), so the maximum is
not a unique physical boundary. On OM-1 Mark II 7267 (10386x7792, bpp
8.450) the default W+1200 window peaks at S=W+1039 z=3.7742; extending the
same profile to W+2500 gives S=W+1239 z=6.2675, so the declared window cuts
off the peak on this file. On OM-3 7801 (10386x7792, bpp 8.208) no clear
peak was found up to W+2500 (best z=3.5257 at S=W+2266). These two high-bpp
files are reported for completeness and are outside this finding's positive
scope; the universal "one sharp peak per file" wording is therefore not
extended to 7801. Physical segmentation, later row bands, a constant
whole-frame stride and the meaning of the extra S-W tokens remain open.

## Reproduce

Save the script below as `row_stride.py` in the repository root, then run
from the root with a local copy of each named CC0 file (paths are examples;
the script only reads them and prints numbers):

    python -I -B row_stride.py FILE [FILE ...]
    python -I -B row_stride.py FILE --extra 2500

`row_stride.py`:

    import argparse
    import array
    import hashlib
    import math
    import sys

    sys.path.insert(0, "tools")
    import orf_tokens as T

    def profile(qs, lo, hi, rows, head):
        pre = [0]
        for q in qs:
            pre.append(pre[-1] + q)
        out = []
        for S in range(max(lo, head + 2), hi + 1):
            n = min(rows, len(qs) // S)
            if n < 20:
                continue
            d = []
            for i in range(n):
                a = pre[i * S + head] - pre[i * S]
                b = pre[(i + 1) * S] - pre[i * S + head]
                d.append(a / head - b / (S - head))
            m = sum(d) / n
            v = sum((x - m) ** 2 for x in d) / (n - 1)
            out.append((m / (math.sqrt(v) / math.sqrt(n)) if v > 0 else 0.0, m, S, n))
        return sorted(out, reverse=True)

    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--rows", type=int, default=300)
    ap.add_argument("--head", type=int, default=32)
    ap.add_argument("--extra", type=int, default=1200)
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    for path in a.files:
        w, h, buf = T.locate(path)
        lo, hi = w, w + a.extra
        q = array.array("B")
        s = array.array("B")
        T.scan(buf, a.rows * hi, 0, 0, None, q, s, 40)
        scores = profile(q, lo, hi, a.rows, a.head)
        print("file", path)
        print("sha256", hashlib.sha256(open(path, "rb").read()).hexdigest())
        print("payload", w, h, "tokens", len(q), "scan", lo, hi)
        for z, e, S, n in scores[:a.top]:
            print("S=%d S-W=%+d rows=%d z=%.4f elevation=%.6f" % (S, S - w, n, z, e))
        print()
