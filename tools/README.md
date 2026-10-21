# tools

Analysis scripts, all original code (see RULES.md).

Each script should:
- take raw.pixls.us file paths as arguments and not download anything itself (`pixls_samples.py` is the one exception);
- print or write aggregate statistics only, with no images or pixel dumps;
- run on CPU, with GPU acceleration optional;
- state at the top which finding (an ID from `findings/`), lead issue (`#n`) or spec Gap (`specs/V<n>.md`) it supports.

**`suffix_window_probe.py`** supports lead #11's remaining local-extent question.
Four consecutive 262144-candidate-token windows report all H/L pair tables and
plug-in MI at lags 1..3, with endpoint escape omissions preserving indices.
Pairs stay inside windows; intervening escapes remain. Every cell and the
strict alternating-order criterion are reported, including null/short windows.
These descriptive token-index windows are not physical rows, a stationarity
test, historical reproduction or decoder. Unknown framing remains unresolved.
Reuse retained CC0 provenance after verifying the exact input hash.

    python -I -B tools/suffix_window_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_suffix_window_probe.py

## Example tools

**`token_framing_probe.py`** is the corrected null comparison for lead #197,
building on the superseded probe in #198. Bernoulli bits use the measured ones
fraction as their success probability; density is preserved in expectation.
Byte shuffling preserves the exact byte histogram. Separate zero/one run-length
shuffles retain alternating values and exact per-value maximal-run multisets.
Output is aggregate JSON with exact counts, all input outcomes and a completion
flag; any failed input exits nonzero. Short residuals and null separation do not
establish true codec boundaries. Reuse retained CC0 records after local hash checks.

    python -I -B tools/token_framing_probe.py --sample ID PUBLIC_NAME path/to/file.ORF --bytes 131072 --seed 20261021
    python -I -B tools/test_token_framing_probe.py

Optional `--markov` adds a first-order binary Markov null fitted to adjacent-bit
counts of that same prefix, without wraparound or pseudocounts. The initial bit
uses its measured ones fraction; each following bit uses the fitted conditional
probability given the previous generated bit. An unobserved outgoing state falls
back to the measured ones fraction. Exact fit counts and fitted probability
estimates are reported.
This fitted probabilistic control does not exactly preserve finite density,
transitions or run histograms, or establish input stationarity or calibrated significance.
The default four-model report is unchanged.

    python -I -B tools/token_framing_probe.py --markov --sample ID PUBLIC_NAME path/to/file.ORF --bytes 131072 --seed 20261021

Optional `--local-byte-block 256` adds byte shuffling separately inside
consecutive fixed-size prefix blocks, including any short final block. A fresh
seeded generator is consumed in block order. Each block's exact byte histogram
and density are preserved, while within-block order, bit adjacency and maximal
runs are not. Output includes block size, complete-block count and tail bytes.
The default report is unchanged. These diagnostic blocks are not physical rows;
the assumed local permutation model does not calibrate significance or identify
camera framing. It can be combined with `--markov`.

    python -I -B tools/token_framing_probe.py --local-byte-block 256 --sample ID PUBLIC_NAME path/to/file.ORF --bytes 131072 --seed 20261021

**`terminal_residual_null_probe.py`** supports lead #87 with finite iid
Bernoulli residual-length distributions for independently anchored first/last
4096-bit payload windows. It reports the complete PMFs, nonempty all-one
residual probabilities, observed candidate counts and every input failure.
The fair and in-sample fitted baselines are descriptive, not calibrated
significance tests. Tail-window anchors do not reproduce whole-payload
endpoints or decide padding versus a truncated token. Reuse retained CC0
verification after matching the exact local hash.

    python -I -B tools/terminal_residual_null_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_terminal_residual_null_probe.py

**`e400_single_pass_probe.py`** supports the remaining exception in #79.
It marks nonzero-low4 words and tests connected same-colour neighbour
components of size one or two, excluding whole components touching a
two-pixel boundary. Equal coordinate parity uses diagonal-1; unequal uses
axial-2. For increasing/decreasing raster orders, each marked word is
replaced once by the floor four-neighbour mean; initial marked words must
be uint16 multiples of 16 and unmarked words are fixed. For a pair it
inverts the earlier equation and replays every admissible later-site
initial word. Reports contain aggregate equations, candidates, replays,
components and exclusions only. Known public values motivated the model.
Compatibility does not establish actual camera order, sensor values or
universal correction rules; zero-low4 mapped sites, edges and larger
components remain untested. Reuse verified CC0 provenance after matching
the local hash; new content needs its first licence verification.

    python -I -B tools/e400_single_pass_probe.py path/to/E400.ORF
    python -I -B tools/test_e400_single_pass_probe.py

