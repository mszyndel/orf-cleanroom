# No fixed token reading + predictor transfers across two new bodies (Partial #31)

Author: @radialmonster
Verified by: @radialmonster
Lead: #31
Variant: unassigned
Builds on: #11, #159
Partial: fixed 11 token readings x 9 causal predictors from the public token_predictor_probe, on E-M1 Mark III 3800 (normal) and 3801 (High Res) and OM-5 6343; not the historical private loops, adaptive/context predictors, other transforms, boundedness or smoothness, a decode or a round-trip.

## Claim

On three public compressed ORF files from two bodies outside the earlier public
predictor run, no fixed token reading + causal predictor among the 11 x 9
combinations met a pre-declared cross-file transfer criterion: r >= +0.20,
z >= +3 and null sd >= 0.02 on at least two of the three files.

The criterion-passing cells were 1 of 99 on E-M1 Mark III 3800, 9 of 99 on
E-M1 Mark III 3801 (High Res) and 0 of 99 on OM-5 6343; no combination passed on
two files. The result reproduces the scoped negative in lead #31 on these new
bodies: high within-file values are file-specific and do not transfer. This is a
preview-luma correlation proxy, not a bounded or smooth reconstruction, a
physical-row model or a decode.

## Original evidence

Lead #31 (2026-10-18) reports negative predictor, transform and integration tests
from private research notes, with no public file list or method, so its exact
figures cannot be reproduced. The public probe in PR #159 first tested the same
fixed readings and predictors on E-M1 Mark II files 1993, 1994, 1995, 1997 and
1998: high within-file values on 1993 (for example s16 + up, r = +0.633) fell to
+0.095 or below on 1997, +0.033 on 1995 and +0.002 on 1998, and no fixed
combination survived across files. This finding tests that scoped negative on
two further bodies that the earlier run did not use.

All three inputs are public CC0 raw.pixls.us files. Their local SHA-256 values
matched the retained verified CC0 inventory and existing `samples/manifest.csv`
rows before measurement; no download or catalogue request was repeated.

- `3800` `Olympus - E-M1MarkIII - 16bit (4:3).ORF`, SHA-256
  `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f`;
  5240x3912, 6.425 bpp, variable payload, compression tag 1, normal mode.
- `3801` `Olympus - E-M1MarkIII - 16bit (4:3).ORF`, SHA-256
  `e9a21175493e9d9e5653aa91f1bd6fbf421aba42b59b4ffe7cd1f7cac2de385c`;
  8200x6132, 6.033 bpp, variable payload, compression tag 1, High Res mode.
- `6343` `OM System - OM-5 - 16bit (4:3).ORF`, SHA-256
  `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`;
  5240x3912, 6.936 bpp, variable payload, compression tag 1, normal mode.

## Verification

A new run was made on 2026-10-21 UTC after the Taking this comment on #31 and
after the earlier public probe. The unchanged public tool
`tools/token_predictor_probe.py` from PR #159 at commit
`5da8678dd317b5df82137cf40610f5f947898bc8` was used (SHA-256
`3d1a2e443385c75235970a0128507e9683fa721b3dc5d27f36f2c046960302ca`), with
`tools/orf_tokens.py` SHA-256
`c6f51ed26793b1bb400a1dc1b29d8e20f9ef734373770310c665228ce02f08ad`,
`tools/jpeg_dc.py` SHA-256
`d86e5a4d0b4e3bc1481b40dff070d73f5c311611545cee46ae8ac602287ce381` and
`tools/orf_signature.py` SHA-256
`b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`.
Python 3.13.15, `--rows 156 --perms 4`, seed 20261021, all 11 readings and all 9
predictors. The tool's default output prints the top 15 cells by |r|; a one-off
driver over the same public functions in the same order printed all 99 cells and
reproduced the top 15 on each file.

The criterion was fixed before measurement: a combination transfers only if it
reaches r >= +0.20, z >= +3 and null sd >= 0.02 on at least two of the three
files. The counts above apply that criterion to all 99 cells. Top |r| cells:

