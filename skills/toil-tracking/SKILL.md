---
name: toil-tracking
description: >
  Track, measure, and systematically reduce toil — the repetitive, manual, automatable
  work that consumes SRE capacity without improving reliability. Use when reviewing how
  the team spends its time, identifying what to automate next, making the case for
  engineering investment in reliability tooling, or building a quarterly toil reduction
  plan. This skill feeds the Improve phase of the SDLC loop. Trigger keywords: toil,
  toil reduction, repetitive work, manual work, what should we automate, automation
  opportunity, SRE capacity, team bandwidth, where is time going, engineering investment,
  reliability backlog, reduce manual work, alert fatigue, too many pages, too many tickets,
  keep doing the same thing, recurring work.
allowed-tools: Read Glob Grep
---

# Toil Tracking Skill

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

## What Is Toil

Toil is work that is:
- **Manual** — requires a human to do it, even if it could be automated
- **Repetitive** — same task over and over, not building anything new
- **Automatable** — a machine could do it with sufficient engineering investment
- **Reactive** — triggered by an external event, not proactively planned
- **No enduring value** — doing it doesn't leave the system permanently better

Toil is not bad work — it is necessary. The problem is when toil consumes so much capacity
that the team cannot invest in the reliability improvements that would reduce future toil.

Google's SRE book recommends: **toil should be < 50% of each SRE's time.** Above 50%,
the team is in a toil trap — too busy fighting fires to prevent them.

---

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md`. Load oncall schedule
from `context/company/oncall-schedule.md`.

### Step 2: Identify the Mode

- **Audit** — measure current toil load across the team
- **Prioritize** — rank toil items by impact to decide what to automate first
- **Business case** — build the case for engineering investment to reduce toil
- **Quarterly review** — review progress against toil reduction goals

---

### Mode: Audit — Measure Current Toil

#### Step 2a: Toil Inventory

Ask the user to walk through these categories and estimate hours per week per SRE:

**Category 1: Incident and Alert Toil**
- Hours spent on pages that could be auto-remediated
- Hours spent on alerts that are false positives
- Hours spent on P2/P3 incidents that are recurring (same issue, same fix)
- Hours spent writing the same Slack update messages during incidents

**Category 2: Operational Toil**
- Hours spent on manual deployment steps that should be automated
- Hours spent on routine cert renewals, key rotations, access reviews
- Hours spent on manual scaling operations
- Hours spent on "ticket hygiene" — moving, updating, closing tickets manually

**Category 3: Reactive Toil**
- Hours spent responding to ad-hoc requests from developers
- Hours spent on "can you check X" requests
- Hours spent re-explaining the same thing repeatedly (→ should be documentation)

**Category 4: Maintenance Toil**
- Hours spent keeping tools, scripts, and dashboards from breaking
- Hours spent on dependency upgrades with no reliability benefit
- Hours spent on manual report generation

#### Step 2b: Toil Load Calculation

```
Toil audit results:

Category               | Hours/week/SRE | % of 40h week
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Incident / alert toil  |       X        |      X%
Operational toil       |       X        |      X%
Reactive toil          |       X        |      X%
Maintenance toil       |       X        |      X%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL toil             |       X        |      X%
Project / engineering  |       X        |      X%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: 🟢 < 33% | 🟡 33–50% | 🔴 > 50%
```

If total toil > 50%: flag immediately with recommendation to pause new feature work
and invest in toil reduction.

---

### Mode: Prioritize — What to Automate First

#### Toil Scoring Matrix

For each toil item, score on three dimensions (1–5):

| Dimension | 1 (low) | 5 (high) |
|---|---|---|
| **Frequency** | Rare (monthly) | Daily or continuous |
| **Time cost** | < 15 minutes | > 2 hours |
| **Automation feasibility** | Hard / risky | Easy / low risk |

**Priority score = Frequency × Time cost × Automation feasibility**

Generate a ranked toil reduction backlog:

```
Toil Reduction Backlog — Ranked by Priority Score

Rank 1: Auto-remediate pod OOMKill restarts
  Score: 5 × 4 × 5 = 100
  Current cost: ~3 pages/week × 20 min/page = 1h/week per SRE
  Automation: kubectl rollout restart on OOMKill event → VPA recommendation
  Estimated effort: 2 engineer-weeks
  Annual savings: ~52h per SRE × team size

Rank 2: Automate certificate renewal for internal services
  Score: 3 × 3 × 5 = 45
  Current cost: 2h/month manual process, high error-rate
  Automation: cert-manager with auto-renewal
  Estimated effort: 1 engineer-week
  Annual savings: ~24h per SRE

