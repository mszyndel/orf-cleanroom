# Lead #29 item 6: six-file public lag-MI generality test

Tool: `tools/token_lag_probe.py` at repository commit
`d92f18f5f52f206ff2a5b7ff16b9c317927a2eaa` (unchanged).
Public raw.pixls.us IDs: 241, 1079, 1051, 4126, 4132, 6946;
exact names, SHA-256 and all aggregate tables are in
[lead29-lag-mi-public-cohort.json](lead29-lag-mi-public-cohort.json).
Measured by: @radialmonster, 2026-10-21 UTC.
Builds on: #11, #29 item 6, and the existing public estimator from #164.

The predeclared criterion holds on 2 of 6 prefixes: E-PM1 id1079 and
E-M10 Mark IV id4126. Lag 3 is not the largest q-positive MI on the other
four. This limits the earlier three-file descriptive lag-3 pattern; it does
not reproduce or contradict #29's exact historical held-out/smoothed
figures, whose named private cohort and complete estimator were not supplied.
No finding or independent human verification is claimed.

## Fixed design

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6309388709)
fixed both the cohort and decision before outcomes: all locally available
public files in five specified non-5240 model folders, outside the earlier
1993/5283/6343 lag-MI cohort. This is an availability-selected cohort, not a
random sample of files, cameras or scenes. The two E-M10 IV files are not
assumed independent scene replicates.

Primary descriptive criterion per file: q-positive lag-3 MI is strictly
largest among lags 1..5, and exceeds its own 16-permutation mean. Every
q-positive and low-three-suffix-symbol lag MI and its own comparison mean
is reported; the two symbol alphabets can have different finite-sample biases.

The unchanged tool parses the first 262144 complete candidate tokens from
payload bit zero, using MSB-first q zeros, a one stop bit and five suffix
bits. Candidate q>=17 tokens consume q+6 bits, with no extra escape skip.
It retains complete consecutive 128-token blocks from index zero, omitting
whole escape-containing blocks and incomplete tails. Pairs stay within each
retained block. It computes unsmoothed plug-in MI for binary q>0 and the
8-category low-three-bit symbol, at every lag 1..5.

Each comparison independently permutes whole tokens within each retained
block, using Random(20261021+replicate), replicate 0..15. This preserves
block marginals and within-token dependence, not temporal dependence.
The values are descriptive comparisons, not p-values or uncertainty bounds.
Token blocks are not established camera rows. Selective omissions do not
repair unknown post-escape framing; even retained blocks after an earlier
escape rely on the candidate parse. No decoding or preview access occurs.

## Cohort and selection

All six files passed `tools/pixls_samples.py check` immediately before the
run. Measured TIFF models and dimensions, not the folder labels, identify
the files. Every SHA-256 matches an existing `samples/manifest.csv` row;
no manifest row or prior attribution was changed. All have variable-size
payload signatures and remain unassigned rather than inferred V1 by model.
Python 3.13.15, CPU only; the available RTX 3090 was unnecessary.

Every file returned 262144 tokens and 2048 complete blocks; no incomplete
tail. In the fixed cohort order:

| ID | Measured body | Payload | Retained blocks | Escape-omitted blocks | Candidate escapes | Consumed bits |
|---|---|---|---:|---:|---:|---:|
| 241 | E-P3 | 4080x3040 | 2045 | 3 | 3 | 1737004 |
| 1079 | E-PM1 | 4080x3040 | 1999 | 49 | 55 | 1756598 |
| 1051 | E-M1 | 4640x3472 | 2046 | 2 | 3 | 1775448 |
| 4126 | E-M10MarkIV | 5200x3904 | 2047 | 1 | 1 | 1737857 |
| 4132 | E-M10MarkIV | 5200x3904 | 2046 | 2 | 3 | 1788524 |
| 6946 | TG-7 | 4040x3016 | 1071 | 977 | 2235 | 1946399 |

TG-7 loses 977 of 2048 blocks, so its selected-prefix statistic has a
particularly strong omission limitation. No denominator silently treats
those omitted blocks as retained observations.

## Results

Every q-positive observed MI, in bits, rounded here to nine decimals.
Exact counts and all 16 comparison values per cell are in the JSON.

| ID | lag 1 | lag 2 | lag 3 | lag 4 | lag 5 | Largest lag | Primary criterion |
|---|---:|---:|---:|---:|---:|---:|---|
| 241 | .001804648 | .003750469 | .001548916 | .000223552 | .000146821 | 2 | fails |
| 1079 | .000158802 | .001050605 | .001850534 | .000843943 | .000724691 | 3 | holds |
| 1051 | .000721016 | .001744274 | .000255436 | .000027012 | .000009599 | 2 | fails |
| 4126 | .000373324 | .001299999 | .003885620 | .001330087 | .000991531 | 3 | holds |
| 4132 | .020280215 | .000191798 | .001802944 | .002392382 | .000936966 | 1 | fails |
| 6946 | .000021844 | .000044727 | .000020738 | .000009906 | .000008975 | 2 | fails |

Lag-3 q-positive MI exceeds its own permutation mean on all six, but this
alone does not make lag 3 the largest lag. The two E-M10 IV files have
different winning lags (3 and 1), so the winner is not fixed by measured
model or geometry on these files.

The JSON also reports every low3 observation, own comparison mean and
replicate value. In particular, 4132 low3 lag3 is .006468089 versus a
.007487665 permutation mean; the numerically smaller q-positive lag3
statistic there is .001802944 versus .000006985. Thus comparing only the
magnitudes of q-positive and low3 MI would conceal their different
comparison baselines. No significance or causal claim follows.

## Reproduce

Read the full unchanged tool and its repository imports
`tools/suffix_joint_probe.py` and `tools/orf_signature.py` at the commit
above first. Read `tools/pixls_samples.py` before its licence check. Obtain
the exact public CC0 files through that downloader, respecting its refusal
to save inside a repository. Substitute each FILE token with its local path.

```text
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_lag_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_lag_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

The tool prints aggregates only. The committed JSON wraps its complete
unchanged report with study metadata and the predeclared decision. The
source hashes pin the parser, locator and arithmetic. Five synthetic lag
tests and the scanner self-test passed before the measurements. A fresh
supervisor licence check and six-file report matched the helper output
exactly. A separate string-based bit parser, Counter contingency tables and
entropy-identity arithmetic confirmed all 60 observed joint tables, MI values,
consumed bits and selection counts. Both agents represent the same human;
this audit is not independent human verification.

## Status

Holds descriptively: all declared public measurements completed; q-positive
lag3 exceeds its own permutation mean in all six; the full primary criterion
holds on 1079 and 4126 only.
Contradicts as a generalization of the earlier public three-prefix pattern:
lag3 being the largest q-positive MI does not extend to all six declared
prefixes. Historical exact #29 item6 figures are neither reproduced nor
declared contradicted by this different estimator and cohort.
Not tested: historical held-out/smoothed estimates, stationarity, log-magnitude,
physical row structure, causal scale effects, other #29 claims or a decoder.
Open: settle framing and escape interpretation, then use a declared wider
window/cohort with physical-row controls when boundaries are established;
4132 is a public counterexample worth checking across untouched windows.
Exact rerun: the commands above at the named immutable tool commit.
All numbers use named public CC0 files; none depends on private files.
This aggregate study follows RULES.md and is released under CC0 1.0.
