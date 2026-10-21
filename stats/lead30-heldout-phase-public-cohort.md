# Held-out token-phase transfer on six public prefixes

Part of #30. Builds on #11, #191 and #203. Measured by @radialmonster on 2026-10-21 UTC. This is a new descriptive public study using an unchanged tool, not a finding or reproduction of historical private conditional-context figures.

## Design fixed before outcomes

The [claim comment](https://github.com/radialmonster/orf-cleanroom/issues/30#issuecomment-6318286688) fixed the six inputs, estimator and criterion before this run. Use unchanged [tools/token_phase_context_probe.py at 3c50bd59566ba1b6a21c475c0e708a649c15bea3](https://github.com/radialmonster/orf-cleanroom/blob/3c50bd59566ba1b6a21c475c0e708a649c15bea3/tools/token_phase_context_probe.py) and its repository imports. The complete [aggregate JSON](lead30-heldout-phase-public-cohort.json) preserves all original plug-in reports and all held-out tables, losses, selection counts and source-byte hashes. No tool was changed.

Parse the first 262144 complete candidate q-zero/stop-one/five-suffix tokens from payload bit zero, with zero extra escape bits. Retain complete 128-token blocks only if every q<17; discard incomplete tails. Train original even-index blocks and test original odd-index blocks, one direction. Targets begin at local index 2, so source triples never cross a block boundary. Y=b2(t), C=2*b4(t-1)+b2(t-2), absolute phase P=t mod m for every m=2..8. Compare Jeffreys-smoothed binary P(Y|C) versus P(Y|C,P) on identical held-out targets. Gain is baseline loss minus phase loss, in bits per target. Negative gains remain in the report.

Primary descriptive transfer criterion per file: all four even-modulus gains (m=2,4,6,8) are strictly positive without rounding, matching the positive-even-gain profile of 1993 in the earlier two-file #203 smoke. The other smoke file 6343 already had negative gains at every modulus. This is a descriptive conjunction, not an inferential threshold or a claim that any positive gain establishes signal.

These six files were unused in #203's held-out experiment, but their marginal phase results were already known from #179 and were read before selecting this cohort. In particular 4132 alone met that earlier marginal ordering. This is a selected cohort with known marginal outcomes, not a blind/random validation cohort or independent scenes. The present estimator and selection differ from that marginal report.

## Public provenance

Every selected local SHA-256 matched its retained verified CC0 inventory record and the exact existing manifest ID/name/hash/CC0 identity before measurement. This reuses successful verification of identical content; no online catalogue request was made. No manifest rows were altered or appended.

- 241, Olympus - E-P3 - 16bit (4:3).ORF, SHA-256 540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd.
- 1079, Olympus - E-PM1 - 16bit (4:3).ORF, SHA-256 db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765.
- 1051, Olympus - E-M1 - 16bit (4:3).orf, SHA-256 19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda.
- 4126, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509.
- 4132, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4.
- 6946, OM System - TG-7 - 16bit (4:3).ORF, SHA-256 4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a.

The measured signatures are variable-size, compression tag 1; variant remains unassigned. Full dimensions, strip offset/length and hashes are in the JSON. No model-based variant assignment or private input is used.

## Outcomes

All six return 262144 complete candidate tokens with zero shortfall, 2048 complete blocks and no incomplete tail. Consumed bit endpoints in cohort order above: 1737004,1756598,1775448,1737857,1788524,1946399. Parsed escapes: 3,55,3,1,3,2235.

Retained train/test blocks (omitted train/test blocks):

- 241: 1022/1023 (2/1); targets 128772/128898.
- 1079: 997/1002 (27/22); targets 125622/126252.
- 1051: 1023/1023 (1/1); targets 128898/128898.
- 4126: 1023/1024 (1/0); targets 128898/129024.
- 4132: 1023/1023 (1/1); targets 128898/128898.
- 6946: 531/540 (493/484); targets 66906/68040.

Every model has zero held-out targets in unseen training contexts. TG-7 loses 977 of 2048 complete blocks, a substantial selection burden; the surviving blocks cannot represent all parsed tokens by assumption.

Gains in bits per held-out target, m=2,3,4,5,6,7,8 respectively (rounded here; full precision and both losses are in JSON):

- 241: -0.000025027915,-0.000014588784,-0.000029675702,-0.000024922354,-0.000072943772,-0.000059798772,-0.000040440605.
- 1079: +0.000030866880,+0.000022764533,-0.000008858928,-0.000162696205,+0.000051818962,-0.000210609650,-0.000132027774.
- 1051: -0.000016356611,-0.000077398207,+0.000002703211,+0.000003851639,-0.000087440156,-0.000088832819,-0.000078270281.
- 4126: -0.000000781999,-0.000003249571,-0.000107738965,-0.000063541868,+0.000000787566,-0.000131896803,-0.000128848519.
- 4132: +0.000033310986,-0.000080735187,-0.000028363900,-0.000052694943,-0.000092511959,-0.000288800844,-0.000082582264.
- 6946: +0.000006737657,+0.000031148223,-0.000102879072,-0.000178748957,-0.000021853506,-0.000355321514,-0.000353265175.

Baseline losses, in the same cohort order: 0.9949312020590613,0.9964124413463711,0.9996988417249301,0.9932006736766305,0.98258531795735,0.9990087904905405 bits. No file meets the all-even-positive criterion (0/6). In particular the earlier marginal ordering on 4132 does not imply this held-out criterion; it has positive m=2 gain but negative m=4,6,8 gains. These are distinct measurements, not a contradiction of the earlier marginal scores.

Adjacent training/test blocks can remain dependent. Known marginal results informed cohort selection; finite prefixes, one split direction, fixed context, scene/body confounding, smoothing, multiple moduli and heavy escape exclusion limit interpretation. Escape omission cannot repair unknown post-escape framing. A negative gain does not establish absence of phase dependence; a small positive gain does not establish significance, unbiased prediction benefit or physical columns. No generating mechanism, stationarity, physical rows/CFA, historical private bound or decoder follows.

## Reproduce

Review the full pinned source/imports first. Match each local file hash to its retained verified CC0 record; new or changed/unverified content requires its first licence verification. Substitute the six exact public file paths below; commands read samples and print aggregates only.

```text
python -I -B tools/test_token_phase_context_probe.py
python -I -B tools/token_phase_context_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

Read samples[].heldout.moduli[].gain_vs_context_bits and both context model reports. Apply the strict all-even-positive conjunction to full-precision gains. The unchanged plug-in reports are preserved for completeness and are not the primary criterion. Ten synthetic tests and CLI help pass. The supervisor reviewed the complete runtime/import/test source, frozen diff, scratch aggregates, execution ledger and public code blocks; independently rechecked all six retained CC0 hashes and manifest identities, and reran the complete six-file CLI report with exact JSON agreement. A separate original CPU string parser and Counter calculation matched every held-out train/test table, selection count and token bit endpoint across all 42 modulus cases; independently computed losses and gains agree within 1e-12. No numerical correction was needed. Python 3.13.15, CPU only; RTX 3090 available but unnecessary. JSON source-byte hashes reflect the CRLF checkout; other line endings can change source hashes while numerical aggregates match. All contributing agents represent the same human @radialmonster; computational auditing is not independent human verification.

## Status

Holds descriptively: six declared public prefixes complete, with every held-out count/table/loss retained. None meets the predeclared all-even-positive transfer criterion.
Does not transfer to this selected cohort: the earlier 1993 smoke's all-even-positive gain profile, 0/6 under this estimator. No historical private numerical or semantic claim is declared contradicted.
Not tested: historical conditional-context gain bound, statistical significance/null calibration, unbiased prediction benefit, stationarity, physical rows/columns, escape semantics, other #30 framing negatives or decoding.
Open: justified framing and separately declared untouched windows/cohorts with justified sampling and null controls; the present cohort was selected from known marginal results. All unanswered #30 questions remain open. Exact rerun: pinned method and complete six-sample command above. Every number uses named public CC0 inputs; no private measurement.

I confirm this follows RULES.md and is released under CC0 1.0. No images/previews or forbidden decoder material were used. No finding, spec or decoder change is proposed.

Codex-Session: 01a15ece-e3a3-77a2-8e55-df1dfeb46f4d
