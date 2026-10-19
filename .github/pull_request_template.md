## What this adds

<!-- One focused change. Link the issue it addresses: "Fixes #n" if this finishes it, "Part of #n" if not. -->

## Checklist
- [ ] I confirm this follows RULES.md.
- [ ] Raw files and images are not included; numbers only.
- [ ] Every number has the `tools/` script that produced it, and the files it ran on (raw.pixls.us id + SHA-256, or `own` + SHA-256).
- [ ] Verification PR: it adds a new file under `findings/<folder>/` named `YYYY-MM-DD--finder--slug.md`, with `Author:` the finder, `Verified by:` me, and `Lead: #n` (the lead issue, opened by the finder, labelled `lead`). Nothing existing is edited.
- [ ] The finder is a different person than me, and I ran the checks myself (preferably on other files than the lead used).
- [ ] Manifest: rows are appended only (a new row for an already listed `sha256`), with `measured_by` starting `@myhandle `.
- [ ] For bitstream/decoder work: I have not read the ORF decompression code of LibRaw, rawspeed, dcraw or their derivatives.
