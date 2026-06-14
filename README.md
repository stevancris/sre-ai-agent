# SRE AI Agent

> An AI agent that grows smarter with every incident — so expertise is never locked in one person's head.

---

## The Problem

Every SRE team has the same silent crisis.

Your most experienced engineer carries years of operational knowledge in their head: which alerts are false positives at 2am, which service misbehaves after a certain deploy pattern, what the database does under load, which fix works and which wastes 40 minutes. That knowledge lives nowhere else.

Then they leave. Or go on vacation. Or are simply not the one who gets paged at 3am.

The junior SRE who picks up the pager starts from zero. They re-learn what the senior already knew. They try the same dead ends. The MTTR is 4x longer — not because they're less capable, but because the knowledge wasn't theirs to keep.

This is not a people problem. It is a **systems problem**. And it has a systems solution.

---

## What This Is

**SRE AI Agent** is your company's institutional memory — built on the [Agent Skills specification](https://agentskills.io/specification) and designed to run with [Claude Code](https://claude.ai/code).

Think of it as a briefing document for AI. Before a new employee starts, you brief them: what stack you use, how incidents are handled, what's failed before. SRE AI Agent is that briefing — but for an AI that never forgets, never goes on vacation, and is available at 3am.

Any team can get started in minutes — either by forking this repo or using the `sre-agent` CLI (coming soon) — and immediately have an AI that understands how *their* systems work. Not generic SRE advice, but knowledge built from their own incidents, their own stack, their own team.

**The more incidents it sees, the smarter it gets.** Every resolved incident feeds the knowledge base. MTTR shrinks. Junior SREs handle incidents that used to require a senior. New hires are productive in days, not months.

### Why not just use incident.io or PagerDuty?

Those are great tools — but they're SaaS. Your incident data lives on their servers, not yours. SRE AI Agent is local-first: the knowledge base is a folder in your repo, version-controlled, auditable, and never leaves your infrastructure.

---

## How It Works

```
Alert fires at 3am
        │
        ▼
Agent searches knowledge base ──► "Seen this before — here's what worked,
        │                          here's what not to try, ~12 min to resolve"
        │ (first time? no match)
        ▼
Agent guides troubleshooting
  · Severity classification
  · Step-by-step remediation
  · Real-time timeline tracking
  · Stakeholder communication drafts
        │
        ▼
Issue resolved
        │
        ▼
knowledge-capture runs (mandatory closing step)
  · Runbook updated: what worked, what failed, dead ends
  · Pattern saved: symptom signature, fastest diagnostic path
  · Early warning gaps identified: "add alert at 70% threshold"
        │
        ▼
Next occurrence: any SRE resolves it in 12 min instead of 47
```

**The flywheel:** every incident makes the agent more useful for the next one. Knowledge compounds. MTTR shrinks. Toil reduces. The team stops being dependent on any one person.

---

## Live Example

Here's what a session looks like after the agent has accumulated context from a few months of incidents:

```
SRE: "Payment API is throwing 503s. PagerDuty just fired."

Agent: ⚡ Known pattern detected: payment-api — connection pool exhaustion
       Last seen: 2024-11-02 | Resolved in: ~12 min | Seen 3 times

       Fastest path (skip what doesn't work):
         1. Check connection count first — not pod health
            kubectl exec <db-pod> -- psql -c "SELECT count(*) FROM pg_stat_activity;"
            If > 90 connections: this is it.
         2. Identify which service is leaking
            kubectl logs -l app=payment-api --since=10m | grep "connection"
         3. Scale payment-api DOWN by 20% to shed load while diagnosing
            (not up — more pods = more connections = faster exhaustion)

       Do NOT try:
         → Restarting pods: no effect, tried 2024-09-14
         → Scaling up replicas: makes it worse, tried 2024-11-02

       Opening incident channel: #inc-2024-12-01-payment-api-503
       Drafting P1 stakeholder message...
```

Compare that to a cold-start with no context: 47 minutes of trial and error, half of which are dead ends the team already learned the hard way.

---

## Skills

19 skills covering the full SRE SDLC:

```
DESIGN         DEPLOY            OPERATE              IMPROVE
──────────     ──────────────    ─────────────────    ──────────────────
PRR            deployment-       incident-response    knowledge-capture ◄─┐
RFC            safety            oncall-runbook       postmortem          │
slo-           iac-review        oncall-handoff       rca-summary         │
monitoring                       slo-monitoring       root-cause-         │
observability                                         analysis            │
                                                      toil-tracking       │
                                                                          │
                    knowledge-base/patterns/ ◄────────────────────────────┘
                    (grows with every incident)
```

| Skill | What it does |
|---|---|
| `production-readiness-review` | 8-section checklist before any service goes live |
| `incident-response` | End-to-end incident management with knowledge base lookup |
| `oncall-runbook` | Walk through remediation steps, search known patterns first |
| `oncall-handoff` | Structured shift handoff — routine and active incident formats |
| `postmortem` | Blameless postmortem with five-whys and SMART action items |
| `rca-summary` | Shareable RCA digest: Slack, executive email, or knowledge base |
| `knowledge-capture` | Persist what was learned so the next SRE starts ahead |
| `slo-monitoring` | SLO setup, error budget calculation, burn rate alerts |
| `deployment-safety` | Risk scoring, canary strategy, rollback decision |
| `observability` | Four golden signals, structured logging, alerting design |
| `root-cause-analysis` | Five-whys, fishbone, timeline correlation |
| `capacity-planning` | Traffic forecasting, bottleneck identification, cost projection |
| `chaos-engineering` | Blast radius assessment, experiment design, gameday runbooks |
| `iac-review` | Terraform/K8s review: security, blast radius, cost impact |
| `cost-optimization` | Cloud cost reduction ranked by impact and safety |
| `security-posture` | IAM review, secrets audit, vulnerability triage, compliance |
| `runbook-generator` | Generate complete runbooks from scratch |
| `rfc` | Draft and iterate on technical proposals and architecture decisions |
| `toil-tracking` | Measure SRE toil load, build automation business cases |

