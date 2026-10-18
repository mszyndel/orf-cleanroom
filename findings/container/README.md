# container/

Findings about the file container (TIFF structure, tags, maker notes, payload offsets and sizes), and findings that span more than one variant.

Format, file names and status rules: [../README.md](../README.md).
Variant definitions: [VARIANTS.md](../../VARIANTS.md).

## Findings here
A snapshot; `python tools/findings_index.py` gives the live list with peer status.

- [F2 (f2-compression-tag-does-not-identify-compressed-orf)](2026-10-18--radialmonster--f2-compression-tag-does-not-identify-compressed-orf.md): The TIFF compression tag reads "uncompressed" even on compressed ORFs, so it cannot be used to tell them apart; the payload size can (see F4).
- [F3 (f3-entry-format-update)](2026-10-18--radialmonster--f3-entry-format-update.md): A process note: entries may name what they build on and who submitted them.
- [F4 (f4-fixed-size-payloads-are-exact)](2026-10-18--radialmonster--f4-fixed-size-payloads-are-exact.md): Uncompressed payloads have an exact size of width x height x 12, 12.8 or 16 bits; every other payload is compressed. Includes a census of the models on raw.pixls.us.
