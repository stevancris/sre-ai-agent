# Incident Communication Templates

Pre-written templates for common incident communication scenarios.
Adapt to your company's voice and channel structure.

---

## 1. Incident Opening — Slack / Teams

```
🚨 INCIDENT [P<N>] — <short description>

Status: INVESTIGATING
Impact: <what users or features are affected>
Started: ~HH:MM UTC (approximately X minutes ago)
IC (Incident Commander): @<primary-oncall>

Bridge: <zoom/meet link>
Slack thread: Reply here for updates. DM @<IC> for urgent items.

Next update: in 15 minutes or on status change.
```

---

## 2. Status Update — Every 15 Minutes During P0/P1

```
🔄 Update [N] — HH:MM UTC

Status: INVESTIGATING / IDENTIFIED / MITIGATING
Impact: <current scope — is it better, worse, or the same?>
What we know: <1-3 sentences on current understanding>
What we're doing: <current action>
ETA: <estimated resolution time, or "unknown">

Next update: HH:MM UTC
```

---

## 3. Root Cause Identified Update

```
✅ Root Cause Identified — HH:MM UTC

Root cause: <brief, plain-language description>
Fix in progress: <what is being done now>
ETA to resolution: <time>
Impact so far: <users/features affected, duration>

Next update: HH:MM UTC or when resolved.
```

---

## 4. Incident Resolved

```
✅ RESOLVED — HH:MM UTC | Total duration: X hours Y minutes

Incident: <name>
What happened: <2-3 sentence summary>
Root cause: <brief>
Resolution: <what fixed it>
Impact: ~<N> users affected for <duration>

Postmortem: in progress — will be shared within 5 business days.
Monitoring: watching for any recurrence.

Thank you to everyone who helped resolve this.
```

---

## 5. Status Page Update (external — customers see this)

**Investigating:**
```
We are investigating an issue affecting [feature/service]. Some users may experience
[specific symptom, e.g., "errors when checking out" or "slow loading times"].
We will provide an update within 30 minutes.
```

**Identified:**
```
We have identified the cause of the issue affecting [feature/service] and are working on a fix.
Affected users may experience [symptom]. We expect to resolve this by approximately [time].
```

**Monitoring:**
```
A fix has been applied and we are monitoring the results. The issue affecting [feature/service]
appears to be resolved. We will update this status once we have confirmed resolution.
```

**Resolved:**
```
This incident has been resolved. [Feature/service] is now operating normally.
We apologize for the inconvenience. A full postmortem will be published within 5 business days.
```

---

## 6. Escalation Message to Engineering Manager

```
Hi <Manager>, heads up on an active incident:

Incident: <name> [P<N>]
Started: HH:MM UTC (~X minutes ago)
Impact: <user impact summary>
Current status: <investigating / identified / mitigating>
IC: <name>
Bridge: <link>

Do you need to be on the bridge? <Yes — need your decision on X / No — just keeping you informed>
```

---

## 7. Customer-Facing Email (for P0 with extended duration)

```
Subject: [Action Required / Service Update]: <brief description>

Hi <Customer Name>,

We want to let you know that on <date>, between <start time> and <end time> UTC, you may
have experienced <specific impact — e.g., "errors when placing orders" or "inability to log in">.

We have resolved the issue and your service is now fully operational.

What happened: <plain-language, non-technical 2-3 sentences>

What we're doing to prevent recurrence: <top 1-2 action items>

We sincerely apologize for the disruption. If you have any questions or believe you were
affected in a way not described above, please contact <support email>.

<Signature>
```
