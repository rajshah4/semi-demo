# Local, Cloud, And Air-Gapped Deployment

## Why This Matters

Foundry IT teams often cannot use a public SaaS coding assistant directly against sensitive design data. The deployment story is part of the product value.

## Local

Best for:

- laptop demo
- customer proof of concept
- debugging workflow logic
- showing Agent Canvas conversations

Tradeoffs:

- inbound webhooks from public services usually cannot reach a local server
- use manual dispatch or cron-style polling for local demos
- easier to show, less realistic for enterprise operations

## Cloud

Best for:

- live webhook demos
- GitHub/Jira/Slack integrations
- managed model endpoints
- easy sharing and repeatability

Tradeoffs:

- data-boundary questions
- customer security review
- secrets and access control need to be crisp

## Air-Gapped Or Private

Best for:

- foundry IT story
- sensitive RTL/IP
- PDK and licensed EDA environments
- controlled model and toolchain images

Tradeoffs:

- heavier setup
- model availability depends on local/private inference
- image and license management matter

## Demo Guidance

Use local for the build-out and first rehearsal. Use cloud if the audience needs to see real webhooks. Use air-gap as the enterprise deployment proof point:

> The same workflow can run against approved models and pre-baked EDA tools inside a controlled environment.

