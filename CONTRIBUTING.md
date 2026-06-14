# Contributing to SRE AI Agent

Thank you for wanting to contribute. This project grows in value as more SRE experience
is encoded into it — every skill, pattern, and example makes it more useful for the
entire community.

---

## What We Need Most

### 1. New Skills
SRE domains not yet covered:
- Database-specific skills (PostgreSQL, MySQL, MongoDB operational patterns)
- Platform-specific skills (GCP-specific, Azure-specific tooling)
- Service mesh operations (Istio, Linkerd)
- On-call scheduling and rotation management
- SRE interviewing and hiring
- Incident communication for specific industries (fintech, healthcare, etc.)

### 2. Stack-Specific Context Examples
Alternatives to the default AWS + Datadog + ArgoCD setup:
- `context/company/tech-stack-gcp.md`
- `context/company/tech-stack-azure.md`
- `context/company/tech-stack-onprem.md`

### 3. Knowledge Base Patterns
Anonymized failure patterns from real incidents. These are the most valuable
contributions — they encode operational knowledge that usually lives only in
an engineer's head.

### 4. Onboarding Examples
Real-world examples of how teams have set up their company context — sanitized `tech-stack.md`, `oncall-schedule.md`, and knowledge-base patterns that help new adopters get started faster.

---

## How to Add a New Skill

### Skill File Structure

Each skill lives in `skills/<skill-name>/SKILL.md` with this format:

```markdown
---
name: skill-name
description: >
  What this skill does and when to use it. Include trigger keywords —
  the agent matches user messages to skill descriptions using these.
  Trigger keywords: keyword1, keyword2, keyword3.
allowed-tools: Read Glob Grep
---

# Skill Name

## Instructions

### Step 1: ...
### Step 2: ...

## Examples

## Guidelines
```

### Requirements for a good skill

- **description** must include trigger keywords — this is how the agent finds the skill
- **Instructions** must be executable — not vague ("investigate the issue") but specific
  ("run `kubectl logs -l app=<service> --since=15m | grep ERROR`")
- Each step must include: what to do, expected output, and what to do if it fails
- Include at least one concrete **example** showing the skill in action
- **Guidelines** section covers edge cases and persona-specific behavior

### Persona adaptation

Every skill should note how output differs by persona:
- `junior-sre` — more verbose, step-by-step, escalation reminders
- `senior-sre` — concise, assumes expertise, surfaces trade-offs
- `sre-manager` — business impact framing, stakeholder communication drafts

---

## How to Add a Knowledge Base Pattern

Patterns live in `skills/knowledge-base/patterns/<service>-<failure-mode>.md`.

Use this frontmatter:

```yaml
---
service: service-name
failure-mode: short-description
first-seen: YYYY-MM-DD
times-seen: N
last-seen: YYYY-MM-DD
avg-mttr-minutes: N
best-mttr-minutes: N
related-incidents: [inc-YYYY-MM-DD]
---
```

Required sections:
1. **Symptom Signature** — how to recognize this within 2 minutes
2. **Fastest Diagnostic Path** — concrete commands, < 5 minutes total
3. **Resolution** — what actually works
4. **Dead Ends** — what was tried and failed (critical — prevents others repeating mistakes)
5. **Early Warning Signals** — proposed alerts to catch this earlier

**Anonymization:** Remove company names, internal URLs, team names, and individual names
before contributing. Replace with generic placeholders like `<your-db-host>` or
`<service-name>`.

After adding a pattern, update `skills/knowledge-base/INDEX.md` with a new row.

---

## Contribution Guidelines

### Do

- Keep skills focused — one skill per domain, not one skill per everything
- Write instructions you would actually follow during an incident at 3am
- Include "dead ends" — failed approaches are as valuable as successful ones
- Test your skill by reading it out loud as if you were explaining it to a junior SRE
- Reference other skills when they should be chained (e.g., "invoke `knowledge-capture` when done")

### Do Not

- Add skills that require company-specific internal tools without making them configurable
- Include real incident data, customer information, or PII
- Add skills that duplicate existing ones — improve the existing skill instead
- Create skills with vague steps ("investigate the logs" without specifying what to look for)
- Add runbooks that skip the "expected output" — that is the most important part

---

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b skill/your-skill-name` or `git checkout -b pattern/service-failure-mode`
3. Add your skill or pattern
4. Update the relevant index file:
   - New skill → add to `AGENTS.md` skills index and `README.md` skills table
   - New pattern → add to `skills/knowledge-base/INDEX.md`
5. Open a pull request with:
   - What the skill/pattern covers
   - Why it is not already covered by an existing skill
   - Which SRE scenario prompted this (real incident, common question, gap you noticed)

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

SRE work is high-stakes and often stressful. Contributions should reflect the blameless
culture we try to build in our postmortems: focus on systems and processes, not people.
