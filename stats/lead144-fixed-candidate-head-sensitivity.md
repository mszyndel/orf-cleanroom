# Fixed-candidate head-length sensitivity for lead #144

Part of #144. Builds on #11 and #218. Measured by @radialmonster on
2026-10-21; both helper and supervisor represent this same human contributor.
This is new descriptive lead evidence, not independent human verification or
a finding. It follows RULES.md and is released under CC0 1.0.

## Design fixed before outcomes

The [claim comment](https://github.com/radialmonster/orf-cleanroom/issues/144#issuecomment-6321312207)
declared the two public inputs, first 300 candidate rows, token origin zero,
heads 1/8/16/32/64/128, and three fixed input/stride combinations. Strides were
already reported in #144: 5240 on id 1993, and 5240/5472 on id 6343. Neither
stride nor phase is refitted. Every declared head is retained without selecting
a winner. These availability-selected files and their earlier metrics are
known; this is neither blind sampling nor a scene-controlled comparison.

The unchanged tool is [tools/token_band_profile.py at 9f731ea](https://github.com/radialmonster/orf-cleanroom/blob/9f731ea9614d790c3d95f0e594b085b8116502bb/tools/token_band_profile.py).
Its source SHA-256 is
`8211d2535517097033a444e49f9c3f5e0dc4af833be0d6d9b256e6db2ee31c46`.
Its only repository import is `orf_signature.py`, SHA-256
`b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`.

Candidate tokens are unary zero runs, a one stop bit and five suffix bits;
only complete tokens are accepted. Zero extra bits are skipped at candidate
escapes. All q values remain, capped at 40; q>=17 is counted. This uncertain
escape treatment cannot establish actual framing. For each candidate row,
the contrast is mean capped q over the head minus mean capped q over the rest.
The tool emits exact integer contrast moments and signed mean/standard-error
scores. These scores are descriptive, without a calibrated significance or
independent-row assumption. Changing head changes both contrast and variance;
score increases do not identify an optimal block length or a physical endpoint.

## Public inputs and provenance

Both local SHA-256 values matched the retained CC0 verification inventory and
existing manifest identity/hash rows before measurement. The prior verification
was reused for identical content; no catalogue request or new download occurred.
Both measured payloads are 5240x3912, compression tag 1, variable-size,
variant unassigned. Camera names alone do not assign a variant.

- raw.pixls.us 1993, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256
  `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`;
  payload 15,760,125 bytes.
- raw.pixls.us 6343, `OM System - OM-5 - 16bit (4:3).ORF`, SHA-256
  `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`;
  payload 17,772,487 bytes.

## Results

All 18 declared cells completed 300 rows, with no shortfall or undefined score.
The accompanying JSON preserves every exact head/rest sum, contrast moment,
denominator, candidate escape count, parse endpoint and source/input identity.

For heads 1, 8, 16, 32, 64, 128 respectively:

- 1993 S=5240 signed scores: 0.837423, -0.585165, 3.765437, 10.002171,
  13.824603, 10.681506. Head-minus-rest means: 0.109285, -0.014925,
  0.066969, 0.123351, 0.103761, 0.053862.
- 6343 S=5472 signed scores: 1.231806, 5.204049, 7.100735, 10.588039,
  15.080469, 19.656912. Means: 0.172177, 0.177405, 0.175576,
  0.176511, 0.187516, 0.187548.
- 6343 S=5240 width-control signed scores: 1.104442, 0.905492, 0.078289,
  0.001413, -0.162905, 0.073695. Means: 0.155374, 0.032895, 0.002227,
  0.000032, -0.003184, 0.001261.

Thus the head-32 profile is sensitive to head choice at the fixed candidates;
its score is exceeded at other declared heads on both inputs. The 1993
head-8 contrast is negative. On 6343 S=5472, the mean contrast persists through
head 128 rather than uniquely singling out 32. These nested, overlapping
contrasts do not establish that a physical special block is longer than 32.
No stride maximum is measured at any head.

At every head, 1993 parsed 1,572,000 tokens consuming 9,574,636 bits; its
profile includes one candidate escape. 6343 parsed 1,641,600 tokens consuming
10,781,790 bits; its S=5240/S=5472 profiles include 200/211 escapes. The two
6343 strides cover different token spans (300*S); this is not equal-span
controlled sampling.

## Reproduce

Read the pinned source and its import first; match each local input SHA-256
to its retained verified CC0 record. New or changed content needs its first
licence verification. Replace FILE1993 and FILE6343 with those local copies.
Run each measurement command six times, replacing HEAD with each of the
literal values 1, 8, 16, 32, 64, 128; no other arguments change:

```text
python -I -B tools/test_token_band_profile.py
python -I -B tools/token_band_profile.py --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" 0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8 FILE1993 --stride 5240 --start-row 0 --rows 300 --head HEAD
python -I -B tools/token_band_profile.py --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7 FILE6343 --stride 5240 --stride 5472 --start-row 0 --rows 300 --head HEAD
```

The JSON has the twelve CLI objects in head-major order, input 1993 then 6343.
No parser or reusable tool was added or modified. Six existing synthetic tests
and CLI help passed before measurement. CPU only; RTX 3090 was available and
unnecessary for this job. No images/previews, private files or prohibited
decoder material were accessed.

## Status

Holds descriptively: every declared cell completed; the profile depends on
head length, and a 32-token head is not uniquely favored by these fixed-candidate
scores. The head-32 cells agree numerically with the prior figures, without
claiming a new historical finding verification.

Contradicts: no historical physical-row or universal claim is declared
contradicted by this different bounded measurement.

Not tested: whether a scanned stride maximum moves with head length, an exact
special-block endpoint, physical rows, whole-frame constancy, later maxima,
meaning of extra S-W tokens, escape semantics, calibrated significance,
historical private measurements or decoding. The last head-length Next step
is only partly advanced; it remains open alongside all other unanswered steps.

Open: a separately predeclared head-by-stride comparison with appropriate
phase/content controls could test movement of the maximum; independent
physical framing evidence would still be needed to identify image rows.
Exact rerun: the pinned source and commands above. All sample measurements
are from the named public CC0 inputs; no private measurements. No finding,
spec/decoder change, independent-human verification or lead closure proposed.
Candidate PR review/merging belongs to the separate hourly maintainer task.
