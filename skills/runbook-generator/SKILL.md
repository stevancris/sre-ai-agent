---
name: runbook-generator
description: >
  Generate complete, actionable runbooks for services, alerts, and operational procedures.
  Use when an alert has no runbook, when onboarding a new service, when standardizing
  operational documentation, or when updating stale runbooks. Trigger keywords: generate
  runbook, create runbook, write runbook, runbook template, document procedure, operational
  guide, no runbook exists, runbook missing, new service runbook, need a runbook, write up
  steps, document this alert, how do I document, onboarding docs, ops documentation.
allowed-tools: Read Glob Grep
---

# Runbook Generator Skill

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md` to understand the
deployment tooling, observability stack, and on-call setup.

### Step 2: Gather Inputs
Ask the user for:
- **Service name** — the name of the service this runbook covers
- **Alert name or condition** — what alert triggers this runbook (or "general service runbook")
- **Severity level** — P0 / P1 / P2 / P3
- **Owner team** — which team owns this service
- **What you know about this failure mode** — any context from past incidents or code review

If the runbook is being generated during an active incident (incident-response skill invoked it):
- Pull available context from the incident timeline.
- Mark sections that need to be filled in post-incident with `<!-- TODO: fill in from incident -->`.

### Step 3: Load the Template
Load `skills/oncall-runbook/references/runbook-template.md` as the base structure.

### Step 4: Populate the Runbook

**Alert Trigger Condition** — populate from:
- The alerting rule (if user can share it)
- The metric name and threshold from the user's observability stack

**What This Means** — write a plain-language explanation:
- What does this service do?
- What is the user impact when this alert fires?
- What are the most common causes of this alert?

**Blast Radius** — determine:
- Which services depend on this service?
- Is there user-facing impact?
- Is there any data integrity risk?

**Triage Steps** — generate concrete diagnostic commands specific to the tech stack.
For Kubernetes / Datadog stack, generate `kubectl` and Datadog query commands.
For each step, include: the command, expected output, and what to do if output is wrong.

**Remediation Steps** — generate at least two remediation paths (most common causes).
Each path must include a rollback procedure.

**Persona adjustments:**
- **junior-sre**: verbose commands with full flags explained, no assumed knowledge.
  Example: `kubectl get pods -n production -l app=payment-api --output=wide`
  (The `-n` flag specifies the Kubernetes namespace. `-l` filters by label. `--output=wide`
  shows extra info like the node each pod is running on.)
- **senior-sre**: concise commands, assume kubectl and standard tools are known.

### Step 5: Validate the Runbook
Check that the generated runbook includes all required sections:
- [ ] Alert trigger condition
- [ ] What this means (plain language)
- [ ] Blast radius
- [ ] At least 3 triage steps
- [ ] At least 1 remediation path with rollback
- [ ] Escalation path with time thresholds
- [ ] Post-incident checklist

### Step 6: Output the Runbook
Output the complete runbook in Markdown, ready to commit to a runbooks repository.
Suggest the file path: `skills/oncall-runbook/references/<service-name>-<alert-name>.md`

### Step 7: Follow-up
After generating:
- "Would you like me to walk you through this runbook now for the current alert?"
- "Should I add this runbook to the oncall-runbook references index?"

---

## Guidelines

- A runbook is only as good as its "expected output" sections. Never skip them.
- If you do not know what the expected output should be, say so and mark it as
  `<!-- TODO: validate expected output -->` rather than guessing.
- Runbooks are living documents — always include the Last Updated date and a prompt
  to update after each use.
- Every triage step should be independently executable — avoid "do steps 1–3 first."
