# Lead 32: candidate-q stratified b4 low-field transfer

Method: `tools/token_b4_gate_probe.py --q-stratified` unchanged at `c33e9d646d690102d0070f8df301d8035190c3e3`.
Inputs: public CC0 ids 241/1079/4126/6343, names and full SHA256 below and in the companion JSON's first lines.
Part of #32; Builds on #11/#186/#226/#237. Measured by @radialmonster; both agents act for this same human, not independent human verifiers.

## Fixed question and method

Design frozen before outcomes in https://github.com/radialmonster/orf-cleanroom/issues/32#issuecomment-6325913358 . The four selected prefixes' pooled low4 direction was already known positive from #186/#226. Their q-stratified diagnostic had not been measured in #32/#237. Selection was based on available verified public inputs and known pooled contrasts, not blind or random scene sampling.

Does mean(low4|b4=0)-mean(low4|b4=1) remain positive in each file's equal-weight average over every defined candidate-q stratum, and is that direction uniform across its defined strata? Low4=s&15 is primary; low3=s&7 is retained as a field-definition control. For each file separately, use ALL q=0..16 with both b4 groups nonempty; compute exact Fraction differences, then their equal-weight average. Empty-group strata are undefined and listed, not assigned zero. No count threshold, selected q range, fitted weights, across-file support intersection or cross-file pooled estimator.

The unchanged tool parses the first 262144 complete candidate q-zero/stop1/five-suffix tokens from payload bit zero with zero additional escape skip. It retains ordinary q<17 tokens individually, without compacting original indices for lag pairs. All q-stratified low3/low4 histograms/counts/integer sums/exact means/contrasts, pooled fields, original current/lag-q tables, MI and omission accounting remain in the JSON. Candidate q is not established codec state; stratification and escape omission cannot repair unknown framing.

## Public provenance

Each selected local SHA256 matched the retained previously CC0-verified inventory and exact existing CC0 manifest ID/name/hash before measurement. No catalogue request, new download or licence refresh. Existing manifest rows and attribution are unchanged; no append is needed.

- 241: Olympus - E-P3 - 16bit (4:3).ORF; SHA256 `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`.
- 1079: Olympus - E-PM1 - 16bit (4:3).ORF; SHA256 `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765`.
- 4126: Olympus - E-M10 Mark IV - 16bit (4:3).ORF; SHA256 `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`.
- 6343: OM System - OM-5 - 16bit (4:3).ORF; SHA256 `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.

All measured payload signatures are variable-size and remain unassigned. The JSON includes geometry, payload offset/size, input SHA256 and all three runtime source SHA256 values. CPU sufficient; RTX 3090 available and unused. No images/previews, private samples or prohibited decoder material used.

## Outcomes

Every file returns 262144 tokens, no shortfall or failures. Low4 pooled means and exact integer-derived q-stratified summaries:

| ID | Pooled b4=0 mean | Pooled b4=1 mean | Equal-q contrast | Defined q | Positive/zero/negative/undefined strata |
|---|---:|---:|---:|---|---|
| 241 | 7.4887585879283325 | 6.967993393889348 | 0.030170357819520148 | 0..8 | 7/0/2/8 |
| 1079 | 7.398952080079014 | 6.983214614933378 | 0.40187470071216946 | 0..16 | 13/0/4/0 |
| 4126 | 7.348956692775596 | 6.914327632461435 | 0.2679534736197143 | 0..8 | 8/0/1/8 |
| 6343 | 6.991204136784118 | 6.694150165474143 | 0.571570383442965 | 0..15 | 12/0/4/1 |

The primary positive equal-q direction persists in 4/4 files. No file has a uniformly positive direction across its defined q strata. Low3 equal-q contrasts, in the same order, are 0.30072439381619087, -0.2297699152739867, 0.08396059390599381 and 0.4606613378747678; all four pooled low3 directions were negative. Exact fractions and every stratum, including zero and undefined cells, are retained rather than selecting favorable rows.

Sparse high-q strata receive the same weight as abundant q=0: id241 q8 counts are 9/1 with contrast -19/9; id1079 q16 counts 2/6 with contrast 55/6; id4126 q8 counts 15/15 with contrast -3/5; id6343 q15 counts 1/1 with contrast 12. These examples illustrate sensitivity; the entire support and counts, including all other sparse strata, are in the JSON. Differing supports mean the four summaries do not estimate a common standardized population effect. Positive averages neither establish all-stratum positivity nor causal adjustment, significance or actual gate semantics.

Selection/endpoints, in cohort order 241/1079/4126/6343:

- Consumed bits: 1737004/1756598/1737857/1725464.
- Ordinary tokens: 262141/262089/262143/262110; omitted q>=17: 3/55/1/34.
- Original-index candidate lag pairs: 262143 each; omitted escape-endpoint pairs: 5/108/1/67; retained pairs: 262138/262035/262142/262076.
- Geometry: 4080x3040/4080x3040/5200x3904/5240x3912.

## Reproduce

Read complete source/imports at the pinned method commit, then match local input SHA256 to the retained verified CC0 identities. New/unverified content requires first licence verification. Run:

```text
python -I -B tools/test_token_b4_gate_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_b4_gate_probe.py --q-stratified --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343
```

Replace FILE placeholders with quoted local paths. The emitted JSON equals the companion file after omitting its added method/source_commit/measured_by/public_inputs provenance fields; python_version can differ across environments. The following one-off read-only reduction of existing aggregate output reproduces all stratum-sign counts and exact summaries. Run with `python -I -B` after reading it:

```python
import json
from fractions import Fraction
with open("stats/lead32-q-stratified-b4-transfer.json", encoding="utf-8") as stream:
    report = json.load(stream)
