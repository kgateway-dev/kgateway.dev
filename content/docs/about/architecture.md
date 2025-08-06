---
title: Architecture
weight: 15

---

Learn more about the components that make up {{< reuse "/docs/snippets/kgateway.md" >}}. These components work together to provide traffic management, security, and resiliency for your apps.

## Component architecture

The following image shows the different components that make up the {{< reuse "/docs/snippets/kgateway.md" >}} control and data plane. These components work together to translate gateway custom resources into gateway proxy configuration. The gateway proxy configuration controls the behavior of the gateway proxies that serve your apps.  {{< reuse "/docs/snippets/kgateway-capital.md" >}} supports the Envoy-based kgateway proxy and the agentgateway proxy.

{{< reuse-image src="img/gw-control-plane-components.svg" caption="Component architecture" >}}
{{< reuse-image-dark srcDark="img/gw-control-plane-components-dark.svg" caption="Component architecture" >}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

1. The config and secret watcher components in the `{{< reuse "/docs/snippets/helm-kgateway.md" >}}` pod watch the cluster for new Kubernetes Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} resources, such as Gateways, HTTPRoutes, or TrafficPolicies.
2. When the config or secret watcher detect new or updated resources, it sends the resource configuration to the {{< reuse "/docs/snippets/kgateway.md" >}} translation engine. 
3. The translation engine translates Kubernetes Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} resources into gateway proxy configuration. All gateway proxy configuration is consolidated into an xDS snapshot.
4. The reporter receives a status report for every resource that is processed by the translator. 
5. The reporter writes the resource status back to the etcd data store. 
6. The xDS snapshot is provided to the {{< reuse "/docs/snippets/kgateway.md" >}} xDS server component in the `{{< reuse "/docs/snippets/helm-kgateway.md" >}}` pod. 
7. Gateway proxies in the cluster pull the latest gateway proxy configuration from the {{< reuse "/docs/snippets/kgateway.md" >}} xDS server.
8. Users send a request to the IP address or hostname that the gateway proxy is exposed on. 
9. The gateway proxy uses the listener and route-specific configuration that was provided in the xDS snapshot to perform routing decisions and forward requests to destinations in the cluster.

### Config watcher 

The config watcher component is part of the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and watches the cluster for new or updated Kubernetes Gateway API and {{< reuse "/docs/snippets/kgateway.md" >}} resources, such as Gateways, HTTPRoutes, and Backends. When the config watcher detects new or updated resources, it sends the Kubernetes configuration to the {{< reuse "/docs/snippets/kgateway.md" >}} translation engine.

### Secret watcher

The secret watcher component is part of the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and watches a secret store for updates to secrets. For example, you might use a Kubernetes Secret to store the AWS access key and secret key credentials for a Backend to access an AWS Lambda. However, you can configure {{< reuse "/docs/snippets/kgateway.md" >}} to also watch other secret stores.

<!--
### Endpoint discovery 

The endpoint discovery component is part of the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and watches service registries such as Kubernetes for IP addresses and hostnames that are associated with services. Each endpoint requires its own plug-in that supports the discovery functionality. For example, Kubernetes runs its own endpoint discovery goroutine. When endpoint discovery discovers a new or updated endpoint, the configuration is stored in etcd. -->

### Translation engine

The {{< reuse "/docs/snippets/kgateway.md" >}} translator receives snapshots of all the Kubernetes Gateway API, Kubernetes API, and {{< reuse "/docs/snippets/kgateway.md" >}} resources that you create or update. The translator starts a new translation loop for each update to translate these resources into valid gateway proxy configuration. The gateway proxy configuration is stored in an xDS snapshot.  

The following image shows the different stages of a translation cycle for the different gateway proxies.

{{< tabs items="Envoy-based kgateway proxy, Agentgateway proxy" tabTotal="2" >}}

{{% tab tabName="Envoy-based kgateway proxy" %}}

{{< reuse-image src="img/translation-loop.svg" caption="Kgateway translation cycle" >}}
{{< reuse-image-dark srcDark="img/translation-loop-dark.svg" caption="Kgateway translation cycle" >}}

<!--Source https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF-->

1. The translation cycle starts by defining [Envoy clusters](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/cluster.proto) from all configured Backend and Kubernetes service resources. Clusters in this context are groups of similar hosts. Each Backend has a type that determines how the Backend is processed. Correctly configured Backends and Kubernetes services are converted into Envoy clusters that match their type, including information like cluster metadata.

2. The next step in the translation cycle is to process all the functions on each Backend. Function-specific cluster metadata is added and is later processed by function-specific Envoy filters.

