---
name: import-rca
description: >
  Transform any RCA or postmortem document into a reusable knowledge-base pattern.
  Accepts any company format — Google SRE, Atlassian, PagerDuty, Elastic, plain text,
  Confluence export, or free-form notes. Extracts and distills the incident into a
  structured failure pattern that the agent can search in future incidents.
  Trigger keywords: import rca, convert postmortem, add to knowledge base, import incident,
  we have an old RCA, transform postmortem, bulk import RCA, add past incident,
  import from confluence, convert our incident report.
allowed-tools: Read Glob Grep
---

# Import RCA Skill

## Setup Check

Before loading context files, check if `context/CONTEXT.md` exists in the current directory.

**If `context/CONTEXT.md` exists** — read it and proceed normally.

**If `context/CONTEXT.md` does not exist** — ask the user for their role and company
context inline before proceeding.

---

## Purpose

Every company has a bank of past RCAs — in Confluence, Google Docs, Notion, Jira, or
plain text. This skill converts them into the agent's knowledge-base pattern format so
that institutional memory from past incidents is immediately searchable.

**The conversion logic:**

| RCA field (any format) | → | Knowledge-base pattern field |
|---|---|---|
| Summary / executive summary | → | frontmatter `failure-mode` + pattern title |
| Impact duration, MTTR | → | `avg-mttr-minutes`, `best-mttr-minutes` |
| Root cause + trigger | → | `## Symptom Signature` + `## Trigger Conditions` |
| Timeline / detection method | → | `## Fastest Diagnostic Path` |
| What didn't work / dead ends | → | `## Dead Ends — Do Not Try These` |
| Resolution steps | → | `## Resolution` |
| What went well / lucky | → | `## Notes` |
| Action items / prevention | → | `## Prevention` |
| Incident date | → | `first-seen`, `last-seen` |

---

## Instructions

### Step 1: Receive the RCA

Ask the user to paste or provide their RCA document. Accept any of the following:

- **Paste inline** — user pastes the text directly into the chat
- **File path** — user provides a path, read it with the Read tool
- **Multiple RCAs** — user can provide multiple at once for bulk import

If the user has multiple RCAs, process them one at a time and confirm each before moving
to the next.

---

### Step 2: Detect the Source Format

Identify which format the RCA follows and acknowledge it. Common formats:

**Google SRE format** — has sections: Summary, Impact, Root Causes, Trigger, Resolution,
Detection, Action Items, Lessons Learned (went well / wrong / lucky), Timeline.

**Atlassian / Jira format** — has: Incident summary, Contributing factors, Timeline,
Impact, Resolution, Follow-up actions. Often has a severity field and component labels.

**PagerDuty format** — has: Incident overview, Timeline, Impact analysis, Contributing
factors, Resolution summary, Follow-up tasks.

**Elastic / cloud provider format** — has: Incident title, Date/time, Duration, Impact,
Summary, Root cause, Remediation, Prevention measures.

**Elastic / cloud provider format** — has: Incident title, Date/time, Duration, Impact,
Summary, Root cause, Remediation, Prevention measures.

**SRE AI Agent postmortem format** — output from this agent's own `postmortem` skill.
Has sections: Summary, Impact, Root Causes, Trigger, Timeline, Lessons Learned
(went well / wrong / lucky), Action Items, Distribution. Map as follows:
- "Root Causes + Trigger" → `## Symptom Signature` + `## Trigger Conditions`
- "Timeline" → `## Fastest Diagnostic Path` (rewrite as forward-looking steps)
- "What went wrong + Lessons Learned" → `## Dead Ends — Do Not Try These`
- "Resolution" → `## Resolution`
- "Action Items" → `## Prevention`
- "What went well + lucky" → `## Notes`

**Custom / free-form** — any internal template. Extract by intent, not by heading name.

---

### Step 3: Extract and Map Fields

Extract the following from the RCA, regardless of what the source headings are called:

#### 3a. Frontmatter metadata
```yaml
service: <service or system that failed>
failure-mode: <short slug: what broke, e.g. "database-connection-pool-exhaustion">
first-seen: <incident date, YYYY-MM-DD>
last-seen: <incident date if single occurrence, same as first-seen>
times-seen: 1
avg-mttr-minutes: <total incident duration in minutes>
best-mttr-minutes: <same as avg for first occurrence>
related-incidents: [<incident ID if available>]
```

#### 3b. Symptom Signature
Extract: what were the observable signals? Metrics, alerts, logs, user reports, error
messages. Focus on signals visible in the **first 2 minutes** of the incident.

If the RCA doesn't explicitly list symptoms, infer from: "how was it detected?",
"what did the monitoring show?", "what did users report?"

