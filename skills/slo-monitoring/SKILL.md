---
name: slo-monitoring
description: >
  Define, review, and alert on Service Level Objectives and error budgets. Use when
  setting up SLOs, reviewing SLA compliance, calculating error budget burn rate, debugging
  why an error budget is depleted, or planning reliability investments. Trigger keywords:
  SLO, SLA, error budget, burn rate, reliability target, availability, latency percentile,
  p99, p95, p50, uptime, four nines, five nines, nine nines, service level objective,
  service level agreement, error budget exhausted, reliability investment.
allowed-tools: Read Glob Grep
---

# SLO Monitoring Skill

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and the company's SLO configuration from `context/CONTEXT.md`
(`primary_slo_target` and `error_budget_policy` fields).

### Step 2: Determine the Task
Classify the user's request into one of these modes:
- **Define SLO** — no SLO exists yet for a service
- **Review SLO** — existing SLO, check current status
- **Diagnose burn** — error budget is depleting faster than expected
- **Policy review** — is the error budget policy appropriate?

---

### Mode: Define SLO

#### 2a. Choose the SLI (Service Level Indicator)
For each service, identify the right SLI type:

| Service type | Recommended SLI |
|---|---|
| Request-serving (API, web) | Availability (successful requests / total requests) |
| Request-serving (latency-sensitive) | Latency (% of requests under threshold) |
| Data pipeline | Freshness (age of latest processed record) |
| Storage | Durability (% of writes successfully persisted) |
| Batch job | Completion rate (successful runs / total runs) |

#### 2b. Set the SLO Target
Use this framework:
- Look at historical performance over the last 90 days.
- Set the target slightly below historical performance (leave room for improvement).
- Align with customer expectations (explicit SLA or implicit from product tier).

Common starting points:
- Consumer-facing API: 99.9% (43.8 min/month downtime allowance)
- Internal API: 99.5% (3.65 hours/month)
- Batch pipeline: 99.0% (7.3 hours/month)

#### 2c. Define Burn Rate Alerts
Set multi-window, multi-burn-rate alerts using these thresholds:

| Alert | Burn rate | Short window | Long window | Error budget consumed |
|---|---|---|---|---|
| P1 (page) | 14.4x | 1 hour | 5 minutes | 2% in 1 hour |
| P2 (page) | 6x | 6 hours | 30 minutes | 5% in 6 hours |
| P3 (ticket) | 3x | 3 days | 6 hours | 10% in 3 days |
| P4 (notify) | 1x | 30 days | — | budget on track to exhaust |

#### 2d. Define Error Budget Policy
```
- If error budget remaining > 50%: feature work proceeds normally
- If error budget remaining 10–50%: add reliability work to sprint
- If error budget remaining < 10%: freeze non-critical feature work
- If error budget exhausted: full reliability mode until budget replenishes
```

---

### Mode: Review SLO

Ask the user for (or calculate from context):
- Current SLO target (%)
- Measurement window (rolling 30-day is standard)
- Number of bad minutes or bad requests in the window

Calculate:
```
Error Budget = (1 - SLO_target) × window_duration
Error Budget Consumed = (1 - current_availability) × window_duration
Error Budget Remaining = Error Budget − Error Budget Consumed
Error Budget Remaining % = (Error Budget Remaining / Error Budget) × 100
Days Until Exhaustion = (Error Budget Remaining / current_burn_rate)
```

Output a status card:
```
SLO Status: <SERVICE NAME>
Target:     99.9%    (43.8 min/month error budget)
Current:    99.85%   (65.7 min consumed)
Remaining:  0% — BUDGET EXHAUSTED
Burn rate:  1.5x normal
Action:     Error budget policy: reliability mode
```

---

### Mode: Diagnose Burn

When error budget is burning faster than expected:

1. Identify the time range when burn accelerated.
2. Ask: what changed around that time? (deploys, config changes, traffic spikes)
3. Identify the specific failure mode: high error rate, high latency, or both?
4. Calculate which service or endpoint is contributing most to the burn.
5. Recommend: fix, freeze, or adjust target?

---

## Guidelines

- Tight SLOs (99.99%+) require significant engineering investment. Question whether the
  business actually needs that level and what the cost is.
- Never set an SLO tighter than what you can currently measure accurately.
- Error budgets are not punishments; they are a shared language for trading features vs. reliability.
- Persona (sre-manager): always include a "business impact" section — what does this SLO mean
  for customer retention, SLA penalties, or brand risk?
