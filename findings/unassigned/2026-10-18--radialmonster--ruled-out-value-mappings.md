# Ruled out: ways of turning the token fields into a value

Author: @radialmonster
Variant: unassigned
Builds on: F1

## Claim
Many ways of reading the 5-bit suffix (and the unary count q) as a number were tested and none produced a bounded, image-like reconstruction. This file lists them so they are not repeated. A negative here means "not supported on the bodies tested", not "impossible". The test in nearly every case was: build a running sum or per-row reconstruction from the candidate values and compare its growth, row-to-row correlation and local smoothness with the same tokens shuffled. A real reading should look clearly better than the shuffle; none did.

Tested readings, all not supported:
- Sign taken from b2, from b4, from b3, or toggled by b2 at lag 1 or 2, magnitude from the remaining bits plus q (24 magnitude orderings, then 240 sign/magnitude/zigzag layouts). Three bodies (A, B, C). Cumulative sums grow like a random walk, about the same as the null.
- b2 or b4 as a flag or state (b2, b4, xor, and, or) with magnitude q plus the remaining three bits. Best growth equal to null.
- Two's-complement and ones-complement readings of the low digit; signed digit 4(b4b3)+(b1b0)-8*b2 (worse than null: growth about 15 vs 5). Three bodies.
- Rice zigzag of the whole value, and of u=32q+s, for k from 2 to 8, plus 8 adaptive-k variants: only the fixed k=5 parse is self-consistent (any other fixed or adaptive k changes the bit consumption per row by thousands of bits; k=5 changes it by zero). Calm and busy bodies.
- 3,840 direct maps of (q, b4..b0) onto a value, each tried raw, zigzag and coarse, tested for horizontal and vertical smoothness against the null (target ratio 0.5 or better): best ratio 0.89 to 1.0, and the best map was just the identity (it only reflects q correlation). Three bodies.
- Split-bit maps: u=32q+s, low two bits lo, z=u>>2, signed coarse value from z; also a 256-table sign family. The small coupling between b2 and the low bits is real (see the facts file) but the signed coarse value does not telescope per row better than the null (the per-row sum bound was met 94-100% for both real and null), and the lane cumulative sum wandered more than the null with row-to-row correlation 0.10 vs 0.61 for the null. Three bodies. The 256-table sign family gave raw smoothness 16 to 60 vs a target below 2, not better than a selection-matched null.
- Modular reconstructions: wrapped reconstruction modulo 2^12, 2^14 and 2^16 with single, per-parity, double and Lorenzo loops, on unsigned and both sign readings. Circular smoothness was equal to or below the null in every case (no case exceeded the null by 0.1). A wrap of a random walk is a random walk, so this adds nothing. Two bodies.
- Bit-position readings: b1 and b0 behave like noise (about 1 bit of entropy each), so a reading that makes them high-order bits is unlikely. Reading the 3-bit low field LSB-first is disfavoured: P(b2=1) rises monotonically with the MSB-first value of b1b0 on 12 of 13 non-null streams, and not with the swapped value.
- Block-shared scale (triples, groups of 3 or 6 tokens): the triple intraclass correlation of log-magnitude is identical for shifted groupings (0.327 vs 0.327 on body A); mean value and b2 are flat modulo 3, 4 and 6. No phase-locked blocks. Two bodies.
- b4 as a significance gate (a "no information" flag): not supported, since b4=0 tokens carry higher low bits (mean 5.0 vs 3.8), and P(b4) is independent of the previous q on two bodies and rises weakly with q on a third.

## Evidence
Private research notes, 2026-10-14..18; not yet reproducible with public tools. Everything here is a lead until a different author reproduces it. Bodies are named by size class only: body A (5240x3912, calm, about 1.0 tokens per pixel), body B (5240-wide class, slow scale drift, about 1.0 token per pixel), body C (near-structureless, little context of any kind), body D (5220x3912, busy, about 1.15 tokens per pixel), body E (4640x3472 class). Row length W is the sensor width in tokens. "Null" means the same tokens shuffled within the row or block. The numbers above are the aggregate figures of each test; no public script exists for them yet.

## Reproduce
Not yet reproducible with public tools. A reproduction should parse the stream with the F1 token model, form each candidate value as above and compare the resulting cumulative sum against a within-row shuffle of the same tokens.
