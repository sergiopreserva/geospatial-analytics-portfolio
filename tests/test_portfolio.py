import copy
import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from portfolio import haversine_m, run, screen_sites, validate_locations


def location(key="X", lat="4.65", lon="-74.06", name="Example", category="retail"):
    return dict(source_id=key, name=name, category=category, latitude=lat, longitude=lon)


class QualityTests(unittest.TestCase):
    def test_conflicting_identifier_rejects_both_versions(self):
        accepted, rejected, _ = validate_locations([location(), location(lon="-74.07")])
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 2)
        self.assertTrue(all("conflicting_identifier" in p["issues"] for p in rejected))

    def test_colocated_businesses_are_not_silently_deduplicated(self):
        accepted, rejected, report = validate_locations([location(), location(key="Y", name="Other")])
        self.assertEqual(len(accepted), 2)
        self.assertEqual(rejected, [])
        self.assertEqual(report["coincident_location_groups"], [["X", "Y"]])

    def test_axis_swap_is_flagged_without_modifying_input(self):
        rows = [location(lat="-74.06", lon="4.65")]
        original = copy.deepcopy(rows)
        accepted, rejected, _ = validate_locations(rows)
        self.assertEqual(accepted, [])
        self.assertIn("possible_swapped_coordinates", rejected[0]["issues"])
        self.assertEqual(rows, original)

    def test_nonfinite_coordinates_are_rejected(self):
        for value in ["NaN", "inf", "-inf"]:
            with self.subTest(value=value):
                self.assertEqual(validate_locations([location(lat=value)])[0], [])

    def test_identical_normalized_id_retains_one_record(self):
        accepted, rejected, _ = validate_locations([location(), location(key=" x ")])
        self.assertEqual(len(accepted), 1)
        self.assertIn("duplicate_identifier", rejected[0]["issues"])


class ScreeningTests(unittest.TestCase):
    def test_distance_uses_metres(self):
        self.assertEqual(haversine_m(0, 0, 0, 0), 0)
        self.assertAlmostEqual(haversine_m(0, 0, 0, 1), 111195.08, delta=1)

    def test_missing_transport_does_not_become_perfect_access(self):
        with self.assertRaises(ValueError):
            screen_sites([], [])

    def test_end_to_end_reconciles_rows_and_is_deterministic(self):
        import shutil
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            shutil.copytree(ROOT / "data", base / "data")
            shutil.copytree(ROOT / "src", base / "src")
            before = {p.name: p.read_bytes() for p in (base / "data").glob("*.csv")}
            report = run(base)
            quality = report["quality"]
            self.assertEqual(quality["input_rows"], quality["accepted_rows"] + quality["quarantined_rows"])
            self.assertEqual((quality["input_rows"], quality["accepted_rows"], quality["quarantined_rows"]), (32, 21, 11))
            snapshots = {p.name: p.read_bytes() for p in (base / "outputs").iterdir()}
            run(base)
            self.assertEqual(snapshots, {p.name: p.read_bytes() for p in (base / "outputs").iterdir()})
            self.assertEqual(before, {p.name: p.read_bytes() for p in (base / "data").glob("*.csv")})
            for source, digest in report["provenance"]["source_sha256"].items():
                self.assertEqual(hashlib.sha256(before[source]).hexdigest(), digest)
            for result in report["screening"]["scenarios"].values():
                self.assertAlmostEqual(sum(result["weights"].values()), 1)
                self.assertTrue(all(math.isfinite(p["score"]) and 0 <= p["score"] <= 100 for p in result["ranking"]))
            geojson = json.loads((base / "outputs" / "accepted_locations.geojson").read_text())
            first = geojson["features"][0]["geometry"]["coordinates"]
            self.assertEqual(first, [-74.06, 4.65])


if __name__ == "__main__":
    unittest.main()
