# Company Tech Stack

Fill in your actual values. The agent uses this file to produce concrete, tool-specific
recommendations instead of generic advice.

---

## Cloud & Infrastructure
```
cloud_provider: aws
primary_regions: [us-east-1, us-west-2]
secondary_regions: [eu-west-1]
multi_account: true
account_structure: prod | staging | dev | shared-services
```

## Container & Orchestration
```
container_platform: kubernetes
kubernetes_distribution: eks
# Options: eks | gke | aks | self-managed | openshift
node_count_prod: 30
```

## Infrastructure as Code
```
iac_tool: terraform
terraform_version: "1.7"
state_backend: s3
modules_registry: terraform-registry
```

## Observability
```
metrics: datadog
logs: datadog
traces: datadog
synthetics: datadog
alerting: pagerduty
oncall_tool: pagerduty
```

## Deployment
```
ci_tool: github-actions
cd_tool: argocd
artifact_registry: ecr
deployment_strategy: canary
feature_flags: launchdarkly
```

## Databases
```
primary_db: postgresql-rds
cache: elasticache-redis
search: opensearch
queue: sqs
stream: kinesis
```

## Service Mesh & Networking
```
service_mesh: none
# Options: istio | linkerd | none
load_balancer: alb
cdn: cloudfront
dns: route53
```

## Languages & Frameworks
```
languages: [python, go]
primary_language: python
frameworks: [fastapi, grpc]
```

## Security & Compliance
```
secrets_manager: aws-secrets-manager
vulnerability_scanner: snyk
compliance_frameworks: [soc2, iso27001]
sast_tool: semgrep
```
