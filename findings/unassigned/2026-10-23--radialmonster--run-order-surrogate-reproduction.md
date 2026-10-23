# Run-order surrogate measurement reproduces on public E-M1 Mark II files

Author: @radialmonster
Verified by: @radialmonster
Lead: #322
Variant: unassigned
Builds on: #297, #231, #308

## Claim

On the lead's public `id1993` development slice, the frozen 154-candidate periodic bit-density search has maximum `99.05161517759645` (`11,520,000/116,303`), above all 127 declared run-order surrogate maxima: `0/127` exceedances, plus-one rank `1/128 = 0.0078125`, two exact ties. The winner is the second window, width 2, phase 0, with 378 of 1024 selected ones against 603 of 1024 others. This is a narrow surrogate-model diagnostic; it does not establish camera exchangeability, a p-value, framing, codec syntax or pixel values.

The same frozen search on two further public High Res E-M1 Mark II files not used by the lead also gives `0/127` exceedances. Those two files are additional development controls, not untouched validation.

## Original evidence

@radialmonster opened lead #322 on 2026-10-22. The original tool was `tools/run_reorder_search.py` at commit `427d8f84fc0a69f2b6bc7b719bd6995ecb8623cd` (PR #321). Its predeclared design is a 512-byte logical strip window `[4096,4608)`, two non-overlapping 2048-bit windows, widths 2-12 and every phase (154 candidates), and 127 run-order surrogates from Python `random.Random` MT19937 seed `20261022`. The surrogate preserves each symbol's global maximal-run-length multiset, endpoints, density and all four adjacent-transition counts; it does not preserve local window density, byte histograms or run positions.

The lead's public input is raw.pixls.us id 1993, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`, measured 5240x3912, variable-size payload.

## Verification

A new run was made on 2026-10-23 UTC, after the lead was posted, with the unchanged tool at current main commit `7da0817` (`tools/run_reorder_search.py` SHA-256 `b9d7694b06831644ec28efebf3e1a26358acde30fa25d178ec9cc492bc6177bc`). `git diff 427d8f8..7da0817` over `tools/run_reorder_search.py`, `tools/orf_signature.py` and `tools/test_run_reorder_search.py` is empty. `python -I -B tools/test_run_reorder_search.py` passes all 6 tests.

Local hashes were matched to the retained verified CC0 inventory and existing `samples/manifest.csv` rows before measurement. No download or licence-catalogue request was made.

The lead's id1993 figures reproduce exactly:

- winner: window 1, width 2, phase 0, `selected_n=1024`, `selected_ones=378`, `other_n=1024`, `other_ones=603`;
- exact score `11,520,000/116,303 = 99.05161517759645`, two exact ties;
- exceedances `0/127`, plus-one rank `1/128`, Wilson 95% interval `[0, 0.029359645293763368]`.

The three synthetic development controls also reproduce: constant zero maximum `0` with `127/127`; uniform seed 611 maximum `9.043628441897434` with `42/127`; forced-byte-LSB maximum `229.8228920164404` with `0/127`.

The same frozen search was applied to two public files the lead did not use, with the same window, widths, phases, 127 replicates, seed and transition/run invariants:

- id 1994, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`, 10400x7792: winner window 1, width 2, phase 0, 284/1024 versus 668/1024, score `289.430902287922`, `0/127`, two ties.
- id 1996, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`, 10400x7792: winner window 1, width 6, phase 3, 341/341 versus 639/1707, score `445.857408270865`, `0/127`, one tie.

These are development inputs selected for availability, not untouched validation or independent captures. The lead's warning that a run-conditioned null does not justify a camera p-value or camera exchangeability remains in force.

GPU cross-check: a CuPy 14.0.1 / RTX 3090 implementation recomputed the counts for all 128 bit arrays (the observed window plus 127 surrogates) times all 154 candidates, i.e. 19,712 candidate rows, with exact int64 counts. All selected/other counts and all reduced rational scores match the CPU tool exactly (`0` count mismatches, `0` score mismatches, maximum absolute score difference `0.0`). The CPU tool output is the authoritative published measurement; the GPU result is an independent-backend arithmetic check only. GPU pool high-water was 4,354,048 bytes; CPU surrogate generation 0.24 s, GPU count phase 0.02 s, transfer 0.09 s. No GPU-only claim is made.

## Reproduce

Use a clean checkout of this repository at `7da0817`, the public CC0 files whose hashes are listed above (local filenames may differ), and:

```sh
python -I -B tools/test_run_reorder_search.py
python -I -B tools/run_reorder_search.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" 0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8 FILE1993
python -I -B tools/run_reorder_search.py --sample 1994 "Olympus - E-M1MarkII - 16bit (4:3).ORF" f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23 FILE1994
python -I -B tools/run_reorder_search.py --sample 1996 "Olympus - E-M1MarkII - 16bit (4:3).ORF" eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2 FILE1996
```

The tool prints aggregate JSON only: every observed candidate, every surrogate maximum, exact rational scores and the declared invariants. Compare the `winner`, `exceedances_ge`, `plus_one_rank_diagnostic`, `replicate_maxima` and synthetic development controls. The GPU cross-check source was local scratch and is not submitted; the CPU tool is sufficient to reproduce every number in this finding.

## Public input identities

- raw.pixls.us id 1993, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`, 5240x3912.
- raw.pixls.us id 1994, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`, 10400x7792.
- raw.pixls.us id 1996, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`, 10400x7792.