Rank 3: Dashboard for weekly capacity report (currently manual)
  Score: 4 × 2 × 4 = 32
  Current cost: 2h/week manual data gathering and formatting
  Automation: Datadog scheduled report + Slack bot
  Estimated effort: 3 engineer-days
  Annual savings: ~104h per SRE
```

#### Automation Decision Framework

Before investing in automation, validate:
1. **Is this toil recurring?** If it happened once, document it — don't automate it.
2. **Is the toil stable?** If the underlying system is changing, automation will break.
3. **Is the automation safe?** Auto-remediation can hide real problems — ensure it logs
   every action and has an emergency kill switch.
4. **Does eliminating this toil free capacity for higher-value work?**

---

### Mode: Business Case

Build a cost-of-toil argument for engineering investment:

```
Toil Reduction Business Case

Current state:
  Team size: N SREs
  Average SRE fully-loaded cost: $X/year (salary + benefits + overhead)
  Current toil load: X% of time = X hours/week per SRE

Annual cost of current toil:
  X hours/week × 52 weeks × N SREs × (hourly rate) = $X/year

Top toil reduction opportunities:

1. <Automation A>
   Investment: X engineer-weeks = $X
   Annual savings: X hours × $rate = $X/year
   Payback period: X months
   ROI (3-year): X%

2. <Automation B>
   Investment: X engineer-weeks = $X
   Annual savings: $X/year
   Payback period: X months

Total investment required: $X (X engineer-weeks)
Total annual savings: $X/year
Total 3-year ROI: X%

Non-financial benefits:
  - Reduce on-call burden → improve retention
  - Free X engineer-weeks/quarter for reliability projects
  - Reduce incident MTTR by ~X% (less manual intervention required)
```

---

### Mode: Quarterly Review

At the end of each quarter, review progress:

```
Toil Reduction Review — Q<N> YYYY

Target: reduce toil from X% to Y% of SRE time

━━━ Completed this quarter ━━━
✅ Auto-remediation for pod OOMKill — saves 1h/week/SRE
✅ cert-manager deployed — saves 2h/month/SRE
✅ Automated capacity report — saves 2h/week/SRE

Total saved: X hours/week across team

━━━ In progress ━━━
🔄 Alert deduplication — 60% complete, targeting next month

━━━ Not started (deprioritized) ━━━
⏸ Dashboard auto-generation — deprioritized due to incident load

━━━ New toil identified this quarter ━━━
⚠️ Manual Slack notification for deploy status — added to backlog

━━━ Current toil load ━━━
Before: X% | After: Y% | Target: Z%
Status: 🟢 On track / 🟡 Slipping / 🔴 Toil trap

━━━ Next quarter targets ━━━
1. Complete alert deduplication — owner: SRE team
2. Automate deploy status notifications — owner: platform team
3. Target toil load: <Z%
```

---

### Toil vs. Engineering Work Balance

Track and protect the ratio each sprint:

```
Sprint X toil balance:
  Toil work:        X points (X%)
  Engineering work: X points (X%)
  
  🟢 Healthy: toil < 33% of sprint capacity
  🟡 Warning: toil 33–50%
  🔴 Toil trap: toil > 50% — pause new features, address toil first
```

---

## Connection to the SDLC Improve Loop

Toil tracking is the **measurement layer** of the Improve phase. Without it, the improve
loop runs blind:

```
Operate (incidents, alerts, deploys)
   ↓ generates
Toil (manual work, repetition)
   ↓ measured by
Toil tracking → backlog of automation opportunities
   ↓ feeds
RFC skill → propose the automation
   ↓ implemented → reduces toil in Operate
   ↓ measured again → loop closes
```

Connect toil items directly to RFCs: every Rank 1 toil item should have a corresponding
RFC for the automation solution.

---

## Guidelines

- Toil that is < 10% of time is normal overhead — do not over-engineer its elimination.
- Alert fatigue is a form of toil: too many alerts = SREs ignore alerts = missed incidents.
  Alert count per SRE per week is a key metric to track.
- Toil tracking data should go into the quarterly SRE report to management.
- Persona (sre-manager): use toil audit data to justify headcount, tooling budget, or
  platform team investment. A clear "we spend $X/year on manual work that $Y investment
  would eliminate" is the most effective engineering ask.
- Persona (junior-sre): if > 50% of your time is toil, raise this with your manager.
  That is not sustainable and is a signal the team needs investment.