#### 3c. Trigger Conditions
Extract: what caused the failure? What changed or reached a threshold?
Distinguish between:
- **Root cause** (the underlying condition)
- **Trigger** (the event that activated it)

Example: root cause = undersized connection pool, trigger = traffic spike from flash sale.

#### 3d. Fastest Diagnostic Path
Extract from: timeline, "how we found it", "investigation steps", "what we checked".
Rewrite as ordered steps (1, 2, 3) with the fastest path to confirm the failure mode.
Include any CLI commands, queries, or dashboard links mentioned.

If no commands are mentioned, write the diagnostic steps as prose with placeholders:
```bash
# Check <metric> in <observability tool>
# Look for <symptom> in <log source>
```

#### 3e. Dead Ends — Do Not Try These
Extract from: "what didn't work", "what we tried first", "mistakes made", "what to avoid".
Also infer from the timeline: steps taken before resolution that caused delay or made
things worse.

Format as a table:
| What was tried | When | Result | Why it failed |

If the RCA has no explicit dead ends, note: "No dead ends documented in source RCA.
Add here after future occurrences."

#### 3f. Resolution Steps
Extract: the exact steps that resolved the incident. Be specific — include commands,
config changes, rollbacks, or manual interventions.

#### 3g. Prevention (Action Items)
Extract: follow-up tasks, action items, recommendations. Preserve ownership and due dates
if present.

#### 3h. Notes
Extract: "what went well", "lucky factors", "things we learned", observations about
response quality. Also include context about timing, team, or contributing circumstances.

---

### Step 4: Generate the Pattern File

Output the complete pattern in this format:

```markdown
---
service: <service>
failure-mode: <failure-mode-slug>
first-seen: <YYYY-MM-DD>
last-seen: <YYYY-MM-DD>
times-seen: <N>
avg-mttr-minutes: <N>
best-mttr-minutes: <N>
related-incidents: [<id>]
source-rca: <format detected, e.g. "Google SRE format" or "Atlassian Jira">
---

# Failure Pattern: <service> — <Failure Mode Title>

> Imported from RCA. Review and enrich after the next occurrence.

## Symptom Signature
...

## Trigger Conditions
...

## Fastest Diagnostic Path
...

## Resolution
...

## Dead Ends — Do Not Try These
...

## Prevention
...

## Notes
...
```

---

### Step 5: Confirm and Save

Show the generated pattern to the user and ask:

1. **"Does this look accurate?"** — let them correct any mismatched fields
2. **"What filename should I use?"** — suggest: `<service>-<failure-mode>.md`
3. **"Confirm to save to `skills/knowledge-base/patterns/<filename>.md`"**

After confirmation, write the file.

---

### Step 6: Bulk Import

If the user has multiple RCAs to import:

- After saving the first pattern, ask: **"Do you have more RCAs to import?"**
- If yes, repeat from Step 1
- After all are imported, show a summary:

```
Import complete — <N> patterns added to knowledge-base/patterns/

Services covered:
  - payment-api (2 patterns)
  - auth-service (1 pattern)
  - order-service (1 pattern)

Run `sre-agent search <query>` to verify patterns are searchable.
```

---

## Quality Checks

Before saving, verify the pattern has:

- [ ] `failure-mode` slug is lowercase with hyphens, not spaces
- [ ] `avg-mttr-minutes` is a number, not a string
- [ ] `## Symptom Signature` has at least one observable signal
- [ ] `## Fastest Diagnostic Path` has at least one actionable step
- [ ] `## Resolution` has at least one concrete action

If any check fails, flag it and ask the user to fill in the gap rather than saving an
incomplete pattern.

---

## Handling Incomplete RCAs

Some RCAs are sparse. Handle gracefully:

| Missing field | Action |
|---|---|
| No symptoms listed | Ask: "What would you look for first if this happened again?" |
| No diagnostic steps | Ask: "How did you confirm it was this issue?" |
| No dead ends | Leave section with note: "Not documented — add after next occurrence" |
| No MTTR | Ask: "Approximately how long did it take to resolve?" |
| No action items | Leave `## Prevention` empty with TODO marker |

Never leave a required field blank without a placeholder or note. An incomplete pattern
with TODOs is better than a skipped import.

---

## Guidelines

- Preserve technical specifics — exact error messages, metric names, threshold values.
  These are what make patterns searchable in future incidents.
- Rewrite for future use — the RCA was written looking backwards. The pattern should read
  as instructions for someone responding to the incident right now.
- Be concise — target 80–150 lines per pattern. Long patterns don't get read during incidents.
- Add `source-rca` to frontmatter so future readers know this was imported, not
  written from a live incident.
- If multiple incidents describe the same failure mode, merge them into one pattern and
  set `times-seen` accordingly.
