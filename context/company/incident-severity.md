# Incident Severity Levels

Customize these definitions to match your company's severity classification scheme.
The agent uses this file to classify incidents consistently.

---

## P0 — Critical (SEV1)
**Definition:** Total service outage or data loss affecting all users or all of a core feature.

- Response SLA: page immediately, acknowledge within 5 minutes
- Bridge: always open an incident bridge/war room
- Stakeholders: notify VP Engineering + Customer Success immediately
- External comms: post status page update within 15 minutes
- Examples:
  - Payment service completely down
  - Auth service rejecting all logins
  - Data corruption or loss in production database
  - All API endpoints returning 5xx

## P1 — High (SEV2)
**Definition:** Major degradation affecting >10% of users or a critical path feature.

- Response SLA: acknowledge within 15 minutes
- Bridge: open if multiple teams involved
- Stakeholders: notify engineering manager
- External comms: post status page update if user-facing impact persists >30 minutes
- Examples:
  - Checkout flow failing for 20% of users
  - P99 latency > 5x normal for primary API
  - Single-region outage in a multi-region setup
  - Core feature unavailable (not payment critical)

## P2 — Medium (SEV3)
**Definition:** Minor degradation affecting <10% of users or a non-critical feature.

- Response SLA: acknowledge within 30 minutes
- Bridge: not required
- Stakeholders: notify on-call team lead
- External comms: only if persists >2 hours
- Examples:
  - Slow response on non-critical endpoints
  - Single tenant or small cohort affected
  - Non-critical background job failures
  - Admin UI degraded (not customer-facing)

## P3 — Low (SEV4)
**Definition:** No user-facing impact. Internal tools or monitoring affected.

- Response SLA: next business day
- Bridge: not required
- Stakeholders: ticket created for team
- External comms: none
- Examples:
  - Flaky test in CI
  - Internal dashboard broken
  - Non-critical cron job failing
  - Log volume spike (no user impact)

---

## Severity Decision Tree

```
User-facing impact?
├── No  → P3
└── Yes →
    All users or critical path?
    ├── Yes → P0
    └── No  →
        >10% of users or major feature?
        ├── Yes → P1
        └── No  → P2
```
