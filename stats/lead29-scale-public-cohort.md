# Lead #29 item 7: running-count transfer on six public prefixes

Measured by: @radialmonster, 2026-10-21 UTC.
Builds on: #11, #29 item 7 and the public binary-q estimator from #173.
Tool: unchanged `tools/token_scale_probe.py` at
`71b6e96065564357e601a861fb37a118ff96c724` (#174 CLI validation included).
Exact public names, SHA-256, source hashes, every integer training/test table,
every model loss/signed gain and all 16 comparison replicates are in
[lead29-scale-public-cohort.json](lead29-scale-public-cohort.json).

The predeclared criterion holds on 4 of 6 prefixes (241, 1079, 4126, 4132).
It fails on E-M1 1051 and TG-7 6946. Thus the earlier three-file public
pattern, in which both joint running-count models improved upon lag1 beyond
their own permutation means, does not transfer to every declared prefix.
This binary-q/block estimator differs from the historical private q-magnitude
running-mean protocol: its .10/.011-bit figures are neither reproduced nor
declared contradicted. No finding or independent human verification is claimed.

## Fixed design and provenance

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6310114958)
fixed the cohort and criterion before outcomes. All six locally available
public files in five folders were used: 241 E-P3, 1079 E-PM1, 1051 E-M1,
4126/4132 E-M10 Mark IV, 6946 TG-7. These were outside the earlier
1993/5283/6343 binary-q scale study. Availability selected the cohort; it is
not a random sample, and the two E-M10 files are not assumed independent
scene replicates. All six passed `pixls_samples.py check` immediately before
measurement. Each exact hash, ID, name and CC0 licence matched existing
manifest rows; no manifest rows or attribution were modified. Variable-size
payload signatures remain unassigned, rather than inferred V1 from models.

Primary descriptive criterion per file: BOTH lag1_count8 and lag1_count16
have strictly positive gain against lag1, and EACH gain strictly exceeds its
own mean over all 16 comparison permutations. There is no significance
threshold or p-value, and no selection of the better window after outcomes.

The tool parses the first 262144 complete candidate tokens from payload bit
zero: MSB-first q zeros, one stop and five suffix bits; q>=17 consumes q+6
bits with no extra escape skip. Complete consecutive 128-token blocks retain
original block numbers. Entire escape-containing blocks and incomplete tails
are omitted. Original even blocks train and odd blocks test, without closing
gaps; every model uses identical targets t>=16 and no boundary contexts.

Target y is 1[q>0]. Models are frequency; lag1; count8; count16;
lag1_count8; lag1_count16. Counts include only prior tokens, including lag1.
Joint context = lag1*(window+1)+count. Jeffreys half-count fits
P(y|c)=(n[c,y]+0.5)/(n[c]+1); unseen contexts predict .5. Loss is held-out
cross-entropy, not empirical entropy. Signed gain is control loss minus
model loss; negative gains are preserved. Sixteen Random(20261021+replicate)
within-block whole-token permutations refit and rescore the same models.
They preserve block marginals, not temporal structure, and are descriptive
controls, not uncertainty estimates.

## Selection

All files returned 262144 complete candidate tokens and 2048 complete blocks,
zero shortfall/tail. Python 3.13.15, CPU only; RTX 3090 was unnecessary.
Every model has 112 targets per retained block. Full target counts and unseen
context counts are in JSON; omitted blocks are never counted as observations.

| ID | Payload | Train/test blocks | Omitted train/test | Escapes | Consumed bits |
|---|---|---|---|---:|---:|
| 241 | 4080x3040 | 1022/1023 | 2/1 | 3 | 1737004 |
| 1079 | 4080x3040 | 997/1002 | 27/22 | 55 | 1756598 |
| 1051 | 4640x3472 | 1023/1023 | 1/1 | 3 | 1775448 |
| 4126 | 5200x3904 | 1023/1024 | 1/0 | 1 | 1737857 |
| 4132 | 5200x3904 | 1023/1023 | 1/1 | 3 | 1788524 |
| 6946 | 4040x3016 | 531/540 | 493/484 | 2235 | 1946399 |

