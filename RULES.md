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
- Raw files are never committed. Reference them by SHA-256, plus the raw.pixls.us id and name when they come from there.
- **raw.pixls.us files:** use only CC0 ones. Verify the licence when downloading, or use `tools/pixls_samples.py check` once for previously unverified content. Keep the verified licence, public identity and SHA-256; reuse that verification while the local hash matches. Do not repeat the online check for unchanged verified files. New or changed content without a verified record still needs verification before use.
- **Your own files are welcome.** You can test with raws you shot yourself, or ones whose owner agreed. Publish only aggregate numbers and the file's SHA-256, never the file or images from it. Results that rest only on files others can't get are marked `not yet reproducible` until a CC0 copy exists. Uploading a few to raw.pixls.us as CC0 fixes that.
- Don't use files whose licence you don't know, or that are under a non-CC0 licence (e.g. the CC BY-NC-SA files on raw.pixls.us).
- No images of decoded or preview data are committed. Aggregate statistics only.

## Leads are issues, findings are files
- A **lead** is an unverified result, published as a GitHub issue. Leads follow the same rules as everything else here: public specs, patents, the files' own structure and original code. Leads that come from another decoder's code or output are not accepted.
- A **finding** is a lead that was reproduced in a second, separate run, by a different person (preferred) or by the finder (`self-verified`). Each finding is its own file `findings/<folder>/YYYY-MM-DD--finder--short-slug.md`, in the folder for its variant (`container`, `V0`, `V1`, `V2`, `unassigned`), added by the reproducer's PR. Format and rules: findings/README.md.
- An existing finding file is never edited, renamed or deleted (except by the repo owner), so nobody's work can be erased.
- To correct a finding, add a new verified finding with `Corrects: <ID>`; the index shows the old one as superseded.
- CI rejects pull requests that modify or remove existing finding files, or that add a finding file that doesn't validate (including one not verified by its own PR author).

## Credit
Everyone who finds something keeps the credit for it.
- The finder keeps credit: their `@handle` is in the finding's file name and its `Author:` line, and the lead issue stays theirs. The verifier is credited as `Verified by:`. Because existing files are never edited, that credit can't be edited away, and a later correction is a new file that leaves the original and its author in place.
- If your work builds on someone else's finding or lead, say so with a `Builds on:` line (a finding ID or `#n`). A lead you reproduce is credited by `Verified by:`; a different person who later reproduces a self-verified finding is credited in a new file with `Reproduces:`.
- Publish leads under your own handle. If you want to publish someone else's result (for example from a Discussion), ask them to open the lead themselves, or link their post from your own lead as `Builds on`.
- In `samples/manifest.csv`, rows are append-only and `measured_by` is never overwritten. When you measure more columns of a file already listed, add a new row for the same `sha256` under your own handle.
- Pull requests are squash-merged with the contributor kept as the commit author. Add `Co-authored-by:` lines for anyone else who did the work.
- When a decoder built from this work is contributed to LightCraft or elsewhere, it credits every finding author and verifier it relies on, by name and finding ID.

## Sign-off
By opening a pull request you confirm that your contribution follows these rules and is released under CC0 1.0 (see LICENSE). Please say so in the PR description ("I confirm this follows RULES.md").
