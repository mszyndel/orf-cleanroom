# q x s suffix table reproduces on 1993; transfer is weak and the reverse 1993->1995 direction does not

Author: @radialmonster
Verified by: @radialmonster
Lead: #155
Variant: V1
Builds on: 2026-10-21--radialmonster--suffix-luma-table-weak-transfer, #11, #29, #32
Partial: the `q x s` table's held-out figures and table ordering on the lead's 1995->1993 run, plus transfer to High-Res 1994, 1996 and 1997, and the reverse 1993->1995 direction; not a pixel decode, predictor, scan order, round-trip, other bodies, or the `s`-table results already in the merged finding.

## Claim

This verifies the two variants that the merged suffix-table finding explicitly left outside its scope: a 4-class `q x s` table, and the reverse 1993->1995 training direction.

On the lead's exact `q x s` run (train 1995, test 1993, 600 token rows, mode `qs`, `--lam 1 --smooth 10`), the held-out-row correlation is **+0.14595** and the held-out-file correlation on 1993 is **+0.07719** (R2 +0.00301). The fitted table's order correlation with `s` is **+0.9158** for q=0 and **-0.9791** for q=1, as the lead states. The four within-row token shuffles give **-0.00147 +/- 0.00827** (z=+9.52).

The same fixed `q x s` table, held unchanged, transfers to:

| test file | r | R2 | within-row token shuffle | z |
|---|---:|---:|---|---:|
| 1997 (normal) | +0.14710 | +0.01560 | +0.00074 +/- 0.01012 | +14.46 |
| 1994 (High-Res) | +0.06124 | -0.09138 | +0.00092 +/- 0.01291 | +4.67 |
| 1996 (High-Res) | +0.00292 | -0.09366 | +0.00709 +/- 0.00972 | -0.43 |

So the `q x s` variant's 1993 figures reproduce, and it transfers weakly to two further files, but it is null on 1996. Its transfer is therefore scene-dependent and not universal, the same limit the merged `s`-table finding reports.

The reverse direction (train 1993, test 1995, mode `s`) gives held-out-row **+0.18710** (R2 +0.03012), held-out-file **+0.02895** (R2 -0.40069), and within-row shuffle **+0.00677 +/- 0.00671** (z=+3.31). This reproduces the lead's +0.187 / +0.029: the direction is asymmetric, and the held-out-file transfer is effectively zero.

Limits: these are row-centred correlations of block means on 600 token rows (top 46x400 preview DC blocks), not pixel values. There is no predictor, scan-order model or round-trip, and the token-shuffle null preserves each row's symbol distribution. This is a Self-verification by the same human account as the finder, not independent human verification.

## Original evidence

Lead #155, found by @radialmonster on 2026-10-21. Tool: `tools/token_value_probe.py` on main at `01c6546`; its `table` mode is unchanged from PR #154 (`18c815b`, later `3da9740`). The table is a least-squares solve because the block mean of the fitted value is linear in the per-block symbol fractions. The merged finding `2026-10-21--radialmonster--suffix-luma-table-weak-transfer` gives the corresponding `s`-table numbers and says those variants are outside its scope.

Files are CC0 raw.pixls.us copies:

- 1993 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1994 `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`
- 1995 `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1996 `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`
- 1997 `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`

## Verification

A new run on 2026-10-21 UTC, after lead #155 was posted. Local SHA-256 values were matched to the retained verified CC0 records and to the existing manifest rows for these files before the run; no download or licence lookup was repeated. `python -I -B tools/token_value_probe.py --self-test` passed.

The lead's `q x s` run was repeated exactly and its numbers match to the printed digits: held-out rows +0.14595 (R2 +0.01544), 1993 +0.07719 (R2 +0.00301), q=0 order +0.9158, q=1 order -0.9791. The reverse `s` run also matches: +0.18710 held-out rows and +0.02895 on 1995.

The three new `q x s` test files were fixed before measurement: 1997 (a normal 5240-wide file the lead did not use in the `q x s` run), 1994 and 1996 (High-Res 10400x7792; 1996 was not used by the lead at all). No source, settings or file substitutions were made after seeing results. The training table is identical in every `q x s` run (even rows +0.15433, held-out rows +0.14595), as it must be, because only the test file changes.

Against the lead:

- `q x s` held-out-row r=+0.146: holds exactly (+0.14595).
- `q x s` held-out-file r=+0.077 on 1993: holds exactly (+0.07719).
- q=0 ordered with `s` (+0.916) and q=1 ordered oppositely (-0.979): holds exactly (+0.9158, -0.9791).
- 1993->1995 direction: holds (+0.18710 held-out rows, +0.02895 held-out file).

## Reproduce

With the tool on main at `01c6546`, using downloaded raw.pixls.us files (downloaded names use `_` for `:` in `(4:3)`):

    python -I -B tools/token_value_probe.py --self-test
    python -I -B tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1993_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode qs --lam 1 --smooth 10 --perms 4
    python -I -B tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1997_Olympus - E-M1MarkII - 16bit (4_3).ORI" --rows 600 --mode qs --lam 1 --smooth 10 --perms 4
    python -I -B tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1994_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode qs --lam 1 --smooth 10 --perms 4
    python -I -B tools/token_value_probe.py table --train "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --test "1996_Olympus - E-M1MarkII - 16bit (4_3).ORF" --rows 600 --mode qs --lam 1 --smooth 10 --perms 4
    python -I -B tools/token_value_probe.py table --train "1993_Olympus - E-M1MarkII - 16bit (4_3).ORF" --test "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" --rows 600 --mode s --lam 1 --smooth 10 --perms 4
