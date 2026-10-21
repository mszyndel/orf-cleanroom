# Lead #31 suffix-match replication on three further CC0 files

Script: `tools/suffix_match_probe.py`, source commit `3f955e7ec962ba8a9888647a1b549af6bab340ce`. Public inputs (raw.pixls.us id, SHA-256): 1803 `ba4605bbd9fe9b77971da444bcdb1698904c0ad4ebdf9dd42dd45ab255f3f6d4`; 241 `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd`; 1051 `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda`.

Human contributor: @radialmonster. Builds on #31 and #11 and the public suffix-match method by @mtakemoto (PR #89). This is an additional descriptive replication cohort, selected from available lawful samples and fixed in issue comment 6307413396 before measuring. It is neither the original validation cohort nor independent human verification. No findings, decoder changes or variant assignments are proposed.

The unchanged tool at source commit `3f955e7ec962ba8a9888647a1b549af6bab340ce` ran on 2026-10-21 UTC, using the v1 metric and phase `replication`. Inputs, ordered: raw.pixls.us IDs 1803 (E-3), 241 (E-P3), 1051 (E-M1), all CC0 on a fresh `pixls_samples.py check`. Public names and full hashes are in the cohort. All already have manifest rows; none were edited. These files are outside the earlier six-file suffix-match cohort; their broader research history is not claimed to be unseen.

Every requested input succeeded: 262144 tokens each, 30 total lag rows, no substitution, tuning, pooling or omitted lag. Exact counts, rational means/rates/differences/ratios, parser settings, signatures, source hashes and run time are preserved in `lead31-suffix-matches-helper002-replication.json`.

Lag-1 observed/conditional-mean ratios, in cohort order: 1.085478, 1.090907, 1.077531. Lag-2: 0.956282, 1.000670, 1.000833. Lag 2 is below the mean in one of three files, whereas mtakemoto's #89/#31 experiment found five of six. Thus a universal lag-2 deficit does not extend to these prefixes. The six W/2W-related lag labels across three files (18 ratios) span 0.981189 to 1.025052. These are descriptive comparisons without significance thresholds or independent-pair assumptions.

The historical private figures and shuffle definition cannot be reproduced from #31. Single-symbol equality cannot establish or exclude dictionary coding. W-token blocks and lags are candidate coordinates, not known physical rows. Parsing after escapes is tentative; the null retains escape masks and block suffix multisets but does not preserve q/s coupling or slow within-block drift. Nothing here tests the predictor/transform families or reconstructs an image.

Reproduce with `tools/suffix_match_probe.py` from the exact source commit above and the cohort JSON in this change (SHA-256 `edba4a1b4b202fe963f253bcb6dec55af559e4a3d8cd8543fa822a1c6d333881`), passing explicit local paths for the three checked CC0 files:

```powershell
python -I -B tools/suffix_match_probe.py --cohort tools/cohorts/lead31-suffix-matches-v1-helper002-replication.json --measured-by radialmonster --sample 1803 'SAMPLES/1803_Olympus - E-3 - 16bit (4_3).ORF' --sample 241 'SAMPLES/241_Olympus - E-P3 - 16bit (4_3).ORF' --sample 1051 'SAMPLES/1051_Olympus - E-M1 - 16bit (4_3).orf'
```

Replace SAMPLES with local paths; the checked data need not share one directory. Do not download inside the repository. The output contains aggregate statistics and public identities only. No result depends on private files.

Verification: 19 existing synthetic tests pass, including exhaustive exact-permutation enumeration; the subprocess-based malformed-CLI test was excluded because its child command omits -B, and both malformed real CLI cases were instead run directly with -I -B (exit 2 and identical sanitized JSON). An original bit-by-bit CPU parser independently agreed with the reviewed fast parser for the first 4096 tokens of each input: consumed bits 26530, 26938, 27920. This checks implementation agreement for small prefixes, not the token model's semantic correctness. No GPU was needed.

Publication route: proposed aggregate cohort/stats PR requires maintainer review, Part of #31. No finding file is added because the private numerical result cannot be reproduced and the broader negative is not established. After audit/publication, report the bounded extension with a Status block and release #31. This document records an unverified measurement, not a verified finding.