TG-7 omits 977/2048 blocks, a strong selective-omission limitation. Omission
cannot repair candidate framing after an earlier escape. Blocks are not
established physical rows; adjacent train/test blocks may remain dependent.

## Results

All six observed model losses (bits/test target), rounded to nine decimals:

| ID | frequency | lag1 | count8 | count16 | lag1_count8 | lag1_count16 |
|---|---:|---:|---:|---:|---:|---:|
| 241 | .975316572 | .973579639 | .974764809 | .975248386 | .973110670 | .973453608 |
| 1079 | .981507840 | .981298496 | .979800924 | .978919541 | .978982340 | .978102668 |
| 1051 | .994890110 | .993946022 | .994497005 | .994803536 | .993834808 | .994020188 |
| 4126 | .971086338 | .970782139 | .966570100 | .965067244 | .964718930 | .963324390 |
| 4132 | .999278593 | .978846635 | .998561758 | .999284849 | .974011891 | .975938106 |
| 6946 | .999346904 | .999353170 | .999619350 | .999502286 | .999826422 | .999845443 |

Primary comparisons: incremental gain against lag1, observed / own
permutation mean, in bits/test target. Every other signed gain against both
frequency and lag1 and every replicate is preserved in the JSON.

| ID | lag1_count8 | lag1_count16 | Criterion |
|---|---:|---:|---|
| 241 | .000468970 / -.000042581 | .000126032 / -.000147188 | holds |
| 1079 | .002316157 / .000935523 | .003195828 / .001658390 | holds |
| 1051 | .000111214 / -.000091856 | -.000074166 / -.000158704 | fails |
| 4126 | .006063209 / .002527859 | .007457749 / .004859453 | holds |
| 4132 | .004834744 / -.000038736 | .002908529 / -.000071517 | holds |
| 6946 | -.000473253 / -.000175332 | -.000492273 / -.000406437 | fails |

In 1051 count16 joint gain exceeds its negative comparison mean but remains
negative; a comparison-only rule would conceal that loss. TG-7 has negative
joint gains and they are below their own negative comparison means. Running
counts alone also lose to lag1 on 241, 1051, 4132 and 6946. These outcomes
limit generality under this estimator; they do not identify codec semantics,
causal adaptation, or a universal scale law.

## Reproduce

Read the full unchanged tool and imported `suffix_joint_probe.py` and
`orf_signature.py` at the named commit first. Read `pixls_samples.py` before
licence checking. Obtain the exact public CC0 files through that downloader,
respecting its refusal to save inside a repository. Substitute each FILE
with its local path. Commands print aggregates only.

```text
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_scale_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_scale_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

The JSON wraps the tool's complete unmodified report with predeclaration
metadata and the boolean decision. Eight synthetic scale tests and the
scanner self-test passed before measurements. Supervisor read the complete
source/imports, reviewed provenance and reran
licence checks and all six reports, obtaining an exact JSON match. A separate
string parser with Counter tables and logarithm-difference scoring confirmed
all 72 observed and first-permutation model tables/scores, bit endpoints,
omissions, manifest identities and all permutation means. Both agents
represent @radialmonster; this is not independent human verification.

## Status

Holds descriptively: all declared measurements completed; the full primary
criterion holds on 241,1079,4126,4132 only.
Contradicts as a generalization of the earlier public three-prefix pattern:
both joint models do not uniformly improve on lag1 in this broader cohort.
Historical private item7 figures are neither reproduced nor contradicted.
Not tested: historical full-q/running-mean estimator, physical row controls,
causal scale adaptation, stationarity, significance, other numbered claims,
or a decoder. Existing findings are not reverified.
Open: settle escape/framing interpretation, then use a separately declared
untouched window/cohort and physical-row controls once boundaries are known.
1051 and 6946 provide public negative-transfer prefixes for those checks.
Exact rerun: commands above at the named immutable tool commit.
All measurements use named public CC0 inputs; no private files support them.
This aggregate study follows RULES.md and is released under CC0 1.0.
