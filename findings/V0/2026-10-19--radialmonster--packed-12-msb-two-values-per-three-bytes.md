# packed-12: two 12-bit values per 3 bytes, MSB first; three bodies need bytes reversed in 4-byte words

Author: @radialmonster
Verified by: @radialmonster
Lead: #69
Variant: V0
Builds on: #28

## Claim

The 9 CC0 `packed-12` files store two 12-bit values per 3 bytes, most-significant bit first (first value = byte0 << 4 | byte1 >> 4, second = (byte1 & 15) << 8 | byte2), rows contiguous, stride = width x 1.5 bytes. Six files (C5060WZ, C7070WZ, SP-510UZ, SP-550UZ, SP-565UZ, SP-570UZ) use plain byte order; three (XZ-2, XZ-10, SH-2) have the bytes reversed inside every 4-byte word before the same unit layout. In XZ-2 the low 2 bits of every value in the window are zero; in XZ-10 and SH-2 they are not. The order of the two pixels inside a unit is not decided by these statistics.

## Original evidence

Lead #69 (opened by @radialmonster, 2026-10-19), from `tools/orf_v0_unpack.py` (last changed in `0785fcb`) on the 9 files, raw.pixls.us ids and SHA-256 as listed in the lead: 1432 XZ-2 (675fefe7...), 1799 C5060WZ (3fc12bc3...), 2420 SP510UZ (f0737d78...), 2431 XZ-10 (a25383ac...), 3438 SP565UZ (5088771f...), 5491 SP570UZ (baab9239...), 780 C7070WZ (9d55506f...), 792 SH-2 (6e6b9b7d...), 8609 SP550UZ (05f49918...). The lead used the default window (3 bands of 16 rows, first 1200 columns).

## Verification

New run on 2026-10-19 UTC by @radialmonster, after the lead was posted, on repository commit `abe5c10` (`tools/orf_v0_unpack.py` still at `0785fcb`), Python 3.13. The lead already used every CC0 `packed-12` file (all 9), so no unused CC0 file exists. This is a wider run on the same files: 8 bands of 32 rows and 2400 columns (about 5 times the lead's 3 x 16 x 1200 window, and nearly the full width on the 2608-wide C5060WZ), bands at different row positions. All 9 SHA-256 values matched the lead. `pixls_samples.py check` reported every file CC0.

The chosen layout family matches the lead on 9 of 9 files. Best-layout margin (best score of the next family divided by the winner's score) and row-stride correlation at the true stride; the 1 byte off correlation is in brackets:
- XZ-2: w4-12-msb, margin 5.30, 0.985 (0.160 / 0.157); low 2 bits zero share 1.0000
- XZ-10: w4-12-msb, margin 11.61, 0.994 (0.110 / 0.109); low 2 bits zero share 0.7068
- SH-2: w4-12-msb, margin 5.02, 0.941 (0.100 / 0.090); low 2 bits zero share 0.2596
- C5060WZ: 12-msb, margin 3.19, 0.891 (-0.003 / -0.001)
- SP510UZ: 12-msb, margin 2.33, 0.914 (0.071 / 0.069)
- SP565UZ: 12-msb, margin 1.88, 0.781 (0.043 / 0.045)
- SP570UZ: 12-msb, margin 1.68, 0.588 (0.029 / 0.028)
- C7070WZ: 12-msb, margin 1.96, 0.918 (0.048 / 0.049)
- SP550UZ: 12-msb, margin 2.57, 0.857 (0.004 / -0.000)

The three word-reversed files again have the largest margins (5.0 to 11.6) and the six plain ones the smallest (1.7 to 3.2); the weakest plain file is again SP570UZ. In five files the tool printed a `-swap` variant as the winner or a 2% tie (SP570UZ printed `12-msb-swap`, tied with `12-msb` at score 0.626 and h1 0.530 vs 0.529): the pixel order inside a unit is undecided (h1 gap 0.0 to 0.5%) on 7 files and weakly favoured the unswapped order by 3.8 and 4.1% on SP510UZ and SP550UZ, as in the lead. Compared with the lead's margins, the wider window gives larger ones on 6 files (C5060WZ, SP510UZ, XZ-10, SP565UZ, SP570UZ, C7070WZ) and smaller ones on 3 (XZ-2 6.26 to 5.30, SH-2 6.49 to 5.02, SP550UZ 2.84 to 2.57); no layout call changes. This reproduces the claim; it is the same tool on the same files, so it checks repeatability on a larger sample of each frame, not an independent implementation. No pixel values or images were written or compared with another decoder.

## Reproduce

Keep the files outside the repository (here `../orf-samples`, with names as downloaded). From the repository root:

    python tools/pixls_samples.py check ../orf-samples/*
    python tools/orf_v0_unpack.py --bands 8 --rows 32 --cols 2400 FILE [FILE ...]

where FILE are the 9 `packed-12` files listed above (raw.pixls.us ids 1432, 1799, 2420, 2431, 3438, 5491, 780, 792, 8609). Read the `chosen:` line, the `row-stride test` line and the `low2=0` column of the chosen layout for each file.
