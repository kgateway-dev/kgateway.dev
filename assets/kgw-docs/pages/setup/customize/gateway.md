Customize your gateway proxy with the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Customize the gateway proxy

Choose between the following options to customize your gateway proxy:

* [Built-in customization](#built-in)
* [Overlays](#overlays)

{{< conditional-text include-if="envoy" >}}
> [!NOTE]
> To change the default proxy template and inject your own Envoy configuration, use a {{< version include-if="2.1.x,2.2.x" >}}[self-managed gateway]({{< link-hextra path="/setup/selfmanaged/" >}}){{< /version >}}{{< version include-if="2.0.x" >}}[self-managed gateway]({{< link-hextra path="/setup/customize/selfmanaged/" >}}){{< /version >}}{{< version exclude-if="2.0.x,2.1.x,2.2.x" >}}[self-managed gateway]({{< link-hextra path="/setup/customize/envoy/selfmanaged/" >}}){{< /version >}} instead.
{{< /conditional-text >}}

### Built-in customization {#built-in}

You can use the built-in customization fields in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to change settings on the proxy. This way, your configuration is validated when you apply the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource in your cluster.

1. Create a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example changes the following proxy settings:
   * `service.type`: Changes the service type from `LoadBalancer` to `NodePort`
   * `envoyContainer.bootstrap.logformat`: Configures the Envoy application logs to use JSON format. 
   * `envoyContainer.extraArgs`: Adds a custom base ID and enables CPU set threading for the gateway proxy. 
   
   For other examples, see the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     kube:
       service:
         type: NodePort
       envoyContainer:
         bootstrap:
           logFormat:
             json:
               message: "%j"
               level: "%l"
               scope: "%n"
               timestamp: "%Y-%m-%dT%T.%eZ"
         extraArgs:
           - --base-id
           - "7"
           - --cpuset-threads
   EOF
   ```

   The `logFormat` field configures how Envoy formats its application logs (not access logs). Define the variable fields you want by using the [Envoy format flags](https://www.envoyproxy.io/docs/envoy/latest/operations/cli#cmdoption-log-format). You can choose between the following options:
   - `json`: Emit logs in structured JSON format. For more information, see the [Envoy application logs documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/application_logging#printing-logs-in-json-format).
   - `text`: Emit logs in a custom text format. If you omit `logFormat`, Envoy uses `text` as the default format.

2. Create a Gateway resource that references your custom {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "kgw-docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Verify that the proxy Service is of type `NodePort`.

   ```sh
   kubectl get svc custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
   ```

   Example output:

   ```
   NAME     TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
   custom   NodePort   10.96.123.456   <none>        80:30xxx/TCP   30s
   ```

4. Verify that the Envoy application logs are emitted in JSON format.

   ```sh
   kubectl logs -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -l app.kubernetes.io/name=custom --tail=1
   ```

   Example output:

   ```json
   {"message":"all clusters initialized. initializing init manager","timestamp":"yyyy-mm-ddThh:mm:ssZ","scope":"main","level":"info"}
   ```

5. Check the container arguments that are passed to the gateway proxy and verify that you see the custom base ID and CPU set threading. 
   ```sh
   kubectl get deploy/custom -n kgateway-system -o yaml 
   ```

   Example output: 
   ```console {hl_lines=[10,11,12]}
   ...
    spec:
      containers:
      - args:
        - --disable-hot-restart
        - --service-node
        - $(POD_NAME).$(POD_NAMESPACE)
        - --log-level
        - info
        - --base-id
        - "7"
        - --cpuset-threads
   ```

### Overlays {#overlays}

You can define Kubernetes overlays in the {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource to override default settings for the Deployment, Service, and ServiceAccount that are created for a gateway proxy. Overlays use [Kubernetes strategic merge patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) semantics.

1. Create a {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} resource with your custom overlay. The following example sets the minimum time that a new pod must be ready before the Deployment considers it available. `minReadySeconds` does not have a built-in {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} field, so an overlay is appropriate. For other examples, see [Gateway customization examples]({{< link-hextra path="/setup/customize/configs/" >}}).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     kube:
       deploymentOverlay:
         spec:
           minReadySeconds: 10
   EOF
   ```

2. Create a Gateway resource that references your custom {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "kgw-docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "kgw-docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Check the generated Deployment. Verify that the minimum ready time is 10 seconds.

   ```sh
   kubectl get deployment custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o jsonpath='{.spec.minReadySeconds}'
   ```

   Example output:

   ```
   10
   ```

## Next

[Explore gateway customization examples]({{< link-hextra path="/setup/customize/configs/" >}}), such as autoscaling, pod scheduling, security contexts, volumes, load-balancer settings, init containers, and sidecars.

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "kgw-docs/snippets/gatewayparameters.md" >}} gw-params -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
