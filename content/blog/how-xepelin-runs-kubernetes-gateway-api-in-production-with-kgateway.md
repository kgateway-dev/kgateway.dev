---
title: How Xepelin Runs Kubernetes Gateway API in Production with kgateway
toc: false
publishDate: 2026-01-09T00:00:00-00:00
author: Javier Orellana, DevOps / Platform Engineer, Xepelin
excludeSearch: true
---
Xepelin, one of the largest fintech companies in Latin America, was founded in Chile in 2019 and now also operates in Mexico. Xepelin focuses on providing personalized financial solutions designed to fuel growth without traditional bureaucratic processes.

At Xepelin, we have been running **kgateway** with **Gateway API resources in production** across multiple Kubernetes clusters, spanning ~500 namespaces and hundreds of route resources. Our platform integrates Kubernetes with Prometheus, OpenTelemetry, CloudWatch, Datadog, and other components to support a high-traffic, highly observable environment.

### Background
Xepelin’s platform runs on AWS using Kubernetes with EKS. We operate multiple environments and handle a significant amount of internal and external traffic. Over time, the traffic layer became more complex, both operationally and in terms of cost. Our main goals were to:
- Simplify the traffic architecture
- Improve observability
- Reduce infrastructure costs

{{< reuse-image src="blog/kgateway-at-xepelin-1.svg" caption="Legacy traffic architecture at Xepelin based on AWS API Gateway, Lambda authorizers, and per-service Network Load Balancers, which led to operational complexity and high infrastructure costs." >}}

As we operate the AWS API Gateway which controls all incoming traffic to the EKS clusters, with Lambda authorizers and Network Load Balancers (NLBs), we started to hit several issues:
- A large number of NLBs, leading to high infrastructure costs.
- Fragmented traffic management, where Kubernetes specifications handled the Service (type LoadBalancer) configuration, while AWS API Gateway routes were created and modified separately using Terraform or the AWS Console. This split ownership resulted in a disjointed workflow and increased operational complexity when managing traffic changes end-to-end.
- Fragmented observability across the traffic path, which made it impossible to have centralized metrics and end-to-end visibility across the API Gateway → NLB → Kubernetes Service chain. As a result, diagnosing issues such as sporadic 503 errors was slow and required manual investigation across multiple systems.

Our initial model relied heavily on Kubernetes Services of type **LoadBalancer**, with AWS API Gateway routing traffic directly to the NLBs created by those services. This resulted in a large number of Network Load Balancers and steadily increasing operational costs.

At the time, we had the AWS Load Balancer Controller installed in each cluster. While this made it easy to create new load balancers, **it also contributed significantly to infrastructure sprawl**.

### Why kgateway?
Migrating away from an AWS API Gateway–centric architecture to a Kubernetes-native solution was not just a tooling change. It represented a **fundamental shift** in how we expose, operate, and observe our APIs. Because of this, choosing the gateway for north–south traffic was a critical decision.

The existing architecture had been in place for years and **did not scale well**. Any migration therefore had to meet one fundamental requirement: it needed to be as transparent as possible for both teams and existing traffic flows.

With that in mind, we focused on the following aspects.

#### Transparent and low-friction migration
One of the main challenges was replicating the behavior that already existed in AWS API Gateway, especially the Lambda Authorizer.

This authorizer received each request, performed several validations, and interacted with AWS services such as Secrets Manager.

With kgateway, we were able to replicate this behavior thanks to its tight integration with Envoy and its support for external authorization.

#### Full, first-class support for Gateway API
Full, native support for the Kubernetes Gateway API was a key requirement for us.

We wanted the Gateway API to be the primary way to model north–south traffic, not an optional layer. Kgateway stood out because the Gateway API is at the core of its design, which made it a natural fit for how we manage routing and traffic behavior in production.

#### Built on Envoy
Kgateway is built on top of Envoy, one of the most widely used and powerful proxies in the cloud-native ecosystem. Envoy provides:

