---
title: "My LFX Mentorship Journey with kgateway"
toc: false
publishDate: 2026-06-30T00:00:00-00:00
author: Lahiru De Silva
excludeSearch: true
---

Open source has been a defining part of my career for many years. As an engineer working in the cloud native ecosystem, I have spent the last five years building and contributing to technologies around Kubernetes, Envoy Proxy, API gateways, and service networking. These technologies power modern platforms at scale, and they are also at the heart of many CNCF projects that shape the future of cloud infrastructure.

Earlier this year, I had the opportunity to participate in the Linux Foundation Mentorship Program (LFX) through the kgateway project. What started as a mentorship project quickly evolved into something much bigger: a path toward becoming a long-term contributor and future maintainer in a community I genuinely enjoy being part of.

## Why kgateway?

At my day job, we recently started adopting kgateway in [OpenChoreo](https://openchoreo.dev/), an open source internal developer platform for Kubernetes and a CNCF Sandbox project, and were impressed by its technical architecture, stability, and alignment with modern cloud native standards. Built on top of Envoy Proxy and Kubernetes Gateway API, kgateway provides a powerful and extensible foundation for managing traffic in Kubernetes environments. The project's maturity, active development, and commitment to open standards made it particularly attractive as we evaluated solutions for our platform.

While evaluating the project, I noticed an LFX mentorship opportunity that focused on an area directly related to my background. The timing felt perfect. Rather than simply consuming the project as a user, I wanted to contribute back and become an active member of the community.

The mentorship program offered an ideal starting point.

## Why an LFX Mentorship?

There is a common misconception that the LFX Mentorship program is only for students or early-career engineers. With five years of experience in cloud native API gateways and networking, I was already comfortable working with Go, Kubernetes, and Envoy Proxy. However, joining a mature open source ecosystem as a newcomer can still be challenging. Every project has its own architecture, governance model, testing practices, and community norms that take time to understand.

At the same time, balancing a full-time job and family commitments means open source contributions often lack consistency without structure. Without a clear scope and guidance, it’s easy for contributions to get delayed or lose momentum.

I saw the [LFX Mentorship for kgateway](https://mentorship.lfx.linuxfoundation.org/project/b8acc432-094a-431a-877a-97f209893672) as the ideal starting point. It provided structured onboarding, a well-defined project scope, and direct weekly interaction with core maintainers.

I applied, was accepted, and my journey began.

## The Mentorship Experience

From day one, I was working closely with core maintainers, which made a huge difference in understanding the project. Instead of spending weeks trying to decode design decisions on my own, I was able to get direct context on architecture, trade-offs, and long-term direction.

The focus of my mentorship was [adding chaos engineering support to kgateway through HTTP fault injection](https://mentorship.lfx.linuxfoundation.org/project/b8acc432-094a-431a-877a-97f209893672). The idea is to let platform teams deliberately inject failures, such as delays and aborts, into their traffic so they can validate how resilient their services are before those failures show up in production.

My core deliverable was [implementing fault injection support by extending `TrafficPolicy`](https://github.com/kgateway-dev/kgateway/pull/13730), covering delay injection, abort injection with both HTTP and gRPC status codes, response rate limiting, and a per-route override to disable it. Under the hood it maps to the Envoy HTTP fault filter, which is added to the filter chain disabled by default and enabled selectively per route or virtual host. This keeps the feature completely inert unless a policy explicitly opts in.

The learning curve was still real. kgateway sits at the intersection of Kubernetes, Envoy Proxy, and the Gateway API, so even small changes often required understanding multiple layers of the system. But having a structured path and regular syncs kept the progress steady and focused.

Some of the key areas I gained a deep understanding of during the mentorship included:

- Understanding the internal architecture of the kgateway control plane
- Kubernetes Gateway API implementation within kgateway
- kgateway plugin architecture for extensible policy design
- Abstracting low-level Envoy Proxy configuration into developer-facing policies
- kgateway policy merge implementation and merge strategies
- Community collaboration and open source development workflows

What stood out most was how iterative and collaborative the process was. Every contribution went through thoughtful review, not just for correctness, but for long-term maintainability and alignment with the direction of the project.

By the end of the mentorship, I had not only completed the assigned project work but also built enough context to contribute independently without needing step-by-step guidance.

## Beyond the Mentorship

For me, the mentorship was never intended to be a one-time contribution. My goal from the beginning was to use the program as a starting point for a deeper involvement in the project and community. After completing the mentorship project, I continued contributing to kgateway by working on new features, bug fixes, and community discussions.

The transition from mentee to regular contributor felt natural because the mentorship had already provided the context, relationships, and confidence needed to contribute independently.

Since completing the program, I have continued contributing to kgateway by:

- Contributing feature enhancements
- Fixing bugs and improving project stability
- Participating in technical discussions
- Reviewing and collaborating on community contributions
- Helping shape future improvements to the project

A couple of contributions I am especially proud of since completing the mentorship:

- **[BackendConfigPolicy merge semantics and BCP/BTP conflict resolution](https://github.com/kgateway-dev/kgateway/pull/14043)** — `BackendConfigPolicy` had no merge semantics, so when multiple policies targeted the same backend the behavior was inconsistent. On top of that, `BackendConfigPolicy` and `BackendTLSPolicy` overlap on the TLS configuration, and the conflict resolution between them was not properly defined. This work fixed both: field-level merge for `BackendConfigPolicy` where fields from older policies take precedence and newer policies fill in unset fields, and a clear rule for TLS conflicts that gives priority to `BackendTLSPolicy` as the standard Gateway API resource.
- **[Configurable filter stage positioning for ExtProc](https://github.com/kgateway-dev/kgateway/pull/13845)** — This added the ability to control where the ExtProc filter is placed in the Envoy HTTP filter chain, which matters when ExtProc needs to run before or after filters like authentication or rate limiting. The main challenge was the API design: exposing a stage (`Fault`, `AuthN`, `AuthZ`, `RateLimit`, `Route`), a predicate (`Before`, `During`, `After`), and a weight to order multiple filters at the same stage, while keeping it intuitive to use.

Beyond these, I contributed several other features: TLS termination for `TLSRoute` on a TLS listener, upstream proxy protocol support via `BackendConfigPolicy`, forwarding client certificate details upstream, and async fetch with retry support for remote JWKS.

These experiences have given me a much broader appreciation for the work that maintainers do every day to keep open source projects healthy and sustainable.

## The Value of Open Source Mentorship

The LFX Mentorship Program demonstrates something important about open source communities: **great contributors are developed, not discovered**.

Many engineers have the technical skills to contribute, but they often lack the guidance or confidence needed to take the first step. Mentorship programs create an environment where new contributors can learn, grow, and eventually become leaders within the community.

My experience is a perfect example of that progression. What began as a mentorship project has grown into an ongoing commitment to the kgateway community and a long-term goal of becoming a maintainer.

## Looking Ahead

Today, I continue contributing to kgateway and am actively working toward becoming a maintainer.

The project sits at the intersection of several technologies that I am deeply passionate about: Kubernetes, Envoy Proxy, API gateways, and cloud native networking. Being able to contribute to a project that aligns so closely with my professional interests makes the experience particularly rewarding.

Looking back, applying for the LFX mentorship was one of the best decisions I made in my open source journey. It provided a structured path into a community, accelerated my understanding of the project, and opened opportunities that continue to grow long after the mentorship officially ended.

To anyone considering an LFX mentorship, my advice is simple: **view it as the beginning of your journey, not the destination**.

The most valuable outcome is not the project you complete during the mentorship. It is the community you become part of afterward.

## Thank You

A huge thank you to my mentors, [Tim Flannagan](https://github.com/timflannagan) and [Omar Hammami](https://github.com/puertomontt), along with the kgateway maintainers and community members, for their time, guidance, and support throughout the mentorship process. Open source thrives because people are willing to help others learn, contribute, and succeed.

I am excited to continue contributing to the project and helping shape the future of cloud native API gateways together with the community.

*GitHub: [@NomadXD](https://github.com/NomadXD) · LinkedIn: [Lahiru De Silva](https://www.linkedin.com/in/lahiru-udayanga/)*
