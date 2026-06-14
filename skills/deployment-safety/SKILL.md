---
name: deployment-safety
description: >
  Ensure safe production deployments using canary, blue-green, and feature flag strategies.
  Use before deploying to production, when planning a release, when a deployment is going
  wrong, or when deciding whether to roll back. Trigger keywords: deploy, deployment, canary,
  rollback, roll back, release, feature flag, blue-green, progressive rollout, production push,
  ship, go live, hotfix, release train, deployment freeze, failed deploy, bad deploy,
  should I deploy, is it safe to deploy.
allowed-tools: Read Glob Grep Bash(git log:*) Bash(git diff:*)
---

# Deployment Safety Skill

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

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md` to determine:
- Deployment tool (ArgoCD, Spinnaker, GitHub Actions, etc.)
- Deployment strategy (canary, blue-green, rolling)
- Feature flag tool (LaunchDarkly, etc.)
- Current SLO status (from `context/CONTEXT.md`)

### Step 2: Determine the Mode
- **Pre-deployment review** — user wants to deploy something
- **Active deployment** — deployment is in progress
- **Rollback decision** — something went wrong post-deploy

---

### Mode: Pre-Deployment Review

#### Risk Classification
Score the change on these dimensions:

| Dimension | Low (0) | Medium (1) | High (2) |
|---|---|---|---|
| Change scope | Config change | New feature | Schema migration |
| Services affected | 1 service | 2–3 services | Core infrastructure |
| Data mutations | None | Read path | Write path |
| Traffic affected | <5% of users | 5–50% | All users |
| Rollback complexity | Instant | Minutes | Hours or impossible |
| Time of day | Off-peak | Business hours | Peak hours |

**Total score:**
- 0–3: Green — standard deploy
- 4–6: Yellow — canary required
- 7+: Red — requires manager approval + canary + feature flag

#### Pre-Deploy Checklist
- [ ] Change has been reviewed and approved
- [ ] Tests pass in CI (unit, integration, e2e)
- [ ] Staging deployment was successful
- [ ] Monitoring dashboards are open and baselines noted
- [ ] Rollback procedure is documented and tested
- [ ] On-call engineer is aware of the deployment
- [ ] Feature flag available to disable the change without a deploy (for high-risk changes)
- [ ] Database migrations are backwards-compatible (no blocking locks, no data loss)
- [ ] Traffic volume is not at peak (for high-risk changes)

#### Recommended Deployment Strategy (by risk score)
- **Green (0–3):** Rolling update, monitor for 15 minutes
- **Yellow (4–6):** Canary — 5% → 25% → 100% with 10-minute bake time per stage
- **Red (7+):** Canary + feature flag — deploy code off, enable flag for 1% → 10% → 100%

#### Rollback Trigger Conditions
Define before every deployment:
```
Rollback immediately if:
- Error rate increases by > <N>% compared to pre-deploy baseline
- P99 latency increases by > <X>ms compared to pre-deploy baseline
- Any new exception type appears in logs
- On-call engineer's gut says something is wrong (trust this)
```

---

### Mode: Active Deployment (monitoring)

During a canary deployment, check these signals at each stage:
1. Error rate: current vs. baseline
2. Latency P99: current vs. baseline
3. Saturation: CPU / memory on new pods vs. old pods
4. Business metrics: conversion rate, order volume (if accessible)

Provide a go/no-go recommendation for each canary stage.

---

### Mode: Rollback Decision

Ask:
1. What metric or error triggered the concern?
2. How many users are affected?
3. Is the issue getting worse or stable?

**Roll back immediately (no debate) if:**
- Error rate is increasing and not stabilizing
- Data corruption is suspected
- The on-call engineer cannot confidently diagnose the cause within 10 minutes

**Consider waiting (with close monitoring) if:**
- Error rate is elevated but stable and small subset of users
- Root cause is known and a forward fix is possible in < 30 minutes

#### Rollback Command (output for manual execution)
For ArgoCD:
```bash
# Roll back to previous revision — run this yourself:
argocd app rollback <app-name> <revision-number>
```

For kubectl:
```bash
# Roll back to previous deployment — run this yourself:
kubectl rollout undo deployment/<name> -n <namespace>

# Verify rollback:
kubectl rollout status deployment/<name> -n <namespace>
```

---

## Guidelines

- If error budget is at <10%: no non-critical deployments until budget recovers.
- Hotfixes bypass risk scoring but still require the pre-deploy checklist.
- Never deploy during a P0 or P1 incident unless the deploy is the rollback.
- Persona (junior-sre): always require a second person to verify rollback trigger conditions
  before initiating a rollback.
- Persona (sre-manager): include a go/no-go sign-off section for high-risk deploys.
