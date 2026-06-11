---
service: auth-service
failure-mode: redis-session-timeout
first-seen: 2024-08-03
times-seen: 2
last-seen: 2024-10-17
avg-mttr-minutes: 22
best-mttr-minutes: 9
related-incidents: [inc-2024-08-03, inc-2024-10-17]
---

# Failure Pattern: auth-service — Redis Session Timeout

## Symptom Signature

- **Primary signal:** Login failures across all clients — `401 Unauthorized` on `/api/v1/auth/login`
- **Metric:** `auth_service.session.create.error_rate` > 10%
- **User report pattern:** "I can't log in" — affects 100% of new login attempts, existing sessions unaffected
- **Key distinction:** Users who are *already* logged in (valid session in Redis) are unaffected.
  Only *new* login attempts fail. This is the fastest way to distinguish Redis from a full auth outage.
- **Log pattern:** `RedisTimeoutError: Command timed out after 500ms` or `ECONNREFUSED 6379`

## What Is NOT This Pattern

If *existing* sessions are also failing (users get logged out): this is not a Redis timeout.
Check ElastiCache cluster health and failover status instead.

## Trigger Conditions

Two triggers observed:

1. **ElastiCache primary node failover** (root cause of inc-2024-08-03)
   - AWS triggers automatic failover to replica
   - During failover: 60–90 second window where Redis is unreachable
   - auth-service has no circuit breaker on Redis → all login requests fail immediately
   - Fingerprint: sudden spike at exact minute, AWS RDS/ElastiCache health event in console

2. **Memory pressure causing Redis to evict sessions and reject writes** (root cause of inc-2024-10-17)
   - ElastiCache memory > 95% → `maxmemory-policy allkeys-lru` starts evicting
   - New session writes fail with `OOM command not allowed when used memory > maxmemory`
   - Fingerprint: gradual degradation over 15–30 min, memory metric climbing before incident

## Fastest Diagnostic Path

Total time to confirm: **~3 minutes**

```bash
# Step 1: Confirm Redis is the issue, not auth-service itself (1 min)
kubectl exec -n production deployment/auth-service -- \
  redis-cli -h $REDIS_HOST ping
# Expected if healthy: PONG
# If timeout or ECONNREFUSED: Redis is unreachable → check ElastiCache console

# Step 2: Check ElastiCache memory (1 min)
# In AWS Console: ElastiCache → auth-redis-prod → Metrics → DatabaseMemoryUsagePercentage
# OR via CloudWatch CLI:
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name DatabaseMemoryUsagePercentage \
  --dimensions Name=CacheClusterId,Value=auth-redis-prod \
  --start-time $(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 --statistics Average
# If memory > 90%: trigger is memory pressure → Option B
# If memory normal: trigger is failover or network → Option A

# Step 3: Check AWS health events (1 min)
# AWS Console → ElastiCache → Events
# Look for: "Failover complete", "Replication group modified"
```

## Resolution by Trigger

### Option A: ElastiCache failover in progress
**Estimated resolution: 3–5 min (wait for AWS) + 2 min verification**

```bash
# Nothing to fix — AWS is handling the failover automatically
# Monitor ElastiCache events until "Failover complete" appears
# Once complete, new logins will succeed immediately (connection re-established)

# If failover taking > 5 min: escalate to AWS Support (Business tier)
# Case type: ElastiCache, severity: Production system down

# Mitigation while waiting:
# Enable "degraded mode" via LaunchDarkly flag if available:
# Flag: auth-service.redis-fallback → set to true
# This allows login with DB-only session validation (slower but functional)
```

### Option B: Memory pressure / OOM
**Estimated resolution: 8–10 min**

```bash
# 1. Immediate: flush expired sessions to free memory
kubectl exec -n production deployment/auth-service -- \
  redis-cli -h $REDIS_HOST --scan --pattern "session:*" | \
  xargs redis-cli -h $REDIS_HOST TTL | grep -c "^-2"
# This shows count of already-expired keys still consuming memory

# 2. If > 10,000 expired keys: run cleanup
#    (copy and run yourself — this deletes data)
redis-cli -h $REDIS_HOST --scan --pattern "session:*" | \
  while read key; do
    ttl=$(redis-cli -h $REDIS_HOST TTL "$key")
    [ "$ttl" -eq -2 ] && redis-cli -h $REDIS_HOST DEL "$key"
  done

# 3. Reduce session TTL temporarily to prevent recurrence
# Default: 7 days. Reduce to 24h via env var SESSION_TTL_SECONDS=86400
# (requires rolling restart of auth-service)

# 4. Resize ElastiCache node — this is the permanent fix
# Current: cache.r6g.large (6.38 GB)
# Recommended: cache.r6g.xlarge (12.93 GB)
# Create RFC or ticket for permanent resize
```

## Dead Ends

| What was tried | When | Result |
|---|---|---|
| Restarting auth-service pods | inc-2024-08-03 | No effect — issue is at Redis level |
| Scaling auth-service replicas | inc-2024-08-03 | Made alert storm worse (more connections to broken Redis) |
| Flushing ALL Redis data (`FLUSHALL`) | Never (proposed) | DO NOT — this logs out every active user. Nuclear option. |

## False Positive Pattern

**Alert fires but Redis is healthy:** can happen when auth-service itself restarts and
briefly loses its connection pool. Resolves within 60 seconds without intervention.

Fingerprint: error spike lasts < 90 seconds and returns to 0 on its own.
Check: `kubectl rollout status deployment/auth-service` — if pods restarting, wait.

## Early Warning Signals

```
Alert: ElastiCache memory high
Metric: DatabaseMemoryUsagePercentage > 80% for 10 minutes
Severity: P2 (Slack only)
Action: Schedule node resize before hitting 95%

Alert: Redis connection errors
Metric: auth_service.redis.error_rate > 1% for 2 minutes
Severity: P1 (page)
Action: Run diagnostic path above
```

## Notes

- inc-2024-10-17 was caught by the on-call engineer noticing memory trending up
  in the morning standup. It did not escalate to a user-facing incident because
  the cleanup was run proactively. This is the value of the P2 early warning.
- Session TTL of 7 days is generous — most products use 24h. Worth reviewing
  with product team whether 7 days is actually needed.
- There is no circuit breaker on auth-service → Redis connection. If Redis is
  slow, all login requests pile up and wait. RFC-0038 proposes adding a circuit
  breaker with a DB fallback. Priority: high.
