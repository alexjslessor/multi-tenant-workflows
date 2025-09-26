

# python otel instrumentation
- https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/#auto-instrumenting-python-logs
- https://opentelemetry.io/docs/zero-code/js/
- https://github.com/open-telemetry/opentelemetry-js-contrib/tree/main/packages/auto-instrumentations-node#supported-instrumentations

# Logs Collection agent (OTLP or Promtail)
OTLP (OpenTelemetry Protocol) only collects traces and metrics, not logs.
- Looking at your Tempo configuration, it only has OTLP receivers for:
- Traces (port 4317/4318)
- Metrics (via metrics_generator)

OTLP does NOT collect logs automatically. For logs you need:
1. Promtail (what we just deployed) - collects Kubernetes pod logs
2. Or your applications must explicitly send logs via OTLP to Loki
3. Or use OpenTelemetry Collector with log receivers

Applications need to be instrumented to send logs via OTLP via pod annotations. 
Promtail is the standard solution for collecting existing Kubernetes pod logs and sending them to Loki.
The Promtail we deployed will automatically collect all pod logs from /var/log/pods/ and send them to Loki, which is what you need for the Grafana Logs drilldown to work.