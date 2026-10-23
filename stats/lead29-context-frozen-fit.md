# Frozen-fit suffix-context transfer from public E-M1MarkII id 1993

Author: @radialmonster
Date: 2026-10-21 UTC
Part of #29 item 4. Builds on #11, #169 and #181.

The claim/design was frozen before this run in [the Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6324386043). This is a new descriptive cross-file fit experiment, with every model retained. Earlier #169/#181 reports refit on each file; this run freezes the 1993 training tables and scores different files without refitting. No historical private figures or finding are reproduced.

Method: unchanged [tools/token_context_probe.py at 3e306f1](https://github.com/radialmonster/orf-cleanroom/blob/3e306f1e358c83e59aaaf49f56f7efad7f5f218b/tools/token_context_probe.py) and its imports. First 262144 complete candidate q-zero/one/five-suffix tokens from payload bit zero, zero extra escape skip; omit entire q>=17-containing 128-token blocks and incomplete tail. Original even blocks supply training tables; original odd blocks supply test tables, t>=5 within each block, with no cross-block context. All six fixed b2/b4 models are unchanged. Jeffreys half-count smoothing: P(y|context)=(n_y+0.5)/(n_0+n_1+1). Frozen scores use ONLY the 1993 even-block training tables against each target's odd-block test tables, including 1993 as self reference. The target-file within-file-refit score is a descriptive comparator, not a lower bound or ground truth. The primary criterion is both b2_two and b4_one frozen-fit gains over the frozen same-target empty model strictly positive. No outcome-selected thresholds or model winner.

The cohort is availability-selected and previously used for other measurements: 1993 as known reference; additional same-body 1995/1997/1998, and deliberately contrasting other-body 6343/5283. Files are not blind or controlled scene replicates. A between-body difference cannot isolate body, scene, processing or mode. Token blocks are not established camera rows; selective escape omission cannot repair unknown framing. Adjacent train/test dependence, marginal differences and model misspecification remain. Frozen gains are relative to a frozen marginal model, so a positive gain does not establish good absolute prediction. No calibrated significance/null distribution, general codec law, physical row/CFA, historical private estimator, independent human verification, decoder or finding follows.

All six local SHA-256 values matched the retained verified CC0 inventory and exact public manifest ID/name/hash entries before measurement. No catalogue refresh or new file download. Their existing manifest rows and attribution are unchanged. Full public identities/hashes, every exact source train/test table, source hashes, all original permutation comparisons, geometry, omissions and endpoints are retained in `lead29-context-frozen-fit-source.json`. The separate `lead29-context-frozen-fit-results.json` contains all 36 derived frozen scores/gains, reference-unseen counts and refit differences. The original permutation scores refit within each file; they are not controls for this cross-file experiment and are not used for its criterion.

All six reports return 262144 requested tokens with zero shortfall/failures. Retained even/odd blocks: 1993/1995/1997/1998 each 1023/1024, 6343 1006/1008, 5283 890/897; omissions respectively 1/0,18/16,134/127. All complete block counts are 2048, no tail; test targets per model are 125952 for each E-M1MarkII file, 123984 for 6343 and 110331 for 5283. The reference training targets are 125829 per model. No test target has an unseen reference context in any of the 36 scores.

Primary frozen-fit gains (b2_two / b4_one, bits per test target), in fixed cohort order:

- 1993 self reference: +0.079385841315 / +0.008371537060.
- 1995: +0.080668650631 / +0.008897151372.
- 1997: +0.078360089924 / +0.009357895359.
- 1998: +0.077468349554 / +0.008082763606.
- 6343: -0.081939027704 / -0.022688250083.
- 5283: -0.115127001098 / -0.031562512568.

Thus the declared criterion holds on all three additional same-body files and fails on both selected other-body files. The self reference agrees exactly with the original within-file score as expected from identical tables; this is an arithmetic check, not fresh independent verification. On 6343/5283 the frozen b2_two losses are 1.097675158691/1.174517449851, respectively 0.120769736246/0.179158589603 bits above their own refit scores. Every loss, nested gain, frozen-empty gain and signed refit difference remains in JSON, including negative differences. These selected comparisons do not establish a causal body effect or a universal transfer law.

After reading the complete pinned source/imports, match the six local hashes to retained verified CC0 records (previously unverified content needs its first licence check), then run:

```text
python -I -B tools/test_token_context_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_context_probe.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 1995 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1995 --sample 1997 "Olympus - E-M1MarkII - 16bit (4:3).ORI" FILE1997 --sample 1998 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1998 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283
```

For the one-off reduction over that existing aggregate output, save its stdout JSON locally and run the following original stdlib code as `python -I -B SCRATCH_REDUCER.py SOURCE_OUTPUT.json`. It only reads the aggregate input and prints derived aggregate numbers. This reducer is included inline because it is a one-off count-table reduction, not a new reusable sample measurement tool.

```python
import json
import math
import sys

with open(sys.argv[1], encoding="utf-8-sig") as handle:
    report = json.load(handle)
assert not report["failures"]
samples = report["samples"]
assert [s["pixls_id"] for s in samples] == ["1993", "1995", "1997", "1998", "6343", "5283"]
assert all(s["prefix_shortfall"] == 0 for s in samples)
reference = samples[0]["models"]

def loss(train, test):
    n = sum(map(sum, test))
    assert sum(map(sum, train)) > 0 and n > 0
    return math.fsum(-held[y] * math.log2((fit[y] + 0.5) / (sum(fit) + 1))
                     for fit, held in zip(train, test) for y in (0, 1)) / n

# One-off arithmetic controls: balanced, unseen and reversed fit.
assert loss([[1, 1]], [[3, 7]]) == 1
assert loss([[0, 0], [8, 0]], [[3, 7], [0, 0]]) == 1
assert loss([[99, 0]], [[0, 10]]) > 7
rows = []
for sample in samples:
    models, empty, previous = [], {}, {}
    for fitted, target in zip(reference, sample["models"]):
        assert fitted["name"] == target["name"]
        train = fitted["training_counts_context_by_outcome"]
        test = target["test_counts_context_by_outcome"]
        assert len(train) == len(test)
        score = loss(train, test)
        bit = target["target_bit"]
        if not fitted["context_taps_first_is_msb"]:
            empty[bit] = score
        models.append(dict(name=target["name"], frozen_fit_loss_bits=score,
            gain_vs_frozen_empty_bits=empty[bit] - score,
            gain_vs_previous_frozen_bits=(previous[bit] - score if bit in previous else None),
            within_file_refit_loss_bits=target["heldout_log_loss_bits"],
            frozen_minus_refit_loss_bits=score - target["heldout_log_loss_bits"],
            reference_training_targets=sum(map(sum, train)), test_targets=sum(map(sum, test)),
            test_targets_in_unseen_reference_contexts=sum(sum(held) for fit, held in zip(train, test) if sum(fit) == 0)))
        previous[bit] = score
    by_name = {row["name"]: row for row in models}
    rows.append(dict(pixls_id=sample["pixls_id"], models=models,
        primary_both_frozen_gains_positive=all(by_name[n]["gain_vs_frozen_empty_bits"] > 0
                                             for n in ("b2_two", "b4_one"))))
print(json.dumps(dict(reference_training_pixls_id="1993", reference_split="even-original-blocks",
    target_split="odd-original-blocks", results=rows), indent=2, allow_nan=False))
```

Validation: six existing context tests, scanner self-test and CLI help pass. Three one-off reducer arithmetic controls cover balanced, unseen and reversed-fit outcomes. Supervisor numerical audit passes: a fresh full six-file CLI report equals the source JSON exactly; an original CPU TIFF reader/string parser confirms all 72 exact observed train/test tables, geometry, endpoints, escapes and omissions. Alternate doubled-integer logarithm-difference arithmetic confirms all 36 frozen/refit losses, gains, unseen counts, targets and criteria within 1e-12. Supervisor reviewed the full runtime/import sources, actual diff, scratch artifacts and public drafts. The fresh reviewed reducer output also equals the derived JSON byte-for-byte. No source or numerical correction was needed. CPU only; RTX3090 was available and unnecessary. No images/previews, forbidden decoder material, private inputs or token/pixel dumps used. Both agents represent @radialmonster, not independent human verifiers.

Status
Holds/measured: all six reports complete; the declared frozen-fit criterion holds on the three additional E-M1MarkII files and fails on both selected other-body inputs, with every model retained.
Contradicts: no historical-private claim is declared contradicted by this different estimator.
Not tested: original historical gains/files/estimator, physical rows, parity-invariance, GF(2) laws, significance, true framing/escape semantics, causal body/scene effect, generality, other numbered claims or decoding.
Open: independently justified framing and separately specified controlled sampling/window tests; no historical Next step is closed. Exact rerun: pinned original tool, complete six-file command and one-off reducer above. Every file measurement uses the six public CC0 inputs; none private. No finding/spec/decoder change or lead closure. Candidate PR review/merging belongs to the separate hourly maintainer task.

I confirm this follows RULES.md and is released under CC0 1.0.
