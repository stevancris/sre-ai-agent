---
name: production-readiness-review
description: >
  Review a service or feature for production readiness before launch. Use when a new
  service is about to go live, when an existing service is adding a major new capability,
  or when onboarding a service to SRE ownership. This is the primary shift-left skill —
  catching reliability, observability, and operational gaps before they become incidents.
  Trigger keywords: production readiness, PRR, launch readiness, ready to launch, ready
  for production, going to prod, new service, onboard service, pre-launch, launch review,
  is this ready, can we ship, pre-production checklist, launch checklist, go live checklist,
  service handover, SRE handoff.
allowed-tools: Read Glob Grep Bash(git log:*)
---

# Production Readiness Review (PRR) Skill

## Purpose

The PRR is the SRE's primary tool for **preventing incidents before they happen**.
It is a structured review that a service must pass before SRE accepts on-call ownership.
A service that fails a PRR does not go to production — it goes back to the team with a
remediation list.

This skill operationalizes the principle: *reliability is designed in, not bolted on.*

---

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md`, `context/company/tech-stack.md`, and
`context/company/incident-severity.md`.

Identify:
- Service name and owner team
- Expected traffic at launch (RPS, DAU, data volume)
- Launch date / deadline
- Risk tier (see Step 2)

### Step 2: Classify the Service Risk Tier

| Tier | Criteria | PRR depth |
|---|---|---|
| **Critical** | Revenue path, auth, data storage, >50% of users | Full PRR — all sections mandatory |
| **Standard** | User-facing feature, significant traffic | Full PRR — minor items can be deferred with plan |
| **Internal** | Internal tooling, low traffic, no revenue path | Lightweight PRR — abbreviated checklist |

Ask: "Is this service on the critical path for revenue or user authentication?" — if yes,
default to Critical tier.

### Step 3: Run the PRR Checklist

Work through each section. For each item: ✅ Pass / ⚠️ Defer with plan / ❌ Blocker.

**Blockers must be resolved before launch. Deferred items need an explicit owner and date.**

---

#### Section 1: Observability

| # | Requirement | Status |
|---|---|---|
| 1.1 | Four golden signals instrumented: latency, traffic, errors, saturation | |
| 1.2 | Structured logs with trace_id, service, level, request_id | |
| 1.3 | Distributed tracing spans at all service boundaries | |
| 1.4 | Dashboard exists showing golden signals at a glance | |
| 1.5 | Logs are queryable and retained per policy | |
| 1.6 | No sensitive data (PII, tokens, secrets) in logs | |

**Blocker threshold:** 1.1 and 1.2 must pass. Others are ⚠️ deferrable with 2-week plan.

---

#### Section 2: Alerting

| # | Requirement | Status |
|---|---|---|
| 2.1 | SLI defined (what to measure) | |
| 2.2 | SLO defined (target value and window) | |
| 2.3 | Error budget policy defined | |
| 2.4 | Multi-window burn rate alerts configured (P1 and P2 thresholds) | |
| 2.5 | Every alert has a runbook link | |
| 2.6 | Alerts route to the correct on-call rotation | |
| 2.7 | Alert volume is reasonable (no alert storm expected at launch) | |

**Blocker threshold:** 2.1, 2.2, 2.4, 2.5 must pass. Service without SLO cannot be owned by SRE.

---

#### Section 3: Runbooks and Documentation

| # | Requirement | Status |
|---|---|---|
| 3.1 | Runbook exists for each configured alert | |
| 3.2 | Runbooks include: triage steps, remediation, rollback, escalation path | |
| 3.3 | Service architecture diagram is current and accessible | |
| 3.4 | Dependency map documented (what this service calls, what calls this service) | |
| 3.5 | Data flow documented (what data enters and exits, where it is stored) | |
| 3.6 | Known failure modes documented with blast radius | |

**Blocker threshold:** 3.1 and 3.2 must pass. Invoke `runbook-generator` for any missing runbooks.

---

#### Section 4: Deployment and Rollback

| # | Requirement | Status |
|---|---|---|
| 4.1 | Deployment is automated (no manual steps in the critical path) | |
| 4.2 | Canary or progressive rollout configured | |
| 4.3 | Rollback procedure is documented and tested | |
| 4.4 | Rollback takes < 10 minutes | |
| 4.5 | Feature flags available for high-risk functionality | |
| 4.6 | Database migrations are backwards-compatible | |
| 4.7 | Deployment does not require downtime (zero-downtime deploy) | |

**Blocker threshold:** 4.1, 4.3, 4.4 must pass. 4.7 required for Critical tier.

---

#### Section 5: Capacity and Scaling

| # | Requirement | Status |
|---|---|---|
| 5.1 | Expected peak traffic estimated and documented | |
| 5.2 | Service load tested at 2x expected peak | |
| 5.3 | Autoscaling configured with appropriate min/max | |
| 5.4 | Resource requests and limits set on all pods | |
| 5.5 | Dependency capacity verified (DB, cache, downstream APIs can handle load) | |
| 5.6 | Rate limiting configured on public endpoints | |
| 5.7 | Circuit breakers configured for all downstream dependencies | |

**Blocker threshold:** 5.1, 5.3, 5.5 must pass. 5.2 required for Critical tier.

---

#### Section 6: Reliability Design

| # | Requirement | Status |
|---|---|---|
| 6.1 | Service degrades gracefully when dependencies are unavailable | |
| 6.2 | Timeouts configured on all outbound calls | |
| 6.3 | Retry logic uses exponential backoff with jitter | |
| 6.4 | No single point of failure for Critical tier services | |
| 6.5 | Data loss scenarios identified and mitigated | |
| 6.6 | Service handles restart correctly (no state loss on crash) | |
| 6.7 | Health check endpoint returns correct status (not just 200 always) | |

**Blocker threshold:** 6.1, 6.2, 6.7 must pass.

---

#### Section 7: Security

| # | Requirement | Status |
|---|---|---|
| 7.1 | Service account uses least-privilege IAM role | |
| 7.2 | No hardcoded secrets in code or IaC | |
| 7.3 | All secrets loaded from secrets manager at runtime | |
| 7.4 | Network exposure is minimal (not publicly accessible unless required) | |
| 7.5 | Input validation on all public endpoints | |
| 7.6 | Authentication and authorization implemented on all endpoints | |

**Blocker threshold:** 7.1, 7.2, 7.3, 7.6 must pass.

---

#### Section 8: On-Call Readiness

| # | Requirement | Status |
|---|---|---|
| 8.1 | On-call rotation defined and engineers are trained on this service | |
| 8.2 | Engineers have been walked through runbooks in a dry run | |
| 8.3 | Escalation path defined (primary → secondary → manager) | |
| 8.4 | Service added to alert catalog | |
| 8.5 | Post-launch monitoring plan defined (who watches what, for how long) | |
| 8.6 | Launch communication sent to SRE team and stakeholders | |

**Blocker threshold:** 8.1, 8.3 must pass.

---

### Step 4: Generate the PRR Report

```
Production Readiness Review: <Service Name>
Reviewed: YYYY-MM-DD | Tier: Critical / Standard / Internal
Reviewer: SRE Team

