# Common-window suffix widths across three known files and two windows

Part of #197. Builds on #239/#260/#281. Measured by @radialmonster.
Design fixed before outcomes in [the claim](https://github.com/radialmonster/orf-cleanroom/issues/197#issuecomment-6329250992).
This follows RULES.md and is released under CC0. Original file measurements only;
no images/previews, other raw-decoder material or private inputs were used.
Both agents represent the same human, not independent human verification.

## Scope and method

This report extends #281's E-M1 Mark II prefix-only common-window width comparison
to already-studied OM-1 and OM-5 files and one later window. These are known-profile
convenience inputs, not untouched discovery/validation captures. Seeds are
algorithmic controls, not additional camera captures. No finding is claimed.

Unchanged [tools/token_framing_probe.py](https://github.com/radialmonster/orf-cleanroom/blob/1de479f13d2229cb35617cc581258655003f0777/tools/token_framing_probe.py) at
`1de479f13d2229cb35617cc581258655003f0777` (also cycle base
`f418be51e834dccd733eee28850ad858ec7efda6`): exact 131072-byte logical strip-payload
windows at byte offsets 0 and 8388608, independently restarted at window bit zero;
seeds 20261021 and 20261022; `--suffix-width-scan --markov --local-byte-block 256`.
For each model/window the same bytes are parsed at every k=2..8. Candidate grammar
is q zeros, stop 1, k suffix bits, complete tokens only, no extra escape skip.
The arbitrary anchor is not an established whole-stream boundary.

Six models: real, measured-p independent Bernoulli, global byte shuffle,
alternating per-value maximal-run-length shuffle, fitted first-order binary
Markov, and independent byte shuffle within consecutive 256-byte blocks.
Bernoulli preserves density in expectation; Markov uses fitted adjacent-bit
probabilities with finite counts unconstrained. Byte controls preserve exact
respective histograms; run control preserves per-value maximal-run multisets and
endpoints. None preserves every local statistic or establishes framing.
Fresh `Random(seed)` per model, Python 3.13.15. No settings selected after outcomes.

The accompanying [JSON](lead197-cross-body-width-windows.json) is a lossless array
of four complete CLI reports, in offset-then-seed order: all 12 sample/window/seed
records, 504 model/width cells, exact counts/endpoints, probabilities, identities
and metadata. The compatibility k5 summaries are retained too. All inputs succeeded,
all windows had exactly the requested length, all q0 denominators were positive,
and all endpoints reconcile with their 1048576-bit budgets. No raw/pixel bytes or
local paths are stored.

## Public inputs and reusable provenance

Local hashes matched retained verified-CC0 inventory and exact existing
`samples/manifest.csv` id/name/hash rows before measurement and supervisor audit.
No catalogue refresh, new licence inference or manifest changes.

- 1993, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`.
- 5283, `OM System - OM-1 - 16bit (4:3).ORF`, SHA256 `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`.
- 6343, `OM System - OM-5 - 16bit (4:3).ORF`, SHA256 `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.

Source SHA256 (file bytes in this checkout):
`token_framing_probe.py`: `46e01f28930b22e02b5aaa2d5661d253a114807fbd8c044c1155b63344ff9cb9`;
`orf_signature.py`: `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`;
`test_token_framing_probe.py`: `c72f1ac33afe0c12afa06f4e0cb29015548be3a62e4cd6a254e113eb3a76a719`.

## Results

Compare q0_count/tokens as exact rational numbers, not rounded fractions. A listed
width has real q0 strictly greater than every one of its five matched controls.
This descriptive label is not significance, a codec estimator or true framing.

Widths above all matched controls, at both seeds unless stated:

- Offset0, 1993: {5,7}; 5283: {2,5,6,7}; 6343: {5,7}.
- Offset8388608, 1993: {5}; 5283: {2,3,5,6,7}.
- Offset8388608, 6343: {2,5,7} at seed20261021; {5,7} at seed20261022.

Thus k5 exceeds all controls in 12/12 records; k7 does so in 10/12. Extra widths
pass on selected cross-body inputs, and one k2 comparison changes with seed.
The E-M1 prefix's k5-and-k7 description does not transfer unchanged to every later
window. This does not contradict the older prefix measurement or prove k5 uniquely
identifies camera framing. Every width/control cell is retained in JSON.

## Reproduce

First review the complete pinned tool and imported `orf_signature.py`; match local
hashes against retained verified CC0 provenance. New/changed unverified content
requires its first licence verification. In PowerShell assign `$file1993`,
`$file5283`, `$file6343` to the checked public samples, then:

```powershell
python -I -B tools/test_token_framing_probe.py
foreach ($offset in @(0, 8388608)) {
    foreach ($seed in @(20261021, 20261022)) {
        python -I -B tools/token_framing_probe.py --suffix-width-scan --markov --local-byte-block 256 --bytes 131072 --offset-bytes $offset --seed $seed --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" $file1993 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" $file5283 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" $file6343
    }
}
```

The JSON array preserves these four stdout reports in loop order. This one-off
read-only reducer over the existing aggregate file prints every comparison:

```python
import json
from fractions import Fraction
from pathlib import Path
reports = json.loads(Path("stats/lead197-cross-body-width-windows.json").read_text(encoding="utf-8-sig"))
total = 0
for report in reports:
    assert report["complete"] and report["failure_count"] == 0
    for sample in report["samples"]:
        models = sample["suffix_width_scan"]["models"]
        above = []
        for index, k in enumerate(range(2, 9)):
            rows = {model: values[index] for model, values in models.items()}
            assert all(row["suffix_bits"] == k and row["tokens"] > 0 for row in rows.values())
            assert all(row["bits"] == row["consumed_bits"] + row["residual_bits"] == 1048576 for row in rows.values())
            fractions = {model: Fraction(row["q0_count"], row["tokens"]) for model, row in rows.items()}
            if all(fractions["real"] > value for model, value in fractions.items() if model != "real"):
                above.append(k)
            total += len(rows)
        print(sample["pixls_id"], sample["window"]["offset_bytes"], report["seed"], above)
print("model_width_cells", total)
```

## Audit and Status

Full runtime/import/test code reviewed before execution. All 33 existing tests,
CLI help and four complete CLI runs pass. Supervisor freshly hash-checked the
three inputs against retained verified CC0 records and manifest, reproduced all
four complete CLI reports exactly, and independently matched all 504 cells and
Markov fits using an original CPU TIFF locator/string parser/six null generators.
Both agents represent radialmonster, not independent human verifiers. RTX3090
available freely; CPU sufficient. No numerical correction required.

Holds descriptively: all 504 cells and the width sets above. Historical prefix
agreement is a compatibility check only. No historical numerical or camera claim
is declared contradicted. Not tested: calibrated significance/exchangeability,
untouched captures, actual codec framing/alphabet/rows, adaptation, predictors,
values, controlled captures or decoding. No finding, spec/decoder change or issue
closure follows. All broader #197 questions remain open; independently justified
framing evidence or controlled captures would address them. Exact rerun pinned
above. Every new sample number uses named public CC0 content, none private;
no historical private values reproduced. Review/merging belongs to hourly maintenance.

Codex-Session: 01a160e4-a62c-77b0-9d20-230c2d4095d1
