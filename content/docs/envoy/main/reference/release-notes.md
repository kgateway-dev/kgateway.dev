---
title: Release notes
description: What's new, breaking changes, and bug fixes for each kgateway release.
weight: 100
---

Review the release notes for kgateway. For a detailed list of changes between tags, use the [GitHub Compare changes tool](https://github.com/kgateway-dev/kgateway/compare/).

## 2.5.0

### 🔥 Breaking changes {#v25-breaking-changes}

#### Removed HTTPListenerPolicy CRD {#v25-httplistenerpolicy-removed}

The deprecated HTTPListenerPolicy custom resource definition (CRD) is removed. Versions 2.4.x and earlier install this CRD, and version 2.5.x does not, so the upgrade deletes the CRD from your cluster. Kubernetes then garbage-collects every remaining HTTPListenerPolicy object in the cluster. 

Any HTTPListenerPolicy resource that exists in your cluster at the time of the upgrade is deleted along with the CRD, and the listener configuration that it applied stops taking effect.

**Required action**: Migrate your configuration to the ListenerPolicy resource **before** you upgrade {{< reuse "kgw-docs/snippets/kgateway.md" >}} by moving the policy spec under the `spec.default.httpSettings` block in your ListenerPolicy resource. If you already migrated to the ListenerPolicy in an earlier version, no action is needed. 

1. List the HTTPListenerPolicy resources in your cluster. 
   ```sh
   kubectl get httplistenerpolicies -A
   ```
   
2. For each resource, create an equivalent ListenerPolicy resource. You find the corresponding fields in the `spec.default.httpSettings` block. For more information about the policy and supported fields, see [ListenerPolicy]({{< link path="/reference/api/kgateway/#listenerpolicy" >}}). For the field-by-field mapping, see the [HTTPListenerPolicy to ListenerPolicy migration guide](https://github.com/kgateway-dev/kgateway/blob/main/docs/guides/migrating-httplistenerpolicy-to-listenerpolicy.md) in the kgateway open source project.

3. Confirm that the new resources are accepted and that your listeners behave as expected.
   ```sh
   kubectl get ListenerPolicy <name> -n <namespace> -o yaml
   ```

4. Delete the HTTPListenerPolicy objects. 
   ```sh
   kubectl delete HTTPListenerPolicy <name> -n <namespace>
   ```

5. Continue with the [upgrade]({{< link path="/operations/upgrade/" >}}).

#### SDS sidecar binds to loopback by default {#v25-sds-loopback-bind}

The SDS (Secret Discovery Service) sidecar now binds to `127.0.0.1:8234` (loopback) by default instead of `0.0.0.0:8234`. Previously, any pod on the cluster network could reach the SDS endpoint. Because all consumers of SDS run in the same pod as the sidecar, restricting the bind address to loopback closes this unintended exposure.

If you need to reach the SDS sidecar from outside its pod in a trusted environment, set the `SDS_SERVER_ADDRESS=0.0.0.0:8234` environment variable on the `sds` container. For an example, see [Change the SDS sidecar's pod-network bind address]({{< link-hextra path="/setup/customize/configs/#sds-bind-address" >}}). If you use a custom deployment overlay or manifest that overrides the SDS container's readiness probe, note that the default probe also changed, from a `tcpSocket` check on port 8234 to an `exec` probe that runs `sds healthcheck`, because a TCP probe against the pod IP no longer succeeds against a loopback-only listener.

### 🌟 New features {#v25-new-features}

#### JWT verified token caching {#v25-jwt-cache}

You can now enable Envoy's in-memory cache of successfully verified JWTs by using the `cache` field on a JWT provider in a GatewayExtension resource. For a successfully verified token that is presented more than once, the gateway proxy does not parse the token again, or perform a JWKS lookup and signature verification. Expired tokens are automatically removed from the cache. For more information, see [JWT caching]({{< link-hextra path="/security/jwt/simple/basic/#jwt-caching" >}}).

#### JWT clock skew tolerance {#v25-jwt-clock-skew}

You can now set how much clock drift the gateway tolerates when it verifies the `exp` and `nbf` claims of a JWT, by using the `clockSkew` field on a JWT provider in a GatewayExtension resource. Use this when a token that is still valid at the issuer arrives at the proxy as expired or not-yet-valid, such as when the identity provider runs outside the cluster or on a host with an unsynchronized clock. If unset, the gateway keeps Envoy's default tolerance of 60 seconds. For more information, see [Clock skew tolerance]({{< link-hextra path="/security/jwt/simple/basic/#clock-skew" >}}).

#### Preserve request paths {#v25-preserve-request-paths}
You can now disable Envoy's default path normalization and slash merging on a listener by using the `normalizePath` and `mergeSlashes` fields in the HTTP settings of a ListenerPolicy resource. Disable these settings for backends that depend on the original, unmodified request path, such as S3-compatible object stores that use object keys containing repeated slashes.

For more information, see [Preserve request paths]({{< link-hextra path="/traffic-management/preserve-request-paths/" >}}).

#### Maximum connection duration {#v25-max-connection-duration}
You can now use the `maxConnectionDuration` field to set a maximum connection duration for downstream or upstream connections. 

For more information, see [Maximum connection duration]({{< link-hextra path="/resiliency/timeouts/max-connection-duration/" >}}).

#### Share a local rate limit across Gateway replicas {#v25-share-local-ratelimit}

The {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource now supports the `shareAcrossGateway` field for local rate limiting. By default, each Envoy proxy replica enforces its own local token bucket, so the effective rate increases as the Gateway scales out. Set `shareAcrossGateway` to `true` to divide the token bucket evenly across all Gateway proxy replicas, so the configured rate applies to the Gateway as a whole.

For more information, see [Share a local rate limit across Gateway replicas]({{< link-hextra path="/security/ratelimit/local/#share-across-gateway" >}}).

#### Move the buffer filter before body-reading filters {#v25-buffer-filter-stage}

You can now use the `buffer.filterStage` field on a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource to place the buffer filter at an earlier position in the HTTP filter chain. By default, the buffer filter runs after authentication, authorization, and rate limiting, so a filter that reads the request body first, such as external auth with request-body checks or ExtProc, can prevent `buffer.maxRequestSize` from being enforced. 

For more information, see [Move the buffer filter before body-reading filters]({{< link-hextra path="/traffic-management/buffering/#move-the-buffer-filter-before-body-reading-filters" >}}).

<!--

### ⚒️ Installation changes {#v2.2-installation-changes}

### 🔄 Feature changes {#v2.2-feature-changes}

### 🗑️ Deprecated or removed features {#v2.2-removed-features}

### 🚧 Known issues {#v2.2-known-issues}
-->

