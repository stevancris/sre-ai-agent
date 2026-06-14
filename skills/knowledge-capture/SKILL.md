---
name: knowledge-capture
description: >
  Capture and persist knowledge from a resolved incident, troubleshooting session, or
  RCA into the agent's context — so the next SRE who faces the same problem benefits
  immediately. This is the closing step of every incident and troubleshooting session.
  It converts ephemeral knowledge (in someone's head or a Slack thread) into durable,
  searchable, agent-readable context. Trigger keywords: save this, remember this fix,
  update the runbook, capture this, add to knowledge base, document what we found,
  don't want to lose this, next time this happens, update agent context, this happened before,
  same issue again, knowledge capture, close out incident.
allowed-tools: Read Glob Grep
---

# Knowledge Capture Skill

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

## Purpose

Every resolved incident contains knowledge. This skill ensures that knowledge is
structured and stored so that:
1. The agent can use it immediately in future similar incidents.
2. Any SRE — junior or senior, new or experienced — gets the same quality of guidance.
3. The team is not dependent on any one person's memory.

---

## Instructions

### Step 1: Identify What Was Learned
At the end of any troubleshooting session or incident, ask the user:

1. "What was the actual root cause?" (even if different from initial hypothesis)
2. "What was the fix that worked?"
3. "What did we try first that did NOT work?"
4. "Was there anything in the runbook that was wrong or missing?"
5. "Is there a signal we could have caught this earlier? (metric, log pattern, alert)"
6. "Would you recognize this faster next time? What would you look for?"

These six questions extract the knowledge that usually stays in someone's head.

### Step 2: Classify the Knowledge Type

Determine which knowledge artifacts need to be created or updated:

| Type | When to create/update | File location |
|---|---|---|
| **Runbook update** | Fix or triage steps changed | `skills/oncall-runbook/references/<service>-<alert>.md` |
| **New runbook** | No runbook existed for this failure mode | `skills/oncall-runbook/references/<service>-<alert>.md` + update `alert-catalog.md` |
| **Failure pattern** | New failure mode discovered for a service | `skills/knowledge-base/patterns/<service>-<failure-mode>.md` |
| **Diagnostic shortcut** | Found a faster way to diagnose | Add to runbook triage steps |
| **False positive note** | Alert fired but was not a real incident | Add to runbook "known issues" section |
| **Company context update** | Tech stack changed, severity levels updated | `context/company/` files |

### Step 3: Update the Runbook
If a runbook exists, update it with:

**Add to triage steps** (if a faster diagnostic was found):
```markdown
### [NEW] Step X: Check <specific thing> first
This was identified in the 2024-01-15 incident as the fastest signal.
```bash
<command that surfaces the issue in < 30 seconds>
```
Expected: <what to look for>
```

**Add to "What did NOT work"** (prevents future SREs from wasting time):
```markdown
## Dead Ends (do not repeat these)
- **Restarting the pod** does not help — the issue is in the DB, not the application.
  Discovered: 2024-01-15 incident. Added by: SRE team.
- **Scaling up replicas** makes it worse — more pods = more connections = faster exhaustion.
```

**Add to "Known issues / False positives"**:
```markdown
## Known False Positives
- This alert fires during scheduled batch jobs between 02:00–03:00 UTC.
  Check job schedule before paging secondary. Discovered: 2024-02-01.
```

**Update "How we detect it faster next time"**:
```markdown
## Early Warning Signals (catch this before it pages)
- DB connection count climbing above 70% of pool limit → investigate before it pages
  Metric: <metric name and query>
  Threshold: add alert at 75% (P2) and 90% (P1)
```

### Step 4: Create a Failure Pattern Entry
For novel failure modes, create a structured pattern entry:

**File:** `skills/knowledge-base/patterns/<service>-<failure-mode>.md`

```markdown
# Failure Pattern: <Service> — <Failure Mode>

**First observed:** YYYY-MM-DD
**Times seen:** 1
**Last seen:** YYYY-MM-DD
**Related incidents:** [links or incident IDs]

## Signature
How to recognize this failure mode when you see it:
- Observable symptom: <what metrics/logs show>
- Typical trigger: <what usually causes it>
- Time of day pattern: <if any>
- Traffic pattern correlation: <if any>

## Fastest Diagnostic Path
1. Check <X> → if you see <Y>, this is the pattern
2. Confirm by checking <Z>
Total time to confirm: ~X minutes

## Fix
<what actually resolves it — specific commands or steps>

## Why It Happens
<brief technical explanation — enough to understand, not a full postmortem>

## Prevention
<what would prevent this from happening or being caught earlier>

## Dead Ends
- Do NOT try <X> — it does not help because <reason>

## Notes
<anything else worth knowing — edge cases, variations, related failure modes>
```

### Step 5: Update the Alert Catalog
If a new runbook was created, add it to `skills/oncall-runbook/references/alert-catalog.md`:
```markdown
## <Service Name>
- Alert: <alert-name>
  Runbook: skills/oncall-runbook/references/<file>.md
  Severity: P<N>
  Last updated: YYYY-MM-DD
  Notes: <any important context about this alert>
```

### Step 6: Propose Early Warning Improvements
If the incident could have been caught earlier, propose concrete alert improvements:

```
Early warning gap identified:
  Current detection: PagerDuty fired at 90% connection pool utilization
  Could have been: P2 alert at 70% would give 15 extra minutes of lead time

Proposed new alert:
  Metric: db_connection_pool_utilization
  Threshold: > 70% for 5 minutes → P2 (no page, Slack only)
  Threshold: > 85% for 2 minutes → P1 (page primary)
  Add to: skills/observability/ alert recommendations
```

### Step 7: Confirm and Commit
Show the user a summary of all knowledge updates made:

```
Knowledge capture complete for: [Incident Name]

Updated:
  ✓ skills/oncall-runbook/references/postgresql-connection-exhaustion.md
    - Added "scaling replicas makes it worse" dead end
    - Added early warning signal at 70% pool utilization
    - Updated triage step 2 with faster diagnostic command

Created:
  ✓ skills/knowledge-base/patterns/postgres-connection-exhaustion.md
    - New failure pattern documented with full signature

Catalog:
  ✓ alert-catalog.md updated

Next recommended action:
  - Add a P2 alert at 70% connection pool utilization (see above)
  - Propose an RFC for connection pooler (PgBouncer) to prevent recurrence
```

---

## The Compounding Effect

Each captured incident makes the agent more useful for the next one:

```
Incident 1: SRE spends 47 min, no runbook
    → knowledge-capture runs → runbook created

Incident 2 (3 months later, different SRE): same failure mode
    → agent finds the runbook → resolution in 12 min
    → knowledge-capture adds "false positive at 02:00 UTC" finding

Incident 3 (6 months later, junior SRE, 2am): same failure mode
    → agent finds runbook + false positive note → "is this the batch job window?"
    → checks → confirms false positive → no incident → 3 min
```

The knowledge stays even when the SRE who discovered it leaves.

---

## Guidelines

- Run knowledge-capture at the end of EVERY incident, even P2s and false positives.
  False positives are especially valuable — they prevent future unnecessary pages.
- "Dead ends" are as valuable as the fix. Future SREs waste time on the same wrong paths.
- Do not wait for the postmortem to capture knowledge. Do it while the incident is fresh.
  The postmortem is the formal document; this is the operational knowledge.
- A 5-minute knowledge capture prevents a 47-minute incident next time.

## Importing Historical RCAs

This skill captures knowledge from incidents that just happened. If your team has an
existing bank of RCAs written before the agent was set up, use the `import-rca` skill
instead — it accepts any RCA format (Google SRE, Atlassian, PagerDuty, Confluence, or
free-form) and converts them into knowledge-base patterns in bulk.
