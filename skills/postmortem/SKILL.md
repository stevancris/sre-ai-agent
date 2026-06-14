---
name: postmortem
description: >
  Create blameless postmortems after incidents are resolved. Use when an incident is over,
  during post-incident review, or when writing a retrospective. Covers timeline
  reconstruction, contributing factor analysis, action item generation, and distribution.
  Trigger keywords: postmortem, post-mortem, post incident review, PIR, retrospective,
  blameless, lessons learned, what went wrong, action items, incident review, follow-up,
  write up, incident report.
allowed-tools: Read Glob Grep
---

# Postmortem Skill

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

### Step 1: Load Context and Incident Data
Read `context/CONTEXT.md` for persona. Ask the user for:
- Incident name / ID
- Incident timeline (or pull from incident-response skill if available)
- Severity classification
- Affected services and estimated user impact
- Resolution summary

### Step 2: Reconstruct the Timeline
Build a complete chronological timeline with these milestone markers:
- **[STARTED]** — when did the problem actually begin (may predate detection)
- **[DETECTED]** — when did monitoring or a user report alert the team
- **[ACKNOWLEDGED]** — when did someone start working on it
- **[IDENTIFIED]** — when was the root cause identified
- **[MITIGATED]** — when was user impact stopped (may differ from root cause fix)
- **[RESOLVED]** — when was the system fully restored

Calculate and highlight:
- **Time to Detect (TTD):** DETECTED − STARTED
- **Time to Acknowledge (TTA):** ACKNOWLEDGED − DETECTED
- **Time to Mitigate (TTM):** MITIGATED − ACKNOWLEDGED
- **MTTR:** RESOLVED − STARTED

### Step 3: Root Cause Analysis
Apply the five-whys technique. Start from the customer-facing symptom and ask "why"
iteratively until reaching a systemic or process-level cause.

Format:
```
Why 1: Why did users see 503 errors?
  → Because the API pods were crashing.
Why 2: Why were the API pods crashing?
  → Because they ran out of memory.
Why 3: Why did they run out of memory?
  → Because a memory leak was introduced in the v2.3.1 deploy.
Why 4: Why was the memory leak not caught before deploy?
  → Because the staging environment does not run load tests.
Why 5: Why does staging not run load tests?
  → Because we have no automated load testing in CI.
Root Cause: No automated load testing in CI allowed a memory leak to reach production.
```

### Step 4: Contributing Factor Analysis
Categorize contributing factors across four dimensions:
- **Detection gaps** — why was it hard to detect or took too long?
- **Response gaps** — why did response take longer than it should have?
- **Process gaps** — what process or procedure failed or was missing?
- **Tooling gaps** — what tooling limitation made this worse?

### Step 5: Generate Action Items
For each gap identified, generate a SMART action item:
- **What:** specific change to make
- **Why:** which gap it closes
- **Owner:** team or role responsible (do not name individuals; assign to roles)
- **Due:** relative date (e.g., "2 weeks", "next sprint")
- **Priority:** P0 (blocks similar incident) / P1 (reduces risk significantly) / P2 (improvement)

### Step 6: Produce the Postmortem Document
Fill in the template from `references/postmortem-template.md`.

Persona adjustments:
- **sre-manager**: prepend an executive summary with: total downtime, estimated revenue impact
  (if known), number of users affected, and top 1–2 action items.
- **junior-sre**: add a "What I learned" section at the end with educational notes.

### Step 7: Distribution
Recommend the distribution list based on severity:
- P0: all engineering, customer success, executive team, shared to public status page
- P1: engineering team, engineering manager, customer success
- P2/P3: SRE team and service owners

---

## Examples

### Example postmortem action items

| Priority | Action | Owner | Due |
|---|---|---|---|
| P0 | Add memory usage alert at 80% threshold | SRE team | 1 week |
| P0 | Add load test to staging CI pipeline | Backend team | 2 weeks |
| P1 | Add canary deployment step for all services | Platform team | 1 month |
| P2 | Document memory leak debugging runbook | SRE team | 2 weeks |

---

## Guidelines

- Postmortems are blameless: do not name individuals, only systems, processes, and teams.
- The root cause should always be a systemic issue, never "human error."
  ("Human error" is always a symptom — the root cause is why the error was possible.)
- Action items without owners and due dates will not get done; enforce SMART format.
- The five-whys should reach a process or systemic level by Why 4 or 5.
- Never close a postmortem with "we will be more careful next time."
