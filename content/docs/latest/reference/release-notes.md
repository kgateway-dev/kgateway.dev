---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.1.0 {#v210}

For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.1.0).

### 🔥 Breaking changes {#v21-breaking-changes}

#### Kubernetes Gateway API version v1.4.0

Now, kgateway supports version 1.4.0 of the Kubernetes Gateway API. As part of this change, the BackendTLSPolicy API version in the experimental channel is promoted from `v1alpha3` to `v1`. Before you upgrade kgateway, make sure to upgrade the Kubernetes Gateway API to version 1.4.0.

{{< tabs items="Standard,Experimental" tabTotal= "2" >}}
{{% tab tabName="Standard" %}}
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/standard-install.yaml
```
{{% /tab %}}
{{% tab tabName="Experimental" %}}
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/experimental-install.yaml
```
{{% /tab %}}
{{< /tabs >}}

#### AI Backend API changes {#v21-ai-backend-api-changes}

The AI Backend API is updated to simplify the configuration of various LLM features. For more information, see the [API reference](../api/#aibackend) and [AI guides](../../agentgateway/llm/) docs.

Update your old configuration to the new API style as follows.

**Simpler LLM provider nesting**

LLM providers are now nested directly under the `llm` spec field, removing the previous `llm.provider` field.

{{< tabs items="New llm,Old llm.provider" >}}
{{% tab %}}
```yaml
llm:
  openai:
```
{{% /tab %}}
{{% tab %}}
```yaml
llm:
  provider:
    openai:
```
{{% /tab %}}
{{< /tabs >}}


**Priority groups instead of multipool**

The `priorityGroups` field replaces the `multipool` field with simpler nesting for providers.

{{< tabs items="New priorityGroups,Old multipool" >}}
{{% tab %}}
```yaml
priorityGroups:
- providers:
  - openai:
```
{{% /tab %}}
{{% tab %}}
```yaml
multipool:
  priorities:
    - pool:
        - provider:
            openai:
```
{{% /tab %}}
{{< /tabs >}}

**Overrides are simplified**

Some LLM settings are renamed to remove redundant `Override` prefixes.

{{< tabs items="New priorityGroups,Old multipool" >}}
{{% tab %}}
```yaml
host: foo
port: 8080
path: 
  full: "/foo"
authHeader:
  prefix: foo
  headerName: bar
```
{{% /tab %}}
{{% tab %}}
```yaml
hostOverride:
  host: foo
  port: 8080
pathOverride:
  full: /foo
authHeaderOverride:
  prefix: foo
  headerName: bar
```
{{% /tab %}}
{{< /tabs >}}

#### Route delegation annotation for policy merging {#v21-delegation-policy-merging}

The route delegation feature for policy merging is expanded to reflect its broader role of applying not only to routes, but also to policies. This update includes the following changes:

* The annotation is renamed from `delegation.kgateway.dev/inherited-policy-priority` to the simpler `kgateway.dev/inherited-policy-priority`.
* Now, four values are accepted: `ShallowMergePreferParent`, `ShallowMergePreferChild`, `DeepMergePreferParent`, and `DeepMergePreferChild`. Deep merges apply only to the transformation filter in a TrafficPolicy.
* The default behavior of parent route policies taking precedence over child routes policies is reversed. Now, child routes take precedence, which aligns better with the precedence defaults across other resources in the kgateway and Gateway APIs.

To maintain the previous default behavior of 2.0, update your annotations to `kgateway.dev/inherited-policy-priority: ShallowMergePreferParent`.

To learn more about policy merging, see the [Policy merging](../../about/policies/merging/) docs.

Note that this change does not impact the other delegation annotations:
* `delegation.kgateway.dev/inherit-parent-matcher`
* `delegation.kgateway.dev/label`

#### Deprecated support for AI Gateway and Inference Extension with Envoy

AI Gateway and Inference Extension support for Envoy-based gateway proxies is deprecated and is planned to be removed in version 2.2. If you want to use AI capabilities, use an [agentgateway proxy]({{< link-hextra path="/agentgateway/" >}}) instead.

#### Fail open policy for ExtProc providers

The default fail open policy for ExtProc providers changed from `false` to `true`. Because of that, requests are forwarded to the upstream service, even if the ExtProc server is unavailabe. To change this policy, set the `spec.extProc.failOpen` field to `false` in your GatewayExtension resource. 

#### Helm changes for agentgateway

The Helm value to enable the agentgateway integration changed from `agentGateway` to `agentgateway`. To enable agentgateway, use the following values in your Helm chart: 

```yaml
agentgateway: 
  enabled: true
```

#### Helm changes for waypoints

The kgateway waypoint integration is disabled by default. To enable the integration, use the following values in your Helm chart: 

```yaml
waypoint:
  enabled: true
```

#### `ai.llm.hostOverride.insecureSkipVerify` removed from Backend

The `insecureSkipVerify` flag was removed for AI Backends. To configure this option, use a [BackendConfigPolicy]({{< link-hextra path="/reference/api/#backendconfigpolicy" >}}) instead. 

#### Disable per route policies

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


### 🌟 New features {#v21-new-features}

#### Agentgateway integration {#v21-agentgateway}

Kgateway now supports [agentgateway](https://agentgateway.dev/), an open source, highly available, highly scalable, and enterprise-grade gateway data plane that provides AI connectivity for agents and tools in any environment. For more information, see the [Agentgateway docs](../../agentgateway/).

#### Global policy attachment {#v21-global-policy-attachment}

By default, you must attach policies to resources that are in the same namespace. Now, you can enable a feature to create a "global" namespace for policies. Then, these global policies can attach to resources in any namespace in your cluster through label selectors. For more information, see the [Global policy attachment](../../about/policies/global-attachment/) docs.

#### Weighted routing {#v21-weighted-routing}

Now, you can configure weights for more fine-grained control over your routing rules. This feature is disabled by default. To enable it, see the [Weighted routing]({{< link-hextra path="/traffic-management/weighted-routes/" >}}) docs.

#### Deep merging for extauth and extproc policies {#deep-merge}

You can now apply deep merging for extAuth and extProc policies. In addition, you can use the `kgateway.dev/policy-weight` annotation to determine the priority in which multiple extAuth and extProc policies are merged. For more information, see [Policy priority during merging]({{< link-hextra path="/about/policies/merging/#policy-priority-during-merging" >}}). 

#### Additional proxy pod template customization {#podtemplate}

Gateway proxies are created with a default proxy template that is stored in the default GatewayParameters resource. To change the default settings, you create a custom GatewayParameters resource and deploy a Gateway with it. {{< reuse "docs/snippets/kgateway-capital.md" >}} now has more options to customize the gateway proxies' default pod template, including configuration for `nodeSelectors`,`affinity`, `tolerations`, `topologySpreadConstraints`, and `externalTrafficPolicy`.

For more information, see [Customize the gateway]({{< link-hextra path="/setup/customize/general-steps/" >}}). To find all the values that you can change, see the [PodTemplate reference]({{< link-hextra path="/reference/api/#pod" >}}) in the GatewayParameters API.

#### Header modifier filter for {{< reuse "docs/snippets/trafficpolicy.md" >}} {#header-modifier}

Now, you can apply header request and response modifiers in a {{< reuse "docs/snippets/trafficpolicy.md" >}}. This way, you get more flexible policy attachment options such as a gateway-level policy. For more information, see the [Header control](../../traffic-management/header-control/) docs. Note that this feature is available only for Envoy-based kgateway proxies, not the agentgateway proxy.


#### Horizontal Pod Autoscaling {#hpa}

You can bring your own Horizontal Pod Autoscaler (HPA) plug-in to kgateway. This way, you can automatically scale gateway proxy pods up and down based on certain thresholds, like memory and CPU consumption. For more information, see [Horizontal Pod Autoscaling (HPA)]({{< link-hextra path="/setup/hpa/" >}}).

#### HTTP1.0/0.9 support {#http10}

Configure your gateway proxy to accept the HTTP/1.0 and HTTP/0.9 protocols so that you can support legacy applications. For more information, see [HTTP/1.0 and HTTP/0.9]({{< link-hextra path="/setup/http10/" >}}).

#### Dynamic Forward Proxy {#dfp}

Configure the gateway proxy to use a Dynamic Forward Proxy (DFP) filter to allow the proxy to act as a generic HTTP(S) forward proxy without the need to preconfigure all possible upstream hosts. Instead, the DFP dynamically resolves the upstream host at request time by using DNS.

For more information, see [Dynamic Forward Proxy (DFP)]({{< link-hextra path="/traffic-management/dfp/" >}}).

#### Session affinity {#session-affinity}

You can configure different types of session affinity for your Envoy-based gateway proxies:
* [Change the loadbalancing algorithm]({{< link-hextra path="/traffic-management/session-affinity/loadbalancing/" >}}): By default, incoming requests are forwarded to the instance with the least requests. You can change this behavior and instead use a round robin or random algorithm to forward the request to a backend service.
* [Consistent hashing]({{< link-hextra path="/traffic-management/session-affinity/consistent-hashing/" >}}): Set up soft session affinity between a client and a backend service by using consistent hashing algorithms. 
* [Session persistence]({{< link-hextra path="/traffic-management/session-affinity/session-persistence/" >}}): Set up “strong” session affinity or sticky sessions to ensure that traffic from a client is always routed to the same backend instance for the duration of a session.

#### Enhanced retries and timeout capabilities {#retries-timeouts}

You can now set the following retries and timeouts for your Envoy-based gateway proxies:
* [Request retries]({{< link-hextra path="/resiliency/retry/retry/" >}})
* [Request timeouts]({{< link-hextra path="/resiliency/timeouts/request/" >}})
* [Per-try timeouts]({{< link-hextra path="/resiliency/retry/per-try-timeout/" >}})
* [Idle timeouts]({{< link-hextra path="/resiliency/timeouts/idle/" >}})
* [Idle stream timeouts]({{< link-hextra path="/resiliency/timeouts/idle-stream/" >}})

#### Passive health checks with outlier detection {#outlier-detection}

Configure passive health checks and remove unhealthy hosts from the load balancing pool with an outlier detection policy. An outlier detection policy sets up several conditions, such as retries and ejection percentages, that kgateway uses to determine if a service is unhealthy. When an unhealthy service is detected, the outlier detection policy defines how the service is removed from the pool of healthy destinations to send traffic to. For more information, see [Outlier detection]({{< link-hextra path="/resiliency/outlier-detection/" >}}).

#### New kgateway operations dashboard {#kgateway-dashboard}

When you install the [OTel stack]({{< link-hextra path="/observability/otel-stack/" >}}), you can now leverage the new kgateway operations dashboard for Grafana. This dashboard shows important metrics at a glance, such as the translation and reconciliation time, total number of operations, the number of resources in your cluster, and latency.
      
{{< reuse-image src="img/kgateway-dashboard.png" >}}
{{< reuse-image-dark srcDark="img/kgateway-dashboard.png" >}}

#### Leader election enabled {#kgateway-dashboard}

Leader election is now enabled by default to ensure that you can run kgateway in a multi-control plane replica setup for high availability. 

You can disable leader election by setting the `controller.disableLeaderElection` to `true` in your Helm chart. 

```sh
helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/n-patch.md" >}} kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway --set controller.disableLeaderElection=true
```




<!-- TODO release 2.1

### ⚒️ Installation changes {#v2.1-installation-changes}

### 🔄 Feature changes {#v2.1-feature-changes}

### 🗑️ Deprecated or removed features {#v2.1-removed-features}

### 🚧 Known issues {#v2.1-known-issues}
-->
