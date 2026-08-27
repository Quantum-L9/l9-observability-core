# Non-goals

`l9-observability-core` intentionally does not implement:

- a telemetry collector
- an OpenTelemetry SDK wrapper
- a Prometheus registry
- a logging configuration framework
- a trace context middleware
- an HTTP or MCP server
- an event bus
- persistence or retention
- Grafana, Tempo, Loki, Jaeger, or dashboard definitions
- alerting or SLO engines
- anomaly detection
- retry orchestration
- agent evaluation
- autonomous repair
- policy promotion
- CI workflows
- deployment manifests

Those concerns may consume the canonical contracts but remain owned elsewhere.
