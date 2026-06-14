# SRE AI Agent

> Your company's institutional memory for SRE — grows smarter with every incident.

---

## The Problem

Every SRE team has the same silent crisis. Your most experienced engineer carries years of operational knowledge in their head: which alerts are false positives at 2am, which service misbehaves after a certain deploy, what the fix is and which dead ends to avoid. That knowledge lives nowhere else.

Then they leave. Or go on vacation. Or aren't the one paged at 3am.

The junior SRE who picks up the pager starts from zero — not because they're less capable, but because the knowledge wasn't theirs to keep.

---

## How It Works

```
Alert fires
    │
    ▼
Agent searches knowledge base ──► "Seen this before — here's what worked,
    │                               here's what not to try, ~12 min to resolve"
    │ (first time?)
    ▼
Agent guides troubleshooting
    │
    ▼
Issue resolved
    │
    ▼
knowledge-capture runs (mandatory closing step)
    · Runbook updated: what worked, what failed, dead ends
    · Pattern saved: symptom signature, fastest diagnostic path
    │
    ▼
Next occurrence: any SRE resolves it faster
```

**The flywheel:** every incident makes the agent more useful for the next one. Knowledge compounds. MTTR shrinks. The team stops being dependent on any one person.

---

## Quick Start

### Option A — CLI (recommended)

```bash
pip install git+https://github.com/stevancris/sre-ai-agent.git
sre-agent init
```

Setup wizard asks about your role, cloud provider, observability stack, and team — then scaffolds a pre-configured agent directory in under 2 minutes.

```
sre-agent init          Set up a new SRE agent for your company
sre-agent search        Search the knowledge base by symptom
sre-agent incident      Scaffold a new incident with timeline
sre-agent import-rca    Convert existing RCA documents into knowledge-base patterns
sre-agent validate      Validate all SKILL.md files
```

### Option B — No Python required

```bash
npx skills add stevancris/sre-ai-agent
```

Installs all 20 skills directly into your AI client (Claude, Cursor, Copilot, and more).

### Manual setup

1. Clone or fork this repo
2. Edit [`context/CONTEXT.md`](context/CONTEXT.md) with your role, cloud provider, and stack
3. Run `claude` in the directory — the agent reads `CLAUDE.md` automatically

---

## Already Have RCAs?

If your team has existing incident reports or postmortems, import them directly:

```bash
sre-agent import-rca postmortem-2024-11.md
sre-agent import-rca pagerduty-export.json
sre-agent import-rca incidents/*.md
```

Accepts any format — our postmortem template, PagerDuty JSON, Atlassian, or plain text. Converts to searchable knowledge-base patterns automatically. Day one, the agent already knows your history.

---

## Skills

20 skills covering the full SRE lifecycle:

| Skill | What it does |
|---|---|
| `incident-response` | End-to-end incident management with knowledge base lookup |
| `oncall-runbook` | Walk through remediation steps, search known patterns first |
| `knowledge-capture` | Persist what was learned — mandatory closing step after every incident |
| `import-rca` | Convert existing RCA bank into knowledge-base patterns |
| `postmortem` | Blameless postmortem with five-whys and action items |
| `rca-summary` | Shareable RCA digest for Slack, email, or management |
| `root-cause-analysis` | Five-whys, fishbone, timeline correlation |
| `deployment-safety` | Risk scoring, canary strategy, rollback decision |
| `slo-monitoring` | SLO setup, error budget calculation, burn rate alerts |
| `observability` | Four golden signals, structured logging, alerting design |
| `oncall-handoff` | Structured shift handoff — routine and active incident formats |
| `production-readiness-review` | 8-section checklist before any service goes live |
| `iac-review` | Terraform/K8s review: security, blast radius, cost impact |
| `chaos-engineering` | Blast radius assessment, experiment design, gameday runbooks |
| `capacity-planning` | Traffic forecasting, bottleneck identification, cost projection |
| `cost-optimization` | Cloud cost reduction ranked by impact and safety |
| `security-posture` | IAM review, secrets audit, vulnerability triage, compliance |
| `runbook-generator` | Generate complete runbooks from scratch |
| `rfc` | Draft and iterate on technical proposals and architecture decisions |
| `toil-tracking` | Measure SRE toil load, build automation business cases |

---

## Team Setup

The real power comes when the entire team shares one knowledge base.

1. One person runs `sre-agent init` → creates a configured directory
2. Push that directory to a **new private repo** in your company's Git org — everyone else clones it
3. After every incident, `knowledge-capture` generates a pattern file — open a PR
4. One teammate reviews, merges — everyone pulls, knowledge is synced

```
Incident resolved
  → sre-agent knowledge-capture
  → new pattern file in knowledge-base/patterns/
  → PR → 1 approval → merge → git pull
  → next SRE resolves the same issue in 12 min instead of 47
```

---

## Personas

The agent adapts to your role:

| Role | Behavior |
|---|---|
| `junior-sre` | Step-by-step with explanations, escalation reminders, safety nets |
| `senior-sre` | Concise, trade-offs surfaced, technical depth |
| `sre-manager` | Executive summaries, business risk framing, stakeholder comms |

---

## Inspired By

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — principles behind the skills
- [Agent Skills specification](https://agentskills.io/specification) — SKILL.md structure
- [Google SRE AI blog post](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations) — validation that this direction is right

---

## Contributing

Contributions welcome — especially new skills, stack-specific examples, and anonymized knowledge-base patterns from real incidents.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
