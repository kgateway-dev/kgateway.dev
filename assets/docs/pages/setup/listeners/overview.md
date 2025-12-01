Set up listeners on your API Gateway. A listener configures how your API Gateway accepts and processes incoming requests.

In the Kubernetes Gateway API, you can create listeners in two main ways:

* Inline as part of the Gateway resource.
* As a separate resource called a ListenerSet.

## Inline on the Gateway {#inline}

A common, simple approach is to write the listener inline on the Gateway resource. You have the flexibility to write different protocols, ports, and even TLS certificates. Each listener can specify its own hostname, or inherit the hostname of the Gateway. Gateways support up to 64 listeners.

Most examples in both the {{< reuse "docs/snippets/kgateway.md" >}} and Kubernetes Gateway API docs use the inline approach.

## ListenerSets (experimental) {#listenersets}

{{< callout type="warning" >}}
{{< reuse "docs/versions/warn-2-1-only.md" >}} {{< reuse "docs/versions/warn-experimental.md" >}} As such, the ListenerSet CRD is prefixed with `X` to indicate that it is experimental.
{{< /callout >}}

With ListenerSets, you can group together listeners that have their own unique configuration, such as different protocols, ports, hostnames, or TLS settings. Then, the ListenerSet refers to a Gateway, which can be in a different namespace than the ListenerSet. The same Gateway can also have multiple ListenerSets.

Similar to Gateways, ListenerSets can have a maximum of 64 listeners. However, because you can attach multiple ListenerSets to a single Gateway, now a single Gateway can have more than 64 listeners. Keep in mind that more listeners can impact how long it takes to propagate configuration changes on the Gateway. If you have more than 1,000 listeners, consider attaching ListenerSets to multiple Gateways.

### ListenerSet use cases {#listenerset-use-cases}

As such, you might use ListenerSets for the following advantages:

- **Multitenancy**: You can let different teams create their own ListenerSets, but share the same Gateway and backing load balancing infrastructure.
- **Inheritance**: Because ListenerSets inherit routes and policies from the Gateway, you can standardize the configuration of listeners across a multitenant environment. Teams still have the flexibility to overwrite settings in the ListenerSet.
- **Large scale deployments**: By using ListenerSets, Gateways can have more than 64 listeners attached. Teams can also share the same ListenerSet configuration to avoid duplication.
- **Certificates for more listeners per gateway**: Because you can now have more than 64 listeners per Gateway, a single Gateway can forward secured traffic to more backends that might have their own certificates. This approach aligns with projects that might require service-level certificates, such as Istio Ambient Mesh or Knative.

The following diagram presents a simple illustration of how ListenerSets can help you decentralize route configuration in a multitenant environment at scale.

* Team 1 and Team 2 each manage their own Service and HTTPRoute resources within their respective namespaces.
* Each HTTPRoute refers to a namespace-local ListenerSet. This way, each team controls how their routes are exposed, such as the protocol, port, and TLS certificate settings.
* The ListenerSets from both teams share a common Gateway in a separate namespace. A separate Gateway team can setup and manage centralized infrastructure or enforce policies as appropriate.


```mermaid
flowchart TD

  subgraph team1 namespace
    SVC1[Services]
    HR1[HTTPRoutes]
    LS1[ListenerSet]
  end

  subgraph team2 namespace
    SVC2[Services]
    HR2[HTTPRoutes]
    LS2[ListenerSet]
  end

  subgraph shared namespace
    GW[Gateway]
  end

  HR1 -- "parentRef" --> LS1
  LS1 -- "parentRef" --> GW
  HR1 -- "backendRef" --> SVC1

  HR2 -- "parentRef" --> LS2
  LS2 -- "parentRef" --> GW
  HR2 -- "backendRef" --> SVC2
```

### Prerequisites {#prerequisites}

To use ListenerSets, you must have the following environment:

1. Install the Kubernetes Gateway API v{{< reuse "docs/versions/k8s-gw-version.md" >}} or later experimental channel, which includes the `XListenerSet` CRD.
   
   ```sh
   kubectl apply --kustomize "https://github.com/kubernetes-sigs/gateway-api/config/crd/experimental?ref=v{{< reuse "docs/versions/k8s-gw-version.md" >}}"
   ```

2. Follow the [Get Started guide]({{< link-hextra path="/quickstart/" >}}) to install {{< reuse "docs/snippets/kgateway.md" >}}.

3. If you already have a {{< reuse "docs/snippets/kgateway.md" >}} installation, restart the `{{< reuse "docs/snippets/pod-name.md" >}}` deployment to pick up the new CRDs.

   ```sh
   kubectl rollout restart deployment/{{< reuse "docs/snippets/pod-name.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

### More information {#more-info}

The listener setup guides in this section include tabs for examples of using both the inline and ListenerSet approaches.

For more information about ListenerSets, see the [Kubernetes Gateway API docs](https://gateway-api.sigs.k8s.io/geps/gep-1713/).


