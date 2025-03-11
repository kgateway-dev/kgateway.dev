---
title: Debug your setup
weight: 15
---

Use built-in tools to troubleshoot issues in your {{< reuse "docs/snippets/product-name.md" >}} setup.

{{< reuse "docs/snippets/product-name-caps.md" >}} is based on [Envoy proxy](https://www.envoyproxy.io). If you experience issues in your environment, such as policies that are not applied or traffic that is not routed correctly, in a lot of cases, these errors can be observed at the proxy. In this guide you learn how to use the {{< reuse "docs/snippets/product-name.md" >}} and Envoy debugging tools to troubleshoot misconfigurations on the gateway.

## Debug your gateway setup

1. Make sure that the {{< reuse "docs/snippets/product-name.md" >}} control plane and gateway proxies are running. For any pod that is not running, describe the pod for more details.
   
   ```shell
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}}
   ```
   <!-- TODO: CLI You can do that by using the `{{< reuse "docs/snippets/cli-name.md" >}} check` [command](/docs/reference/cli/glooctl_check/) that quickly checks the health of {{< reuse "docs/snippets/product-name.md" >}} deployments, pods, and custom resources, and verifies Gloo resource configuration. Any issues that are found are reported back in the CLI output. 
   ```sh
   {{< reuse "docs/snippets/cli-name.md" >}} check
   ```
   
   Example output for a misconfigured VirtualHostOption:
   ```console
   Found rejected VirtualHostOption by '{{< reuse "docs/snippets/ns-system.md" >}}': {{< reuse "docs/snippets/ns-system.md" >}} jwt (Reason: 2 errors occurred:
	* invalid virtual host [http~bookinfo_example] while processing plugin enterprise_warning: Could not load configuration for the following Enterprise features: [jwt]
   ```
   -->

2. Check the HTTPRoutes for the status of the route and any attached policies.
   
   ```sh
   kubectl get httproute <name> -n <namespace>
   ```

3. Access the debugging interface of your gateway proxy on your localhost. Configuration might be missing on the gateway or might be applied to the wrong route. For example, if you apply multiple policies to the same route by using the `targetRefs` section, only the oldest policy is applied. The newer policy configuration might be ignored and not applied to the gateway.
   
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/ns-system.md" >}} 19000 &  
   ```
   
   * [http://localhost:19000/](http://localhost:19000/)

   {{< reuse-image src="img/gateway-admin-interface.png" caption="Figure: Debugging interface of the gateway proxy.">}}
   
   Common endpoints that can help troubleshoot your setup further, include: 
   | Endpoint | Description| 
   | -- | -- | 
   | config_dump | Get the configuration that is available in the Envoy proxy. Any {{< reuse "docs/snippets/product-name.md" >}} resources that you create are translated in to Envoy configuration. Depending on whether or not you enabled resource validation, you might have applied invalid configuration that is rejected Envoy. You can also use `{{< reuse "docs/snippets/cli-name.md" >}} proxy dump` to get the Envoy proxy configuration. | 
   | listeners | See the listeners that are configured on your gateway. | 
   | logging | Review the log level that is set for each component. |  
   | stats/prometheus | View metrics that Envoy emitted and sent to the built-in Prometheus instance. |

4. Review the logs for each component. Each component logs the sync loops that it runs, such as syncing with various environment signals like the Kubernetes API. You can fetch the latest logs for all the components with the following command. 
   
   ```bash
   # kgateway control plane
   kubectl logs -n {{< reuse "docs/snippets/ns-system.md" >}} deployment/kgateway
   
   # Replace $GATEWAY_NAME with the name of your gateway.
   kubectl logs -n {{< reuse "docs/snippets/ns-system.md" >}} deployment/$GATEWAY_NAME
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
5. Check the proxy configuration that is served by the {{< reuse "docs/snippets/product-name.md" >}} xDS server. When you create {{< reuse "docs/snippets/product-name.md" >}} resources, these resources are translated into Envoy configuration and sent to the xDS server. If {{< reuse "docs/snippets/product-name.md" >}} resources are configured correctly, the configuration must be included in the proxy configuration that is served by the xDS server. 
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
   kubectl logs -f -n {{< reuse "docs/snippets/ns-system.md" >}} -l kgateway=kgateway
   ```

   To follow the logs of other {{< reuse "docs/snippets/product-name.md" >}} components, simply change the value of the `gloo` label as shown in the table below.

   | Component | Command |
   | ------------- | ------------- |
   | Gloo control plane | `kubectl logs -f -n {{< reuse "docs/snippets/ns-system.md" >}} -l kgateway=kgateway` |
   | {{< reuse "docs/snippets/product-name.md" >}} proxy {{< callout type="info" >}}To view logs for incoming requests to your gateway proxy, be sure to <a href="/docs/security/access-logging/" >enable access logging</a> first.{{< /callout >}}| `kubectl logs -f -n {{< reuse "docs/snippets/ns-system.md" >}} -l gloo=kube-gateway` |
   | Redis | `kubectl logs -f -n {{< reuse "docs/snippets/ns-system.md" >}} -l gloo=redis` |

7. If you still cannot troubleshoot the issue, capture the logs and the state of {{< reuse "docs/snippets/product-name.md" >}} in a file. 
   ```bash
   {{< reuse "docs/snippets/cli-name.md" >}} debug logs -f gloo-logs.log
   {{< reuse "docs/snippets/cli-name.md" >}} debug yaml -f gloo-yamls.yaml
   ```
   -->