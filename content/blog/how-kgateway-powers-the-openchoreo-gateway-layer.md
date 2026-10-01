---
title: "How OpenChoreo builds a modular gateway layer with kgateway"
toc: false
publishDate: 2026-09-12T00:00:00-00:00
author: Lahiru De Silva
excludeSearch: true
---

## OpenChoreo, and the problem it solves

Kubernetes is an infrastructure API, deliberately designed to be highly flexible for the people operating infrastructure. That same flexibility is exactly what makes it too complex for developers who just want to deploy an application. There's no built-in concept of an application, an environment, a promotion, or an owner. What is missing is a platform abstraction layer that builds these higher-level concepts on top of Kubernetes. Without it, someone has to build that layer, and most organizations end up building it by accident. For example, a Helm chart per team, a CI template that gets copied and mutated, an ingress convention that lives in one engineer's head.

[OpenChoreo](https://openchoreo.dev/) takes a different approach and turns that layer into a product instead of an ongoing integration project. It's a modular, open-source, ready-to-use internal developer platform for Kubernetes, and a CNCF Sandbox project. It defines high-level platform and developer abstractions to hide the infrastructure complexity from the developer, orchestrating Kubernetes and other CNCF and open-source projects underneath. Together, these bring development and architecture guardrails, a Backstage-powered developer portal, application CI/CD, GitOps, and observability into a single, cohesive platform.

## OpenChoreo’s multi-plane architecture and the gateway layer

OpenChoreo is divided into four **planes** to separate concerns and provide architectural flexibility. This separation allows the planes to scale and be isolated independently, while also allowing workload execution to be distributed across different Kubernetes clusters or even different clouds, with centralized control maintained through the control plane. There is a **control plane** that reconciles desired state, one or more **data planes** where workloads run, an optional **workflow plane** for builds, and an optional **observability plane** for logs, metrics, and traces. Each plane can be its own Kubernetes cluster, or several of them can share one, and the control plane never has direct Kubernetes API access to any of them. Connectivity between the control plane and the other planes instead runs through a hub-and-spoke architecture, covered later in this article.

Every plane needs a way to get traffic in. Since each plane can be its own cluster, OpenChoreo doesn't have a single "the gateway". Each plane that needs one runs its own gateway, and each carries a distinctly different responsibility:

- **Control plane**: The gateway here exposes OpenChoreo system services. These include the OpenChoreo REST API and MCP server, the Backstage-based developer portal, and the AI portal assistant.  
- **Data plane**: The gateway application developers actually care about. This is where user applications deployed to OpenChoreo get exposed. A data plane can also have multiple environment-level gateways, each dedicated to a specific environment.  
- **Observability plane**: This gateway also exposes system services rather than user traffic. It fronts the observability plane's own REST APIs, serving logs, metrics, and traces.  
- **Workflow plane**: Has no gateway at all. It executes builds and other automation, has no inbound traffic to serve, and only ever needs to reach *out*. That's covered by the hub-and-spoke architecture explained later in this article.

&nbsp;

```mermaid
flowchart BT
    subgraph cp["Control Plane"]
        gwcp["Gateway\n(System services + TLS passthrough listener)"]
        cgw["OpenChoreo Cluster Gateway\n(Hub;terminates mTLS tunnels)"]
        api["Openchoreo API Server"]
        portal["Backstage Portal"]
        assistant["Portal assistant"]
        gwcp --> api & portal & assistant
        gwcp -. "SNI-routed, TLS passthrough" .-> cgw
    end

    subgraph dp["Data Plane(s)"]
        gwdp["Gateway(s)\n(User Application Traffic)"]
        agentdp["OpenChoreo Cluster Agent\n(Spoke;initiate mTLS tunnels)"]
        teledp["Telemetry Agents"]
        app["User Applications"]
        gwdp --> app
    end

    subgraph wp["Workflow Plane"]
        agentwp["OpenChoreo Cluster Agent\n(Spoke;initiate mTLS tunnels)"]
        telewp["Build Telemetry"]
        buildwf["Build Workflows"]
    end

    subgraph op["Observability Plane"]
        gwop["Gateway\n(Observability APIs + Telemetry ingestion)"]
        agentop["OpenChoreo Cluster Agent\n(Spoke;initiate mTLS tunnels)"]
        observerapi["Observability REST APIs"]
        telemetrysink["Telemetry Sink"]
        gwop --> observerapi
        gwop --> telemetrysink
        gwop ~~~ agentop
    end

    agentdp -- "outbound mTLS WebSocket" --> gwcp
    agentwp -- "outbound mTLS WebSocket" --> gwcp
    agentop -- "outbound mTLS WebSocket" --> gwcp

    teledp -- "publish application logs, metrics, traces" --> gwop
    telewp -- "publish build logs, metrics, traces" --> gwop

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class gwcp,gwdp,gwop gateway;
```
***Figure 1:** Every plane's cluster-agent dials outbound to the control plane gateway, which passes the mTLS tunnel straight through to the cluster-gateway by SNI, undecrypted. Data and workflow planes also publish their telemetry outbound to the observability plane gateway.*

OpenChoreo has built its gateway architecture on top of the [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/) and follows a modular gateway architecture, where any Kubernetes Gateway API implementation can be plugged into OpenChoreo, including kgateway, Traefik, Envoy Gateway, Istio, Cilium Gateway, Nginx Gateway Fabric, and others.

**kgateway** is the default because its maturity and feature set align well with OpenChoreo’s advanced gateway requirements.

## How OpenChoreo uses kgateway

### One controller, multiple gateways, for single-cluster deployments

In the common case, a single-cluster OpenChoreo deployment, typical for evaluation and for right-sized production setups, one kgateway controller reconciles separate `Gateway` objects for the control plane, the data plane, and the observability plane all at once, each living in its own namespace with its own listener configuration, TLS configuration, and hostnames. One controller, several independently configured gateways, with no coordination required between them beyond sharing the same cluster.

&nbsp;

```mermaid
flowchart TB
    apiserver[("Kubernetes API server")]
    kgw["kgateway controller\n(single instance, watches Gateway and\nHTTPRoute across every namespace)"]

    apiserver <-- "watch / reconcile" --> kgw

    subgraph ns_cp["openchoreo-control-plane"]
        gw_cp["Gateway"]
        hr_cp["HTTPRoute(s)"]
        gw_cp --- hr_cp
    end

    subgraph ns_dp["openchoreo-data-plane"]
        gw_dp["Gateway"]
        hr_dp["HTTPRoute(s)"]
        gw_dp --- hr_dp
    end

    subgraph ns_op["openchoreo-observability-plane"]
        gw_op["Gateway"]
        hr_op["HTTPRoute(s)"]
        gw_op --- hr_op
    end

    kgw -- "reconciles" --> gw_cp
    kgw -- "reconciles" --> gw_dp
    kgw -- "reconciles" --> gw_op

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class gw_cp,gw_dp,gw_op,kgw gateway;
```
***Figure 2:** One kgateway controller, watching every namespace, reconciles a separate `Gateway` and its `HTTPRoute`s per plane's namespace.*

### Multiple gateway controllers for multi cluster deployments

For organizations that need stricter isolation, whether for security and compliance reasons, high availability, or to support a hybrid architecture, OpenChoreo planes can be deployed across multiple Kubernetes clusters instead of sharing one. The most distributed setup is four dedicated clusters, one per plane. There are other variations too. The control plane can run in its own cluster while the data, workflow, and observability planes share a second cluster. Or the control plane can run alone, the data and observability planes can share a cluster, and the workflow plane can run in a cluster of its own. Whatever the layout, every cluster gets its own kgateway controller, shared across whichever planes happen to live there.

&nbsp;

```mermaid
flowchart TB

    subgraph s1["Most Distributed"]
        direction LR

        subgraph c1["Cluster A: CP"]
            k1["kgateway<br/>controller"]
            g1["Gateway"]
            k1 --> g1
        end

        subgraph c2["Cluster B: DP"]
            k2["kgateway<br/>controller"]
            g2["Gateway"]
            k2 --> g2
        end

        subgraph c3["Cluster C: WP"]
            n1["No gateway<br/>needed"]
        end

        subgraph c4["Cluster D: OP"]
            k3["kgateway<br/>controller"]
            g3["Gateway"]
            k3 --> g3
        end

        c1 ~~~ c2
        c2 ~~~ c3
        c3 ~~~ c4
    end

    subgraph s2["Control Plane Isolated"]
        direction LR

        subgraph c5["Cluster A: CP"]
            k4["kgateway<br/>controller"]
            g4["Gateway"]
            k4 --> g4
        end

        subgraph c6["Cluster B: DP + WP + OP"]
            k5["kgateway<br/>controller"]
            g5["Gateway (DP)"]
            g6["Gateway (OP)"]

            k5 --> g5
            k5 --> g6
        end

        c5 ~~~ c6
    end

    subgraph s3["Data Plane + Observability Plane Shared"]
        direction LR

        subgraph c7["Cluster A: CP"]
            k6["kgateway<br/>controller"]
            g7["Gateway"]
            k6 --> g7
        end

        subgraph c8["Cluster B: DP + OP"]
            k7["kgateway<br/>controller"]
            g8["Gateway (DP)"]
            g9["Gateway (OP)"]

            k7 --> g8
            k7 --> g9
        end

        subgraph c9["Cluster C: WP"]
            n2["No gateway<br/>needed"]
        end

        c7 ~~~ c8
        c8 ~~~ c9
    end

    s1 ~~~ s2
    s2 ~~~ s3

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class k1,k2,k3,k4,k5,k6,k7,g1,g2,g3,g4,g5,g6,g7,g8,g9 gateway;
```

***Figure 3:** In every one of these layouts, each cluster gets its own kgateway controller, and that single controller is used across whichever planes happen to be deployed in that cluster. The workflow plane never needs one of its own, since it has no inbound traffic to serve.*

### Environment level gateways in a Dataplane

Multiple environments sharing a single data plane can also have a flexible gateway architecture. By default, all the applications in all the environments share the same physical gateway. For isolation, high availability, and scalability, per-environment gateways can be provisioned and configured instead.

Consider three environments, dev, staging, and production, sharing the same Kubernetes cluster. One option is to give each environment its own dedicated gateway, three separate gateways for three environments. Another option is to serve all the lower environments through a single shared gateway, and give production a separate, dedicated gateway of its own.

&nbsp;

```mermaid
flowchart TB
    kgw["kgateway controller\n(single instance, one cluster)"]
    subgraph prodns["production"]
        gwprod["Gateway"]
    end
    subgraph stagens["staging"]
        gwstage["Gateway"]
    end
    subgraph devns["dev"]
        gwdev["Gateway"]
    end
    kgw --> gwdev
    kgw --> gwstage
    kgw --> gwprod

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class kgw,gwdev,gwstage,gwprod gateway;
```

***Figure 4:** Three environments, three dedicated gateways, one kgateway controller.*

&nbsp;

```mermaid
flowchart TB
    kgw["kgateway controller\n(single instance, one cluster)"]
    subgraph prodns["production"]
        gwprod["Gateway\n(dedicated)"]
    end
    subgraph lowerns["dev + staging"]
        gwlower["Gateway\n(shared)"]
    end
    kgw --> gwlower
    kgw --> gwprod

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class kgw,gwlower,gwprod gateway;
```
***Figure 5:** Lower environments share one gateway; production gets a dedicated one.*

### External and internal gateways in a Dataplane

OpenChoreo supports external and internal gateways through the gateway architecture itself, using the Kubernetes Gateway API. The Gateway API’s `Gateway` resource has an `infrastructure` field, and kgateway uses it to configure vendor- and implementation-specific infrastructure, such as the load balancer type, the subnet a load balancer gets provisioned into, and the Kubernetes Service type. For an external gateway, that translates to an internet-facing load balancer. For an internal gateway, it translates to a load balancer placed inside a VPC, or simply a `ClusterIP` Service. The same single-controller, multiple-gateway pattern used everywhere else in OpenChoreo applies here too. One kgateway controller reconciles both the external and the internal `Gateway`.

&nbsp;

```mermaid
flowchart TB
    kgw["kgateway controller\n(single instance, one cluster)"]

    subgraph extgw["External gateway"]
        gwext["Gateway\n(internet-facing load balancer)"]
    end
    subgraph intgw["Internal gateway"]
        gwint["Gateway\n(ClusterIP, or load balancer\ninside an internal VPC)"]
    end

    kgw --> gwext
    kgw --> gwint

    gwext --> extapi["external APIs"]
    gwint --> intapi["internal APIs"]

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class kgw,gwext,gwint gateway;
```

***Figure 6:** One kgateway controller, two gateways per data plane, split by visibility rather than by plane or environment. External consumers reach the external gateway; internal consumers reach the internal gateway, which never needs a public IP at all.*

### TLS passthrough for the hub-and-spoke mTLS tunnels

So far, we've discussed the critical data path where the gateway serves external and internal clients with either system APIs or user-deployed application APIs. The platform layer also has to propagate control signals between the planes which is just as critical as the data path.

In this multi-plane architecture, cluster-agents running in data, observability, and workflow planes connect to the cluster-gateway in the control plane. This connectivity happens over a mTLS WebSocket tunnel, and the control plane kgateway instance performs a TLS passthrough to facilitate it. With `mode: Passthrough`, kgateway never decrypts this traffic. It reads the SNI field in the TLS ClientHello, matches it against the `TLSRoute` hostname, and forwards the raw encrypted bytes straight to the cluster-gateway. This is one of the most critical control-signal flows in the platform.

&nbsp;

```mermaid
flowchart LR
    subgraph dp["Data / workflow / observability plane"]
        agent["cluster-agent\n(mTLS client cert)"]
    end
    subgraph cp["Control plane"]
        kgw["kgateway\nTLS listener: Passthrough\n(SNI match only, no decrypt)"]
        cgw["cluster-gateway\n(terminates mTLS,\nverifies client cert\nagainst per-plane CA)"]
    end
    agent -- "wss:// outbound" --> kgw
    kgw -- "raw TLS bytes" --> cgw

    classDef gateway fill:#6C5CE8,stroke:#4834A6,color:#ffffff,stroke-width:1px;
    class kgw gateway;
```
***Figure 7:** The cluster-agent dials outbound over a WebSocket. The control plane's kgateway listener runs in `Passthrough` mode, so it matches on the SNI field alone and forwards the raw encrypted bytes without ever decrypting them. The cluster-gateway behind it terminates the mTLS session and verifies the client certificate against that plane's CA.*

### TrafficPolicy, and how OpenChoreo Traits encapsulate it

kgateway is a feature-rich gateway that provides many vendor-specific features on top of the Kubernetes Gateway API, such as security, rate limiting, and request/response transformation. These are exposed through the kgateway `TrafficPolicy` resource, which pairs nicely with OpenChoreo Traits.

A Trait attaches to an OpenChoreo component, and lets developers use kgateway functionality via developer abstractions that platform engineers define, without needing to know kgateway, or the Kubernetes Gateway API, exists underneath. With a Trait, a platform engineer can create, delete, or patch any Kubernetes object. That means a platform engineer can template a kgateway `TrafficPolicy` inside a Trait, and expose just a handful of parameters for developers to configure.

Following is an example where a `TrafficPolicy` with rate limits is implemented as a Trait and exposed to developers as high-level rate limit parameters.

```
apiVersion: openchoreo.dev/v1alpha1
kind: ClusterTrait
metadata:
  name: request-rate-limit
spec:
  parametersSchema:
    ocSchema:
      requestsPerUnit: { type: integer, default: 100 }
      unit: { type: string, default: Minute }
  creates:
    - targetPlane: DataPlane
      template:
        apiVersion: gateway.kgateway.dev/v1alpha1
        kind: TrafficPolicy
        metadata:
          name: ${oc_generate_name(metadata.componentName, "rate-limit")}
        spec:
          targetRefs:
            - group: gateway.networking.k8s.io
              kind: HTTPRoute
              name: ${oc_generate_name(metadata.componentName, endpoint.key)}
          rateLimit:
            local:
              tokenBucket:
                maxTokens: ${parameters.requestsPerUnit}
                tokensPerFill: ${parameters.requestsPerUnit}
                fillInterval: ${parameters.unit}
```

A developer attaches it the same way they'd attach any other trait:

```
apiVersion: openchoreo.dev/v1alpha1
kind: Component
metadata:
  name: checkout-service
spec:
  traits:
    - kind: ClusterTrait
      name: request-rate-limit
      parameters:
        requestsPerUnit: 200
```

### More kgateway features OpenChoreo uses

Beyond routing, hub-and-spoke connectivity, and TrafficPolicy-driven policies, OpenChoreo relies on a handful of other kgateway features directly.

**WebSocket support:** A `HTTPListenerPolicy` turns on WebSocket upgrades at the `Gateway` level, enabled on both the control plane and data plane gateways. On the data plane, this lets user components run WebSocket services. On the control plane, several system services need WebSocket connections too. That includes the hub-and-spoke mTLS tunnel itself, since the cluster-agent to cluster-gateway connection is a WebSocket connection.

**Disabled request timeouts and a long stream idle timeout for MCP:** OpenChoreo treats AI agents as first-class citizens. It runs an MCP server in both the control plane and observability plane, used by the OpenChoreo SRE Agent, FinOps Agent, and Portal Assistant Agent. A static `TrafficPolicy` targets the `HTTPRoute` in front of these services and replaces the gateway's default request timeout with a long `streamIdle`, so MCP responses and server-sent-event streams aren't cut off mid-flight.

**Session persistence for sticky sessions:** OpenChoreo lets developers and platform engineers exec into a running pod for troubleshooting, through the OpenChoreo control plane. Both the [`occ` CLI](https://openchoreo.dev/docs/next/getting-started/cli-installation/) and the Backstage Portal support this today. An exec session is sticky by nature, every request in that session has to land on the same backend pod, which is exactly what session persistence of kgateway is for.

## Wrapping up

Across all the use cases, it's evident that kgateway is a critical piece of software in the OpenChoreo platform layer. The use cases range from serving user applications, to serving system services, to handling all the cross-plane communication over mTLS tunnels.

It’s stability, feature-richness, and flexibility have been genuinely impressive to build on, and that's worth appreciating outright. A real shout-out is owed to the kgateway maintainers for that. We're looking forward to adopting even more of its features such as ListenerSet support and HTTPRoute Delegation in OpenChoreo going forward.

## Learn more about OpenChoreo

[What is OpenChoreo | OpenChoreo](https://openchoreo.dev/docs/)

[OpenChoreo Architecture](https://openchoreo.dev/docs/overview/architecture/)

[Developer Abstractions | OpenChoreo](https://openchoreo.dev/docs/concepts/developer-abstractions/)

[Platform Abstractions | OpenChoreo](https://openchoreo.dev/docs/concepts/platform-abstractions/)