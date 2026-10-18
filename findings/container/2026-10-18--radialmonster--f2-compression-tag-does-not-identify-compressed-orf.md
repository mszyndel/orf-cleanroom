# the compression tag doesn't identify compressed ORF

Author: @radialmonster
Alias: F2
Variant: container

- Claim: on every compressed ORF tested, the raw IFD's TIFF Compression tag (0x103) is 1 ("uncompressed"), and BitsPerSample is 16. The tag can't be used to classify. Bits per pixel (payload bytes x 8 / pixels) can: about 6-8.5 for the compressed bodies tested, and 16.00 for an uncompressed body (E-1).
- Also seen: High Res Shot-sized payloads (8172-10400 wide) in the same container with the same tag values.
- Evidence: `tools/orf_signature.py` on raw.pixls.us CC0 files from E-P7, E-M1MarkII, E-M5, E-1, OM-1, OM-3 and OM-5 Mark II (17 files).
- Reproduce: `python tools/orf_signature.py <those files>`.
