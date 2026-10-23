#!/usr/bin/env python3
"""Synthetic rejection controls for #301; no ORF input or sensor-truth oracle.

All thresholds are upper envelopes of plausible DEVELOPMENT controls only.
The fixed held-out seeds test implementation behavior, not new scene families.
Noise levels, 12-bit bounds and coordinate lanes are synthetic assumptions.
The wrong label means non-identity relative to the generator, not a physically
impossible sensor array: complement or offset can describe other scenes.
Complement preserves these features in exact arithmetic. The strict binary64
envelope comparison can reject a rounding-level tie: one of the 31 development
non-identity rejections exceeds lane_mean_spread by about 4.55e-13. It is not
discriminating evidence; the report retains the implemented comparison/counts.
Only aggregate features are printed; arrays stay in memory. Stdlib only.
"""
import argparse
import json
import time

MAX_CODE = 4095
WIDTH, HEIGHT = 32, 24
SCENES = ("smooth", "textured", "dark")
NOISE = (2, 16)
DEVELOPMENT_SEEDS = (1, 2, 3)
HELDOUT_SEEDS = (101, 102, 103)
MAPPINGS = ("identity", "complement", "xor_high", "affine_permutation", "offset_range")
FEATURES = ("outside_fraction", "lag2_mean_abs", "lane_mean_spread", "seam_mean_abs")


def synthetic(scene, noise, seed, width=WIDTH, height=HEIGHT):
    """Original toy arrays, not a physical sensor/noise/CFA simulation.

    LCG state updated per row-major cell: (1664525*s+1013904223) mod 2**32.
    The upper 16 state bits modulo (2*noise+1), minus noise, give bounded noise.
    """
    if scene not in SCENES or noise < 0 or width < 4 or height < 4:
        raise ValueError("invalid synthetic parameters")
    state = seed & 0xffffffff
    values = []
    for y in range(height):
        for x in range(width):
            state = (1664525 * state + 1013904223) & 0xffffffff
            perturbation = ((state >> 16) % (2 * noise + 1)) - noise
            if scene == "smooth":
                base = 200 + 22 * x + 11 * y
            elif scene == "textured":
                base = 512 + 2300 * ((x + y) % 2) + 9 * x + 3 * y
            else:
                base = 32
            values.append(min(MAX_CODE, max(0, base + perturbation)))
    return values


def transform(values, mapping, inverse=False):
    """Deliberately wrong reversible mappings, not candidate ORF layouts.

    complement and xor_high are involutions on 12-bit integers; affine is a
    permutation of indices. offset_range is reversible on integers but leaves
    the declared synthetic range. Identity is the plausible-control label.
    """
    if mapping == "identity":
        return list(values)
    if mapping == "complement":
        return [MAX_CODE - v for v in values]
    if mapping == "xor_high":
        return [v ^ 2048 for v in values]
    if mapping == "offset_range":
        return [v + (-4096 if inverse else 4096) for v in values]
    if mapping == "affine_permutation":
        n = len(values)
        if not n or n % 5 == 0:
            raise ValueError("affine index map requires length coprime to 5")
        if inverse:
            result = [0] * n
            for i, value in enumerate(values):
                result[(5 * i + 7) % n] = value
            return result
        return [values[(5 * i + 7) % n] for i in range(n)]
    raise ValueError("unknown mapping")


