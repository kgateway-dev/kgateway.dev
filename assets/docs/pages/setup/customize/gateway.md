Customize your gateway proxy with the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Customize the gateway proxy

Choose between the following options to customize your gateway proxy:

* [Built-in customization](#built-in)
* [Overlays](#overlays)

{{< conditional-text include-if="envoy" >}}
{{< callout type="info" >}}
To change the default proxy template and inject your own Envoy configuration, use a [self-managed gateway]({{< link-hextra path="/setup/customize/selfmanaged/" >}}) instead.
{{< /callout >}}
{{< /conditional-text >}}

### Built-in customization {#built-in}

You can use the built-in customization fields in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to change settings on the proxy. This way, your configuration is validated when you apply the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource in your cluster.

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom configuration. The following example changes the proxy Service type from `LoadBalancer` to `NodePort`. For other examples, see the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       service:
         type: NodePort
   EOF
   ```

2. Create a Gateway resource that references your custom {{< reuse "docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
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
   kubectl get svc custom -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

   Example output:

   ```
   NAME     TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
   custom   NodePort   10.96.123.456   <none>        80:30xxx/TCP   30s
   ```

### Overlays {#overlays}

You can define Kubernetes overlays in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to override default settings for the Deployment, Service, and ServiceAccount that are created for a gateway proxy. Overlays use [Kubernetes strategic merge patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) semantics.

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource with your custom overlay. The following example changes the default replica count from 1 to 3. For other examples, see [Overlay examples]({{< link-hextra path="/setup/customize/configs/" >}}).

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube:
       deploymentOverlay:
         spec:
           replicas: 3
   EOF
   ```

2. Create a Gateway resource that references your custom {{< reuse "docs/snippets/gatewayparameters.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: custom
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: gw-params
         group: {{< reuse "docs/snippets/trafficpolicy-group.md" >}}
         kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
     listeners:
     - protocol: HTTP
       port: 80
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Check the number of gateway proxy pods that are created. Verify that you see 3 replicas.

   ```sh
   kubectl get pods -l app.kubernetes.io/name=custom -n {{< reuse "docs/snippets/namespace.md" >}}
   ```

   Example output:

   ```
   NAME                      READY   STATUS    RESTARTS   AGE
   custom-54975d9598-qrh8v   1/1     Running   0          7s
   custom-54975d9598-tb6qx   1/1     Running   0          7s
   custom-54975d9598-w4cx2   1/1     Running   0          7s
   ```

## Next

[Explore common overlay configurations]({{< link-hextra path="/setup/customize/configs/" >}}) such as deployment replicas, pod scheduling, security contexts, and cloud provider load balancer annotations.

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} gw-params -n {{< reuse "docs/snippets/namespace.md" >}}
```
