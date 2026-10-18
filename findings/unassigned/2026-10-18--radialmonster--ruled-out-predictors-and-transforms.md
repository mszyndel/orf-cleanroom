# Ruled out: predictor, transform and integration loops over the token stream

Author: @radialmonster
Variant: unassigned
Builds on: F1

## Claim
Treating the tokens as residuals (or transform coefficients) and running them through common predictor or transform structures did not give a smooth, bounded image on the bodies tested. A negative here means "not supported on these bodies". One structural reason applies to all linear loops: the token values are close to white at every lag, so any unit-root linear loop over them is a random walk by construction. That makes boundedness a weak test by itself; the tests below therefore compare against a shuffled null and look at row-to-row correlation, not just boundedness.

Not supported:
- Plain running sum per row, one running sum per pixel parity (stride 2), leaky running sums with coefficient 0.0 to 0.5 and 0.9-0.99. Growth equal to null; the leaky versions are bounded only because they filter white noise.
- Double integration (stride 1 and per parity), second-order loops x=2x[t-2]-x[t-4]+e, Lorenzo (left + up - upleft) in 1D and with stride-2 rows: growth many times the null (for example 176-193 vs 76-83; Lorenzo 18 vs 4-6).
- Row-to-row predictors: previous-row, two-row stride, half-row DPCM, Haar, pair lifting (second-difference ratio 0.85-1.0, seam ratio about 1.00). No cancellation.
- Median-edge and gradient-adjusted nonlinear predictors with zigzag residuals. These are self-clamping so boundedness is automatic. Real standard deviation was 2-8x the null in one test (a bias of the residual, not an image) and equal to the null in another; no texture beyond the null. A weak test, not a positive.
- Selector schemes where b2 picks a left versus up/NE predictor and b4 signs the step. Strict violation rate 8.6-14.8% for the real tokens vs 9.1-15.4% for the null (target exactly zero). Staggered-field variants (m=4q+2j+previous-bit with a median predictor) did not beat the unstaggered map (ratios 0.70-0.95 vs a target of 0.5 or better; worse than null on one body). Two bodies.
- b2 as the sign in a delta recursion against a diagonal donor: sign correlation +0.09 on one body, +0.07 on another, 0.00 on a third; variance ratio 0.91-1.0. A tiny real correlation, no cancellation.
- Planar (rectangle-sum) bounds with w=128: real not more bounded than null (2.47 vs 2.29, 5.2 vs 3.9, 1.89 vs 1.13). Rectangle and bridge bounds were not discriminating.
- Suffix-match dictionary (LZ-like) at lags 1-4, W-2, W, W+2, 2W-2, 2W, 2W+2: match rates 0.030-0.051 vs shuffled baseline 0.035-0.045; lag 2 below baseline. No repeat structure.
- A candidate decoder found by automated parameter search scored well on smoothness, but a block-shuffled null reproduced the same signature, and re-encoding its output did not reproduce the stream (first mismatch within 90 bits, then chance level). Scoring artefact; not supported.

## Evidence
Private research notes, 2026-10-14..18; not yet reproducible with public tools. Everything here is a lead until a different author reproduces it. Bodies are named by size class only: body A (5240x3912, calm), body B (5240-wide class, slow scale drift), body C (near-structureless). Most tests used 300-400 rows, alternating row groups for held-out checks, and three bodies. The 2D tests used real row starts on body A and an approximate reshape on the others. "Null" means the same tokens shuffled within the row or block.

## Reproduce
Not yet reproducible with public tools. A reproduction should compute each loop from the F1 tokens and report the growth of the reconstruction, the row-to-row correlation and the same two numbers for the within-row shuffle.
