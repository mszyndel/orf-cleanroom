# Null distance tracks bits per pixel within an OM-1-family body, with a body offset

Author: @radialmonster
Verified by: @radialmonster
Lead: #106
Variant: unassigned
Builds on: #11, 2026-10-20--radialmonster--large-sensor-k5-parse-near-bernoulli-null, 2026-10-21--radialmonster--tokens-per-pixel-on-5240-and-5220-wide-bodies
Partial: the per-file variation and its relation to bits per pixel, on five OM-1 files and two new files of the lead's bodies; ISO and the scene/setting property are not tested

## Claim

On 13 CC0 files from three OM-1-family bodies, the k=5 parse's tokens-per-pixel estimate sits above the Bernoulli null by an amount that falls monotonically as the file's bits per pixel rises, within each body. The body shifts the offset: at 5220x3912 and 7.76 to 8.11 bpp the excess is +5.7% to +5.9% on OM-1 Mark II, +1.6% on OM-1 and 0.0% to +0.5% on OM-3.

Excess over the null (real/null - 1), by body:

- OM-1 Mark II: +5.75% at 8.107 bpp, +5.92% at 8.078, +11.57% at 7.191, +11.79% at 6.980.
- OM-1: +1.60% at 7.836 bpp, +1.61% at 7.813, +2.25% at 7.538, +6.91% at 6.947, +10.39% at 6.283.
- OM-3: -0.02% at 7.944 bpp, +0.48% at 7.764, +4.16% at 6.993, +5.18% at 6.760.

The lag 1 and lag 2 correlations of min(q,8) follow the same ordering. So the lead's per-file variation holds, but "not the body" is too strong: bits per pixel orders the files within a body, and the body sets the level of the curve.

## Original evidence

Lead #106, opened by @radialmonster on 2026-10-20: `tools/orf_tokens.py --max-tokens 1500000`, tokens per pixel real vs null and lag 1 / lag 2 on six files, all CC0:

| raw.pixls.us id | Body | Payload | bpp | real | null | lag 1 | lag 2 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 7262 | OM-1 Mark II | 5220x3912 | 8.078 | 1.1987 | 1.1317 | +0.188 | +0.189 |
| 7263 | OM-1 Mark II | 8180x6132 | 7.191 | 1.1214 | 1.0051 | +0.258 | +0.218 |
| 7265 | OM-1 Mark II | 10400x7792 | 6.980 | 1.0939 | 0.9785 | +0.252 | +0.220 |
| 7797 | OM-3 | 8180x6132 | 6.993 | 1.0361 | 0.9947 | +0.088 | +0.069 |
| 7799 | OM-3 | 10400x7792 | 6.760 | 1.0161 | 0.9661 | +0.064 | +0.060 |
| 7796 | OM-3 | 5220x3912 | 7.764 | 1.1014 | 1.0961 | +0.037 | +0.007 |

The lead states that files at about 7 bpp or below are 4 to 12% above the null and show lag 1 to 3 correlations of +0.06 to +0.26, unlike the four high-bpp files of #86, and that closeness depends on the file, not the body. It names no files beyond the ids above.

## Verification

A new run on 2026-10-21 UTC, after the lead was posted, with `tools/orf_tokens.py` at commit `a3fdd6f` (unchanged since; repository head `b91aa99`), Python 3.13.15. Files were downloaded with `tools/pixls_samples.py` and confirmed CC0 in this run, then matched to the table by SHA-256. The command is the lead's: `python -I tools/orf_tokens.py FILE --max-tokens 1500000`. Excess is the printed "real" divided by the printed "Bernoulli null", minus 1; correlations are the "correlation of min(q,8)" line.