**`e400_exception_probe.py`** supports lead #79 and `specs/V0.md` G3.
It scans a licence-checked packed-16 input in TIFF byte order and tests every
nonempty subset of the axial-2 and diagonal-1 neighbour families under floor,
ceiling and nearest-half-up means. Output contains aggregate counts by low
nibble, edge exclusions, and residual tests for words unmatched by either
full-family floor mean. It also tests clearing neighbour low nibbles; no
pixel values, neighbourhood arrays or images are printed. Subset matches
are descriptive and do not establish the camera's processing order.

    python -I -B tools/e400_exception_probe.py path/to/E400.ORF
    python -I -B tools/test_e400_exception_probe.py

**`suffix_match_probe.py`** supports lead #31 with exact suffix-equality counts
against independent within-block permutations that preserve escape positions.
It prints aggregate JSON, with every declared lag and explicit sample failures.
The frozen discovery and validation cohorts are in `tools/cohorts/`; later files
use a separate `replication` cohort with the same design metadata. Local paths
are supplied separately and never appear in output. This bounded descriptive
measure cannot establish or exclude dictionary coding. Synthetic exhaustive
permutation tests run with `python -I tools/suffix_match_probe.py --self-test`.

    python -I tools/suffix_match_probe.py --cohort PUBLIC_COHORT.json --measured-by @yourhandle --sample ID path/to/file.ORF

**`pixls_samples.py`** lists, checks and downloads raw.pixls.us Olympus/OM samples using the site's licence listing. It downloads CC0 files only and verifies SHA-256. See the top-level README.

**`manifest_rows.py`** turns local CC0 files into ready-made `samples/manifest.csv` rows, combining the licence listing with `orf_signature.py`.

