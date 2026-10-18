# Findings

One file per finding, in the folder for the variant it concerns. Nobody numbers anything and nobody edits anyone else's file, so pull requests don't conflict.

The first four findings carry an `Alias:` line (`F1`..`F4`), and those short IDs work anywhere an ID is expected, for example `Builds on: F1`. They are ordinary files like all the others.

## What's known so far
A snapshot, grouped by folder. `python tools/findings_index.py` gives the live list with peer status (lead, reproduced or disputed).

**container/**
- [F2 (f2-compression-tag-does-not-identify-compressed-orf)](container/2026-10-18--radialmonster--f2-compression-tag-does-not-identify-compressed-orf.md): The TIFF compression tag reads "uncompressed" even on compressed ORFs, so it cannot be used to tell them apart; bits per pixel can.
- [F3 (f3-entry-format-update)](container/2026-10-18--radialmonster--f3-entry-format-update.md): A process note: entries may name what they build on and who submitted them.
- [F4 (f4-fixed-size-payloads-are-exact)](container/2026-10-18--radialmonster--f4-fixed-size-payloads-are-exact.md): Uncompressed payloads have an exact size of width x height x 12, 12.8 or 16 bits; every other payload is compressed. Includes a census of the models on raw.pixls.us.

**V0/**
none yet

**V1/**
- [F1 (f1-initial-results)](V1/2026-10-18--radialmonster--f1-initial-results.md): First measurements of the token structure in compressed ORFs, still without a reproducible script.

**V2/**
none yet

**unassigned/**
- [additional-established-facts](unassigned/2026-10-18--radialmonster--additional-established-facts.md): Further bit-level facts about the token stream beyond F1, each with how strongly it is supported.
- [ruled-out-layouts-and-framing](unassigned/2026-10-18--radialmonster--ruled-out-layouts-and-framing.md): Row, header and escape layouts that were tested and are not supported.
- [ruled-out-predictors-and-transforms](unassigned/2026-10-18--radialmonster--ruled-out-predictors-and-transforms.md): Predictor, transform and integration loops that did not give an image-like result.
- [ruled-out-value-mappings](unassigned/2026-10-18--radialmonster--ruled-out-value-mappings.md): Ways of reading the token fields as a number that did not give an image-like result.

## Folders
- [`container/`](container/): facts about the file container, or that span variants
- [`V0/`](V0/), [`V1/`](V1/), [`V2/`](V2/): bitstream findings for that variant (see [VARIANTS.md](../VARIANTS.md))
- [`unassigned/`](unassigned/): bitstream findings whose variant isn't known yet

A new variant gets a new folder `V<n>` with a README, added together with its section in VARIANTS.md.

## File name and ID
`YYYY-MM-DD--handle--short-slug.md`, for example `2026-10-18--alice--f2-on-seven-bodies.md`.

- Double hyphens separate the three fields. GitHub handles can't contain `--`.
- The slug is lowercase letters, digits and single hyphens.
- The finding's ID is the file name without `.md`.
- `Alias:` (`F1`..`F4`) exists only on the first four findings. New findings don't use it, and CI rejects any other alias.

## Format

    # <title>

    Author: @handle
    Submitted by: @handle
    Variant: container
    Builds on: F2, 2026-10-18--alice--some-finding
    Reproduces: <ID>
    Corrects: <ID>

    ## Claim
    What you found, in plain sentences.

    ## Evidence
    The tools/ script and its last commit, and the files by raw.pixls.us id + SHA-256
    (or `own` + SHA-256), with the numbers.

    ## Reproduce
    The exact commands.

- `Author:` is required and must match the handle in the file name. Add only your own work under your own handle.
- `Submitted by:` only when you add someone else's result (for example from a Discussion). The author stays the one who found it.
- `Variant:` is required and must match the folder: `container`, `V0`, `V1`, `V2`, `unassigned`, ...
- Don't put the RULES.md sign-off or the clean-room declaration in the file; they go in the pull request description (the PR template has them).
- `Builds on:`, `Reproduces:` and `Corrects:` are optional. Each is a comma-separated list of finding IDs (`F1`..`F4` also work, see above). Delete the lines you don't use.
- Evidence: numbers come with the `tools/` script that produced them. Results that rest only on `own` files are marked `not yet reproducible` (RULES.md, "Data").

## Rules
- An existing finding file is never edited, renamed or deleted, by anyone. CI rejects it.
- To correct or retract a finding, add a new file with `Corrects: <ID>` that says what was wrong.
- Findings are about the files and bitstream, with the clean-room rules of [RULES.md](../RULES.md).

## Status comes from peer validation
Nobody needs a maintainer's sign-off.

- **lead**: no finding by a different author reproduces or corrects it yet.
- **reproduced**: a finding by a different author lists it in `Reproduces:`. That means you ran the same checks, preferably on other files, and got matching results.
- **disputed**: a finding by a different author lists it in `Corrects:`.

If your results don't match, don't write `Reproduces:`. Write a finding with `Corrects:` and show your numbers. Reproducing your own finding doesn't change its status.

See the current state with:

    python tools/findings_index.py           # per variant: ID, author, title, status
    python tools/findings_index.py --check   # validate every file (CI runs this)
