# Additional bit-level facts beyond F1, with strength of each

Author: @radialmonster
Variant: unassigned
Builds on: F1

## Claim
Facts about the token stream that F1 does not state, from tests of different strengths. Each item says on how many bodies it was seen. All of these are statistical properties of the F1 tokens, not a decoder.

1. The stop-bit parse is exact. Only k=5 gives zero change in bits consumed per row across the alternatives k=2..8 (both stop-bit conventions). Strong, all bodies tested.
2. About one token per pixel on calm bodies (1.0001, 1.0013 and 1.0036 tokens per pixel on three 5240-wide class bodies) and more on busy bodies (1.025 to 1.034 on the 4640-wide class, 1.154 on the 5220x3912 body). Strong.
3. Within a token, the 3-bit low field is not independent of b2: correlation of b2 with b1 is +0.09 and +0.07 on two bodies and 0.00 on the near-structureless one, with b0 +0.04 to +0.05; b3 and b4 are negatively correlated (-0.15 on two bodies). The joint of b2b1b0 skews toward 000 (0.19) vs 111 (0.10). Mutual information of b2 with b1b0 is only about 0.005-0.008 bit. Moderate, two bodies. Reading b1b0 as an MSB-first number, P(b2=1) rises roughly linearly with it (for example 0.31, 0.33, 0.37, 0.41 on body A); this holds on 12 of 13 non-null streams. Moderate to strong.
4. The b2/b4 chain, in held-out entropy terms: b2 at t is predicted by b2 at t-2 and b4 at t-1, then b4 at t-3, b2 at t-4, b4 at t-5; b4 at t is predicted by b2 at t-1 and t-3. So lags 1-5 alternate between the two bits, like one binary sequence interleaved over b2 and b4. The gain is about 0.15 bit of 0.91 on the calm body, 0.14 on a second body, and 0.016 on the near-structureless one. There is no parity dependence (even and odd t alike) and no linear scrambler relation (no rank-1 relation over GF(2) among 24 context bits); a four-tap form beats a two-tap form by only about 0.02 bit. Strong for the chain; the absence of a deeper law is moderate.
5. Context search outcome: a greedy held-out context search over about 340 features (q class, each bit, magnitude class at lags 1-8, previous row at column offsets -4..+4, two rows back, running means, position since row start, t mod 6) selected only lags 1-5 and running means. No lag-W, lag-2W, row-position or t mod 6 feature was chosen for any bit on any of three bodies (caveat: on two of them W was approximate). Moderate.
6. Where the lag-3 dependence lives: the lag-3 effect noted in F1 sits in q, not in the low bits. Mutual information of q>0 at lag 3 is 0.022 bit on the calm body (vs 0.0003 at lags 1-2, 0.0066 at lag 4, 0.0024 at lag 5), and about 0.0002 bit for the low three bits at lag 3. On one body the log-magnitude autocorrelation at lags 1-4 is 0.01, -0.055, 0.116, 0.036. It is stationary (not locked to a grid), so it is a magnitude-scale effect. Strong on three bodies.
7. A slow scale component: on body B the running mean over 8-16 tokens alone gives 0.10 bit on q; on the calm body only 0.011. So there is adaptive-scale (busy or quiet region) behaviour in some bodies. Moderate, one clear body.
8. Donor correlation structure in b2: b2 is anticorrelated with b2 at positions W and 2W away and positively correlated at 2W-2 and 2W+2 (a planar-predictor residual pattern); b2 vs b4 and magnitude peak at 2W-1. Identical across the four row/column parity classes. Weak to moderate (correlations are tiny, about 0.09 at most), four bodies.
9. A short elevated row-start block of about 10 tokens exists on the calm body; the first 24 tokens average 9.5-14 vs 13.0 later. Moderate, one body.

## Evidence
Private research notes, 2026-10-14..18; not yet reproducible with public tools. Everything here is a lead until a different author reproduces it. Bodies are named by size class only: body A (5240x3912, calm), body B (5240-wide class, slow scale drift), the near-structureless body is a third 5240-wide class body. Entropy and mutual-information figures are held-out (train on even rows, test on odd rows) with light smoothing.

## Reproduce
Not yet reproducible with public tools. Items 1-2 need only the F1 parser; items 3-8 need the tokens' bits and mutual-information or held-out-entropy estimates with a within-row shuffle null.