- Rich metrics per proxy and per route (counters, gauges, histograms)
- Detailed visibility into request rates, latencies, errors, and upstream/downstream behavior
- Advanced flexibility around timeouts, retries, circuit breaking, and more

#### History and maturity: Born as Gloo
Before being called kgateway, the project was known as Gloo and was developed by Solo.io. This was an important factor for us because:

- It has been proven across hundreds of production deployments
- It is not experimental, but a very mature and stable project
- It has processed billions of requests for large companies worldwide

This track record was a major advantage over newer or less widely adopted alternatives.

#### Advanced observability with native OpenTelemetry integration

##### Metrics
- Control plane: The kgateway control plane exposes Prometheus metrics that give full visibility into how synchronization and reconciliation are behaving.
- Data plane: Each Envoy pod exposes detailed Prometheus metrics describing real traffic behavior.
This allows metrics to be consumed directly by our existing observability stack or via an OpenTelemetry Collector, fully integrating with our monitoring infrastructure.

##### Access logs
Envoy access logs from the data plane are very easy to expose using resources managed by the kgateway controller itself. It also provides native exporters to OpenTelemetry collectors.

##### Traces
Kgateway includes native trace exporters that can send traces directly to OpenTelemetry collectors.

#### Fast synchronization and near-immediate feedback
One aspect that turned out to be more important than expected was synchronization speed between Kubernetes resources and the gateway data plane.
With kgateway, changes to HTTPRoute resources are reflected in Envoy near-instantaneously, typically within seconds in our experience. This contrasts sharply with our previous AWS API Gateway setup, where changes were slower, involved multiple deployment steps, and often required manual cross-team coordination.
The low latency between HTTPRoute changes in the control plane and their application in the data plane was a key factor in choosing kgateway. It also fits very naturally with a GitOps model, where manifest changes are quickly reflected in live traffic.

#### Focus on north–south traffic with a path to east–west
The primary goal of this migration was to fix north–south traffic routing, specifically:
- Reducing costs by cutting down the number of NLBs
- Gaining real and detailed observability
- Enforcing external security policies

Beyond that, we wanted an architecture that could evolve toward a service mesh capable of handling east–west traffic.
Kgateway fit well because it:
- Uses Envoy as its data plane
- Integrates cleanly with Gateway API
- Can act as an ingress for a future service mesh
- Works particularly well as an ingress for Istio Ambient Mode, where Envoy acts as a waypoint proxy to apply L7 policies without sidecars

#### Comparison with other tools
We also evaluated Kong and Traefik before we decided on kgateway:
| **Feature / Tool**                      | **Kgateway**           | **Kong**                                    | **Traefik**                       |
|-----------------------------------------|------------------------|---------------------------------------------|-----------------------------------|
| _Core technology_                       | Envoy                  | Nginx/OpenResty                             | Go (open source)                  |
| _Native Gateway API support_            | Yes                    | Yes                                         | Yes                               |
| _Sync speed (HTTPRoute → live route)_   | Fast                   | Variable                                    | Variable                          |
| _Extensible external authorization_     | Decoupled, flexible    | Plugin-based (OSS and Enterprise)           | ForwardAuth middleware            |
| _Native rate limiting_                  | Yes (local and global) | Basic in OSS, advanced features enterprise  | Basic                             |
| _Configurable timeouts (>30s)_          | Per route / backend    | Plugin-based                                | Limited                           |
| _Prometheus metrics per data-plane pod_ | Yes                    | Yes                                         | Yes                               |
| _OpenTelemetry compatibility_           | Yes                    | Yes                                         | Yes                               |
| _Advanced L7 observability_             | Yes                    | Basic in OSS, enhanced in Enterprise        | Standard (traces, metrics, logs)  |
| _North–south traffic focus_             | Yes                    | Yes                                         | Yes                               |
| _East–west traffic_                     | Via Istio              | Via separate service mesh                   | Via separate service mesh         |
| _Istio Ambient / Waypoint integration_  | Waypoint-ready         | No                                          | No                                |
| _AWS Lambda invocation_                 | Native                 | Via plugins                                 | No (community plugins available)  |
| _Licensing model_                       | Open source            | Open source (OSS) + Enterprise subscription | Open source + Commercial products |
| _Production maturity_                   | Very high (ex-Gloo)    | High                                        | High                              |

