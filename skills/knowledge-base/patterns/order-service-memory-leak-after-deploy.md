---
service: order-service
failure-mode: memory-leak-after-deploy
first-seen: 2024-07-22
times-seen: 1
last-seen: 2024-07-22
avg-mttr-minutes: 67
best-mttr-minutes: 67
related-incidents: [inc-2024-07-22]
---

# Failure Pattern: order-service — Memory Leak After Deploy

## Symptom Signature

- **Primary signal:** OOMKilled pods appearing 30–90 min after a deploy (not immediately)
- **Metric:** `container_memory_working_set_bytes` climbing steadily at ~50MB/min per pod
- **Log pattern:** `signal: killed` in pod logs immediately before crash
- **Timeline shape:** Deploy succeeds → service appears healthy → memory climbs → pods OOMKill
  one by one → HPA cannot keep up → partial service degradation
- **Key characteristic:** The delay between deploy and failure (30–90 min) makes the
  deploy-failure connection non-obvious. On-call engineers often do not suspect the deploy.

## What Makes This Hard to Catch Early

- Memory growth is gradual — no sudden spike to trigger alerts
- Under low traffic (off-peak), memory grows slower → longer delay before crash
- The HPA adds more pods as existing ones OOMKill, masking the problem temporarily
- Existing memory alert was set at > 85% for 5 min — by the time it fired, pods were
  already crashing (alert was too slow)

## Trigger Conditions

**One trigger observed:**

Deploy introduces code that allocates memory inside a request handler but does not
release it when the request completes. Common causes:

- Global cache or registry that grows unboundedly (no TTL, no size limit)
- Event listener registered per-request but never removed
- Large object held in closure keeping reference alive after response sent
- Third-party library with a known leak (check library changelog)

**Fingerprint:** Memory growth is *linear* and *continuous* — not spiky. Graph looks
like a steady upward slope, not a sawtooth pattern.

## Fastest Diagnostic Path

Total time to confirm: **~6 minutes**

```bash
# Step 1: Confirm memory is climbing (not a one-time spike) (1 min)
kubectl top pods -n production -l app=order-service --sort-by=memory
# Run twice, 60 seconds apart. If memory is climbing on all pods: leak confirmed.
# If memory is stable: OOMKill may have been a one-time event — monitor and wait.

# Step 2: Check if a recent deploy correlates (1 min)
kubectl rollout history deployment/order-service -n production
# Note the last deploy time. Was it 30–90 min before the first OOMKill?
# Check: kubectl get events -n production | grep OOMKill | head -5

# Step 3: Check memory growth rate (2 min)
# In Datadog: order-service container_memory_working_set_bytes, 2h window
# If trend is linear and started at deploy time: memory leak from deploy confirmed

# Step 4: Profile to confirm (optional — only if rollback is not immediately safe)
# Port-forward to a pod and hit the /debug/pprof/heap endpoint (if Go)
# or /actuator/metrics (if Spring Boot)
kubectl port-forward -n production deployment/order-service 6060:6060
curl http://localhost:6060/debug/pprof/heap > heap.out
go tool pprof -top heap.out | head -20
```

## Resolution

**Step 1: Rollback immediately — do not wait for profiling if users are affected**

```bash
# Rollback to previous version (copy and run yourself)
kubectl rollout undo deployment/order-service -n production

# Monitor: memory on surviving pods should stabilize within 2 minutes
kubectl top pods -n production -l app=order-service --watch

# If all pods have OOMKilled and none are running:
kubectl scale deployment/order-service --replicas=0 -n production
kubectl rollout undo deployment/order-service -n production
kubectl scale deployment/order-service --replicas=<normal-count> -n production
```

**Step 2: Verify recovery**
```bash
# Memory should stabilize (not keep climbing) within 5 min of rollback
# Error rate should return to 0 within 2 min of pods becoming Ready
kubectl rollout status deployment/order-service -n production
```

**Step 3: Fix forward (after service is stable)**

The deploy that introduced the leak must be fixed before re-deploying. Do not
re-deploy the same version. Engage the order-service team to:
1. Run a heap profile in staging under sustained load (> 10 min)
2. Identify the allocation that is not being freed
3. Fix and verify in staging before production deploy

## Dead Ends

| What was tried | When | Result |
|---|---|---|
| Increasing memory limits | inc-2024-07-22 | Bought 20 extra minutes before same crash. Leak continued. |
| Restarting individual pods | inc-2024-07-22 | Restarted pods started leaking again immediately. |
| Waiting for HPA to scale out | inc-2024-07-22 | HPA added pods, but new pods also leaked. Made cost worse. |

**Lesson from inc-2024-07-22:** We spent 40 minutes on mitigation attempts before
rolling back. The correct answer was rollback within 5 minutes of confirming the
memory growth trend. Every minute of delay added more crashed pods and more user impact.

## Early Warning Signals (proposed after this incident)

```
Alert: order-service memory growth rate high
Metric: rate(container_memory_working_set_bytes[10m]) > 40MB/min per pod
Severity: P2 (Slack only — gives 15 min lead time before OOMKill)
Action: Check for recent deploy, begin diagnostic path

Alert: order-service pod OOMKilled
Metric: kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} > 0
Severity: P1 (page immediately)
Action: Skip straight to rollback decision
```

> **Status:** Both alerts configured after inc-2024-07-22. Memory growth rate alert
> fired once (2024-09-05) and enabled proactive rollback before users were affected.
> Memory growth rate alert has already paid for itself.

## Prevention

- [ ] Add memory growth rate alert — **DONE** (2024-07-29)
- [ ] Add heap profiling step to staging load test pipeline — In progress (order-service team)
- [ ] Add memory leak detection to CI: run service for 5 min under load, check growth rate
      Owner: platform-team | Status: Planned
- [ ] Add `--max-old-space-size` limit to Node.js services to force OOMKill faster
      (better to fail fast than to degrade slowly) — **DONE** (2024-08-12)

## Notes

- This incident had the longest MTTR (67 min) of any incident this year. The delay
  was almost entirely spent on mitigation attempts that did not work.
- The core learning: **when memory is climbing linearly post-deploy, rollback is
  always the right first action.** Profiling is for after the service is stable.
- order-service is written in Node.js. Memory leaks in Node.js are common when
  event listeners or closures hold references. The heap profiler at `/debug/pprof`
  requires the `clinic` package to be installed — confirm this is available before
  assuming profiling will work during an incident.
- The deploy that caused this was a dependency upgrade (lodash 4.17.20 → 4.17.21).
  The leak was in lodash's memoize function used in a hot path. Lesson: dependency
  upgrades in hot paths need load testing, not just unit tests.
