---
name: incident-response
description: >
  Manage active production incidents end-to-end. Use when an alert fires, a service is
  degraded or down, error rates spike, latency increases, or a customer reports an outage.
  Covers detection, severity classification, response coordination, communication drafting,
  and incident timeline tracking. Trigger keywords: incident, outage, down, degraded,
  alert, pager, on-call, oncall, P0, P1, P2, SEV1, SEV2, firing, pagerduty, opsgenie,
  service unavailable, 5xx spike, error rate high, latency spike, customers affected.
allowed-tools: Read Glob Grep Bash(kubectl get:*) Bash(kubectl describe:*) Bash(kubectl logs:*)
---

# Incident Response Skill

## Instructions

### Step 0: Search Knowledge Base First (MANDATORY — before anything else)
Before classifying severity or opening a channel, search `skills/knowledge-base/patterns/`
using Glob (`skills/knowledge-base/patterns/*.md`) and Grep for the service name or
symptom keywords from the user's message.

If a matching pattern file is found:
```
⚡ Known pattern detected: <pattern name>
Last seen: <date> | Times seen: <N>

Fastest diagnostic path:
  1. <step from pattern file>
  2. <step from pattern file>

What NOT to try (dead ends):
  - <dead end from pattern file>

Estimated resolution time based on history: ~X minutes
```

Surface this immediately — before opening the incident channel or doing anything else.
If no pattern matches, continue to Step 1 and note: "No prior pattern found — starting fresh."

### Step 1: Load Context
Read `context/CONTEXT.md`, `context/company/incident-severity.md`, and
`context/company/oncall-schedule.md` before taking any other action.

### Step 2: Classify Severity
Using the severity definitions from `context/company/incident-severity.md`, ask the user:
- Is this user-facing?
- What percentage of users are affected?
- Which services or features are impacted?

Classify the incident as P0 / P1 / P2 / P3 based on the decision tree in the severity file.

### Step 3: Open the Incident
Generate the following immediately:

**Incident channel name:**
```
inc-YYYY-MM-DD-<short-description>
```

**Opening Slack message template:**
```
🚨 INCIDENT [P<N>] — <short description>

Status: INVESTIGATING
Impact: <what users/services are affected>
Started: <approximate start time>
IC (Incident Commander): <primary oncall name>

Bridge: <link>
Runbook: <link if known>
Updates every 15 min or on status change.
```

### Step 4: Immediate Actions Checklist
Output a checklist tailored to severity:

**P0 checklist:**
- [ ] Notify primary on-call (if not already paged)
- [ ] Notify secondary on-call
- [ ] Notify engineering manager
- [ ] Open incident bridge
- [ ] Post status page update (draft below)
- [ ] Identify blast radius: which services / regions / customers
- [ ] Pull relevant runbook
- [ ] Assign roles: IC (Incident Commander), Comms Lead, Tech Lead

**P1 checklist:**
- [ ] Notify primary on-call (if not already paged)
- [ ] Open incident Slack channel
- [ ] Identify blast radius
- [ ] Pull relevant runbook
- [ ] Notify engineering manager

**P2/P3 checklist:**
- [ ] Create incident ticket
- [ ] Notify on-call team via Slack (no bridge needed)
- [ ] Begin investigation

### Step 5: Blast Radius Assessment
Determine and document:
- Which services are affected (primary + downstream dependencies)?
- Which regions are affected?
- What percentage of users or requests are impacted?
- Is there any data loss or data integrity risk?
- Are any SLOs currently breaching?

### Step 6: Pull the Runbook
Search `skills/oncall-runbook/references/` for a runbook matching the affected service
and alert name. If none exists, invoke the `runbook-generator` skill in parallel.

### Step 7: Timeline Tracking
Maintain a running timeline as the user provides updates. Format:
```
HH:MM UTC — <event description>
```

Prompt the user for updates at natural pause points (after each diagnostic step).

### Step 8: Status Updates
Generate stakeholder status updates every 15 minutes during P0/P1:
```
Update [N] — HH:MM UTC
Status: INVESTIGATING / IDENTIFIED / MITIGATING / RESOLVED
Impact: <current scope>
What we know: <current understanding>
Next update: HH:MM UTC
```

### Step 9: Resolution
When the user signals the incident is resolved:
1. Generate a final resolution message.
2. Calculate MTTR (Mean Time To Resolve) from timeline.
3. Prompt to transition to the `postmortem` skill.
4. Remind to close the status page incident.

---

## Examples

### Example: Database connection pool exhausted

User: "Alert just fired — our API is returning 503s. Looks like DB connections exhausted."

Response (senior-sre persona):
```
Severity: P1 (API degraded, partial user impact)

Immediate actions:
- [ ] Open #inc-2024-01-15-db-conn-exhausted
- [ ] Check current connection count: kubectl exec <db-pod> -- psql -c "SELECT count(*) FROM pg_stat_activity;"
- [ ] Check which services are holding connections: kubectl logs -l app=api --since=5m | grep "connection"
- [ ] Scale API replicas down by 20% to shed load while diagnosing
- [ ] Check for connection leak in recent deploys: git log --oneline -10

Runbook: See skills/oncall-runbook/references/postgresql-connection-exhaustion.md
```

---

## Guidelines

- Never skip severity classification even if the user says "it's just a P2."
- During a P0, produce the Slack message template before doing any technical diagnosis.
- If the user does not know the blast radius, provide kubectl/query commands to find it.
- Keep timeline entries timestamped to the minute; they become the postmortem foundation.
- Persona: junior-sre version always ends each step with an escalation reminder.
