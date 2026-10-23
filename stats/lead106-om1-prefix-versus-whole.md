# OM-1 prefix versus whole-payload null-distance sensitivity

Part of #106. Builds on `2026-10-21--radialmonster--null-distance-tracks-bpp-within-body`. Measured by @radialmonster on 2026-10-21 UTC using unchanged [tools/orf_tokens.py](https://github.com/radialmonster/orf-cleanroom/blob/23f0b52ecd75c73487778d95226cd226c71d3968/tools/orf_tokens.py) and [tools/orf_signature.py](https://github.com/radialmonster/orf-cleanroom/blob/23f0b52ecd75c73487778d95226cd226c71d3968/tools/orf_signature.py). The public sample identities and SHA-256 values are below. This new sensitivity comparison is not a finding or reproduction of the lead's original six-file figures.

## Fixed design

The [claim comment](https://github.com/radialmonster/orf-cleanroom/issues/106#issuecomment-6323596942) fixed the five public OM-1 files, both scopes and endpoint rejection rule before new outcomes. These files already had published prefix results; they are neither a blind nor a random cohort. Run the unchanged tool with `--max-tokens 1500000` and `--all`. Candidate syntax starts at payload bit zero: q zero bits, stop one, five suffix bits, no extra escape bits. q>=17 remains a candidate escape, with unresolved actual grammar.

Compare the tool's printed real/null estimates, excess `real/null - 1`, min(q,8) lag1/2/3 correlations, and ordering against payload bits per pixel. Excess uses the printed four-decimal real/null values, exactly as the earlier finding; rounding affects the last displayed digits. For a scope containing n candidates consuming E bits of a B-bit payload with P stored positions, the real estimate is `(B/P)/(E/n)`. Even for the whole scan this differs from the actual count n/P by the factor B/E when residual bits remain; these residual corrections are tiny here and do not change the displayed comparisons. The Bernoulli comparison uses `6+(1-p)/p` expected bits per candidate, with p the measured ones fraction over only the complete bytes before E. This fitted iid comparison is descriptive, without inferential calibration or a codec interpretation.

The known fast-path limitation of this version of orf_tokens can accept a candidate suffix past EOF. The predeclared rule rejects such a whole-payload result rather than repairing the tool. An original independent bounded string scanner checked that each accepted candidate's stop plus five suffix bits fitted inside the actual strip, and checked total count, escape count and both scope endpoints. The actual endpoint checks for these five files are in the aggregate JSON. Unconsumed residual bits are censored; their role is not interpreted as padding or a truncated real codec token. No #138 fix is duplicated.

## Public inputs and measured signatures

All local SHA-256 values matched retained verified CC0 provenance and existing exact manifest ID/name/hash rows before measurement. No catalogue refresh or new download was used. Every measured payload is a single contiguous strip, compression tag 1 and variable size; variant remains unassigned. No manifest row or attribution was changed.

- 5283, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b, 5220x3912, 20003129 payload bytes.
- 5284, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf, 8180x6132, 43559951 payload bytes.
- 5285, OM System - OM-1 - 16bit (4:3).ORF, SHA-256 862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874, 10400x7792, 63641088 payload bytes.
- 5286, OM System - OM-1 - 16bit (4:3).ORI, SHA-256 2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1, 5220x3912, 19942944 payload bytes.
- 5287, OM System - OM-1 - 16bit (4:3).ORI, SHA-256 dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2, 5220x3912, 19242578 payload bytes.

## Outcomes and limits

All five whole-payload runs match bounded candidate counts/endpoints without an accepted out-of-bounds token. Residual lengths in ID order 5283-5287 are 4,4,2,3,2 bits. The entire payload is inspected, while those residual bits contribute no candidate. Whole counts are 23025451,52639788,81570741,22975377,22390070. Candidate escape counts are 24213,10426,8158,23545,15816. The prefix endpoint and all selection budgets are retained.

Excess percentages from the printed four-decimal values, prefix then whole:

- 5283, 7.836 bpp: +1.60% then +1.41%.
- 5284, 6.947 bpp: +6.91% then +6.08%.
- 5285, 6.283 bpp: +10.39% then +12.94%.
- 5286, 7.813 bpp: +1.61% then +1.46%.
- 5287, 7.538 bpp: +2.25% then +2.18%.

The excess remains ordered inversely with bpp among these five files in either scope. Its magnitude is scope-sensitive: the largest change is about +2.54 percentage points on 5285. That file exceeds the lead's 4-12% range when the candidate parse is applied across the whole payload. This does not contradict the original fixed-prefix figures; it limits transferring their range to a different scope. In particular, 5285's prefix real estimate is 0.9845 tokens per stored position, whereas its actual whole count is 1.00659 per stored position. A prefix-based extrapolation can miss this descriptive distinction without establishing a one-token-per-pixel codec.

Lag1/2/3 min(q,8) correlations remain positive in both scopes, with full values recorded. For example, 5283 changes from +0.0481/+0.0335/+0.0433 to +0.0303/+0.0141/+0.0281; 5285 changes from +0.1506/+0.1543/+0.2032 to +0.1537/+0.1554/+0.2285. No statistical significance or stationarity claim follows from those differences.

The [complete aggregate JSON](lead106-om1-prefix-versus-whole.json) retains every aggregate CLI line except local basename and nondeterministic elapsed time/speed, plus exact input/source hashes, scope counts/endpoints, independent bounded count checks and residual lengths. Other printed suffix/row-proxy statistics are retained for completeness, without new interpretation. They are not independently validated by this report's scoped numerical check.

All numbers use these five public CC0 inputs. No private historical values, images, previews or another decoder's material were used. Prefix sensitivity does not identify stationarity, scene busyness, processing mode, calibrated ISO or a causal body/bpp/frame-size effect. The earlier recorded sensitivity of 200 is not remeasured here. ORF/ORI extensions do not establish a camera mode. Nothing here establishes true token/escape framing, physical rows, sensor values, a predictor or a decode. Both agents represent @radialmonster; this is not independent human verification. Existing immutable findings and specs/decoder/conformance are unchanged.

## Reproduce

Read the complete pinned tool and its import before running it. Match local hashes to the identities and retained CC0 records above. New or changed content needs its first licence verification; unchanged verified content needs no catalogue refresh. Run both commands for each of FILE5283, FILE5284, FILE5285, FILE5286 and FILE5287, preserving the complete aggregate output:

```text
python -I -B tools/test_orf_tokens.py
python -I -B tools/orf_tokens.py FILE5283 --max-tokens 1500000
python -I -B tools/orf_tokens.py FILE5283 --all
```

Substitute each other named file in turn. Whole runs can take minutes because they also compute the tool's complete MI tables. Inspect consumed_bits against 8*payload_bytes; do not trust the whole-payload label alone on arbitrary inputs. The source hashes and independent endpoint checks are retained in the JSON.

The following one-off reduction reads only committed aggregate JSON and prints all derived excesses, scope differences and endpoint budgets. Run it with python -I -B after source review; it writes no files.

```python
import json

with open("stats/lead106-om1-prefix-versus-whole.json", encoding="utf-8") as source:
    report = json.load(source)
for sample in report["samples"]:
    prefix, whole = sample["prefix"], sample["whole"]
    p = prefix["printed_real"] / prefix["printed_null"] - 1
    w = whole["printed_real"] / whole["printed_null"] - 1
    residual = 8 * whole["payload_bytes"] - whole["consumed_bits"]
    print(sample["pixls_id"], 100*p, 100*w, 100*(w-p), residual)
```

## Validation

Five existing synthetic token-parser tests and CLI help pass. Full source and imported repository code were read before execution. All five local hashes and exact existing manifest identities were checked before the numerical runs, using retained verified CC0 records. An original bounded string scanner independently implemented the candidate-boundary check and matched all five full counts, escape counts and both endpoints. This is implementation independence under the same human account, not an independent human verifier. CPU was sufficient; RTX3090 was available but unnecessary. Supervisor audit and complete rerun details are recorded in the PR and results comment.

The supervisor reviewed the complete two-file diff, executed source and imports, scratch aggregates, provenance records and public reproduction code. A fresh run of all ten CLI reports matched every aggregate line after removing filenames and timing. A separate original CPU TIFF walker and bounded regex parser confirmed both scopes' token counts, endpoints, escapes, real/null estimates and lag1/2/3 correlations. Fresh file/source hashes, measured signatures, residual lengths and residual all-ones flags passed; the aggregate reducer agreed. No numerical correction was needed. The report clarifies the extrapolated estimate versus actual count and the limits of the terminal scanner. Both agents represent the same human contributor.
