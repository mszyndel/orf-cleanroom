# Clean-room rules

## Allowed sources
- Public specifications: TIFF / TIFF-EP, Exif, DNG, JPEG, and similar published standards.
- Patents (their prose and figures), as a description of a method. Constants and bit layouts are confirmed from the files themselves.
- The files' own structure: tags, maker notes, embedded previews, and measurements of the compressed data.
- Your own original code and analysis.

## Not allowed
- Code from any other raw decoder, including **LibRaw, rawspeed and dcraw**, and any project derived from them.
- Write-ups, wikis, blog posts or forum posts that describe what such code does.
- The *output* of such decoders, used as a reference, an oracle, a test expectation or a comparison, even as a black box.
- Anything from pull requests or branches whose decoder was developed with any of the above.

If you have read the ORF decompression code in any of those projects, you're welcome to help with samples, tooling and testing, but please don't contribute to decoder logic or findings about the bitstream.

## Data
- Raw files are referenced by raw.pixls.us name and hash, never committed.
- Only CC0 / public-domain samples are used for published numbers.
- No images of decoded or preview data are committed. Aggregate statistics only.

## Findings are append-only
- New findings are added at the end of FINDINGS.md as a new numbered, dated entry with an author.
- Existing entries are never edited, reordered or deleted, so nobody's work can be erased.
- To correct or retract an entry, append a new entry that says which one it corrects and why.
- A CI check rejects pull requests that change or remove existing lines in FINDINGS.md.

## Sign-off
By opening a pull request you confirm that your contribution follows these rules and is released under CC0 1.0 (see LICENSE). Please say so in the PR description ("I confirm this follows RULES.md").
