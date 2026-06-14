---
name: root-cause-analysis
description: >
  Systematically identify root causes of incidents, bugs, and reliability failures. Use
  after an incident, when debugging a persistent reliability problem, or when a postmortem
  needs structured analysis. Covers five-whys, fishbone diagrams, timeline correlation,
  and contributing factor categorization. Trigger keywords: root cause, RCA, why did this
  happen, five whys, contributing factors, investigation, debugging production, what caused,
  correlation, timeline analysis, why is this happening, keep happening, recurring incident,
  same problem again.
allowed-tools: Read Glob Grep Bash(git log:*)
---

# Root Cause Analysis Skill

## Setup Check

Before loading context files, check if `context/CONTEXT.md` exists in the current directory.

**If `context/CONTEXT.md` exists** — read it and proceed normally.

**If `context/CONTEXT.md` does not exist** — this skill was installed standalone (e.g. via `npx skills add`). Ask the user these questions before proceeding:

1. **Role** — `junior-sre` / `senior-sre` / `sre-manager`
   *(shapes output depth and tone)*
2. **Cloud provider** — `aws` / `gcp` / `azure` / `on-prem` / `hybrid`
3. **Observability stack** — e.g. Datadog, Prometheus+Grafana, New Relic
4. **Company name and primary services affected** *(if relevant to this task)*

Use the answers inline for this session. For persistent setup across all skills, suggest:
```
pipx install sre-agent
sre-agent init
```

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` for persona. Ask the user for:
- The observable symptom (what users or monitors saw)
- The timeline of events (when did it start, when was it detected, when resolved)
- What was changed recently (deploys, config, infra, data volume)

### Step 2: Build the Problem Statement
Write a precise problem statement:
```
On [date] at [time], [service] experienced [symptom], causing [user impact] for [duration].
The problem was first detected by [monitoring/user report] at [time] and resolved at [time].
```

Vague: "The service was slow."
Precise: "On 2024-01-15, the payment-api service experienced P99 latency of 8 seconds
(5x normal), causing checkout failures for ~15% of users for 47 minutes."

### Step 3: Five-Whys Analysis
Start from the customer-facing symptom. Ask "why" iteratively until you reach a systemic
or process-level cause (usually by Why 4 or 5).

Format each why as a question-answer pair:
```
Symptom: Users saw checkout failures (503 errors)

Why 1: Why did users see 503 errors?
  Answer: The payment-api pods were returning 503s.

Why 2: Why were the payment-api pods returning 503s?
  Answer: The database connection pool was exhausted.

Why 3: Why was the connection pool exhausted?
  Answer: A code change in v2.4.0 introduced N+1 queries in the checkout flow.

Why 4: Why did the N+1 query bug reach production?
  Answer: The code change was not reviewed for query patterns, and staging
          does not run load tests.

Why 5: Why does staging not run load tests?
  Answer: We have no automated load testing infrastructure or CI gate.

Root Cause: Absence of load testing in CI allowed a query performance regression
            to reach production undetected.
```

Acceptable root causes point to **systems or processes**, not people:
- Missing automated test
- Absent monitoring for a specific failure mode
- Lack of capacity limit or circuit breaker
- Process gap (no review step for X)
- Tooling limitation

Not acceptable root causes:
- "Human error" (always a symptom, never a root cause)
- "Someone made a mistake"
- "We were not careful enough"

### Step 4: Contributing Factor Analysis (Fishbone / Ishikawa)
Map contributing factors across four categories:

**Detection failures** — why was this hard to detect or took longer than expected?
- No metric for the failure mode?
- Alert threshold set too high?
- Runbook did not include this scenario?

**Response failures** — why did response take longer than it should?
- Unclear escalation path?
- Missing runbook?
- On-call engineer lacked context?
- Tooling made diagnosis slow?

**Process failures** — what process or procedure failed or was missing?
- No review step for this type of change?
- No load testing requirement?
- No canary / progressive rollout?

**Tooling failures** — what tooling limitation made this worse?
- No circuit breaker?
- No connection pool limit?
- No query timeout?
- Observability gap?

### Step 5: Timeline Correlation
Plot events on a timeline to identify the exact trigger:
```
T-24h: v2.4.0 deployed to staging — passed all tests
T-0:   v2.4.0 deployed to production (rolling update)
T+15m: DB connection count begins climbing (not alerted)
T+45m: Connection pool exhausted — 503s begin
T+47m: PagerDuty alert fires (latency P99 threshold)
T+1h2m: N+1 query identified in logs
T+1h15m: v2.3.9 rollback initiated
T+1h22m: Service restored
```

Identify: what was the trigger event? What was the delay between trigger and detection?

### Step 6: Distinguish Cause Types
| Type | Definition | Example |
|---|---|---|
| Proximate cause | The immediate technical cause | Connection pool exhausted |
| Root cause | The systemic reason it was possible | No load testing |
| Contributing factor | Made it worse or harder to detect | No connection pool alert |

### Step 7: Feed into Postmortem
Pass the structured output (problem statement, five-whys chain, contributing factors,
cause classification) to the `postmortem` skill for documentation.

---

## Guidelines

- Stop the five-whys when you reach a cause that is a system or process gap.
- If two different five-whys chains point to the same root cause, that is strong signal.
- Correlation is not causation — always verify that the change at T-0 actually caused the symptom.
- For recurring incidents: compare five-whys across all occurrences; the shared element is the root cause.
