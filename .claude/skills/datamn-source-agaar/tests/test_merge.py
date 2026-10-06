import csv
import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))  # fetch_data imports agaar_client


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SKILL_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fetch = load_module("agaar_fetch", "fetch_data.py")
HOURLY = fetch.FREQS["hourly"]
DAILY = fetch.FREQS["daily"]


def site_hourly(lastdata, **values):
    """A getRealChart hourly row as the site returns it."""
    row = {"DATA_TIME2": "2026-08-10:05", "LASTDATA": lastdata, "PM25_YN": "Y",
           "KHAI_VALUE": "61", "KHAI_ITEM_CODE": "10008", "KHAI_GRADE": "2"}
    for item in fetch.ITEMS:
        row["VALUE_" + item] = values.get(fetch.ITEMS[item]["key"])
    return row


def merge(rows, spec=HOURLY):
    return fetch.merge_all(rows, spec["key"], spec["conc"], spec["values"])


def roundtrip(rows, spec=HOURLY):
    """Write rows to CSV and read them back, as the archive stores them."""
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "month.csv")
        fetch.write_csv(path, spec["cols"], rows)
        return fetch.read_csv(path)


class ArchiveMergeTest(unittest.TestCase):
    def test_validated_aqi_only_row_keeps_archived_concentrations(self):
        # Archive written before validation: real-time concentrations.
        old = roundtrip(merge([fetch.parse_hourly("12401", site_hourly("N", pm10=51, pm25=23, no2=10))]))
        self.assertEqual(old[0]["pm25"], "23")
        # After NAMEM validates the month the site sends AQI only.
        new = [fetch.parse_hourly("12401", site_hourly("Y"))]
        [row] = merge(old + new)
        self.assertEqual(row["validated"], 1)            # validation flag from the new row
        self.assertEqual(row["aqi"], 61)                 # AQI from the new row
        self.assertEqual(row["pm25"], "23")              # concentrations kept
        self.assertEqual(row["pm10"], "51")
        self.assertEqual(row["no2"], "10")
        self.assertEqual(row["concentrations_source"], "realtime")

    def test_same_fetch_validated_and_realtime_rows_are_merged(self):
        raw = [site_hourly("N", pm25=23), site_hourly("Y")]
        [row] = merge([fetch.parse_hourly("12401", r) for r in raw])
        self.assertEqual(row["validated"], 1)
        self.assertEqual(row["pm25"], 23)
        self.assertEqual(row["concentrations_source"], "realtime")

    def test_validated_values_beat_realtime_values(self):
        old = roundtrip(merge([fetch.parse_daily("10101", {
            "DATA_TIME": "2026-08-10", "LASTDATA": "N", "PM25_YN": "Y", "VALUE_10008": 12.7})], DAILY), DAILY)
        new = [fetch.parse_daily("10101", {
            "DATA_TIME": "2026-08-10", "LASTDATA": "Y", "PM25_YN": "Y", "VALUE_10008": 13.1})]
        [row] = merge(old + new, DAILY)
        self.assertEqual(row["pm25"], 13.1)
        self.assertEqual(row["concentrations_source"], "validated")

    def test_newer_realtime_values_replace_older_realtime_values(self):
        old = roundtrip(merge([fetch.parse_hourly("12401", site_hourly("N", pm25=23))]))
        [row] = merge(old + [fetch.parse_hourly("12401", site_hourly("N", pm25=25))])
        self.assertEqual(row["pm25"], 25)

    def test_fields_merge_individually(self):
        old = roundtrip(merge([fetch.parse_hourly("12401", site_hourly("N", pm25=23))]))
        [row] = merge(old + [fetch.parse_hourly("12401", site_hourly("Y", pm10=40))])
        self.assertEqual(row["pm25"], "23")
        self.assertEqual(row["pm10"], 40)
        self.assertEqual(row["concentrations_source"], "mixed")

    def test_rows_missing_from_new_fetch_are_kept(self):
        old = roundtrip(merge([fetch.parse_hourly("12401", site_hourly("N", pm25=23))]))
        self.assertEqual(len(merge(old + [])), 1)

    def test_archive_rows_from_before_the_source_column_are_inferred(self):
        legacy = {"station_code": "12401", "datetime": "2026-08-10 04:00", "date": "2026-08-10",
                  "hour": "5", "validated": "0", "pm25": "23", "aqi": "61", "pm25_withheld": "0"}
        [row] = merge([legacy, fetch.parse_hourly("12401", site_hourly("Y"))])
        self.assertEqual(row["pm25"], "23")
        self.assertEqual(row["concentrations_source"], "realtime")

    def test_withheld_pm25_stays_blank(self):
        old = roundtrip(merge([fetch.parse_hourly("12401", site_hourly("N", pm25=23))]))
        withheld = site_hourly("Y")
        withheld["PM25_YN"] = "N"
        [row] = merge(old + [fetch.parse_hourly("12401", withheld)])
        self.assertEqual(row["pm25"], "")

    def test_csv_uses_lf_line_endings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "month.csv"
            fetch.write_csv(str(path), HOURLY["cols"],
                            merge([fetch.parse_hourly("12401", site_hourly("N", pm25=23))]))
            self.assertNotIn(b"\r", path.read_bytes())


class CompletenessTest(unittest.TestCase):
    today = date(2026, 10, 6)

    def test_unvalidated_month_stays_open(self):
        self.assertFalse(fetch.is_complete([], False, 0, (2026, 5), self.today))

    def test_validated_month_is_complete(self):
        self.assertTrue(fetch.is_complete([], False, 10, (2026, 5), self.today))

    def test_old_unvalidated_month_is_given_up_on(self):
        self.assertTrue(fetch.is_complete([], False, 0, (2025, 10), self.today))

    def test_current_month_failures_and_partial_runs_are_never_complete(self):
        self.assertFalse(fetch.is_complete([], False, 10, (2026, 10), self.today))
        self.assertFalse(fetch.is_complete(["12401"], False, 10, (2026, 5), self.today))
        self.assertFalse(fetch.is_complete([], True, 10, (2026, 5), self.today))


if __name__ == "__main__":
    unittest.main()
