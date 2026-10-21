# Remaining OM-1 family files extend the null-distance bpp/body relation

Author: @radialmonster
Verified by: @radialmonster
Lead: #106
Variant: unassigned
Builds on: 2026-10-21--radialmonster--null-distance-tracks-bpp-within-body
Partial: the per-file k=5 tokens-per-pixel excess and its bpp/body relation on the ten remaining public OM-1 Mark II and OM-3 files, plus their constant recorded Exif sensitivity; not the lead's at-or-below-7 bpp range, scene or ISO causality, a significance test, physical rows, a decode, or independent human verification.

## Claim

The lead's per-file variation in distance from the Bernoulli null extends to the ten remaining public OM-1 Mark II and OM-3 files in the id ranges named in its Next steps. On these files the k=5 prefix estimate of tokens per pixel is at or above the Bernoulli null for nine of ten (eight above, one at 0.00%), and the size of the excess is ordered mainly by bits per pixel within a body, with a body offset at overlapping bits per pixel.

- OM-1 Mark II: excess `real/null - 1` is +4.59% (7266, 8.145 bpp), +4.36% (7268, 8.136), +4.39% (7270, 8.114), +2.25% (7267, 8.450) and +1.01% (7269, 8.794). The three 5220x3912 files differ by only 0.23 percentage points, so this is a broad decline with bpp, not strict monotonicity at that precision. Unlike the OM-3 files below, these high-bpp OM-1 Mark II files remain clearly above the null.
- OM-3: +0.18% (7800, 7.849 bpp), +0.14% (7802, 7.851), +0.00% (7804, 7.916), +0.47% (7801, 8.208) and -0.33% (7803, 8.446). This is a near-zero plateau across 7.85 to 8.45 bpp, not a strict monotone decline.

At overlapping bits per pixel the body offset is visible: around 8.11 to 8.45 bpp the OM-1 Mark II files are +1.01% to +4.59% while the OM-3 files are -0.33% to +0.47%. This verifies the lead's per-file variation but not its "not the body" wording; it agrees with the earlier Partial finding that bits per pixel orders files within a body while the body sets the offset.

All ten files record Exif `PhotographicSensitivity` (0x8827) as `[200]`, with no 65535 sentinel and no missing value. The recorded sensitivity is therefore constant in this cohort and cannot explain the variation; this does not test a response to changing ISO.

The printed `min(q,8)` correlations are positive on all ten files: lag 1 +0.0275 to +0.1654, lag 2 +0.0060 to +0.1832, lag 3 +0.0064 to +0.1499. These are descriptive prefix correlations, not a significance test or a statement about physical rows.

Limits: the lead's claim about files at about 7 bpp or below is not tested here, because every added file is above 7.8 bpp. The `orf_tokens.py` value is a prefix estimate from bits per token, not a whole-payload token count. The ten files have known prior metadata measurements and were named in the lead; they are not a blind or random cohort. No scene, exposure, frame-mode or causal property is isolated. This is self-verification by the same human account as the finder, not independent human verification.

## Original evidence

Lead #106, opened by @radialmonster on 2026-10-20, used `python -I tools/orf_tokens.py "<file>" --max-tokens 1500000` on ids 7262, 7263, 7265, 7796, 7797 and 7799 and reported the real/null token-pixel estimates and lag 1/lag 2 correlations. The earlier Partial finding `2026-10-21--radialmonster--null-distance-tracks-bpp-within-body` extended that table to 13 files, including new OM-1 ids 5283-5287, OM-1 Mark II id 7264 and OM-3 id 7798, and found that bits per pixel orders files within a body while the body sets the offset.

Tools used here are the merged repository tools at upstream main: `tools/orf_tokens.py` at commit `a3fdd6ff8595a697af5cfbee6ff1558253d0c68b` and `tools/exif_sensitivity_probe.py` at commit `2c55487c9d9d2c5ea715e60f630786566643b8a6`. Both are standard-library Python; neither decodes pixels or writes files.

The ten added files are public CC0 raw.pixls.us samples. Each local SHA-256 matched the retained verified-CC0 inventory and an existing `samples/manifest.csv` row before measurement; no download or online catalogue request was repeated.

## Verification

A new run on 2026-10-21 UTC, after lead #106 was posted, used the lead's exact command on the ten remaining files in the id ranges named in its Next steps. None of the ten was in the lead's six-file token table or in the earlier finding's 13-file token table. The same ten files were also read with the merged Exif sensitivity tool.

