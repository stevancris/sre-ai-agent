---
name: rfc
description: >
  Draft, review, and iterate on RFC (Request for Comments) documents for infrastructure,
  reliability, and platform changes. Use when proposing a significant technical change,
  new architecture, major process shift, or any decision that needs cross-team alignment
  before implementation. Covers problem framing, solution options, trade-off analysis,
  risk assessment, and rollout plan. Trigger keywords: RFC, request for comments, proposal,
  design doc, design document, architecture proposal, ADR, architecture decision record,
  technical proposal, propose a change, write a proposal, get alignment, we need to decide,
  compare options, technical decision, platform change, migration plan, new architecture.
allowed-tools: Read Glob Grep Bash(git log:*)
---

# RFC Skill

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md`.
Persona adjustments:
- **junior-sre**: provide extra guidance on each RFC section, explain why it matters.
- **senior-sre**: focus on trade-off depth and risk analysis.
- **sre-manager**: emphasize business impact, team bandwidth, and decision timeline.

### Step 2: Determine the RFC Type
Classify the RFC scope to calibrate how formal and detailed it needs to be:

| Type | Scope | Typical audience | Approval needed |
|---|---|---|---|
| **Lightweight** | Single-service change, low risk | SRE team | Team lead |
| **Standard** | Multi-service or platform-wide | Engineering teams | Staff engineer + manager |
| **Major** | Company-wide infra, security posture, data architecture | All engineering + leadership | VP Engineering / CTO |

### Step 3: Gather RFC Inputs
Ask the user for:
1. **Problem statement** — what is broken, missing, or needs to improve? Why now?
2. **Proposed solution** — what is the leading idea (even rough)?
3. **Alternatives considered** — what other options exist or have been ruled out?
4. **Constraints** — budget, timeline, team bandwidth, compliance, existing contracts
5. **Who needs to weigh in** — which teams or individuals are stakeholders?

### Step 4: Draft the RFC

Populate the full RFC document using the structure below.

---

#### RFC Structure

```markdown
# RFC: <Title>

