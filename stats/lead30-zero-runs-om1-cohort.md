# Complete b2 zero-run distributions within five OM-1 files

Part of #30. Builds on #11, #170, #175 and #184. Measured by @radialmonster on 2026-10-21 UTC. This is a new aggregate comparison using an unchanged merged tool, not a finding or reproduction of historical private figures.

## Fixed design

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/30#issuecomment-6321155507) fixed all five inputs, two windows and the comparison before outcomes. These inputs were outside the earlier zero-run cohorts. Their earlier null-distance results and recorded sensitivity of 200 were already public in #106; this is not a blind or random sample. [tools/token_zero_runs_probe.py at 31a9dc84d43bb0ea108fd87b599f20870f502986](https://github.com/radialmonster/orf-cleanroom/blob/31a9dc84d43bb0ea108fd87b599f20870f502986/tools/token_zero_runs_probe.py) and its imports are unchanged.

Request 262144 complete candidate tokens at absolute token starts 0 and 1048576. Scan from payload bit zero with q zeros, a stop one and five suffix bits, zero extra escape bits. Omit and split at q>=17. Count maximal positive-length b2 zero runs bounded by ones inside a retained segment. Censor both window edges independently; retain leading, trailing and all-zero-segment censoring counts separately. Omission cannot repair uncertain post-escape framing. Candidate-token windows are not established physical rows or regions.

Use #184's descriptive total variation (TV) between the empirical complete-run PMF and a positive geometric fitted to its mean. For histogram H, n=sum(H), T=sum(k*H[k]), p=n/T and largest observed length M:

    TV = (sum(k=1..M, abs(H[k]/n - p*(1-p)^(k-1))) + (1-p)^M) / 2.

The last term includes the infinite tail. Exact rational TV<=1/20 is the predeclared arbitrary descriptive tolerance. It is not a statistical goodness-of-fit/significance test or evidence of a geometric generating law. Fitting selected/censored complete runs does not estimate an unconditional law.

## Public inputs and measured signature

Local SHA-256 matched retained verified CC0 provenance and exact existing manifest ID/name/hash entries before measurement. No catalogue refresh or new download was used. No manifest row or attribution was changed. All five payloads measure variable size and compression tag 1; variant remains unassigned. Model alone does not assign a variant. Exact dimensions, byte counts, source hashes, endpoints, full histograms, all moments, omission/selection/censoring counts and failures are in [the complete aggregate JSON](lead30-zero-runs-om1-cohort.json).

- 5283, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b, 5220x3912.
- 5284, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf, 8180x6132.
- 5285, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874, 10400x7792.
- 5286, OM System - OM-1 - 16bit (4:3).ORI, SHA-256 2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1, 5220x3912.
- 5287, OM System - OM-1 - 16bit (4:3).ORI, SHA-256 dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2, 5220x3912.

## Outcomes and limits

All ten windows complete with zero start/count shortfall and zero failures. TV at starts 0 / 1048576:

- 5283: 0.006827083 / 0.005499544; both meet the tolerance.
- 5284: 0.051544960 / 0.045225466; prefix exceeds, later window meets it.
- 5285: 0.104837249 / 0.115003924; both exceed it.
- 5286: 0.005831285 / 0.004397771; both meet it.
- 5287: 0.006412236 / 0.005997866; both meet it.

Seven of ten cells meet the tolerance. Every 5220x3912 cell meets it (6/6); only one of the four larger-frame cells does. This is a descriptive association among these five selected files, not a causal frame-size/mode effect. The ORF/ORI extension does not establish processing mode. Scene, frame geometry, bpp, processing and sample selection remain confounded; no controlled matching or causal separation was performed. The same raw recorded sensitivity was reported earlier for these files, but this run does not remeasure ISO or determine calibrated sensitivity.

Selected escape counts at starts 0 / 1048576 are 313/318, 83/94, 24/21, 312/292, 293/263, respectively. All selected and skipped escape accounting and boundary censoring remain visible. In particular 5285 has complete maximum run lengths 102/119, means 3.209125034/3.343699764 and population variances 16.69242244/19.45529219; none is trimmed. Prefix/later differences expose window dependence without establishing stationarity or its failure. The historical private 1.99/4.2/5.9 estimator remains unspecified and is not reproduced. Neither meeting nor exceeding TV<=1/20 settles run-copy semantics, true framing, physical rows or a decoder.

