# A suffix-to-luma table transfers weakly across E-M1 Mark II files

Author: @radialmonster
Verified by: @radialmonster
Lead: #155
Variant: V1
Builds on: 2026-10-21--radialmonster--b2b4-local-luma-proxy, #11, #29, #32
Partial: the 32-entry suffix table's held-out transfer on E-M1 Mark II files 1993, 1997, 1998 and High-Res 1994; not the q x s table, the 1993 to 1995 direction, or any pixel decode/round-trip.

## Claim

A 32-entry table `f(s)` from the 5-bit token suffix to a luma value, fitted on E-M1 Mark II 1995 and then held fixed, predicts the embedded preview's within-row luma DC on held-out E-M1 Mark II files better than a within-row token shuffle, but only weakly.

All runs use 600 token rows, the preview's 46x400 DC blocks, mode `s`, `--lam 1 --smooth 10`, and row-centred correlation:

| test file | r | R2 | within-row token shuffle | z |
|---|---|---|---|---|
| 1993 | +0.08696 | +0.00260 | -0.00054 +/- 0.00825 | +10.61 |
| 1998 | +0.08531 | +0.00604 | -0.00227 +/- 0.00790 | +11.09 |
| 1997 (verification) | +0.10556 | +0.00818 | -0.00254 +/- 0.00991 | +10.91 |
| 1994 High Res (verification) | +0.05517 | -0.04055 | +0.00184 +/- 0.01056 | +5.05 |

On held-out rows of the training file the fit gives r=+0.10802, R2=+0.00845. The learned table is mostly ordered with `s` (correlation +0.8857 with 0..31).

The mapping is weak and scene-dependent. Training on 1993 and testing on 1995 gives held-out-file r=+0.02895 (R2 -0.40069), so the direction does not transfer. A `q x s` table raises held-out-row r to +0.14595 but gives held-out-file r=+0.07719 on 1993; its q=0 table is ordered with `s` (+0.9158) while its q=1 table is ordered oppositely (-0.9791). Those variants are outside this finding's scope.

Limits: this is a row-centred correlation of block means at the preview's 8x8 DC scale, not a pixel value. There is no predictor, scan-order or round-trip model, so this is not a decode. The token-shuffle null preserves each row's symbol distribution and removes only the within-row spatial correspondence.

## Original evidence

Lead #155. Tool: `tools/token_value_probe.py`, PR #154, commit `3da9740` (the `table` mode is unchanged from `18c815b`). The table is a least-squares solve because the block mean of the fitted value is linear in the per-block symbol fractions.

Files are CC0 raw.pixls.us copies:

- 1993 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1995 `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1997 `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`
- 1998 `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`
- 1994 `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`

Found by @radialmonster, 2026-10-21.

## Verification

New run on 2026-10-21, after lead #155 was posted, on two files the lead did not use: 1997 (same normal 5240-wide class) and 1994 (High Res, 10400x7792). Same command and settings as the lead.

- 1997: r=+0.10556, R2=+0.00818, shuffle -0.00254 +/- 0.00991, z=+10.91. Direction, magnitude and significance agree with the lead's 1993/1998 runs.
- 1994 High Res: r=+0.05517, R2=-0.04055, shuffle +0.00184 +/- 0.01056, z=+5.05. The direction agrees and the shuffle is centred on zero, but the absolute scale does not transfer to High Res; this finding does not claim High Res calibration.

The lead's 1993 and 1998 rows are its original evidence; this verification adds 1997 and 1994 and re-runs the held-out-row and q=0 table-order values.

## Reproduce

With the tool from PR #154 at `3da9740`, using the raw.pixls.us files named above (downloaded names use `_` for `:` in `(4:3)`):

    python -I tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1997_Olympus - E-M1MarkII - 16bit (4_3).ORI" --rows 600 --mode s --lam 1 --smooth 10 --perms 4
    python -I tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1994_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode s --lam 1 --smooth 10 --perms 4
    python -I tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1993_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode s --lam 1 --smooth 10 --perms 4
    python -I tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1998_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode s --lam 1 --smooth 10 --perms 4
