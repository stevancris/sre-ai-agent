# My SRE Context

Fill in the fields below. The agent reads this file at the start of every conversation
to calibrate its output for your role and company situation.

---

## Role
```
role: senior-sre
# Options: junior-sre | senior-sre | sre-manager
```

## Current Situation
```
situation: learning
# Options: active-incident | post-incident | planning | routine-review | learning
# You can leave this blank — the agent will infer it from your message.
```

## Team
```
team_size: 5
on_call_rotation: weekly
company_stage: series-b
# company_stage options: startup | series-a | series-b | growth | enterprise
```

## Technology Stack
```
cloud_provider: aws
# Options: aws | gcp | azure | multi-cloud | on-prem | hybrid

container_platform: kubernetes

iac_tool: terraform
# Options: terraform | pulumi | cloudformation | ansible | cdk

observability_stack: datadog
# Options: datadog | prometheus-grafana | newrelic | dynatrace | opentelemetry

deployment_tool: argocd
# Options: argocd | spinnaker | jenkins | github-actions | flux

languages:
  - python
  - go
```

## SLO Configuration
```
primary_slo_target: 99.9
error_budget_policy: freeze-features-at-10pct-remaining
# When error budget falls below this threshold, feature work pauses and reliability
# work is prioritized.
```

## Incident Severity Levels
```
# Map your company's severity naming to P-levels
p0: total_service_outage_all_users_affected
p1: partial_outage_or_major_degradation_gt_10pct_users
p2: minor_degradation_lt_10pct_users_or_single_region
p3: non_user_facing_impact_or_internal_tools_only

# Escalation SLAs
p0_response_sla: 5min
p1_response_sla: 15min
p2_response_sla: 30min
p3_response_sla: next_business_day
```

## On-Call Rotation
```
primary_oncall: fill-in-name
secondary_oncall: fill-in-name
escalation_manager: fill-in-name
slack_incident_channel: "#incidents"
alerting_tool: pagerduty
# Options: pagerduty | opsgenie | victorops | grafana-oncall
```
