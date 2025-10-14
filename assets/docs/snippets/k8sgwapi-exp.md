The following features are experimental in the upstream Kubernetes Gateway API project, and are subject to change.

| Feature | Minimum Gateway API version |
| --- | --- |
| [ListenerSets]({{< link-hextra path="/setup/listeners/overview/#listenersets" >}}) | 1.3 |
| [TCPRoutes]({{< link-hextra path="/setup/listeners/tcp/" >}})| 1.3 |
| [BackendTLSPolicy]({{< link-hextra path="/security/backend-tls/" >}})| 1.4 |
| [CORS policies]({{< link-hextra path="/security/cors/" >}}) | 1.2 |
| [Retries]({{< link-hextra path="/resiliency/retry/" >}}) | 1.2 |
| [Session persistence]({{< link-hextra path="/traffic-management/session-affinity/session-persistence" >}}) | 1.3 | 
| [HTTPRoute rule attachment option]({{< link-hextra path="/about/policies/trafficpolicy/#attach-to-rule" >}}) | 1.3 |

**Sample command for version {{< reuse "docs/versions/k8s-gw-version.md" >}}**: Note that some CRDs are prefixed with `X` to indicate that the entire CRD is experimental and subject to change.
     
```sh
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v{{< reuse "docs/versions/k8s-gw-version.md" >}}/experimental-install.yaml
```  