### How Xepelin uses kgateway
Today, kgateway is the core of our traffic layer at Xepelin. We use it consistently across production, development, and testing environments, which allows us to keep the same operational model throughout the entire service lifecycle.

When traffic reaches the platform, either through an Application Load Balancer for public traffic or a Network Load Balancer for internal traffic, both flows pass through Envoy proxies in the kgateway data plane. From there, all routing is handled declaratively within Kubernetes.

Applications are managed through an internal developer platform (IDP) that centralizes onboarding and governance. This IDP is responsible for creating HTTPRoute resources and binding them to the appropriate Gateway objects based on environment and traffic type. For application teams, the process is **simple, consistent and self-service**, while gateway complexity is fully abstracted away by the platform.

Synchronization speed is another key advantage. From the moment an HTTPRoute is created or updated, it typically takes only a few seconds for the route to become active. This fast feedback loop significantly improved our service lifecycle, reducing wait times and making deployments more predictable.

Beyond basic routing, we rely on kgateway extensions to control advanced behavior. Using BackendPolicies such as BackendConfigPolicy, we tune Envoy-specific parameters including upstream keep-alives, backend timeouts, and connection handling. We also apply native rate limiting, allowing us to protect services and standardize limits without relying on external systems.

From a security standpoint, we can integrate our own custom external auth service with kgateway. This internally developed service can be enabled and configured per gateway or per route. It allowed us to replicate and evolve the Lambda Authorizer model we used previously, while keeping authorization logic decoupled from the gateway and fully Kubernetes-native.

Overall, this model based on an internal IDP, Gateway API, kgateway, and custom external auth gave us a traffic layer that is **predictable, fast to operate, and easy to scale**. 
Kgateway did not just replace the previous architecture, it became a core platform component that we continue to build on.

{{< reuse-image src="blog/kgateway-at-xepelin-2.svg" caption="Current traffic architecture using kgateway and the Kubernetes Gateway API, with centralized ingress, shared gateways, and declarative routing managed entirely inside Kubernetes." >}}

### How we use kgateway telemetry
We currently use kgateway telemetry across two distinct layers. On one side, we rely on access logs for each gateway. On the other, we consume metrics from both the control plane and the data plane, with most of the focus on the data plane.

#### Metrics
In practice, the metrics we rely on the most are those exposed by Envoy in the data plane, as they provide a clear and accurate picture of how traffic is actually behaving.

We primarily monitor:
- Request counts
- Latencies
- Throughput
- Errors and timeouts
- Envoy response codes and flags

What makes these metrics especially valuable is their **level of granularity**. We can break them down by **backend service, Gateway API resource, environment, and even custom tags**. This is straightforward to achieve thanks to kgateway’s native OpenTelemetry integration, which allows us to enrich telemetry without locking ourselves into a specific observability vendor.

In production, we send these metrics to Datadog. In development and testing environments, we send them to Prometheus and visualize them in Grafana. The model stays the same, only the backend changes.

{{< reuse-image src="blog/kgateway-at-xepelin-3.svg" caption="Datadog dashboards built from Envoy and kgateway metrics, providing detailed visibility into request rates, latencies, errors, and traffic behavior per service." >}}

Through our Grafana dashboards, we can easily drill into response codes and investigate non-200 responses in more detail when needed.

{{< reuse-image src="blog/kgateway-at-xepelin-4.svg" caption="Per-request Envoy access logs from kgateway, including HTTP status codes, request paths, upstream services, and end-to-end request duration." >}}

