# Token-phase profile transfer on six public prefixes

Part of #30. Builds on #11 and #153. Measured by @radialmonster on 2026-10-21 UTC. This is an aggregate study using an unchanged tool, not a finding or reproduction of historical private conditional-context gains.

## Design fixed before outcomes

The [claim comment](https://github.com/radialmonster/orf-cleanroom/issues/30#issuecomment-6310280301) fixed the cohort and criterion before measurements. Use [tools/token_phase_probe.py at bcbf789d84bf75f2724f27e04ab21e2facf9e40e](https://github.com/radialmonster/orf-cleanroom/blob/bcbf789d84bf75f2724f27e04ab21e2facf9e40e/tools/token_phase_probe.py) and its unchanged repository imports. Scan the first 262144 complete candidate tokens from payload bit zero, q zeros/stop/5-bit suffix, zero extra escape bits. Omit q>=17 symbols without compacting absolute token indices. For every modulus 2..8, count phase versus joint suffix symbol 2*b4+b2, and report unsmoothed plug-in mutual information (MI), marginal entropy and conditional entropy in bits. Every integer table is preserved in [the complete JSON](lead30-phase-public-cohort.json).

Primary descriptive transfer criterion per file: MI(mod2)>MI(mod3) AND MI(mod2)>MI(mod5). This asks whether the 1993 parity-prominent prefix profile from the earlier two-file #153 smoke report transfers under this narrow comparison. The other smoke file, 6343, already failed this ordering, so the earlier report never supported uniform transfer. The claim comment used shorthand for that heterogeneous smoke report; this study tests the 1993 pattern specifically. These six prefixes were unused in that phase smoke cohort (1993/6343); they have been measured for different metrics elsewhere. No significance threshold, shuffle, conditional-context estimator or physical column inference is supplied.

## Public provenance

Every file passed a fresh tools/pixls_samples.py check against the public site's licence listing before measurement. Each exact ID/name/full hash matches an existing CC0 manifest row; no row was changed or appended. Hashes, names, dimensions, strip offsets/lengths, compression tags and measured signatures are retained in the JSON. Each signature is variable-size with compression tag 1 and variant unassigned; model names do not select a variant.

- 241, Olympus - E-P3 - 16bit (4:3).ORF, SHA-256 540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd.
- 1079, Olympus - E-PM1 - 16bit (4:3).ORF, SHA-256 db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765.
- 1051, Olympus - E-M1 - 16bit (4:3).orf, SHA-256 19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda.
- 4126, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509.
- 4132, Olympus - E-M10 Mark IV - 16bit (4:3).ORF, SHA-256 77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4.
- 6946, OM System - TG-7 - 16bit (4:3).ORF, SHA-256 4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a.

## Outcomes

All six returned 262144 tokens with zero shortfall. In cohort order above, consumed bit endpoints are 1737004,1756598,1775448,1737857,1788524,1946399; omitted escapes are 3,55,3,1,3,2235. Thus retained symbol counts are 262141,262089,262141,262143,262141,259909. All omissions preserve original phase indices.

Only 4132 meets the primary criterion; the other five fail. MI bits for moduli 2,3,4,5,6,7,8 respectively (rounded here; full precision in JSON):

- 241: 0.000014909734,0.000013485772,0.000037536926,0.000031136585,0.000035372865,0.000057429598,0.000061380889.
- 1079: 0.000005469628,0.000025109146,0.000023036667,0.000030725601,0.000048052731,0.000082067675,0.000034711472.
- 1051: 0.000003347066,0.000014033675,0.000015113657,0.000019047509,0.000028721070,0.000035762102,0.000032910306.
- 4126: 0.000016939582,0.000023501555,0.000042297090,0.000014270913,0.000086165744,0.000064901562,0.000078811650.
- 4132: 0.000677292774,0.000009461054,0.000678247494,0.000031926470,0.000711884718,0.000047336344,0.000707017992.
- 6946: 0.000002375452,0.000024480937,0.000021055855,0.000042216062,0.000041846597,0.000025160375,0.000047029220.

The descriptive parity comparison therefore does not transfer uniformly to this cohort. These values do not reproduce or contradict the historical zero conditional-context gain: its metric and private cohort differ. Positive finite-sample plug-in MI need not indicate dependence; failure of this ordering does not establish absence of parity dependence. Unequal degrees of freedom across moduli, multiple comparisons, arbitrary origin at payload bit zero, scene variation and a single selected prefix per file limit interpretation. A global shift of token phase merely permutes phase labels, but changing the bit-parse origin can change tokens. Selective escape omission and uncertain post-escape framing remain limitations. No physical rows, run-copy semantics, causal mechanism, stationarity, significance or decoding claim follows.

## Reproduce

Review complete source and imports first. Substitute paths for the six public files; names below are exact public identities. Run the licence checker before the measurement.

```text
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_phase_probe.py
python -I -B tools/token_phase_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

Read samples[].statistics.moduli[].plugin_mi_bits and phase_by_symbol_00_01_10_11. The criterion is the strict conjunction above, without rounding. Seven synthetic tests passed before public measurements. Supervisor independently rechecked all six CC0 licences and reran the complete report, matching the full JSON exactly. An independent entropy-identity calculation H(phase)+H(symbol)-H(joint) matched every one of the 42 contingency-table MI values within 1e-12. These checks confirm the computation, without providing independent human verification. Python 3.13.15, CPU only; no GPU overhead was needed. JSON source_sha256 hashes identify the actual Windows CRLF working files; LF checkouts may report different source-byte hashes while sample aggregates match. No source was modified for this study.

## Status

Holds descriptively: all six specified public prefix measurements completed; 4132 alone passes the declared parity comparison.
Does not generalize the 1993 descriptive ordering: five prefixes fail this newly declared comparison. The earlier two-file smoke was already heterogeneous (6343 failed). No historical private numerical claim is declared contradicted.
Not tested: historical conditional-context gains, physical columns/rows, statistical significance, framing variants, run-copy semantics, causal adaptation, other #30 negatives or a decoder.
Open: predeclared untouched windows and suitable context/null controls, then physical-column tests once boundaries are established. Full public rerun: exact method link and six-sample command above. No number rests on private inputs.

I confirm this follows RULES.md and is released under CC0 1.0. No images/previews were viewed or forbidden decoder material used. All contributing agents represent the same human @radialmonster; this is not independent human verification.

Codex session: 01a15d4b-4392-7930-ab5e-b31bc1b4c01b.
