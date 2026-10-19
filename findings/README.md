# Findings

This folder holds **verified findings only**: results that someone other than the finder reproduced. Unverified results are *leads*, and leads are GitHub issues, not files.

Open leads: `gh issue list -R radialmonster/orf-cleanroom --label lead`, or https://github.com/radialmonster/orf-cleanroom/issues?q=is%3Aopen+label%3Alead

## How a lead becomes a finding
1. The finder publishes a lead issue (template: "Lead"). It stays an issue.
2. A different person reproduces it, preferably on other files than the finder used.
3. They open a PR that adds the finding file here, with `Author:` the finder, `Verified by:` themselves and `Lead:` the issue number. When it merges, the lead issue is closed as verified.
4. If the numbers do not match, nothing goes in this folder. The reproducer comments their numbers on the lead issue.

Files are independent, so there are no numbers to pick and no merge conflicts.

## Folders
- [`container/`](container/): facts about the file container, or that span variants
- [`V0/`](V0/), [`V1/`](V1/), [`V2/`](V2/): bitstream findings for that variant (see [VARIANTS.md](../VARIANTS.md))
- [`unassigned/`](unassigned/): bitstream findings whose variant isn't known yet

A new variant gets a new folder `V<n>` with a README, added together with its section in VARIANTS.md.

## File name and ID
`YYYY-MM-DD--finder--short-slug.md`, for example `2026-10-18--alice--tag-is-1-on-compressed-orf.md`.

- The date is the day of the verification PR. The handle is the **finder** (the lead's author), not the verifier.
- Double hyphens separate the three fields. GitHub handles can't contain `--`.
- The slug is lowercase letters, digits and single hyphens.
- The finding's ID is the file name without `.md`.

## Format

    # <title>

    Author: @finder
    Verified by: @reproducer
    Lead: #123
    Variant: container
    Builds on: 2026-10-18--alice--some-finding, #45
    Corrects: <ID>

    ## Claim
    What was found, in plain sentences.

    ## Original evidence
    The finder's tools/ script and commit, the files (raw.pixls.us id + SHA-256, or `own` + SHA-256) and numbers, as on the lead.

    ## Verification
    What the reproducer ran, on which files (preferably others), and the numbers they got.

    ## Reproduce
    The exact commands.

- `Author:` is required and must match the finder handle in the file name. `Verified by:` is required, is the PR author, and must be a different person.
- `Lead:` is the lead issue (`#n`) by the finder. It must exist and carry the `lead` label.
- `Variant:` is required and must match the folder.
- `Builds on:` and `Corrects:` are optional lists of finding IDs (or `#n` issues). Delete the lines you don't use.
- Don't put the RULES.md sign-off or the clean-room declaration in the file; they go in the PR description.
- Numbers come with the `tools/` script that produced them. Results that rest only on `own` files are marked `not yet reproducible` (RULES.md, "Data").

## Rules
- An existing finding file is never edited, renamed or deleted by anyone but the repo owner. CI rejects it.
- To correct a verified finding, add a new verified finding with `Corrects: <ID>` (it needs its own lead and a different verifier). The index then shows the old one as superseded.
- Findings are about the files and bitstream, with the clean-room rules of [RULES.md](../RULES.md).

## Status
- **verified**: the normal state of every file here.
- **superseded**: a later finding lists it in `Corrects:`.

    python tools/findings_index.py           # per variant: ID, author, verifier, title, status
    python tools/findings_index.py --check   # validate every file (CI runs this)