3. In the next step, all [Envoy routes](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/route.proto) are generated. Routes are generated for each route rule that is defined on the HTTPRoute and TrafficPolicy resources. When all of the routes are created, the translator processes and aggregates HTTPListenerPolicy resources into [Envoy virtual hosts](https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/route/v3/route_components.proto#config-route-v3-virtualhost), and adds them to a new [Envoy HTTP Connection Manager](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/http/http_connection_management) configuration. 

4. Filter plug-ins are queried for their filter configurations, generating the list of HTTP and TCP Filters that are added to the [Envoy listeners](https://www.envoyproxy.io/docs/envoy/latest/configuration/listeners/listeners).

5. Finally, an xDS snapshot is composed of the all the valid endpoints (EDS), clusters (CDS), route configs (RDS), and listeners (LDS). The snapshot is sent to the {{< reuse "/docs/snippets/kgateway.md" >}} xDS server. Gateway proxies in your cluster watch the xDS server for new config. When new config is detected, the config is pulled into the gateway proxy. 

{{% /tab %}}

{{% tab tabName="Agentgateway proxy" %}}

<!--{{< reuse-image src="img/translation-loop.svg" caption="Agentgateway translation cycle" >}}
{{< reuse-image-dark srcDark="img/translation-loop-dark.svg" caption="Agentgateway translation cycle" >}}-->

The Agentgateway syncer in kgateway follows this specific order when translating resources:
1. Input Collection Building
Collects all input resources: Namespaces, Services, Secrets, GatewayClasses, Gateways, HTTPRoutes, GRPCRoutes, TCPRoutes, TLSRoutes, ReferenceGrants, ServiceEntries, InferencePools, and Backends
2. Core Collection Processing
GatewayClasses: Processes GatewayClass resources to determine which gateways to handle
ReferenceGrants: Builds reference grants for cross-namespace references
Gateways: Builds gateway collection with listeners and validates against the agentgateway class
3. ADP (Agentgateway Data Plane) Resource Building
The buildADPResources method processes resources in this specific order:
3.1 Binds (Port Bindings)
Groups gateways by port
Creates api.Bind resources for each port/gateway combination
Binds are the foundation for connecting listeners to ports
3.2 Listeners
Creates api.Listener resources from gateway listeners
Sets protocol (HTTP, HTTPS, TCP, TLS) and TLS configuration
Associates listeners with their corresponding binds
3.3 Routes
Route Parents: Builds route parent references from gateways
Route Context: Sets up context with grants, services, namespaces, inference pools, backends, and plugins
Route Translation: Translates different route types:
HTTPRoutes: Converts to api.Route resources with matches, backends, and policies
GRPCRoutes: Converts to api.Route resources for gRPC traffic
TCPRoutes: Converts to api.TCPRoute resources
TLSRoutes: Converts to api.TCPRoute resources for TLS termination
3.4 Policies
Processes attached policies for routes and listeners
Applies policy-specific configurations through plugins
4. Backend Collections
Processes all Backend resources independently (not per-gateway)
Converts Backends to agentgateway-compatible backend configurations
Includes service discovery and endpoint information
5. Address Collections
Builds address configurations for services and workloads
Handles service discovery and endpoint resolution
6. XDS Collection Building
The buildXDSCollection method combines everything:
Merges all ADP resources (binds, listeners, routes, policies) per gateway
Adds backend resources to all gateways
Creates separate resource and address configurations
Generates versioned XDS snapshots
7. Status Reporting
Builds status reports for gateways, listeners, and routes
Tracks attached routes and policy acceptance
8. Final XDS Snapshot
Composes final xDS snapshot with:
ResourceConfig: Contains binds, listeners, routes, policies, and backends
AddressConfig: Contains service and workload addresses
Sends snapshot to agentgateway xDS server
Key Differences from Envoy-based Translation
Unlike the Envoy-based translation you described, the Agentgateway translation:
Starts with binds rather than clusters - binds are the foundation for port binding
Processes listeners early - listeners are created directly from gateway configurations
Handles routes with policy integration - routes are translated with attached policies applied through plugins
Separates backends globally - backends are not per-gateway but shared across all gateways
Uses agentgateway-specific APIs - translates to api.Bind, api.Listener, api.Route, api.TCPRoute rather than Envoy resources
The translation order ensures that dependencies are resolved correctly: binds → listeners → routes → policies, with backends and addresses processed separately and added to the final configuration.

{{% /tab %}}

{{< /tabs >}}

### Reporter

The reporter component receives a validation report for every {{< reuse "/docs/snippets/kgateway.md" >}} resource that was processed by the translator. Any invalid configuration is reported back to the user through the Kubernetes storage layer. Invalid resources are marked as `rejected` and an error message is captured in the resource configuration.  

### xDS Server

The final snapshot is passed to the xDS Server, which notifies the gateway proxy of a successful config update. 

### xDS server

The xDS server is responsible for sending the xDS snapshot to the gateway proxies in the data plane.

* **Envoy-based kgateway proxy**: Updates the Envoy cluster with a new configuration of Envoy EDS, CDS, RDS, and LDS resources to match the desired state.

**Agentgateway proxy:** Updates the agentgateway proxy with agentgateway-specific configuration, including MCP and A2A protocol support, to match the desired state.

<!--

## Discovery architecture

{{< reuse "docs/snippets/discovery-about.md" >}}

To enable automatic discovery of services, see [Discovery](/docs/traffic-management/destination-types/backends/#discovery). To learn more about Backends, see [Backends](/docs/traffic-management/destination-types/backends/).

The following image shows how the endpoint discovery component discovers Kubernetes services and Functions and automatically creates Backend resources for them. 

{{< reuse-image src="img/discovery.svg" >}}

-->

