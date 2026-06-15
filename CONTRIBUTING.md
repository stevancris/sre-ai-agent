# Contributing to SRE AI Agent

The more SRE experience encoded into this project, the more useful it becomes for everyone. Every skill, pattern, and real-world example compounds.

---

## What we need most

| Contribution | Why it matters |
|---|---|
| **New skills** | SRE domains not yet covered |
| **Knowledge-base patterns** | Anonymized failure patterns from real incidents — the most valuable contribution |
| **Stack-specific context examples** | GCP, Azure, on-prem alternatives to the default AWS setup |
| **Bug fixes and improvements** | CLI, skill logic, documentation |

**Skill gaps we know about:**
- Database-specific operations (PostgreSQL, MySQL, MongoDB)
- Service mesh (Istio, Linkerd)
- Platform-specific (GCP-native, Azure-native tooling)
- On-call scheduling and rotation management

---

## Getting started

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/sre-ai-agent.git
cd sre-ai-agent

# 2. Install the CLI in editable mode
pip install -e .

# 3. Validate everything works
sre-agent validate
```

---

## Branch naming

```
skill/<skill-name>              # new or updated skill
pattern/<service>-<failure>     # new knowledge-base pattern
fix/<what-you-fixed>            # bug fix
docs/<what-you-updated>         # documentation
chore/<what-you-did>            # cleanup, refactor, tooling
```

---

## How to add a new skill

Each skill lives in `skills/<skill-name>/SKILL.md`:

```markdown
---
name: skill-name
description: >
  What this skill does and when to use it.
  Trigger keywords: keyword1, keyword2, keyword3.
allowed-tools: Read Glob Grep
---

# Skill Name

## Setup Check

Before loading context files, check if `context/CONTEXT.md` exists.
If not — ask: Role, Cloud provider, Observability stack inline.

## Instructions

### Step 1: ...
### Step 2: ...
```

**Checklist before opening a PR:**

- [ ] `description` includes trigger keywords — this is how the agent finds the skill
- [ ] Every step has: what to do, expected output, what to do if it fails
- [ ] Instructions work at 3am without Googling anything
- [ ] Skill notes persona differences (junior / senior / manager output)
- [ ] Added to `AGENTS.md` skills index and `README.md` skills table
- [ ] `sre-agent validate` passes

---

## How to add a knowledge-base pattern

Patterns live in `skills/knowledge-base/patterns/<service>-<failure-mode>.md`.

```yaml
---
service: service-name
failure-mode: short-slug
first-seen: YYYY-MM-DD
times-seen: 1
last-seen: YYYY-MM-DD
avg-mttr-minutes: 0
best-mttr-minutes: 0
related-incidents: []
---
```

**Required sections:**

1. **Symptom Signature** — how to recognize this within 2 minutes
2. **Fastest Diagnostic Path** — concrete commands, total < 5 minutes
3. **Resolution** — what actually works
4. **Dead Ends** — what was tried and failed *(critical — prevents others repeating mistakes)*
5. **Prevention** — what would stop this happening again

**Before contributing a pattern:**

- Remove all company names, internal URLs, team names, and individual names
- Replace with generic placeholders: `<your-db-host>`, `<service-name>`, `<your-org>`
- Tip: use `sre-agent import-rca <your-rca-file>` to auto-generate a draft pattern from an existing RCA document, then anonymize and refine

---

## Pull request process

1. Create a branch from `main` using the naming convention above
2. Make your changes
3. Run `sre-agent validate` — must pass before opening a PR
4. Open a PR with:
   - **What** — what the skill or pattern covers
   - **Why** — why it's not already covered by an existing skill
   - **Context** — which real scenario prompted this

PRs are reviewed within a few days. One approval required to merge.

---

## Guidelines

**Do:**
- Write instructions you would actually follow during an incident at 3am
- Include dead ends — failed approaches are as valuable as successful ones
- Chain skills when relevant (`"after resolution, run knowledge-capture"`)
- Keep skills focused — one domain per skill

**Don't:**
- Include real incident data, customer information, or PII
- Duplicate an existing skill — improve the existing one instead
- Write vague steps (`"investigate the logs"` without specifying what to look for)
- Skip expected output — that's the most important part of any runbook step

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

SRE work is high-stakes and often stressful. Contributions should reflect the blameless culture we try to build in postmortems: focus on systems and processes, not people.
