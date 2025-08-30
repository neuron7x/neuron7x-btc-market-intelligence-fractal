#!/usr/bin/env python3
"""Prometheus exporter for BTC Market Intelligence metrics.

This script runs the appropriate BTCMI runner on a JSON payload and exposes
key values as Prometheus metrics.  The following metrics are provided:

* ``btcmi_overall_signal`` – overall trading signal (gauge)
* ``btcmi_overall_signal_l1`` – level 1 signal when available (gauge)
* ``btcmi_overall_signal_l2`` – level 2 signal when available (gauge)
* ``btcmi_overall_signal_l3`` – level 3 signal when available (gauge)
* ``btcmi_confidence`` – signal confidence score (gauge)
* ``btcmi_vol_regime_pctl`` – input volatility regime percentile (gauge)
* ``btcmi_router_path`` – current router path (gauge with ``path`` label)

The exporter reloads the input file on every scrape.  Any errors encountered
while loading the file or running the model result in a ``500`` response but
the server remains available for subsequent requests.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    generate_latest,
)

sys.path.append(str(Path(__file__).resolve().parents[2]))

from btcmi.runner import run_v1, run_v2


log = logging.getLogger(__name__)


# Metrics registry and metric objects
REGISTRY = CollectorRegistry()
OVERALL_SIGNAL = Gauge(
    "btcmi_overall_signal",
    "Overall trading signal",
    registry=REGISTRY,
)
OVERALL_SIGNAL_L1 = Gauge(
    "btcmi_overall_signal_l1",
    "Level 1 signal",
    registry=REGISTRY,
)
OVERALL_SIGNAL_L2 = Gauge(
    "btcmi_overall_signal_l2",
    "Level 2 signal",
    registry=REGISTRY,
)
OVERALL_SIGNAL_L3 = Gauge(
    "btcmi_overall_signal_l3",
    "Level 3 signal",
    registry=REGISTRY,
)
CONFIDENCE = Gauge(
    "btcmi_confidence",
    "Signal confidence",
    registry=REGISTRY,
)
VOL_REGIME = Gauge(
    "btcmi_vol_regime_pctl",
    "Volatility regime percentile",
    registry=REGISTRY,
)
ROUTER_PATH = Gauge(
    "btcmi_router_path",
    "Router path in use",
    ["path"],
    registry=REGISTRY,
)


def _run(data: dict) -> dict:
    """Run the BTCMI engine returning the result."""

    mode = data.get("mode", "v1")
    runner = run_v2 if mode == "v2.fractal" else run_v1
    return runner(data, None, out_path=None)


def collect_metrics(payload_path: Path) -> bytes:
    """Collect metrics by running the model on ``payload_path``.

    Parameters
    ----------
    payload_path:
        Path to the JSON payload to run through the engine.
    Returns
    -------
    bytes
        Prometheus-formatted metrics.
    """

    data = json.loads(payload_path.read_text())
    result = _run(data)
    summary = result.get("summary", {})

    # Update metrics
    OVERALL_SIGNAL.set(summary.get("overall_signal", float("nan")))
    OVERALL_SIGNAL_L1.set(summary.get("overall_signal_L1", float("nan")))
    OVERALL_SIGNAL_L2.set(summary.get("overall_signal_L2", float("nan")))
    OVERALL_SIGNAL_L3.set(summary.get("overall_signal_L3", float("nan")))
    CONFIDENCE.set(summary.get("confidence", float("nan")))
    VOL_REGIME.set(float(data.get("vol_regime_pctl", float("nan"))))

    path = summary.get("router_path", "unknown")
    ROUTER_PATH.labels(path=path).set(1)

    return generate_latest(REGISTRY)


class MetricsHandler(BaseHTTPRequestHandler):
    """Serve Prometheus metrics for the BTCMI project."""

    payload_file: Path  # injected at server startup

    def do_GET(self) -> None:  # pragma: no cover - simple I/O wrapper
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return
        try:
            body = collect_metrics(self.payload_file)
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:  # noqa: BLE001
            log.exception("metrics_collection_failed")
            self.send_response(500)
            self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="BTCMI Prometheus exporter")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "examples"
        / "intraday_fractal.json",
        help="Path to input JSON payload",
    )
    parser.add_argument("--port", type=int, default=9101)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    MetricsHandler.payload_file = args.input
    HTTPServer(("0.0.0.0", args.port), MetricsHandler).serve_forever()


if __name__ == "__main__":
    main()
