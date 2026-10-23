"""Synthetic window selection checks; no target data or external processes."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import value_map_window_probe as probe
from test_value_map_probe import encoded_tokens, synthetic_tiff, oracle


class WindowTests(unittest.TestCase):
    def test_windows_match_independently_encoded_tokens_and_fraction_energy(self):
        tokens = [(17 if j == 140 else j % 5, (j * 7 + j // 13) % 32) for j in range(700)]
        payload = encoded_tokens(tokens)
        for start, count in ((0, 128), (128, 256), (256, 137), (640, 60)):
            qs, ss, first, end = probe.parse_window(payload, start, count)
            self.assertEqual(list(zip(qs, ss)), tokens[start:start + count])
            self.assertEqual(first, sum(q + 6 for q, _ in tokens[:start]))
            self.assertEqual(end, sum(q + 6 for q, _ in tokens[:start + count]))
        # A nonzero absolute block offset includes omission and lane parity.
        qs, ss, _, _ = probe.parse_window(payload, 128, 256)
        report = probe.base.token_aggregates(qs, ss)
        self.assertEqual(report["omissions"]["retained_blocks"], 1)
        self.assertEqual(report["omissions"]["escape_omitted_blocks"], 1)
        for cell in report["cells"]:
            for block in cell["blocks"]:
                lo = 128 + 128 * block["block_index"]
                for lane in block["lanes"]:
                    p = lane["absolute_parity"]
                    xs = [probe.base.map_suffix(tokens[j][1], cell["mapping"])
                          for j in range(lo, lo + 128) if p is None or j % 2 == p]
                    self.assertEqual(probe.base.energies(len(xs), lane["A"], lane["V"]), oracle(xs))
        qs, ss, first, end = probe.parse_window(payload, 640, 128)
        self.assertEqual(list(zip(qs, ss)), tokens[640:])
        self.assertEqual(end, sum(q + 6 for q, _ in tokens))

    def test_prefix_storage_is_bounded_and_invalid_or_overrun_windows_fail(self):
        sink = probe.WindowSink(1024, True)
        for _ in range(1024):
            sink.append(2)
        self.assertEqual(sink.values, [])
        self.assertEqual(sink.prefix_bits, 8192)
        for start, count in ((-128, 1), (1, 128), (True, 1), (0, 0),
                             (0, 262145), (100000000, 1)):
            with self.assertRaises(probe.base.ProbeError):
                probe.parse_window(b"", start, count)
        for payload, start in ((b"\x01", 0), (b"\xff", 128)):
            with self.assertRaises(probe.base.ProbeError):
                probe.parse_window(payload, start, 1)

    def test_cli_container_absolute_indices_prefix_equivalence_and_private_errors(self):
        tokens = [(0, j % 32) for j in range(513)]
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "PRIVATE.ORF")
            with open(path, "wb") as stream:
                stream.write(synthetic_tiff(encoded_tokens(tokens)))
            args = ["--sample", "1", "PUBLIC.ORF", path, "--measured-by", "synthetic-user",
                    "--max-tokens", "256"]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(probe.main(args + ["--start-token", "128"]), 0)
            self.assertNotIn(directory, output.getvalue())
            self.assertNotIn("PRIVATE.ORF", output.getvalue())
            result = json.loads(output.getvalue())
            sample = result["sample"]
            self.assertTrue(result["exploratory"])
            self.assertEqual(sample["window_start_bit"], 768)
            self.assertEqual(sample["window_end_bit_exclusive"], 2304)
            self.assertEqual([b["block_index"] for b in sample["cells"][0]["blocks"]], [1, 2])
            prefix = probe.measure(1, "PUBLIC.ORF", path, 0, 256)
            original = probe.base.measure(1, "PUBLIC.ORF", path, 256)
            self.assertEqual(prefix["cells"], original["cells"])
            self.assertEqual(prefix["omissions"], original["omissions"])
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(probe.main(args + ["--start-token", "128"]), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertNotIn(directory, errors.getvalue())
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            probe.main(args + ["--start-token", "1"])


if __name__ == "__main__":
    unittest.main()