def features(values, width, height):
    """Exact sums/counts plus descriptive scalar features, no fitted semantics.

    Lag2 pairs: horizontal AND vertical distance two, no row wrapping.
    Lanes: four coordinate parity means; spread is max(mean)-min(mean).
    Seam: horizontal adjacent pairs crossing the fixed central column only.
    It is a toy internal boundary; no physical row/packet boundary is assumed.
    """
    if width < 4 or height < 4 or len(values) != width * height:
        raise ValueError("invalid shape")
    outside = sum(v < 0 or v > MAX_CODE for v in values)
    lag_sum = lag_count = seam_sum = seam_count = 0
    lane_sums, lane_counts = [0] * 4, [0] * 4
    for y in range(height):
        for x in range(width):
            i = y * width + x
            lane = 2 * (y % 2) + x % 2
            lane_sums[lane] += values[i]
            lane_counts[lane] += 1
            if x >= 2:
                lag_sum += abs(values[i] - values[i - 2])
                lag_count += 1
            if y >= 2:
                lag_sum += abs(values[i] - values[i - 2 * width])
                lag_count += 1
            if x == width // 2:
                seam_sum += abs(values[i] - values[i - 1])
                seam_count += 1
    means = [s / n for s, n in zip(lane_sums, lane_counts)]
    return {
        "counts": {"values": len(values), "outside": outside,
                   "lag2_sum_abs": lag_sum, "lag2_pairs": lag_count,
                   "lane_sums": lane_sums, "lane_counts": lane_counts,
                   "seam_sum_abs": seam_sum, "seam_pairs": seam_count},
        "scalars": {"outside_fraction": outside / len(values),
                    "lag2_mean_abs": lag_sum / lag_count,
                    "lane_mean_spread": max(means) - min(means),
                    "seam_mean_abs": seam_sum / seam_count}}


def envelope(training):
    if not training:
        raise ValueError("empty development set")
    return {key: max(row["features"]["scalars"][key] for row in training)
            for key in FEATURES}


def classify(measurement, limits):
    return [key for key in FEATURES if measurement["scalars"][key] > limits[key]]


def cohort(seeds):
    rows = []
    for scene in SCENES:
        for noise in NOISE:
            for seed in seeds:
                original = synthetic(scene, noise, seed)
                for mapping in MAPPINGS:
                    rows.append({"scene": scene, "noise": noise, "seed": seed,
                                 "mapping": mapping,
                                 "features": features(transform(original, mapping), WIDTH, HEIGHT)})
    return rows


def evaluate(rows, limits):
    confusion = {"plausible_accepted": 0, "plausible_rejected": 0,
                 "wrong_accepted": 0, "wrong_rejected": 0}
    grouped = {}
    result = []
    for row in rows:
        reasons = classify(row["features"], limits)
        plausible = row["mapping"] == "identity"
        key = ("plausible_" if plausible else "wrong_") + ("rejected" if reasons else "accepted")
        confusion[key] += 1
        group = "%s/noise%d/%s" % (row["scene"], row["noise"], row["mapping"])
        counts = grouped.setdefault(group, {"accepted": 0, "rejected": 0})
        counts["rejected" if reasons else "accepted"] += 1
        result.append(dict(row, rejected_by=reasons))
    return {"confusion": confusion, "by_scene_noise_mapping": grouped, "trials": result}


def experiment():
    development = cohort(DEVELOPMENT_SEEDS)
    limits = envelope([r for r in development if r["mapping"] == "identity"])
    heldout = cohort(HELDOUT_SEEDS)
    return {"protocol": {"width": WIDTH, "height": HEIGHT, "max_code": MAX_CODE,
                         "scenes": SCENES, "noise": NOISE,
                         "development_seeds": DEVELOPMENT_SEEDS, "heldout_seeds": HELDOUT_SEEDS,
                         "mappings": MAPPINGS,
                         "rule": "reject if any feature strictly exceeds plausible development maximum",
                         "limitations": "Wrong means non-identity, not physically impossible. Synthetic families reused across splits; no held-out scene/body validation, sensor truth, CFA, black level, ORF cohort, universal threshold or GPU claim."},
            "development_limits": limits,
            "development": evaluate(development, limits), "heldout": evaluate(heldout, limits)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true", help="include CPU experiment wall time; no process/peak-memory claim")
    args = parser.parse_args()
    start = time.perf_counter()
    report = experiment()
    if args.benchmark:
        report["cpu_seconds"] = time.perf_counter() - start
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
