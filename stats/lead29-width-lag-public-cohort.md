# Lead #29 item 8: nominal width-lag signs on six public prefixes

Measured by: @radialmonster, 2026-10-21 UTC.
Builds on: #11, #29 item 8 and the original width-lag tool from #180.
Method: unchanged `tools/token_width_lag_probe.py` at
`dd6e2c3b92443b75163dbdca3af2fb063aaa0a10`.
[Complete aggregate report](lead29-width-lag-public-cohort.json) contains every
sample identity/hash, source hash, all 150 binary count tables, Pearson values,
nominal parity strata and pair omissions. No new tool or finding is proposed.

The predeclared pooled-sign criterion holds on **0 of 6** public prefixes.
The historical private donor-pattern values and physical interpretation are
neither reproduced nor declared contradicted. These are new descriptive
candidate-token measurements at nominal payload-width lags.

## Fixed design and provenance

The [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6311364371)
fixed the cohort and criterion before measurements. All six public files from
the five selected folders were included: 241 E-P3, 1079 E-PM1, 1051 E-M1,
4126/4132 E-M10 Mark IV, 6946 TG-7, outside the earlier 1993/5283/6343 width-lag
smoke cohort. Availability selected these files; they have been measured for
other questions and are not random population samples or assumed independent
scene replicates. Each passed a fresh `pixls_samples.py check` as CC0 and
matched an existing manifest row by exact SHA-256, ID, public name and licence.
Existing manifest rows and attribution are unchanged. Measured variable-size
signatures remain unassigned, rather than inferring a variant from the body.

The existing tool takes the first 262144 complete candidate tokens, parsing
MSB-first q zeros, one stop bit and five suffix bits from payload bit zero.
Escapes q>=17 consume q+6 bits with no extra skip. W is measured payload width,
not an established token-row stride. At W, 2W, 2W-2 and 2W+2, compare past b2
to current b2. At 2W-1 compare past b4 to current b2. All indices t>=lag are
eligible, including the final incomplete nominal row. Omit a pair if either
endpoint has q>=17, without renumbering. Intervening escapes remain; endpoint
omission cannot repair unknown post-escape framing.

For each lag report exact 2x2 counts and Pearson correlation pooled and in all
four target nominal parity strata `((t//W)%2,(t%W)%2)`. Empty/zero-variance
correlations are null. These strata are not established sensor/CFA parity.

Primary descriptive criterion per file: pooled b2 correlations satisfy
`W<0 AND 2W<0 AND 2W-2>0 AND 2W+2>0`. The fifth lag and all nominal strata
are descriptive secondary outputs. No invariance threshold, significance
test, p-value, uncertainty estimate or post-outcome cohort change is used.

## Selection and results

Every file returned all 262144 requested complete tokens, no shortfall.
Python 3.13.15; CPU only, RTX 3090 unnecessary for this bounded calculation.
Lag order throughout: W, 2W, 2W-2, 2W+2, 2W-1.

| ID | Payload | Escapes | Consumed bits | Pooled retained pairs | Pooled omitted pairs |
|---|---|---:|---:|---|---|
| 241 | 4080x3040 | 3 | 1737004 | 258059/253980/253982/253978/253981 | 5/4/4/4/4 |
| 1079 | 4080x3040 | 55 | 1756598 | 257956/253881/253883/253879/253882 | 108/103/103/103/103 |
| 1051 | 4640x3472 | 3 | 1775448 | 257499/252861/252863/252859/252862 | 5/3/3/3/3 |
| 4126 | 5200x3904 | 1 | 1737857 | 256943/251743/251745/251741/251744 | 1/1/1/1/1 |
| 4132 | 5200x3904 | 3 | 1788524 | 256940/251741/251743/251739/251742 | 4/3/3/3/3 |
| 6946 | 4040x3016 | 2235 | 1946399 | 253744/249733/249734/249733/249731 | 4360/4331/4332/4329/4334 |

All pooled correlations, rounded to nine decimal places:

| ID | W b2/b2 | 2W b2/b2 | 2W-2 b2/b2 | 2W+2 b2/b2 | 2W-1 b4/b2 | Criterion |
|---|---:|---:|---:|---:|---:|---|
| 241 | -.003798954 | -.000696163 | +.002054245 | -.000972870 | +.001869711 | fails |
| 1079 | +.001583458 | -.000162829 | -.001417172 | +.000410894 | -.000142230 | fails |
| 1051 | -.003409383 | -.000262452 | -.003481602 | -.000159628 | +.002539921 | fails |
| 4126 | +.000434311 | +.002521531 | +.006748434 | +.005031107 | +.004716331 | fails |
| 4132 | +.012995590 | +.010031981 | +.007693433 | +.010563013 | +.019963121 | fails |
| 6946 | +.002363533 | +.000280080 | -.001514600 | +.002449248 | -.000792915 | fails |

No prefix has the complete predeclared sign conjunction. This limits extension
of the historical qualitative sign pattern to these new nominal-grid public
measurements, without testing the historical files, exact estimator or physical
donor interpretation. Small signed values are retained without treating their
signs as significant. All 120 stratum tables and 30 pooled tables, including
negative values, are preserved in JSON; no parity-invariance claim is made.
The two E-M10 IV files differ numerically despite matching geometry, so these
are per-file measurements rather than constants for a model or size class.

## Reproduce

Read complete tool/import sources at the named method commit first. Obtain
the exact public files through the repository CC0 downloader; SHA-256 and
public names are in the JSON and `samples/manifest.csv`. Replace FILE identifiers
with corresponding checked local paths; commands read inputs and print
aggregate data only.

```sh
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_width_lag_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_width_lag_probe.py \
  --sample 241 'Olympus - E-P3 - 16bit (4:3).ORF' FILE241 \
  --sample 1079 'Olympus - E-PM1 - 16bit (4:3).ORF' FILE1079 \
  --sample 1051 'Olympus - E-M1 - 16bit (4:3).orf' FILE1051 \
  --sample 4126 'Olympus - E-M10 Mark IV - 16bit (4:3).ORF' FILE4126 \
  --sample 4132 'Olympus - E-M10 Mark IV - 16bit (4:3).ORF' FILE4132 \
  --sample 6946 'OM System - TG-7 - 16bit (4:3).ORF' FILE6946
```

Six synthetic width-lag tests and the scanner self-test passed before the
real report. All sources/imports were fully reviewed. This work uses public
CC0 samples only, with no private inputs, images/previews viewed or other raw
decoder material. All helper/supervisor agents represent the same human
@radialmonster; a separate agent audit is not independent human verification.

Supervisor audit reviewed the complete runtime/import/test sources, frozen
diff, command ledger, scratch aggregates, provenance and public code blocks.
A fresh six-file CC0-checked run matched the helper report exactly. A separate
TIFF reader and string-based token parser, with Counter tables and covariance
arithmetic and no repository imports, confirmed all 150 contingency tables,
candidate/omission counts, Pearson values, endpoints, escapes and manifest
identities. Six synthetic tests, scanner self-test, findings validation,
whitespace and public text checks passed. No substantive source or measurement
correction was needed; an initial PowerShell parse error executed no code and
was corrected before measurement. The unchanged method is CPU-only.

## Status

Holds descriptively: the fixed measurements completed on all six prefixes;
all exact tables, omissions, hashes and nominal strata are reported.
Fails on this cohort: the predeclared pooled sign conjunction, 0/6.
Historical exact values and physical donor claims are neither reproduced nor
declared contradicted by this different candidate-token metric.
Not tested: #29 items 1-7/9, magnitude correlations, physical row/CFA meaning,
parity invariance, stationarity, significance, encoder mechanism or decoding.
Open: framing/escape interpretation and established row boundaries, then a
separately declared untouched-window/cohort study with width-lag controls.
All four historical Next steps of #29 remain open; no lead closure or finding
is proposed. Exact rerun: commands above at the immutable method commit.
Every number uses named public CC0 files; none depends on private inputs.