**`orf_signature.py`** prints one CSV row per file with its measured container and payload facts: SHA-256, magic, make, model, payload size, bits per sample, compression tag, payload offset and bytes, and bits per pixel. It reads the TIFF structure only and decodes nothing.

    python tools/orf_signature.py path/to/* > rows.csv

**`conformance.py`** runs the reference decoder (`decoder/orf_decode.py`) on files and prints per file the input SHA-256, packing, size, bytes consumed vs payload size, min/max, out-of-range count (for packed-16: words with a non-zero low nibble), smoothness and the output hash, then a summary. `--csv` gives the `samples/conformance-V0.csv` format. Supports ROADMAP.md.

    python -I tools/conformance.py path/to/*

**`test_orf_decode.py`** round-trip tests of the decoder on synthetic bytes: `python -I tools/test_orf_decode.py`.

**`bit_runs.py`** gives a histogram of zero-bit runs in the payload (MSB-first), as aggregate numbers. It's a starting point for bitstream work (the F1 lead, #11).

    python tools/bit_runs.py path/to/file.ORF --mb 1

Example output on raw.pixls.us `8549_OM System - OM-5 Mark II - 16bit (4_3).ORF` (CC0), first 1 MB:

    q= 0  share=0.48036
    q= 1  share=0.27349
    q= 2  share=0.13019
    q= 3  share=0.06272

**`orf_tokens.py`** parses the token stream described in lead #11 (q zero bits, stop bit, 5-bit suffix; escape at q >= 17) and prints aggregate statistics per file: tokens against width x height, bit alignment at multiples of the width, q histogram and escapes, suffix bit balance, H/L bit-group shares, the ones-density with the tokens per pixel a Bernoulli (independent-bits) null predicts next to the measured value, correlation of min(q,8) at token lags 1, 2, 3, 6 and the row stride, and mutual information at token lags 1-3 (H->L, L->H, L->L, H->H), the b2 context gain and vertical lag 2, each with a baseline that shows the estimator bias. Numbers are printed as measured, whether or not they match that lead. It parses a prefix by default (`--max-tokens`, `--rows`); `--all` parses the whole payload. `--escape-landing` tabulates, per escape q, where the stream re-synchronises (distance modulo 6) after each escape. H = b4b3 and L = b2b1b0 are only labels for bit groups; no signed or other meaning is assumed.

    python tools/orf_tokens.py path/to/file.ORF --rows 400
    python tools/orf_tokens.py path/to/file.ORF --all

**`jpeg_dc.py`** decodes only the DC coefficient of each 8x8 block of a
baseline JPEG, for the first (luma) component. For an ORF it finds the largest
embedded preview (width and height at least 1000). On the E-M1 Mark II files the
3200x2400 preview gives a 400x300 luma grid. AC coefficients are skipped; no
image or pixel data is written. Standard library only. Supports the P0
token-to-luma probe and the geometry part of lead #11.

    python -I tools/jpeg_dc.py path/to/file.ORF

**`token_luma_probe.py`** tests a fixed token-field to low-resolution luma
mapping against a within-row suffix permutation. The default `--map sum` takes
`v = b2 + b4`; `--map b2` and `--map b4` select that bit alone. Every map
zeroes escape markers, box-averages `v` over `--window` tokens within each row,
block-averages to the preview's luma DC grid, and correlates the row-centred
grids. The target comes from `jpeg_dc.py`; the null permutes the suffix tokens
within each row. It prints one aggregate line per file (`r`, shuffle mean and
sd, z, escape count). The default `--rows 300` is the top token band; a
full-frame reshape is not used because the token row stride can drift. This is
a low-frequency luma proxy, not a full pixel decode. The camera rendering is
a numerical sanity reference, not sensor ground truth. Marginal map rankings
do not establish unique bit contribution or significance. Test:
`python -I tools/token_luma_probe.py --self-test`.

    python -I tools/token_luma_probe.py path/to/file.ORF --rows 300 --window 63 --perms 20
    python -I tools/token_luma_probe.py path/to/file.ORF --map b2 --rows 300 --window 63 --perms 20
    python -I tools/token_luma_probe.py --self-test

**`token_value_probe.py`** supports leads #11 and #32 with band-wise
b2+b4 correlations, nominal versus whole-preview scale comparisons, column
statistics and fixed suffix-table transfer against numeric embedded-preview
luma DC. Rows are candidate token blocks at the payload width; physical row
boundaries and escape framing remain unresolved. The table measures a weak
statistical correlate, not sensor values, a predictor or a round-trip decode.
Within-row shuffles are descriptive; a four-shuffle z is not calibrated
significance. Licence-check the public training and test inputs first.

    python -I -B tools/token_value_probe.py --self-test
    python -I -B tools/token_value_probe.py table --train PUBLIC_TRAIN --test PUBLIC_TEST --rows 600 --mode s --lam 1 --smooth 10 --perms 4

**`value_map_probe.py`** (by @mtakemoto) measures suffix bridge energies under the three candidate suffix mappings from lead #32, against an exact permutation null, in 128-token blocks of the #11 parse. It is a frozen, pre-registered experiment: the sample IDs per phase (`discovery`, `validation`) and the settings are fixed on purpose, so it reruns that one design rather than measuring arbitrary files. It prints aggregate JSON only. `--self-test` runs its tests.

    python tools/value_map_probe.py --phase discovery --measured-by @yourhandle --sample 1993 NAME path/to/file.ORF

**`value_map_window_probe.py`** supports the later-window control in lead #32.
It reuses @mtakemoto's suffix bridge-energy arithmetic and the original #11
candidate scanner, scanning from payload bit zero while retaining only the
requested window. Start tokens must be multiples of 128; reported block indices
and lane parity are absolute. Each window holds at most 262144 tokens, and the
scan ends by token 100000000. It emits explicitly exploratory aggregate JSON,
source hashes, measured signature, absolute token/bit boundaries and escape
omissions. Licence-check samples first. The frozen six-file prefix experiment
is unchanged; later windows do not repair potential escape misalignment or
establish a decoder, physical row boundaries, or content/code causation.

    python -I -B tools/value_map_window_probe.py --sample ID PUBLIC_NAME path/to/file.ORF --measured-by @yourhandle --start-token 1048576
    python -I -B tools/test_value_map_window_probe.py

**`orf_v0_unpack.py`** scores candidate bit layouts for the uncompressed V0 files (`packed-12`, `packed-12.8`, `packed-16`, lead #28) on a small window of each file: value range, smoothness at same-colour horizontal and vertical distance 2 against distance 1, row correlation, and a row-stride test for the chosen layout. Text statistics only; it prints the layout with the lowest roughness and the margin to the next one.

    python tools/orf_v0_unpack.py path/to/file.ORF

**`layout_probe.py`** supports lead #77 by measuring strip gaps, stored-row
discontinuities, and natural versus two-field row-order scores over 400 centre
columns. By default it scores about 200 interior rows; `--all-rows` scores every
interior row, excluding the same boundary margins. Gap detection, pairing and
shift-curve sampling are unchanged. Output includes the scoring row counts.

    python -I tools/layout_probe.py --all-rows path/to/file.ORF

**`findings_index.py`** lists the verified findings under `findings/` by variant, with finder, verifier, title and status (verified or superseded). `--check` validates the files (file name, `Author:` matches the handle, `Verified by:` is another person, `Lead:` is `#n`, `Variant:` matches the folder, referenced IDs exist) and exits 1 on errors; CI runs it on pull requests.

    python tools/findings_index.py
    python tools/findings_index.py --check

**`trailing_ones_probe.py`** measures literal trailing one-bit counts for the
frozen full cohort in lead #87. It matches regular input files by streamed
SHA-256 regardless of filename or extension; duplicate cached copies count
once. It reuses `orf_signature.signature()` and the original
`orf_tokens.locate()` contiguous locator, checks their dimensions and payload
length agree, and requires `size_class=variable` and `compression_tag=1`.
Tag 1 alone does not distinguish fixed-size from compressed ORF payloads.
The frozen cohort has one strip per payload: this tool is not a generic parser
for separated strips.

The final byte, final eight bytes and whole payload are counted independently.
The tool checks that the two shorter counts equal `min(full, 8)` and
`min(full, 64)`; it makes no padding, token-end or decoder inference.
Measurement mode prints one JSON object containing public sample measurements,
sanitized failure categories, exact cohort-file and source hashes, and summary
histograms named `histogram_last_byte`, `histogram_last_eight_bytes` and
`histogram_full_payload`. Successful samples remain in frozen cohort order
when another required input fails; any failure returns a nonzero exit status.
No local paths or raw bytes appear in measurement output.

`--help` works alone. `--self-test` works alone and loads the independent
`test_trailing_ones_probe.py` unittest suite. Measurement mode requires all
three flags shown below.

    python -I tools/trailing_ones_probe.py --help
    python -I tools/trailing_ones_probe.py --self-test
    python -I tools/trailing_ones_probe.py --cohort tools/cohorts/lead87-trailing-ones-v1-full.json --sample-dir /path/to/samples --measured-by @yourhandle

**`byte_boundary_tail_probe.py`** supports lead #87 with an empirical reference
for trailing-one runs at every payload byte boundary, including cross-byte
runs. It compares the final run with all earlier boundaries in that same
payload, retaining full histograms, ties and exact ratio denominators. Empty
payloads reject; one-byte payloads have no earlier-boundary fractions. These
are descriptive frequencies, without endpoint exchangeability, significance,
padding, token-framing or decoder inference. Match local hashes to retained
CC0 verification before running; new content needs first verification. The
CLI retains successful samples and sanitized errors, exits nonzero for any
failure, and prints aggregates only. Stdlib; no sample data is written.

    python -I -B tools/byte_boundary_tail_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_byte_boundary_tail_probe.py

All of them use the standard library only (Python 3.8+). Contributions of new tools are welcome. Follow the rules above and RULES.md.

**`token_bit_chain_probe.py`** supports lead #29 item 4 and builds on #11.
It reports all four ordered b2/b4 bit-pair tables at lags 1..5, plug-in MI,
Pearson correlations and every fixed-seed within-block whole-token permutation
comparison. The fixed prefix contains at most 262144 complete tokens; whole
128-token blocks containing escapes and incomplete tails are omitted. Pairs
stay within retained blocks, which are not established camera rows. This is
descriptive pairwise dependence, not the historical multivariate conditional
chain, held-out gains, significance, a deeper law or a decoder. Licence-check
samples first; failures are sanitized and other sample reports retained.

    python -I -B tools/token_bit_chain_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_bit_chain_probe.py

**`v0_spec_check.py`** is an independent, aggregate-only implementation of
`specs/V0.md` at `bf56d39`, supporting lead #75. Original payload logic and
synthetic tests were written without target files, reference code, or output
hashes. Shared container code is limited to `orf_signature.Tiff` header/endian
and integer reads; an original wrapper validates relevant IFD descriptors.

    python -I tools/v0_spec_check.py --help
    python -I tools/v0_spec_check.py --self-test
    python -I tools/test_v0_spec_check.py
    python -I tools/v0_spec_check.py --measured-by @yourhandle --sample ID PUBLIC_NAME path/to/file.ORF

Repeat `--sample` for multiple files. IDs are distinct positive decimals; public
names may repeat. Match records by input SHA-256, never basename. Check CC0
licensing before supplying downloaded files. Each JSONL result includes public
identity, input/output hashes, measured signature, aggregates, selectors, source
hashes and pinned spec metadata. Failures emit sanitized categories, preserve
other results and return a nonzero exit code. No decoded data is written.

Selectors are **unverified spec generalizations**: packed-12 `IIRS` is plain,
`IIRO` reverses global four-byte words; no strip gaps means natural rows; one
packed-12 gap at the even-field boundary means two fields; packed-16 uses TIFF
byte order. Unsupported cases fail without trying alternatives. First/second
unit order is a convention, not physical pixel-order proof. The S4.3/S6 wording
ambiguity is resolved by preserving packed-16 stored words with **no numeric
shift**, including low nibbles. Above-4095 and nonzero-low-nibble counts are
separate measurements. Hashing uses explicit uint16 little-endian image rows.

Read-only mmap, individual strip reads, strict integer size classification and
row streaming are bounded by 8 GiB per file, 100,000 per dimension, 250,000,000
pixels, 4,096 IFDs and 1,000,000 strips. Malformed relevant fields, tied largest
IFDs, repeated pointers, overlaps, nonascending strips and unsupported gaps are
rejected. Report mismatches under these frozen assumptions; do not tune them to
expected hashes.

Input opening uses `os.O_NONBLOCK` where the platform has it: the acquired
descriptor is checked with `fstat` before any mmap/read, so a FIFO without a
writer is rejected promptly and later inputs still run. Where the flag is missing
(Windows), a non-regular path is refused by `os.stat` before opening, and the
opened descriptor is still checked with `fstat`. Descriptors close on success
and failure. Symlinks to regular files remain usable. `--help` and `--self-test`
are portable; the FIFO test skips where FIFOs or `O_NONBLOCK` are absent.

**`token_phase_probe.py`** supports the unverified token-phase part of lead #30
and builds on candidate parse #11. It reports every modulo-2..8 contingency
table between absolute token phase and joint suffix symbol `2*b4+b2`, together
with plug-in symbol entropy, phase-conditional entropy and mutual information.
The fixed prefix is 262144 complete tokens; escapes (`q>=17`) are omitted
without compacting indices, with zero extra escape bits. It requires a single
in-bounds variable-size strip and prints aggregate JSON with sample hashes,
measured dimensions, prefix shortfall, source hashes and sanitized failures.
Licence-check downloaded samples first. This descriptive metric has no bias
correction, significance threshold or physical column interpretation; it does
not reproduce the historical conditional-context gain or private figures.

    python -I -B tools/token_phase_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_phase_probe.py

**`exif_sensitivity_probe.py`** supports the remaining ISO-setting question in
lead #106. It reports raw numeric Exif PhotographicSensitivity (0x8827) values
from the primary IFD's ExifIFD pointer alongside measured signatures. Missing
values remain absent; 65535 is flagged as a possible sentinel requiring extended
tags. It reads no maker notes, GPS, serials or preview pixels. It does not test
ISO/bpp correlation, scene content, or causality. Licence-check inputs first.

    python -I -B tools/exif_sensitivity_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_exif_sensitivity_probe.py

**`token_lag_probe.py`** supports lead #29 item 6 and builds on #11 and
`suffix_joint_probe.py`'s bounded candidate scanner. In the first 262144 tokens,
it keeps complete 128-token blocks without q>=17, forms only within-block
pairs, and reports q>0 and low-three-suffix-symbol plug-in MI at all lags 1..5.
It emits exact contingency counts, 16 fixed-seed within-block whole-token
permutation MI values, selection counts, source/input hashes and sanitized
per-sample failures. Blocks are not established camera rows; comparison values
are descriptive, without a significance test. This different metric does not
reproduce #29's historical private held-out/smoothed estimates or establish
stationarity, magnitude meaning or a decoder. Check CC0 licences first.

    python -I -B tools/token_lag_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_lag_probe.py

**`token_scale_probe.py`** supports lead #29 item 7 with held-out binary-q
prediction from lag1 and preceding 8/16-token positive-q counts. It reports
exact training/test tables, losses, signed gains against frequency and lag1,
unseen contexts and all sixteen within-block permutation comparisons.
Original even/odd 128-token blocks define the split; escape-containing blocks
and incomplete tails are omitted. Blocks are not physical rows, adjacent
split blocks may depend, and omission does not repair unknown framing.
These descriptive scores do not reproduce historical q-entropy estimates or
establish significance, a codec scale law or a decoder. Check CC0 licences first.

    python -I -B tools/token_scale_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_scale_probe.py

**`token_context_probe.py`** supports the held-out multivariate context step
for lead #29 item 4, building on #11 and the bounded `suffix_joint_probe.py`
scanner. Six fixed binary models use common within-block targets, Jeffreys
smoothing and original even/odd block training/test splits; escape-containing
blocks and incomplete tails are omitted. It reports exact train/test tables,
absolute held-out log-loss, nested gains, unseen-context counts and all sixteen
within-block whole-token permutation comparisons. Adjacent blocks can remain
dependent, and blocks are not camera rows. These descriptive transfer scores
do not reproduce historical private estimates or establish a conditional law,
significance or a decoder. Check CC0 licences before measurement.

    python -I -B tools/token_context_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_context_probe.py

**`token_zero_runs_probe.py`** supports the remaining b2 zero-run question in
lead #30 and builds on #11's candidate parse. In the first 262144 complete
tokens it splits at every q>=17 escape, omits that token, and counts maximal
positive-length b2 zero runs bounded by ones within a retained segment.
Leading, trailing and all-zero-segment censoring are reported separately.
It emits the full run histogram, integer moment sums, population moments and
the fitted positive-geometric variance `mean*(mean-1)`. This is descriptive,
without a fit/significance test, physical-row or run-copy interpretation.
Historical private figures have unspecified run-support/censoring definitions
and are not reproduced. Escape omission does not repair uncertain framing.
Outputs are aggregate JSON with hashes and sanitized per-sample failures;
licence-check samples first.

    python -I -B tools/token_zero_runs_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_zero_runs_probe.py

Optional `--start-token N --tokens K` selects K candidate tokens starting at
absolute token index N, counting escapes. Parsing always starts at payload
bit zero; only the selected window is retained in memory. Each window censors
both edges independently. Reports include skipped tokens/escapes, start and
length shortfalls, absolute start/end bit positions and selected-window bit
length. `prefix_shortfall` is retained as an alias of `token_shortfall` for
older consumers. Untouched windows can expose within-file variation but do
not establish stationarity, representativeness or a geometric law.

    python -I -B tools/token_zero_runs_probe.py --start-token 1048576 --tokens 262144 --sample ID PUBLIC_NAME path/to/file.ORF

**`escape_balance_probe.py`** supports the remaining b1/b0 suffix-balance
question in lead #11. In the fixed first 262144 complete candidate tokens,
it splits ordinary tokens strictly before versus after the first q>=17,
excluding every escape. Exact suffix histograms and b4..b0 one-counts are
reported, including empty groups, prefix shortfalls and sanitized failures.
No first escape means all ordinary tokens are in the before group. Framing
following an escape remains unknown; scene variation and unequal group sizes
prevent a causal interpretation. This new descriptive metric is not a
reproduction of historical private numbers. Check CC0 licences first.

    python -I -B tools/escape_balance_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_escape_balance_probe.py

**`token_width_lag_probe.py`** supports the nominal-width-lag part of lead #29
item 8, building on #11 and the bounded `suffix_joint_probe.py` scanner.
It reports exact binary tables and Pearson correlations at W, 2W, 2W-2,
2W+2 (past/current b2) and 2W-1 (past b4/current b2), pooled and by all four
target nominal-grid parity strata. W is measured payload width, not an
established token row stride or sensor/CFA grid. In the first 262144 complete
tokens it omits pairs with q>=17 at either endpoint without renumbering;
intervening escapes remain. Every candidate, omitted and retained pair count
is reported; empty/zero-variance correlations are null. These descriptive
aggregates do not reproduce historical private figures or establish donor
structure, parity invariance, significance or a decoder. Check CC0 licences first.

    python -I -B tools/token_width_lag_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_width_lag_probe.py

**`q_value_bridge_probe.py`** supports lead #32 with a preview-free bridge
metric for the q-inclusive readings `u=32*q+s` and `zigzag(u)`. It builds on
@mtakemoto's exact permutation-mean bridge design (#64) and #11's candidate
parse; PR #159 tests the same readings with a different predictor/preview
score. All four mapping/lane-count cells, exact block A/V terms, pooled
energies, separate absolute-parity pools and omissions are emitted. The fixed
262144-token prefix uses complete 128-token blocks, omitting whole blocks
containing q>=17 and the incomplete tail. No escape skip is added. Ratios
are sums of energies divided by sums of observed-multiset permutation means,
not averages of ratios or significance tests. Degenerate ratios are null.
Blocks and token parity are not physical rows/channels; omission cannot
repair unknown framing. Detrending removes drift, so these measurements
cannot establish a bounded reconstruction or reproduce historical private
growth figures. Licence-check public inputs first. Failed samples are
sanitized; successful reports survive and any failure makes the exit nonzero.

    python -I -B tools/q_value_bridge_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_q_value_bridge_probe.py

**`token_position_probe.py`** supports the still-open item 9 of lead #29,
building on #11 and `suffix_joint_probe.py`. It reports ordinary-q (0..16)
and unsigned-suffix (0..31) histograms at nominal positions 0..23 and the
remainder, plus pooled first10/first24/remainder counts, sums and means.
Only complete payload-width W-token rows from token0 contribute; q>=17
symbols are omitted without compacting indices. All escape omissions and
incomplete nominal-tail counts are explicit. W and origin are hypotheses,
not established physical rows; omission cannot repair unknown escape framing.
The historical row-start statistic did not specify its field/estimator, so
these new explicit metrics do not reproduce its values. No elevation criterion,
null model, significance or decoder is supplied. Check CC0 licences first.

    python -I -B tools/token_position_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_position_probe.py

**`token_b4_gate_probe.py`** supports the b4 significance-gate question in
lead #32 and builds on candidate parser #11. It emits complete low3/low4
unsigned histograms by b4, current-q/current-b4 and previous-q/current-b4
17-by-2 count tables, conditional probabilities and unsmoothed plug-in MI.
The first 262144 complete tokens use zero extra escape bits; q>=17 tokens
are omitted, with both endpoints required ordinary for lag1 pairs. Original
indices are preserved; omitted tokens are never joined. Both low-bit field
definitions are explicit because the historical phrase was unspecified.
No significance, independence, semantic gate or historical-number claim
follows; omission cannot repair unknown framing. Licence-check inputs first.

The b4-gate probe's optional `--q-stratified` flag adds exact within-q
low3/low4 contrasts and each file's equal-weight summary over its reported
support. Sparse strata and differing support limit comparisons. Missing files
or token-prefix shortfalls exit nonzero while retaining aggregate records.

    python -I -B tools/token_b4_gate_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_b4_gate_probe.py

**`suffix_width_probe.py`** supports the committed candidate k-scan requested
in V1 G8 and relates to lead #29 item 1. For each whole payload it reports
all k=2..8 and both stop-bit conventions: q opposite bits, one stop bit,
then k skipped suffix bits. Only complete tokens count; q>=17 has no extra
skip. Exact q histograms, escape counts, consumed/unconsumed lengths and
tokens per measured payload pixel are emitted. There are no row delimiters
or neighbour-dependence measures. Small residuals or near-one token ratios
do not establish the correct grammar, padding or a decoder. Single-strip
variable-size inputs with compression tag 1 are required; input size is
limited to 512 MiB. Failures are sanitized and successful samples retained.
Check CC0 licences first. Original scanner, stdlib only, aggregates only.

    python -I -B tools/suffix_width_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_suffix_width_probe.py

Optional `--block-tokens 262144` adds exact q0-count histograms over complete
fixed-size candidate-token blocks and separate tail counts, supporting the
within-file framing question in #197. The default output is unchanged. Blocks
under different grammars cover different bit intervals; a high q0 share or its
variation cannot select a true code or establish adaptation. All candidate
tokens, including q>=17, contribute; there is no fitted offset or escape skip.

    python -I -B tools/suffix_width_probe.py --block-tokens 262144 --sample ID PUBLIC_NAME path/to/file.ORF

**`token_affine_probe.py`** supports the untested GF(2) part of lead #29
item 4, building on #11 and #166/#169. It tests exact affine prediction of
current b2 and b4 from both bits at lags 1..12, with an intercept. All six
pooled/even/odd-target systems report context and target-augmented ranks.
The first 262144 complete candidate tokens use zero extra escape bits;
any 13-token context-plus-target window containing q>=17 is omitted without
compacting indices. A rank increase excludes only an exact affine predictor
of this context on these observed selected rows. It does not exclude noisy,
nonlinear or longer-context laws, identify a scrambler or physical rows,
reproduce historical private ranks, or decode. Escape omission cannot repair
uncertain framing. Check CC0 licences first. Stdlib, aggregate output only.

    python -I -B tools/token_affine_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_affine_probe.py

Every affine sample now reports `prefix_complete`. Incomplete requests retain
all selected-row diagnostic ranks/consistency but make the CLI exit nonzero;
those verdicts cover only observed rows. Failed public identities appear
in `failures`, with sanitized exception classes, while valid
reports remain in `samples`. Any input failure also exits nonzero. Every ID
is validated before reading samples. Existing complete-prefix ranks/counts
are unchanged. Reuse retained CC0 verification after matching the local hash.

**`suffix_width_lag_probe.py`** follows the neighbour-dependence question after
the candidate width scan (#29, V1 G8). All k=2..8 and stop=0,1 grammars use
their first 262144 complete tokens and zero extra escape skip. All lags1..5
report exact q-positive 2x2 and fixed low-two-suffix-bit 4x4 tables and
unsmoothed plug-in MI, omitting only q>=17 endpoints without compacting
indices. Intervening escapes remain; omission cannot repair unknown framing.
Reports include endpoints, shortfalls, omissions, public/source hashes and
sanitized failures. Equal alphabets do not remove finite-sample, marginal
or selection bias: MI does not rank/select grammars. No null, significance,
physical rows, historical private-value reproduction or decode is claimed.
Licence-check public inputs first. Stdlib, reads files/prints aggregates only.

    python -I -B tools/suffix_width_lag_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_suffix_width_lag_probe.py

Optional `--block-rotation-control` adds a separate matched descriptive
control for #29/V1 G8. Complete 128-token blocks from token zero are kept
only when every q<17; incomplete tails are excluded. At lag L=1..5, M=128-L
donors at indices 0..M-1 pair with fixed targets L..127. The control rotates
these M donor tokens by floor(M/2), modulo M. Both observed and control
tables therefore have identical donor/target marginals in each block and
pooled. Exact q-positive and low2 suffix tables, MI, signed observed-minus-
control differences and selection counts are reported for every grammar.
The default endpoint-only report stays unchanged. Whole-block selection
differs from that default. This single deterministic rotation preserves
block mixtures but can retain longer dependencies; it is not a null
distribution, significance test, unbiased correction or grammar selection.
Blocks are not physical rows and omission cannot repair escape framing.
Reuse retained CC0 verification after matching the local hash; new content
needs its first licence verification. Reports contain aggregates only.

    python -I -B tools/suffix_width_lag_probe.py --block-rotation-control --sample ID PUBLIC_NAME path/to/file.ORF

`token_phase_context_probe.py` also emits a separate `heldout` report for
lead #30. Complete 128-token blocks containing any q>=17 and the incomplete
tail are omitted. Original even-index blocks train; original odd-index
blocks test. Each retained block contributes local targets 2..127, so no
source triple crosses a split boundary. The fixed target/context are
Y=b2(t), C=2*b4(t-1)+b2(t-2); phase is the absolute index modulo m=2..8.
For identical held-out targets it compares Jeffreys-smoothed binary
P(Y|C) with P(Y|C,phase), emitting full train/test tables, denominators,
unseen-training-context counts, both log losses, and signed baseline-minus-
phase gains. Negative gains are retained. Absent training data predicts 0.5
with null gain; absent test data gives null loss/gain. This whole-block
selection differs from the earlier triple-wise plug-in tables, which remain
unchanged. Adjacent blocks may remain dependent; these descriptive scores
are not unbiased estimates, significance/null calibration, historical
private-gain reproduction, physical columns or a decoder. Excluding escapes
cannot repair unknown framing. Reuse prior CC0 verification after checking
the local file hash against its verified record; new content needs its first
licence verification.

    python -I -B tools/token_phase_context_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_phase_context_probe.py

**`token_band_profile.py`** supports lead #144's later-band question with
fixed candidate strides and absolute boundaries r*S from token zero. Each
300-row band reports exact capped-q contrast moments, signed mean/SE,
escape counts and incomplete-band accounting. Zero variance gives a null
score, retaining its signed mean. No stride search or phase refit occurs.
The default starts are candidate-row ordinals 0, 1000 and 2000, not physical
rows. Changing profiles can reflect content, phase or framing; they do not
establish stride drift, significance or a decoder. Candidate unary-plus-five
parsing keeps q>=17 with zero extra skip and caps q at 40. Reuse retained CC0
verification only after matching the supplied public SHA-256; the hash is
checked before parsing. Every supplied sample identity survives failures,
with a nonzero exit for any failure or shortfall. Reads/prints aggregates only.

    python -I -B tools/token_band_profile.py --sample ID PUBLIC_NAME VERIFIED_SHA256 path/to/file.ORF --stride 5240 --stride 5472
    python -I -B tools/test_token_band_profile.py

**`token_phase_surrogate_probe.py`** adds a separate conditional phase-offset
comparison for #30, Builds on #11/#203/#211. It preserves the fixed 262144
candidate-token prefix, 128-token whole-block escape selection, original
even-block training/odd-block test split, local targets 2..127, context
C=2*b4(t-1)+b2(t-2), and target Y=b2(t). Every modulus 2..8 gets sixteen
surrogates: independently add a uniform offset 0..m-1 to all phase labels
in each retained block, leaving context/target ordering and split fixed.
Random(20261021+replicate) is restarted for each modulus and consumed in
retained original-block order, including both splits. Full observed and
surrogate train/test tables, offset histograms, Jeffreys losses, signed
gains, and rank counts (<, =, > observed) are emitted. There is no inferential
p-value: exchangeability of these offsets is assumed for this diagnostic,
not established for actual ORFs. Adjacent blocks can depend and within-block
phase structure remains. The comparison does not repair framing, reproduce
historical private gains, establish physical columns or decode. Known-profile
smoke inputs are tool validation rather than untouched confirmation. Reuse
retained CC0 records only after matching the local SHA-256. Stdlib, reads
samples and prints aggregates only; missing inputs and shortfalls exit nonzero.

    python -I -B tools/token_phase_surrogate_probe.py --sample ID PUBLIC_NAME path/to/file.ORF
    python -I -B tools/test_token_phase_surrogate_probe.py

**`token_tail_distribution_probe.py`** supports #144's candidate extra-token
question, Builds on #11/#218/#234. At a fixed supplied stride S and measured
width W, T=S-W defines tail positions [W,S). Every complete candidate row
contributes exact uncapped q and five-bit suffix histograms to the tail,
first-width [0,W), preceding [W-T,W), and middle [S//2,S//2+T) regions.
Both comparison windows have T tokens and fit inside first-width; they can
overlap each other for some geometries. Histograms include q>=17, with zero
extra escape skip. Reports retain region counts, q sums, localized escapes,
entropies, tail-versus-comparison total-variation distances, all band
shortfalls, endpoints and source/input hashes. Incomplete final candidate
rows contribute no region statistics. Defaults are 300 candidate rows at
ordinal starts 0/1000/2000, with absolute r*S boundaries and no phase/stride
fit. Position comparisons are descriptive and not exchangeable nulls;
differences cannot identify padding, headers, a field, physical rows or an
actual entropy grammar. Unknown post-escape framing remains unresolved.
No significance, historical private-number reproduction or decode is
claimed. Reuse retained CC0 verification after matching the supplied hash,
which the tool checks before TIFF parsing. Every sample identity survives
sanitized failures; any failure or shortfall returns nonzero. Stdlib,
reads files/prints aggregates only.

    python -I -B tools/token_tail_distribution_probe.py --sample ID PUBLIC_NAME VERIFIED_SHA256 path/to/file.ORF --stride 5472
    python -I -B tools/test_token_tail_distribution_probe.py

**`token_cyclic_phase_probe.py`** supports the fixed-stride phase question in
lead #144 and builds on #11/#218. For each original S-token candidate row,
the head at phase p uses positions `(p+j) mod S` for j=0..head-1; the rest is
its complement. Every phase therefore uses identical tokens, including wraps
within the original row, rather than shifting contiguous row boundaries.
All phases report exact capped-q sums and contrast moments, signed mean/SE,
and all minimum/maximum ties. Phase zero equals `token_band_profile.py`.
Defaults are head 32, 300 candidate rows, ordinal starts 0/1000/2000.
Candidate unary-plus-five parsing retains q>=17, caps q40, and skips zero
extra escape bits. Reports retain shortfalls, sanitized failures, hashes and
public identities; any sample failure/shortfall gives a nonzero exit. Reuse
retained CC0 provenance after matching local SHA-256; new content requires
first verification. Selected phase extrema are descriptive, with no null,
calibrated significance, true-framing, physical-row or decoder inference.
They do not estimate later best strides or separate scene from framing.
Stdlib only; reads files and prints aggregate JSON, no token/pixel dumps.

    python -I -B tools/token_cyclic_phase_probe.py --sample ID PUBLIC_NAME VERIFIED_SHA256 path/to/file.ORF --stride 5240
    python -I -B tools/test_token_cyclic_phase_probe.py
