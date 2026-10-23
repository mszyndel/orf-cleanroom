# Nominal width-lag sign transfer on six 5240-wide public prefixes

Author: @radialmonster
Part of #29. Builds on #11, #180 and #183.

## Design and scope

Frozen before measurement in [the claim](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6319929383): known E-M1MarkII id 1993 reference, three additional files of that body (1995/1997/1998), and two other 5240-wide bodies (8549/6347). These samples have other published measurements and were selected for availability/body/width, not blind or random population sampling. No controlled scene, exposure, mode or camera-body causal inference follows.

Unchanged tool: `tools/token_width_lag_probe.py` at `01c6546494ba80a9757934874a4d9d7146cfc247`. First 262144 complete candidate tokens from payload bit zero, MSB-first q zeros/one/five suffix bits; q>=17 consumes q+6 with no extra skip. W is measured payload width. Report past/current b2 at W,2W,2W-2,2W+2 and past b4/current b2 at 2W-1. Omit a pair if either endpoint q>=17, retaining absolute indices and intervening escapes. This selective omission cannot repair unknown escape framing. Every target nominal parity stratum and pooled table remains in the companion JSON.

Primary descriptive criterion: pooled correlation at 2W is negative, both 2W-2 and 2W+2 positive, and past-b4/current-b2 at 2W-1 positive. W is separately reported and was excluded from this primary conjunction before outcomes. Undefined correlations make the criterion undefined. Signs can be assessed from exact count-table covariance numerators; no significance, uncertainty, minimum effect, parity-invariance threshold, physical-row/CFA/donor interpretation or decoder is established. This is a new public transfer criterion; the historical unnamed/private estimator and figures are not reproduced.

## Results

All six return 262144 complete tokens with zero shortfall or failures, variable-size measured signature, unassigned variant. Each payload measures 5240x3912. All 150 exact 2x2 tables, pair counts, omissions, correlations and sample/source hashes are retained in `lead29-width-lag-same-width-transfer.json`. The criterion holds on 3/3 additional same-body files and fails on 2/2 other-body same-width files; the already-known 1993 reference passes. Width alone does not extend the reference sign pattern across this selected cohort. These files are finite prefixes, not assumed independent scene replicates.

Columns below are pooled Pearson correlations, in the predeclared lag order.

| ID | W | 2W | 2W-2 | 2W+2 | 2W-1 (b4 to b2) | Core criterion |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1993 | -0.002682699112 | -0.130166659091 | 0.117432907290 | 0.076137103591 | 0.091174474418 | True |
| 1995 | -0.004794181157 | -0.131436682821 | 0.108129684976 | 0.077836832462 | 0.086221263716 | True |
| 1997 | -0.002869078041 | -0.129464012895 | 0.109017872264 | 0.083105095791 | 0.087203552316 | True |
| 1998 | -0.001965146634 | -0.125697063367 | 0.113134558489 | 0.075081920086 | 0.086168370668 | True |
| 8549 | 0.005233017103 | 0.003006463274 | 0.006500135063 | 0.002982081178 | 0.005326050722 | False |
| 6347 | 0.003663568966 | 0.000429954528 | -0.000208250894 | -0.003700777701 | 0.001639564007 | False |

| ID | Bits consumed | Parsed escapes | Retained pairs W,2W,2W-2,2W+2,2W-1 | Omitted pairs in same order |
| --- | ---: | ---: | --- | --- |
| 1993 | 1595634 | 1 | 256903,251663,251665,251661,251664 | 1,1,1,1,1 |
| 1995 | 1595135 | 1 | 256903,251663,251665,251661,251664 | 1,1,1,1,1 |
| 1997 | 1595581 | 1 | 256903,251663,251665,251661,251664 | 1,1,1,1,1 |
| 1998 | 1595500 | 2 | 256902,251662,251664,251660,251663 | 2,2,2,2,2 |
| 8549 | 1696078 | 1 | 256903,251663,251665,251661,251664 | 1,1,1,1,1 |
| 6347 | 1744299 | 127 | 256656,251421,251424,251419,251422 | 248,243,242,243,243 |

## Public provenance

