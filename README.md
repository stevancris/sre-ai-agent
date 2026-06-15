<div align="center">

# SRE AI Agent

**Your company's institutional memory for SRE.**  
Grows smarter with every incident. Available at 3am. Never leaves.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Skills](https://img.shields.io/badge/Skills-20-green)](#skills)
[![npx](https://img.shields.io/badge/npx-skills%20add-black)](https://agentskills.io)

</div>

---

## The problem no one talks about

Your best SRE carries years of knowledge in their head.

Which alerts are false positives at 2am. Which service breaks after a specific deploy pattern. What the actual fix is — and which dead ends to avoid. That knowledge exists nowhere else.

Then they leave. Or go on vacation. Or aren't the one who gets paged.

The junior SRE who picks up the pager **starts from zero**. They re-learn what the senior already knew. They try the same dead ends. MTTR is 4× longer — not because they're less capable, but because the knowledge wasn't theirs to keep.

---

## What changes with SRE AI Agent

```
Without it                          With it
──────────────────────────────────  ──────────────────────────────────
Alert fires at 3am                  Alert fires at 3am
  ↓                                   ↓
Junior SRE starts from zero         Agent searches knowledge base
  ↓                                   ↓
Tries restarting pods               "Seen this 3 times. Don't restart pods.
  ↓                                    Go straight to connection pool.
Doesn't help                           ~12 min to resolve."
  ↓                                   ↓
Tries scaling replicas              Junior SRE follows the path
  ↓                                   ↓
Makes it worse                      Resolved in 12 min
  ↓
47 min later, finally resolved

First time: 47 min                  First time: guided
Second time: 40 min                 Second time: 12 min
Third time: still 35 min            Third time: any SRE, same result
```

**The flywheel:** every resolved incident gets captured. Next time it fires — any SRE on your team resolves it faster. Knowledge compounds. MTTR shrinks. The team stops depending on any one person.

---

## How it works

```
Alert fires
    │
    ▼
Agent searches knowledge base ──► known pattern found?
    │                               → fastest path, dead ends to skip, ETA
    │ first time? no match
    ▼
Agent guides troubleshooting
    · severity classification
    · step-by-step remediation
    · stakeholder communication drafts
    │
    ▼
Resolved
    │
    ▼
knowledge-capture runs (mandatory closing step)
    · what worked, what didn't, dead ends
    · pattern saved → searchable next time
    · early warning gaps identified
    │
    ▼
Next occurrence: any SRE, faster resolution
```

---

## Quick Start

### Option A — CLI

```bash
pip install git+https://github.com/stevancris/sre-ai-agent.git
sre-agent init
```

5-step wizard. Asks your role, cloud provider, observability stack, team size, Slack channels. Done in under 2 minutes.

```
sre-agent init          Set up a new SRE agent for your company
sre-agent search        Search the knowledge base by symptom keyword
sre-agent incident      Scaffold a new incident with timeline and checklist
sre-agent import-rca    Convert existing RCA documents into knowledge-base patterns
sre-agent validate      Validate all SKILL.md files
```

### Option B — No Python required

```bash
npx skills add stevancris/sre-ai-agent
```

Installs all 20 skills into your AI client — Claude, Cursor, Copilot, and [71 more](https://agentskills.io).

### Option C — Manual

1. Clone this repo
2. Edit [`context/CONTEXT.md`](context/CONTEXT.md) with your role, stack, and team
3. Run `claude` — the agent reads `CLAUDE.md` automatically

---

## Already have old RCAs sitting in Confluence?

Don't wait for new incidents to build your knowledge base. Import what you already have:

```bash
sre-agent import-rca postmortem-2024-11.md
sre-agent import-rca pagerduty-export.json
sre-agent import-rca incidents/*.md
```

Accepts our postmortem format, PagerDuty JSON, Atlassian exports, or plain text.  
Day one, the agent already knows your history.

---

## Skills

20 skills covering the full SRE lifecycle:

| Skill | What it does |
|---|---|
| `incident-response` | End-to-end incident management with knowledge base lookup |
| `oncall-runbook` | Walk through remediation, search known patterns first |
| `knowledge-capture` | Persist what was learned — mandatory after every incident |
| `import-rca` | Convert existing RCA bank into searchable patterns |
| `postmortem` | Blameless postmortem with five-whys and action items |
| `rca-summary` | Shareable digest for Slack, email, or management |
| `root-cause-analysis` | Five-whys, fishbone, timeline correlation |
| `deployment-safety` | Risk scoring, canary strategy, rollback decision |
| `slo-monitoring` | SLO setup, error budget, burn rate alerts |
| `observability` | Four golden signals, structured logging, alerting design |
| `oncall-handoff` | Structured shift handoff — routine and active incident formats |
| `production-readiness-review` | 8-section checklist before any service goes live |
| `iac-review` | Terraform/K8s review: security, blast radius, cost impact |
| `chaos-engineering` | Blast radius assessment, experiment design, gameday runbooks |
| `capacity-planning` | Traffic forecasting, bottleneck identification, cost projection |
| `cost-optimization` | Cloud cost reduction ranked by impact and safety |
| `security-posture` | IAM review, secrets audit, vulnerability triage, compliance |
| `runbook-generator` | Generate complete runbooks from scratch |
| `rfc` | Draft and iterate on technical proposals |
| `toil-tracking` | Measure SRE toil load, build automation business cases |

---

## The agent adapts to your role

| Role | Behavior |
|---|---|
| `junior-sre` | Step-by-step with explanations, escalation reminders, safety nets |
| `senior-sre` | Concise, trade-offs surfaced, no hand-holding |
| `sre-manager` | Executive summaries, business risk framing, stakeholder comms |

---

## Team setup

The real power comes when the whole team shares one knowledge base. Every incident one SRE resolves makes the next one faster for everyone.

1. One person runs `sre-agent init` → get a configured directory
2. Push to a **new private repo** in your company's Git org
3. Everyone clones it — context is shared from day one
4. After every incident: `knowledge-capture` generates a pattern file → open a PR → 1 approval → merge → `git pull`

```
Month 1   →  3–5 patterns   →  known issues resolved 2–3× faster
Month 3   →  10–15 patterns →  junior SREs handle P2s independently
Month 6   →  25+ patterns   →  MTTR down, alert fatigue reduced
Year 1    →  deep history   →  new hires productive in days, not months
```

---

## Inspired by

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — principles behind the skills
- [Agent Skills specification](https://agentskills.io/specification) — SKILL.md structure
- [Google SRE AI blog post](https://cloud.google.com/blog/products/devops-sre/how-google-sre-is-using-agentic-ai-to-improve-operations) — validation that this direction matters

---

## Contributing

Contributions welcome — new skills, stack-specific examples, anonymized knowledge-base patterns from real incidents.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE).
