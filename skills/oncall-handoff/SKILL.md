---
name: oncall-handoff
description: >
  Generate a structured on-call handoff document when shifting between on-call engineers.
  Use at the end of an on-call shift, when handing over an active incident to another
  engineer, or when an engineer needs to step away mid-incident. Ensures no context is
  lost between shifts and the incoming SRE can continue without starting from scratch.
  Trigger keywords: handoff, hand off, hand over, shift change, end of shift, my shift
  is ending, taking over, I'm stepping off, passing the pager, shift handover, oncall
  handover, who's next, briefing the next person, context transfer, shift summary.
allowed-tools: Read Glob Grep
---

# On-Call Handoff Skill

## Purpose

Knowledge loss at shift boundaries is one of the most dangerous moments in SRE operations.
When context lives only in the outgoing engineer's head, the incoming engineer starts blind —
re-diagnosing what was already known, missing nuance about what failed, wasting precious
minutes in an active incident.

This skill produces a handoff document that makes shift transitions invisible to the system.

---

## Instructions

### Step 1: Determine Handoff Type

| Type | When | Urgency |
|---|---|---|
| **Routine shift handoff** | End of oncall week/day, no active incidents | Low — thorough summary |
| **Active incident handoff** | Handing over an ongoing P0/P1 mid-investigation | High — fast, focused |
| **Mid-incident step-away** | Engineer must leave briefly (< 1 hour) | Medium — quick brief + return plan |

### Step 2: Gather Handoff Context

Ask the outgoing SRE:

**For routine handoff:**
1. Any alerts that fired this shift? (even if resolved)
2. Any changes deployed this shift that could affect the incoming week?
3. Any services behaving unusually or "to watch"?
4. Any open tickets or follow-ups that need action?
5. Anything the incoming SRE should know that isn't in a ticket?

**For active incident handoff:**
1. What is the incident? (name, severity, affected service)
2. What is the current state? (what symptoms are visible right now)
3. What have we already tried? (and what happened)
4. What is the current hypothesis about root cause?
5. What is the next action the incoming SRE should take?
6. What are the abort/escalate conditions?
7. Where is the incident channel and bridge?

---

### Step 3: Generate the Handoff Document

#### Format A: Routine Shift Handoff

```markdown
# On-Call Handoff — Week of YYYY-MM-DD

**Outgoing:** <role/name>
**Incoming:** <role/name>
**Handoff time:** YYYY-MM-DD HH:MM UTC
**Shift duration:** X days

---

## Shift Summary

**Overall:** 🟢 Quiet / 🟡 Moderate / 🔴 Heavy

Incidents this shift: <N>
Alerts fired (including non-paging): <N>
Deploys that touched production: <N>

---

## Active Incidents (if any)

> None — clean handoff.

OR

> ⚠️ 1 active incident — see Active Incident Handoff section below.

---

## Resolved Incidents This Shift

| Time | Service | Severity | Duration | Root Cause (brief) | Runbook updated? |
|---|---|---|---|---|---|
| HH:MM UTC | payment-api | P1 | 23 min | Connection pool exhaustion | ✅ Yes |
| HH:MM UTC | auth-service | P2 | 8 min | False positive — batch job window | ✅ Yes |

---

## Things to Watch

Services or systems that are not in incident but behaving unusually:

- **order-service**: P99 latency trending up since Tuesday deploy. Not alerting yet but
  approaching threshold. Watch: `<metric link>`. Contact: backend team if it pages.

- **RDS prod-primary**: Disk at 72%, growing ~2GB/day. Not critical yet but will need
  attention within ~2 weeks. Ticket: <link>

---

## Deployments This Shift

| Service | Version | When | Who | Notes |
|---|---|---|---|---|
| payment-api | v2.4.1 | Mon 14:30 UTC | platform-team | Hotfix for connection pool bug |
| user-service | v1.9.0 | Wed 10:00 UTC | backend-team | New profile feature — canary ongoing |

> ⚠️ user-service v1.9.0 canary is still rolling (currently at 25%). Monitor error rate
> during ramp to 100% on Thursday.

---

## Open Follow-Ups (needs action this shift)

- [ ] Add connection pool alert at 70% utilization — SRE team — Due: Friday
      Context: came out of Monday's incident, will prevent next occurrence
- [ ] Check if order-service latency continues trending up — check by Wednesday
- [ ] Review capacity plan for prod DB disk growth — ticket <link>

---

## Knowledge Captured This Shift

New patterns added to knowledge base:
- `skills/knowledge-base/patterns/payment-api-connection-exhaustion.md` — updated with
  "scaling replicas makes it worse" dead end
- `skills/knowledge-base/patterns/auth-service-batch-false-positive.md` — new entry

---

## Notes for Incoming SRE

Free-text field for anything that doesn't fit the above:
<outgoing SRE's notes — anything the incoming person should know>

---

## Handoff Acknowledgment

- [ ] Incoming SRE has read this document
- [ ] Incoming SRE has access to incident channel(s)
- [ ] Incoming SRE knows how to reach outgoing SRE if needed (for < 1 hour after handoff)
```

