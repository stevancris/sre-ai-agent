# Knowledge Base Index

This directory is the **living memory** of the SRE team's operational experience.
Every entry was created from a real incident or troubleshooting session.

Unlike runbooks (which are prescriptive), patterns here describe what was *actually observed*
in this specific environment — shortcuts, dead ends, and failure signatures that only exist
because someone lived through them.

---

## How to Use

The agent searches this index when:
- An alert fires that matches a known pattern signature
- A user describes symptoms that match a known failure mode
- The `oncall-runbook` skill cannot find a matching runbook

## How Entries Are Created

Entries are created automatically by the `knowledge-capture` skill at the end of every
resolved incident. Do not edit patterns manually — run the skill instead, so the metadata
stays consistent.

---

## Pattern Index

| Service | Failure Mode | First Seen | Times Seen | Avg MTTR | File |
|---|---|---|---|---|---|
| payment-api | Connection pool exhaustion | 2024-09-14 | 3 | 31 min | [payment-api-connection-pool-exhaustion.md](patterns/payment-api-connection-pool-exhaustion.md) |
| auth-service | Redis session timeout | 2024-08-03 | 2 | 22 min | [auth-service-redis-timeout.md](patterns/auth-service-redis-timeout.md) |
| order-service | Memory leak after deploy | 2024-07-22 | 1 | 67 min | [order-service-memory-leak-after-deploy.md](patterns/order-service-memory-leak-after-deploy.md) |

---

## Statistics

- Total patterns: 3
- Most recurring failure mode: payment-api connection pool exhaustion (3x)
- Services with most incidents: payment-api
- MTTR improvement on known patterns: 31 min avg → 12 min best (payment-api)

*(Updated automatically by knowledge-capture skill after each incident)*

---

## Pattern Files

Pattern files live in `patterns/<service>-<failure-mode>.md`.

Each file contains:
- Observable signature (what metrics/logs show)
- Fastest diagnostic path
- What works, what does not work
- Times seen and dates (tracks recurrence)
