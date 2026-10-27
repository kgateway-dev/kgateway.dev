{{< version include-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
The following features are experimental in the upstream Kubernetes Gateway API project, and are subject to change.

| Feature | Minimum Gateway API version |
| --- | --- |
| [ListenerSets]({{< link-hextra path="/setup/listeners/overview/#listenersets" >}}) | 1.3 |
| [TCPRoutes]({{< link-hextra path="/setup/listeners/tcp/" >}}) | 1.3 |
| [BackendTLSPolicy]({{< link-hextra path="/security/backend-tls/" >}}) | 1.4 |
| [CORS policies]({{< link-hextra path="/security/cors/" >}}) | 1.2 |
| [Retries]({{< link-hextra path="/resiliency/retry/" >}}) | 1.2 |
| [Session persistence]({{< link-hextra path="/traffic-management/session-affinity/session-persistence" >}}) | 1.3 |
| [HTTPRoute rule attachment option]({{< link-hextra path="/about/policies/trafficpolicy/#attach-to-rule" >}}) | 1.3 |
{{< /version >}}

{{< version exclude-if="2.0.x,2.1.x,2.2.x,2.3.x,2.4.x" >}}
The following feature is experimental in the upstream Kubernetes Gateway API project, and is subject to change. Features that are in the standard channel, such as ListenerSets, TCPRoutes, CORS policies, and retries, do not require the experimental channel.

| Feature | Minimum Gateway API version |
| --- | --- |
| [Session persistence in HTTPRoutes]({{< link-hextra path="/traffic-management/session-affinity/session-persistence" >}}) | 1.3 |
{{< /version >}}

{{< version exclude-if="2.0.x,2.1.x" >}}
> [!NOTE]
> **Experimental feature gate**: In kgateway version 2.2 and later, experimental Gateway API features are enabled by default. The `KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES` environment variable on the kgateway controller deployment defaults to `true`. To disable these features, set the variable to `false` in your Helm values:
>
> ```yaml
> controller:
>   extraEnv:
>     KGW_ENABLE_EXPERIMENTAL_GATEWAY_API_FEATURES: "false"
> ```
{{< /version >}}

**Sample command for version {{< reuse "kgw-docs/versions/k8s-gw-version.md" >}}**: Note that some CRDs are prefixed with `X` to indicate that the entire CRD is experimental and subject to change.
    
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "kgw-docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
```
