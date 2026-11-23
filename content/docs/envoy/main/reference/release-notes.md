---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.6.0

### 🔥 Breaking changes {#v26-breaking-changes}

#### Stricter BackendConfigPolicy TLS verification {#v26-bcp-tls-verification}

BackendConfigPolicy `tls` settings that skipped backend certificate verification without saying so now verify the certificate or are rejected. Review your policies before you upgrade.

* `insecureSkipVerify` accepts only `true`. To verify the backend certificate, remove the field and set a trust source, such as `wellKnownCACertificates: System`. Existing policies that set `insecureSkipVerify: false` now verify the backend certificate against the system CA certificates, so connections fail if the backend certificate is not signed by a publicly trusted CA.
* `wellKnownCACertificates` accepts only `System`. Existing policies with another value report `Accepted=False`, and the routes that use them are replaced.
* With `wellKnownCACertificates: System`, `sni` set, and no `verifySubjectAltNames`, the backend certificate must now also be valid for the `sni` hostname. Before, only the certificate chain was checked.

For more information, see [Backend TLS]({{< link-hextra path="/security/backend-tls/" >}}).


### 🌟 New features {#v26-new-features}



### ⚒️ Installation changes {#v26-installation-changes}

#### Go runtime sets GOMAXPROCS for the controller {#v26-controller-gomaxprocs}

The `GOMAXPROCS` setting controls how many CPUs the controller uses at the same time. Now, the controller's `GOMAXPROCS` value follows the CPU limit of the controller container, even when the limit changes while the pod runs. For example, if a Vertical Pod Autoscaler (VPA) raises the CPU limit, the controller starts to use the extra CPU without a restart.

Before, the Helm chart set `GOMAXPROCS` once when the pod started. If the CPU limit changed later, the controller kept the old value until the pod restarted.

To use a fixed value instead, set `GOMAXPROCS` in `controller.extraEnv`. A fixed value turns off the automatic updates.

```yaml
controller:
  extraEnv:
    GOMAXPROCS: "4"
```

For more information, see [Controller CPU limit and GOMAXPROCS]({{< link-hextra path="/install/advanced/#controller-gomaxprocs" >}}).


### 🗑️ Deprecated or removed features {#v26-removed-features}

#### Controller reconciliation metrics removed {#v26-controller-reconcile-metrics}

The control plane no longer reports how long each Gateway and GatewayClass reconciliation takes. These metrics added a separate set of series for every Gateway in the cluster, including Gateways that other controllers own.

* The `kgateway_controller_reconcile_duration_seconds` metric is removed.
* The `kgateway_controller_reconciliations_total` metric no longer has the `name` and `namespace` labels. It keeps the `controller` and `result` labels.

If your dashboards or alerts use the removed metric or filter `kgateway_controller_reconciliations_total` by `name` or `namespace`, update them before you upgrade. The [kgateway operations dashboard]({{< link-hextra path="/observability/otel-stack/" >}}) no longer has the Reconciliation Latency panel.

For more information, see [kgateway-dev/kgateway#14836](https://github.com/kgateway-dev/kgateway/pull/14836).

<!--

### 🔄 Feature changes {#v2.2-feature-changes}

### 🚧 Known issues {#v2.2-known-issues}
-->
