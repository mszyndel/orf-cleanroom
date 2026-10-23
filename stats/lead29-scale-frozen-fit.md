# Frozen-fit binary-q scale-context transfer from public id 1993

Author: @radialmonster
Date: 2026-10-21 UTC
Part of #29 item 7. Builds on #11, #173, #177 and the distinct item-4 frozen-fit design #254.

Design fixed before measurement in [Taking this](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6327627640). Freeze only id 1993 even-original-block training tables, evaluate odd-original-block tables of 1995/1997/1998 (same body) and 6343/5283 (other bodies), plus 1993 self reference. Earlier scale studies refit each file; this experiment tests transfer without target-file refitting. Every model is retained. No historical private estimator or finding is reproduced.

Method: unchanged [tools/token_scale_probe.py at 55f399d](https://github.com/radialmonster/orf-cleanroom/blob/55f399d3d2afe2b1958e7a19d3ca369625419dcd/tools/token_scale_probe.py) and its imports, at checkout b0c1c6048c8171e473fe7e29107c389483be7929. First 262144 complete candidate unary-zero/stop-one/five-suffix tokens from payload bit zero; zero extra escape bits; whole q>=17-containing 128-token blocks and incomplete tail omitted. Original even blocks train, odd blocks test, common targets t>=16 within each block. All six models predict binary q>0: frequency, lag1, count8, count16, lag1_count8, lag1_count16. Counts cover strictly preceding 8/16 tokens, including lag1. Joint context=previous_bit*(window+1)+count. Jeffreys half-count P(y|c)=(n(c,y)+0.5)/(n(c)+1); unseen contexts predict 0.5. Frozen losses use only reference 1993 training counts against each target's test counts. Target-local refit loss is a descriptive calibration comparator, not ground truth or a guaranteed lower bound. All frozen-minus-refit differences remain signed.

Primary criterion: BOTH lag1_count8 and lag1_count16 frozen gains against frozen lag1 >0. Gains against frozen frequency are also retained. This relative criterion can pass when the frozen reference baseline is badly calibrated. The previously examined availability-selected files are not blind held-out research inputs or scene-controlled replicates; a between-body contrast cannot isolate causal body, scene, mode or processing effects. Blocks are not established camera rows; adjacent splits can depend; selective omission cannot repair unknown framing/escape syntax. No significance, codec scale law, historical private-value reproduction, physical row/CFA, independent human verification or decoder follows.

All six local SHA256 values matched the retained verified CC0 inventory and exact existing manifest ID/name/hash/licence rows before measurement. No catalogue refresh/download; existing manifest rows and attribution unchanged. Full public identities/hashes, source hashes, exact observed count tables, original permutations/refit scores, geometry, endpoints and omissions are in `lead29-scale-frozen-fit-source.json`. Original permutations refit within each file and are NOT cross-file nulls or used for this criterion. All 36 derived model scores, unseen counts and calibration comparisons are in `lead29-scale-frozen-fit-results.json`. Only aggregate tables/scores are committed; no token/pixel arrays.

All six requested prefixes complete: 262144 tokens, zero shortfall/errors, 2048 complete blocks, no tail. Every file has compression tag 1 and measured variable-size signature, variant unassigned; models do not assign variants. Reference training targets 114576 per model. Test targets 114688 for 1993/1995/1997/1998, 112896 for 6343, 100464 for 5283. Retained even/odd blocks 1023/1024 for each of the first four, 1006/1008 for 6343, 890/897 for 5283; omitted 1/0,18/16,134/127 respectively.

Frozen joint count8/count16 gains against frozen lag1, bits/test target:

- 1993 self reference: +0.027165493292/+0.021345841411.
- 1995: +0.026134040385/+0.020262101532.
- 1997: +0.026501789065/+0.020695014692.
- 1998: +0.025372214461/+0.020639206710.
- 6343: +0.250135248909/+0.196553622933.
- 5283: +0.391460750982/+0.353878129996.

The declared criterion passes all five transfer files, including both other-body files. That does not imply useful absolute prediction: 6343 joint losses 1.101980945649/1.155562571625 and 5283 losses 1.404706741271/1.442289362257 exceed even one bit per target. A constant 0.5 predictor scores exactly 1 bit for any binary target sequence; this is an arithmetic comparator, not an additional fitted model. Frozen lag1 is still worse, 1.352116194558/1.796167492253, explaining why large relative gains coexist with poor losses. Relative to target-local refit, joint losses are higher by 0.247377120328/0.301107711693 for 6343 and 0.420841504908/0.460200931652 for 5283. Reference-unseen test targets for joint8/16 are 234/7701 and 326/13391. All four E-M1MarkII files have zero reference-unseen targets; their transferred scores remain close to local refits (all signed differences retained). The self reference equals its local refit as an arithmetic check, not independent verification. Thus the relative-gain criterion alone fails to diagnose this transfer calibration loss; no body causality or general transfer law is established.

After full source/import review and local hash match to retained verified CC0 records (new content needs its first licence verification), run:

```text
python -I -B tools/test_token_scale_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_scale_probe.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 1995 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1995 --sample 1997 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1997 --sample 1998 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1998 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283
```

Save the existing tool stdout JSON locally, then run this one-off original stdlib table reduction as `python -I -B SCRATCH_REDUCER.py SOURCE_OUTPUT.json`. It reads aggregate output and prints aggregates; no sample access, new parser or reusable measurement tool.

```python
"""One-off reduction of the exact public scale count tables; no sample access."""
import json
import math
import sys


def loss(train, test):
    n = sum(map(sum, test))
    assert sum(map(sum, train)) and n and len(train) == len(test)
    terms = [count * (math.log2(sum(a) + 1) - math.log2(a[y] + .5))
             for a, b in zip(train, test) for y, count in enumerate(b)]
    return math.fsum(terms) / n


# Hand arithmetic, unused contexts and negative transfer controls.
assert math.isclose(loss([[4, 0]], [[0, 4]]), math.log2(10), abs_tol=1e-14)
assert loss([[0, 0], [3, 1]], [[4, 0], [0, 0]]) == 1
assert loss([[8, 0], [0, 8]], [[0, 4], [4, 0]]) > loss([[4, 4]], [[4, 4]])

with open(sys.argv[1], encoding="utf-8-sig") as handle:
    source = json.load(handle)
assert not source["errors"] and len(source["samples"]) == 6
reference = next(s for s in source["samples"] if s["pixls_id"] == "1993")
frozen = reference["statistics"]["observed"]
results = []
for sample in source["samples"]:
    assert sample["prefix_complete"] and sample["shortfall_tokens"] == 0
    rows = []
    for ref, target in zip(frozen, sample["statistics"]["observed"]):
        assert ref["model"] == target["model"]
        train = ref["train_context_by_target"]
        test = target["test_context_by_target"]
        refit = loss(target["train_context_by_target"], test)
        assert math.isclose(refit, target["loss_bits"], abs_tol=1e-12)
        rows.append({"model": ref["model"], "test_targets": sum(map(sum, test)),
                     "reference_train_targets": sum(map(sum, train)),
                     "reference_unseen_test_targets": sum(sum(b) for a, b in zip(train, test) if not sum(a)),
                     "frozen_loss_bits": loss(train, test),
                     "target_refit_loss_bits": refit,
                     "frozen_minus_target_refit_loss_bits": loss(train, test) - refit})
    for row in rows:
        row["frozen_gain_vs_frequency_bits"] = rows[0]["frozen_loss_bits"] - row["frozen_loss_bits"]
        row["frozen_gain_vs_lag1_bits"] = rows[1]["frozen_loss_bits"] - row["frozen_loss_bits"]
    if sample["pixls_id"] == "1993":
        assert all(math.isclose(row["frozen_minus_target_refit_loss_bits"], 0, abs_tol=1e-12) for row in rows)
    results.append({"pixls_id": sample["pixls_id"], "pixls_name": sample["pixls_name"],
                    "sha256": sample["sha256"],
                    "both_joint_frozen_gains_vs_lag1_positive": all(row["frozen_gain_vs_lag1_bits"] > 0 for row in rows[-2:]),
                    "models": rows})
print(json.dumps({"reference_fit_id": "1993", "samples": results}, indent=2, allow_nan=False))

```

Supervisor audit: read the full runtime/import/test sources, actual three-file diff, execution ledger, scratch artifacts and public reproduction code. Fresh local CC0 inventory/manifest hash checks passed. A complete six-file CLI rerun matched the source JSON exactly; the one-off reducer matched the derived JSON exactly. A separate CPU regex parser and string-context counter matched all 36 train/test model tables, consumed-bit endpoints and escape-block omissions; separate scoring checked every frozen/local loss, signed gain/difference and unseen-context count. The TIFF locator was reused, not independently reimplemented. Eleven scale tests, scanner self-test, three reducer arithmetic controls, CLI help, 37-finding validation, whitespace and public-text checks pass. Audit corrected prose spacing and replaced pending-audit placeholders; no numerical or runtime source correction. RTX 3090 was freely available; CPU sufficed. Both agents represent @radialmonster, not independent human verifiers. No images/previews, forbidden decoder material, private inputs, raw/token/pixel dumps or existing attribution edits.

Status
Holds/measured: all six complete reports; both-joint-relative-gains criterion passes all 5 transfer files; both selected other-body files nevertheless have joint losses>1 and materially worse than their target-local refits. Every model and signed difference retained.
Contradicts: no historical private claim is declared contradicted by this different estimator.
Not tested: historical full-q/running-mean figures/estimator/files, causal scale adaptation, physical rows/CFA, significance, stationarity, true framing/escape syntax, other numbered claims, generality or decoding.
Open: independently justified framing and separately specified controlled sampling/window validation and calibrated transfer criteria. All historical Next steps remain open. Exact rerun: pinned unchanged tool, complete six-file command and one-off reducer above. Every numerical input is public CC0, none private. No finding/spec/decoder change or issue closure. Review/merging stays with the separate hourly maintainer task.

I confirm this follows RULES.md and is released under CC0 1.0.
