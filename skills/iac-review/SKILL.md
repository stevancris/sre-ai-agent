---
name: iac-review
description: >
  Review Infrastructure as Code changes for correctness, security, and operational safety.
  Use when reviewing Terraform, Pulumi, CloudFormation, Kubernetes manifests, Helm charts,
  or Ansible playbooks before applying them. Covers security misconfiguration, resource
  drift, cost impact, and blast radius. Trigger keywords: Terraform, IaC, infrastructure
  as code, Kubernetes manifest, Helm chart, CloudFormation, Pulumi, Ansible, tf plan,
  terraform plan, k8s yaml, review infra, apply this, should I apply, is this safe,
  infra change, eks, rds, s3, iam role, security group.
allowed-tools: Read Glob Grep Bash(terraform validate:*) Bash(terraform fmt:*)
---

# IaC Review Skill

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
Read `context/company/tech-stack.md` to identify the IaC tool and cloud provider.

### Step 2: Identify the Change
Ask the user to share:
- The IaC tool and file(s) being changed
- The `terraform plan` output (or equivalent) if available
- The intent of the change

Parse and classify all resource changes:
- **Create** — new resources (verify they are necessary and correctly configured)
- **Modify** — changes to existing resources (check for drift and unintended side effects)
- **Destroy** — resource deletions (require explicit confirmation and assess data loss risk)

### Step 3: Blast Radius Assessment
For any destroy or replace operations:
- What depends on this resource?
- What is the expected downtime?
- Is there a way to do this without destroying (in-place update)?
- If data is involved: is there a backup? What is the recovery procedure?

Flag all destroy operations with:
```
⚠️ DESTROY DETECTED: <resource>
Impact: <what breaks if this is destroyed>
Data loss risk: <yes/no>
Downtime expected: <estimate>
Alternative: <is there a non-destructive path?>
Proceed? (requires explicit confirmation)
```

### Step 4: Security Review

**For AWS resources, check:**
- [ ] S3 buckets: no public ACL or bucket policy, encryption enabled, versioning enabled
- [ ] Security groups: no 0.0.0.0/0 ingress on sensitive ports (22, 3306, 5432, 6379)
- [ ] IAM roles/policies: least privilege, no `*` actions on sensitive services
- [ ] RDS: encryption at rest, deletion protection enabled, no public accessibility
- [ ] Lambda: no overly permissive execution role, VPC if accessing private resources
- [ ] EKS: no public API endpoint (or IP whitelist configured), node IAM roles minimal
- [ ] Secrets: no hardcoded passwords, tokens, or keys in IaC

**For Kubernetes manifests, check:**
- [ ] No container running as root (`runAsNonRoot: true`)
- [ ] No privileged containers (`privileged: false`)
- [ ] Resource requests and limits set (prevents resource starvation)
- [ ] Liveness and readiness probes configured
- [ ] No `hostNetwork: true` without justification
- [ ] Image tags are pinned (not `latest`)
- [ ] PodDisruptionBudget exists for critical services

### Step 5: Operational Safety Review

**Deployment concerns:**
- Will this change cause downtime? (zero-downtime vs. restart required)
- Are database migrations backwards-compatible?
- If this fails mid-apply, what is the partial state? Is it recoverable?

**Drift and state concerns:**
- Does this change match the current infrastructure state?
- Are there resources that were manually modified that this would overwrite?

### Step 6: Cost Impact Assessment
Estimate cost change:
- New resources: monthly cost estimate
- Modified resources: delta cost
- Destroyed resources: savings

Flag significant cost increases (>$500/month) for manager review.

### Step 7: Review Output Format

```
IaC Review: <change description>
Tool: Terraform | Date: <today>

## Summary
<N> resources to create, <N> to modify, <N> to destroy

## Critical Findings (must fix before apply)
- [ ] SECURITY: Security group sg-xxx allows 0.0.0.0/0 on port 5432 (PostgreSQL)
      Fix: restrict to VPC CIDR or specific IP ranges

## Warnings (should fix or document reason for exception)
- [ ] RDS deletion_protection is false — enable before applying to production
- [ ] S3 bucket versioning is disabled — recommended for production data buckets

## Informational
- [ ] Consider enabling S3 intelligent tiering for cost optimization

## Destroy Operations Requiring Confirmation
- [ ] aws_elasticache_cluster.session — DATA LOSS RISK — confirm backup exists

## Cost Impact
  New resources: +$340/month
  Destroyed resources: -$120/month
  Net: +$220/month

## Verdict
🔴 DO NOT APPLY — 1 critical finding must be resolved first
```

---

## Guidelines

- Every destroy requires explicit human confirmation — never approve blindly.
- Hardcoded secrets are always a critical finding, regardless of other context.
- Open security groups to 0.0.0.0/0 on database ports are always a critical finding.
- `latest` image tags in Kubernetes are always a warning.
- Persona (junior-sre): always recommend senior review for any destroy operations.
