Use a BackendConfigPolicy resource to configure connection settings for a backend.  

{{< callout type="warning" >}} 
{{< reuse "docs/versions/warn-2-1-only.md" >}} {{< reuse "docs/versions/warn-experimental.md" >}}
{{< /callout >}}

## Policy attachment {#policy-attachment-backendconfigpolicy}

You can apply BackendConfigPolicies to individual backend services, any backend that matches a specific label, or a global service in your ambient mesh.

{{< callout type="info" >}}
By default, you must attach policies to resources that are in the same namespace. To create global policies that can attach to resources in any namespace, see the [Global policy attachment](../global-attachment/) guide.
{{< /callout >}}

### Individual backend {#attach-to-backend}

You can use the `spec.targetRefs` section in the BackendConfigPolicy resource to apply policies to a specific backend, such as a Kubernetes Service or a Backend resource. 

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

Instead of applying the policy to a specific backend, you can also use a label selector to apply the policy to all backends that match the label. 

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

If you use kgateway with an Istio ambient mesh and you exposed services across multiple clusters by using the `solo.io/service-scope=global` label, Istio automatically creates ServiceEntry resources in each of your clusters that use the same global hostname. You can then use the global hostname to send and load balance requests across multiple clusters. 

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
