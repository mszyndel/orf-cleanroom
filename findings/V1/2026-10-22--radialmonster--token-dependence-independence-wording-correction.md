# Within-token H/L mutual information is small but nonzero, not exact independence

Author: @radialmonster
Verified by: @radialmonster
Lead: #11
Variant: V1
Corrects: 2026-10-21--radialmonster--token-dependence-new-bodies
Partial: the within-token H/L MI and b0/b1 marginals on the original four files plus new E-M1 Mark II 1998, and the correction of the "independent" wording; the original lag-order tables, cross-field/same-field structure, b4 to b2 share, prefix sensitivity and all non-tested limits are retained; not a pixel decode, predictor, geometry, physical rows, values or round-trip.

## Claim

The original finding's sentence "H and L are independent within a token" is not supported by its own measurements. H is b4b3 and L is b2b1b0; their within-token mutual information is small but nonzero on every measured file. The unchanged tool prints 0.0027 bit for 1993, 0.0014 for 3800, 0.0015 for 3802 and 0.0013 for 3588, against one-rotation baselines of 0.0000 to 0.0001 bit. The b0/b1 marginals are near fair (0.4753 to 0.4940). A new file not used by the original finding, E-M1 Mark II 1998, prints 0.0007 bit (baseline 0.0000).

The correct statement is a small nonzero within-token association, far below the lag-1 cross-field values. The data do not establish exact independence, and the original finding declared no equivalence threshold. Its verified lag-order tables and the rest of its scope are unchanged.

## Original evidence

The original finding is `2026-10-21--radialmonster--token-dependence-new-bodies` (Partial for lead #11). It reported whole-payload `tools/orf_tokens.py FILE --all` values on E-M1 Mark II 1993 and E-M1 Mark III 3800/3802 and E-M5 Mark III 3588. Its own table gave within-token MI 0.0027, 0.0014, 0.0015 and 0.0013 bit against rotated-pair baselines of 0.0000 to 0.0001, while its text still called H and L independent. That is the wording corrected here; the numerical tables are retained.

Public identities, all CC0 raw.pixls.us files whose local SHA-256 matched the retained verified inventory before measurement:

- 1993 `Olympus - E-M1MarkII - 16bit (4:3).ORF`, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1998 `Olympus - E-M1MarkII - 16bit (4:3).ORF`, `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`
- 3800 `Olympus - E-M1MarkIII - 16bit (4:3).ORF`, `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f`
- 3802 `Olympus - E-M1MarkIII - 16bit (4:3).ORI`, `83932e61123a90a423a81f87d08c9ed66bca5feb0d900d7d1d0924845dfa9f46`
- 3588 `OLYMPUS - E-M5 Mark III - 16bit (4:3).ORF`, `24de6ac3bd5e668ee22fd0dbf2e344608949eb85f7342f28470ce709c9d51226`

Measured values, whole payloads, at `21ca6ea`:

| id | body | bpp | within-token MI(H;L) | rotated baseline | b1 | b0 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1993 | E-M1 Mark II | 6.151 | 0.0027 | 0.0000 | 0.4815 | 0.4939 |
| 1998 | E-M1 Mark II | 6.156 | 0.0007 | 0.0000 | 0.4759 | 0.4936 |
| 3800 | E-M1 Mark III | 6.425 | 0.0014 | 0.0000 | 0.4753 | 0.4892 |
| 3802 | E-M1 Mark III | 6.395 | 0.0015 | 0.0000 | 0.4769 | 0.4900 |
| 3588 | E-M5 Mark III | 6.353 | 0.0013 | 0.0001 | 0.4778 | 0.4940 |

## Verification

A new run was made on 2026-10-22 UTC, after the original finding was posted, with `python -I -B tools/orf_tokens.py FILE --all` at repository main `21ca6ea`. It used the four original public files again and added 1998, a public file the original finding did not use. All five whole-payload parses completed; the tool printed the MI, baseline and marginals above. The four original rounded MI values reproduced exactly, and 1998 gives the new 0.0007 bit value. The original finding's lag-order lines also reproduced in the same runs; they are not restated as a new claim here.

An auxiliary rotation-null check was run on the installed RTX 3090, in ignored scratch, to make sure the small MI is not just estimator noise. It parsed the same payloads with the repository parser, dropped escapes, and compared each observed within-token MI with 1024 rotations of L (Python `random.Random` MT19937, seed 20261022, without replacement). Every observed value was above all 1024 rotation values; an exact pure-Python subset count (200000 tokens, eight rotations) matched the GPU counts. This GPU check is not a repository-reproducible number and is not part of the claim above; it only supports the "small nonzero" wording over "independent".

Limits: the MI is a plug-in estimate and the tool's single rotated baseline is an estimator-bias diagnostic, not a calibrated p-value. The numbers are whole-payload and not row-aligned; escapes are dropped. "Small" is not a bound, and no equivalence threshold is declared. Nothing here establishes values, a predictor, scan order, physical rows, geometry, a round-trip or a decode. The corollary is narrow: the original finding's independence wording is replaced by a measured nonzero MI; its verified lag-order scope and all of its non-tested limits stay as they were.

## Reproduce

Read the complete tool, test and imported `tools/orf_signature.py` first, then match each local file to the SHA-256 above:

    python -I -B tools/test_orf_tokens.py
    python -I -B tools/orf_tokens.py "<dir>/1993_Olympus - E-M1MarkII - 16bit (4_3).ORF" --all
    python -I -B tools/orf_tokens.py "<dir>/1998_Olympus - E-M1MarkII - 16bit (4_3).ORF" --all
    python -I -B tools/orf_tokens.py "<dir>/3800_Olympus - E-M1MarkIII - 16bit (4_3).ORF" --all
    python -I -B tools/orf_tokens.py "<dir>/3802_Olympus - E-M1MarkIII - 16bit (4_3).ORI" --all
    python -I -B tools/orf_tokens.py "<dir>/3588_OLYMPUS - E-M5 Mark III - 16bit (4_3).ORF" --all

Read the `within-token MI(H;L)` line and the `suffix bit balance P(bit=1)` line. The exact whole-payload values should be 0.0027/0.0000 for 1993, 0.0007/0.0000 for 1998, 0.0014/0.0000 for 3800, 0.0015/0.0000 for 3802 and 0.0013/0.0001 for 3588 (four decimals). All inputs are public CC0; no number here depends on a private file. The finder and verifier are the same human account, so this is self-verified, not independent human verification.
