---
title: kgateway v2.1 release blog
toc: false
publishDate: 2025-10-10T10:00:00-00:00
author: Nadine Spies, Aryan Parashar, Nina Polshakova
excludeSearch: true
---

We’re excited to announce the release kgateway v2.1, a release packed with exciting new features and improvements. Here are a few select updates the kgateway team would like to highlight!

## 🌟 What's new in kgateway 2.1?

### Agentgateway integration {#v21-agentgateway}

This release marks a major milestone — it’s the first version of integrating the open source project [agentgateway](https://agentgateway.dev/)! Agentgateway is a highly available, highly scalable, and enterprise-grade data plane that provides AI connectivity for LLMs, MCP tools, AI agents, and inference workloads. As part of this evolution, we’re beginning the deprecation of the Envoy-based AI Gateway and Envoy-based Inference Extension, since all related functionality is now implemented natively through agentgateway. You can still continue to use Envoy-based Gateways for API Gateway use cases. 

For this release, agentgateway support is released as a beta. If you’re trying out the `agentgateway` `GatewayClass`, we recommend following the beta release feed to stay up to date with improvements, bug fixes, and breaking changes as the implementation is refined.

To get started with agentgateway, you simply install kgateway with the following Helm values: 
```yaml
agentgateway:
  enabled: true
```

Then you create a Gateway with the `agentgateway` GatewayClass as shown here: 
```yaml
kubectl apply -f- <<EOF
kind: Gateway
apiVersion: gateway.networking.k8s.io/v1
metadata:
  name: agentgateway
  namespace: kgateway-system
  labels:
    app: agentgateway
spec:
  gatewayClassName: agentgateway
  listeners:
  - protocol: HTTP
    port: 8080
    name: http
    allowedRoutes:
      namespaces:
        from: All
EOF
```

You are now ready to try out agentgateway. Check out the [agentgateway guides](/docs/latest/agentgateway/) to learn how to route traffic to an LLM provider, MCP tool server, or AI agent. 

### K8s GW API 1.3.0 and Inference Extension 1.0.0

Kgateway is now fully conformant with the Kubernetes Gateway API version 1.3.0 and Inference Extension version 1.0.0. To learn more, check out the conformance test reports: 

* [Kubernetes Gateway API](https://github.com/kubernetes-sigs/gateway-api/tree/main/conformance/reports/v1.3.0/kgateway)
* [Inference Extension](https://github.com/kubernetes-sigs/gateway-api-inference-extension/tree/main/conformance/reports/v1.0.0/gateway/kgateway)

### Global policy attachment {#v21-global-policy-attachment}

By default, you must attach policies to resources that are in the same namespace. Now, you can enable a feature to create a "global" namespace for policies. Then, these global policies can attach to resources in any namespace in your cluster through label selectors. For more information, see the [Global policy attachment](/docs/latest/about/policies/global-attachment/) docs.

### Weighted routing {#v21-weighted-routing}

Now, you can configure weights for more fine-grained control over your routing rules. This feature is disabled by default. To enable it, see the [Weighted routing](/docs/latest/traffic-management/weighted-routes/) docs.

### Deep merging for extauth and extproc policies {#deep-merge}

You can now apply deep merging for extAuth and extProc policies. In addition, you can use the `kgateway.dev/policy-weight` annotation to determine the priority in which multiple extAuth and extProc policies are merged. For more information, see [Policy priority during merging](/docs/latest/about/policies/merging/#policy-priority-during-merging). 

### Additional proxy pod template customization {#podtemplate}

Kgateway now has more options to customize the gateway proxies' default pod template, including configuration for `nodeSelectors`,`affinity`, `tolerations`, `topologySpreadConstraints`, and `externalTrafficPolicy`.

For more information, see [Customize the gateway](/docs/latest/setup/customize/general-steps/). To find all the values that you can change, see the [PodTemplate reference](/docs/latest/reference/api/#pod) in the GatewayParameters API.

### Header modifier filter for TrafficPolicy {#header-modifier}

Now, you can apply header request and response modifiers in a TrafficPolicy. This way, you get more flexible policy attachment options such as a gateway-level policy. For more information, see the [Header control](/docs/latest/traffic-management/header-control/) docs. Note that this feature is available only for Envoy-based kgateway proxies, not the agentgateway proxy.


### Horizontal Pod Autoscaling {#hpa}

You can bring your own Horizontal Pod Autoscaler (HPA) plug-in to kgateway. This way, you can automatically scale kgateway control and data plane pods up and down based on certain thresholds, like memory and CPU consumption. See [Horizontal Pod Autoscaling (HPA)](/docs/latest/setup/hpa/) for more information.

### HTTP1.0/0.9 support {#http10}

Configure your gateway proxy to [accept the HTTP/1.0 and HTTP/0.9 protocols](/docs/latest/setup/http10/) so that you can support legacy applications.

### Dynamic Forward Proxy {#dfp}

You can now configure the gateway proxy to use a Dynamic Forward Proxy (DFP) filter. This filter allows the proxy to act as a generic HTTP(S) forward proxy without the need to preconfigure all possible upstream hosts. Instead, the DFP dynamically resolves the upstream host at request time by using DNS. Check out [Dynamic Forward Proxy (DFP)](/docs/latest/traffic-management/dfp/) for more information.

### Session affinity {#session-affinity}

You can now configure different types of session affinity for your Envoy-based gateway proxies:
* [Change the default loadbalancing algorithm](/docs/latest/traffic-management/session-affinity/loadbalancing/): By default, incoming requests are forwarded to the instance with the least requests. You can change this behavior and instead use a round robin or random algorithm to forward the request to a backend service.
* [Consistent hashing](/docs/latest/traffic-management/session-affinity/consistent-hashing/): Set up soft session affinity between a client and a backend service by using consistent hashing algorithms. 
* [Session persistence](/docs/latest/traffic-management/session-affinity/session-persistence/): Set up “strong” session affinity or sticky sessions to ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

### Enhanced retries and timeout capabilities {#retries-timeouts}

Retries and timeout capabilities were enhanced for your Envoy-based gateway proxies. Check out the following guides for more information: 

* [Request retries](/docs/latest/resiliency/retry/retry/)
* [Request timeouts](/docs/latest/resiliency/timeouts/request/)
* [Per-try timeouts](/docs/latest/resiliency/retry/per-try-timeout/)
* [Idle timeouts](/docs/latest/resiliency/timeouts/idle/)
* [Idle stream timeouts](/docs/latest/resiliency/timeouts/idle-stream/)

### Passive health checks with outlier detection {#outlier-detection}

You can now configure passive health checks and remove unhealthy hosts from the load balancing pool with an outlier detection policy. An outlier detection policy sets up several conditions, such as retries and ejection percentages, that kgateway uses to determine if a service is unhealthy. When an unhealthy service is detected, the outlier detection policy defines how the service is removed from the pool of healthy destinations to send traffic to. For more information, see [Outlier detection](/docs/latest/resiliency/outlier-detection/).

### New kgateway operations dashboard {#kgateway-dashboard}

When you install the [OTel stack](/docs/latest/observability/otel-stack/), you can now leverage the new kgateway operations dashboard for Grafana. This dashboard shows important metrics at a glance, such as the translation and reconciliation time, total number of operations, the number of resources in your cluster, and latency.
      
{{< reuse-image src="img/kgateway-dashboard.png" >}}
{{< reuse-image-dark srcDark="img/kgateway-dashboard.png" >}}

### Leader election enabled {#kgateway-dashboard}

Leader election is now enabled by default to ensure that you can run kgateway in a multi-control plane replica setup for high availability. 

You can disable leader election by setting the `controller.disableLeaderElection` to `true` in your Helm chart. 

```sh
helm upgrade -i --namespace kgateway-system --version v2.1.0 kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway --set controller.disableLeaderElection=true
```

## 🔥 Breaking changes from the previous release

### Kubernetes Gateway API version v1.4.0

Now, kgateway supports version 1.4.0 of the Kubernetes Gateway API. As part of this change, the BackendTLSPolicy API version in the experimental channel is promoted from `v1alpha3` to `v1`. Before you upgrade kgateway, make sure to upgrade the Kubernetes Gateway API to version 1.4.0.

{{< tabs items="Standard,Experimental"  >}}
{{% tab  %}}
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/standard-install.yaml
```
{{% /tab %}}
{{% tab %}}
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/experimental-install.yaml
```
{{% /tab %}}
{{< /tabs >}}

### AI Backend API changes {#v21-ai-backend-api-changes}
The AI Backend API is updated to simplify the configuration of various LLM features. For more information, see the [API reference](/docs/latest/reference/api/#aibackend) and [AI guides](/docs/latest/agentgateway/llm/) docs.


### Route delegation annotation for policy merging {#v21-delegation-policy-merging}
The route delegation feature for policy merging is expanded to reflect its broader role of applying not only to routes, but also to policies. This update includes the following changes:
* The annotation is renamed from `delegation.kgateway.dev/inherited-policy-priority` to the simpler `kgateway.dev/inherited-policy-priority`.
* Now, the following values are accepted: `ShallowMergePreferParent` and `ShallowMergePreferChild`
* The default behavior of parent route policies taking precedence over child routes policies is reversed. Now, child routes take precedence, which aligns better with the precedence defaults across other resources in the kgateway and Gateway APIs.

To maintain the previous default behavior of 2.0, update your annotations to `kgateway.dev/inherited-policy-priority: ShallowMergePreferParent`. For more information, check out the [Policy merging](/docs/latest/about/policies/merging/) docs.


### Fail open policy for ExtProc providers

The default fail open policy for ExtProc providers changed from `false` to `true`. Because of that, requests are forwarded to the upstream service, even if the ExtProc server is unavailabe. To change this policy, set the `spec.extProc.failOpen` field to `false` in your GatewayExtension resource. 

### Helm changes for agentgateway

The Helm value to enable the agentgateway integration changed from `agentGateway` to `agentgateway`. To enable agentgateway, use the following values in your Helm chart: 

```yaml
agentgateway: 
  enabled: true
```

### Helm changes for waypoints

The kgateway waypoint integration is disabled by default. To enable the integration, use the following values in your Helm chart: 

```yaml
waypoint:
  enabled: true
```

### `ai.llm.hostOverride.insecureSkipVerify` removed from Backend

The `insecureSkipVerify` flag was removed for AI Backends. To configure this option, use a [BackendConfigPolicy](/docs/latest/reference/api/#backendconfigpolicy) instead. 

### Disable per route policies

The configuration for disabling policies on a route changed. Previously, you used the `enablement` field, such as in `extAuth.enablement` to enable or disable a policy on a route. Now, you use the `disable` field instead as shown in the following example: 

```yaml
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
metadata:
  name: disable-all-extauth-for-route-2-1
  namespace: infra
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: route-2
    sectionName: rule1
  extAuth:
    disable: {} 
``` 

Disabling policies can be applied to CORS, extAuth, extProc, and rate limit policies.

##  🗑️ Deprecated or removed features

AI Gateway and Inference Extension support for Envoy-based gateway proxies is deprecated and is planned to be removed in version 2.2. If you want to use AI capabilities, use an [agentgateway proxy](/docs/latest/agentgateway/) instead. To learn more about why we think that agentgateway is better suited as a gateway for agentic AI and MCP workloads, check out this [blog](https://www.solo.io/blog/why-do-we-need-a-new-gateway-for-ai-agents). 

## Release notes
Check out the full details of the kgateway v1.2 release in our [release notes](https://kgateway.dev/docs/latest/reference/release-notes/).

## Availability

Ready to get started? Download the latest release on [GitHub](https://github.com/kgateway-dev/kgateway/releases). Then, check out our [getting started guide](https://kgateway.dev/docs/latest/quickstart/) to install kgateway. 


## Get Involved

The simplest way to get involved with kgateway is by joining our [slack](https://kgateway.dev/slack/) and [community meetings](https://github.com/kgateway-dev/community?tab=readme-ov-file#community-meetings).

Thank you for your continued feedback and support!