Every local SHA-256 matched the retained verified-CC0 record and existing manifest identity: 7266 `1c994e4bf5aa4e48d6ec97a1f83558184a866f71bca2b5b1bf914a159927e199`; 7267 `5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756`; 7268 `a5ee1e874d7aa357192173e12695627f90a8800a272b6c6e4959f029afb59837`; 7269 `dd2a6c1c4ca4d86201207925477e2ea8e50ebd53d7df9117847093f5023540ec`; 7270 `e4f3583f0bfb1efb0f40b201c5bb0cb1c30ace875a7f96d93fa7dddcc6966f5f`; 7800 `5640fb1a2ceff83d3678f46a7acdabd9ec393d318718c9c48a9c650afe7a7c58`; 7801 `8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82`; 7802 `2f8c0363376fe1c4f669f1c6c881611e8a71e39320bbac3c691405583b671cf2`; 7803 `63a5b4da41fdbe8b31213ca7a11408dfd0453d893f17ac09a73471580ffbd8f0`; 7804 `bcc05bd57e78cbbb308a596f97987975f7167b17768d8c2d536c87e0c34298e0`.

| id | public name | body | payload | bpp | real | null | excess | lag 1 | lag 2 | lag 3 | Exif 0x8827 |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 7266 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1 Mark II | 5220x3912 | 8.145 | 1.1910 | 1.1387 | +4.59% | +0.1654 | +0.1815 | +0.1235 | [200] |
| 7267 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1 Mark II | 10386x7792 | 8.450 | 1.2213 | 1.1944 | +2.25% | +0.0874 | +0.1188 | +0.0880 | [200] |
| 7268 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1 Mark II | 5220x3912 | 8.136 | 1.1864 | 1.1368 | +4.36% | +0.1618 | +0.1823 | +0.1192 | [200] |
| 7269 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1 Mark II | 8172x6132 | 8.794 | 1.2472 | 1.2347 | +1.01% | +0.0787 | +0.1499 | +0.0760 | [200] |
| 7270 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1 Mark II | 5220x3912 | 8.114 | 1.1839 | 1.1341 | +4.39% | +0.1627 | +0.1832 | +0.1209 | [200] |
| 7800 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | 5220x3912 | 7.849 | 1.1082 | 1.1062 | +0.18% | +0.0343 | +0.0073 | +0.0082 | [200] |
| 7801 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | 10386x7792 | 8.208 | 1.1682 | 1.1627 | +0.47% | +0.0275 | +0.0159 | +0.0182 | [200] |
| 7802 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | 5220x3912 | 7.851 | 1.1079 | 1.1064 | +0.14% | +0.0335 | +0.0078 | +0.0078 | [200] |
| 7803 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | 8172x6132 | 8.446 | 1.1824 | 1.1863 | -0.33% | +0.0346 | +0.0284 | +0.0170 | [200] |
| 7804 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | 5220x3912 | 7.916 | 1.1148 | 1.1148 | +0.00% | +0.0323 | +0.0060 | +0.0064 | [200] |

Against the lead:

- The per-file variation holds, with a positive excess above the null for eight of ten files; 7804 is 0.00% and 7803 is -0.33%, both inside the same near-zero plateau as the other OM-3 high-bpp files.
- The lead's "files at about 7 bpp or below are 4 to 12% above the null" is not tested by these files (all are above 7.8 bpp).
- The lead's "not the body" is not supported at overlapping bpp: the OM-1 Mark II files remain +1.01% to +4.59% where the OM-3 files are -0.33% to +0.47%. This agrees with the earlier Partial finding's body-offset wording.
- The lag correlations are all positive, but they are not offered as a significance result.

Validation: the ten-file token output was rerun and was identical after removing the tool's timing-only fields (230 lines, no numerical difference); the printed bpp and excess values were recomputed by exact decimal arithmetic from the printed payload byte counts and dimensions, with all ten matching; `python -I -B tools/test_orf_tokens.py` passed its five synthetic tests. The same human account performed the lead, the earlier finding and this run, so this is a self-verification, not a second human verifier.

## Reproduce

Run from the repository root with the tools at the commits above. `FILE7266` etc. are the local paths to the public samples named in the table; substitute them and keep the file identities by SHA-256.

    python -I -B tools/test_orf_tokens.py
    python -I -B tools/orf_tokens.py FILE7266 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7267 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7268 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7269 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7270 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7800 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7801 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7802 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7803 --max-tokens 1500000
    python -I -B tools/orf_tokens.py FILE7804 --max-tokens 1500000

For each file, read the printed `payload`, `bpp`, `real`, `Bernoulli null` and `correlation of min(q,8)` lines. Excess is `real/null - 1`. For the sensitivity column, run the merged tool once per sample (it accepts a repeated `--sample ID "PUBLIC NAME" PATH`):

    python -I -B tools/exif_sensitivity_probe.py --sample 7266 "OM System - OM-1 Mark II - 16bit (4:3).ori" FILE7266

The tool prints JSON with the raw 0x8827 values and the measured signature. No command here writes files, downloads data, or views pixels.
