# Same-width separated suffix-window transfer (#11)

Method: unchanged `tools/suffix_window_probe.py` at repository commit
`7d49b20bfcdffd74245558890cee92da71c63b20` (last changed in #212,
`b457123ffcb551523d7fc63c52a8666839860440`). Exact source SHA-256s,
public raw.pixls.us identities/hashes and all contingency tables are retained
in `lead11-same-width-separated-windows.json`.
Measured by @radialmonster, 2026-10-21 UTC. Builds on #11, #176, #204 and #212.

The earlier E-M1MarkII 1995/1997 consecutive windows met a strict alternating
H/L ordering criterion. The separated-window extension on 4126/6946 met it
on 0/8 windows. This study asks whether the same ordering transfers across
selected files sharing nominal payload width 5240. The cohort and criterion
were fixed before outcomes in
https://github.com/radialmonster/orf-cleanroom/issues/11#issuecomment-6320650389 .
These available files had known earlier measurements and different reported
candidate row-strides; selection was neither blind nor random. This metric is
sequential H/L MI, distinct from #219's nominal-width lag correlation signs
and #222's fixed-phase q profiles.

Public CC0 inputs (raw.pixls.us id, exact public name, SHA-256):

- 1993, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`.
- 6343, `OM System - OM-5 - 16bit (4:3).ORF`, `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.
- 8549, `OM System - OM-5 Mark II - 16bit (4:3).ORF`, `c6fe861982ddc18464cf6858d2700f6813cc3a17956bcb12d1179212c999c76a`.

Every local hash matched a retained prior verified-CC0 record and its existing
manifest identity before measurement. No catalogue refresh or manifest edits.
Every measured signature is variable-size 5240x3912 with compression tag 1;
variant remains unassigned, rather than inferred from camera model.

Fixed method: parse from payload bit zero, MSB-first q zeros, stop1, five
suffix bits, no extra escape skip. Four windows of 262144 candidate tokens
start at absolute indices 0,2097152,4194304,6291456. For lags 1,2,3, all four
ordered H/L pairings use ordinary q<17 endpoints without compacting indices;
intervening escapes remain. Pairs stay inside each window. H=suffix>>3,
L=suffix&7. The empirical unsmoothed plug-in MI tables and every omission
count are retained. The strict criterion requires every cross-field MI >
every same-field MI at lags1/3 and every same-field MI > every cross-field MI
at lag2. A file passes the predeclared all-window criterion only when all
four windows pass every lag. No null, significance or stationarity test.

All three scans return 6553600 tokens, all 12 windows are full, and there
are zero failures. Consumed endpoints in id order are 40339794,43355999,
43538994 bits. Escape counts per window:

- 1993: 1,0,0,0. Strict criterion 4/4 windows; each lag passes 4/4.
- 6343: 34,35,64,30. Strict criterion 0/4; each lag passes 0/4.
- 8549: 1,91,124,79. Strict criterion 0/4; lag1 passes 0/4,
  lag2 passes 4/4 and lag3 passes 1/4 (last window only).

The all-four-window file criterion holds on 1/3 selected files. The ordering
seen on 1995/1997 persists on separated 1993 windows, but does not transfer
to either selected other-body file at the same width. Nominal width alone
therefore does not guarantee this descriptive criterion in these inputs.
This does not establish a causal body/stride difference: scene, token density,
escape selection, and unknown initial/post-escape framing remain confounded.
Earlier exact-input measurements and immutable findings are unchanged.

After reading the full source/imports and verifying exact local SHA-256s
against retained verified-CC0 records, substitute only FILE paths:

```text
python -I -B tools/test_suffix_window_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/suffix_window_probe.py --window-stride 2097152 --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 8549 "OM System - OM-5 Mark II - 16bit (4:3).ORF" FILE8549
```

Read `samples[].windows[].lags[].pairings[]` for every exact table/MI,
not selected cells. The JSON is unchanged CLI output, including source hashes,
Python version, endpoints, selection denominators, shortfalls and failures.
Nine existing synthetic tests, scanner self-test and CLI help passed before
measurements. CPU only; RTX3090 available but unnecessary. Both agents
represent the same human radialmonster, not independent human verifiers.
No images/previews, prohibited external decoder material, private inputs,
raw bytes or pixel dumps were used. No reusable tool or decoder change.

Status
Holds/measured: complete three-file, twelve-window accounting with every table
retained; strict ordering 4/4 on 1993 and 0/4 on each other file.
Does not transfer: the earlier E-M1MarkII ordering uniformly across these
three same-width files (all-window criterion 1/3). No historical private
figure was reproduced or declared contradicted.
Not tested: significance/null calibration, exact H/L independence or exclusive
chains, b1/b0 fairness, physical rows, one token per pixel, CFA, initial/escape
semantics, causal scene/body/stride explanations, values/predictors or decoding.
Open: independently justified framing and sampling/null controls; controlled
public scene/setting comparisons would distinguish possible causes. All
unanswered #11 questions remain open. No finding/spec change or lead closure.
Rerun: pinned unchanged method and exact three-file command above. Every
measurement rests on the named public CC0 inputs; no private numbers.

Supervisor audit: full executed sources/imports, actual two-file diff, aggregate output, scratch inventory and execution ledger reviewed. Fresh local hash verification and unchanged CLI rerun matched the frozen JSON byte for byte. An independent original CPU TIFF locator, string-search scanner, Counter tables and entropy calculation matched all three payloads/endpoints, all 144 tables, counts/omissions/order flags and MI within 1e-12. Nine synthetic tests, scanner self-test and CLI help passed again. No numerical/source correction was needed. Repository checks and public-text scans passed. Same human throughout; this is not independent human verification.
