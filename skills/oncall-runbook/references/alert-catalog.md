# Alert Catalog

Index of known alerts and their associated runbooks. Add a new entry each time a runbook
is created. This file is used by the oncall-runbook skill to find the right runbook quickly.

---

## Format

```
## <Service Name>
- Alert: <alert-name>
  Runbook: <path-to-runbook.md>
  Severity: P<N>
  Last updated: YYYY-MM-DD
```

---

## Template Entries (replace with your actual alerts)

## API Gateway
- Alert: HighErrorRate5xx
  Runbook: skills/oncall-runbook/references/api-gateway-high-error-rate.md
  Severity: P1
  Last updated: YYYY-MM-DD

- Alert: HighLatencyP99
  Runbook: skills/oncall-runbook/references/api-gateway-high-latency.md
  Severity: P1
  Last updated: YYYY-MM-DD

## Database (PostgreSQL / RDS)
- Alert: ConnectionPoolExhausted
  Runbook: skills/oncall-runbook/references/postgresql-connection-exhaustion.md
  Severity: P1
  Last updated: YYYY-MM-DD

- Alert: ReplicationLagHigh
  Runbook: skills/oncall-runbook/references/postgresql-replication-lag.md
  Severity: P2
  Last updated: YYYY-MM-DD

- Alert: DiskSpaceLow
  Runbook: skills/oncall-runbook/references/rds-disk-space-low.md
  Severity: P1
  Last updated: YYYY-MM-DD

## Cache (Redis / ElastiCache)
- Alert: HighMemoryUsage
  Runbook: skills/oncall-runbook/references/redis-high-memory.md
  Severity: P2
  Last updated: YYYY-MM-DD

- Alert: ConnectionRefused
  Runbook: skills/oncall-runbook/references/redis-connection-refused.md
  Severity: P1
  Last updated: YYYY-MM-DD

## Kubernetes / EKS
- Alert: PodCrashLooping
  Runbook: skills/oncall-runbook/references/k8s-pod-crashloop.md
  Severity: P1
  Last updated: YYYY-MM-DD

- Alert: NodeNotReady
  Runbook: skills/oncall-runbook/references/k8s-node-not-ready.md
  Severity: P1
  Last updated: YYYY-MM-DD

- Alert: HPAMaxReplicasReached
  Runbook: skills/oncall-runbook/references/k8s-hpa-max-replicas.md
  Severity: P2
  Last updated: YYYY-MM-DD

## Message Queue (SQS / Kinesis)
- Alert: DeadLetterQueueDepthHigh
  Runbook: skills/oncall-runbook/references/sqs-dlq-depth-high.md
  Severity: P2
  Last updated: YYYY-MM-DD

- Alert: ConsumerLagHigh
  Runbook: skills/oncall-runbook/references/kinesis-consumer-lag.md
  Severity: P2
  Last updated: YYYY-MM-DD

---

## How to Add a New Entry

1. Create the runbook using the `runbook-generator` skill.
2. Save it to `skills/oncall-runbook/references/<service>-<alert>.md`.
3. Add an entry to this catalog with the correct path, severity, and date.
4. Commit both files to version control.
