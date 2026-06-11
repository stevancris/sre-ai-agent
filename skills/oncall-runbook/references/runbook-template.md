# Runbook: <Service Name> — <Alert Name>

**Service:** <service-name>
**Alert:** <alert-name>
**Severity:** P<N>
**Owner Team:** <team-name>
**Last Updated:** <YYYY-MM-DD>
**Maintained By:** <role or team>

---

## Alert Trigger Condition

Describe exactly when this alert fires:
```
metric: <metric name>
threshold: <value and comparison operator>
window: <evaluation window>
example: error_rate > 5% over 5 minutes
```

## What This Means

Plain-language explanation of what is happening when this alert fires. Include:
- What the service does
- Why this alert matters (user impact)
- What usually causes it

## Blast Radius

- **User impact:** <who is affected>
- **Dependent services:** <list services that depend on this one>
- **Data integrity risk:** <yes/no and why>

---

## Triage Steps

### 1. Confirm the alert is real (not a fluke)
```bash
# Check current metric value
<command to check metric>
# Expected: value above threshold
# If value is normal: alert may be stale — check alert evaluation window
```

### 2. Check service health
```bash
kubectl get pods -l app=<service-name> -n <namespace>
# Expected: all pods Running, restarts < 3
# If pods are CrashLoopBackOff: go to step 4
```

### 3. Check recent logs
```bash
kubectl logs -l app=<service-name> -n <namespace> --since=15m | tail -100
# Look for: <error signatures>
```

### 4. Check upstream dependencies
```bash
# Check dependency health:
<command to check each dependency>
# If a dependency is down: escalate to that service's on-call
```

---

## Remediation Steps

### Option A: <most common cause>
**When to use:** <describe the condition>

```bash
# Step 1:
<command>
# Expected output: <what success looks like>
# If this fails: <what to do>

# Step 2:
<command>
```

### Option B: <second common cause>
**When to use:** <describe the condition>

```bash
<command>
```

---

## Rollback Procedure

If remediation makes things worse, roll back:

```bash
# Identify the previous good deployment
kubectl rollout history deployment/<service-name> -n <namespace>

# Roll back to the previous version
# (Run this manually — copy and execute)
kubectl rollout undo deployment/<service-name> -n <namespace>

# Verify rollback
kubectl rollout status deployment/<service-name> -n <namespace>
```

---

## Escalation Path

| Time without resolution | Action |
|---|---|
| 0–15 min | Primary on-call investigates |
| 15–30 min | Page secondary on-call |
| 30 min | Page engineering manager |
| 45 min (if P0) | Page VP Engineering |

**Secondary on-call:** See `context/company/oncall-schedule.md`
**Slack channel:** See `context/company/oncall-schedule.md`

---

## Known Issues and False Positives

- **Known issue 1:** <description and how to distinguish from real incident>
- **False positive scenario:** <when this alert fires but is not actionable>

---

## Post-Incident Checklist

- [ ] Alert resolved in PagerDuty / OpsGenie
- [ ] Incident channel closed
- [ ] Timeline documented
- [ ] Runbook updated with any new findings
- [ ] Postmortem initiated (if P0 or P1)
