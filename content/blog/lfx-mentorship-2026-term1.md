---
title: "LFX Mentorship Journey: Ecosystem integrations & tutorials for AI Gateway"
toc: false
publishDate: 2026-06-01T00:00:00-00:00
author: Lasse Vierow
excludeSearch: true
---

## How the journey started
Three months ago I received my acceptance for the [LFX Mentorship Program](https://mentorship.lfx.linuxfoundation.org/project/1c354620-3475-474a-9641-a0a93f6961cf) and I was absolutely thrilled. But of course right after that the questions started piling up. How does this actually work? What exactly is expected of me? Am I actually able to deliver what they need?

The anticipation was huge.

The first thing that happened was a kick-off event with all the mentees who were working on a project in this term. Two days later I met my mentors [@Nina](https://github.com/npolshakova) and [@Art](https://github.com/artberger) in a personal video call and we could immediately clarify the first questions and talk through what the first concrete tasks would look like.

All of my activities during the mentorship can be tracked in the following issue: [kgateway-dev/kgateway.dev#606](https://github.com/kgateway-dev/kgateway.dev/issues/606)

## The projects I worked with
The main focus during the term was writing practical integration guides to connect the individual projects with each other. Of course other open source tools were used along the way to get all the tasks done, but these five were the core.

{{< reuse-image src="blog/lfx-mentorship-2026-term1-1.png">}}
{{< reuse-image-dark srcDark="blog/lfx-mentorship-2026-term1-1.png">}}

## What I worked on
The goal of the mentorship was to improve and expand the documentation on both [kgateway.dev](https://kgateway.dev) and [agentgateway.dev](https://agentgateway.dev) by creating clear, practical, and ecosystem focused integration guides. That meant actually running the tools, getting them to work together, and writing up step-by-step guides that others could follow from scratch.

The four main integration guides I wrote and shipped were:


1. **Argo Rollouts + kgateway** \
   This guide shows how to use [Argo Rollouts](https://kgateway.dev/docs/envoy/main/integrations/argo/) with kgateway for progressive delivery. Argo Rollouts is a Kubernetes controller that enables advanced deployment strategies like canary and blue-green releases. Since it supports the Kubernetes Gateway API, it can control exactly how traffic shifts between a stable and a canary version of your app, all routed through the kgateway proxy. The guide walks through setting up the Argo Rollouts plugin, defining a canary `Rollout`, creating the matching `HTTPRoute`, and watching traffic weights shift live as the promotion progresses.

2. **Argo Rollouts + agentgateway** \
   The same concept, applied to the agentgateway [Argo Rollouts](https://agentgateway.dev/docs/kubernetes/main/integrations/argo/) integration.

3. **KServe + agentgateway** \
   This guide demonstrates how to use agentgateway as a gateway for [KServe](https://agentgateway.dev/docs/kubernetes/main/integrations/kserve/) model serving, a Kubernetes-native platform for serving machine learning models. With agentgateway sitting in front of KServe, you can enforce policies like token-based rate limiting on inference requests without touching the inference service itself. The guide covers installing KServe, deploying a mock LLM, creating an `AgentgatewayBackend`, and applying a token budget policy that returns `429` responses once the per-minute token limit is exhausted.

4. **Kagent + agentgateway** \
   [Kagent](https://agentgateway.dev/docs/kubernetes/main/integrations/web-uis/kagent/) is a Kubernetes-native framework for running AI agents as declarative CRD-based resources. This guide shows how to secure and observe Kagent by routing its LLM traffic through agentgateway, giving you centralized control over authentication, rate limiting, and observability across all agent workloads, without changing a single line of agent code.

Beyond the documentation itself, the work meant constantly switching between repos, spinning up real Kubernetes clusters, and testing every step by hand. It was as much about learning how to write good documentation, following style guides, keeping examples reproducible, and structuring content so a first-time reader could actually follow along, as it was about understanding the underlying systems.

## What made it exciting
The cool thing about working across all these projects was discovering new things constantly. And naturally you also stumble into obstacles.
One that really stood out: while working on the KServe integration I found a small bug in agentgateway related to regex recognition in the HTTPRoutes that KServe auto-generates. The two tools simply did not work together because of it.
What made this moment special was not just finding the bug, it was what came next. Up until this point I had no real hands-on Go experience. But instead of just logging the issue and moving on, my mentors offered me the chance and the support to fix it myself. That was something I genuinely did not expect. And because of that support, I worked through the fix, learned a bit of Go, and in the end both tools worked together correctly.
That was one of my favourite and most satisfying moments, seeing everything work.

## The unexpected
One thing I truly did not see coming was the chance to create content that might actually make it to KubeCon, as a real talk submission. That possibility alone felt like a whole new chapter opening up. I am keeping my fingers crossed that one talk get accepted.

## Conclusion
The last few months were packed with new knowledge and experiences. What is great about the program is that it provides a structured flow with weekly check-ins on your progress, while still leaving you enough freedom to work on topics that genuinely interest you. A huge thank you to [@Nina](https://github.com/npolshakova) and [@Art](https://github.com/artberger) for being awesome mentors, for the support and the fast feedback throughout the whole term. If you ever get the chance to apply for the Mentorship Program, I would definitely recommend it.

cheers!

*GitHub: [@Lasse4](https://github.com/Lasse4) · LinkedIn: [lasse-vierow](https://www.linkedin.com/in/lasse-vierow/)*
