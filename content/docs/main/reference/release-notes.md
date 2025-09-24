---
title: Release notes
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## v2.1.0 {#v210}

<!-- TODO release 2.1 
For more details, review the [GitHub release notes](https://github.com/kgateway-dev/kgateway/releases/tag/v2.1.0).-->

### 🔥 Breaking changes {#v21-breaking-changes}

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

### 🌟 New features {#v21-new-features}

#### Agentgateway integration {#v21-agentgateway}

Kgateway now supports [agentgateway](https://agentgateway.dev/), an open source, highly available, highly scalable, and enterprise-grade gateway data plane that provides AI connectivity for agents and tools in any environment. For more information, see the [Agentgateway docs](../../agentgateway/).

#### Global policy attachment {#v21-global-policy-attachment}

By default, you must attach policies to resources that are in the same namespace. Now, you can enable a feature to create a "global" namespace for policies. Then, these global policies can attach to resources in any namespace in your cluster through label selectors. For more information, see the [Global policy attachment](../../about/policies/global-attachment/) docs.

#### Weighted routing {#v21-weighted-routing}

Now, you can configure weights for more fine-grained control over your routing rules. This feature is disabled by default. To enable it, see the [Weighted routing](/docs/traffic-management/weighted-routes/) docs.

#### Additional proxy pod template customization {#podtemplate}

Gateway proxies are created with a default proxy template that is stored in the default GatewayParameters resource. To change the default settings, you create a custom GatewayParameters resource and deploy a Gateway with it. {{< reuse "docs/snippets/kgateway-capital.md" >}} now has more options to customize the gateway proxies' default pod template, including configuration for `nodeSelectors`,`affinity`, `tolerations`, `topologySpreadConstraints`, and `externalTrafficPolicy`.

For more information, see [Customize the gateway]({{< link-hextra path="/setup/customize/general-steps/" >}}). To find all the values that you can change, see the [PodTemplate reference]({{< link-hextra path="/reference/api/#pod" >}}) in the GatewayParameters API.

#### Header modifier filter for {{< reuse "docs/snippets/trafficpolicy.md" >}} {#header-modifier}

Now, you can apply header request and response modifiers in a {{< reuse "docs/snippets/trafficpolicy.md" >}}. This way, you get more flexible policy attachment options such as a gateway-level policy. For more information, see the [Header control](../../traffic-management/header-control/) docs. Note that this feature is available only for Envoy-based kgateway proxies, not the agentgateway proxy.

<!-- TODO release 2.1

### ⚒️ Installation changes {#v2.1-installation-changes}

### 🔄 Feature changes {#v2.1-feature-changes}

### 🗑️ Deprecated or removed features {#v2.1-removed-features}

### 🚧 Known issues {#v2.1-known-issues}
-->
