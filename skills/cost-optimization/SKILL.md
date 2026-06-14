---
name: cost-optimization
description: >
  Identify and reduce cloud infrastructure costs without compromising reliability. Use when
  reviewing cloud bills, investigating cost spikes, rightsizing resources, planning Reserved
  Instance or Savings Plan purchases, or building a FinOps practice. Trigger keywords:
  cost, cloud bill, spend, rightsizing, reserved instances, savings plans, waste, idle
  resources, FinOps, cost anomaly, budget alert, expensive, overprovisioned, underutilized,
  cost spike, cloud spend, AWS cost, GCP cost, monthly bill, reduce spend.
allowed-tools: Read Glob Grep
---

# Cost Optimization Skill

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
Read `context/company/tech-stack.md` for cloud provider and platform.

### Step 2: Identify Cost Drivers
Ask the user to share:
- Top cost categories from the billing dashboard (compute, storage, data transfer, etc.)
- Any recent cost spikes (when and how much)
- Current monthly total and recent trend

Classify costs into:
| Category | Typical % of bill | Optimization potential |
|---|---|---|
| Compute (EC2/GCE/VMs) | 40–60% | High |
| Managed services (RDS, ElastiCache) | 15–25% | Medium |
| Storage (S3, EBS, GCS) | 5–15% | Medium |
| Data transfer / egress | 5–20% | Variable |
| Kubernetes (EKS/GKE) | 10–20% | High |
| Logging / observability | 5–15% | Medium |

### Step 3: Waste Identification

**Idle resources:**
- EC2/VM instances with CPU < 5% sustained
- Unattached EBS volumes
- Unused Elastic IPs
- Unused load balancers
- Old snapshots (> 90 days with no restore)
- Dev/staging resources running 24/7 (schedule to turn off nights/weekends)

**Overprovisioned resources:**
- Instances where CPU is consistently < 20% and memory < 40%
- Database instances with < 20% utilization
- Over-specified Kubernetes resource requests (pod requests >> actual usage)
- EBS volumes that are only 20–30% full but sized for 10x current data

**On-demand vs. commitment opportunity:**
- Instances running > 3 months on-demand → Reserved Instance or Savings Plan candidate
- Steady-state workloads → Compute Savings Plans (1-year, no-upfront)
- Flexible workloads → Spot Instances (batch jobs, CI/CD workers, stateless services)

### Step 4: Rightsizing Analysis
For compute rightsizing:

```
Rightsizing recommendation logic:
  If avg CPU < 20% and avg memory < 40%:
    → Downsize to next smaller instance type
  If avg CPU > 70% or avg memory > 80%:
    → This is correctly sized or may need upsizing
  If CPU is high but memory is low:
    → Consider compute-optimized instance type
  If memory is high but CPU is low:
    → Consider memory-optimized instance type
```

### Step 5: Kubernetes Cost Optimization
- Compare pod resource requests vs. actual usage (Vertical Pod Autoscaler recommendations).
- Identify namespaces or workloads with no resource limits (risk of resource starvation and overspend).
- Check if cluster autoscaler is configured and working.
- Evaluate whether Spot/Preemptible nodes can be used for non-critical workloads.
- Check node utilization: if < 40% average, the cluster may be over-provisioned.

### Step 6: Storage Optimization
- S3: lifecycle rules to transition to Infrequent Access after 30 days, Glacier after 90 days.
- EBS: delete unattached volumes, rightsize over-provisioned volumes.
- Log retention: audit log retention periods (7 days for debug logs, 30 days for info, 1 year for audit).
- Old snapshots: automate deletion of snapshots older than retention policy.

### Step 7: Generate Recommendations

Rank by: (monthly savings) × (implementation ease) / (reliability risk)

```
Recommendation Report — Cloud Cost Optimization

Current monthly spend: $XX,XXX
Potential savings identified: $X,XXX/month (XX%)

Priority 1: Reserved Instances for steady-state EC2 (save ~$1,200/mo)
  Risk: Low | Effort: Low (1-click purchase) | Payback: immediate
  Action: Purchase 1-year no-upfront Compute Savings Plan for $X commit/hr

Priority 2: Schedule dev/staging environment off-hours (save ~$800/mo)
  Risk: None | Effort: Low | Payback: immediate
  Action: Lambda function to stop instances 6pm–8am weekdays, all weekend

Priority 3: Rightsize 8 overprovisioned RDS instances (save ~$600/mo)
  Risk: Medium (test in staging first) | Effort: Medium
  Action: See rightsizing table below

Priority 4: S3 lifecycle rules for logs bucket (save ~$200/mo)
  Risk: None | Effort: Low
  Action: Add lifecycle rule: IA after 30d, Glacier after 90d

Total addressable: ~$2,800/month (~28% reduction)
```

---

## Guidelines

- Never recommend a cost saving that introduces a reliability risk without explicitly stating
  the trade-off and getting confirmation.
- Spot instances are only appropriate for stateless, fault-tolerant workloads.
- Reserved Instances are a financial commitment — confirm with finance/management before purchasing.
- Persona (sre-manager): frame the savings as ROI and include the time to implement each item.
  Calculate cost of engineering time to implement vs. expected savings.
