# Four high-bpp compressed payloads start with q=47, not q=39

Author: @radialmonster
Verified by: @radialmonster
Lead: #246
Variant: unassigned
Builds on: #37, #86, 2026-10-21--radialmonster--initial-q39-token-and-escape-counts-on-three-bodies, 2026-10-20--radialmonster--large-sensor-k5-parse-near-bernoulli-null

## Claim

On the frozen 87-file CC0 `size_class=variable` cohort (unique input SHA-256), the first payload token is q=39 with a 5-bit suffix of 0 on 83 files, and q=47 with suffix 0 on four files. The four are raw.pixls.us ids 7267, 7269, 7801 and 7803 (OM-1 Mark II / OM-3 High Res, 10386x7792 or 8172x6132, 8.208 to 8.794 bpp). Their located payload begins `00 00 00 00 00 01`, one leading zero byte more than the other 83 (`00 00 00 00 01 00`); payload bytes 1..5 on all four are `00 00 00 00 01`, the same 40-bit start pattern as the 83. On all four, a whole-payload parse counts q=47 exactly once and q=39 zero times, so q=47 is the initial token, not an isolated later escape.

This corrects the universal wording of lead #37 ("Every payload starts with a 39-zero-bit token") and the V2 S2.2 reading of q=47 as a later isolated escape. Whether the extra leading zero byte is a header field, padding or an artifact of the TIFF strip offset is not established; no variant assignment is made.

## Original evidence

Lead #246, opened by @radialmonster on 2026-10-21. The tool is `tools/orf_tokens.py` at `a3fdd6ff8595a697af5cfbee6ff1558253d0c68b` (`locate` and `scan`); `tools/orf_signature.py` at `8318921d74d6788a5ab7af8a244f0d850dd3ae35`. The frozen cohort is `tools/cohorts/lead87-trailing-ones-v1-full.json`, SHA-256 `13d58cd6149671e53cbd853956ac40f0b4673f00bebe3b79e0d10fd1f2ce49e2`. All 87 local files matched the retained verified-CC0 inventory by SHA-256 and existing `samples/manifest.csv` identities before measurement; no online licence lookup or download was repeated.

First-token census: 87 files, 0 unmatched, 0 failures. q=39: 83; q=47: 4. Suffix 0: 87. First five payload bytes `0000000001`: 83; `0000000000`: 4. First six bytes `000000000100`: 83; `000000000001`: 4.

The four public identities (raw.pixls.us id, name, SHA-256):

- 7267 `OM System - OM-1 Mark II - 16bit (4:3).orf` `5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756`
- 7269 `OM System - OM-1 Mark II - 16bit (4:3).orf` `dd2a6c1c4ca4d86201207925477e2ea8e50ebd53d7df9117847093f5023540ec`
- 7801 `OM System - OM-3 - 16bit (4:3).ORF` `8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82`
- 7803 `OM System - OM-3 - 16bit (4:3).ORF` `63a5b4da41fdbe8b31213ca7a11408dfd0453d893f17ac09a73471580ffbd8f0`

Whole-payload `scan()` counts: 7267 96,747,418 tokens, q=39 0, q=47 1; 7269 61,335,792 tokens, q=39 0, q=47 1; 7801 95,492,255 tokens, q=39 0, q=47 1; 7803 60,282,029 tokens, q=39 0, q=47 1. The 7801 `scan()` end overshoots the payload by 2 bits, the suffix overread documented in `2026-10-21--radialmonster--token-end-and-final-run`; the q counts are unaffected.

Found by @radialmonster, 2026-10-21. Strength: deterministic 87/87 first-token split; whole-payload q=47 uniqueness on all four. The cause of the extra byte and any variant assignment are not claimed.

## Verification

A new run by the same finder on 2026-10-21 UTC, after lead #246 was posted. The lead's cohort is the complete compressed variable-size CC0 set (87 of the 104 CC0 files; the other 17 are fixed-size V0 and outside this claim), so no unused variable-size CC0 file exists; this is an independent measurement on the same 87 files, not a new-body validation.

