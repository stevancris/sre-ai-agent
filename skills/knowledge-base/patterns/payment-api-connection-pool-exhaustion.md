---
service: payment-api
failure-mode: connection-pool-exhaustion
first-seen: 2024-09-14
times-seen: 3
last-seen: 2024-11-02
avg-mttr-minutes: 31
best-mttr-minutes: 12
related-incidents: [inc-2024-09-14, inc-2024-10-21, inc-2024-11-02]
---

# Failure Pattern: payment-api — Connection Pool Exhaustion

## Symptom Signature

How to recognize this pattern within the first 2 minutes:

- **Primary signal:** HTTP 503 errors on `/api/v1/checkout` and `/api/v1/orders`
- **Metric:** `db_connection_pool_utilization` > 95% on `payment-api` pool
- **Log pattern:** `FATAL: remaining connection slots are reserved for non-replication superuser connections`
- **Secondary signal:** P99 latency spike to > 3s before 503s appear (leading indicator — ~8 min before 503s)
- **What is NOT affected:** Auth endpoints (`/api/v1/auth`) still respond normally — this rules out a full service outage

## Trigger Conditions

Three distinct triggers have been observed:

1. **N+1 query regression in a deploy** (root cause of inc-2024-09-14 and inc-2024-11-02)
   - New code introduces a query-per-item loop instead of a bulk query
   - Connection hold time increases → pool exhausts under normal traffic
   - Fingerprint: connection count rises *immediately after a deploy*, not gradually

2. **Traffic spike beyond baseline** (root cause of inc-2024-10-21)
   - Flash sale or campaign drives 3x+ normal traffic
   - Connection pool sized for baseline, not peak
   - Fingerprint: connection count rises proportionally to traffic, no recent deploy

3. **Slow query caused by missing index** (not yet seen, but identified as risk)
   - Long-running queries hold connections
   - Fingerprint: connection count high + `pg_stat_activity` shows many long-running queries

## Fastest Diagnostic Path

Total time to confirm and identify trigger: **~4 minutes**

```bash
# Step 1: Confirm this is connection exhaustion, not something else (30s)
kubectl exec -n production deployment/payment-api -- \
  psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
# Expected if this pattern: count > 95 (pool max is 100)
# If count < 80: this is NOT connection exhaustion → investigate elsewhere

# Step 2: Identify the trigger — was there a recent deploy? (30s)
kubectl rollout history deployment/payment-api -n production | head -5
# If deploy < 30 min ago: trigger is likely code regression → go to Option A
# If no recent deploy: trigger is likely traffic spike → go to Option B

# Step 3: Check which queries are holding connections (2 min)
kubectl exec -n production deployment/payment-api -- \
  psql $DATABASE_URL -c "
    SELECT pid, now() - query_start AS duration, state, left(query, 80) AS query
    FROM pg_stat_activity
    WHERE state != 'idle'
    ORDER BY duration DESC
    LIMIT 20;"
# If many queries > 5s duration from same query pattern: N+1 regression confirmed
# If queries are fast but many: traffic spike confirmed
```

## Resolution by Trigger

### Option A: Code regression (N+1 query)
**Estimated resolution: 12–15 min**

```bash
# 1. Rollback to previous version immediately — do not wait for diagnosis
#    (copy and run this yourself)
kubectl rollout undo deployment/payment-api -n production

# 2. Monitor: connection count should drop within 2 minutes of rollback
kubectl exec -n production deployment/payment-api -- \
  psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Verify 503s stop
# Watch error rate in Datadog: payment-api.http.5xx — should drop to 0 within 3 min
```

### Option B: Traffic spike
**Estimated resolution: 8–10 min**

```bash
# 1. Increase connection pool size temporarily (buys time)
# Edit the PAYMENT_API_DB_POOL_SIZE env var and trigger rolling restart
# (coordinate with platform team — this is a config change)

# 2. Enable rate limiting on checkout endpoint via LaunchDarkly flag
# Flag: payment-api.checkout.rate-limit → set to 500 req/min

# 3. Scale payment-api replicas up — BUT increase pool size FIRST
#    (more replicas without pool size increase = faster exhaustion)
kubectl scale deployment/payment-api --replicas=<current+3> -n production
```

## Dead Ends — Do Not Try These

These were attempted in previous incidents and wasted time:

| What was tried | When | Result | Why it failed |
|---|---|---|---|
| Restarting pods | inc-2024-09-14 | No improvement | Pool exhaustion is at DB level, not pod level. Restart just reconnects. |
| Scaling up replicas FIRST | inc-2024-10-21 | Made it worse | More pods = more connections = faster exhaustion. Scale pool FIRST. |
| Killing idle connections manually | inc-2024-09-14 | Temporary relief only | New requests immediately took the freed slots. Not sustainable. |
| Restarting the RDS instance | inc-2024-09-14 | Caused 3 min additional outage | Nuclear option. Do not use unless data corruption suspected. |

## Early Warning Signals

We can catch this **before it pages** with these leading indicators:

```
Alert: payment-api connection pool warning
Metric: db_connection_pool_utilization > 70% for 5 minutes
Severity: P2 (Slack only, no page)
Action: Investigate proactively — page incoming within ~15 min at current rate

Alert: payment-api connection pool critical
Metric: db_connection_pool_utilization > 85% for 2 minutes
Severity: P1 (page primary on-call)
```

> **TODO:** These alerts were proposed after inc-2024-11-02 but not yet configured.
> Owner: SRE team | Due: 2024-11-15

## Prevention (from RCA action items)

- [ ] Add load testing to CI pipeline — catches N+1 regressions before deploy
      Owner: backend-team | Status: In progress
- [ ] Implement PgBouncer as connection pooler — permanent solution to pool exhaustion
      Owner: platform-team | RFC: RFC-0042 | Status: Planned Q1 2025
- [ ] Add connection pool warning alert at 70% — buys 15 min of lead time
      Owner: SRE team | Status: TODO (see above)

## Notes

- inc-2024-11-02 was resolved in 12 min because we had learned from inc-2024-09-14.
  Primary improvement: we went straight to rollback instead of debugging first.
- The 2am timing of inc-2024-10-21 (traffic spike) was a surprise — turns out a
  scheduled batch job in EU region was driving unexpected checkout activity.
  Added to known batch job windows: 01:30–03:00 UTC.
- RDS connection limit is 100 (db.r6g.large). At 80+ connections, response times
  visibly degrade even before 503s appear.