---

## Personas

The agent adapts its output based on your role:

| Role | Behavior |
|---|---|
| `junior-sre` | Step-by-step with explanations, escalation reminders, safety nets |
| `senior-sre` | Concise, trade-offs surfaced, technical depth, no hand-holding |
| `sre-manager` | Executive summaries, business risk framing, stakeholder comms |

---

## Quick Start

**1. Prerequisites**

- [Claude Code](https://claude.ai/code) installed
- A terminal open in this directory

**2. Fill in your context** — edit [`context/CONTEXT.md`](context/CONTEXT.md):

```yaml
role: senior-sre          # junior-sre | senior-sre | sre-manager
cloud_provider: aws       # aws | gcp | azure | on-prem | hybrid
observability_stack: datadog
deployment_tool: argocd
```

**3. Customize your company context:**

| File | What to fill in |
|---|---|
| [`context/company/tech-stack.md`](context/company/tech-stack.md) | Your actual tools and platforms |
| [`context/company/incident-severity.md`](context/company/incident-severity.md) | Your P-level definitions |
| [`context/company/oncall-schedule.md`](context/company/oncall-schedule.md) | Your team and rotation |

**4. Start Claude Code in this directory:**

```bash
claude
```

That's it. The agent reads `CLAUDE.md` automatically and loads your context.

> **New to Claude Code?** It's a terminal-based AI coding assistant from Anthropic. Install it with `npm install -g @anthropic-ai/claude-code`, then run `claude` in any project directory. [Get started here](https://claude.ai/code).

**5. Try it:**

```
"Alert just fired — payment-api is returning 503s"
"Write up the postmortem for yesterday's incident"
"Is this Terraform plan safe to apply?"
"My team spends half our time on manual work — help me measure it"
```

---

## Team Setup — Shared Knowledge Base

The real power of SRE AI Agent comes when the entire team shares one knowledge base. Every incident one SRE resolves makes it faster for everyone else to resolve the next one.

### How It Works

```
Incident resolved
  → SRE runs knowledge-capture
  → agent generates a new pattern file in knowledge-base/patterns/
  → SRE opens a PR to the shared private repo
  → one teammate reviews and approves
  → merge → everyone pulls → knowledge is synced across the team
```

### Setup Steps

**1. Create a private repo for your team**

Fork this repo into a private repository inside your company's Git organization. This is where your team's knowledge will live — keep it private.

**2. Each SRE clones the shared repo**

```bash
git clone git@github.com:<your-org>/sre-ai-agent.git
cd sre-ai-agent
```

**3. Fill in company context once — together**

One person fills in the context files, commits, and pushes. Everyone else pulls.

```bash
# After filling in context/CONTEXT.md and context/company/*
git add context/
git commit -m "feat: add company context"
git push
```

**4. After every incident — open a PR**

When `knowledge-capture` generates a new pattern file:

```bash
git checkout -b knowledge/payment-api-timeout
git add skills/knowledge-base/patterns/
git commit -m "knowledge: payment-api connection timeout pattern"
git push origin knowledge/payment-api-timeout
# Open PR → 1 approval → merge
```

**5. Everyone pulls after merge**

```bash
git pull
```

That's it. The knowledge base grows with every incident, and every SRE always has the latest patterns.

### Recommended Branch Convention

```
knowledge/<service>-<symptom>    # new incident pattern
context/<what-changed>           # updates to company context
skill/<skill-name>               # new or updated skill
```

### Why PR-based?

A quick PR review before merging a pattern means a second SRE reads what happened. This doubles the learning, catches misdiagnoses, and keeps the knowledge base accurate. With low incident frequency, the overhead is minimal.

---

## The Knowledge Loop in Practice

The knowledge base starts empty. That's intentional — it fills with *your* incidents, not generic examples.

Here's what the growth looks like:

| Time | Knowledge base state | Impact |
|---|---|---|
| Day 1 | Empty | Agent provides structured guidance, no shortcuts |
| Month 1 | 3–5 patterns from real incidents | Known issues resolved 2–3x faster |
| Month 3 | 10–15 patterns, runbooks updated | Junior SREs handle P2s independently |
| Month 6 | 25+ patterns, false positives documented | MTTR down significantly, alert fatigue reduced |
| Year 1 | Deep company-specific knowledge | New SREs onboard in days, not months |

After every incident, the `knowledge-capture` skill runs as a mandatory closing step, ensuring nothing is lost.

---

## Stack Variants

The default context assumes AWS + Kubernetes + Datadog + ArgoCD. The agent adapts to your stack — edit `context/company/tech-stack.md` with your actual tools.

Tested configurations:
- AWS + EKS + Datadog + ArgoCD (default)
- GCP + GKE + Prometheus/Grafana + Cloud Deploy
- Azure + AKS + Azure Monitor + GitHub Actions
- On-prem + bare Kubernetes + Prometheus/Grafana + Jenkins

---

## Inspired By

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — principles behind the skills
- [getsentry/sentry-skills](https://github.com/getsentry/sentry-skills) — Agent Skills format
- [Agent Skills specification](https://agentskills.io/specification) — SKILL.md structure
- [Google SRE AI blog post](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations) — validation that this direction is right

---

## Contributing

Contributions welcome — especially:
- New skills for SRE domains not yet covered
- Stack-specific examples (GCP, Azure, on-prem)
- Example knowledge-base patterns from anonymized real incidents

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
