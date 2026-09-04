"""Tests for the in-process metrics registry."""
import unittest
from app.core import metrics


class MetricsRegistryTests(unittest.TestCase):
    def setUp(self):
        metrics.gauges.clear()
        # Don't clear counters between tests so we can rely on the pre-registered
        # help strings. Instead, just reset the scrape test ones.
        for name in list(metrics.counters):
            metrics.counters[name].clear()

    def test_inc_increments_counter(self):
        metrics.inc("scrape_runs_total")
        self.assertEqual(metrics.counters["scrape_runs_total"][""], 1)
        metrics.inc("scrape_runs_total")
        self.assertEqual(metrics.counters["scrape_runs_total"][""], 2)

    def test_inc_with_labels(self):
        metrics.inc("scrape_errors_total", {"source": "remotive"})
        self.assertEqual(metrics.counters["scrape_errors_total"]['source="remotive"'], 1)

    def test_set_gauge(self):
        metrics.set_gauge("jobs_total_db", 1423)
        self.assertEqual(metrics.gauges["jobs_total_db"][""], 1423.0)

    def test_render_output_is_valid_prometheus_format(self):
        metrics.inc("scrape_runs_total", value=3)
        metrics.set_gauge("jobs_total_db", 7)
        output = metrics.render()
        self.assertIn("# TYPE scrape_runs_total counter", output)
        self.assertIn("scrape_runs_total 3", output)
        self.assertIn("# TYPE jobs_total_db gauge", output)
        self.assertIn("jobs_total_db 7", output)
        self.assertIn("scrape_timestamp_seconds", output)

    def test_describe_registers_help(self):
        metrics.describe("custom_counter", "A test metric")
        self.assertEqual(metrics._metadata["custom_counter"], "A test metric")


if __name__ == "__main__":
    unittest.main()