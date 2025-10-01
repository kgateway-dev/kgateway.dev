---
title: Debug your setup
weight: 15
---

Use built-in tools to troubleshoot issues in your {{< reuse "/docs/snippets/kgateway.md" >}} setup.

{{< reuse "/docs/snippets/kgateway-capital.md" >}} is based on [Envoy proxy](https://www.envoyproxy.io). If you experience issues in your environment, such as policies that are not applied or traffic that is not routed correctly, in a lot of cases, these errors can be observed at the proxy. In this guide you learn how to use the {{< reuse "/docs/snippets/kgateway.md" >}} and Envoy debugging tools to troubleshoot misconfigurations on the gateway.

## Debug the control plane {#control-plane}

1. Enable port-forwarding on the control plane.

   ```sh
   kubectl port-forward deploy/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} 9095
   ```

2. In your browser, open the admin server debugging interface: [http://localhost:9095/](http://localhost:9095/).

   {{< reuse-image src="img/admin-server-debug-ui.png" caption="Figure: Admin server debugging interface.">}}
   {{< reuse-image-dark srcDark="img/admin-server-debug-ui.png" caption="Figure: Admin server debugging interface.">}}

3. Select one of the endpoints to continue debugging. {{< reuse "docs/snippets/review-table.md" >}} 

   | Endpoint | Description |
   | -- | -- |
   | `/debug/pprof` | View the pprof profile of the control plane. A profile shows you the stack traces of the call sequences, such as Go routines, that led to particular events, such as memory allocation. The endpoint includes descriptions of each available profile.|
   | `/logging` | Review the current logging levels of each component in the control plane. You can also interactively set the log level by component, such as to enable `DEBUG` logs. |
   | `/snapshots/krt` | View the current krt snapshot, or the point-in-time view of the transformed Kubernetes resources and their sync status that the control plane processed. These resources are then used to generate gateway configuration that is sent to the gateway proxies for routing decisions. |
   | `/snapshots/xds` | View the current xDS snapshot, or the Envoy-specific configuration (such as Listeners, Routes, Backends, and Workloads) that is being sent to and applied by Envoy gateway proxies. These snapshots show the final translated configuration that Envoy gateway proxies use for routing decisions. |  

## Debug your gateway setup

1. Make sure that the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and gateway proxies are running. For any pod that is not running, describe the pod for more details.
   
   ```shell
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   <!-- TODO: CLI You can do that by using the `{{< reuse "docs/snippets/cli-name.md" >}} check` [command](../../reference/cli/glooctl_check/) that quickly checks the health of kgateway deployments, pods, and custom resources, and verifies Gloo resource configuration. Any issues that are found are reported back in the CLI output. 
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} check
   ```
   
   Example output for a misconfigured VirtualHostOption:
   ```console
   Found rejected VirtualHostOption by '{{< reuse "docs/snippets/namespace.md" >}}': {{< reuse "docs/snippets/namespace.md" >}} jwt (Reason: 2 errors occurred:
	* invalid virtual host [http~bookinfo_example] while processing plugin enterprise_warning: Could not load configuration for the following Enterprise features: [jwt]
   ```
   -->

2. Check the HTTPRoutes for the status of the route and any attached policies.
   
   ```sh
   kubectl get httproutes -A
   ```
   ```sh
   kubectl get httproute <name> -n <namespace> -o yaml
   ```

3. Access the debugging interface of your gateway proxy on your localhost. Configuration might be missing on the gateway or might be applied to the wrong route. For example, if you apply multiple policies to the same route by using the `targetRefs` section, only the oldest policy is applied. The newer policy configuration might be ignored and not applied to the gateway.
   
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000 &  
   ```
   
   * [http://localhost:19000/](http://localhost:19000/)

   {{< reuse-image src="img/gateway-admin-interface.png" caption="Figure: Debugging interface of the gateway proxy.">}}
   {{< reuse-image-dark srcDark="img/gateway-admin-interface.png" caption="Figure: Debugging interface of the gateway proxy.">}}
   
   Common endpoints that can help troubleshoot your setup further, include: 
   | Endpoint | Description| 
   | -- | -- | 
   | config_dump | Get the configuration that is available in the Envoy proxy. Any kgateway resources that you create are translated in to Envoy configuration. Depending on whether or not you enabled resource validation, you might have applied invalid configuration that is rejected Envoy. You can also use `{{< reuse "docs/snippets/cli-name.md" >}} proxy dump` to get the Envoy proxy configuration. | 
   | listeners | See the listeners that are configured on your gateway. | 
   | logging | Review the log level that is set for each component. |  
   | stats/prometheus | View metrics that Envoy emitted and sent to the built-in Prometheus instance. |

4. Review the logs for each component. Each component logs the sync loops that it runs, such as syncing with various environment signals like the Kubernetes API. You can fetch the latest logs for all the components with the following command.

   * If you have not already, [set the log level for the Envoy gateway proxy to `debug`](#gateway-debug-logging).
   
   ```bash
   # {{< reuse "/docs/snippets/kgateway.md" >}} control plane
   kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} deployment/{{< reuse "/docs/snippets/helm-kgateway.md" >}}
   
   # Replace $GATEWAY_NAME with the name of your gateway.
   export GATEWAY_NAME=http
   kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} deployment/$GATEWAY_NAME
   ```

## Set gateway proxy debug logging {#gateway-debug-logging}

You can set the log level for the Envoy proxy to get more detailed logs. Envoy log level options include `trace`, `debug`, `info`, `warn`, `error`, `critical`, and `off`. The default log level is `info`. For more information, see [Debugging Envoy](https://www.envoyproxy.io/docs/envoy/latest/start/quick-start/run-envoy#debugging-envoy).

1. Create a GatewayParameters resource to add any custom settings to the gateway. For other settings, see the [GatewayParameters API docs](../../reference/api/#gatewayparametersspec) or check out the [Gateway customization guides](../../setup/customize/).
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: debug-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube: 
       envoyContainer:
         bootstrap:
           logLevel: debug
   EOF
   ```

