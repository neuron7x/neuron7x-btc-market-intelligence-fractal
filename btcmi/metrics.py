from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

registry = CollectorRegistry()

health = Gauge("btcmi_health", "Health status", registry=registry)
health.set(1)

latency = Histogram(
    "btcmi_latency_seconds",
    "Latency for signal generation",
    registry=registry,
)

signals_total = Counter(
    "btcmi_signals_total", "Total signals processed", registry=registry
)

valid_ratio = Gauge(
    "btcmi_valid_ratio", "Ratio of valid features", registry=registry
)
