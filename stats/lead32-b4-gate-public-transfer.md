# Lead 32: public transfer of the b4 conditional low-field ordering

Part of #32. Builds on #11 and the original descriptive b4-gate tool (#186).
Measured by: @radialmonster. Both supervising and contributor agents represent this same human; this is not independent human verification.

## Fixed question and method

Design fixed before outcomes in https://github.com/radialmonster/orf-cleanroom/issues/32#issuecomment-6320819136 . The three-prefix smoke in #186 had mean(low4 | b4=0) > mean(low4 | b4=1). Does this descriptive direction transfer to each newly selected public prefix 241/1079/4126/6946? Known 1993/6343 smoke prefixes are reference controls. Other metrics on these files were known before selection; this is not a blind or random scene cohort.

Unchanged tools/token_b4_gate_probe.py at 7d49b20bfcdffd74245558890cee92da71c63b20 parses the first 262144 complete candidate tokens from payload bit zero with zero extra escape bits. Ordinary q<17 tokens are retained individually. Fields are low3=s&7 and low4=s&15, with b4=s>>4. For each field the JSON retains both complete histograms, counts, integer sums and means. Primary direction uses exact cross-products sums[0]*counts[1] > sums[1]*counts[0]; an empty group would make it undefined. No sample replacement, selected q ranges or fitted model.

Every current-q/current-b4 and previous-q/current-b4 17x2 table, all conditional probabilities and unsmoothed empirical MI are retained. Lag pairs must be adjacent original token indices with both q<17; omissions never join neighbours. This individual-token selection differs from whole-block selection in other #32 experiments. No stratified low-field means are measured, and aggregate directions do not establish directions within q strata or remove confounding.

## Public provenance

All selected local SHA256 values matched the retained verified-CC0 inventory and an existing CC0 manifest row with the same public ID/name/hash before measurement. No catalogue request or licence refresh was made. Unchanged verified content reuses its earlier verification. No manifest row was edited or required. Public inputs:

- 241: Olympus - E-P3 - 16bit (4:3).ORF; SHA256 `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`.
- 1079: Olympus - E-PM1 - 16bit (4:3).ORF; SHA256 `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765`.
- 4126: Olympus - E-M10 Mark IV - 16bit (4:3).ORF; SHA256 `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`.
- 6946: OM System - TG-7 - 16bit (4:3).ORF; SHA256 `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a`.
- 1993: Olympus - E-M1MarkII - 16bit (4:3).ORF; SHA256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`.
- 6343: OM System - OM-5 - 16bit (4:3).ORF; SHA256 `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.

All six signatures are measured variable-size payloads; the tool leaves their variant unassigned. Identity, geometry, offset, byte count, parse endpoint and source SHA256s are in lead32-b4-gate-public-transfer.json. The source hash fields pin every runtime file, in addition to the method commit above.

## Outcomes

All six return 262144 complete tokens with zero shortfall and no failures. Both conditional groups are nonempty in every field/sample. In the following lines means are b4=0 / b4=1; comparison uses the exact integers in the JSON, not these rounded displays.

- 241: low3 3.29548145574691 / 3.2982328654005; low4 7.48875858792833 / 6.96799339388935; primary direction True. Ordinary 262141, escapes 3, retained lag pairs 262138, omitted pairs 5, consumed bits 1737004.
- 1079: low3 3.30578807640849 / 3.30608396882594; low4 7.39895208007901 / 6.98321461493338; primary direction True. Ordinary 262089, escapes 55, retained lag pairs 262035, omitted pairs 108, consumed bits 1756598.
- 4126: low3 3.26845999314028 / 3.27945171026157; low4 7.3489566927756 / 6.91432763246144; primary direction True. Ordinary 262143, escapes 1, retained lag pairs 262142, omitted pairs 1, consumed bits 1737857.
- 6946: low3 3.23945942847316 / 3.32934783511836; low4 6.93976611539454 / 7.14970960424751; primary direction False. Ordinary 259909, escapes 2235, retained lag pairs 257684, omitted pairs 4459, consumed bits 1946399.
- 1993: low3 2.74902168617941 / 2.72399193013193; low4 6.37268537106332 / 5.11681399485015; primary direction True. Ordinary 262143, escapes 1, retained lag pairs 262142, omitted pairs 1, consumed bits 1595634.
- 6343: low3 3.13084658559401 / 3.18528481890288; low4 6.99120413678412 / 6.69415016547414; primary direction True. Ordinary 262110, escapes 34, retained lag pairs 262076, omitted pairs 67, consumed bits 1725464.