2. Create a Gateway resource that references your custom GatewayParameters. 
   
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: debug-gateway
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: debug-gateway
         group: gateway.kgateway.dev
         kind: GatewayParameters       
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that a pod is created for your gateway proxy and that it has the pod settings that you defined in the GatewayParameters resource. 
   
   ```sh
   kubectl get pods -l app.kubernetes.io/name=debug-gateway -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml
   ```
   
4. Create an HTTPRoute that routes traffic to your app through the debug gateway. The following example assumes that you set up the [sample `httpbin` app]({{< link-hextra path="/install/sample-app/" >}}).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin
     namespace: httpbin
   spec:
     parentRefs:
       - name: debug-gateway
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - "debug.com"
     rules:
       - backendRefs:
           - name: httpbin
             port: 8000
   EOF
   ```

5. Get the address of the debug gateway proxy.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   export INGRESS_GW_ADDRESS=$(kubectl get svc -n {{< reuse "docs/snippets/namespace.md" >}} debug-gateway -o=jsonpath="{.status.loadBalancer.ingress[0]['hostname','ip']}")
   echo $INGRESS_GW_ADDRESS
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}} 
   ```sh
   kubectl port-forward deployment/debug-gateway -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
   ```
   {{% /tab %}}
   {{< /tabs >}}

6. Send traffic through the debug gateway proxy.

   {{< tabs items="Cloud Provider LoadBalancer,Port-forward for local testing" tabTotal="2" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: debug.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing"%}}
   ```sh
   curl -i localhost:8080/headers -H "host: debug.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

7. Review the debug logs for the gateway proxy.

   ```sh
   kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} -l app.kubernetes.io/name=debug-gateway
   ```

   Example output:

   ```console
   [2025-07-08 18:59:13.234][34][debug][pool] [external/envoy/source/common/conn_pool/conn_pool_base.cc:254] [Tags: "ConnectionId":"2"] destroying stream: 0 active remaining, readyForStream false, currentUnusedCapacity 1
   [2025-07-08 18:59:14.240][34][debug][connection] [external/envoy/source/common/network/connection_impl.cc:774] [Tags: "ConnectionId":"1"] remote close
   [2025-07-08 18:59:14.241][34][debug][connection] [external/envoy/source/common/network/connection_impl.cc:314] [Tags: "ConnectionId":"1"] closing socket: 0
   [2025-07-08 18:59:14.243][34][debug][conn_handler] [external/envoy/source/common/listener_manager/active_stream_listener_base.cc:136] [Tags: "ConnectionId":"1"] adding to cleanup list
   [2025-07-08 18:59:14.244][1][debug][main] [external/envoy/source/server/server.cc:245] flushing stats
   [2025-07-08 18:59:18.232][34][debug][connection] [external/envoy/source/common/network/connection_impl.cc:774] [Tags: "ConnectionId":"2"] remote close
   [2025-07-08 18:59:18.233][34][debug][connection] [external/envoy/source/common/network/connection_impl.cc:314] [Tags: "ConnectionId":"2"] closing socket: 0
   [2025-07-08 18:59:18.233][34][debug][client] [external/envoy/source/common/http/codec_client.cc:107] [Tags: "ConnectionId":"2"] disconnect. resetting 0 pending requests
   [2025-07-08 18:59:18.234][34][debug][pool] [external/envoy/source/common/conn_pool/conn_pool_base.cc:532] [Tags: "ConnectionId":"2"] client disconnected, failure reason: 
   [2025-07-08 18:59:18.235][34][debug][pool] [external/envoy/source/common/conn_pool/conn_pool_base.cc:500] invoking 1 idle callback(s) - is_draining_for_deletion_=false
   ```

