#!/usr/bin/env python3
"""Original synthetic packed-16 fixtures; no files or pixel output."""
import pathlib
import contextlib
import hashlib
import io
import json
import stat
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import v0_sensor_controls as probe


def fixture(endian="<", width=36, height=28):
    # Four LONG TIFF fields; payload starts at the end of this one IFD.
    offset = 8 + 2 + 4 * 12 + 4
    fields = ((256, width), (257, height), (273, offset), (279, width * height * 2))
    data = bytearray((b"II" if endian == "<" else b"MM") +
                     struct.pack(endian + "HIH", 0x4f52, 8, 4))
    for tag, value in fields:
        data.extend(struct.pack(endian + "HHII", tag, 4, 1, value))
    data.extend(struct.pack(endian + "I", 0))
    for y in range(height):
        for x in range(width):
            data.extend(struct.pack(endian + "H", 16 * (100 + 3 * y + x) + (x % 2)))
    return bytes(data)


class V0Tests(unittest.TestCase):
    def test_endian_window_coordinates_and_independent_values(self):
        for endian in ("<", ">"):
            data = fixture(endian)
            info = probe.geometry(data)
            self.assertEqual((info["width"], info["height"], info["payload_bytes"]),
                             (36, 28, 2016))
            for (label, x, y, got), expected_y in zip(probe.windows(data, info), (0, 2, 4)):
                self.assertEqual((x, y), (2, expected_y))
                expected = [16 * (100 + 3 * yy + xx) + (xx % 2)
                            for yy in range(y, y + 24) for xx in range(x, x + 32)]
                self.assertEqual(got, expected)

    def test_precision_and_control_accounting(self):
        limits = {key: 1e20 for key in probe.controls.FEATURES}
        report = probe.diagnostic(fixture(), limits)
        self.assertEqual(report["construction_confusion"],
                         {"identity_accepted": 3, "identity_rejected": 0,
                          "nonidentity_accepted": 12, "nonidentity_rejected": 0})
        for row in report["windows"]:
            self.assertEqual(row["nonzero_low_nibbles"], 384)
            identity = row["trials"][0]
            self.assertEqual(identity["changed_values"], 0)
            self.assertEqual(identity["features"]["counts"]["outside"], 0)
            self.assertEqual(identity["features"]["counts"]["lag2_sum_abs"],
                             2 * 24 * 30 + 6 * 22 * 32)
            self.assertEqual(identity["features"]["counts"]["seam_sum_abs"], 24)
            self.assertEqual(row["shift4_min"], 102 + 3 * row["y"])
            self.assertEqual(row["shift4_max"], 202 + 3 * row["y"])

    def test_rejects_wrong_payload_size_and_truncation(self):
        data = bytearray(fixture())
        # StripByteCounts inline value at fourth entry + 8.
        struct.pack_into("<I", data, 8 + 2 + 3 * 12 + 8, 2015)
        for bad in (bytes(data), fixture()[:-1], b"II", b"ZZ" + fixture()[2:]):
            with self.assertRaises(ValueError):
                probe.geometry(bad)

    def test_rejects_cycles_duplicate_and_oversized_descriptors(self):
        original = fixture()
        for pos, value in ((8 + 2 + 4 * 12, 8), (8 + 2 + 4, 5000)):
            data = bytearray(original)
            struct.pack_into("<I", data, pos, value)
            with self.assertRaises(ValueError):
                probe.geometry(bytes(data))
        data = bytearray(original)
        struct.pack_into("<H", data, 8 + 2 + 12, 256)
        with self.assertRaises(ValueError):
            probe.geometry(bytes(data))

    def test_boundaries_and_raw_units_not_classified(self):
        report = probe.diagnostic(fixture(), {key: 0 for key in probe.controls.FEATURES})
        self.assertEqual(report["construction_confusion"]["identity_rejected"], 3)
        self.assertNotIn("rejected_by", report["windows"][0]["stored_word_features"])
        self.assertEqual(sum(report["construction_confusion"].values()), 15)
        self.assertEqual(sum(v["accepted"] + v["rejected"] for v in report["by_mapping"].values()), 15)

    def test_contiguous_multistrip_and_gap_rejection(self):
        original = fixture()
        header = bytearray(original[:62])
        struct.pack_into("<II", header, 8 + 2 + 2 * 12 + 4, 2, 62)
        struct.pack_into("<II", header, 8 + 2 + 3 * 12 + 4, 2, 70)
        tables = struct.pack("<IIII", 78, 222, 144, 1872)
        data = bytes(header) + tables + original[62:]
        info = probe.geometry(data)
        self.assertEqual(info["strips"], 2)
        self.assertEqual([r[3] for r in probe.windows(data, info)],
                         [r[3] for r in probe.windows(original, probe.geometry(original))])
        bad = bytearray(data)
        struct.pack_into("<I", bad, 66, 223)
        with self.assertRaises(ValueError):
            probe.geometry(bytes(bad))

    def test_read_verified_gate_without_file_writes(self):
        data = fixture()

        class FakePath:
            st_mode = stat.S_IFREG
            st_size = len(data)

            def stat(self):
                return self

            def open(self, mode):
                self_mode = mode
                if self_mode != "rb":
                    raise AssertionError("read-only contract")
                return io.BytesIO(data)

        path = FakePath()
        self.assertEqual(probe.read_verified(path, hashlib.sha256(data).hexdigest()), data)
        with self.assertRaises(ValueError):
            probe.read_verified(path, "0" * 64)
        path.st_mode = stat.S_IFDIR
        with self.assertRaises(ValueError):
            probe.read_verified(path, hashlib.sha256(data).hexdigest())

    def test_public_error_output_redacts_local_path(self):
        out = io.StringIO()
        private_path = "DO_NOT_PUBLISH_LOCAL_PATH"
        with mock.patch.object(probe, "read_verified", side_effect=OSError(private_path)):
            with contextlib.redirect_stdout(out):
                result = probe.main(["--sample", "1", "public.ORF", "0" * 64, private_path])
        self.assertEqual(result, 1)
        self.assertNotIn(private_path, out.getvalue())
        self.assertEqual(json.loads(out.getvalue())["samples"][0]["category"],
                         "file_access_hash_or_layout_rejected")


if __name__ == "__main__":
    unittest.main()
