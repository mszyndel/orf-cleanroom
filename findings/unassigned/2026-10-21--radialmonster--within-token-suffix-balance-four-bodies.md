# Within-token suffix balance holds within a stated tolerance on four further bodies

Author: @radialmonster
Verified by: @radialmonster
Lead: #11
Variant: unassigned
Builds on: 2026-10-21--radialmonster--em1mk2-full-payload-suffix-dependence
Partial: within-token MI(H;L) and the b0/b1 marginals on four further public bodies, within the tolerance fixed before this run; not exact independence or exact fairness, the b2/b4 special role, physical rows, escape framing, geometry, values or decoding.

## Claim

Under the candidate q-zero, stop-1, five-bit-suffix parse, lead #11 states that within a token the groups `H = b4b3` and `L = b2b1b0` are statistically independent and that `b1` and `b0` behave as fair coins. The lead gives no numeric figure for this item.

This finding reports a predeclared bounded test of that qualitative claim on four CC0 compressed payloads that the merged suffix-dependence finding did not use (E-P3 id 241, OM-1 id 5283, OM-5 id 6343 and TG-7 id 6946). Measure and tolerance were fixed in the claim comment before the primary H/L outcome:

- first 262144 candidate tokens from payload bit zero, q-zero/stop-1/five-suffix parse with no extra escape skip; escapes retained in sequence and excluded from suffix statistics;
- pass if `MI(H;L) <= 0.010` bit and `|P(b1=1) - 0.5| <= 0.05` and `|P(b0=1) - 0.5| <= 0.05` on every file.

All four files pass that tolerance. `MI(H;L)` is 0.0008 to 0.0030 bit (rotated-pair baseline 0.0000 to 0.0001); `P(b1=1)` is 0.4688 to 0.4806 and `P(b0=1)` is 0.4698 to 0.4904. This supports the lead's qualitative statement within the stated tolerance on these four files. It does not establish exact independence or exact fair-coin marginals: the measured MI is small but nonzero, the b0/b1 deviations reach 0.031, and the other suffix bits are not near 0.5 (`P(b4=1)` 0.4127 to 0.4631).

## Original evidence

[Lead #11](https://github.com/radialmonster/orf-cleanroom/issues/11), by @radialmonster, reports the H/L split and the within-token independence/fairness statement from private research notes dated 2026-10-14..18. It supplies no numeric tolerance and no public script for this item. Its exact figures therefore cannot be reproduced; the measure above verifies the qualitative claim only.

The merged finding `2026-10-21--radialmonster--em1mk2-full-payload-suffix-dependence` measured `MI(H;L)` of 0.0005/0.0007 bit and the b0/b1 marginals on ids 1995/1997, and explicitly did not verify exact H/L independence. This finding uses different files and a stated tolerance; it does not repeat or re-verify that finding's numbers.

All four inputs are public CC0 raw.pixls.us files already listed in `samples/manifest.csv`; no new manifest row or download is needed.

| raw.pixls.us id | Exact public name | SHA-256 | measured payload | bpp |
| --- | --- | --- | --- | ---: |
| 241 | `Olympus - E-P3 - 16bit (4:3).ORF` | `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd` | 4080x3040, variable | 6.725 |
| 5283 | `OM System - OM-1 - 16bit (4:3).ORF` | `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b` | 5220x3912, variable | 7.836 |
| 6343 | `OM System - OM-5 - 16bit (4:3).ORF` | `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7` | 5240x3912, variable | 6.936 |
| 6946 | `OM System - TG-7 - 16bit (4:3).ORF` | `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a` | 4040x3016, variable | 8.076 |

The measured signature does not assign a variant; all four rows remain `unassigned` in the manifest, so the finding is filed under `unassigned`.

## Verification

A new run on 2026-10-21 UTC, after lead #11 was posted, on the four files above. None is in the prior suffix-dependence finding's 1995/1997 cohort. Each local SHA-256 was checked against the retained verified-CC0 inventory and the exact public manifest row before measurement; no catalogue request or download was made for the unchanged files.

From the repository root at commit `3e306f1e358c83e59aaaf49f56f7efad7f5f218b`:

    python -I -B tools/orf_tokens.py FILE241 FILE5283 FILE6343 FILE6946 --max-tokens 262144

The unchanged tool prints the candidate parse, escape counts, suffix-bit balance and within-token MI. Results (first 262144 candidate tokens each):

| id | escapes (q>=17) | MI(H;L) | baseline | P(b4=1) | P(b3=1) | P(b2=1) | P(b1=1) | P(b0=1) | tolerance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 241 | 3 | 0.0030 | 0.0001 | 0.4620 | 0.4939 | 0.4690 | 0.4709 | 0.4790 | pass |
| 5283 | 313 | 0.0008 | 0.0001 | 0.4592 | 0.4817 | 0.4658 | 0.4786 | 0.4785 | pass |
| 6343 | 34 | 0.0012 | 0.0001 | 0.4127 | 0.4644 | 0.4254 | 0.4806 | 0.4904 | pass |
| 6946 | 2235 | 0.0029 | 0.0000 | 0.4631 | 0.4695 | 0.4684 | 0.4688 | 0.4698 | pass |

The commit's Python is 3.13.15; the tool reports `tokens parsed: 262144 (prefix)` for each file.

A secondary block-level control used the merged `tools/suffix_joint_probe.py` (not the primary statistic, because it reports `MI(b2; b1b0)` rather than `MI(H;L)`). It completed on all four files and gave `MI(b2; b1b0)` of 0.000271, 0.000268, 0.000218 and 0.000140 bit for ids 241, 5283, 6343 and 6946, over 261760, 228736, 257792 and 137088 retained tokens respectively. TG-7 omits 977 of 2048 complete 128-token blocks because they contain q>=17 candidates, so that control is much weaker there and is not used to decide the claim.

The rotated-pair baseline is a single deterministic comparison, not a null distribution or a calibrated significance test. No equivalence margin beyond the predeclared pass tolerance, no exact-independence test and no camera-meaning inference is claimed.

## Reproduce

Check each input's CC0 status and hash, then run the primary measurement once per file (or pass all four paths in one call):

    python -I -B tools/pixls_samples.py check FILE241 FILE5283 FILE6343 FILE6946
    python -I -B tools/orf_tokens.py FILE241 --max-tokens 262144
    python -I -B tools/orf_tokens.py FILE5283 --max-tokens 262144
    python -I -B tools/orf_tokens.py FILE6343 --max-tokens 262144
    python -I -B tools/orf_tokens.py FILE6946 --max-tokens 262144

Read the printed `escapes (q>=17)`, `suffix bit balance P(bit=1)` and `within-token MI(H;L)` lines. For the secondary block-level control:

    python -I -B tools/suffix_joint_probe.py --self-test
    python -I -B tools/suffix_joint_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946

All outputs are aggregate text/JSON; no image, preview, raw payload or pixel value is read or written. All four inputs are public CC0 files, so every number here is publicly reproducible.