## TrafficPolicy not applied {#trafficpolicy}

As part of debugging, you might have noticed that your HTTPRoute or Gateway had an attached TrafficPolicy. The TrafficPolicy's status might say `Accepted` and seem normal. However, when you checked the gateway configuration, the policy is not applied to the selected routes. Review the following common reasons for missing policies.

1. Verify that the TrafficPolicy is attached correctly. For example, you might use label selectors that do not match any HTTPRoute or Gateway. For more information, see [Policy attachment](../../about/policies/trafficpolicy/#policy-attachment-trafficpolicy).

2. Confirm that you do not have multiple, conflicting policies. In general, the oldest policy is enforced. For more information, see [Policy priority and merging rules](../../about/policies/trafficpolicy/#policy-priority-and-merging-rules).

3. Determine if you need a [Kubernetes ReferenceGrant](https://gateway-api.sigs.k8s.io/api-types/referencegrant/). For example, the TrafficPolicy might rely on a GatewayExtension to enable a feature such as external auth. However, the GatewayExtension might be in a different namespace than the backing external auth service.

   Example ReferenceGrant for [external auth](../../security/external-auth/) GatewayExtension:

   * The GrantExtension for external auth, HTTPRoute, and backing Service are in the app namespace, such as `httpbin`.
   * The external auth service is in the `{{< reuse "docs/snippets/namespace.md" >}}` namespace.

   ```yaml
   apiVersion: gateway.networking.k8s.io/v1beta1
   kind: ReferenceGrant
   metadata:
     name: reference-grant
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     from:
       - group: gateway.kgateway.dev
         kind: GatewayExtension
         namespace: httpbin
     to:
       - group: ""
         kind: Service
   ```

<!-- TODO: CLI
## Before you begin

If you have not done yet, install the `{{< reuse "docs/snippets/cli-name.md" >}}` CLI. The `{{< reuse "docs/snippets/cli-name.md" >}}` CLI is a convenient tool that helps you gather important information about your gateway proxy. To install the `{{< reuse "docs/snippets/cli-name.md" >}}`, you run the following command: 
```sh
curl -sL https://run.solo.io/gloo/install | sh
export PATH=$HOME/.gloo/bin:$PATH
```

{{< callout type="info" >}}
Make sure to use the version of `{{< reuse "docs/snippets/cli-name.md" >}}` that matches your installed version.
{{< /callout >}}

-->

<!-- TODO: CLI
5. Check the proxy configuration that is served by the kgateway xDS server. When you create kgateway resources, these resources are translated into Envoy configuration and sent to the xDS server. If kgateway resources are configured correctly, the configuration must be included in the proxy configuration that is served by the xDS server. 
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} proxy served-config --name http
   ```

6. Review the logs for each component. Each component logs the sync loops that it runs, such as syncing with various environment signals like the Kubernetes API. You can fetch the latest logs for all the components with the following command. 
   ```bash
   {{< reuse "docs/snippets/cli-name.md" >}} debug logs
   # save the logs to a file
   {{< reuse "docs/snippets/cli-name.md" >}} debug logs -f gloo.log
   # only print errors
   {{< reuse "docs/snippets/cli-name.md" >}} debug logs --errors-only
   ```
   
   You can use the `kubectl logs` command to view logs for individual components. 
   ```bash
   kubectl logs -f -n {{< reuse "docs/snippets/namespace.md" >}} -l kgateway=kgateway
   ```

   To follow the logs of other kgateway components, simply change the value of the `gloo` label as shown in the table below.

   | Component | Command |
   | ------------- | ------------- |
   | Gloo control plane | `kubectl logs -f -n {{< reuse "docs/snippets/namespace.md" >}} -l kgateway=kgateway` |
   | kgateway proxy {{< callout type="info" >}}To view logs for incoming requests to your gateway proxy, be sure to <a href="/docs/security/access-logging/" >enable access logging</a> first.{{< /callout >}}| `kubectl logs -f -n {{< reuse "docs/snippets/namespace.md" >}} -l gloo=kube-gateway` |
   | Redis | `kubectl logs -f -n {{< reuse "docs/snippets/namespace.md" >}} -l gloo=redis` |

7. If you still cannot troubleshoot the issue, capture the logs and the state of kgateway in a file. 
   ```bash
   {{< reuse "docs/snippets/cli-name.md" >}} debug logs -f gloo-logs.log
   {{< reuse "docs/snippets/cli-name.md" >}} debug yaml -f gloo-yamls.yaml
   ```
   -->