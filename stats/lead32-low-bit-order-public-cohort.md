# Lead #32: low-bit numeric-order transfer on public prefixes

Measured by @radialmonster, 2026-10-21 UTC. Part of #32. Builds on #11,
#29 item 3, and the original `suffix_joint_probe.py` tool (#152).
This negative transfer study is lead evidence, not a finding or independent
human verification. Existing immutable findings and attribution are unchanged.

## Frozen question and method

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/32#issuecomment-6319491021)
fixed the design before measurements. Does increasing
P(b2=1 | b1b0) in unsigned numeric order extend to every selected new prefix,
and does swapping b1/b0 change the classification?

The new cohort is public CC0 raw.pixls.us ids 241 (E-P3), 1079 (E-PM1),
4126 (E-M10 Mark IV), and 6946 (TG-7). Ids 1993 (E-M1 Mark II) and 6343
(OM-5) are known references from #152. Their earlier conditional outcomes
were known, as were other metrics on these bodies. Selection is based on
available public bodies, not a blind scene-controlled sample or outcomes of
this measurement. No sample replacement or parameter tuning occurred.

Unchanged source commit: `01c6546494ba80a9757934874a4d9d7146cfc247`:
`tools/suffix_joint_probe.py` and its `tools/orf_signature.py` import.
The [complete aggregate report](lead32-low-bit-order-public-cohort.json)
retains both exact source hashes, Python version, all sample public names/full
SHA-256 hashes, payload dimensions/bytes/offsets, all tables, correlations,
MI and all 16 permutation comparison values emitted by the unchanged tool.
The extra emitted measures are not selected as additional hypotheses here.
Every local input's SHA-256 matched the retained verified CC0 inventory and
an existing manifest ID/name/hash row before measurement. Prior verification
was reused for unchanged content; no catalogue request or download occurred.

First 262144 complete candidate tokens from payload bit zero, MSB-first
q zeros/one/five-bit suffix, zero extra escape bits. Complete 128-token
blocks start at token 0; omit entire q>=17-containing blocks and any final
incomplete block. No token or pixel arrays are published. All inputs have
measured variable-size payloads and remain variant unassigned.

For exact table C[b2][j], j=b1b0=0,1,2,3, let n[j]=C[0][j]+C[1][j].
Numeric order is (0,1,2,3); swapped-bit order is (0,2,1,3).
At each adjacent a,b compute D=C[1][b]*n[a]-C[1][a]*n[b].
Strict increase requires all D>0; nondecrease requires all D>=0.
Any empty column makes both criteria undefined. No tolerance or significance
threshold is fitted. Classifications use integers, never rounded probabilities.

## Complete primary outcomes

All six prefixes return 262144 tokens, 2048 complete blocks and no incomplete
tail. Every column is nonempty. Neither criterion holds for any of the four
new prefixes in either order. Swapping the two low bits therefore does not
change the failed classification on those four prefixes. The known 1993
reference passes only in numeric order; known 6343 fails in both orders.
Strictly-increasing and nondecreasing classifications coincide in every case.

| ID | P(b2=1), numeric columns 00,01,10,11 | Retained blocks | Escapes | Bits consumed | Numeric / swapped increase |
|---|---|---:|---:|---:|---|
| 241 | .478033487, .476663506, .454173537, .465867065 | 2045 | 3 | 1737004 | false / false |
| 1079 | .484321819, .475436665, .450265118, .464329471 | 1999 | 55 | 1756598 | false / false |
| 4126 | .472261895, .468972731, .447502816, .459123344 | 2047 | 1 | 1737857 | false / false |
| 6946 | .482295381, .489892164, .470598414, .479196465 | 1071 | 2235 | 1946399 | false / false |
| 1993 | .260630158, .306041588, .336596506, .389920131 | 2047 | 1 | 1595634 | true / false |
| 6343 | .421818289, .418387570, .419847328, .440140085 | 2014 | 34 | 1725464 | false / false |

Omitted complete blocks are 2048 minus retained: 3,49,1,977,1,34 in table
order. The TG-7 omission of 977/2048 blocks is a substantial selection burden.
Exact 2x4 tables, all selection counts and unrounded probabilities are in the
JSON. The read-only reduction below prints every signed adjacent cross-product
and both exact classifications, rather than selecting favorable comparisons.

