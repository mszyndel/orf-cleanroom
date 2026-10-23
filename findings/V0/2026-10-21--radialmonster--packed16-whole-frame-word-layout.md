# packed-16 whole frame: exact 16-bit rows, TIFF-mark byte order and a 12-bit shift on 3 of 3

Author: @radialmonster
Verified by: @radialmonster
Lead: #71
Variant: V0
Builds on: 2026-10-20--radialmonster--e400-low-nibble-floor-mean-interpolation, 2026-10-21--radialmonster--iiro-packed12-and-packed16-whole-frame-byte-order

## Claim

On the three CC0 `packed-16` files, the concatenated raw strips are exactly width x height x 2 bytes and contain one 16-bit word per pixel with contiguous rows (stride width x 2 bytes). The byte order chosen by whole-frame smoothness matches the TIFF byte-order mark: E-1 and E-400 are little-endian (`II`), E-10 is big-endian (`MM`). The low 4 bits are zero in every word except 793 words of E-400, so the words are 12-bit values shifted left by 4; those 793 exceptions are the interpolated pixels already measured in the E-400 low-nibble finding.

## Original evidence

Lead #71 (@radialmonster, 2026-10-19): `tools/orf_v0_unpack.py` at commit 0785fcb, a window of 3 bands x 16 rows x the first 1200 columns. It reported low-4-zero shares 1.0000, 0.9999 and 1.0000, layouts u16-le, u16-le and u16-be, and margins 6.58, 16.28 and 18.59. The three CC0 files:

- raw.pixls.us 1800, E-1, 2624x1966, SHA-256 042286653fbae5b085bef4a4e626145385ea6e82e817f166b4904abcef64457c
- raw.pixls.us 2151, E-400, 3768x2840, SHA-256 1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b
- raw.pixls.us 5424, E-10, 2256x1684, SHA-256 2bfdade72439017a60a47aad1e5bbcb1aca36f2be7a21e94a4257a678fb6f4da

## Verification

New run on 2026-10-21 UTC by @radialmonster, whole frame, with a new script (inline under Reproduce) using only `tools/orf_signature.py` for the TIFF parse; `decoder/` was not used. The measure was fixed before the run: read the largest-strip-byte IFD, concatenate its strips in StripOffsets order, require the total to equal width x height x 2, unpack each row as 16-bit little-endian and big-endian, and compute horizontal lag-2 roughness `h2 = sum |v[x] - v[x+2]| / (sum(v[x]+v[x+2])/2)` and vertical lag-2 roughness `v2 = sum |v[y][x] - v[y+2][x]| / (sum(v[y][x]+v[y+2][x])/2)` over every row. The lower `h2 + v2` wins. The row-stride test repeats the chosen order at `row_bytes + delta` for delta -2 to +2 bytes, using `v2`.

This is a wider run on the same three files, not a new body: the lead already used every CC0 `packed-16` file, and no fourth CC0 file of this size class exists. The lead's comment reports a non-CC0 fourth body with an `MM` mark and a big-endian result; it was not re-run here and no number below depends on it.

| raw.pixls.us id | body | frame | strips / gaps | bytes = 2 x w x h | words | low-4-zero (share) | LE score | BE score | chosen / TIFF mark | margin |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 1800 | E-1 | 2624x1966 | 16 / 0 | 10317568 | 5158784 | 5158784 (1.0000000) | 0.12640 | 1.41385 | LE / `II` | 11.185 |
| 2151 | E-400 | 3768x2840 | 89 / 0 | 21402240 | 10701120 | 10700327 (0.9999259) | 0.07800 | 1.40865 | LE / `II` | 18.059 |
| 5424 | E-10 | 2256x1684 | 15 / 0 | 7598208 | 3799104 | 3799104 (1.0000000) | 1.66098 | 0.09016 | BE / `MM` | 18.422 |

Against the lead's claims:

