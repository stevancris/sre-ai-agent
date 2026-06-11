# Severity Classification Matrix

Use this matrix to classify an incident consistently. When uncertain between two severities,
choose the higher one — it is always easier to downgrade than to escalate late.

---

## Decision Tree

```
Is there any user-facing impact?
├── No → P3
└── Yes →
    Is the entire service/product down, or is a critical revenue path (checkout, auth, payments) broken?
    ├── Yes → P0
    └── No →
        Is more than 10% of users affected, or is a major feature completely unavailable?
        ├── Yes → P1
        └── No →
            Is any user affected (even a small cohort)?
            ├── Yes → P2
            └── No → P3
```

---

## Matrix Table

| Criteria | P0 | P1 | P2 | P3 |
|---|---|---|---|---|
| Service availability | Total outage | Major degradation | Minor degradation | N/A |
| Users affected | All or near all | > 10% | < 10% | 0 (internal only) |
| Revenue impact | Direct, significant | Significant risk | Minor | None |
| Data integrity risk | Possible/confirmed | Possible | No | No |
| Time to first response | 5 minutes | 15 minutes | 30 minutes | Next business day |
| Bridge required | Always | If multi-team | No | No |
| Status page update | Within 15 min | If > 30 min | Only if > 2 hours | Never |
| Postmortem required | Always | Always | If novel | No |

---

## Examples by Severity

### P0 Examples
- All users receive 500 errors on the main application
- Checkout / payment processing down for all users
- Auth service down (no one can log in)
- Database corruption or data loss confirmed
- Security breach with active data exfiltration

### P1 Examples
- Checkout failing for 25% of users due to intermittent errors
- API P99 latency > 5x normal for > 5 minutes
- Single-region outage in a multi-region setup
- Major feature unavailable (e.g., search, notifications)
- Performance degradation affecting user experience broadly

### P2 Examples
- Slow responses on non-critical endpoints
- Single tenant or small user cohort affected
- Background job failures not affecting end users immediately
- Admin UI down (not customer-facing)
- Feature degradation (not failure) for < 10% of users

### P3 Examples
- Flaky tests in CI pipeline
- Internal dashboard broken or slow
- Non-critical cron job failing
- Log volume anomaly (no user impact)
- Monitoring or alerting tool degraded

---

## Downgrade Criteria

Downgrade severity when:
- Impact scope is confirmed to be smaller than initially assessed
- The problem is contained to a single tenant or cohort
- A workaround exists and most users can proceed normally
- The initial alert was a false positive

Always communicate downgrades in the incident channel with the reason.
