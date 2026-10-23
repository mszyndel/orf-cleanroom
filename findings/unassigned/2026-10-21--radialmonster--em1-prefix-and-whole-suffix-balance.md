# Within-token suffix balance on a public E-M1 prefix and whole payload

Author: @radialmonster
Verified by: @radialmonster
Lead: #11
Variant: unassigned
Builds on: 2026-10-21--radialmonster--within-token-suffix-balance-four-bodies
Partial: within-token MI(H;L) and b0/b1 marginals within the previously stated tolerance on public E-M1 id 1051, first 262144 candidate tokens and whole payload; not exact independence/fairness, population generality, framing, geometry, values or decoding.

## Claim

The public E-M1 file raw.pixls.us id 1051 passes the same descriptive tolerance used by `2026-10-21--radialmonster--within-token-suffix-balance-four-bodies`, both on its first 262144 candidate tokens and its whole payload: `MI(H;L) <= 0.010` bit and `|P(b1=1)-0.5| <= 0.05` and `|P(b0=1)-0.5| <= 0.05`. Here `H=b4b3` and `L=b2b1b0` label the candidate suffix groups.

This is one public E-M1 input outside the earlier finding's four-body cohort. It is a selected available file with prior published escape/marginal measurements, not a blind file or a random E-M1 sample. It cannot reproduce the maintainer's private 55/57 tolerance result or show whether the two private E-M1 failures have a public counterpart. Exact independence, exact fair-coin marginals and universal tolerance are not established.

## Original evidence

[Lead #11](https://github.com/radialmonster/orf-cleanroom/issues/11), by @radialmonster, states that H/L are independent within a token and that b0/b1 behave as fair coins, from private research notes dated 2026-10-14..18. It gives no numeric tolerance for that item, so its exact historical figures cannot be reproduced. The earlier four-body finding used the explicit tolerance above on ids 241/5283/6343/6946, all first-262144-token prefixes.

The maintainer's subsequent comment on #11 requested public E-M1 measurements after reporting that the tolerance passed 55/57 further private files and 38/40 private E-M1 files. Those private inputs and numbers are not retested here. The bounded two-extent method and unchanged tolerance were fixed in the [Taking this comment](https://github.com/radialmonster/orf-cleanroom/issues/11#issuecomment-6326689951) before this run's primary outcomes.

Input: raw.pixls.us **1051**, exact public name `Olympus - E-M1 - 16bit (4:3).orf`, SHA-256 `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda`. Its local hash matched the retained verified CC0 inventory and the existing manifest's exact id/name/hash/licence before measurement; no catalogue refresh or download. Existing manifest rows and attribution were unchanged.

Measured container signature: ORF-RO, 4640x3472, 16 bits per sample, compression tag 1, payload offset 1491456, payload 13919144 bytes, 6.912 bpp, variable-size payload. The measured signature remains `unassigned`; model name alone does not assign a variant.

## Verification

A new run on 2026-10-21 UTC after lead #11 and the previous finding were posted. Unchanged `tools/orf_tokens.py` and its imported locator `tools/orf_signature.py` at repository commit `2cfdf7caa379e2f7e0c565964c415eaed7e175c4`, Python 3.13.15. The last commits changing those sources were respectively `a3fdd6ff8595a697af5cfbee6ff1558253d0c68b` and `8318921d74d6788a5ab7af8a244f0d850dd3ae35`.

The candidate grammar reads MSB-first q zero bits, one stop bit and five suffix bits from payload bit zero. No extra escape bits are skipped. Candidates with q>=17 remain at their original sequence indices and are omitted from suffix statistics. Neither the candidate grammar nor escape meaning is established as camera syntax.

Both declared extents passed without changing the tolerance or selecting another file. The whole-payload extent has 3 residual bits (13919144*8 - 111353149); this is parser accounting, not evidence of padding or true framing. Statistics below are at the unchanged CLI's printed precision.

| extent | candidates | q>=17 | ordinary candidates | bits consumed | MI(H;L), bit | rotated baseline | P(b4=1) | P(b3=1) | P(b2=1) | P(b1=1) | P(b0=1) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| first 262144 | 262144 | 3 | 262141 | 1775448 | 0.0039 | 0.0001 | 0.4743 | 0.5025 | 0.4992 | 0.4911 | 0.4867 |
| whole payload | 16694598 | 2225 | 16692373 | 111353149 | 0.0018 | 0.0000 | 0.4441 | 0.4780 | 0.4578 | 0.4809 | 0.4829 |

The printed MI is nonzero and both b0/b1 marginals fall below 0.5. Passing the tolerance is not an exact-independence or equivalence test. The rotated baseline is one deterministic descriptive comparison, not a null distribution or calibrated significance. The whole-payload statistic pools positions; local windows may differ. No scene/body/mode cause, physical rows, predictor, value mapping or decoding is inferred. The existing immutable findings retain their scope.

The finder and verifier are the same human account, @radialmonster. This is self-verification. Separate helper/supervisor calculations under that account do not provide independent human verification.

## Reproduce

Read complete source and imports first. Match unchanged local input content to its retained verified CC0 hash; new or changed content needs first licence verification. All inputs and reported file measurements here are public; none rests on private content. Replace `FILE1051` with the matching local input:

    python -I -B tools/test_orf_tokens.py
    python -I -B tools/orf_signature.py FILE1051
    python -I -B tools/orf_tokens.py FILE1051 --max-tokens 262144
    python -I -B tools/orf_tokens.py FILE1051 --all

The commands print aggregates. Read the token, escape, consumed-bit, suffix-bit-balance and within-token MI lines. No image or preview was viewed, and no raw/pixel data is committed.
