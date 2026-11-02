---
title: BackendConfigPolicy
weight: 10
description: Configure backend connection, TLS, and load balancing with BackendConfigPolicy.
---

{{< reuse "kgw-docs/pages/about/backendconfigpolicy.md" >}}

## Policy priority and merging rules

If you apply multiple BackendConfigPolicy resources to the same backend, policies are merged at the field level.

The following rules apply:

* If you apply multiple BackendConfigPolicy resources that set the same top-level field, only the oldest policy is enforced for that field. Policies with a later timestamp are ignored for that field. If two policies share the same creation timestamp, they are tie-broken alphabetically by resource name.
* BackendConfigPolicy resources that set different top-level fields are merged and are enforced in combination.
* Native Kubernetes Gateway API policies, such as [BackendTLSPolicy]({{< link-hextra path="/security/backend-tls/" >}}), have higher priority than BackendConfigPolicy for TLS configuration. If both a BackendConfigPolicy and a BackendTLSPolicy target the same backend, the BackendTLSPolicy's TLS settings are enforced and the `spec.tls` field in the BackendConfigPolicy is ignored.

### Multiple BackendConfigPolicies {#multiple-bcps}

The following example shows two BackendConfigPolicy resources that target the same httpbin Service. The `bcp-older` BackendConfigPolicy was created first and sets `connectTimeout` and `upstreamProxyProtocol`. The `bcp-newer` BackendConfigPolicy is created later and sets `connectTimeout` and `circuitBreakers`.

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: bcp-older
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  connectTimeout: 5s
  upstreamProxyProtocol:
    version: V2
---
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: bcp-newer
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  connectTimeout: 99s
  circuitBreakers:
    maxConnections: 1024
    maxPendingRequests: 1024
    maxRequests: 1024
    maxRetries: 3
```

Because both policies set `connectTimeout`, only the value from `bcp-older` is enforced and the value from `bcp-newer` is ignored. Because `circuitBreakers` is only set in `bcp-newer`, it is merged with `bcp-older`'s fields and both are enforced in combination.

| Field | Source | Value enforced |
| -- | -- | -- |
| `connectTimeout` | `bcp-older` | `5s` |
| `upstreamProxyProtocol` | `bcp-older` | `V2` |
| `circuitBreakers` | `bcp-newer` | Merged (not set in `bcp-older`) |

### Conflict with BackendTLSPolicy {#bcp-btp-conflict}

If you apply both a BackendConfigPolicy and a [BackendTLSPolicy]({{< link-hextra path="/security/backend-tls/" >}}) to the same backend, the following rules apply:

* **TLS configuration**: BackendTLSPolicy is enforced. Because BackendTLSPolicy is a native Kubernetes Gateway API resource, it has higher priority than BackendConfigPolicy for TLS. The `spec.tls` field in the BackendConfigPolicy is ignored.
* **Upstream proxy protocol**: If the BackendConfigPolicy sets `upstreamProxyProtocol`, both policies are enforced in combination. The BackendTLSPolicy's TLS socket is placed inside the proxy protocol wrapper, regardless of which policy was created first.
* **All other BackendConfigPolicy fields** (`connectTimeout`, `tcpKeepalive`, `circuitBreakers`, `healthCheck`, `outlierDetection`, `dns`): These fields are not affected by the BackendTLSPolicy and are enforced unchanged.

> [!NOTE]
> When the `spec.tls` field in a BackendConfigPolicy is overridden by a BackendTLSPolicy, an `Overridden` condition is set on the BackendConfigPolicy to inform you of the conflict. To check the condition, run `kubectl get backendconfigpolicy <name> -n <namespace> -o yaml` and look for the following in the status:
>
> ```yaml
> conditions:
> - type: Overridden
>   status: "True"
>   reason: ConflictedWithBackendTLSPolicy
> ```