---

#### Format B: Active Incident Handoff

For use when handing over a P0 or P1 in progress. Speed matters — keep it tight.

```markdown
# 🚨 Active Incident Handoff

**Outgoing:** <name/role>
**Incoming:** <name/role>
**Time:** HH:MM UTC
**Estimated time outgoing has been on this:** Xh Ym

---

## The Incident

**Name:** <incident channel name>
**Severity:** P<N>
**Service:** <affected service(s)>
**Bridge:** <link>
**Incident channel:** <#channel>

**User impact right now:**
<1-2 sentences on what users are experiencing at this moment>

---

## Current State

**Status:** INVESTIGATING / IDENTIFIED / MITIGATING

**What we can see right now:**
- Error rate: X% (normal: Y%)
- P99 latency: Xms (normal: Yms)
- Pods in bad state: <kubectl output or summary>

**Timeline so far:**
- HH:MM — <event>
- HH:MM — <event>
- HH:MM — <current moment>

---

## What We've Tried

| Action | Result | Notes |
|---|---|---|
| Restarted pod payment-api-xyz | No improvement | Error rate unchanged after 2 min |
| Checked DB connection count | 98% utilized | This is the leading indicator |
| Rolled back to v2.3.9 | In progress | Started 5 min ago, not done yet |

---

## Current Hypothesis

**Most likely root cause:**
<1-2 sentences on what we think is happening>

**Confidence:** High / Medium / Low

**Evidence for this:**
- <observation 1>
- <observation 2>

**Alternative hypotheses not yet ruled out:**
- <alternative 1>

---

## Next Action for Incoming SRE

**Do this first:**
1. <specific action>
2. <specific action>

**Watch for:**
- If <condition>: do <action>
- If <condition>: escalate to <person/role>

**Abort/escalate conditions:**
- Error rate > X% for > Y min → page engineering manager
- Any sign of data loss → page VP Engineering immediately

---

## Do NOT Try These (dead ends)

- <action> — tried at HH:MM, made it worse / had no effect
- <action> — not applicable because <reason>

---

## People Involved

| Name/Role | Status | Contact |
|---|---|---|
| Engineering Manager | Informed | DM on Slack |
| DB Team | Standby | In incident channel |
| Customer Success | Notified | Watching status page |

---

## Outgoing SRE Availability

Available for questions until: HH:MM UTC
Contact via: <Slack / phone>
```

---

#### Format C: Quick Step-Away Brief (< 5 minutes)

For when an engineer needs to step away briefly mid-incident:

```
QUICK BRIEF — <incident name>

Current state: <1 sentence>
Last action taken: <1 sentence>
Next action needed: <1 sentence>
Watch for: <abort condition>
Back in: ~X minutes
Reach me at: <contact>
```

---

### Step 4: Delivery

- Post the handoff document in the team's SRE Slack channel
- For active incident handoffs: post in the incident channel AND do a live verbal/video
  brief if possible (< 5 minutes)
- Tag the incoming SRE explicitly
- Set a "handoff complete" confirmation: incoming SRE acknowledges with ✅

### Step 5: Knowledge Capture Trigger

After every routine handoff, check if `knowledge-capture` should run:
- Were there any incidents this shift? → Run `knowledge-capture` if not already done
- Were there any near-misses or unusual behaviors? → Create a pattern entry

---

## Guidelines

- The handoff document is not optional. Even a "quiet shift" handoff takes 5 minutes
  and prevents the incoming SRE from flying blind.
- "Do NOT try" section is as important as the current hypothesis. Dead ends waste time.
- For active incident handoffs: the incoming SRE should read the document AND get a
  live brief. Written + verbal = full context transfer.
- Persona (junior-sre): always do a live verbal handoff in addition to the written doc.
  Text alone misses nuance that matters during a P0.
- Persona (sre-manager): scan handoffs weekly for patterns — recurring watch items,
  repeat incidents, or open follow-ups that are aging are signals of systemic problems.