The second run used a different payload path and its own bit reader: `orf_signature.signature()` supplied `payload_offset` and `payload_bytes`, the payload was sliced directly, and the first stop bit and 5-bit suffix were read from an 8-byte bit string. It then ran a separate bounded token counter that accepts a token only when its q zeros + stop bit + 5 suffix bits fit inside the payload.

Results:

- First-token histogram exactly `{(39, '00000', '0000000001'): 83, (47, '00000', '0000000000'): 4}`; inventory/identity mismatches and failures: 0.
- Every one of the four q=47 files had payload bytes 1..5 equal to `0000000001`.
- Bounded whole-payload counts on the four: 7267 96,747,418 tokens, q=39 0, q=47 1, 5 residual bits; 7269 61,335,792 tokens, q=39 0, q=47 1, 0 residual bits; 7801 95,492,254 tokens, q=39 0, q=47 1, 6 residual bits; 7803 60,282,029 tokens, q=39 0, q=47 1, 5 residual bits.
- The 7801 bounded count is one token lower than `scan()` and leaves 6 residual bits instead of overshooting, exactly the known suffix overread; the q=39 and q=47 counts agree.

Limits: the claim covers the frozen 87-file variable-size CC0 cohort only. The extra leading zero byte's cause is not established, and it could be a header field, padding or a strip-offset artifact. q=47 is not claimed as a V2 signature, only as the initial token on these four files. No decode, value mapping or significance test is claimed. This is self-verification by the same human account, not independent human verification.

## Reproduce

Download the CC0 files outside the repository. The frozen cohort lists the 87 ids, names and SHA-256 values. Match files by SHA-256, not by name (downloaded names use `_` for `:`).

First-token census (`SAMPLES` is the folder holding the downloaded files):

    import hashlib
    import json
    import os
    import sys
    sys.path.insert(0, "tools")
    from orf_tokens import locate

    cohort = json.load(open("tools/cohorts/lead87-trailing-ones-v1-full.json", encoding="utf-8"))
    paths = {}
    for root, _, names in os.walk("SAMPLES"):
        for name in names:
            p = os.path.join(root, name)
            paths[hashlib.sha256(open(p, "rb").read()).hexdigest()] = p
    hist = {}
    for s in cohort["samples"]:
        w, h, buf = locate(paths[s["sha256"]])
        bits = "".join(format(b, "08b") for b in buf[:8])
        q = bits.index("1")
        key = (q, bits[q + 1:q + 6], buf[:5].hex())
        hist[key] = hist.get(key, 0) + 1
    print(hist)

Expected: `{(39, '00000', '0000000001'): 83, (47, '00000', '0000000000'): 4}`.

Whole-payload counts with the repository scanner:

    python -I -B tools/orf_tokens.py --all "7267_OM System - OM-1 Mark II - 16bit (4_3).orf"
    python -I -B tools/orf_tokens.py --all "7269_OM System - OM-1 Mark II - 16bit (4_3).orf"
    python -I -B tools/orf_tokens.py --all "7801_OM System - OM-3 - 16bit (4_3).ORF"
    python -I -B tools/orf_tokens.py --all "7803_OM System - OM-3 - 16bit (4_3).ORF"

The `escape q values` line shows `47:1`; q=39 is absent. The 7801 end overshoot is the known overread.

Bounded counter used in the Verification (read the payload at `orf_signature.signature()["payload_offset"]` for `payload_bytes` first):

    def bounded_counts(buf):
        nbits = len(buf) * 8
        pad = buf + bytes(12)
        pos = 0
        n = 0
        c39 = 0
        c47 = 0
        while pos + 6 <= nbits:
            win = int.from_bytes(pad[pos >> 3:(pos >> 3) + 12], "big")
            avail = 96 - (pos & 7)
            v = win & ((1 << avail) - 1)
            if v == 0 or avail - v.bit_length() + 6 > avail:
                q = 0
                p = pos
                while p < nbits and not (buf[p >> 3] >> (7 - (p & 7))) & 1:
                    q += 1
                    p += 1
                if p + 6 > nbits:
                    break
                pos = p + 6
            else:
                q = avail - v.bit_length()
                if pos + q + 6 > nbits:
                    break
                pos += q + 6
            n += 1
            if q == 39:
                c39 += 1
            elif q == 47:
                c47 += 1
        return n, c39, c47, pos
