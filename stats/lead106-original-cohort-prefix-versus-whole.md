# Original #106 cohort: prefix versus whole-payload sensitivity

Part of #106. Builds on #249 and the existing null-distance Partial findings. Measured by @radialmonster on 2026-10-21 UTC. This extends #249's OM-1-only scope comparison to the original lead's OM-1 Mark II and OM-3 inputs. It is a new descriptive sensitivity report, with historical prefix values retained as consistency checks. It is not a finding, an independent human verification, a causal body/scene/ISO claim or a complete six-file whole-payload comparison.

## Design fixed before outcomes

The [claim](https://github.com/radialmonster/orf-cleanroom/issues/106#issuecomment-6327029298) fixed exactly six known public inputs, both scopes, the unchanged scanner and the endpoint rejection rule. The cohort was neither blind nor random. [tools/orf_tokens.py](https://github.com/radialmonster/orf-cleanroom/blob/b5cb9c2952e4396649c369a05d2502c97ff6e711/tools/orf_tokens.py), importing [tools/orf_signature.py](https://github.com/radialmonster/orf-cleanroom/blob/b5cb9c2952e4396649c369a05d2502c97ff6e711/tools/orf_signature.py), runs with `--max-tokens 1500000` and `--all`. Candidate syntax starts at payload bit zero: q zero bits, a one stop bit, five suffix bits, and zero extra escape skip. q>=17 remains an escape candidate with unresolved actual grammar.

For each scope, retain every aggregate CLI line except local basename and nondeterministic elapsed time/speed. Compare excess `printed_real/printed_null - 1`, min(q,8) lag1/2/3, counts/endpoints/escapes and residual budgets. Excess uses the printed four-decimal estimates, so the last digits reflect rounding. For n candidates consuming E bits of a B-bit payload containing P stored positions, the tool's real estimate is `(B/P)/(E/n)`. It is a prefix extrapolation, not necessarily the actual whole count n/P. The fitted Bernoulli expected length is `6+(1-p)/p`, with p measured over complete consumed bytes only. This descriptive iid comparison is not a calibrated significance test or an established codec model.

The unchanged scanner has a known fast-path EOF limitation tracked separately in #138. An original bounded string parser independently checks candidate counts/endpoints and escape counts. Any whole scan that accepts a candidate past the actual strip end is rejected as a whole-payload measurement; its full diagnostic output is retained with explicit false acceptance flags. No scanner fix, corrected whole-scope metric, replacement input or post-outcome scope adjustment is made here. Residual bits are censored, without a padding/truncation interpretation.

## Public inputs

Before measurement, each local SHA-256 matched the retained verified CC0 inventory and the exact existing manifest ID/name/hash row. No catalogue refresh or download was used. Every measured input has compression tag 1 and one variable-size strip; variant remains unassigned. No manifest row was added or changed.

- 7262, OM System - OM-1 Mark II - 16bit (4:3).orf, SHA-256 d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd, 5220x3912, 20619192 payload bytes.
- 7263, OM System - OM-1 Mark II - 16bit (4:3).orf, SHA-256 780fa6a22ecd272cf3e86c04114439953b95fbc1bba8a05b4c99595a22e36bba, 8180x6132, 45088889 payload bytes.
- 7265, OM System - OM-1 Mark II - 16bit (4:3).orf, SHA-256 c7bd43b29ed89542058534b867fa894b8550d1960503cf4b4cb9f5912fd242b3, 10400x7792, 70703372 payload bytes.
- 7796, OM System - OM-3 - 16bit (4:3).ORF, SHA-256 1cee7deb661e45101ab3ca6c4240d24ed949b167ed423703fca15c09dd8ec176, 5220x3912, 19818873 payload bytes.
- 7797, OM System - OM-3 - 16bit (4:3).ORF, SHA-256 318e35647d93b2c598c0fec1d0d075336d2e2f5e6930faee05f32182c9a8ac5f, 8180x6132, 43844274 payload bytes.
- 7799, OM System - OM-3 - 16bit (4:3).ORF, SHA-256 9da7407d27007320c5bcf4e4d0b8c5c7bb533669cf4fabdf4e6a4b567cf318cc, 10400x7792, 68474774 payload bytes.

## Results

All six fixed-prefix printed real/null pairs match the historical lead values, as consistency checks only. Five whole scans match the complete bounded candidate counts/endpoints/escapes; the sixth is rejected under the predeclared rule. Accepted comparisons (real/null are the tool's printed estimates):

- 7262, 8.078 bpp: prefix 1.1987/1.1317, excess +5.92%; whole 1.1505/1.1278, excess +2.01%; change -3.91 percentage points. Lag1/2/3 prefix +0.1883/+0.1894/+0.1396, whole +0.1186/+0.1572/+0.0918.
- 7263, 7.191 bpp: prefix 1.1214/1.0051, excess +11.57%; whole 1.0846/1.0095, excess +7.44%; change -4.13 percentage points. Lag1/2/3 prefix +0.2576/+0.2182/+0.2116, whole +0.2101/+0.1811/+0.1687.
- 7265, 6.980 bpp: prefix 1.0939/0.9785, excess +11.79%; whole 1.0678/0.9841, excess +8.51%; change -3.29 percentage points. Lag1/2/3 prefix +0.2518/+0.2197/+0.2165, whole +0.2189/+0.1835/+0.1883.
- 7797, 6.993 bpp: prefix 1.0361/0.9947, excess +4.16%; whole 1.0566/0.9919, excess +6.52%; change +2.36 percentage points. Lag1/2/3 prefix +0.0879/+0.0687/+0.0786, whole +0.1348/+0.1129/+0.1314.
- 7799, 6.760 bpp: prefix 1.0161/0.9661, excess +5.18%; whole 1.0353/0.9615, excess +7.68%; change +2.50 percentage points. Lag1/2/3 prefix +0.0641/+0.0600/+0.0894, whole +0.1259/+0.1188/+0.1499.

For 7796, the strip budget is 158550984 bits. The unchanged scanner reports 23008929 candidates and consumed bit 158550986, two bits past EOF. Bounded counting yields 23008928 complete candidates ending at bit 158550978, leaving six censored bits. Its whole output is preserved only as rejected diagnostics; none of its ratios/correlations is used in a scope or cross-body comparison, and no corrected whole metric is substituted. The full six-file whole-scope comparison is incomplete until a separately declared rerun after the separately reviewed scanner fix.

Among the three accepted OM-1 Mark II files, excess remains inverse to bpp in both scopes but is lower in the whole scope. The two accepted OM-3 changes are listed separately; the rejected normal-size input prevents a three-file whole comparison. The largest accepted absolute scope change is 4.13 percentage points on 7263. These statements describe only these selected files; geometry and scene are confounded, and the rejected OM-3 normal-size input prevents completing that body's three-file comparison. In particular, 7263 is 7.191 bpp (above 7); no at-or-below-7 bpp range inference uses it. Printed correlations and all additional aggregates remain available without significance or codec semantics.

Accepted whole complete-candidate counts in order 7262/7263/7265/7797/7799 are 23492997/54403675/86528972/52998388/83900294; residual lengths 3/5/4/3/5. All count/escape/endpoint comparisons are exact. Residuals are censored rather than interpreted as padding.

The [complete aggregate JSON](lead106-original-cohort-prefix-versus-whole.json) retains all twelve normalized CLI reports, exact public identities/source hashes, measured signatures, independently bounded scope counts/endpoints/escapes and acceptance flags. Rejected outputs remain diagnostic only. Other retained MI, suffix and nominal-row proxy statistics are not independently validated or interpreted by this scoped report.

## Reproduce and limits

Read the complete pinned tool and its import before execution; match each local input to its retained CC0 hash record. Unchanged verified content needs no catalogue refresh; new or changed content needs its first licence verification. Run both commands on each of FILE7262, FILE7263, FILE7265, FILE7796, FILE7797 and FILE7799:

```text
python -I -B tools/test_orf_tokens.py
python -I -B tools/orf_tokens.py FILE7262 --max-tokens 1500000
python -I -B tools/orf_tokens.py FILE7262 --all
```

Substitute the other named files in turn, retain the full output and inspect consumed bits against `8*payload_bytes`. The whole-payload label alone is insufficient for this scanner. Complete runs may take minutes because they compute all existing MI tables.

The following one-off count consumes the output of the existing bounded `scan_tokens` generator. Save it locally as `count_existing.py` after reviewing the complete pinned [token_tail_distribution_probe.py](https://github.com/radialmonster/orf-cleanroom/blob/b5cb9c2952e4396649c369a05d2502c97ff6e711/tools/token_tail_distribution_probe.py) and its imported `orf_signature.py`; run `python -I -B count_existing.py FILE7262 FILE7263 FILE7265 FILE7796 FILE7797 FILE7799` from the repository root. It only reads samples and prints aggregate JSON. Compare its hashes and budgets with the report; it regenerates the independent bounded endpoint/count numbers, including the rejected scanner case. The original separate regex implementation was an additional local audit only, not the sole public method.

```python
"""One-off count over existing bounded generator output; read samples, print aggregates."""
import hashlib
import json
import sys
sys.path.insert(0, "tools")
from orf_tokens import locate
from token_tail_distribution_probe import scan_tokens

for path in sys.argv[1:]:
    with open(path, "rb") as source:
        digest = hashlib.sha256(source.read()).hexdigest()
    width, height, payload = locate(path)
    count = escapes = end = 0
    prefix = None
    for q, suffix, end in scan_tokens(payload, 1 << 62):
        count += 1
        escapes += q >= 17
        if count == 1500000:
            prefix = dict(tokens=count, escapes=escapes, consumed_bits=end)
    residual = len(payload)*8 - end
    all_ones = residual > 0 and all((payload[k >> 3] >> (7-(k & 7))) & 1
                                  for k in range(end, len(payload)*8))
    print(json.dumps(dict(sha256=digest, payload_w=width, payload_h=height,
                         payload_bytes=len(payload), prefix=prefix,
                         whole=dict(tokens=count, escapes=escapes, consumed_bits=end,
                                    residual_bits=residual, residual_all_ones=all_ones))), flush=True)
```

The following one-off reduction reads only the committed aggregates and prints accepted comparisons and rejected budgets. It writes no files. Run with python -I -B after source review:

```python
import json

with open("stats/lead106-original-cohort-prefix-versus-whole.json", encoding="utf-8") as source:
    report = json.load(source)
for sample in report["samples"]:
    prefix, whole = sample["prefix"], sample["whole"]
    budget = 8 * whole["payload_bytes"] - whole["consumed_bits"]
    if not whole["accepted_for_scope_comparison"]:
        print(sample["pixls_id"], "rejected", budget)
        continue
    p = prefix["printed_real"] / prefix["printed_null"] - 1
    w = whole["printed_real"] / whole["printed_null"] - 1
    print(sample["pixls_id"], 100*p, 100*w, 100*(w-p), budget)
```

All new numbers use the six named public CC0 inputs; no private historical figures were reproduced. Prefix values are consistency checks, not a new independent verification. No images/previews or prohibited decoder material were accessed. Both agents represent @radialmonster. No new tool, finding, manifest, immutable finding, spec, decoder or conformance change is proposed. The lead remains open for scene/ISO/frame-size/body-offset causality, independently established framing, significance and decoding. This report does not establish stationarity, a physical row/one-token-per-pixel correspondence, sensor values or the meaning of escaped syntax.

## Validation

Five existing parser synthetic tests and CLI help passed before measurements. Complete executed source and imported repository modules were read first. All selected local file hashes matched retained verified CC0 provenance and exact existing manifest identity. The public one-off count over the existing bounded generator matches all six original regex endpoint checks exactly, including prefix/full counts, endpoints, escapes and censored residual/all-ones flags. The original bounded CPU string parser preserves chunk-boundary carry and checks complete candidates independently of the scanner. It outputs aggregates only. RTX3090 was freely available; CPU was sufficient. Supervisor audit and rerun details are recorded in the PR/results comment after review.
