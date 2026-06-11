# Postmortem: [Incident Title]

**Date:** YYYY-MM-DD
**Severity:** P<N>
**Duration:** X hours Y minutes
**Author:** SRE Team
**Status:** Draft / Under Review / Approved

---

## Executive Summary
*(sre-manager persona: always fill this section)*

In 3 sentences or fewer: what happened, how many users were affected, and what is the
top action item to prevent recurrence.

> Example: On January 15th, a database connection pool exhaustion caused checkout failures
> for ~15% of users for 47 minutes. The root cause was an N+1 query regression introduced
> in the v2.4.0 deploy that was not caught by existing tests. The primary action item is
> to add automated load testing to CI before production deploys.

---

## Impact

| Metric | Value |
|---|---|
| Incident duration | X hours Y minutes |
| Users affected | ~N (X% of active users) |
| Services affected | service-a, service-b |
| Error budget consumed | X minutes of a Y-minute monthly budget |
| Estimated revenue impact | $X (if known) |

---

## Timeline

All times in UTC.

| Time | Event |
|---|---|
| HH:MM | [STARTED] Problem began |
| HH:MM | [DETECTED] Alert fired / user reported |
| HH:MM | [ACKNOWLEDGED] On-call engineer began investigation |
| HH:MM | [IDENTIFIED] Root cause identified |
| HH:MM | [MITIGATED] User impact stopped |
| HH:MM | [RESOLVED] System fully restored |

**Key metrics:**
- Time to Detect (TTD): X minutes
- Time to Acknowledge (TTA): X minutes
- Time to Mitigate (TTM): X minutes
- MTTR: X minutes

---

## Root Cause

### Five-Whys Analysis

**Symptom:** [customer-facing observable symptom]

| # | Why? | Answer |
|---|---|---|
| 1 | Why did [symptom] occur? | |
| 2 | Why did [answer 1] happen? | |
| 3 | Why did [answer 2] happen? | |
| 4 | Why did [answer 3] happen? | |
| 5 | Why did [answer 4] happen? | |

**Root Cause:** [Systemic or process-level cause — never "human error"]

**Proximate Cause:** [Immediate technical cause]

---

## Contributing Factors

### Detection Gaps
- [What made this hard to detect or caused detection to be slow?]

### Response Gaps
- [What slowed down the response after detection?]

### Process Gaps
- [What process or procedure was missing or failed?]

### Tooling Gaps
- [What tooling limitation contributed to the impact?]

---

## Action Items

| Priority | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| P0 | | SRE Team | | Open |
| P1 | | | | Open |
| P2 | | | | Open |

---

## What Went Well

- [Things that worked as expected and helped limit the impact]

---

## Lessons Learned

- [Non-obvious insights from this incident that the broader team should know]

---

## Appendix

### Relevant Metrics / Screenshots
[Link to dashboard snapshot or paste metrics here]

### Relevant Logs
[Key log lines that were useful in diagnosis]

### Communication Log
[Summary of stakeholder communications during the incident]
