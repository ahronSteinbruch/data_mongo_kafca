#!/usr/bin/env python3
"""
custom_exporter_template.py
============================
Approved template for custom Prometheus exporters.
Follows the internal Custom Metrics Exporters Best-Practice Guide v1.0.

Usage
-----
Copy this file, replace every placeholder marked with <REPLACE_ME>, and
implement _collect_metrics() with your actual collection logic.

Run:
    python custom_exporter_template.py --port 9000 --log-level INFO

Validate output:
    curl -s http://localhost:9000/metrics | promtool check metrics
"""

import argparse
import logging
import sys
import time
from http.server import HTTPServer
from typing import Generator

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    MetricsHandler,
    make_wsgi_app,
)
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

# ─────────────────────────────────────────────────────────────────────────────
# RULE 1 (Section 4): Replace this with your exporter's namespace.
# All metric names will be prefixed with this value.
# Example: "mydb", "kafka_consumer", "payment_service"
# ─────────────────────────────────────────────────────────────────────────────
NAMESPACE = "<REPLACE_ME>"          # e.g. "mydb_exporter"
DEFAULT_PORT = 9000                 # <REPLACE_ME> — pick a port, register it
DEFAULT_SCRAPE_INTERVAL = 30        # seconds between background collections
DEFAULT_SCRAPE_TIMEOUT  = 25        # seconds before a collection is aborted

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SELF-OBSERVABILITY METRICS (Section 9.3 — mandatory for every exporter)
# Do NOT rename these. They are used by the standard alert rules.
# ─────────────────────────────────────────────────────────────────────────────
SCRAPE_DURATION = Histogram(
    f"{NAMESPACE}_scrape_duration_seconds",
    "Time taken for one collection cycle",
    labelnames=["collector"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

SCRAPE_ERRORS = Counter(
    f"{NAMESPACE}_scrape_errors_total",
    "Total number of errors during collection, by collector and error class",
    labelnames=["collector", "error_class"],
)

BUILD_INFO = Info(
    f"{NAMESPACE}_build",
    "Build metadata for this exporter",
)
BUILD_INFO.info({
    "version": "1.0.0",          # <REPLACE_ME>
    "revision": "unknown",        # <REPLACE_ME> — set from CI env var
})


# ─────────────────────────────────────────────────────────────────────────────
# YOUR METRICS (Section 4 — naming rules, Section 6 — type selection)
#
# Rules enforced here:
#  - Names use base units (seconds, bytes, not ms / percent)
#  - Counters end with _total
#  - No label names inside metric names
#  - No dynamic metric names (no variables in metric name strings)
# ─────────────────────────────────────────────────────────────────────────────

# Example counter — replace with your own
# RULE: Only increases. Track events, requests, errors.
EXAMPLE_REQUESTS = Counter(
    f"{NAMESPACE}_requests_total",
    "Total requests processed by this system",
    labelnames=["status"],          # RULE: bounded label. "status" has ~5 values.
)

# Example gauge — replace with your own
# RULE: Can go up and down. Track current state.
EXAMPLE_ACTIVE_CONNECTIONS = Gauge(
    f"{NAMESPACE}_active_connections",
    "Number of currently active connections to the target system",
    labelnames=["pool"],            # RULE: bounded label.
)

# Example histogram — replace with your own
# RULE: Use for any latency or size measurement. Always use seconds/bytes.
# RULE: Set buckets appropriate for your domain. These are for a DB query.
EXAMPLE_QUERY_DURATION = Histogram(
    f"{NAMESPACE}_query_duration_seconds",
    "Duration of queries against the target system in seconds",
    labelnames=["operation"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# Example ratio gauge — replace with your own
# RULE: Ratios must be 0–1, not 0–100.
EXAMPLE_CACHE_HIT_RATIO = Gauge(
    f"{NAMESPACE}_cache_hit_ratio",
    "Cache hit ratio (0.0 = no hits, 1.0 = all hits)",
)


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTOR CLASS
# ─────────────────────────────────────────────────────────────────────────────

class ExporterCollector:
    """
    Wraps the collection logic for one logical group of metrics.
    One class per logical subsystem is recommended.
    """

    def __init__(self, target_config: dict):
        """
        Args:
            target_config: connection parameters for the target system.
                           Load from environment variables or a config file.
                           NEVER hard-code credentials here.
        """
        self.target_config = target_config
        self._client = None       # lazy-initialised connection

    def _connect(self):
        """
        Establish (or re-establish) connection to the target system.
        RULE (Section 9.2): Use read-only access. Set a statement timeout.
        """
        # <REPLACE_ME> — implement your connection logic
        # Example for a DB:
        #   self._client = psycopg2.connect(
        #       host=self.target_config["host"],
        #       port=self.target_config["port"],
        #       dbname=self.target_config["dbname"],
        #       user=self.target_config["user"],
        #       password=self.target_config["password"],
        #       options="-c default_transaction_read_only=on -c statement_timeout=10000",
        #   )
        raise NotImplementedError

    def collect(self) -> None:
        """
        Main collection entry point. Called on each scrape cycle.
        Populates Prometheus metrics. Records duration and errors.
        """
        collector_name = self.__class__.__name__

        start = time.monotonic()
        try:
            self._collect_metrics()
        except TimeoutError as exc:
            SCRAPE_ERRORS.labels(
                collector=collector_name,
                error_class="TimeoutError",
            ).inc()
            log.warning("Collection timed out: %s", exc)
        except ConnectionError as exc:
            SCRAPE_ERRORS.labels(
                collector=collector_name,
                error_class="ConnectionError",
            ).inc()
            log.error("Connection error during collection: %s", exc)
            self._client = None   # force reconnect on next cycle
        except Exception as exc:  # pylint: disable=broad-except
            SCRAPE_ERRORS.labels(
                collector=collector_name,
                error_class=type(exc).__name__,
            ).inc()
            log.exception("Unexpected error during collection: %s", exc)
        finally:
            duration = time.monotonic() - start
            SCRAPE_DURATION.labels(collector=collector_name).observe(duration)
            log.debug("Collection cycle completed in %.3fs", duration)

    def _collect_metrics(self) -> None:
        """
        Implement your actual collection logic here.

        Guidelines:
        - Do NOT fetch unbounded data sets without pagination.
        - Do NOT issue N+1 queries (batch lookups).
        - Do NOT store sensitive data in label values.
        - DO set timeouts on every external call.
        - DO use read-only access to the source system.
        - DO document each metric's expected cardinality.

        Example — replace with real queries:
        """
        # <REPLACE_ME>
        #
        # Example:
        #   rows = self._client.execute("SELECT status, count(*) FROM requests GROUP BY status")
        #   for status, count in rows:
        #       EXAMPLE_REQUESTS.labels(status=status).inc(count)
        #
        #   EXAMPLE_ACTIVE_CONNECTIONS.labels(pool="primary").set(
        #       self._client.execute("SELECT count(*) FROM pg_stat_activity")[0][0]
        #   )
        raise NotImplementedError


# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND COLLECTION LOOP
# (pre-compute expensive queries so /metrics always responds fast)
# ─────────────────────────────────────────────────────────────────────────────

def collection_loop(collector: ExporterCollector, interval: int) -> None:
    """
    Runs collection on a fixed interval in a background thread.
    The /metrics endpoint serves the last cached result immediately.
    RULE (Section 9.1): /metrics must never block on slow operations.
    """
    while True:
        collector.collect()
        time.sleep(interval)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP SERVER
# ─────────────────────────────────────────────────────────────────────────────

def create_server(port: int) -> HTTPServer:
    """
    Creates the HTTP server for the /metrics endpoint.
    RULE (Section 8.2): bind to a private interface unless mTLS is in place.
    """
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)
    return server


# ─────────────────────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"{NAMESPACE} Prometheus exporter",
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to expose /metrics on (default: {DEFAULT_PORT})")
    parser.add_argument("--scrape-interval", type=int, default=DEFAULT_SCRAPE_INTERVAL,
                        help=f"Seconds between collection cycles (default: {DEFAULT_SCRAPE_INTERVAL})")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level (default: INFO)")
    # <REPLACE_ME> — add your target-specific arguments
    # parser.add_argument("--db-host", required=True, help="Database host")
    # parser.add_argument("--db-port", type=int, default=5432)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )

    # <REPLACE_ME> — assemble your target config from args / env vars
    # RULE (Section 8.1): NEVER hard-code credentials. Read from environment.
    import os
    target_config = {
        # "host":     os.environ["TARGET_HOST"],
        # "port":     int(os.environ.get("TARGET_PORT", "5432")),
        # "user":     os.environ["TARGET_USER"],
        # "password": os.environ["TARGET_PASSWORD"],   # from secret manager
    }

    collector = ExporterCollector(target_config=target_config)

    # Run first collection synchronously so metrics are populated before
    # the HTTP server starts accepting requests.
    log.info("Running initial collection...")
    collector.collect()

    # Start background collection loop in a daemon thread
    import threading
    t = threading.Thread(
        target=collection_loop,
        args=(collector, args.scrape_interval),
        daemon=True,
        name="collection-loop",
    )
    t.start()

    log.info("Starting HTTP server on port %d", args.port)
    server = create_server(args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION COMMANDS (run these before submitting a PR)
# ─────────────────────────────────────────────────────────────────────────────
#
#   # 1. Check metric output format
#   curl -s http://localhost:9000/metrics | promtool check metrics
#
#   # 2. Expected self-observability metrics to verify manually
#   curl -s http://localhost:9000/metrics | grep -E "^(mydb_exporter_scrape|mydb_exporter_build)"
#
#   # 3. Confirm no PII or secrets in output
#   curl -s http://localhost:9000/metrics | grep -iE "(password|secret|token|email|ip=)"
#   # ^ should return zero lines
#
# ─────────────────────────────────────────────────────────────────────────────
