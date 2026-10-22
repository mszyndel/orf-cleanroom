#!/usr/bin/env python3
"""Synthetic bounded description-length controls for research plan #298.

This is an invented toy grammar, NOT an ORF parser or sensor-value model.
Alphabet: integers 0..3; traversal: supplied order; previous starts at zero.
Twelve model IDs = predictor*6 + mapping*3 + k, with predictor 0=zero,
1=previous reconstructed symbol; mapping 0=unsigned modular residual,
1=centered modular residual zigzag (residues 0,1,2,3 -> 0,2,3,1);
k=0,1,2. Residual is (symbol-predictor) modulo 4. Each mapped residual
u uses floor(u/2**k) zero bits, one delimiter, then k MSB-first low bits.
There are no escapes, adaptive state, fitted tables or undeclared constants.

Packets are MSB-first bit strings: one kind bit (0 raw, 1 model), eight
count bits (0..255), four model-ID bits for kind 1 only, exactly count
symbols (two-bit literals for raw), then 0..7 zero pad bits to the next
byte. No trailing bytes, nonzero padding, out-of-range residual or unused
model IDs are accepted. Count is known from the header; no EOF token.
Model description cost is four bits per modeled packet, even after freezing.
Kind/count and padding are charged to both alternatives. Costs are lengths
of actual prefix-decodable packets, not an asserted normalized likelihood.

Discovery chooses the shortest total serialized discovery cost, ties by ID;
validation reports that frozen model and every candidate, labeling validation
oracle as exploratory. Candidate definitions and discovery choice never use
validation. Synthetic inputs are fixed in source, with no sample-derived data.
Round trips cannot identify true sensor values or distinguish arbitrary
reversible transforms; independent ORF constraints remain future work.
"""
import argparse
import itertools
import json
import time


MODELS = tuple(range(12))
MAP = (0, 2, 3, 1)
UNMAP = (0, 3, 1, 2)


def parameters(model):
    if type(model) is not int or model not in MODELS:
        raise ValueError("unused model ID")
    return model // 6, (model % 6) // 3, model % 3


def validate_values(values):
    if len(values) > 255 or any(type(x) is not int or not 0 <= x < 4 for x in values):
        raise ValueError("expected at most 255 alphabet-4 integers")


def body(values, model):
    predictor, mapping, k = parameters(model)
    previous = 0
    parts = []
    for value in values:
        residual = (value - (previous if predictor else 0)) % 4
        u = MAP[residual] if mapping else residual
        parts.append("0" * (u >> k) + "1" + (format(u % (1 << k), "0%db" % k) if k else ""))
        previous = value
    return "".join(parts)


def encode(values, model=None):
    validate_values(values)
    bits = ("0" if model is None else "1") + format(len(values), "08b")
    if model is None:
        bits += "".join(format(x, "02b") for x in values)
    else:
        bits += format(model, "04b") + body(values, model)
    return bits + "0" * (-len(bits) % 8)


def decode(bits):
    """Return values and model, rejecting every byte outside the exact grammar."""
    if not bits or len(bits) > 1040 or len(bits) % 8 or any(c not in "01" for c in bits):
        raise ValueError("expected 1..130 bytes of byte-aligned bits")
    position = 0

    def take(count):
        nonlocal position
        if position + count > len(bits):
            raise ValueError("truncated field")
        text = bits[position:position + count]
        position += count
        return int(text, 2) if count else 0

    kind, count = take(1), take(8)
    model = take(4) if kind else None
    if kind:
        predictor, mapping, k = parameters(model)
    values = []
    previous = 0
    for _ in range(count):
        if not kind:
            value = take(2)
        else:
            q = 0
            while take(1) == 0:
                q += 1
                if q > (3 >> k):
                    raise ValueError("quotient outside alphabet")
            u = (q << k) + take(k)
            if u > 3:
                raise ValueError("residual outside alphabet")
            residual = UNMAP[u] if mapping else u
            value = (residual + (previous if predictor else 0)) % 4
        values.append(value)
        previous = value
    if len(bits) - position != -position % 8 or any(c != "0" for c in bits[position:]):
        raise ValueError("noncanonical padding or trailing bytes")
    return values, model


