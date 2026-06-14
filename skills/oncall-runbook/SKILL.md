---
name: oncall-runbook
description: >
  Look up, execute, and maintain on-call runbooks. Use when you receive an alert, need
  step-by-step remediation guidance, want to find the right runbook for a service, or need
  to create a new runbook for an alert that currently has none. Trigger keywords: runbook,
  on-call, oncall, alert firing, pagerduty, opsgenie, what do I do, how do I fix,
  remediation steps, service down, alert triggered, need guidance, step by step.
allowed-tools: Read Glob Grep Bash(kubectl get:*) Bash(kubectl describe:*) Bash(kubectl logs:*)
---

# On-Call Runbook Skill

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

### Step 0: Search Knowledge Base First (MANDATORY)
Before looking up any runbook, search `skills/knowledge-base/patterns/` for a pattern
matching the service name or alert description.

```bash
# Agent executes:
Glob: skills/knowledge-base/patterns/<service-name>*.md
Grep: skills/knowledge-base/patterns/ — keywords from alert name
```

If a match is found, surface it immediately:
```
⚡ This failure mode has been seen before.

Pattern: <name> | Last seen: <date> | Resolved in: ~X min

Fastest path (skip to what works):
  → <step 1 from pattern>
  → <step 2 from pattern>

Skip these (dead ends from prior incidents):
  → <dead end 1>
  → <dead end 2>
```

If no pattern found: "First time seeing this — building knowledge as we go."
Proceed to runbook lookup and run `knowledge-capture` when resolved.

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md`.

### Step 2: Identify the Alert
Ask the user for (or extract from their message):
- Service name
- Alert name or condition
- What they are currently observing (error message, metric value, etc.)

### Step 3: Find the Runbook
Search `skills/oncall-runbook/references/` using Glob and Grep for a file matching
the service name or alert name.

If a runbook is found:
- Load it and walk through it step by step.
- Check off steps as the user confirms completion: `[x]` vs `[ ]`.
- If a step fails or produces unexpected output, branch into diagnostic mode.

If no runbook is found:
- Inform the user: "No runbook found for this alert. Creating one now."
- Invoke the `runbook-generator` skill.
- After the new runbook is generated, offer to walk through it.

### Step 4: Diagnostic Mode (when a step fails)
If a runbook step fails or output is unexpected:
1. Ask: "What did you see instead of the expected output?"
2. Check the service's recent logs: `kubectl logs -l app=<service> --since=15m`
3. Check recent events: `kubectl describe pod -l app=<service>`
4. Check dependencies: are upstream services healthy?
5. Generate a modified recovery path based on the actual observation.

### Step 5: Escalation Decision
After 20 minutes of investigation without resolution:
- Junior SRE: `**[ESCALATE]** — page the secondary on-call now.`
- Senior SRE: Surface the escalation option; let the user decide.
- All personas: if data loss or P0 severity is suspected, escalate immediately.

### Step 6: Post-Resolution Runbook Update
After resolution, ask:
- "Did the runbook need any corrections or additions?"
- "Were there any steps that didn't apply?"
- "Did you discover anything new about this failure mode?"

If yes, update the runbook file with the new findings.

---

## References
- `references/runbook-template.md` — standard structure for all runbooks
- `references/alert-catalog.md` — index of known alerts and their runbook locations

---

## Guidelines

- Never skip the "expected output" for each runbook step; it is how the user knows
  if the step worked.
- Diagnostic mode is not debugging from scratch — stay focused on the alert's failure mode.
- If the runbook leads to a destructive action (delete pod, restart deployment), output the
  command for the user to run manually and warn: "This will cause a brief restart. Confirm?"
- After resolution, always prompt to update the runbook; stale runbooks are worse than none.