- Exact payload and stride hold on 3 of 3: the strip byte totals equal width x height x 2 exactly, every strip gap is 0, and reading rows at the true stride is far smoother than at one byte off. Vertical lag-2 roughness at stride + 0 / -1 / +1 / -2 / +2 bytes is 0.0643 / 0.6409 / 0.6423 / 0.0781 / 0.0785 on E-1, 0.0388 / 0.6632 / 0.6628 / 0.0460 / 0.0452 on E-400 and 0.0457 / 0.7526 / 0.7456 / 0.0566 / 0.0541 on E-10. A two-byte shift keeps same-colour rows aligned and stays low; the one-byte shift is the discriminating test, as the lead says.
- Byte order holds on 3 of 3: the smoother order is LE for the two `II` files and BE for the `MM` file, with margins 11.185, 18.059 and 18.422. This agrees with the whole-frame result in the IIRO packed-12/packed-16 byte-order finding, which measured the same three files.
- Low nibble holds with the lead's own exception count: E-1 and E-10 have 0 words with a non-zero low nibble; E-400 has 793, exactly the count in the E-400 low-nibble finding, whose words are floor-mean interpolated pixels. The measured E-400 share 0.9999259 is the lead's 0.9999. The sentence "every word" is exact for E-1 and E-10; on E-400 it is exact except those 793 words. After discarding the low nibble all words are 12-bit values, so the shift-by-4 description holds.

The lead's margins are not directly comparable: it scored a 3-band window with `h2 + v2` after dividing each difference by the window mean, whereas this run divides by the sum of the two values. The chosen orders and the direction of every comparison agree.

## Reproduce

Save the script below as `packed16_whole.py` outside the repo, run it from the repo root with the three checked CC0 files, and compare the table:

    python -I tools/pixls_samples.py check <the three files>
    python -I packed16_whole.py <the three files>

Expected (one pair of lines per file): E-1 `LE words 5158784 low4=0 5158784 (1.0000000)`, E-400 `LE words 10701120 low4=0 10700327 (0.9999259)`, E-10 `BE words 3799104 low4=0 3799104 (1.0000000)`, and `chosen LE` / `chosen LE` / `chosen BE` with the margins in the table.

```python
import struct
import sys

sys.path.insert(0, "tools")
import orf_signature as S


def load(path):
    data = open(path, "rb").read()
    t = S.Tiff(data)
    best = max(t.all_ifds(), key=lambda d: sum(d.get(0x117) or [0]))
    offs, cnts = best.get(0x111) or [], best.get(0x117) or []
    pay = b"".join(data[o:o + c] for o, c in zip(offs, cnts))
    gaps = [offs[i + 1] - (offs[i] + cnts[i]) for i in range(len(offs) - 1)]
    return pay, S.signature(path), len(offs), sorted(set(gaps))


def stats(pay, w, h, big, delta=0):
    rb = w * 2
    n = low4 = hs = ht = vs = vt = 0
    prev = prev2 = None
    for y in range(h):
        start = y * (rb + delta)
        if start < 0 or start + rb > len(pay):
            continue
        r = struct.unpack_from((">" if big else "<") + "%dH" % w, pay, start)
        n += w
        low4 += sum(1 for v in r if v & 15)
        for x in range(w - 2):
            hs += abs(r[x] - r[x + 2])
            ht += r[x] + r[x + 2]
        if prev2 is not None:
            for x in range(w):
                vs += abs(r[x] - prev2[x])
                vt += r[x] + prev2[x]
        prev2, prev = prev, r
    return n, low4, hs / (ht / 2), vs / (vt / 2)


for path in sys.argv[1:]:
    pay, sig, nstrips, gaps = load(path)
    w, h = sig["payload_w"], sig["payload_h"]
    mark = open(path, "rb").read(2).decode("latin1")
    print("== %s  %s  %dx%d  strips %d  gaps %s  bytes %d/%d  mark %s" % (
        sig["file"], sig["sha256"], w, h, nstrips, gaps, len(pay), w * h * 2, mark))
    r = {}
    for big in (False, True):
        n, low4, h2, v2 = stats(pay, w, h, big)
        r["BE" if big else "LE"] = (n, low4, h2, v2)
        print("%s words %d low4=0 %d (%.7f) h2 %.5f v2 %.5f score %.5f" % (
            "BE" if big else "LE", n, n - low4, (n - low4) / n, h2, v2, h2 + v2))
    best = min(r, key=lambda k: r[k][2] + r[k][3])
    print("chosen %s margin %.3f; stride v2 %s" % (
        best, max(r[k][2] + r[k][3] for k in r) / (r[best][2] + r[best][3]),
        " ".join("%+d:%.4f" % (d, stats(pay, w, h, best == "BE", d)[3]) for d in (-2, -1, 0, 1, 2))))
```

Files: CC0 raw.pixls.us ids 1800, 2151 and 5424, checked in this run with `tools/pixls_samples.py check`; the SHA-256 values are in Original evidence. No number here rests on a file others cannot get.
