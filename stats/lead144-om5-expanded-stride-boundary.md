# OM-5 expanded candidate-stride boundary diagnostic

Part of #144. Builds on #11, #218 and #266. Measured by @radialmonster,
2026-10-21 UTC. This follows RULES.md and is released under CC0 1.0.

The prior #266 head-8 training maximum on public id 6343 was at its declared
lower search edge, S=5456. This experiment addresses that search limit with
the unchanged merged `tools/token_head_stride_probe.py` at
`3fa9bf0c29809336d8520d33bac549591f4a5052`.
[Design frozen before outcomes](https://github.com/radialmonster/orf-cleanroom/issues/144#issuecomment-6328000819).

## Design and provenance

One reused public CC0 input: raw.pixls.us id 6343,
`OM System - OM-5 - 16bit (4:3).ORF`, SHA-256
`ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.
The local hash matched the retained verified-CC0 inventory and existing
manifest identity before measurement. No online licence refresh was needed.
Measured payload: 5240 by 3912, variable size, compression tag 1; variant
remains unassigned. No numbers depend on private inputs.

All integer strides 5408 through 5536 (center 5472, radius 64) and heads
8/32/128 are retained. Each candidate uses absolute token blocks r*S;
training uses candidate rows 0 through 149. Each head selects the greatest
defined signed training mean/SE; computed floating-score ties select the
lowest stride. Undefined scores cannot win. Test uses 150 candidate rows
starting at ordinal 154, fixed by ceil(150*5536/5408). The latest training
endpoint is token 830400 exclusive; earliest test start is 832832, leaving
2432 tokens between these global bounds. Candidate windows span different
token intervals and the heads overlap.

Candidate parsing is q zeros, stop one, five suffix bits, accepting complete
tokens only. It retains q>=17 with no additional escape skip and caps q at
40 for profiling. Actual escape syntax is unknown. Signed mean/SE is a
descriptive score; no null distribution or calibrated significance is given.
Inputs and local neighborhood were informed by previous exploratory results.
There was no adaptive expansion after these outcomes.

## Results

All 387 head/stride cells complete both 150-row splits: 774 split cells,
zero shortfall. The parse consumes 11052864 bits for 1682944 tokens.
Full exact contrast sums/squares, capped-q sums, escapes, completeness,
endpoints, scores and ties appear in
`lead144-om5-expanded-stride-boundary.json`.

All three heads uniquely select S=5455, interior to this declared window
and one below the former lower edge 5456. For heads 8/32/128 respectively:

- Training signed scores: 5.988873685433 / 12.502045720748 / 19.861975403007.
- Selected test signed scores: 0.017055429503 / -1.051772488049 / -3.154683557031.
- Selected test mean head-minus-rest: 0.000864543174 / -0.037691161104 / -0.077091487548.

The wider training search therefore excludes the prior restricted-window
winner as its own maximum for each head. This resolves the boundary
ambiguity within 5408..5536 only. An interior maximum does not establish a
global maximum, physical stride or useful transfer. Two selected test means
are negative and the third is close to zero; no pass/fail threshold was set.
The test starts at ordinal 154 here rather than 151 in #266, so changes in
test scores cannot be attributed solely to changing the candidate set.
Training selection is distinct from each candidate's test score: no
test-local maximum selects the reported stride.

## Reproduce

Read the pinned tool and its imports (`token_band_profile.py`,
`orf_signature.py`) first. Match FILE6343 against its retained verified CC0
hash. With those sources at the commit above:

    python -I -B tools/test_token_head_stride_probe.py
    python -I -B tools/test_token_band_profile.py
    python -I -B tools/token_head_stride_probe.py --radius 64 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7 5472 FILE6343

The JSON is the CLI output, including Python version. Both six-test suites
and CLI help passed. CPU was sufficient; RTX 3090 was available. Same-owner
agents represent @radialmonster, not independent human verification.

## Status

Holds descriptively: all declared candidates/splits complete; all heads
select the unique interior training maximum S=5455 outside the former local
window, resolving that bounded training-search edge ambiguity. Two selected
test contrasts are negative and one near zero under the changed test split.

Contradicts: no historical or physical-row claim was tested using its original
method, so none is declared contradicted. This is a new exploratory search
limit measurement, not a reproduction of the lead's original 300-row scan.

Not tested: global/later-band best strides, physical rows, whole-frame
constancy, phase/framing or content explanations, extra-token meaning, true
escape grammar, calibrated uncertainty, historical/private figures or decoding.
No finding, independent human verification, spec/decoder change or closure.

Open: independent physical-framing evidence and separately justified
contiguous boundary/content controls would distinguish physical layout from
candidate-profile behavior. No further parameter expansion is proposed from
this outcome alone. Every unanswered Next step of #144 stays open. Exact
rerun: pinned source and commands above. All sample numbers use the single
named public CC0 input; no private rerun is required. PR review/merging is
left to the separate hourly maintainer task.
