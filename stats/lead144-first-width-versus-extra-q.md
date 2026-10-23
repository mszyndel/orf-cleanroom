# Candidate first-width versus extra-token q profiles (#144)

Part of #144. Builds on #11, #218 and #222. Measured by @radialmonster on
2026-10-21 UTC. This is a new bounded descriptive measurement, not a finding,
independent human verification, historical reproduction or decoder rule.

## Design and provenance

The design was frozen before outcomes in
https://github.com/radialmonster/orf-cleanroom/issues/144#issuecomment-6321674493.
It addresses one measurable aspect of the second Next step: compare the first
W candidate tokens with the extra S-W tokens. Public OM-5 id 6343 uses the
previously reported prefix candidate S=5472; OM-5 ORI id 6345 uses S=5533.
Both have measured payload width W=5240 and height 3912, variable payload size,
and compression tag 1. These measurements do not assign a variant; both stay
unassigned in the manifest. The fixed candidates come from #144's evidence,
not a new optimization.

In each of the three 300-row candidate bands starting at ordinals 0, 1000 and
2000, the unchanged tool compares positions [0,W) with [W,S). Boundaries are
absolute token indices r*S from payload bit zero. No phase adjustment, stride
scan, candidate selection or comparison with other decoder outputs occurs.
The candidate grammar is q zero bits, one stop bit, then five skipped suffix
bits. q>=17 tokens remain with no extra escape skip; q is capped at 40.
The actual escape syntax is unknown. The two files and unequal stride choices
cover different bit intervals, so this is a within-cell contrast, not a matched
between-file experiment.

Source: tools/token_band_profile.py at
c5a7c13828d052e1297526ed396b82a278aef36d (last changed f3ab6f0d7247cc4f4be6daa84cc0b69b92c0c750),
with tools/orf_signature.py at the same source commit. Exact source hashes,
input identities and every original tool aggregate are retained in
[the JSON](lead144-first-width-versus-extra-q.json).

Both local input hashes matched retained download/check CC0 records in the
user's verified inventory before measurement, plus existing CC0 manifest
identities; no catalogue request was needed. No manifest row was edited.

- raw.pixls.us 6343, `OM System - OM-5 - 16bit (4:3).ORF`, SHA-256
  `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.
- raw.pixls.us 6345, `OM System - OM-5 - 16bit (4:3).ORI`, SHA-256
  `c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02`.

## Results

All six cells completed all 300 requested candidate rows with zero token
shortfall. Each first-W pool contains 1,572,000 tokens. Each 6343 tail pool
contains 69,600 tokens (232 per candidate row), and each 6345 tail pool has
87,900 (293 per candidate row). Values below are capped-q means; contrasts
and scores are first-W minus tail. The signed mean/SE is descriptive, without
calibrated significance; candidate rows need not be independent.

For 6343 at S=5472, in band order 0/1000/2000:

- Exact first-W sums: 884740 / 983300 / 993828; tail sums: 47450 / 43794 / 46542.
- First-W means: 0.562812 / 0.625509 / 0.632206; tail means:
  0.681753 / 0.629224 / 0.668707.
- Mean contrasts: -0.118941 / -0.003715 / -0.036501; signed mean/SE:
  -16.240046 / -0.369900 / -4.546457.
- Whole-cell q>=17 counts: 211 / 166 / 150. These are not separately
  localized to first-W versus tail by this tool.

For 6345 at S=5533, in band order 0/1000/2000:

- Exact first-W sums: 991682 / 1130816 / 1164416; tail sums: 73541 / 63653 / 67544.
- First-W means: 0.630841 / 0.719349 / 0.740723; tail means:
  0.836644 / 0.724152 / 0.768419.
- Mean contrasts: -0.205803 / -0.004804 / -0.027696; signed mean/SE:
  -29.932310 / -0.622137 / -3.744655.
- Whole-cell q>=17 counts: 792 / 689 / 805.

Both candidate tails have larger capped-q means than their same-cell first-W
pools in every declared band. The contrast is much smaller at band 1000
than at band 0 in each file. Positive tail sums exclude an all-q-zero tail
under this candidate parse. No suffix values were measured, so constant-byte
padding, a header, a second field, token semantics and physical image rows are
not identified or excluded. A mean alone does not characterize the complete
distribution or prove a distinct population. Fixed-phase dilution and changing
content remain possible, and capping hides the sizes of long unary runs.

## Reproduce

First read the pinned tool and its imports. Match the local files' SHA-256 to
the retained CC0 verification above. With FILE6343/FILE6345 standing for local
copies, run from the pinned checkout:

```text
python -I -B tools/test_token_band_profile.py
python -I -B tools/token_band_profile.py --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7 FILE6343 --stride 5472 --head 5240
python -I -B tools/token_band_profile.py --sample 6345 "OM System - OM-5 - 16bit (4:3).ORI" c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02 FILE6345 --stride 5533 --head 5240
```

Token counts per pool are complete_rows*head and
complete_rows*(stride-head). Divide the respective exact capped-q sums by
these counts to obtain the reported means. For a short one-off reduction of
the committed aggregate JSON (no sample access or new measurement):

```python
import json
with open("stats/lead144-first-width-versus-extra-q.json", encoding="utf-8-sig") as source:
    report = json.load(source)
for sample in report["samples"]:
    for band in sample["bands"]:
        n = band["complete_rows"]
        first_n = n * band["head"]
        tail_n = n * (band["stride"] - band["head"])
        print(sample["pixls_id"], band["start_candidate_row"], first_n, tail_n,
              band["sum_head_q_capped40"] / first_n,
              band["sum_rest_q_capped40"] / tail_n,
              band["signed_mean_over_se"])
```

Six existing synthetic tests and CLI help passed. CPU only; the available
RTX 3090 was unnecessary for this bounded calculation. Supervisor audit and
fresh numerical reruns are recorded in the publication Status comment.

## Status

Holds descriptively: all six declared pools complete; the candidate extra
S-W positions have larger capped-q means than the corresponding first-W
positions, with varying contrasts across fixed-origin bands. Prior prefix
maxima are inputs to this design, not newly verified maxima.

Contradicts: no historical or physical-row claim is declared contradicted.

Not tested: complete q/suffix distributions, tail-localized escape counts,
padding/header/field interpretation, physical rows, phase-adjusted or scanned
later maxima, actual escape syntax, calibrated significance, historical
private values, original pixels or decoding. No finding, lead closure or
independent human verification is requested.

Open: a separately declared candidate-tail q/suffix histogram and matched
position/phase controls would test whether these means reflect broader field
distribution differences. Physical framing evidence is still needed before
interpreting these positions as image rows. All #144 unanswered Next steps
remain open. Rerun: pinned source and commands above. Every sample number
uses the two named public CC0 inputs; no private measurements are involved.
Review and merging remain with the separate hourly maintainer task.

This follows RULES.md and is released under CC0. No images/previews or
forbidden sources were used. Both agents represent the same human
@radialmonster.

Codex-Session: 01a15f64-9aa4-7162-8441-20208eb490cf
