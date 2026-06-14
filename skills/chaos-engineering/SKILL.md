---
name: chaos-engineering
description: >
  Design and run controlled chaos experiments to validate system resilience. Use when
  validating failure modes, running gameday exercises, testing recovery procedures, or
  building a chaos testing program. Must NOT be invoked during active production incidents.
  Trigger keywords: chaos engineering, chaos experiment, gameday, game day, fault injection,
  resilience testing, failure mode, what happens if, kill pod, simulate failure, disaster
  recovery test, DR test, resilience validation, failure scenario, blast radius test,
  dependency failure, region failure.
compatibility: Must not be invoked during an active production incident. Requires explicit
  confirmation that no active P0 or P1 incidents are occurring.
allowed-tools: Read Glob Grep
---

# Chaos Engineering Skill

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

### Step 0: Safety Gate (MANDATORY)
Before any other step, verify:
1. Ask: "Is there currently an active P0 or P1 incident?" If yes: stop immediately.
   "Chaos experiments must not run during active incidents. Resolve the incident first."
2. Ask: "Has this experiment been approved by the on-call engineer and engineering manager?"
3. Confirm: "What is the rollback/abort procedure if this experiment goes wrong?"

Only proceed if all three are satisfied.

---

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md`.

### Step 2: Blast Radius Assessment
Before designing the experiment, assess the maximum possible impact:

**Scope questions:**
- Which services are in scope for the experiment?
- Which services have a dependency on in-scope services (blast radius)?
- What percentage of users could be affected if the experiment escapes its scope?
- Is there a way to limit the experiment to a subset of users or a single region?
- What is the recovery time if something goes wrong (RTO)?

**Blast radius classification:**
| Class | Scope | User impact possible |
|---|---|---|
| Contained | Single pod / replica | < 1% |
| Service | Entire service | Feature-level |
| Platform | Cluster / DB | Major degradation |
| Multi-service | Cross-service | Potential P0 |

Rule: Only run Class "Contained" or "Service" experiments in production without explicit
VP Engineering approval.

### Step 3: Define the Hypothesis
Every experiment must have a clear, falsifiable hypothesis:

```
Hypothesis template:
"We believe that [service] will [behavior] when [failure condition],
because [reason], and we will verify this by [measurement]."

Example:
"We believe that the checkout-api will continue processing orders
within its normal SLO when the inventory-service is unavailable,
because checkout-api has a circuit breaker configured with a 30-second
timeout and a cached fallback, and we will verify this by measuring
the checkout error rate and latency during the experiment."
```

### Step 4: Define Steady State
Establish measurable baseline before the experiment:

```
Steady state metrics (measure 10 minutes before starting):
- checkout error rate: <0.1%
- checkout P99 latency: <500ms
- order creation success rate: >99.9%
```

### Step 5: Design the Experiment
Choose the failure injection type:

| Failure type | What it tests | Common tool |
|---|---|---|
| Pod kill | Service resilience, restart recovery | `kubectl delete pod` |
| Network partition | Dependency failure handling | Chaos Mesh, tc |
| Latency injection | Timeout handling, circuit breakers | Chaos Mesh, Toxiproxy |
| Resource exhaustion | Saturation handling | stress-ng, Chaos Mesh |
| Region failure | Multi-region failover | Route53 health checks, simulated |
| Dependency failure | Fallback and graceful degradation | Chaos Mesh |

Design output:
```
Experiment: checkout-api circuit breaker validation

Failure injection:
  Tool: Chaos Mesh
  Target: inventory-service, all pods, production namespace
  Failure type: network partition (100% packet drop)
  Duration: 5 minutes

Monitoring:
  - Watch: checkout error rate (expect: <1%)
  - Watch: checkout P99 latency (expect: <1s with cache fallback)
  - Watch: circuit breaker open state in Datadog

Abort conditions:
  - checkout error rate > 5% → abort immediately
  - any other service shows unexpected degradation → abort
  - experiment duration > 10 minutes without resolution → abort

Rollback:
  - Remove Chaos Mesh network policy
  - Verify inventory-service connectivity restored
  - Confirm checkout metrics return to steady state
```

### Step 6: Generate the Gameday Runbook
Produce a gameday document with:
- Experiment hypothesis
- Steady state definition
- Timeline (when each step happens, who does what)
- Monitoring checklist
- Abort conditions and rollback procedure
- Success/failure criteria
- Observation notes section

### Step 7: Post-Experiment Analysis
After the experiment:
1. Did steady state hold? (Hypothesis confirmed or refuted?)
2. What surprises occurred?
3. What did the experiment reveal about the system?
4. Generate action items for gaps discovered.

---

## Guidelines

- Never run chaos experiments during business peak hours without a compelling reason.
- Every experiment needs an abort condition — define it before starting.
- Start small: a single pod kill is more valuable than a full region failure as a first experiment.
- "It worked" is not a result — document what metrics confirmed it worked.
- Persona (junior-sre): read-only participation only; do not design or run experiments without
  senior supervision.
