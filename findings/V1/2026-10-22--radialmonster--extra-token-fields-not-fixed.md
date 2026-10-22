# Extra S-W candidate tokens are not a fixed header or constant padding at measured strides

Author: @radialmonster
Verified by: @radialmonster
Lead: #144
Variant: V1
Builds on: 2026-10-21--radialmonster--wide-row-stride-new-bodies, 2026-10-22--radialmonster--later-band-row-stride-drift
Partial: the extra-token question only, on five public CC0 files and three candidate bands; not the true row length, physical rows, absolute row origin, a variable-row-alignment model, a value mapping or a decode

## Claim

At the measured candidate strides S for five public CC0 files, the T = S-W extra tokens are not a fixed header or constant padding field. They are distributionally close to the adjacent body at the bands tested, and their positions vary from row to row instead of repeating a fixed pattern.

New run on 2026-10-22 UTC, 300 candidate rows per band at start rows 0, 1000 and 2000. All 15 file/band cells:

- Tail [W,S) versus the immediately preceding T tokens: q total variation 0.0017 to 0.0339, suffix total variation 0.0065 to 0.0183.
- Per-position modal share across the 300 rows: tail q 0.5037 to 0.7919, tail suffix 0.0555 to 0.0779; body q 0.4980 to 0.8166, body suffix 0.0555 to 0.0851. A fixed header or constant pad would sit near 1, not in the body range.
- Every cell has 300 distinct exact (q, suffix) sequences across its 300 rows, and 0 adjacent equal sequences. No row repeats the previous row's extra-token sequence.
- The first band sometimes differs from the whole body (q TV up to 0.0914) but not from its immediately preceding T tokens (at most 0.0177). That is consistent with top-of-frame content, not with a fixed field that would appear at every row.

An exact all-offset GPU scan is a supporting cross-check, not the source of the numbers above. For each cell it recomputed the same tail statistics at every contiguous T-token placement in the S-token row with CuPy 14.0.1 on an RTX 3090 (driver 610.74), using integer counts and float64 ratios; selected offsets matched an independent CPU recomputation to floating-point precision. The tail was not an outlier of its own row in that scan. The detailed GPU aggregates are reported separately from this finding.

This rules out a fixed header or constant pad at these bands. It does not decide whether the extra tokens are image columns beyond the stored width, variable row-aligned content, or another field: all of those can be body-like and variable. It also does not establish physical rows, a whole-frame stride model, a value assembly or a decode.

## Original evidence

Lead #144, found by @radialmonster on 2026-10-21, measured one best candidate stride per file from a 300-row prefix row-start q profile. The nine-file prefix table and later-band movement are in the two findings above. The lead explicitly left "segment rows at S and compare the first W tokens with the extra S-W tokens: padding, a header, or a second field?" open; this finding addresses only that question.

The candidate strides used here are the ones published in `2026-10-21--radialmonster--wide-row-stride-new-bodies`: 6347 S=5540, 5286 S=5978, 6346 S=10575, with controls 6343 S=5472 and 5283 S=6010. They are not refitted in this run.

Files, all public CC0 raw.pixls.us:

- 6343 `OM System - OM-5 - 16bit (4:3).ORF`, 5240x3912, SHA-256 `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7`
- 6347 `OM System - OM-5 - 16bit (4:3).ORI`, 5240x3912, `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9`
- 5283 `OM System - OM-1 - 16bit (4:3).ORF`, 5220x3912, `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b`
- 5286 `OM System - OM-1 - 16bit (4:3).ORI`, 5220x3912, `2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1`
- 6346 `OM System - OM-5 - 16bit (4:3).ORF`, 10400x7792, `ffd47d5924b65abdd8af761665d67705fe028cfd08e5efbc264b64a20830d9f4`

## Verification

New run on 2026-10-22 UTC, after lead #144 was posted. The five local SHA-256 values matched the retained verified-CC0 inventory and existing `samples/manifest.csv` rows before measurement; no download or catalogue request was repeated. Python 3.13.15, repository main `428926b`. The parser is the merged `tools/token_tail_distribution_probe.py` `scan_tokens` grammar (q zero bits, stop 1, five suffix bits, no extra escape skip; a token is accepted only when its whole length fits). Candidate rows are absolute r*S token intervals; they are not physical image rows.

