# Lead #32: q-inclusive bridge-energy public cohort

Tool: `tools/q_value_bridge_probe.py`, unchanged at
`ce39a503cde7cbe669d5eb369c7d18db8ec19147`. Public raw.pixls.us identities:

- 1993: `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 6343: `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`
- 1995: `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1997: `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`
- 5283: `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`
- 7262: `d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd`


Measured by @radialmonster, 2026-10-21 UTC. Builds on #11, #32,
@mtakemoto's exact bridge-energy design/tool (#64), and the q-inclusive
measurement tool (#182). This report is descriptive lead evidence, not a
finding or independent human verification. Existing findings are unchanged.

## Frozen design and provenance

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/32#issuecomment-6313697133)
fixed this design before target outcomes. IDs 1993/6343 are known smoke
references from #182; 1995/1997/5283/7262 extend that q-inclusive experiment.
Previous suffix-only measurements of these files were known. Selection spans
available public bodies and modes; these are not blind untouched files or a
controlled scene/setting series. No tuning or sample replacement occurred.

Unchanged source at commit `ce39a503cde7cbe669d5eb369c7d18db8ec19147`:
`tools/q_value_bridge_probe.py`, `tools/suffix_joint_probe.py`, and
`tools/orf_signature.py`. Exact source SHA-256 values, Python version, all
public identities/full hashes, measured signatures and every selection count
are in [the aggregate report](lead32-q-bridge-public-cohort.json).
All six files passed `tools/pixls_samples.py check` immediately before this
run and their exact hashes matched existing `samples/manifest.csv` rows;
no manifest or attribution changes were needed. IDs 1995 and 1997 are ORI.
All six variable-size signatures have compression tag 1 and remain unassigned.

Parse from payload bit zero, first 262144 complete candidate tokens,
MSB-first q zeros/one/five suffix bits, zero extra escape bits. Partition
consecutive 128-token blocks; omit entire blocks containing q>=17 and any
incomplete tail. Compute every u32=32q+s and zigzag(u32) cell with one and two
lanes; retain separate absolute-token parity pools. Token blocks/parities
are not established physical rows/channels. For n increments, E=A/n^3 and
N=(n+1)V/(6n^2), A=sum(n*S_k-k*T)^2, V=n*sum(x*x)-T*T. Pool sum(E)/sum(N).
N is the exact observed-multiset permutation mean, not a sampled shuffle or
inferential null test. The 0.5 target is a rough descriptive effect boundary.

## Complete primary results

Every one of 24 primary cells exceeds 0.5; the range is
0.983598044820033 to 3.19820600814722. All four additional files also have
every primary ratio above 0.5. This does not establish independence,
a valid reading, or impossibility of another value map. Values rounded below;
all exact A/V, E/N and ratio fractions plus every parity pool are in the JSON.
Individual block A/V arrays are omitted from the committed summary to keep it
small; the unchanged measurement CLI emits them for exact reconstruction.

| ID | u32, 1 lane | u32, 2 lanes | zigzag, 1 lane | zigzag, 2 lanes |
|---|---:|---:|---:|---:|
| 1993 | 1.660437310 | 1.148577266 | 1.001150428 | 1.001407837 |
| 6343 | 3.129114874 | 1.989083501 | 1.036756806 | 1.004706767 |
| 1995 | 1.690702448 | 1.157461199 | 1.023556119 | 1.009773961 |
| 1997 | 1.688652322 | 1.148711400 | 1.014334537 | 1.008473869 |
| 5283 | 1.301222304 | 1.128680308 | 1.024126881 | 0.983598045 |
| 7262 | 3.198206008 | 2.044355889 | 1.034808709 | 1.024195759 |

| ID | Bits consumed | Retained / complete blocks | Omitted blocks | Parsed escapes |
|---|---:|---:|---:|---:|
| 1993 | 1595634 | 2047 / 2048 | 1 | 1 |
| 6343 | 1725464 | 2014 / 2048 | 34 | 34 |
| 1995 | 1595135 | 2047 / 2048 | 1 | 1 |
| 1997 | 1595581 | 2047 / 2048 | 1 | 1 |
| 5283 | 1822446 | 1787 / 2048 | 261 | 313 |
| 7262 | 1790936 | 1292 / 2048 | 756 | 1156 |

All windows reach 262144 tokens, with no shortfall, incomplete tail or
zero-variance lane. Sample 7262 omits 36.9140625% of complete blocks; this
selective exclusion is a material limitation. Omission cannot repair unknown
post-escape framing. The fixed prefix covers different fractions of each
frame; content, body and mode are confounded. Detrending removes mean drift,
so bridge energy cannot establish bounded undetrended reconstruction. Prior
suffix-only results and historical/private growth metrics are not reproduced.

## Reproduce

Read complete source/imports first at the explicit commit above. Obtain only
CC0 samples through the approved downloader (which refuses in-repo downloads);
substitute your actual paths for FILE1993, etc. Check each input first:

```text
python -I -B tools/pixls_samples.py check FILE1993 FILE6343 FILE1995 FILE1997 FILE5283 FILE7262
python -I -B tools/test_q_value_bridge_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/q_value_bridge_probe.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 1995 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1995 --sample 1997 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1997 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283 --sample 7262 "OM System - OM-1 Mark II - 16bit (4:3).orf" FILE7262
```

Save that aggregate stdout as OUTPUT.json in your own scratch folder. This
one-off reducer over existing output checks exact arithmetic and prints the
committed summary; it never opens samples or writes files. Supply OUTPUT.json
as its sole argument with `python -I -B`:

```python
import json
import sys
from fractions import Fraction

with open(sys.argv[1], encoding="utf-8-sig") as source:
    report = json.load(source)
assert not report["failures"]
assert [s["pixls_id"] for s in report["samples"]] == [1993, 6343, 1995, 1997, 5283, 7262]
ratios = []
for sample in report["samples"]:
    assert sample["returned_tokens"] == 262144 and sample["token_shortfall"] == 0
    for cell in sample["cells"]:
        for pool in [cell["pool"]] + cell["parity_pools"]:
            n = cell["increments_per_lane"]
            a, v = pool["sum_A"], pool["sum_V"]
            assert Fraction(pool["sum_E"]["numerator"], pool["sum_E"]["denominator"]) == Fraction(a, n**3)
            assert Fraction(pool["sum_N"]["numerator"], pool["sum_N"]["denominator"]) == Fraction((n+1)*v, 6*n*n)
            assert Fraction(pool["R_pool"]["numerator"], pool["R_pool"]["denominator"]) == Fraction(6*a, n*(n+1)*v)
        r = cell["pool"]["R_pool"]
        ratios.append(Fraction(r["numerator"], r["denominator"]))
        del cell["blocks"]
report["summary"] = {"primary_cells": len(ratios), "primary_cells_at_or_below_half": sum(r <= Fraction(1, 2) for r in ratios), "min_ratio_approx": float(min(ratios)), "max_ratio_approx": float(max(ratios))}
report["reduction"] = "Individual block A/V arrays omitted; every sample, selection count and exact pooled/parity summary retained. Reproduce individual blocks using the unchanged measurement CLI."
report["_provenance"] = {"measurement_tool": "tools/q_value_bridge_probe.py", "source_commit": "ce39a503cde7cbe669d5eb369c7d18db8ec19147", "inputs": [{k: s[k] for k in ("pixls_id", "pixls_name", "sha256")} for s in report["samples"]]}
print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
```

## Validation and status

Eight synthetic tests passed before measurements, including exact-rational
and exhaustive-permutation controls, opposite-order controls, pooling,
omission/parity accounting and CLI failure handling. The bounded scanner
self-test passed. The reducer verifies every pooled/parity E/N and ratio with
exact Fraction arithmetic and thresholds exact primary ratios. CPU only;
RTX 3090 was available but unnecessary. No images/previews were viewed or
other raw decoder material consulted. No private inputs or pixel dumps.

Supervisor audit read complete source/imports, actual diff, reducer and public
commands; freshly checked all six CC0 licences and manifest identities,
repeated the complete report byte for byte, and independently parsed every
262144-token prefix to check endpoints, retained blocks, escapes and all
exact pooled A/V/lane counts. A separate Fraction oracle passed 1152 lane
energy/null checks over the first 32 retained blocks with all maps/parities.
Corrections before publication: replaced an inaccurate phrase about four
ordinary-body additions with four additional files, and added source/input
provenance at the start of each report. Both agents represent one human.

Holds descriptively: all six declared prefixes complete, with no primary
cell <=0.5; every exact pooled/parity summary and omission count is retained.
Contradicts: no historical private claim is declared contradicted by this
new metric. The scoped original suffix-only findings remain untouched.
Not tested: historical growth values, other #32 maps, physical framing,
significance, reconstruction, mode/content causality or a decoder.
Open: independently justified framing and a predeclared controlled public
cohort with comparable scene/mode or later windows. These prefixes do not
settle all Next steps. Exact rerun is above at the named source commit.
All measurements use public CC0 inputs; none depends on private files.

This follows RULES.md and is released under CC0. AI helper and supervisor
both represent @radialmonster, not separate human verifiers.
Codex-Session: 01a15dfb-f11a-7770-852b-49aebc8f25ed