Every selected local SHA-256 matched the retained verified CC0 inventory and existing manifest ID/name/hash rows before measurement. This reuses the successful verification for identical content, without a catalogue request. Existing manifest rows and attribution are unchanged. No result depends on a private file. The following are public raw.pixls.us identities, not local paths:

- 1993 Olympus - E-M1MarkII - 16bit (4:3).ORF; SHA-256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`; payload 15760125 bytes.
- 1995 Olympus - E-M1MarkII - 16bit (4:3).ORI; SHA-256 `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`; payload 15768425 bytes.
- 1997 Olympus - E-M1MarkII - 16bit (4:3).ORI; SHA-256 `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`; payload 15767553 bytes.
- 1998 Olympus - E-M1MarkII - 16bit (4:3).ORF; SHA-256 `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`; payload 15772675 bytes.
- 8549 OM System - OM-5 Mark II - 16bit (4:3).ORF; SHA-256 `c6fe861982ddc18464cf6858d2700f6813cc3a17956bcb12d1179212c999c76a`; payload 17712547 bytes.
- 6347 OM System - OM-5 - 16bit (4:3).ORI; SHA-256 `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9`; payload 18379515 bytes.

## Reproduce

Read the complete tool and its imports (`suffix_joint_probe.py`, `orf_signature.py`) at the named revision before running. Obtain the named public inputs lawfully and match local SHA-256 to retained verified CC0 records; new/unverified content needs its first licence check. Replace each FILE token with that exact local input. Commands read samples and print aggregates only.

```text
python -I -B tools/test_token_width_lag_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_width_lag_probe.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 1995 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1995 --sample 1997 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1997 --sample 1998 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1998 --sample 8549 "OM System - OM-5 Mark II - 16bit (4:3).ORF" FILE8549 --sample 6347 "OM System - OM-5 - 16bit (4:3).ORI" FILE6347
```

One-off exact-sign reduction over saved existing-tool output (replace REPORT with its JSON file):

```python
import json
with open("REPORT", encoding="utf-8-sig") as f:
    report = json.load(f)
for sample in report["samples"]:
    signs = []
    for row in sample["measurements"]:
        a = row["strata_then_pooled"][-1]["past_by_current_counts"]
        n = sum(map(sum, a))
        sx, sy = sum(a[1]), a[0][1] + a[1][1]
        num = n * a[1][1] - sx * sy
        signs.append(None if not sx * (n-sx) * sy * (n-sy) else (num > 0) - (num < 0))
    core = None if None in signs[1:] else signs[1:] == [-1, 1, 1, 1]
    print(sample["pixls_id"], signs, core)
```

## Verification and Status

Six existing synthetic tests and the scanner self-test passed. The helper reviewed the full unchanged runtime/imports and tests before execution. CPU only; RTX 3090 was available and unnecessary. Supervisor reviewed the actual files, complete runtime/import/test sources, provenance and public code. A fresh full six-input CLI rerun matched the helper JSON exactly. An independent original CPU TIFF reader, string token parser and Counter/covariance calculation confirmed all 150 exact tables, candidates, omissions, correlations within 1e-12, endpoints/escapes and all six retained verified CC0/hash/manifest identities. No source or numerical correction was needed; the report template public CLI extensions for ids 1995/1997/6347 were corrected to ORI before publication. Both agents represent radialmonster, not independent human verification. No images/previews or prohibited decoder material were consulted.

Holds descriptively: complete declared measurements, reference check and the primary criterion in the three additional E-M1MarkII prefixes. Fails as transfer to these two other same-width prefixes. This neither reproduces nor contradicts the historical unnamed/private estimator. Not tested: lead claims 1-7/9 as stated, historical donor figures, magnitude correlation, physical row/CFA interpretation, parity invariance, significance, generality, framing or decoding.

Open: independently justified framing/row boundaries and a separately declared controlled cohort or untouched windows with width-lag controls. All historical Next steps remain open. No finding, specification change or lead closure is proposed; this new transfer metric does not verify the exact historical claim. Review and merging belong to the separate hourly maintainer task.

I confirm this follows RULES.md and is released under CC0 1.0.