| id | start | W | S | T | tail tokens | tail-body qTV | tail-prec qTV | tail-prec sTV | tail qmode | body qmode | tail smode | body smode | distinct | adjacent | tail qent | body qent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5283 | 0 | 5220 | 6010 | 790 | 237000 | 0.0192 | 0.0339 | 0.0149 | 0.5112 | 0.5305 | 0.0566 | 0.0566 | 300 | 0 | 2.0200 | 1.9368 |
| 5283 | 1000 | 5220 | 6010 | 790 | 237000 | 0.0017 | 0.0017 | 0.0068 | 0.5270 | 0.5278 | 0.0559 | 0.0561 | 300 | 0 | 1.8972 | 1.8961 |
| 5283 | 2000 | 5220 | 6010 | 790 | 237000 | 0.0059 | 0.0046 | 0.0065 | 0.5037 | 0.4980 | 0.0555 | 0.0555 | 300 | 0 | 1.9969 | 2.0133 |
| 5286 | 0 | 5220 | 5978 | 758 | 227400 | 0.0162 | 0.0177 | 0.0131 | 0.5152 | 0.5314 | 0.0564 | 0.0567 | 300 | 0 | 2.0048 | 1.9366 |
| 5286 | 1000 | 5220 | 5978 | 758 | 227400 | 0.0027 | 0.0031 | 0.0068 | 0.5304 | 0.5293 | 0.0559 | 0.0561 | 300 | 0 | 1.8903 | 1.8916 |
| 5286 | 2000 | 5220 | 5978 | 758 | 227400 | 0.0079 | 0.0035 | 0.0080 | 0.5048 | 0.4985 | 0.0559 | 0.0556 | 300 | 0 | 1.9746 | 2.0139 |
| 6343 | 0 | 5240 | 5472 | 232 | 69600 | 0.0744 | 0.0175 | 0.0183 | 0.5938 | 0.6680 | 0.0579 | 0.0642 | 300 | 0 | 1.6365 | 1.4650 |
| 6343 | 1000 | 5240 | 5472 | 232 | 69600 | 0.0054 | 0.0040 | 0.0137 | 0.6212 | 0.6260 | 0.0584 | 0.0594 | 300 | 0 | 1.5667 | 1.5606 |
| 6343 | 2000 | 5240 | 5472 | 232 | 69600 | 0.0150 | 0.0162 | 0.0178 | 0.6056 | 0.6204 | 0.0588 | 0.0594 | 300 | 0 | 1.6195 | 1.5704 |
| 6346 | 0 | 10400 | 10575 | 175 | 52500 | 0.0911 | 0.0034 | 0.0134 | 0.7257 | 0.8166 | 0.0678 | 0.0851 | 300 | 0 | 1.2398 | 0.9563 |
| 6346 | 1000 | 10400 | 10575 | 175 | 52500 | 0.0190 | 0.0051 | 0.0139 | 0.7863 | 0.7676 | 0.0779 | 0.0769 | 300 | 0 | 1.0684 | 1.1272 |
| 6346 | 2000 | 10400 | 10575 | 175 | 52500 | 0.0097 | 0.0031 | 0.0148 | 0.7919 | 0.7822 | 0.0751 | 0.0756 | 300 | 0 | 1.0152 | 1.0655 |
| 6347 | 0 | 5240 | 5540 | 300 | 90000 | 0.0914 | 0.0133 | 0.0107 | 0.5568 | 0.6481 | 0.0568 | 0.0631 | 300 | 0 | 1.8010 | 1.5630 |
| 6347 | 1000 | 5240 | 5540 | 300 | 90000 | 0.0050 | 0.0130 | 0.0114 | 0.5893 | 0.5934 | 0.0581 | 0.0584 | 300 | 0 | 1.7030 | 1.6921 |
| 6347 | 2000 | 5240 | 5540 | 300 | 90000 | 0.0032 | 0.0045 | 0.0079 | 0.5803 | 0.5812 | 0.0574 | 0.0582 | 300 | 0 | 1.7230 | 1.7226 |

Validation: the compact script below was checked against the merged `tools/token_tail_distribution_probe.py` on 6347 band 0; all four regions matched in token count, q and suffix histograms, entropy and total variation exactly (mode shares within 1e-12), and the GPU scan's five selected offsets per cell matched an independent CPU recomputation to floating-point precision.

Limits: candidate rows only; five known-profile public files, not a blind or random cohort; three 300-row bands, not the whole frame; S is a candidate stride, not a physical row length; the extra tokens' origin and any value meaning remain open. The GPU detail and the higher-rank band-0 edge cases are in the accompanying `stats/` report; they do not change the scoped claim.

## Reproduce

Run from the repository root with the merged tool at `428926b` and the file paths substituted. Keep the public identities by SHA-256.

    python -I -B tools/test_token_tail_distribution_probe.py
    python -I -B tools/token_tail_distribution_probe.py --sample 6347 "OM System - OM-5 - 16bit (4:3).ORI" 062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9 FILE6347 --stride 5540 --rows 300 --start-row 0 --start-row 1000 --start-row 2000
    python -I -B extra_fields.py FILE6347 062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9 --stride 5540 --start-row 0 --rows 300

