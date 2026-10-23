#!/usr/bin/env python3
"""Independent small arithmetic/label checks for synthetic #301 controls."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sensor_rejection_controls as probe


class ControlsTests(unittest.TestCase):
    def test_exact_features_against_pair_lists(self):
        width, height = 7, 5
        values = [(-1 if i == 0 else 3 * i * i) for i in range(width * height)]
        f = probe.features(values, width, height)
        grid = [values[y * width:(y + 1) * width] for y in range(height)]
        pairs = [(grid[y][x], grid[y][x + 2]) for y in range(height) for x in range(width - 2)]
        pairs += [(grid[y][x], grid[y + 2][x]) for y in range(height - 2) for x in range(width)]
        lanes = [[grid[y][x] for y in range(height) for x in range(width)
                  if (y % 2, x % 2) == (a, b)] for a in range(2) for b in range(2)]
        seam = [abs(row[width // 2] - row[width // 2 - 1]) for row in grid]
        counts = f["counts"]
        self.assertEqual(counts, {"values": 35, "outside": 1,
                                 "lag2_sum_abs": sum(abs(a - b) for a, b in pairs),
                                 "lag2_pairs": len(pairs),
                                 "lane_sums": [sum(v) for v in lanes],
                                 "lane_counts": [len(v) for v in lanes],
                                 "seam_sum_abs": sum(seam), "seam_pairs": height})
        lane_means = [sum(v) / len(v) for v in lanes]
        self.assertEqual(f["scalars"], {"outside_fraction": 1 / 35,
                                       "lag2_mean_abs": sum(abs(a - b) for a, b in pairs) / len(pairs),
                                       "lane_mean_spread": max(lane_means) - min(lane_means),
                                       "seam_mean_abs": sum(seam) / height})

    def test_mappings_are_reversible(self):
        original = [i % 4096 for i in range(768)]
        for mapping in probe.MAPPINGS:
            with self.subTest(mapping=mapping):
                changed = probe.transform(original, mapping)
                self.assertEqual(probe.transform(changed, mapping, inverse=True), original)
                if mapping != "identity":
                    self.assertNotEqual(changed, original)

    def test_complement_is_unidentifiable_by_frozen_features(self):
        for scene in probe.SCENES:
            values = probe.synthetic(scene, 16, 100)
            original = probe.features(values, 32, 24)["scalars"]
            changed = probe.features(probe.transform(values, "complement"), 32, 24)["scalars"]
            for key in probe.FEATURES:
                self.assertAlmostEqual(original[key], changed[key], places=10)

    def test_constant_and_range_guard(self):
        constant = [32] * 16
        f = probe.features(constant, 4, 4)
        self.assertEqual(set(f["scalars"].values()), {0})
        shifted = probe.features(probe.transform(constant, "offset_range"), 4, 4)
        self.assertEqual(probe.classify(shifted, f["scalars"]), ["outside_fraction"])

    def test_training_only_and_confusion_accounting(self):
        report = probe.experiment()
        dev = report["development"]["trials"]
        heldout = report["heldout"]["trials"]
        expected = {k: max(r["features"]["scalars"][k] for r in dev if r["mapping"] == "identity")
                    for k in probe.FEATURES}
        self.assertEqual(report["development_limits"], expected)
        self.assertFalse(set(r["seed"] for r in dev) & set(r["seed"] for r in heldout))
        for split in ("development", "heldout"):
            outcome = report[split]
            self.assertEqual(len(outcome["trials"]), 90)
            self.assertEqual(sum(outcome["confusion"].values()), 90)
            self.assertEqual(outcome["confusion"]["plausible_accepted"] + outcome["confusion"]["plausible_rejected"], 18)
            self.assertEqual(outcome["confusion"]["wrong_accepted"] + outcome["confusion"]["wrong_rejected"], 72)
            self.assertEqual(sum(v["accepted"] + v["rejected"] for v in outcome["by_scene_noise_mapping"].values()), 90)
            for row in outcome["trials"]:
                if row["mapping"] == "offset_range":
                    self.assertIn("outside_fraction", row["rejected_by"])
        self.assertEqual(report["development"]["confusion"]["plausible_rejected"], 0)

    def test_noise_response_and_invalid_shapes(self):
        low = probe.features(probe.synthetic("dark", 2, 1), 32, 24)
        high = probe.features(probe.synthetic("dark", 16, 1), 32, 24)
        self.assertGreater(high["scalars"]["lag2_mean_abs"], low["scalars"]["lag2_mean_abs"])
        with self.assertRaises(ValueError):
            probe.features([0] * 16, 2, 8)
        with self.assertRaises(ValueError):
            probe.transform([0] * 5, "affine_permutation")
        with self.assertRaises(ValueError):
            probe.envelope([])


if __name__ == "__main__":
    unittest.main()
