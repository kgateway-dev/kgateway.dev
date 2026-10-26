Use a BackendConfigPolicy resource to configure connection settings for a backend.

{{< version exclude-if="2.4.x,2.3.x,2.2.x,2.1.x" >}}
## HTTP CONNECT tunnels {#http-connect-tunnels}

Use the `spec.tunnel` field to send connections from a Static {{< reuse "kgw-docs/snippets/backend.md" >}} through an HTTP CONNECT proxy. The policy must use `spec.targetRefs` to target a {{< reuse "kgw-docs/snippets/backend.md" >}}. Tunnel policies do not support `spec.targetSelectors`.

The following example sends traffic for the `external` Static {{< reuse "kgw-docs/snippets/backend.md" >}} through the `egress-proxy` Service. Only the CONNECT request includes the `Proxy-Authorization` header, and the header value comes from a Secret.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: egress-proxy-credentials
  namespace: httpbin
type: Opaque
stringData:
  authorization: Basic dXNlcjpwYXNz
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
metadata:
  name: external
  namespace: httpbin
spec:
  type: Static
  static:
    hosts:
    - host: external.example.com
      port: 443
---
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: external-egress
  namespace: httpbin
spec:
  targetRefs:
  - group: gateway.kgateway.dev
    kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
    name: external
  tls:
    sni: external.example.com
    wellKnownCACertificates: System
  tunnel:
    proxy:
      backendRef:
        name: egress-proxy
        port: 3128
    headers:
    - name: Proxy-Authorization
      secretRef:
        name: egress-proxy-credentials
        key: authorization
```

| Field | Description |
| -- | -- |
| `spec.targetRefs` | The tunnel policy must target {{< reuse "kgw-docs/snippets/backend.md" >}} resources. The API server rejects a tunnel policy that uses `targetSelectors`. The API server also rejects `targetRefs` that do not reference {{< reuse "kgw-docs/snippets/backend.md" >}} resources. |
| `spec.tls` | Optional. Configures TLS from the gateway proxy to the destination backend. To use TLS to the CONNECT proxy, configure TLS on the proxy backend instead. |
| `spec.tunnel.proxy.backendRef` | Required. References the forward proxy Service or Static {{< reuse "kgw-docs/snippets/backend.md" >}}. For Service references, set `port`. Cross-namespace references require a ReferenceGrant in the proxy namespace. |
| `spec.tunnel.headers` | Optional. Adds up to 16 headers to the CONNECT request only. Each header needs a `name` and exactly one of `value` or `secretRef`. The API server rejects `Host`. |

Tunnels are supported for single-host Static {{< reuse "kgw-docs/snippets/backend.md" >}} destinations. When the destination is not a Static {{< reuse "kgw-docs/snippets/backend.md" >}}, the BackendConfigPolicy reports `Accepted=False` and the backend fails closed. The same failure occurs when the Static {{< reuse "kgw-docs/snippets/backend.md" >}} has more than one host, the tunnel proxy cannot be resolved, or the destination also sets `healthCheck`, `tcpKeepalive`, or `upstreamProxyProtocol`.

{{< /version >}}

## Policy attachment {#policy-attachment-backendconfigpolicy}

You can apply BackendConfigPolicies to individual Kubernetes services, any backend that matches a specific label, or a global service in your ambient mesh.

{{< version exclude-if="2.0.x" >}}
> [!NOTE]
> By default, you must attach policies to resources that are in the same namespace. To create global policies that can attach to resources in any namespace, see the [Global policy attachment](../global-attachment/) guide.
{{< /version >}}

### Individual backend {#attach-to-backend}

You can use the `spec.targetRefs` section in the BackendConfigPolicy resource to apply policies to a specific backend, such as a Kubernetes Service or a {{< reuse "kgw-docs/snippets/backend.md" >}} resource. 

The following example BackendConfigPolicy resource specifies connection settings for the `httpbin` service. 

```yaml 
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy
  namespace: httpbin
spec:
  targetRefs:
    - name: httpbin
      group: ""
      kind: Service
  connectTimeout: 5s
  perConnectionBufferLimitBytes: 1024
```

### Backends with specific label {#label-selector}

Instead of applying the policy to a specific service or {{< reuse "kgw-docs/snippets/backend.md" >}}, you can also use a label selector to apply the policy to all services or {{< reuse "kgw-docs/snippets/backend.md" >}}s that match the label. 

The following example shows a BackendConfigPolicy resource that applies connection settings to all Kubernetes services that have the `app: httpbin` and `service: httpbin` labels. 

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy
  namespace: httpbin
spec:
  targetSelectors:
    - group: networking.istio.io
      kind: Service
      matchLabels:
        app: httpbin
        service: httpbin
  connectTimeout: 5s
  commonHttpProtocolOptions:
    maxHeadersCount: 15
    maxRequestsPerConnection: 100
```

### Global service {#istio-global}

If you use {{< reuse "kgw-docs/snippets/kgateway.md" >}} with an Istio ambient mesh and you exposed services across multiple clusters by using the `solo.io/service-scope=global` label, Istio automatically creates ServiceEntry resources in each of your clusters that use the same global hostname. You can then use the global hostname to send and load balance requests across multiple clusters. 

To apply connection settings to all service instances that are exposed by this global hostname, you can apply a BackendConfigPolicy to an Istio hostname as shown in the following example. 

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: httpbin-policy-alias
  namespace: gwtest
spec:
  targetSelectors:
    - group: networking.istio.io
      kind: Hostname
      matchLabels:
        app: httpbin
        service: httpbin
  connectTimeout: 5s
  commonHttpProtocolOptions:
    maxHeadersCount: 15
    maxRequestsPerConnection: 100
```