## Reproduce

Read the complete method and imported sources first. Match each local SHA-256 to retained verified CC0 provenance and the public identities above. New or changed inputs require their first licence verification; unchanged verified inputs need no online refresh. Run these commands with N=0 and N=1048576, substituting each local file path and retaining complete JSON output:

```text
python -I -B tools/test_token_zero_runs_probe.py
python -I -B tools/token_zero_runs_probe.py --start-token N --tokens 262144 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283 --sample 5284 "OM System - OM-1 - 16bit (4:3).ORF" FILE5284 --sample 5285 "OM System - OM-1 - 16bit (4:3).ORF" FILE5285 --sample 5286 "OM System - OM-1 - 16bit (4:3).ORI" FILE5286 --sample 5287 "OM System - OM-1 - 16bit (4:3).ORI" FILE5287
```

This one-off reduction reads committed aggregate JSON and prints every TV and exact tolerance decision. Run it with python -I -B after source review; it writes no files.

```python
import json
from fractions import Fraction as F

with open("stats/lead30-zero-runs-om1-cohort.json", encoding="utf-8-sig") as f:
    reports = json.load(f)["reports"]
for report in reports:
    for sample in report["samples"]:
        s = sample["statistics"]
        h = {x["length"]: x["count"] for x in s["histogram"]}
        n = sum(h.values())
        total = sum(k*v for k,v in h.items())
        if not n:
            print(sample["pixls_id"], sample["requested_start_token"], None, None)
            continue
        p = F(n, total)
        r = 1-p
        maximum = max(h)
        tv = (sum(abs(F(h.get(k,0),n)-p*r**(k-1))
                  for k in range(1,maximum+1)) + r**maximum)/2
        print(sample["pixls_id"], sample["requested_start_token"],
              float(tv), tv <= F(1,20))
```

Nine existing synthetic tests and CLI help passed before sample measurements. Histogram count/first/second integer moments were checked on every cell. Four exact reducer controls passed: point mass at 1 gives TV=0; point mass at 2 gives 3/4; equal masses at 1 and 2 give 5/18; empty input has no fitted comparison. Python 3.13.15, CPU only; RTX 3090 available but unnecessary for these small jobs. Supervisor reviewed the complete unchanged runtime/import sources, actual two-file diff, ignored artifacts, execution ledger, public code blocks and exact retained CC0/manifest provenance. Fresh five-file hashes passed; both complete CLI reports matched after parsing. An independently written CPU TIFF locator, string parser and run counter confirmed every histogram, selection/escape/censoring count, bit endpoint and moment; a 70-digit Decimal recurrence confirmed all ten TVs and tolerance decisions. Nine synthetic tests, parser self-test, CLI help and four exact reducer controls passed. No source or numerical correction was needed; audit wording and draft spacing were updated. Repository checks and public-text scans passed. Both agents represent radialmonster; this is not independent human verification.

## Status

Holds descriptively: all ten declared windows complete; seven meet the arbitrary tolerance, with the within-body/frame-size grouping above. All histograms and omission/censoring counts remain available.
Contradicts: no historical private numerical or semantic claim tested by its original method, so none declared contradicted.
Not tested: historical private figures, statistical goodness of fit, generating law, stationarity, run-copy semantics, camera modes/causality, true framing, physical rows, other #30 negatives or decoding.
Open: justified framing and an operational semantic hypothesis, plus controlled sampling to separate scene/frame-size/bpp/processing effects. No unanswered lead question closes. Exact rerun: immutable method link and commands above. All inputs are public CC0; no number rests on private files.

I confirm this follows RULES.md and is released under CC0 1.0. No images/previews or forbidden decoder material used. Both agents represent the same human @radialmonster, not independent human verification.

Codex-Session: 01a15f4e-793b-7e33-980c-64022ea97a96