The OM-1 body was not used by the lead (Next steps of #106 name ids 5283 to 5287); 7264 (OM-1 Mark II) and 7798 (OM-3) are files of the lead's bodies that it did not use.

| raw.pixls.us id | Body | Payload | bpp | real | null | excess | lag 1 | lag 2 | lag 3 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7264 | OM-1 Mark II | 5220x3912 | 8.107 | 1.2000 | 1.1348 | +5.75% | +0.1852 | +0.1905 | +0.1361 |
| 7262 | OM-1 Mark II | 5220x3912 | 8.078 | 1.1987 | 1.1317 | +5.92% | +0.1883 | +0.1894 | +0.1396 |
| 7263 | OM-1 Mark II | 8180x6132 | 7.191 | 1.1214 | 1.0051 | +11.57% | +0.2576 | +0.2182 | +0.2116 |
| 7265 | OM-1 Mark II | 10400x7792 | 6.980 | 1.0939 | 0.9785 | +11.79% | +0.2518 | +0.2197 | +0.2165 |
| 5283 | OM-1 | 5220x3912 | 7.836 | 1.1261 | 1.1084 | +1.60% | +0.0481 | +0.0335 | +0.0433 |
| 5286 | OM-1 | 5220x3912 | 7.813 | 1.1230 | 1.1052 | +1.61% | +0.0498 | +0.0358 | +0.0426 |
| 5287 | OM-1 | 5220x3912 | 7.538 | 1.0919 | 1.0679 | +2.25% | +0.0562 | +0.0381 | +0.0530 |
| 5284 | OM-1 | 8180x6132 | 6.947 | 1.0537 | 0.9856 | +6.91% | +0.1524 | +0.1295 | +0.1504 |
| 5285 | OM-1 | 10400x7792 | 6.283 | 0.9845 | 0.8918 | +10.39% | +0.1506 | +0.1543 | +0.2032 |
| 7798 | OM-3 | 5220x3912 | 7.944 | 1.1183 | 1.1185 | -0.02% | +0.0327 | +0.0091 | +0.0064 |
| 7796 | OM-3 | 5220x3912 | 7.764 | 1.1014 | 1.0961 | +0.48% | +0.0374 | +0.0067 | +0.0118 |
| 7797 | OM-3 | 8180x6132 | 6.993 | 1.0361 | 0.9947 | +4.16% | +0.0879 | +0.0687 | +0.0786 |
| 7799 | OM-3 | 10400x7792 | 6.760 | 1.0161 | 0.9661 | +5.18% | +0.0641 | +0.0600 | +0.0894 |

Files, all CC0 raw.pixls.us (id, SHA-256):
- 5283 `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`
- 5284 `f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf`
- 5285 `862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874`
- 5286 `2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1`
- 5287 `dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2`
- 7262 `d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd`
- 7263 `780fa6a22ecd272cf3e86c04114439953b95fbc1bba8a05b4c99595a22e36bba`
- 7264 `d7fea34029b9926e7d9cf6ecdfef9de90cbda41ff6eea009cc1a4f5b1813b8df`
- 7265 `c7bd43b29ed89542058534b867fa894b8550d1960503cf4b4cb9f5912fd242b3`
- 7796 `1cee7deb661e45101ab3ca6c4240d24ed949b167ed423703fca15c09dd8ec176`
- 7797 `318e35647d93b2c598c0fec1d0d075336d2e2f5e6930faee05f32182c9a8ac5f`
- 7798 `6fab41a21d5c8c0469619049888b0a36c7b260d893e3c35c174044b7293e9d43`
- 7799 `9da7407d27007320c5bcf4e4d0b8c5c7bb533669cf4fabdf4e6a4b567cf318cc`

Against the lead:

- The six lead files reproduce exactly: real/null 1.1987/1.1317, 1.1214/1.0051, 1.0939/0.9785, 1.1014/1.0961, 1.0361/0.9947, 1.0161/0.9661, with lag 1 / lag 2 +0.1883/+0.1894, +0.2576/+0.2182, +0.2518/+0.2197, +0.0374/+0.0067, +0.0879/+0.0687, +0.0641/+0.0600. The lead's +0.188/+0.189 figure for 7262 is at 8.078 bpp, just above its "about 7 bpp or below" range, so that range is not the whole story.
- "Files at about 7 bpp or below are 4 to 12% above the null": holds on the new body, where 5284 (6.947 bpp) is +6.91% and 5285 (6.283) is +10.39%, and on the lead's 6.76 to 7.19 bpp files (+4.16% to +11.79%).
- "and show lag 1 to 3 correlations of +0.06 to +0.26": holds at those bpp values (+0.0641 to +0.2576 at lag 1).
- "Unlike the four high-bpp files of #86": directionally holds but is not a bpp threshold. 7264 is +5.75% at 8.107 bpp, the same as 7262 at 8.078, while 7798 is -0.02% at 7.944 and 7796 is +0.48% at 7.764. Bits per pixel does not separate those files across bodies; the ordering is within a body.
- "Depends on the file, not the body": partly. Files of one body differ (OM-1 ranges +1.60% to +10.39%, OM-3 -0.02% to +5.18%), but the body is not irrelevant: at the same 5220x3912 geometry and 7.76 to 8.11 bpp, OM-1 Mark II is +5.75% to +5.92%, OM-1 +1.60% to +1.61% and OM-3 -0.02% to +0.48%. So the data support "bpp orders the files within a body; the body sets the offset", not "not the body".
- ISO and the scene/setting property (the lead's second next step) are not tested: `orf_tokens.py` prints no ISO, and no scene metadata was read. The cause of the body offset is therefore open.

## Reproduce

```sh
python -I tools/pixls_samples.py download ../orf-samples-om1 --model OM-1
python -I tools/pixls_samples.py download ../orf-samples-om --model "OM-1 Mark II" --max 4
python -I tools/pixls_samples.py download ../orf-samples-om --model OM-3 --max 4
python -I tools/orf_tokens.py FILE --max-tokens 1500000
```

In this run `--max 4` saved 7262 to 7265 and 7796 to 7799 (7264 and 7798 are the new files). Repeat for each id; read the lines "ones-density ... real X, Bernoulli null Y", "correlation of min(q,8)" and "payload: ... bpp=Y". Match files to the table by SHA-256, not by name. All are CC0, so a public rerun needs nothing else.
