---
title: Debug your setup
weight: 15
---

Use built-in tools to troubleshoot issues in your kgateway setup.

{{< reuse "/docs/snippets/kgateway-capital.md" >}} is based on [Envoy proxy](https://www.envoyproxy.io). If you experience issues in your environment, such as policies that are not applied or traffic that is not routed correctly, in a lot of cases, these errors can be observed at the proxy. In this guide you learn how to use the {{< reuse "/docs/snippets/kgateway.md" >}} and Envoy debugging tools to troubleshoot misconfigurations on the gateway.

## Debug your gateway setup

1. Make sure that the {{< reuse "/docs/snippets/kgateway.md" >}} control plane and gateway proxies are running. For any pod that is not running, describe the pod for more details.
   
   ```shell
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
   <!-- TODO: CLI You can do that by using the `{{< reuse "docs/snippets/cli-name.md" >}} check` [command](/docs/reference/cli/glooctl_check/) that quickly checks the health of kgateway deployments, pods, and custom resources, and verifies Gloo resource configuration. Any issues that are found are reported back in the CLI output. 
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
   kubectl get httproute <name> -n <namespace>
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
   
   ```bash
   # {{< reuse "/docs/snippets/kgateway.md" >}} control plane
   kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} deployment/{{< reuse "/docs/snippets/helm-kgateway.md" >}}
   
   # Replace $GATEWAY_NAME with the name of your gateway.
   export GATEWAY_NAME=http
   kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} deployment/$GATEWAY_NAME
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

{{% callout type="info" %}}
Make sure to use the version of `{{< reuse "docs/snippets/cli-name.md" >}}` that matches your installed version.
{{% /callout %}}

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