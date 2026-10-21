# OM-5 fixed-phase later-band cohort extension for #144

Measured by @radialmonster on 2026-10-21 UTC with
`tools/token_band_profile.py` at f3ab6f0d7247cc4f4be6daa84cc0b69b92c0c750.
Builds on #144, #11 and the fixed-candidate tool in #218.
The complete aggregate outputs, including every exact integer contrast moment,
are in `stats/lead144-om5-fixed-phase-bands.json`.
This is an incomplete investigation result, not a finding or a claim of
independent human verification.

Public inputs (raw.pixls.us identity; unchanged CC0 content):

- 6345 `OM System - OM-5 - 16bit (4:3).ORI`, SHA-256
  `c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02`.
- 6347 `OM System - OM-5 - 16bit (4:3).ORI`, SHA-256
  `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9`.

Both local hashes matched retained CC0 download/check records before measurement.
Both already have hash-matched manifest rows; no new row or licence request was
needed. The measured signatures are variable-size 5240x3912 payloads, compression
1, of 18317443 and 18379515 bytes respectively. This does not assign a compressed
variant from body name alone.

## Frozen measure

The Taking this comment at
https://github.com/radialmonster/orf-cleanroom/issues/144#issuecomment-6320091634
predeclared both samples, candidate strides and bands before outcomes.
For 6345, candidates are S=5240 and S=5533; for 6347, S=5240 and S=5540.
S=5533 is from the #144 body; S=5540 is from the prefix-profile finding
`2026-10-21--radialmonster--wide-row-stride-new-bodies` (same human contributor).
Each candidate has 300 complete candidate rows starting at ordinals 0, 1000 and
2000, with the first 32 tokens compared with the rest. Boundaries remain absolute
indices r*S from payload bit zero. These are candidate row ordinals, not known
image rows, and different strides therefore sample different later token windows.

The parser is the bounded unary-plus-five candidate syntax with zero extra
escape-bit skipping. It retains q>=17 tokens and caps all q values at 40. The
actual escape grammar remains unknown. Scores are signed mean divided by its
sample standard error, descriptive and not calibrated significance. There is
no phase refit, later-stride scan or image/preview use.

## Results

All twelve bands completed all 300 requested rows; no shortfall or undefined
score occurred. 6345 parsed 12725900 tokens and consumed 85375333 bits; 6347
parsed 12742000 tokens and consumed 85607407 bits. These are the requested
prefix extents through the last tested band, not whole-payload token counts.

Each line lists band0 / band1000 / band2000. Exact values and integer moments
remain in the JSON; these summaries are rounded.

- 6345 S5240 mean differences: 0.025127528162 / -0.033417178699 / 0.009812307988;
  signed scores: 0.993294207788 / -1.616187272166 / 0.549599514851;
  escape counts: 743 / 695 / 703.
- 6345 S5533 mean differences: 0.237551278555 / -0.011125666545 / 0.022105223293;
  signed scores: 14.295562871374 / -0.595266612177 / 1.161438586681;
  escape counts: 792 / 689 / 805.
- 6347 S5240 mean differences: -0.001207277266 / 0.023912890425 / 0.014485727087;
  signed scores: -0.048721789368 / 1.233694094511 / 0.811921693522;
  escape counts: 846 / 728 / 720.
- 6347 S5540 mean differences: 0.239122110264 / 0.034498381143 / 0.028778670419;
  signed scores: 12.943125413582 / 1.717435427337 / 1.501046607708;
  escape counts: 894 / 744 / 789.

The two declared above-width prefix candidates have larger positive head
contrasts in band0 than in either later band, extending the earlier 1993/6343
fixed-phase observation to these additional same-body files. The above-width
prefix scores numerically agree with the published rounded scores, but this
extension does not search for or verify best-stride maxima and is not a finding
verification. Fixed-origin weakening alone cannot distinguish content changes,
accumulated phase, stride changes or an incorrect candidate grammar.

## Reproduce

After reading the pinned tool and its `orf_signature.py` import, match each
local file's SHA-256 against the retained verified CC0 record. FILE6345 and
FILE6347 stand for those exact local files; no catalogue refresh is needed.

    python -I -B tools/test_token_band_profile.py
    python -I -B tools/token_band_profile.py --sample 6345 "OM System - OM-5 - 16bit (4:3).ORI" c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02 FILE6345 --stride 5240 --stride 5533
    python -I -B tools/token_band_profile.py --sample 6347 "OM System - OM-5 - 16bit (4:3).ORI" 062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9 FILE6347 --stride 5240 --stride 5540

All settings not shown use tool defaults: 300 rows, head 32 and start rows 0/1000/2000.
The JSON `runs` array preserves each complete tool output. Only its outer
provenance wrapper is added for the committed aggregate artifact. Six synthetic
tests and the help command passed. CPU calculations suffice for this bounded run;
no GPU numerical claim is made.

Supervisor audit: both exact-input numerical reruns matched every aggregate
field. A separate CPU bit reader matched 10000 token q values and the ending
bit on each input; independent floating mean/stdev calculations matched all
twelve band means and scores. The complete source/imports, diff, scratch
aggregates and public reproduction commands were reviewed. Only JSON formatting
and wording were corrected; measurement logic and results were unchanged.

## Status

Holds in this new fixed-candidate measurement: both above-width candidates have
stronger positive head-minus-rest q profiles in band0 than in bands1000/2000;
all twelve bands complete without shortfall. Their prefix scores agree
numerically with previously published rounded values at these candidates.
Contradicts: no historical or physical-row claim is declared contradicted.
Not tested: best-stride maxima, the universal sharp-peak claim, physical row
boundaries, constant whole-frame stride, the meaning of extra S-W tokens,
escape grammar, calibrated significance, historical private values or decoding.
Open: predeclared later-band stride/phase comparisons with null/content controls
could distinguish fixed-origin failure from shifted profile maxima; physical
framing evidence would still be needed to call those maxima image rows.
Exact rerun: the pinned tool and both commands above. All inputs are public CC0;
no private files support these numbers. No new finding or verification label is
requested, and #144 remains open.
