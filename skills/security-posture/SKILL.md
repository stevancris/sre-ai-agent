---
name: security-posture
description: >
  Assess and improve the security posture of infrastructure and services. Use when
  conducting access reviews, responding to a security alert, preparing for a compliance
  audit, reviewing secrets management, or hardening infrastructure. Trigger keywords:
  security, access review, IAM, permissions, least privilege, secrets, vulnerability,
  CVE, compliance, SOC2, ISO27001, audit, hardening, exposure, attack surface, breach,
  security incident, leaked credentials, security review, penetration test, pentest finding.
allowed-tools: Read Glob Grep
---

# Security Posture Skill

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
Read `context/company/tech-stack.md` for cloud provider, secrets manager, and compliance
frameworks. Determine the scope of the review.

### Step 2: Determine Scope
Classify the request into one or more review areas:
- **IAM / Access review** — who can do what
- **Secrets management** — are secrets handled safely
- **Network exposure** — what is reachable from the internet
- **Container security** — are containers hardened
- **Compliance** — mapping to SOC 2, ISO 27001, PCI-DSS, etc.
- **Vulnerability triage** — prioritizing CVEs and security findings

---

### Mode: IAM / Access Review

**Principle of least privilege audit:**
- [ ] List all IAM roles/service accounts and their policies
- [ ] Flag any role with `*` (wildcard) actions or resources
- [ ] Flag any human user with programmatic access keys (prefer temporary credentials)
- [ ] Check access key age: rotate any key > 90 days old
- [ ] Review cross-account access: are all trust relationships intentional?
- [ ] Check for unused roles/users (no activity in 90+ days) → deactivate

**Service account audit (Kubernetes):**
- [ ] Are pods using the default service account? (should be a dedicated one)
- [ ] Do service accounts have cluster-admin or overly broad RBAC roles?
- [ ] Are service account tokens mounted where not needed? (`automountServiceAccountToken: false`)

**Findings format:**
```
IAM Finding — CRITICAL
Resource: arn:aws:iam::123456789:role/app-role
Issue: Policy allows s3:* on resource: *
Risk: Any service using this role can read/write/delete any S3 bucket in the account
Remediation: Restrict to s3:GetObject on arn:aws:s3:::app-data-bucket/*
```

---

### Mode: Secrets Management

Check for secrets exposure:
- [ ] Scan recent git history for hardcoded secrets (API keys, passwords, tokens)
- [ ] Verify application config uses a secrets manager (AWS Secrets Manager, Vault, GCP Secret Manager)
- [ ] Check environment variables in Kubernetes manifests — no plaintext secrets in `env:` blocks
- [ ] Verify secrets are not logged (grep logs for common secret patterns)
- [ ] Check secrets rotation policy: are secrets rotated automatically or manually?
- [ ] Verify secrets are encrypted at rest in the secrets manager
- [ ] Check who has access to read secrets in production (least privilege)

If a leaked secret is suspected:
1. Rotate the credential immediately (before investigation).
2. Revoke the old credential.
3. Audit access logs for the time window the secret was exposed.
4. Determine what the secret had access to and assess data exposure.
5. Report per your company's incident response plan.

---

### Mode: Network Exposure

**Internet-facing inventory:**
- List all public-facing resources: ALBs, API Gateways, S3 buckets with public access
- Verify each public endpoint is intentional and documented
- Check security group rules: are any database ports (3306, 5432, 6379, 27017) open to 0.0.0.0/0?
- Verify WAF is in place for public-facing web applications
- Check that admin interfaces (Kubernetes API, database admin, CI/CD) are not publicly accessible

**Zero-trust network review:**
- Are service-to-service calls using mTLS or IAM-based auth?
- Is there a network policy in Kubernetes limiting pod-to-pod traffic?

---

### Mode: Vulnerability Triage

Prioritize CVEs using this framework:

| Priority | Criteria | Action |
|---|---|---|
| P0 — Fix in 24h | CVSS ≥ 9.0 AND exploitable in your environment | Emergency patch |
| P1 — Fix in 1 week | CVSS ≥ 7.0 AND exploitable | Planned patch |
| P2 — Fix in 1 month | CVSS 4.0–7.0 OR not directly exploitable | Scheduled update |
| P3 — Fix in quarter | CVSS < 4.0 | Backlog |

**Exploitability factors (increase priority):**
- The vulnerable component is internet-facing
- There is a known public exploit (check CISA KEV catalog)
- The vulnerability allows remote code execution or privilege escalation

---

### Mode: Compliance Mapping

For SOC 2 Type II readiness:
- CC6: Logical and physical access controls
- CC7: System operations (change management, incident response)
- CC8: Change management (IaC, deployment controls)
- CC9: Risk mitigation (vendor management, business continuity)

Map each finding to its applicable control. Flag gaps that would be findings in an audit.

---

## Guidelines

- Always rotate first, investigate second — when a secret is suspected leaked.
- Never log or output plaintext secrets in skill output.
- A finding is actionable only if it is exploitable in this environment — avoid theoretical risks.
- Persona (sre-manager): output a risk register format with likelihood, impact, and remediation
  effort for each finding. Include a compliance impact column.
