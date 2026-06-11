---
name: capacity-planning
description: >
  Forecast infrastructure capacity needs and plan for growth. Use when planning for a
  product launch, reviewing resource utilization, handling autoscaling limits, responding
  to cost spikes from over-provisioning, or building a quarterly infrastructure roadmap.
  Trigger keywords: capacity, scaling, growth, traffic forecast, infrastructure sizing,
  autoscaling, resource limits, nodes, pods, instances, headroom, peak traffic, launch,
  viral growth, capacity crunch, running out of, max replicas, HPA limit, scale up.
allowed-tools: Read Glob Grep
---

# Capacity Planning Skill

## Instructions

### Step 1: Load Context
Read `context/CONTEXT.md` and `context/company/tech-stack.md` for cloud provider,
container platform, and company stage.

### Step 2: Gather Current Baseline
Ask the user for (or help them find):
- Current resource utilization: CPU %, memory %, storage, network throughput
- Current traffic: RPS at P50 / P95 / P99 / peak
- Current pod/instance counts per service
- Autoscaling configuration (min, max, target utilization)
- Cost baseline (monthly cloud spend)

### Step 3: Project Growth
Choose the appropriate growth model:

**Linear growth model** (steady, predictable business)
```
projected_traffic = current_traffic × (1 + monthly_growth_rate)^months
```

**Exponential growth model** (early startup, high growth)
```
projected_traffic = current_traffic × growth_multiplier^quarters
```

**Event-driven model** (product launch, seasonal peak)
```
peak_traffic = baseline_traffic × peak_multiplier
# Common peak multipliers: 2x (normal launch), 5x (viral launch), 10x (major campaign)
```

Ask the user:
- What is the expected monthly traffic growth rate?
- Are there any planned events (launches, campaigns, partnerships) that will spike traffic?
- What is the planning horizon (3 months, 6 months, 1 year)?

### Step 4: Identify Bottlenecks
For each resource dimension, calculate when it hits its limit:

```
Time to limit = (limit - current_value) / monthly_growth_rate

Example:
  CPU: currently at 45%, limit at 80% (with autoscaling headroom)
  Monthly traffic growth: 15%
  CPU grows proportionally to traffic
  Months to limit: (80 - 45) / (45 × 0.15) = 5.2 months
```

Bottleneck analysis table:
| Resource | Current | Limit | Growth Rate | Months to Limit |
|---|---|---|---|---|
| CPU | 45% | 80% | 15%/mo | 5.2 months |
| Memory | 60% | 85% | 12%/mo | 2.1 months ← **FIRST BOTTLENECK** |
| Storage | 30% | 90% | 8%/mo | 7.5 months |
| Network | 20% | 80% | 20%/mo | 3.0 months |

### Step 5: Sizing Recommendations
For each bottleneck, provide concrete recommendations:

**Kubernetes / containers:**
- Adjust resource requests and limits
- Increase max replicas in HPA
- Evaluate cluster node count and instance types
- Consider vertical pod autoscaling for memory-bound services

**Databases:**
- Read replica count for read-heavy scaling
- Connection pool sizing
- Instance class upgrade timeline
- Sharding consideration for write-heavy growth

**Caching:**
- Cache hit rate improvement (reduce origin load)
- Cache cluster sizing

### Step 6: Capacity Timeline
Produce a month-by-month action plan:

```
Month 1: Increase memory limits for payment-api (bottleneck at current rate)
Month 2: Add 5 nodes to prod EKS cluster (before projected limit)
Month 3: Upgrade RDS instance class (replication lag increasing)
Month 4: Add read replica for user-service DB
Month 6: Evaluate sharding strategy for orders table (projected 500GB)
```

### Step 7: Cost Projection
Estimate cost of recommended capacity changes:

| Change | Monthly Cost Impact | One-Time Cost |
|---|---|---|
| 5 additional EKS nodes (m5.xlarge) | +$1,200/mo | — |
| RDS instance upgrade (db.r6g.2xlarge) | +$800/mo | — |
| Additional read replica | +$600/mo | — |
| **Total** | **+$2,600/mo** | — |

---

## Guidelines

- Always include a "do nothing" scenario to show the cost of inaction (incident, degradation).
- Build in a 30% headroom buffer beyond projected peak — forecasts are always wrong.
- Autoscaling is not infinite: always check max replica counts and node pool limits.
- Persona (sre-manager): include team bandwidth to execute the capacity plan and whether
  hiring is needed to manage increased infrastructure complexity.
