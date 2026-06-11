---
name: rca-summary
description: >
  Generate a concise, shareable RCA (Root Cause Analysis) summary from raw incident data,
  postmortem notes, or a completed root-cause-analysis skill session. Use when you need
  to communicate findings quickly to stakeholders, produce a Slack or email digest of an
  RCA, create a one-pager for management, or add a brief RCA entry to a knowledge base.
  Distinct from the full postmortem or deep root-cause-analysis skill — this produces a
  tight, readable summary optimized for sharing. Trigger keywords: RCA summary, summarize
  RCA, RCA one-pager, share the RCA, brief RCA, quick summary of what happened, executive
  RCA, RCA for management, send the findings, incident summary, what happened summary,
  TL;DR of the incident, incident digest, share postmortem findings, RCA writeup, brief
  postmortem.
allowed-tools: Read Glob Grep
---

# RCA Summary Skill

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` for persona. The output format varies significantly by persona:
- **junior-sre**: learning-focused, detailed enough to build mental model
- **senior-sre**: dense technical digest, assumes shared context with the team
- **sre-manager**: business-impact-first, ready to forward to executives

### Step 2: Gather Source Material
Accept input from any of these sources (ask the user which applies):
- A completed `postmortem` skill session in this conversation
- A completed `root-cause-analysis` skill session in this conversation
- Raw text pasted by the user (incident channel log, notes, timeline)
- A postmortem document file path (read it with the Read tool)

### Step 3: Extract the Key Facts
From the source material, extract:

| Field | Source |
|---|---|
| Incident name / ID | postmortem title or incident channel name |
| Date and time (UTC) | incident timeline |
| Duration | RESOLVED time − STARTED time |
| Severity | P0 / P1 / P2 / P3 |
| Services affected | blast radius section |
| User impact | impact section |
| What happened | symptom description |
| Why it happened | root cause from five-whys |
| How it was fixed | resolution section |
| How it was detected | timeline (DETECTED entry) |
| TTD / TTM / MTTR | calculated from timeline |
| Top action items | action items table |

### Step 4: Generate the RCA Summary

Produce the summary in the format matching the requested audience:

---

#### Format A: Slack / Teams Digest (default)

Optimized for posting in an incident channel or engineering Slack channel.
Aim for < 300 words, scannable with bold headings.

```
*RCA Summary — [Incident Name]* | [Date] | [Duration] | [Severity]

*What happened*
[2–3 sentences. What did users experience? When did it start and end?]

*Root cause*
[1–2 sentences. The systemic reason this was possible, not just the proximate cause.]

*Contributing factors*
• [Factor 1]
• [Factor 2]

*How we detected it*
[1 sentence. Alert, user report, or manual discovery. How long after the problem started?]

*How we fixed it*
[1–2 sentences. Immediate remediation taken.]

*Key metrics*
• Time to detect: Xm | Time to mitigate: Xm | MTTR: Xh Ym
• Users affected: ~N (X%)

*Top action items*
1. [Action] — [Owner role] — [Due date]
2. [Action] — [Owner role] — [Due date]
3. [Action] — [Owner role] — [Due date]

Full postmortem: [link or "in progress"]
```

---

#### Format B: Executive / Management Email

Optimized for forwarding to VP, CTO, or customer success. Non-technical language.
Aim for < 200 words.

```
Subject: Incident Summary — [Service/Feature], [Date]

On [date], [service or feature] experienced [plain-language description of user impact]
for approximately [duration]. This affected approximately [N] users ([X]% of our user base).

Root cause: [one sentence in plain language — no jargon]

We resolved the incident by [resolution description].

To prevent recurrence, we are:
1. [Action item 1 — outcome-focused, not technical]
2. [Action item 2]
3. [Action item 3]

A full technical postmortem is [in progress / available here: link].

Please let me know if you have any questions.
```

---

#### Format C: Knowledge Base / Confluence Entry

Optimized for long-term reference. Structured for searchability.

```markdown
# RCA: [Incident Name]
**Date:** YYYY-MM-DD | **Severity:** P<N> | **Duration:** Xh Ym | **MTTR:** Xh Ym

## What Happened
[2–3 sentences. Observable impact from user perspective.]

## Timeline (condensed)
- `HH:MM` Started
- `HH:MM` Detected (TTD: Xm)
- `HH:MM` Mitigated (TTM: Xm)
- `HH:MM` Resolved (MTTR: Xm)

## Root Cause
[1–2 sentences. Systemic cause.]

## Proximate Cause
[1 sentence. Immediate technical trigger.]

## Contributing Factors
- **Detection gap:** [why it took Xm to detect]
- **Response gap:** [what slowed response, if applicable]
- **Process gap:** [what process was missing]

## Resolution
[What was done to stop the impact.]

## Action Items
| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | | | | Open |
| 2 | | | | Open |

## Tags
`[service-name]` `[failure-mode]` `[team-name]`

Full postmortem: [link]
```

---

#### Format D: One-Line Digest (for incident retrospective lists)

For weekly/monthly incident digest tables:

```
| YYYY-MM-DD | P<N> | [Service] | [Xh Ym] | [Root cause in 10 words] | [Top action item] |
```

---

### Step 5: Offer Format Selection
If the user did not specify a format, ask:
"Which format would you like?
A) Slack digest (default)
B) Executive email
C) Knowledge base / Confluence entry
D) One-line digest"

Or produce Format A automatically and offer to convert to others.

### Step 6: Follow-Up Prompts
After generating the summary, offer:
- "Want me to also generate a one-line version for your monthly incident digest?"
- "Should I add this to the knowledge base (Format C)?"
- "Would you like a version tailored for customer communication?"

---

## Examples

### Example Slack digest (senior-sre persona)

```
*RCA Summary — DB Connection Pool Exhaustion* | 2024-01-15 | 47 min | P1

*What happened*
Checkout failures (503s) for ~15% of users between 14:03–14:50 UTC.
Impact: estimated 2,400 failed checkout attempts.

*Root cause*
No automated load testing in CI allowed an N+1 query regression (introduced in v2.4.0)
to reach production undetected.

*Contributing factors*
• No connection pool saturation alert (detection took 42 min post-deploy)
• Staging does not mirror production traffic patterns

*How we detected it*
PagerDuty latency P99 alert fired at 14:03 UTC — 42 minutes after deploy completed.

*How we fixed it*
Rolled back to v2.3.9 at 14:45 UTC. Restored in 7 minutes.

*Key metrics*
• TTD: 42m | TTM: 7m | MTTR: 47m
• Users affected: ~2,400 (~15% of active users in window)

*Top action items*
1. Add DB connection pool saturation alert — SRE team — Jan 22
2. Add load test to CI pipeline — Backend team — Feb 5
3. Implement canary deploy for all services — Platform team — Feb 20

Full postmortem: [link]
```

---

## Guidelines

- The root cause in a summary must be the systemic cause, not "the deploy broke it."
- Never include names of individuals in the summary — only teams and roles.
- TTD / TTM / MTTR must be calculated accurately from the timeline; do not estimate.
- Persona (sre-manager): always lead with user/business impact before technical detail,
  and ensure action items are outcome-focused ("reduce MTTR by X%" not "add an alert").
- If source material is incomplete (missing timeline, no root cause identified yet):
  flag the gaps clearly and produce a partial summary with `[TBD]` placeholders.
  Do not fabricate data.
