#!/usr/bin/env python3
"""Independent grammar/cost/selection failure controls for #298 toy harness."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("bounded_codec_controls", Path(__file__).with_name("bounded_codec_controls.py"))
codec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(codec)


class GrammarTests(unittest.TestCase):
    def test_explicit_codewords(self):
        # Direct hand-derived expectations, independent of encoder/decoder agreement.
        for model, expected in [(0, "1010010001"), (1, "1011010011"),
                                (2, "100101110111"), (3, "1001000101")]:
            self.assertEqual(codec.body([0, 1, 2, 3], model), expected)
        self.assertEqual(codec.encode([0, 1, 2, 3]), "00000010000011011" + "0" * 7)
        self.assertEqual(codec.body([3, 3, 3], 6), "000111")

    def test_invalid_inputs(self):
        for values in ([4], [-1], [True], [1.0], [0] * 256):
            with self.assertRaises(ValueError):
                codec.encode(values)
        for model in (-1, 12, True, 1.0):
            with self.assertRaises(ValueError):
                codec.encode([0], model)

    def test_strict_failures(self):
        valid = codec.encode([0], 0)
        bad = ["", "0", "x" * 16, valid + "00000000", valid[:-1] + "1",
               "1" + "00000000" + "1100" + "000",  # unused model
               "1" + "00000001" + "0000" + "000",  # missing delimiter
               "1" + "00000001" + "0000" + "00001000000"]  # quotient 4
        for bits in bad:
            with self.subTest(bits=bits), self.assertRaises(ValueError):
                codec.decode(bits)

    def test_maximum_count_and_all_byte_truncations(self):
        values = [i % 4 for i in range(255)]
        for model in (None,) + codec.MODELS:
            packet = codec.encode(values, model)
            self.assertEqual(codec.decode(packet), (values, model))
            for end in range(0, len(packet), 8):
                with self.assertRaises(ValueError):
                    codec.decode(packet[:end])
        with self.assertRaises(ValueError):
            codec.decode("0" * 1048)

    def test_exhaustive(self):
        counts = codec.exhaustive(5)
        self.assertEqual(counts["sequences"], 1365)
        self.assertEqual(counts["roundtrips"], 17745)
        self.assertEqual(counts["accepted_short_packets"], 157)
        self.assertEqual(counts["rejected_short_packets"], 65635)

    def test_frozen_selection_and_oracle_optimism(self):
        result = codec.experiment([[0] * 64], [[3] * 64])
        self.assertEqual(result["frozen_model"], 0)
        self.assertEqual(result["validation_frozen_bits"], 272)
        self.assertEqual(result["validation_raw_bits"], 144)
        self.assertEqual(result["validation_oracle_exploratory_bits"], 80)
        self.assertEqual(result["roundtrip_failures"], 0)
        # Validation must never silently select/re-fit the frozen rule.
        changed = codec.experiment([[0] * 64], [[0] * 64])
        self.assertEqual(changed["frozen_model"], result["frozen_model"])
        self.assertEqual([r["discovery_bits"] for r in changed["ledger"]],
                         [r["discovery_bits"] for r in result["ledger"]])

    def test_model_cost_can_reverse_payload_win(self):
        values = [0, 3, 3]
        winner = min(codec.MODELS, key=lambda m: (codec.costs(values, m)["payload_bits"], m))
        modeled, raw = codec.costs(values, winner), codec.costs(values, None)
        self.assertLess(modeled["payload_bits"], raw["payload_bits"])
        self.assertGreater(modeled["total_bits"], raw["total_bits"])
        self.assertEqual((modeled["total_bits"], raw["total_bits"]), (24, 16))
        for score in (modeled, raw):
            self.assertEqual(score["total_bits"], sum(score[key] for key in
                             ("payload_bits", "model_bits", "kind_count_bits", "padding_bits")))


if __name__ == "__main__":
    unittest.main()
