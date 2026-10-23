# Complete b2 zero-run distributions on six public files

Part of #30. Builds on #11, #170 and #175. Measured by @radialmonster on 2026-10-21 UTC. This aggregate report uses an unchanged tool; it is not a finding or reproduction of the historical private 1.99/4.2/5.9 figures.

## Design fixed before outcomes

The [claim comment](https://github.com/radialmonster/orf-cleanroom/issues/30#issuecomment-6311972508) fixed six public files, two windows and a descriptive tolerance before measurement. Use [tools/token_zero_runs_probe.py at 2513a0e8d8ce30ae07763233f2bc75ca44f06e1d](https://github.com/radialmonster/orf-cleanroom/blob/2513a0e8d8ce30ae07763233f2bc75ca44f06e1d/tools/token_zero_runs_probe.py), with its unchanged imports. Every window requests 262144 complete candidate tokens at absolute index 0 or 1048576. Parse from payload bit zero, q zeros/stop/five suffix bits, with no additional escape bits. Omit every q>=17 token and split the retained stream there. Count only maximal positive-length b2 zero runs bounded by ones inside one retained segment. Both window edges are independently censored, including when they cut an ongoing run; leading, trailing and all-zero-segment censored zero counts remain separate.

Compare the empirical complete-positive-run PMF to a positive geometric PMF fitted to its mean: p=n/T, where n is the complete-run count and T the sum of run lengths. For histogram H and largest observed length M, total variation is

    TV = (sum(k=1..M, abs(H[k]/n - p*(1-p)^(k-1))) + (1-p)^M) / 2.

The final term includes the entire geometric tail after M. Fractions determine the exact comparison TV<=1/20; floats are display values only. This predeclared arbitrary descriptive tolerance is not a statistical goodness-of-fit test, significance threshold or acceptance of a geometric generating law. Fitting a mean to selected complete runs does not estimate an unconditional generating distribution under these censoring/selection rules. No fit threshold was defined in the earlier two-file reports; these are new comparisons on six different files, not a verification of their results.

## Public provenance

All six files passed a fresh tools/pixls_samples.py check before measurement. Exact ID/name/SHA-256 identities match existing CC0 manifest rows, whose attribution remains unchanged. All measured payload signatures are variable-size, compression tag 1, variant unassigned. Model alone does not identify a variant. Full input/source hashes, dimensions, payload byte counts, bit boundaries, histograms, moments and censoring/escape counts are preserved in [the complete aggregate JSON](lead30-zero-runs-public-cohort.json).

- 241, Olympus - E-P3 - 16bit (4:3).ORF, SHA-256 540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd.
- 1079, Olympus - E-PM1 - 16bit (4:3).ORF, SHA-256 db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765.
- 1051, Olympus - E-M1 - 16bit (4:3).orf, SHA-256 19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda.
- 4126, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509.
- 4132, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4.
- 6946, OM System - TG-7 - 16bit (4:3).ORF, SHA-256 4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a.

## Outcomes and limitations

All twelve windows return 262144 complete tokens with zero start/count shortfall. TV values at starts 0 / 1048576, in the predeclared cohort order:

- 241: 0.045680143 / 0.036051953; both meet the descriptive tolerance.
- 1079: 0.020383151 / 0.036038986; both meet it.
- 1051: 0.017452139 / 0.019335327; both meet it.
- 4126: 0.053195660 / 0.034289947; prefix exceeds it, later window meets it.
- 4132: 0.054914891 / 0.140152761; both exceed it.
- 6946: 0.008537936 / 0.002121231; both meet it.

Nine of twelve cells meet the tolerance. Every cell and full histogram is retained, including the 4132 later window: 52761 complete runs, mean 3.1627906976744184, population variance 1364.5039857223646, maximum complete-run length 1875, plus 1268 leading-censored zeros. Its variance/fitted-geometric-variance ratio is 199.47563801396683. No outlier is trimmed or selected away. The prefix/later differences expose descriptive window dependence without identifying its cause or proving nonstationarity.

Selected escape counts at starts 0 / 1048576 are 3/0,55/46,3/0,1/0,3/0,2235/1195. In 6946 the censoring burden is material: leading/trailing/all-zero-segment censored zeros are 2420/3201/168 in the prefix and 1240/1469/69 later. These results describe complete runs under this specific windowing and candidate parse. Selective omission does not repair unknown framing after escapes, and long runs plus boundary censoring can substantially alter distributions. Arbitrary token origin, chosen windows, scene/body/mode confounding, dependence between runs and fitting on the same histogram limit interpretation. No near-geometric PMF claim transfers beyond these twelve measurements. Neither meeting nor exceeding the tolerance settles run-copy semantics, physical rows, any historical private estimator, a causal coding mechanism or a decoder.

## Reproduce

Review the complete sources/imports first. Substitute exact local paths for the six public identities. Licence-check before measurement. Run the measurement command twice, with N equal to 0 and 1048576, preserving each aggregate JSON report.

```text
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_zero_runs_probe.py
python -I -B tools/token_zero_runs_probe.py --start-token N --tokens 262144 --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

This one-off count over the existing aggregate output reproduces every TV and exact tolerance decision from the committed reports. It reads JSON and prints numbers only; use python -I -B for this inline calculation too.

```python
import json
from fractions import Fraction as F

with open("stats/lead30-zero-runs-public-cohort.json", encoding="utf-8-sig") as f:
    reports = json.load(f)["reports"]
for report in reports:
    for sample in report["samples"]:
        s = sample["statistics"]
        h = {x["length"]: x["count"] for x in s["histogram"]}
        n = sum(h.values())
        total = sum(k*v for k,v in h.items())
        p = F(n, total)
        r = 1-p
        maximum = max(h)
        tv = (sum(abs(F(h.get(k,0),n)-p*r**(k-1))
                  for k in range(1,maximum+1)) + r**maximum)/2
        print(sample["pixls_id"], sample["requested_start_token"],
              float(tv), tv <= F(1,20))
```

Nine existing synthetic tests passed before measurements. Four hand-calculated reducer assertions passed: point mass at length 1 gives TV=0; point mass at length 2 gives 3/4; equal masses at lengths 1 and 2 give 5/18; empty input has no fitted comparison. Histogram counts and first/second integer moments were checked for every report. Python 3.13.15, CPU only; RTX 3090 was available but unnecessary. Source hashes record the measured source-file bytes; this repository enforces LF line endings through `.gitattributes`.

## Status

Holds descriptively: twelve declared public windows complete; nine meet the new arbitrary TV tolerance and three exceed it. Complete histograms and omissions are available for every cell.
Contradicts: no historical private numerical or semantic claim is declared contradicted; its inputs and run-support/censoring definitions remain unspecified.
Not tested: statistical goodness of fit, stationarity, run-copy semantics, physical row boundaries, historical 1.99/4.2/5.9 values, the other #30 framing/packing/adaptive-k/escape claims or a decoder.
Open: independently justified framing and an operational run-copy hypothesis, plus a controlled cohort/sampling design for any generating-distribution claim. Existing lead questions remain open. Exact public rerun: unchanged method commit and commands above, with every cell preserved. No number rests on private inputs.

I confirm this follows RULES.md and is released under CC0 1.0. No images/previews were viewed and no forbidden decoder material was consulted. All contributing agents represent the same human @radialmonster; this is not independent human verification.

Codex-Session: 01a15da6-3589-7881-9087-de99c1f158f6.
