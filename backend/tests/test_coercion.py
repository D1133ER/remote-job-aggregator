"""Tests for ingest-time normalization helpers in the scraping pipeline.

These guard against the two failure modes that broke the real-time scrape:
(1) scrapers returning ISO strings / epoch ints for posted_at instead of
datetime objects (asyncpg rejects strings for a TIMESTAMPTZ column), and
(2) string fields overflowing their VARCHAR columns (e.g. Greenhouse
location strings listing many cities).
"""
import unittest
from datetime import datetime, timezone

from app.tasks.scraping_tasks import (
    _coerce_datetime,
    _coerce_datetimes,
    _coerce_string_lengths,
)


class DatetimeCoercionTests(unittest.TestCase):
    def test_iso_string_direct(self):
        self.assertEqual(
            _coerce_datetime("2026-09-02T19:59:53"),
            datetime(2026, 9, 2, 19, 59, 53, tzinfo=timezone.utc),
        )

    def test_iso_string_with_offset(self):
        dt = _coerce_datetime("2026-09-02T10:22:15-04:00")
        self.assertEqual(dt.utcoffset().total_seconds(), -14400)

    def test_iso_string_with_z_suffix(self):
        dt = _coerce_datetime("2026-09-01T12:00:00Z")
        self.assertEqual(dt.tzinfo, timezone.utc)

    def test_epoch_int(self):
        dt = _coerce_datetime(1725292800)
        self.assertEqual(dt.tzinfo, timezone.utc)

    def test_passes_through_datetime(self):
        now = datetime(2026, 9, 5, tzinfo=timezone.utc)
        self.assertIs(_coerce_datetime(now), now)

    def test_none_and_garbage(self):
        self.assertIsNone(_coerce_datetime(None))
        self.assertIsNone(_coerce_datetime("not-a-date"))
        self.assertIsNone(_coerce_datetime(-99999999999999))

    def test_coerce_datetimes_applies_to_fields(self):
        out = _coerce_datetimes({"posted_at": "2026-09-02T19:59:53", "noop": "x"})
        self.assertIsInstance(out["posted_at"], datetime)
        self.assertEqual(out["noop"], "x")


class StringCoercionTests(unittest.TestCase):
    def test_truncates_overlong_string(self):
        out = _coerce_string_lengths({"location": "x" * 500})
        self.assertEqual(len(out["location"]), 200)

    def test_leaves_short_strings(self):
        out = _coerce_string_lengths({"title": "Backend Engineer"})
        self.assertEqual(out["title"], "Backend Engineer")

    def test_leaves_non_strings(self):
        value = ["python", "postgres"]
        out = _coerce_string_lengths({"skills": value})
        self.assertIs(out["skills"], value)

    def test_unknown_fields_untouched(self):
        long_value = "y" * 10000
        out = _coerce_string_lengths({"description": long_value})
        self.assertIs(out["description"], long_value)


if __name__ == "__main__":
    unittest.main()