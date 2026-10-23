# Cross-body, multi-seed q0 controls for lead #197

Part of #197. Builds on #198, #214 and #223, and the corrected-null finding
`2026-10-21--radialmonster--corrected-q0-null-definitions-and-separation`.
Measured by @radialmonster; same human as the earlier work, no independent
human verification, finding, correction finding or decoder change claimed.

The [predeclared scope](https://github.com/radialmonster/orf-cleanroom/issues/197#issuecomment-6322189583)
fixed all inputs, eight seeds and prefix length before the outcomes below.
1993 is a known reference. 6343 and 5283 are a cross-body extension reserved
before this run, already studied elsewhere in this repository; they are not
globally untouched samples. One selected file per body cannot establish a
body-wide result. No settings or offsets were selected after seeing outcomes.

## Method and inputs

Unchanged `tools/token_framing_probe.py` at repository commit
`c96a02c5d0615bd3547a19f563a6281890ed21c5`, SHA256
`5d4e7ac3cc682b1744c5cbe715393fccf848bde46d5da22785bec1c4190a6774`;
its only repository import is `tools/orf_signature.py`, SHA256
`b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`.
Python 3.13.15, CPU only. RTX 3090 available; unnecessary for this bounded job.

Each run parses the first 131072 payload bytes from bit zero with the candidate
unary-zero/one-stop/five-suffix grammar. Seeds are every integer 20261021 through
20261028 inclusive. The real prefix is fixed across seeds. Every model starts a
fresh `random.Random(seed)`. Reports retain all model counts, exact endpoint
accounting and fitted Markov transition counts in the accompanying JSON.

Bernoulli uses measured ones density in expectation; byte shuffle preserves the
exact byte histogram; alternating per-value run shuffle preserves exact maximal
run multisets and endpoints. The first-order Markov control fits adjacent-bit
counts without wraparound/pseudocounts, initializes with measured ones density,
and conditions subsequent bits on the generated preceding bit. Its finite
density, transitions and run histogram are not exactly preserved. This is a
homogeneous fitted control; it need not capture local nonstationarity or
higher-order structure. None is a comprehensive null for a camera bitstream.

Public raw.pixls.us CC0 inputs, exact local SHA256 matched to the retained
verified inventory and existing public manifest before measurement; no online
licence refresh was needed or performed:

- 1993 `Olympus - E-M1MarkII - 16bit (4:3).ORF`, SHA256 `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8`.
- 6343 `OM System - OM-5 - 16bit (4:3).ORF`, SHA256 `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`.
- 5283 `OM System - OM-1 - 16bit (4:3).ORF`, SHA256 `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`.

Measured payloads are variable-size: 1993/6343 have dimensions 5240x3912;
5283 has dimensions 5220x3912. These facts alone do not assign a compressed
variant; cross-body measurements here do not imply a shared codec.

## Results

All eight reports complete: 24 sample/seed cells, 120 model cells, zero failures
or prefix shortfalls. Real q0 fraction exceeds each of the four generated
controls at every seed on every file: 96/96 descriptive comparisons. These are
new measurements, not reproduction of the old incorrect null definitions or
historical private figures. Eight seeds are not eight independent camera files.

Exact real q0/token counts and Markov minimum/maximum q0 fractions across seeds
(fractions ordered by integer cross-multiplication, rather than numerator alone):

- 1993: real 157927/172214; Markov range 73723/150341 to 74282/150475.
- 6343: real 104220/159186; Markov range 74651/150498 to 75361/150653.
- 5283: real 79866/150829; Markov range 71514/148671 to 72409/148946.

The selected OM-1 prefix has a much smaller real/control contrast than the
known E-M1 Mark II prefix. This does not isolate camera, scene, exposure,
payload density or processing effects. No calibrated significance, entropy
alphabet, actual token/row boundary, adaptation, predictor, value mapping,
sensor values or decode follows from these comparisons.

## Reproduce

Match local input SHA256 to retained CC0 verification records, or first verify
previously unverified content. Substitute the three matching local file paths.
Read the full tool/import sources before running. This PowerShell loop only
reads inputs and prints aggregate JSON, once per seed:

```powershell
foreach ($seed in 20261021..20261028) {
    python -I -B tools/token_framing_probe.py --markov --bytes 131072 --seed $seed --sample 1993 "Olympus - E-M1MarkII - 16bit (4:3).ORF" FILE1993 --sample 6343 "OM System - OM-5 - 16bit (4:3).ORF" FILE6343 --sample 5283 "OM System - OM-1 - 16bit (4:3).ORF" FILE5283
}
python -I -B tools/test_token_framing_probe.py
```

All exact per-seed outputs are in `lead197-cross-body-multiseed-q0.json`.
The JSON wrapper records method/input identity, predeclared selection and seeds;
its `reports` array contains the eight unchanged parsed CLI reports. No raw or
pixel payloads, image data or local paths are retained.

## Status

Holds descriptively: all 24 sample/seed cells complete; real q0 exceeds all four
implemented generated controls in all 96 comparisons for these selected prefixes.
Contradicts: no historical numerical or camera-mechanism claim was retested or
declared contradicted.
Not tested: significance, local/higher-order controls, unseen files of these
bodies, later payload windows, true framing/rows/alphabet, controlled captures,
adaptive code, predictor/value mapping or decoding.
Open: a predeclared window/cohort study with stronger local controls or controlled
captures could discriminate framing hypotheses. This bounded report leaves #197
and its original Next steps open. Exact rerun: command and immutable method above.
Public/private limits: all new numbers use the three named public CC0 inputs;
no private measurements or historical private values were reproduced.

I confirm this follows RULES.md and is released under CC0 1.0. No images/previews
were viewed and no other decoder code, output, derivatives or write-ups used.