The primary direction transfers to 3/4 newly selected prefixes; TG-7 id6946 reverses it. The two known references retain their earlier direction. Low3 has the opposite direction on all four new prefixes. This limits universal extrapolation of the three-prefix descriptive low4 ordering, rather than contradicting #186's scoped smoke counts. TG-7 omits 2235 individual escape tokens and 4459 lag pairs; its substantial omission and uncertain candidate framing remain material limitations. Every file has 262143 candidate lag pairs. Exact q tables include all empty/sparse rows, rather than dropping them by outcome.

The historical phrase 'low bits', historical files and estimator were unspecified. These results do not reproduce or refute historical 5.0/3.8 means, independence, gate semantics or another historical number. They do not establish significance, population directions, physical rows, original values, scene/body effects or a decoder. Escape omission cannot repair unknown post-escape framing. No images/previews or prohibited decoder material were used; only public original-file aggregates. CPU was sufficient; RTX 3090 was available and unused.

## Reproduce

Read the full tool/import sources first at the pinned method commit, then verify your local files against retained verified-CC0 hashes above. New/unverified content requires its first licence verification. Run:

```text
python -I -B tools/test_token_b4_gate_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_b4_gate_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946 --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343
```

Replace FILE placeholders with quoted local sample paths. The command prints the committed JSON, apart from python_version when environments differ. Reduce the existing JSON using the following one-off read-only code; it only reads aggregate tool output and prints numbers:

```python
import json
with open("stats/lead32-b4-gate-public-transfer.json", encoding="utf-8") as stream:
    report = json.load(stream)
for sample in report["samples"]:
    field = sample["statistics"]["fields"]["low4"]
    counts = field["counts_b4_0_1"]
    sums = field["integer_sums_b4_0_1"]
    direction = sums[0]*counts[1] > sums[1]*counts[0] if all(counts) else None
    print(sample["pixls_id"], counts, sums, direction)
```

Six unchanged synthetic tests and scanner self-tests passed before target measurement and again during supervisor audit. A fresh full six-file CLI run matched the complete JSON exactly after parsing (PowerShell output had different line endings). An original independent CPU TIFF/string parser confirmed all six hashes/manifest identities, payload metadata, complete-prefix endpoints, both histograms/counts/sums/means, all current/lag q tables and probabilities, escape/lag omissions and MI via the entropy identity. The draft command's four incorrect public bit-depth names were corrected to the verified names before publication; numerical output was unchanged. Full source/import, scratch artifact, public code and text safety checks passed. No finding or independent-human verification is proposed.

## Status

Holds descriptively: all six reports complete, both known reference directions persist, and the primary direction transfers to 3/4 newly selected prefixes.
Limits extrapolation: the direction reverses on id6946 under this declared selection. No historical private claim is declared contradicted.
Not tested: historical metrics/files, calibrated significance, population independence/dependence, operational significance-gate semantics, q-stratified low-field directions, physical framing/rows, causality, other #32 readings or decoding.
Open: an operational gate hypothesis with a specified field definition and independently justified framing/sampling/null controls, followed by a predeclared controlled public cohort/window test. This report does not settle the lead's remaining Next steps; no finding, spec/decoder change or closure is proposed.
Exact rerun: the pinned unchanged method and full command above, plus integer reduction of the companion JSON. Every input is public CC0; no number depends on private files. Candidate review/merging belongs to the separate hourly maintainer task.
