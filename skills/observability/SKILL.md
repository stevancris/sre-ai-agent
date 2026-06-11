---
name: observability
description: >
  Design, review, and improve observability for services: metrics, logs, and distributed
  traces. Use when instrumenting a new service, investigating gaps in visibility, reviewing
  dashboards, building alerting, or diagnosing why an incident was hard to detect. Trigger
  keywords: observability, metrics, logs, tracing, traces, dashboard, alerting,
  instrumentation, OpenTelemetry, Prometheus, Datadog, Grafana, structured logging, spans,
  golden signals, USE method, RED method, four golden signals, visibility, monitoring gap,
  hard to debug, missing metrics, no alerts.
allowed-tools: Read Glob Grep
---

# Observability Skill

## Instructions

### Step 1: Load Context
Read `context/company/tech-stack.md` to identify the observability stack (Datadog,
Prometheus+Grafana, New Relic, etc.) and primary language/framework.

### Step 2: Determine the Mode
- **Instrument new service** — adding observability to a new or existing service
- **Review coverage** — assess gaps in existing observability
- **Build alerting** — create alert rules for a service
- **Dashboard design** — build or improve a service dashboard
- **Incident visibility gap** — why was this incident hard to detect?

---

### Mode: Instrument New Service

#### The Four Golden Signals (start here for every service)

| Signal | What to measure | Example metric name |
|---|---|---|
| **Latency** | Request duration, broken by success/error | `http_request_duration_seconds` |
| **Traffic** | Request rate (RPS / QPS) | `http_requests_total` |
| **Errors** | Error rate (5xx, exceptions) | `http_errors_total` |
| **Saturation** | Resource utilization (CPU, memory, queue depth) | `process_cpu_usage`, `queue_depth` |

#### Instrumentation Checklist

**HTTP Services:**
- [ ] Request count (by method, path, status code)
- [ ] Request latency histogram (P50, P95, P99)
- [ ] Error rate (4xx and 5xx separately)
- [ ] In-flight requests (saturation)
- [ ] Dependency call latency (DB, cache, downstream APIs)
- [ ] Circuit breaker state (if applicable)

**Workers / Background Jobs:**
- [ ] Job execution count (success / failure)
- [ ] Job duration histogram
- [ ] Queue depth (consumer lag)
- [ ] Job retry count
- [ ] Dead-letter queue size

**Databases:**
- [ ] Query latency (by query type)
- [ ] Connection pool utilization
- [ ] Replication lag (for read replicas)
- [ ] Cache hit rate (if applicable)

#### Structured Logging Standards
Every log line must include:
```json
{
  "timestamp": "ISO8601",
  "level": "INFO|WARN|ERROR",
  "service": "service-name",
  "version": "v1.2.3",
  "trace_id": "abc123",
  "span_id": "def456",
  "request_id": "uuid",
  "user_id": "optional",
  "message": "human readable",
  "error": "error string if applicable"
}
```

Never log: passwords, tokens, PII (email, phone, address), credit card numbers.

#### Distributed Tracing
- Add trace context propagation at all service boundaries (HTTP headers, queue message attributes).
- Create spans for: inbound requests, outbound calls, DB queries, cache operations.
- Tag spans with: service name, operation name, status (ok/error), relevant business attributes.

---

### Mode: Review Coverage

Assess against the four golden signals for each service in scope. Flag gaps:

```
Service: <name>
Golden Signal Coverage:
  Latency:    ✓ histogram available, P99 alert configured
  Traffic:    ✓ RPS metric available
  Errors:     ✗ MISSING — no error rate metric
  Saturation: ⚠ CPU only — memory and queue depth missing

Tracing:      ✓ spans present, but missing DB query spans
Logging:      ⚠ logs exist but unstructured (no trace_id)

Priority gaps:
  1. Add error rate metric (blocks SLO measurement)
  2. Add trace_id to log lines (needed for incident correlation)
  3. Add queue depth metric (saturation blind spot)
```

---

### Mode: Build Alerting

For each service, build alert rules using the multi-window burn rate approach:

```yaml
# Example: error rate alert (adapt syntax to your stack)
alert: HighErrorRate
expr: |
  (
    rate(http_errors_total[5m]) / rate(http_requests_total[5m])
  ) > 0.05
for: 2m
labels:
  severity: P1
annotations:
  summary: "Error rate above 5% for {{ $labels.service }}"
  runbook: "<link to runbook>"
```

---

## Guidelines

- Alert on symptoms (user-facing impact), not causes (CPU high).
- Every alert must have a runbook. If no runbook exists, invoke `runbook-generator`.
- Dashboards should tell a story from top (user experience) to bottom (infrastructure).
- Do not alert on metrics that do not require human action.
- Persona (junior-sre): add "learning note" explaining why each golden signal matters.