## Reproduce

Read the complete source/import at the pinned source commit first. Match each
local file's hash to its retained verified CC0 record; new content requires
its first licence check. Public names and full hashes are in the JSON and
`samples/manifest.csv`. Substitute each FILE argument with the matching file:

```text
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/suffix_joint_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946 --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343
```

The tool reads files and prints aggregate JSON only. This one-off reduction
reads an existing aggregate output, prints counts/classifications, and checks
its arithmetic on increasing, tied, decreasing and empty-column synthetic
tables using an independent Fraction oracle. Run with the report as argv[1],
for example `python -I -B REDUCER.py stats/lead32-low-bit-order-public-cohort.json`
after placing the following in your own scratch REDUCER.py:

```python
import json
import sys
from fractions import Fraction


def classify(table, order):
    totals = [sum(column) for column in zip(*table)]
    if any(n == 0 for n in totals):
        return {"strictly_increasing": None, "nondecreasing": None, "adjacent_cross_products": None}
    cross = [table[1][b] * totals[a] - table[1][a] * totals[b]
             for a, b in zip(order, order[1:])]
    return {"strictly_increasing": all(x > 0 for x in cross),
            "nondecreasing": all(x >= 0 for x in cross),
            "adjacent_cross_products": cross}

# Fraction comparisons supply an independent synthetic arithmetic oracle.
for table in ([[7, 6, 3, 2], [1, 2, 5, 6]], [[1]*4, [1]*4],
              [[1, 2, 3, 4], [4, 3, 2, 1]], [[1, 0, 3, 4], [1, 0, 2, 3]]):
    for order in ([0, 1, 2, 3], [0, 2, 1, 3]):
        actual = classify(table, order)
        if all(sum(column) for column in zip(*table)):
            p = [Fraction(table[1][j], table[0][j] + table[1][j]) for j in order]
            assert actual["strictly_increasing"] == all(a < b for a, b in zip(p, p[1:]))
            assert actual["nondecreasing"] == all(a <= b for a, b in zip(p, p[1:]))
        else:
            assert actual["strictly_increasing"] is None
            assert actual["nondecreasing"] is None
with open(sys.argv[1], encoding="utf-8-sig") as handle:
    report = json.load(handle)
rows = []
for sample in report["samples"]:
    table = sample["statistics"]["joint_b2_by_b1b0"]
    rows.append({"pixls_id": sample["pixls_id"], "joint_b2_by_b1b0": table,
                 "p_b2_one_given_b1b0_00_01_10_11": sample["statistics"]["p_b2_one_given_b1b0_00_01_10_11"],
                 "numeric_order": classify(table, [0, 1, 2, 3]),
                 "swapped_order": classify(table, [0, 2, 1, 3]),
                 "selection": sample["selection"], "returned_tokens": sample["returned_tokens"],
                 "bits_consumed": sample["bits_consumed"]})
print(json.dumps(rows, indent=2, allow_nan=False))
```

## Limits and status

Holds descriptively: all six reports completed with explicit whole-block
selection; the already-known 1993 numeric-order pattern is present again.
The extension-to-every-new-prefix criterion fails on all four new files.
These observations limit extrapolation of numeric-order monotonicity.
They do not reproduce or contradict #32's historical 12-of-13 claim: that
cohort, estimator and selection were not supplied. A fresh number under a
new public selection rule is not the historical experiment.

Not tested: historical private figures, calibrated significance or population
monotonicity, encoding bit significance/order, physical rows or pixel meaning,
framing/escape semantics, other value mappings, reconstruction or decoding.
Nonmonotonic finite-prefix conditionals cannot identify an alternative code.
Candidate parsing, selective escape omission, scene/body confounding and the
single prefix per file limit generalization. Omission cannot repair unknown
post-escape alignment. Token blocks are not established camera rows.

Open: specify independently justified framing and an operational bit-order
hypothesis, then predeclare untouched within-file windows or a controlled
public cohort and appropriate uncertainty controls. Historical questions and
all remaining Next steps stay open; no lead closure or finding is proposed.
Every number here rests on named public CC0 inputs; no private input is used.
CPU only; RTX 3090 was available and unnecessary. No images/previews viewed or
other raw decoder material used. This work follows RULES.md.
