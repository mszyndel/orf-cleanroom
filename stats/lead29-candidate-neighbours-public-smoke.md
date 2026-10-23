# Lead #29: candidate-grammar neighbour smoke on two public files

Measured by: @radialmonster, 2026-10-21 UTC.
Builds on: #11, #29, #187 and #194; specs/V1.md G8.
Method: unchanged `tools/suffix_width_lag_probe.py` at
`54271dad8e91e96a5f04432d5f3e1f1ad976859c` (merged #194).
[Complete aggregate JSON](lead29-candidate-neighbours-public-smoke.json)
contains every exact contingency table, MI, endpoint, omission and source hash.
This completes #194's previously unmeasured real-file smoke. No new tool,
finding, historical private-number reproduction or specification change.

## Fixed design and provenance

The original #194 design and cohort are retained, reaffirmed before outcomes
in [Taking this](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6316533241).
For every k=2..8 and stop bit 0/1, parse the first 262144 complete tokens from
payload bit zero: q non-stop bits, one stop bit, k MSB-first suffix bits.
No extra escape skip. At every lag 1..5, count binary q>0 (2x2) and fixed
low-two suffix bits s&3 (4x4). Omit pairs only when either endpoint has q>=17,
without compacting indices; intervening escapes remain. Rows are past symbol,
columns current symbol. All 14 grammars and five lags are reported per file.

Both original planned public samples were drawn from the existing verified
CC0 pool. Each local SHA-256 matched its retained verified licence/public
identity record and an existing manifest ID/name/hash row before measurement.
Prior verification remains valid for identical content; no catalogue refresh
was needed. No new content was downloaded. Existing manifest attribution is
unchanged. The measured variable-size signatures remain unassigned.

6946: `OM System - TG-7 - 16bit (4:3).ORF`, SHA-256
`4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a`,
payload 4040x3016, 12300700 bytes.
4126: `Olympus - E-M10 Mark IV - 16bit (4:3).ORF`, SHA-256
`ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509`,
payload 5200x3904, 17235346 bytes.
These files have appeared in earlier public measurements; they are neither a
random population sample nor an untouched research cohort.

## Results and limitations

Python 3.13.15, CPU only. All 28 grammar/file cases returned 262144 complete
tokens, zero shortfall, zero failures. The JSON retains all 140 lag cases,
280 exact tables and their MI values, rather than selected peaks.

Every table below lists lags 1,2,3,4,5 in order. MI is unsmoothed plug-in bits,
rounded here to nine decimal places; exact counts/full precision are in JSON.
No null, significance threshold, grammar-ranking criterion or winner is
proposed. Grammar-dependent endpoints and escape omissions mean the same
number of tokens covers different source bits and selected pairs. Equal
alphabet sizes do not remove marginal, selection or finite-sample bias.
Endpoint omission cannot repair unknown post-escape framing. No physical row,
padding meaning, codec grammar or decoding is established.

### Sample 6946

| Stop | k | Consumed bits | q>=17 | q-positive MI, lags 1..5 | low2 MI, lags 1..5 |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 2 | 1003718 | 3 | 0.001762873, 0.000898393, 0.000552055, 0.000564654, 0.000367200 | 0.011968340, 0.006401716, 0.002723634, 0.003483149, 0.001116226 |
| 0 | 3 | 1267790 | 4 | 0.001456980, 0.000552522, 0.000305511, 0.000114069, 0.000151606 | 0.009219588, 0.002973892, 0.002374582, 0.000651027, 0.000270575 |
| 0 | 4 | 1533365 | 6 | 0.000852862, 0.000273588, 0.000198738, 0.000083038, 0.000074516 | 0.006898478, 0.002354682, 0.000927862, 0.000679661, 0.000949786 |
| 0 | 5 | 1795516 | 2 | 0.000726059, 0.000344728, 0.000109297, 0.000212402, 0.000067462 | 0.004397638, 0.002184226, 0.000381016, 0.000883809, 0.000742467 |
| 0 | 6 | 2060068 | 3 | 0.000679080, 0.000313770, 0.000080929, 0.000216346, 0.000076057 | 0.003767209, 0.001656961, 0.000568030, 0.000655768, 0.000487457 |
| 0 | 7 | 2319943 | 3 | 0.000287360, 0.000083602, 0.000149787, 0.000054088, 0.000105244 | 0.003029206, 0.000748414, 0.000892030, 0.000556407, 0.000422966 |
| 0 | 8 | 2583784 | 5 | 0.000236091, 0.000044091, 0.000096402, 0.000039333, 0.000052403 | 0.001805584, 0.000312761, 0.000649569, 0.000344482, 0.000271873 |
| 1 | 2 | 1133161 | 2323 | 0.000089763, 0.000006075, 0.000039476, 0.000005976, 0.000006534 | 0.000438451, 0.000563837, 0.000895287, 0.000475934, 0.000333940 |
| 1 | 3 | 1403943 | 2560 | 0.000192103, 0.000220429, 0.000027970, 0.000067084, 0.000041255 | 0.000432773, 0.000605449, 0.000485356, 0.000178257, 0.000250512 |
| 1 | 4 | 1673385 | 2143 | 0.000001543, 0.000714291, 0.000009752, 0.000049386, 0.000009102 | 0.000398039, 0.001420992, 0.000217071, 0.000350451, 0.000163377 |
| 1 | 5 | 1946399 | 2235 | 0.000023185, 0.000223225, 0.000033561, 0.000003901, 0.000020227 | 0.000156170, 0.001606149, 0.000186264, 0.000258366, 0.000289640 |
| 1 | 6 | 2221651 | 2451 | 0.000013627, 0.000032237, 0.000005364, 0.000015916, 0.000032330 | 0.000344177, 0.000657933, 0.000095422, 0.000041839, 0.000050095 |
| 1 | 7 | 2501891 | 3401 | 0.001197404, 0.000489032, 0.000052523, 0.000058265, 0.000001065 | 0.000265873, 0.000184256, 0.000060682, 0.000089746, 0.000086835 |
| 1 | 8 | 2778389 | 3330 | 0.000208760, 0.000114849, 0.000032954, 0.000055907, 0.000039210 | 0.000476712, 0.000248509, 0.000133139, 0.000180944, 0.000082436 |

### Sample 4126

| Stop | k | Consumed bits | q>=17 | q-positive MI, lags 1..5 | low2 MI, lags 1..5 |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 2 | 1040946 | 2 | 0.000042186, 0.000003978, 0.000007487, 0.000025733, 0.000011150 | 0.001130065, 0.000734414, 0.000902626, 0.000240029, 0.000056491 |
| 0 | 3 | 1309259 | 1 | 0.000168776, 0.000192039, 0.000011394, 0.000034129, 0.000004131 | 0.000353978, 0.000298339, 0.000284969, 0.000088218, 0.000023061 |
| 0 | 4 | 1573374 | 2 | 0.000512616, 0.000001245, 0.000042707, 0.000003379, 0.000002180 | 0.000735671, 0.000267711, 0.000043109, 0.000042637, 0.000024879 |
| 0 | 5 | 1819178 | 2 | 0.000000036, 0.000079342, 0.000059929, 0.000001868, 0.000000005 | 0.002285853, 0.000168305, 0.000288887, 0.000075349, 0.000029332 |
| 0 | 6 | 2090548 | 1 | 0.000013815, 0.000007091, 0.000011155, 0.000000242, 0.000001083 | 0.000685926, 0.000180648, 0.000101731, 0.000082664, 0.000023702 |
| 0 | 7 | 2351487 | 4 | 0.000501235, 0.000009786, 0.000010719, 0.000000034, 0.000007828 | 0.000447831, 0.000097339, 0.000027049, 0.000028352, 0.000013892 |
| 0 | 8 | 2613871 | 3 | 0.000536817, 0.000136885, 0.000026349, 0.000002133, 0.000002072 | 0.001094017, 0.000244591, 0.000011772, 0.000031294, 0.000031164 |
| 1 | 2 | 1020558 | 1 | 0.000411370, 0.000135600, 0.000024972, 0.000334276, 0.000036867 | 0.000140876, 0.000201220, 0.000049160, 0.000063023, 0.000077731 |
| 1 | 3 | 1295386 | 1 | 0.000351593, 0.000001982, 0.000080421, 0.000036620, 0.000000086 | 0.000319741, 0.000756376, 0.000328764, 0.000156969, 0.000026198 |
| 1 | 4 | 1554980 | 1 | 0.000179317, 0.000020586, 0.000099685, 0.000010660, 0.000001020 | 0.000707601, 0.000449332, 0.000194277, 0.000111504, 0.000041905 |
| 1 | 5 | 1737857 | 1 | 0.000367555, 0.001290962, 0.003907116, 0.001286284, 0.000996108 | 0.000088923, 0.000392324, 0.000056201, 0.000022375, 0.000044191 |
| 1 | 6 | 2071363 | 1 | 0.000105840, 0.000018012, 0.000000034, 0.000000910, 0.000001894 | 0.003855485, 0.000785425, 0.000093030, 0.000043512, 0.000021335 |
| 1 | 7 | 2337096 | 1 | 0.000085713, 0.000013394, 0.000000967, 0.000003785, 0.000000587 | 0.002335697, 0.000326100, 0.000122578, 0.000076693, 0.000034937 |
| 1 | 8 | 2596031 | 1 | 0.000172938, 0.000001983, 0.000002879, 0.000004875, 0.000001283 | 0.000359438, 0.000514261, 0.000054299, 0.000017864, 0.000027534 |

## Reproduce and status

Read the full named tool, its imported `tools/orf_signature.py`, and tests
before running. Obtain the named public CC0 inputs; verify each local hash
against its retained verified record. New/unverified content requires a first
licence check. Replace FILE6946/FILE4126 with the exact matching local files.

```text
python -I -B tools/test_suffix_width_lag_probe.py
python -I -B tools/suffix_width_lag_probe.py --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126
```

Five existing synthetic tests pass, covering independent string parsing,
exact contingency/entropy identities, directed pairs, endpoint-only escape
omission, both container byte orders and sanitized mixed CLI failures.
Supervisor read the complete runtime/import/test sources and frozen artifacts,
rechecked both input hashes, reran the complete report identically, and used a
separate original TIFF locator/string parser/Counter/entropy calculation to
confirm all 280 exact tables and MI values (tolerance 1e-12), token counts,
endpoints and omissions. No source or measurement correction was needed.
CLI help passes. No GPU overhead is needed for this bounded CPU job; RTX3090
was available. Both helper and supervisor represent the same human
@radialmonster, not independent human verifiers.

Status: the predeclared two-file measurement now completes with all cases
reported. None of #29's historical private figures or claims 1..9 is verified
or declared contradicted by this distinct descriptive metric. The undefined
row-exactness measure, justified framing/escape semantics, deeper b2/b4 law,
physical rows and all historical Next steps remain open. A separately declared
comparison with appropriate nulls and framing controls is needed before any
code-family interpretation. All new measurements rest on the named public
CC0 inputs; none uses private files. No finding or lead closure is proposed.
