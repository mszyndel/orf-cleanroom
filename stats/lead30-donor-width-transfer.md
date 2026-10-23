# Nominal-lattice donor-comb transfer across four public widths

Part of #30. Builds on #11 and #268. Measured by @radialmonster.

The earlier two-file donor diagnostic found a positive/negative/positive b2
correlation sign pattern at lags 2W-2, 2W, 2W+2 in all four nominal classes
on id 1993, while 6343 had mixed signs. The predeclared descriptive transfer
criterion is that same strict sign pattern in every class. It holds on **0/4**
of the selected additional prefixes. This is a new public diagnostic, not a
reproduction or contradiction of the unspecified historical private donor
metric, equality between classes, or a finding.

Design fixed before outcomes in
https://github.com/radialmonster/orf-cleanroom/issues/30#issuecomment-6329167342 .
Use unchanged `tools/token_donor_comb_probe.py` at
`1495728edf48c13cafc714761655a6c8b564cdcf` (introduced by #268). First 262144
complete candidate tokens from payload bit zero, q zeros/one/five suffix bits,
zero extra escape bits; omit a pair when either endpoint has q>=17, preserving
absolute indices and intervening escapes. W is measured payload width. Split
targets by nominal ((t//W)%2,(t%W)%2), no wrapping. All three lags and all four
classes are retained. See the companion JSON for every exact 2x2 table,
pair/omission count, correlation, source hash and input identity.

Selection used existing lawful availability and measured width diversity,
not random scenes or blind confirmation. These four inputs had previous
measurements under other diagnostics but were outside #268's donor cohort.
Both helper and supervisor represent the same human. RTX 3090 is available;
CPU suffices for these small prefixes.

## Public input provenance

Each local SHA256 matched its retained verified CC0 record in the user's
verified inventory and the exact existing `samples/manifest.csv` public
ID/name/hash identity before measurement. No catalogue request, new download,
private input, manifest edit or attribution change was needed. Retained
verification applies to these exact contents, including renamed copies.

- 241, Olympus - E-P3 - 16bit (4:3).ORF,
  `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`.
- 1051, Olympus - E-M1 - 16bit (4:3).orf,
  `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda`.
- 4126, Olympus - E-M10 Mark IV - 16bit (4:3).ORF,
  `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`.
- 6946, OM System - TG-7 - 16bit (4:3).ORF,
  `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a`.

## Complete outcomes

All four requests return 262144 tokens, zero prefix shortfall, zero input
failures. Measured variable-size payloads, compression tag 1; variant remains
unassigned by this diagnostic. No camera-model classification is inferred.
Widths/heights, consumed bits, parsed escapes respectively:

- 241: 4080x3040; 1737004; 3.
- 1051: 4640x3472; 1775448; 3.
- 4126: 5200x3904; 1737857; 1.
- 6946: 4040x3016; 1946399; 2235.

Pearson values below are rounded for reading; JSON retains full float values
and exact tables. Class order is (0,0),(0,1),(1,0),(1,1).

- 241 lag 8158: 0.003313302, 0.005719230, 0.000211642, -0.001475150;
  lag 8160: 0.000853487, -0.004124468, 0.001120378, -0.001037039;
  lag 8162: -0.000619693, -0.000431464, 0.000522714, -0.003788872.
- 1051 lag 9278: -0.005737834, -0.007002100, 0.002642142, -0.003751735;
  lag 9280: -0.002712586, 0.001525971, -0.005021275, 0.005140315;
  lag 9282: 0.002162957, -0.002567058, -0.003232721, 0.002969439.
- 4126 lag 10398: 0.001328603, 0.008800120, 0.007902901, 0.008893987;
  lag 10400: 0.003007802, 0.001835942, -0.001060987, 0.006188359;
  lag 10402: 0.004521069, 0.012892554, 0.000415776, 0.002062786.
- 6946 lag 8078: -0.002506309, -0.005000777, -0.001292401, 0.002842886;
  lag 8080: 0.007258373, -0.001989640, -0.005597293, 0.001291915;
  lag 8082: 0.000878124, 0.003943841, 0.006426816, -0.001472258.

The sign criterion fails per file. Of 16 individual classes, only id 4126's
class (1,0) matches; the complete JSON preserves every class and omission.
TG-7 has a materially higher escape omission burden: 1021..1168 pairs per
class/lag versus 0..3 on the other inputs. No escape omission repairs unknown
post-escape framing. Undefined correlations would fail the criterion; none
occurred here.

W is not an established token row length. Busy files can have extra tokens;
nominal classes need not be physical row/column parities. Finite prefixes,
scene/body/processing confounding, arbitrary parse origin, uncertain framing,
known prior other diagnostics and the selected cohort limit generality.
Strict signs are a descriptive comparison, with no effect-size threshold,
uncertainty model or significance test. Failure does not show absence of donor
structure, and small mixed values do not establish a null distribution. No
serpentine, mirror, shear, causal layout or decode inference follows.

## Reproduce

Read the complete tool and imported `suffix_joint_probe.py` and
`orf_signature.py` at the pinned commit before running. Verify each local
file's SHA256 against the retained verified CC0 record above (new/changed
content needs its first licence verification). Replace FILE241 etc. with the
matching local samples. The measurement command reads samples and prints
aggregate JSON only:

```text
python -I -B tools/test_token_donor_comb_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_donor_comb_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

This read-only one-off reducer runs over the committed existing tool output
with `python -I -B -c` (paste the quoted source as the argument), printing the
criterion from exact table determinants rather than rounded correlations:

```python
import json
from pathlib import Path
r = json.loads(Path('stats/lead30-donor-width-transfer.json').read_text())
assert not r['failures']
for s in r['samples']:
    assert s['prefix_shortfall'] == 0
    passes = []
    for c in range(4):
        signs = []
        for lag in s['statistics']['lags']:
            a, b = lag['classes'][c]['donor_by_target_b2'][0]
            x, d = lag['classes'][c]['donor_by_target_b2'][1]
            signs.append((a*d > b*x) - (a*d < b*x))
        passes.append(signs == [1, -1, 1])
    print(s['pixls_id'], passes, all(passes))
```

Seven unchanged synthetic/actual-entrypoint tests, the scanner self-test and
CLI help pass. Supervisor review covered the frozen diff, complete runtime,
imports and tests, executed-code ledger, scratch aggregates, public code
blocks and retained CC0/manifest provenance. Fresh local hashes matched; a
fresh four-file CLI run matches the complete helper JSON. An original CPU
TIFF locator, string token parser and determinant-form Pearson calculation
independently confirm all 48 tables, pair/omission counts, dimensions, escape
counts and bit endpoints, with correlations agreeing within 1e-14. The
one-off determinant reducer confirms 0/4 files and 1/16 classes. No source or
numerical correction was needed; audit wording and draft spacing were
completed. Source hashes are included in the JSON. No image or preview was
viewed; no prohibited external decoder material or output was used. These
computational checks represent the same human, not independent human
verification. No abandoned artifacts remain in the worktree.

## Status

Holds descriptively: four complete declared prefixes and all 48 tables;
1993's all-class sign pattern transfers to none of these four selected files.
Contradicts: no historical private claim is declared contradicted.
Not tested: the historical metric/equality, significance, physical rows,
serpentine/mirror/shear semantics, true escape framing, other #30 negatives
or decoding. Existing findings are not reverified by this study.
Open: independently justified framing, an operational spatial hypothesis and
controlled independent captures/windows. All unanswered Next steps stay open;
no finding, lead closure or independent-human verification is proposed.
Exact rerun: pinned unchanged tool and commands above. All numerical inputs
are the named public CC0 files; none rests on private files. PR review/merging
belongs to the separate hourly maintainer task.