VERDICT: ✅ APPROVED / ⚠️ CONDITIONAL / ❌ NOT READY

Summary:
  Pass:     N items
  Deferred: N items (with plans)
  Blockers: N items

━━━ BLOCKERS (must fix before launch) ━━━
❌ 2.2 — No SLO defined. Without an SLO, there is no way to determine when this
         service is degraded or measure reliability over time.
         Owner: <team> | Fix: Define SLI + SLO using slo-monitoring skill | Due: YYYY-MM-DD

❌ 3.1 — No runbook for "HighErrorRate" alert.
         Owner: <team> | Fix: Run runbook-generator skill | Due: YYYY-MM-DD

━━━ DEFERRED ITEMS (launch with plan) ━━━
⚠️ 5.2 — Load test at 2x peak not completed.
         Owner: <team> | Plan: Run load test in staging within 1 week of launch | Due: YYYY-MM-DD

⚠️ 4.5 — Feature flags not implemented for new checkout flow.
         Owner: <team> | Plan: Wrap in LaunchDarkly flag before next major release | Due: YYYY-MM-DD

━━━ PASSED ━━━
✅ 1.1 Four golden signals instrumented
✅ 1.2 Structured logging with trace_id
✅ 2.4 Multi-window burn rate alerts configured
[... etc]

Next steps:
  1. Fix all blockers
  2. Re-review blocked sections
  3. Sign off and add service to SRE on-call rotation
```

### Step 5: Conditional Approval

For **CONDITIONAL** verdict (deferred items only, no blockers):
- Document all deferred items with owners and dates
- Set a 30-day post-launch review checkpoint
- Add deferred items to team backlog

For **NOT READY** verdict:
- Share PRR report with service team and engineering manager
- Schedule a remediation check-in (recommend 1 week)
- Do not add to on-call rotation until blockers are resolved

### Step 6: Post-Launch Monitoring Plan

For approved services, generate a launch monitoring plan:

```
Launch Monitoring Plan: <Service Name>

Launch date: YYYY-MM-DD HH:MM UTC
IC (on-call): <primary oncall>

Hour 0–1 (critical window):
  - Watch error rate (alert threshold: >1% for 2 min)
  - Watch P99 latency (alert threshold: >500ms for 2 min)
  - Watch saturation: CPU and memory on all pods
  - Check downstream dependencies: DB connection count, cache hit rate
  - Be ready to rollback: command pre-staged and tested

Hour 1–24:
  - Monitor error budget burn rate
  - Check for any new alert types firing
  - Review logs for unexpected patterns

Day 2–7:
  - Daily error budget review
  - Confirm deferred PRR items are on track
  - 1-week post-launch retrospective

Rollback trigger:
  - Error rate > 2% sustained for > 3 minutes → rollback immediately
  - Any data integrity concern → rollback immediately
```

---

## Guidelines

- A PRR is a review, not a rubber stamp. If something is wrong, say so clearly.
- The owner of a blocker is always the **service team**, not SRE. SRE identifies; team fixes.
- Deferred items are acceptable — but every deferral needs an owner and a date.
  Undated deferrals become permanent deferrals.
- For Critical tier: involve the engineering manager in the PRR sign-off.
- Persona (junior-sre): always ask a senior SRE or manager to co-sign a Critical tier PRR.
- Persona (sre-manager): add a risk statement to the PRR report summarizing total risk
  exposure if the service launches with current gaps.
- A PRR failure is not a blame event — it is the system working correctly.
