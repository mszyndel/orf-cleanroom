# Ruled out: fixed packing, header framing, row layout and escape variants

Author: @radialmonster
Variant: unassigned
Builds on: F1

## Claim
Several hypotheses about how the stream is framed (row blocks, headers, fixed widths, alternative escape rules and adaptive code lengths) were tested and are not supported on the bodies tested. "Not supported" means the test would have shown a clear signal if the hypothesis were right and did not, not that the hypothesis is impossible.

Not supported:
- Fixed-width packing of values (fixed 6- or 12-bit unpack, plain fixed-bit lanes): the unary-plus-5-bit parse is exactly self-consistent (see the facts file) and the bit statistics do not look like fixed-width fields.
- Adaptive Rice/Golomb parameter per token from past magnitudes (causal width rules), with one, three-phase or shared accumulators: mean row-consumption error 1.7k to 30k bits per row, 0 of 64 test rows consistent on any body. The fixed k=5 parse gives zero error.
- Block headers (block size 32, 64, 128 or 256 tokens, any alignment 0..7): 0 of 64 rows consistent on six streams.
- Multi-token cells (a cell of 1, 2 or 3 tokens under a trigger): 1 token fails everywhere, 2 tokens fits only calm rows, 3 tokens fits calm rows (reducing to the baseline since the trigger rarely fires) and fails on busy bodies.
- Whole-stream grammars with no row resets: none gave a sharper row-period peak than the plain k=5 parse on any busy body.
- A fixed 72-bit row header or a darker plateau at row start: the first 24 tokens average 9.5-14 vs 13.0 later on a calm body, which is the short elevated row-start block, not a fixed header. Not resolved.
- Row period other than W: an earlier suggestion of W-1 was wrong. Streams with a sharp row-start profile give a period equal to W on 5240x3912 (6 of 6), 4640x3472 (7 of 9, the others +1 or +3) and 8200x6132 (1 of 1). Most streams have no sharp profile, so the period is undetermined there, not different from W. On the busy 5220x3912 body the average is 6025 tokens per row and no fixed row period can be detected, so tokens per row should not be assumed equal to W.
- Serpentine row order: the donor correlation comb (offsets 2W-2, 2W, 2W+2) is identical for all four (row parity, column parity) classes, which is a shear or mirror pattern rather than serpentine.
- Column phase: adding column modulo m (m=2..8) to the context gives zero gain (within 0.0003 bit); t modulo 2, 3, 4 and 6 are flat for b2, b4 and the value. A 4-bit alignment grid is not seen (see the facts file).
- Parity or 2x2 class-lock of b2/b4: H(b2b4 | t mod 2) equals H(b2b4). Run-flag semantics for b2: zero-run lengths are close to geometric (mean 1.99, variance 4.2 vs 5.9), no run-copy structure testable without a decode.
- Escape variants: skipping 12 bits after q>=17 gives the baseline row consumption and only matters on busy bodies; no alternative tested (header init, other widths) did better. Variants beyond what F1 states remain untested rather than ruled out.

## Evidence
Private research notes, 2026-10-14..18; not yet reproducible with public tools. Everything here is a lead until a different author reproduces it. Bodies are named by size class only. Row-consumption tests used 64 rows each on six streams from five bodies, with row starts taken from the k=5 parse (flagged where a grammar differs).

## Reproduce
Not yet reproducible with public tools. A reproduction should parse with the F1 model and, for each hypothesis, check whether the bits consumed per row match the target exactly with zero leftover.