#### Logs: understanding individual requests
In parallel, we rely heavily on Envoy access logs to gain detailed visibility at the individual request level. Currently, these logs are sent to Amazon CloudWatch, with the option to route them to Loki in the future.
Access logs are critical when something does not look right. Metrics tell you that something is wrong; logs tell you exactly what happened. More than once, Envoy response codes and flags found in access logs helped us determine whether an issue originated in the backend, the gateway, or somewhere in between.

#### Metrics and logs together
In day-to-day operations, the real value comes from using metrics and logs together. Metrics help us detect issues quickly, while logs allow us to understand them in depth.
Having this level of visibility into the traffic layer was a major improvement over our previous architecture and is now a fundamental part of how we operate kgateway in production.

### Cost and operational impact
One of the clearest impacts of adopting kgateway was on both cost and operational overhead.
Before the migration, our model was essentially one application, one Network Load Balancer. As the platform grew, the number of NLBs grew with it, eventually becoming expensive and difficult to manage.

After consolidating traffic through kgateway, we reduced the number of NLBs by approximately **96%**. Instead of provisioning a load balancer per service, we now route multiple applications through a small set of shared entry points.

This change had an immediate impact on infrastructure costs, but the bigger win was operational simplicity. With far fewer NLBs:

- There is less infrastructure to maintain
- Fewer components can break in the traffic path
- Networking per environment is significantly simpler
- Teams spend less time dealing with load balancer-related issues

In practice, kgateway helped us move away from maintaining large amounts of repetitive infrastructure and **focus more on improving the platform itself**. While the cost savings were important, the **reduction in operational effort and complexity was just as valuable**.

### Challenges and lessons learned
Adopting kgateway was very positive overall, but it also came with important lessons that we now consider essential for stable operation.

#### Every backend is different
Each application, seen by Envoy as an upstream, maintains its own connection pool. There is no single configuration that works for everything. Defining well-tuned BackendPolicies per service, including keep-alives, timeouts, and retries, was critical to achieving stable connections and avoiding intermittent errors.

#### Gateway API requires a mindset shift
Coming from traditional Ingress and load balancer models, it takes time to adjust to the Gateway API way of modeling traffic. Concepts like Gateways, HTTPRoutes, and namespace-level delegation are not complex, but they are different. Once the model clicks, things start to make a lot more sense.

#### The community helped a lot
During adoption, we had many questions around both design and implementation. Our experience with the kgateway community was extremely positive—responses were clear and fast, helping us move forward without getting stuck.

#### North–south traffic still requires careful tuning
Even though kgateway abstracts much of the complexity, timeouts and keep-alives still need to be aligned across ALBs, NLBs, Envoy, and backends. When these settings are misaligned, hard-to-debug issues can appear unless strong telemetry is in place.

#### Without telemetry, this would be impossible to operate
Having metrics and logs from day one was critical. On multiple occasions, Envoy telemetry was what allowed us to pinpoint whether an issue lived in the gateway, the backend, or outside the cluster.

#### External auth is flexible, but not trivial
Moving authorization outside the gateway was the right decision, but it requires careful design around latency, timeouts, and resilience. Authorization remains part of the critical request path, and it must be treated as such.

Overall, kgateway solved many structural problems for us, but like any core platform component, it works best when operated with clear practices and good operational discipline. These lessons are now baked into how we design and run the traffic layer at Xepelin.

### Wrapping up
We are very happy with all the features we explored with kgateway, including built-in external authorization, native OpenTelemetry integration, and high-performance routing. We’re also testing the waypoint proxy integration with Istio ambient mesh in a proof-of-concept phase, and so far it has helped us validate our future service mesh architecture. 

We look forward to continuing to work with the kgateway community and exploring the AI gateway capabilities that kgateway is bringing into this space. If you are looking for an alternative for Ingress NGINX, we highly recommend you check out kgateway and reach out to the [community](https://kgateway.dev/slack/) for questions.