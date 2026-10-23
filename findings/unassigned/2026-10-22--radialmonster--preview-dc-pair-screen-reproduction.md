# Preview-DC pair screen reproduces exactly and adds two held-out E-M1 Mark III positives

Author: @radialmonster
Verified by: @radialmonster
Lead: #313
Variant: unassigned
Builds on: #295

## Claim

Lead #313 reported a fixed identity-aligned 12x12 preview-DC screen on eight
public CC0 files: 10 of 28 distinct-content pairs at or above the frozen
r >= 0.98 cutoff, all ten among ids 1994/1995/1996/1997/1998, with positive
scores from 0.9999303459791392 to 0.9999981079624815 and the other 18 from
-0.19529426418442286 to 0.8596295852239235. The 3800/3802 control pair is
0.8596295852239235. All eight previews are 3200x2400 and the 12x12 grid SD
ranges from 43.179985401186585 to 71.83824708967308.

Those numbers reproduce exactly. Extending the same frozen method to the three
public E-M1 Mark III files the lead did not use gives 12 positives among 55
pairs: the original ten are unchanged, and two held-out pairs cross the cutoff,
3801/3802 at 0.999910190819734 and 3803/3804 at 0.999927340237148. The 10-of-28
count is therefore a property of the eight-file cohort, not of the body. Both
new positives combine a High Res file with an ORI of the same body; that is a
numeric screening result, not evidence of scene identity.

## Original evidence