**RFC Number:** RFC-<NNNN>
**Status:** Draft | Under Review | Accepted | Rejected | Superseded
**Author(s):** <role or name>
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Review Deadline:** YYYY-MM-DD
**Stakeholders:** <teams or roles that must review>
**Approvers:** <who has final say>
```

---

**## Summary**

One paragraph. What are we changing, why, and what is the expected outcome?
Readers should understand the full proposal after reading only this section.

---

**## Problem Statement**

Describe the current state and why it is a problem. Be specific:
- What is the measurable impact of the current situation? (latency numbers, incident count,
  engineering hours lost, cost, customer complaints)
- Who is affected?
- Why is this the right time to address it?

Avoid: "our system is slow." Use: "P99 latency for the order-service is 2.3s against a 500ms
SLO target, causing error budget exhaustion 3 months in a row and 4 P1 incidents in Q4."

---

**## Goals**

Bullet list of what success looks like. Each goal should be measurable:
- ✅ Reduce order-service P99 latency from 2.3s to < 500ms
- ✅ Eliminate connection pool exhaustion as a failure mode
- ✅ No additional headcount required for implementation

**Non-goals** (explicitly out of scope for this RFC):
- ❌ Migrating the legacy reporting pipeline (separate RFC)
- ❌ Changes to the authentication service

---

**## Proposed Solution**

Describe the chosen approach in enough detail that an engineer can evaluate it.

Include:
- Architecture diagram (ASCII or description)
- Key components and how they interact
- Data flow changes
- API or interface changes
- Configuration or infrastructure changes

**Implementation phases** (break into reviewable chunks):
1. Phase 1: [what, timeline, who]
2. Phase 2: [what, timeline, who]
3. Phase 3: [what, timeline, who]

---

**## Alternative Solutions**

For each alternative, explain:
- What it is
- Why it was considered
- Why it was not chosen (the key reason)

| Alternative | Pros | Cons | Reason rejected |
|---|---|---|---|
| Option A | | | |
| Option B | | | |
| Do nothing | | | |

The "do nothing" option must always be included with an honest assessment of its cost.

---

**## Trade-offs and Risks**

### Trade-offs
What are we giving up or accepting as a cost of this approach?
- Performance vs. consistency
- Operational simplicity vs. feature richness
- Cost vs. reliability
- Speed of delivery vs. safety

### Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Migration causes data loss | Low | High | Dual-write with validation before cutover |
| Adoption slow across teams | Medium | Medium | Provide migration tooling and office hours |
| Cost higher than estimated | Medium | Low | Phase rollout, monitor cost per phase |

### Reliability Impact
- Does this change affect any SLO?
- What is the failure mode if this goes wrong during rollout?
- What is the rollback plan?

---

**## Rollout Plan**

How will this change be deployed safely?

- [ ] Feature flagged? (yes / no)
- [ ] Canary rollout? (yes / no — what % and what duration)
- [ ] Rollback procedure: [describe]
- [ ] Validation criteria before proceeding to next phase: [describe]
- [ ] Who owns the rollout?

**Rollback trigger conditions:**
- [metric threshold that triggers rollback]

---

**## Operational Impact**

- **On-call burden:** does this increase or decrease toil? By how much?
- **Runbook changes needed:** [list]
- **Alert changes needed:** [list]
- **Dashboard changes needed:** [list]
- **SLO changes needed:** [list]

---

**## Resource Requirements**

| Resource | Estimate | Notes |
|---|---|---|
| Engineering time | X weeks | Y engineers |
| Infrastructure cost delta | +/- $X/month | |
| External dependencies | [list] | |
| Timeline | Start: YYYY-MM-DD | Done: YYYY-MM-DD |

---

**## Open Questions**

List questions that are not yet resolved and who needs to answer them:
- [ ] Q: Should we use X or Y for the queue? **Owner:** @platform-team **Due:** YYYY-MM-DD
- [ ] Q: What is the data retention requirement? **Owner:** @legal **Due:** YYYY-MM-DD

---

**## Decision**

*Fill in after review period closes.*

**Decision:** Accepted / Rejected / Accepted with modifications

**Rationale:** [why]

**Conditions / modifications:** [if any]

**Decided by:** [approvers] on YYYY-MM-DD

---

**## References**

- Related RFCs: [links]
- Related incidents/postmortems: [links]
- External references: [links]

---

### Step 5: Review Facilitation
After drafting, suggest:
1. Who should review (based on stakeholders named above)
2. A review deadline (typically 5–10 business days for standard, 2 weeks for major)
3. The review format: async comments, or a synchronous review meeting?

For major RFCs, recommend a structured review meeting with:
- Presenting author walks through problem + proposed solution (15 min)
- Open Q&A and challenge session (30 min)
- Decision or next steps (15 min)

### Step 6: Iteration Support
If the user shares feedback or comments from reviewers:
- Summarize the key objections
- Suggest how to address each objection
- Identify which objections should change the proposal vs. which should be documented as
  trade-off acknowledgments

---

## Examples

### Example: RFC for migrating from polling to event-driven architecture

**Problem:** Polling-based job processor adds 10–30s latency to user notifications and
consumes 40% of DB read capacity on polling queries. SLO for notification delivery
(< 5s) is breached 12 days per month.

**Goal:** Deliver notifications within 5s of trigger event with < 0.1% loss.

**Proposed solution:** Replace polling with SQS FIFO queue. Job producers publish events.
Notification service consumes from queue. Estimated DB read reduction: 60%.

**Alternatives:**
- WebSockets: rejected — requires stateful connection management, high ops cost
- Reduce polling interval: rejected — increases DB load further, does not meet SLO
- Do nothing: rejected — SLO breach is accelerating, impacting customer retention

---

## Guidelines

- The problem statement must include data, not just complaints.
- Every RFC must have a "do nothing" alternative with an honest cost.
- Open questions should be tracked with owners and due dates — not left vague.
- An RFC is not a design spec — it is a decision document. Enough detail to evaluate,
  not enough detail to implement without further work.
- Persona (sre-manager): always include a one-paragraph executive summary and a resource
  requirements table. Flag if the RFC requires headcount or budget approval.
- RFCs should be version-controlled. Suggest the file path:
  `docs/rfcs/RFC-<NNNN>-<short-title>.md`
