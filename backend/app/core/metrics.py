"""Lightweight, zero-dependency metrics registry.

Emits the Prometheus text exposition format (https://prometheus.io/docs/instrumenting/exposition_formats/)
so the counters can be scraped by Prometheus or read directly by an uptime monitor.

No external dependency is required at runtime. If `prometheus_client` is ever
installed we could swap this for its Counter/Gauge types, but the text output
below is compatible with standard Prometheus scrapers.
"""
from collections import defaultdict
import threading
import time
from typing import Dict

_lock = threading.Lock()

# {metric_name -> {label: value}}
counters: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
gauges: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
_metadata: Dict[str, str] = {}


def inc(name: str, labels: Dict[str, str] = None, value: float = 1.0) -> None:
    """Increment a counter, optionally under a label key."""
    key = _labels_key(labels)
    with _lock:
        counters[name][key] += value


def set_gauge(name: str, value: float, labels: Dict[str, str] = None) -> None:
    """Set a gauge value under an optional label key."""
    key = _labels_key(labels)
    with _lock:
        gauges[name][key] = value


def describe(name: str, help_text: str) -> None:
    """Register a help string for a metric (emitted alongside it)."""
    with _lock:
        _metadata[name] = help_text


def _labels_key(labels: Dict[str, str]) -> str:
    if not labels:
        return ""
    # Sort labels for a stable, deterministic label set.
    parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return parts


def render() -> str:
    """Render all metrics in Prometheus text exposition format."""
    lines = []

    for name, by_label in counters.items():
        lines.append(f"# HELP {name} {_metadata.get(name, '')}")
        lines.append(f"# TYPE {name} counter")
        for key, value in by_label.items():
            if key:
                lines.append(f"{name}{{{key}}} {value:.0f}")
            else:
                lines.append(f"{name} {value:.0f}")

    for name, by_label in gauges.items():
        lines.append(f"# HELP {name} {_metadata.get(name, '')}")
        lines.append(f"# TYPE {name} gauge")
        for key, value in by_label.items():
            if key:
                lines.append(f"{name}{{{key}}} {value}")
            else:
                lines.append(f"{name} {value}")

    lines.append(f"scrape_timestamp_seconds {time.time()}")
    return "\n".join(lines) + "\n"


# Pre-register the core metrics used across the app.
describe("scrape_runs_total", "Total scrape task executions.")
describe("scrape_jobs_fetched_total", "Jobs fetched by source, labeled by source.")
describe("scrape_errors_total", "Scrape errors by source.")
describe("scrape_runs_active", "Currently active scrape runs.")
describe("jobs_total_db", "Total active jobs currently in PostgreSQL.")
describe("alerts_sent_total", "Job alerts emailed to users.")