`extra_fields.py` (prints aggregate JSON only; no files written):

    import argparse
    import array
    import collections
    import hashlib
    import json
    import math
    import sys

    sys.path.insert(0, "tools")
    import token_tail_distribution_probe as P

    def entropy(counter):
        total = sum(counter.values())
        return (-sum(n / total * math.log2(n / total) for n in counter.values() if n)
                if total else None)

    def tv(a, b):
        na, nb = sum(a.values()), sum(b.values())
        return (sum(abs(a.get(k, 0) / na - b.get(k, 0) / nb)
                    for k in set(a) | set(b)) / 2 if na and nb else None)

    def stats(qrows, srows, lo, hi):
        nrows = len(qrows)
        width = hi - lo
        qh, sh = collections.Counter(), collections.Counter()
        qmode = smode = 0.0
        seqs = []
        for r in range(nrows):
            qr, sr = qrows[r], srows[r]
            for p in range(lo, hi):
                qh[qr[p]] += 1
                sh[sr[p]] += 1
            seqs.append(qr[lo:hi].tobytes() + sr[lo:hi].tobytes())
        for p in range(lo, hi):
            qc = collections.Counter(qrows[r][p] for r in range(nrows))
            sc = collections.Counter(srows[r][p] for r in range(nrows))
            qmode += max(qc.values()) / nrows
            smode += max(sc.values()) / nrows
        return dict(start=lo, stop=hi, tokens=sum(qh.values()),
                    mean_q=(sum(q * n for q, n in qh.items()) / sum(qh.values())
                            if qh else None),
                    escapes=sum(n for q, n in qh.items() if q >= 17),
                    q_entropy=entropy(qh), suffix_entropy=entropy(sh),
                    q_position_mode_share=(qmode / width if width else None),
                    suffix_position_mode_share=(smode / width if width else None),
                    distinct_sequences=len(set(seqs)),
                    adjacent_equal_sequences=sum(1 for r in range(1, nrows)
                                                 if seqs[r] == seqs[r - 1]),
                    q_hist=qh, s_hist=sh)

    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument("file")
        ap.add_argument("sha256")
        ap.add_argument("--stride", type=int, required=True)
        ap.add_argument("--start-row", type=int, default=0)
        ap.add_argument("--rows", type=int, default=300)
        a = ap.parse_args()
        with open(a.file, "rb") as f:
            data = f.read()
        actual = hashlib.sha256(data).hexdigest()
        if actual != a.sha256.lower():
            raise SystemExit("SHA-256 mismatch")
        best = max(P.Tiff(data).all_ifds(), key=lambda d: sum(d.get(0x117) or [0]))
        W, H = best[0x100][0], best[0x101][0]
        off, size = best[0x111][0], best[0x117][0]
        if P.size_class(size, W, H) != "variable":
            raise SystemExit("not a variable-size payload")
        S = a.stride
        T = S - W
        if a.rows < 1 or a.start_row < 0 or T < 1 or T > W or S // 2 + T > W:
            raise SystemExit("require rows>=1, start-row>=0, 1 <= S-W <= W")
        limit = (a.start_row + a.rows) * S
        qflat, sflat = array.array("H"), array.array("B")
        for q, s, end in P.scan_tokens(data[off:off + size], limit):
            qflat.append(q)
            sflat.append(s)
        if len(qflat) < limit:
            raise SystemExit("token shortfall")
        qrows = [qflat[r * S:(r + 1) * S] for r in range(a.start_row, a.start_row + a.rows)]
        srows = [sflat[r * S:(r + 1) * S] for r in range(a.start_row, a.start_row + a.rows)]
        specs = {"body": (0, W), "tail": (W, S), "preceding": (W - T, W),
                 "middle": (S // 2, S // 2 + T)}
        regions = {k: stats(qrows, srows, lo, hi) for k, (lo, hi) in specs.items()}
        tail = regions["tail"]
        comparisons = {k: dict(q_tv=tv(tail["q_hist"], r["q_hist"]),
                               suffix_tv=tv(tail["s_hist"], r["s_hist"]))
                       for k, r in regions.items() if k != "tail"}
        for r in regions.values():
            del r["q_hist"], r["s_hist"]
        print(json.dumps(dict(pixls_sha256=actual, payload_width=W, payload_height=H,
                              stride=S, window=T, start_row=a.start_row, rows=a.rows,
                              regions=regions, tail_comparisons=comparisons),
                         indent=2, sort_keys=True))

    if __name__ == "__main__":
        main()

Repeat with 5283 (S=6010), 5286 (S=5978), 6343 (S=5472) and 6346 (S=10575), and with `--start-row 1000` and `--start-row 2000`.