Lead #313, found by @radialmonster on 2026-10-22. Tool:
`tools/preview_pair_screen.py` at commit
`ea03f1ddb718d1dbc862e3fa4a551213383332b6` (PR #312), using the reviewed
`tools/jpeg_dc.py`. The method was frozen before the scores: largest supported
baseline preview, complete 8x8 luma blocks only, integer-partition 12x12 grid
of quantized DC means, centered and unit-norm, identity alignment, fixed
r >= 0.98 cutoff, grid SD below 1 rejected, exact-content deduplication by
SHA-256, every pair printed.

The lead's eight public CC0 inputs (raw.pixls.us id, name, SHA-256):

- 1993, Olympus - E-M1MarkII - 16bit (4:3).ORF, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`
- 1994, Olympus - E-M1MarkII - 16bit (4:3).ORF, `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23`
- 1995, Olympus - E-M1MarkII - 16bit (4:3).ORI, `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`
- 1996, Olympus - E-M1MarkII - 16bit (4:3).ORF, `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2`
- 1997, Olympus - E-M1MarkII - 16bit (4:3).ORI, `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`
- 1998, Olympus - E-M1MarkII - 16bit (4:3).ORF, `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`
- 3800, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f`
- 3802, Olympus - E-M1MarkIII - 16bit (4:3).ORI, `83932e61123a90a423a81f87d08c9ed66bca5feb0d900d7d1d0924845dfa9f46`

The three additional public CC0 inputs used only by this verification:

- 3801, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `e9a21175493e9d9e5653aa91f1bd6fbf421aba42b59b4ffe7cd1f7cac2de385c`
- 3803, Olympus - E-M1MarkIII - 16bit (4:3).ORF, `4ad47518e3766fae6b98f8b18f3aae3c277e5966028e3f2e0d2702bb0f17a3cd`
- 3804, Olympus - E-M1MarkIII - 16bit (4:3).ORI, `d831692b608471ad64667eb2485bab553de0ddb9366d384c4ecb731092b5dc42`

## Verification

New run on 2026-10-22 at 01:22 UTC, after the lead was posted. All eleven
local SHA-256 values matched the retained verified-CC0 inventory and an
existing `samples/manifest.csv` row; no download, catalogue request or manifest
edit was made. The lead already used all six CC0 E-M1 Mark II files, so no
unused file of that body exists. The lead used two of the five CC0 E-M1 Mark III
files; 3801, 3803 and 3804 are the three held-out files. Python 3.13.15, the
lead's tool at the pinned commit, and the same 12x12 / identity / 0.98 / SD >= 1
settings. No image or preview was rendered or viewed.

Eight-file reproduction (28 pairs, 10 positive):

- Positive scores: 0.9999303459791392 to 0.9999981079624815, all ten pairs
  among 1994/1995/1996/1997/1998. The lowest is 1996/1998; the highest is
  1994/1996.
- Other 18: -0.19529426418442286 to 0.8596295852239235. The minimum is
  1993/1996; the maximum is the 3800/3802 control at 0.8596295852239235.
- All eight previews are 3200x2400 and the grid SD range is
  43.179985401186585 to 71.83824708967308 (minimum 1997, maximum 1993). No
  file was rejected as low-information.

The four published bounds and the 3800/3802 control agree to the last printed
digit with the independent run below; the tool prints the same values.

Held-out extension (11 files, 55 pairs, 12 positive). The original ten scores
are unchanged. The two added positives are:

- 3801/3802: 0.999910190819734
- 3803/3804: 0.999927340237148

Every other added pair is below 0.98, the highest being 3800/3803 at
0.925225291156168 and 3800/3804 at 0.923020922152954. The two new positives
pair a High Res ORF with an ORI of the same body. The screen is symmetric in
its inputs, so this is a candidate-pair observation only; it does not establish
that either pair is one capture.

Independent check. A separate prefix-sum 12x12 bin aggregation, with a raw
two-pass Pearson formula on the unnormalized bin means, reproduced all 55
correlations exactly and the eight-file bounds exactly. An RTX 3090 / CuPy
14.0.1 float64 recomputation of the 11x11 correlation matrix agreed with the
CPU matrix to floating-point precision. This checks the arithmetic and the
grid construction, not scene identity.

## Reproduce

From a clean checkout, with the lead's tool at commit
`ea03f1ddb718d1dbc862e3fa4a551213383332b6` (PR #312; use that commit or the
PR head if it is not yet on `main`), and the files downloaded under names that
use `_` for `:` in `(4:3)`:

    python -I -B tools/test_preview_pair_screen.py
    python -I -B tools/test_jpeg_dc.py
    python -I -B tools/preview_pair_screen.py "1993_Olympus - E-M1MarkII - 16bit (4_3).ORF" "1994_Olympus - E-M1MarkII - 16bit (4_3).ORF" "1995_Olympus - E-M1MarkII - 16bit (4_3).ORI" "1996_Olympus - E-M1MarkII - 16bit (4_3).ORF" "1997_Olympus - E-M1MarkII - 16bit (4_3).ORI" "1998_Olympus - E-M1MarkII - 16bit (4_3).ORF" "3800_Olympus - E-M1MarkIII - 16bit (4_3).ORF" "3802_Olympus - E-M1MarkIII - 16bit (4_3).ORI"

That is the exact eight-file run. For the held-out extension, append:

    "3801_Olympus - E-M1MarkIII - 16bit (4_3).ORF" "3803_Olympus - E-M1MarkIII - 16bit (4_3).ORF" "3804_Olympus - E-M1MarkIII - 16bit (4_3).ORI"

The tool prints one JSON line per sample, one per pair and a summary. The
expected eight-file summary is 8 samples, 28 pairs, 10 positives; the 11-file
summary is 11 samples, 55 pairs, 12 positives.

## Limitations

This is a numeric identity-aligned screen, not scene identity, capture
provenance, exposure or metadata agreement, and not ground truth. High
correlation can come from shared scene structure, tone processing or an
embedded-preview reuse; the two held-out positives are consistent with
same-capture pairs but do not prove one. The 0.98 cutoff is a frozen screening
threshold, not a calibrated false-positive rate; there are no unrelated-scene
labels or held-out labeled evaluation. Only E-M1 Mark II and E-M1 Mark III
files were used, all with 3200x2400 previews; other bodies, preview sizes,
shifts, crops, rotations and low-information scenes were not tested. The
finder and verifier are the same human account (`self-verified`); the
independent implementation is by the same person, not an independent human
verification. The 10-of-28 figure is specific to the eight-file cohort; the
wider public cohort gives 12 of 55, and no general population count is claimed.