def costs(values, model):
    validate_values(values)
    payload = 2 * len(values) if model is None else len(body(values, model))
    header = 9 if model is None else 13
    padding = -(header + payload) % 8
    return {"payload_bits": payload, "model_bits": 0 if model is None else 4,
            "kind_count_bits": 9, "padding_bits": padding,
            "total_bits": header + payload + padding}


def total(packets, model):
    return sum(costs(packet, model)["total_bits"] for packet in packets)


def experiment(discovery, validation):
    if not discovery or not validation:
        raise ValueError("both splits require at least one packet")
    ledger = [{"model": m, "predictor": parameters(m)[0],
               "mapping": parameters(m)[1], "k": parameters(m)[2],
               "discovery_bits": total(discovery, m),
               "validation_bits": total(validation, m)} for m in MODELS]
    frozen = min(ledger, key=lambda row: (row["discovery_bits"], row["model"]))["model"]
    oracle = min(ledger, key=lambda row: (row["validation_bits"], row["model"]))["model"]
    packets = discovery + validation
    failures = sum(decode(encode(p, m)) != (list(p), m) for p in packets for m in MODELS)
    return {"ledger": ledger, "frozen_model": frozen,
            "validation_frozen_bits": total(validation, frozen),
            "validation_raw_bits": total(validation, None),
            "validation_oracle_exploratory_model": oracle,
            "validation_oracle_exploratory_bits": total(validation, oracle),
            "roundtrip_failures": failures,
            "roundtrip_attempts": len(packets) * len(MODELS),
            "validation_frozen_packets": [costs(p, frozen) for p in validation]}


def exhaustive(max_symbols):
    counts = {"sequences": 0, "roundtrips": 0, "accepted_short_packets": 0,
              "rejected_short_packets": 0}
    for n in range(max_symbols + 1):
        for sequence in itertools.product(range(4), repeat=n):
            counts["sequences"] += 1
            for model in (None,) + MODELS:
                bits = encode(sequence, model)
                if decode(bits) != (list(sequence), model) or len(bits) != costs(sequence, model)["total_bits"]:
                    raise AssertionError("exhaustive roundtrip/accounting failure")
                counts["roundtrips"] += 1
    # Exhaust every byte string of length one or two, including malformed syntax.
    # All accepted strings must re-encode exactly, not just to equivalent symbols.
    for width in (8, 16):
        for value in range(1 << width):
            bits = format(value, "0%db" % width)
            try:
                sequence, model = decode(bits)
            except ValueError:
                counts["rejected_short_packets"] += 1
            else:
                if encode(sequence, model) != bits:
                    raise AssertionError("noncanonical accepted packet")
                counts["accepted_short_packets"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-symbols", type=int, default=5, choices=range(0, 7),
                        help="exhaust sequences through this length (0..6; default 5)")
    args = parser.parse_args()
    start = time.perf_counter()
    checks = exhaustive(args.max_symbols)
    pilot_seconds = time.perf_counter() - start
    result = experiment([[0] * 64], [[3] * 64])
    print(json.dumps({"scope": "synthetic only; not an ORF codec result",
                      "grammar": "alphabet4-modular-rice-v1", "search_candidates": 12,
                      "split": "discovery: 64 zeros; validation: 64 threes",
                      "checks": checks, "cpu_pilot_seconds": pilot_seconds,
                      "backend": "stdlib CPU; tiny family does not warrant GPU startup",
                      "payload_win_reversal": {"symbols": "synthetic 0,3,3",
                          "model9": costs([0, 3, 3], 9),
                          "raw": costs([0, 3, 3], None)},
                      "score": result}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