assert not report["failures"]
for sample in report["samples"]:
    assert sample["returned_tokens"] == sample["requested_tokens"] == 262144
    assert sample["token_shortfall"] == 0
    for field in ("low3", "low4"):
        item = sample["statistics"]["q_stratified_fields"][field]
        values = []
        signs = {"positive": 0, "zero": 0, "negative": 0, "undefined": 0}
        for row in item["strata"]:
            n, total = row["counts_b4_0_1"], row["integer_sums_b4_0_1"]
            d = Fraction(total[0], n[0])-Fraction(total[1], n[1]) if all(n) else None
            signs["undefined" if d is None else "positive" if d > 0 else "negative" if d < 0 else "zero"] += 1
            emitted = row["mean_b4_0_minus_b4_1"]
            assert (None if emitted is None else Fraction(emitted["numerator"], emitted["denominator"])) == d
            if d is not None:
                values.append(d)
        expected = sum(values, Fraction()) / len(values) if values else None
        emitted = item["equal_weight_mean_b4_0_minus_b4_1"]
        assert (None if emitted is None else Fraction(emitted["numerator"], emitted["denominator"])) == expected
        print(sample["pixls_id"], field, signs, expected, float(expected) if expected is not None else None)
```

Ten existing synthetic tests, scanner self-test and help pass; an exact Fraction reduction independently checks every emitted contrast and per-file mean from integer counts/sums. This validates arithmetic and declared coverage, not physical interpretation. Supervisor read the complete unchanged runtime/import/test sources and reviewed the actual two-file aggregate patch, ignored scratch outputs, provenance and public code. A fresh four-file CLI rerun matches the full helper JSON byte for byte (SHA256 a1e368e30777d8354787baf60cf39a630306d9703b85bcec2352794bb5f477b0). An original independent CPU string-find parser, using the reported payload offsets, confirms all four complete-prefix endpoints, escape counts, all 136 low3/low4 q strata histograms/counts/sums/exact contrasts, every support/excluded-q list and all eight equal-q summaries. The payload locator was not independently reimplemented in that check. Local hashes were rechecked against retained verified CC0 records without catalogue requests. Both agents represent radialmonster; this is not independent human verification.

## Status

Holds descriptively: all four complete reports; known positive pooled low4 direction and positive equal-q summary in all four. The primary equal-q direction transfers to these four additional prefixes under this explicit metric.

Limits extrapolation: no file is positive in every defined q stratum. Sparse strata and different support make the equal-q score sensitive and prevent a common cross-file population interpretation. No historical private claim contradicted.

Not tested: historical files/estimator/5.0-vs3.8 values, causal adjustment, population significance/independence, actual gate semantics, true entropy framing/escapes, physical rows, original values, other #32 readings or decoding.

Open: independently justified framing and an operational gate hypothesis with prespecified sampling/uncertainty and meaningful q weights, followed by controlled windows/files. Every unanswered Next step stays open; no finding, spec/decoder promotion, lead closure or independent human verification.

Exact rerun: unchanged pinned method, complete command and aggregate reducer above. All inputs are public CC0; no measurement depends on private files. Candidate review/merging remains with the separate hourly maintainer task.