| file | reading | predictor | r | null mean +/- sd | z |
|---|---|---|---:|---:|---:|
| 3800 | zz32 | med | +0.802538 | +0.055588 +/- 0.445606 | +1.6763 |
| 3800 | sig0_32 | med | +0.619473 | +0.010725 +/- 0.167527 | +3.6337 |
| 3800 | sig0 | med | +0.518965 | +0.003645 +/- 0.233926 | +2.2029 |
| 3801 | s16 | up2 | +0.722349 | -0.010233 +/- 0.031880 | +22.9797 |
| 3801 | s16 | up | +0.721094 | +0.009991 +/- 0.047282 | +15.0395 |
| 3801 | u32 | avg2 | +0.703166 | +0.189162 +/- 0.005624 | +91.3949 |
| 6343 | m16b2 | med | +0.534458 | +0.494068 +/- 0.042967 | +0.9400 |
| 6343 | m16b2f | med | -0.534458 | -0.514480 +/- 0.011153 | -1.7913 |
| 6343 | m32b2 | med | +0.532447 | +0.496242 +/- 0.026787 | +1.3516 |

The 3801 High Res file has the only cluster of criterion-passing cells
(sig3 + avg, avg2, up, up2; u32 + up, up2; s16 + up, up2; sig1 + paeth), but none
of those combinations also passed on 3800 or 6343. The single 3800
criterion-passing cell is `sig0_32 + med` (r = +0.619473, z = +3.6337); it did
not pass on 3801 or 6343. The 3800 `zz32 + med` value
does not meet the criterion because its null sd is 0.445606 and z is +1.6763,
and `u32 + avg2` on 3801 has a very small null sd (0.005624). The 6343 top
cells have null means close to the real values and z below +3. This is
consistent with the earlier run's scene-specific high values (1993), not with a
fixed predictor that transfers across bodies.

Limits: the score is a row-centred correlation of block means at the embedded
preview's 8x8 luma-DC scale, using 156 nominal payload-width token rows. Those
rows are not established physical rows, and 3801 has a different payload
geometry (8200x6132, High Res). The null shuffles whole tokens within each
nominal row, four shuffles per cell; z is descriptive, not calibrated
significance. No boundedness, smoothness, scan order, value mapping, round-trip
or sensor ground truth is tested. The tool is in open PR #159, not on main at
this commit. The finder and verifier are the same human account, @radialmonster;
this is self-verification, not independent human verification.

## Reproduce

Read the complete tool and its imports first. The unchanged probe is in open PR
#159; check out `tools/token_predictor_probe.py` at commit
`5da8678dd317b5df82137cf40610f5f947898bc8` (the rest of the tree can be main).
Replace `FILE3800`, `FILE3801` and `FILE6343` with the matching local public
files. The commands read only the samples and print aggregates:

    python -I -B tools/test_orf_tokens.py
    python -I -B tools/test_jpeg_dc.py
    python -I -B tools/token_predictor_probe.py --self-test
    python -I -B tools/token_predictor_probe.py FILE3800 --rows 156 --perms 4
    python -I -B tools/token_predictor_probe.py FILE3801 --rows 156 --perms 4
    python -I -B tools/token_predictor_probe.py FILE6343 --rows 156 --perms 4

The CLI prints the top 15 |r| cells per file, matching the table above. To print
all 99 cells and the criterion count for one file, run this one-off driver from
the repository root (it calls the probe's public functions and writes nothing):

    import math, random, sys
    sys.path.insert(0, "tools")
    import token_predictor_probe as P
    path = sys.argv[1]
    w, h, qa, sa, rows = P.read_tokens(path, 156)
    wb, hb, dc, nd = P.read_preview(path, rows, h)
    target = [dc[r * wb:(r + 1) * wb] for r in range(nd)]
    rng = random.Random(20261021)
    npass = 0
    for kind in P.KINDS:
        d = [P.value(q, s, kind) for q, s in zip(qa, sa)]
        for pred in P.PREDS:
            real = P.score(d, rows, w, nd, wb, target, pred)
            null = []
            for _ in range(4):
                qb, sb = P.shuffle_pairs(qa, sa, rows, w, rng)
                dn = [P.value(q, s, kind) for q, s in zip(qb, sb)]
                null.append(P.score(dn, rows, w, nd, wb, target, pred))
            m = sum(null) / 4
            sd = math.sqrt(sum((v - m) ** 2 for v in null) / 3)
            z = (real - m) / sd if sd else 0.0
            ok = real >= 0.20 and z >= 3.0 and sd >= 0.02
            npass += ok
            print(kind, pred, "%+.6f" % real, "%+.6f" % m, "%.6f" % sd,
                  "%+.4f" % z, ok)
    print("passing cells", npass)
