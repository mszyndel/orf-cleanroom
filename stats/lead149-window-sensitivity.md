# Lead 149: fixed-window sensitivity at the original DC scale

Method: unchanged `tools/token_luma_probe.py` at `f750607171d79781273f9c93bee6e98aec8e7743`; measured by @radialmonster, 2026-10-21 UTC. Builds on #149, #11 and #29. This is an unverified sensitivity experiment, not a new finding or an independent-human reproduction. The window-63 control is already covered by the existing self-verified finding.

The design was [posted before outcomes](https://github.com/radialmonster/orf-cleanroom/issues/149#issuecomment-6308649594): all five widths 1, 15, 31, 63, 127 on IDs 1995, 1997 and 1998, top 300 candidate token rows, 20 shuffles, seed 1 per file/window. No sample, width, target, seed or mapping was selected after seeing this run. These files were previously studied in the lead; they are not newly untouched validation files. They had been held out from the original fixed-mapping design, which does not make this sensitivity experiment a fresh holdout test.

## Public input identities

All passed `tools/pixls_samples.py check` immediately before this run and match existing manifest hashes. Local downloaded names use underscores in `(4_3)`; these are the public names:

- 1995, `Olympus - E-M1MarkII - 16bit (4:3).ORI`, SHA-256 `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f`.
- 1997, `Olympus - E-M1MarkII - 16bit (4:3).ORI`, SHA-256 `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a`.
- 1998, `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA-256 `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71`.

Measured signatures: all ORF-RO, payload 5240x3912, compression tag 1, variable-size/unassigned. Payload byte totals respectively 15768425, 15767553, 15772675. No variant is inferred from the camera model. No manifest row or existing finding was changed.

## Exact method and reproduction

For each input, invoke each of the five declared widths independently, replacing FILE and WINDOW:

```text
python -I -B tools/pixls_samples.py check FILE
python -I -B tools/token_luma_probe.py FILE --rows 300 --window WINDOW --perms 20 --seed 1
```

Read the existing source and imports first. The Python CLI reads files and prints aggregate summaries only. All 15 CLI cells are preserved in the accompanying CSV at its printed precision: correlation/shuffle mean/shuffle SD to five decimal places, descriptive standardized difference z to two. Individual shuffle scores are not printed by this existing CLI and are not represented as available in this table. No added measurement tool is required.

The candidate parse begins at payload bit zero, MSB-first, q zeros + stop one + five suffix bits. Escapes q>=17 consume q+6 bits with no extra skip and their b2+b4 mapping is zero. Tokens are reshaped using the 5240 payload width, without assuming established physical row delimiters. The centered box window is truncated at row edges; width 1 is no token-box smoothing but is still block-averaged at the preview DC scale. The unchanged CLI uses the largest qualifying embedded baseline JPEG, first luma component DC coefficients, and uses its top round(300*300/3912)=23 of 300 DC rows, 400 columns. Correlation subtracts each DC row's mean. This is a numeric comparison with the camera rendering, not sensor ground truth. No preview or image was viewed or written.

Each file/window reinitializes Random(1); windows therefore use the same 20 within-row token permutations in the same order for that file. Shuffle mean and sample standard deviation summarize those 20 draws. Their standardized difference is descriptive, without a significance calibration or multiple-comparison claim. Permutation destroys within-row alignment but preserves each row's suffix distribution, including zero-mapped escapes.

## Results

All 15 reported correlations are positive and exceed their own shuffle means. In window order 1, 15, 31, 63, 127, r is 1995: +0.05306, +0.06436, +0.08141, +0.10846, +0.14807; 1997: +0.06152, +0.07585, +0.09476, +0.12245, +0.16996; 1998: +0.04811, +0.05966, +0.07410, +0.09793, +0.13737. Correlation rises at every tested step in each file, but the shuffle SD rises too. The descriptive standardized differences are not monotone across all widths (see all cells in the CSV); none establishes an optimal codec scale or calibrated significance. Width 63 is not uniquely associated with a positive top-band correlation under this fixed geometry. Every run used 300 token rows, DC 400x300 and target 23x400, with 1, 1 and 2 zero-mapped escapes respectively. The width-63 control agrees with the lead to its stated precision.

## Limits and remaining work

Only token-box width varies. DC scale, body, band, candidate parse, escape policy and payload-width geometry stay fixed. Changing the box width changes the filter as well as spatial resolution; a larger score does not identify a codec scale. Active area differs from payload geometry (ongoing #163); no crop-aware interpretation follows. The proxy is known to vary in sign across other frame bands (#11), so this top-band experiment does not support whole-frame stationarity or pixel-value decoding. No private input is used. DC-scale sensitivity, other bodies, segmented whole-frame tests, context-conditioned mappings and separate b2/b4 contributions remain open.

Validation: the existing four synthetic tests and built-in matched-grid self-test passed before real measurement. CPU only, using the existing stdlib CLI without implementation changes. The supervisor reviewed the complete sources/imports, diff, scratch aggregates and public text, repeated the CC0/hash checks, and reproduced all 15 CLI cells exactly in a separate run. A small independent CPU calculation also checked box-edge handling, zero-mapped escapes, block averaging and row-centred correlation. Both agents represent the same human contributor; this is not independent-human verification. All contribution text follows RULES.md; no other raw decoder sources, outputs or writeups were used.

Source SHA-256: token_luma_probe.py `85415f5d212d82162c362bb2ba0638faa0eeb8b8acbc259666dcfc75ca66ebcc`; orf_tokens.py `c6f51ed26793b1bb400a1dc1b29d8e20f9ef734373770310c665228ce02f08ad`; orf_signature.py `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`; jpeg_dc.py `d86e5a4d0b4e3bc1481b40dff070d73f5c311611545cee46ae8ac602287ce381`. Python 3.13.15.
