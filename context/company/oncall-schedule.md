# On-Call Schedule & Escalation Paths

Customize with your actual team members, rotation schedule, and escalation policy.

---

## Current Rotation
```
primary_oncall: <fill-in>
secondary_oncall: <fill-in>
escalation_manager: <fill-in>
rotation_length: weekly
handoff_day: monday
handoff_time: "10:00 UTC"
```

## Communication Channels
```
incident_slack_channel: "#incidents"
sre_team_slack_channel: "#sre-team"
status_page_url: <fill-in>
incident_bridge_tool: zoom
runbook_base_url: <fill-in>
```

## Escalation Path

```
Level 1 (0–15 min):   Primary on-call
Level 2 (15–30 min):  Secondary on-call
Level 3 (30–45 min):  Engineering Manager / SRE Lead
Level 4 (45+ min):    VP Engineering
Level 5 (P0 only):    CTO + Customer Success Lead
```

## PagerDuty / OpsGenie Configuration
```
alerting_tool: pagerduty
p0_policy: immediate-notify-all
p1_policy: notify-primary-then-secondary-after-5min
p2_policy: notify-primary-only
p3_policy: create-ticket-no-page
```

## External Contacts
```
# Cloud provider support
aws_support_tier: business
aws_support_url: https://console.aws.amazon.com/support/home

# Key vendor SLAs for escalation
datadog_status_url: https://status.datadoghq.com
```
