# fixed-size payloads are exact; everything else is compressed

Author: @radialmonster
Alias: F4
Variant: container
Builds on: F2

- Claim: uncompressed ORF payloads have a size exactly equal to width x height x 12, 12.8 or 16 bits. Compressed payloads have data-dependent sizes, 6-8.5 bits per pixel on the bodies tested. A bits-per-pixel threshold alone misleads: High Res Shot files from older bodies are 12.8 bpp packed (uncompressed), while newer bodies' High Res Shot files are compressed (6-7 bpp).
- Census of every CC0 Olympus / OM System ORF on raw.pixls.us (65 models):
  - packed-12 (9): C5060WZ, C7070WZ, SH-2, SP-510UZ, SP-550UZ, SP-565UZ, SP-570UZ, XZ-10, XZ-2
  - packed-12.8 (5): E-300, E-330, E-500, plus the High Res Shot files of E-M5 Mark II and PEN-F
  - packed-16 (3): E-1, E-10, E-400
  - variable (48): E-3, E-410, E-420, E-450, E-5, E-510, E-620, E-M1, E-M10, E-M10 Mark II/III/IIIs/IV, E-M1 Mark II/III, E-M1X, E-M5, E-M5 Mark II/III, E-P1, E-P2, E-P3, E-P5, E-P7, E-PL1, E-PL2, E-PL3, E-PL5, E-PL6, E-PL7, E-PL8, E-PL9, E-PL10, E-PM1, E-PM2, OM-1, OM-1 Mark II, OM-3, OM-5, OM-5 Mark II, PEN-F, STYLUS1, STYLUS1s, TG-4, TG-5, TG-6, TG-7, XZ-1, including High Res Shot sizes (8172-10400 wide) on E-M1 Mark II and later.
- Builds on: F2 (@radialmonster).
- Evidence: `tools/orf_signature.py` (`size_class` column) on raw.pixls.us CC0 files from the bodies above. Reproduce: `tools/pixls_samples.py download DIR` (all CC0 Olympus/OM files), then `tools/orf_signature.py DIR/*` and count `size_class` per model.
