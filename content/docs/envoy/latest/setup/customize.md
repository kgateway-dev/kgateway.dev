---
title: Customize the proxy
weight: 20
next: /docs/setup/customize/aws-elb
---

The configuration that is used to spin up a gateway proxy is stored in several custom resources, including {{< reuse "docs/snippets/gatewayparameters.md" >}}, and a gateway proxy template. By default, {{< reuse "docs/snippets/kgateway.md" >}} creates these resources for you during the installation so that you can spin up gateway proxies with the [default proxy configuration]({{< link-hextra path="/setup/default/" >}}). You have the following options to change the default configuration for your gateway proxies: 

| Option | Description | 
| -- | -- | 
| Create your own {{< reuse "docs/snippets/gatewayparameters.md" >}} resource (recommended) | To adjust the settings on the gateway proxy, you can create your own {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. This approach allows you to spin up gateway proxies with different configurations. Keep in mind that you must maintain the {{< reuse "docs/snippets/gatewayparameters.md" >}} resources that you created manually. The values in these resources are not automatically updated during upgrades.  | 
| Change default proxy settings | You can change some of the values for the default gateway proxy updating the values in the {{< reuse "docs/snippets/kgateway.md" >}} Helm chart. The values that you set in your Helm chart are automatically rolled out to the gateway proxies.  |
| Create self-managed gateways with custom proxy templates | If you want to change the [default gateway proxy template]({{< link-hextra path="/setup/default/#gateway-proxy-template" >}}) and provide your own Envoy configuration to bootstrap the proxy with, you must create a self-managed gateway. For more information, see [Self-managed gateways (BYO)]({{< link-hextra path="/setup/customize/selfmanaged" >}}). | 

## Customize the gateway proxy 

The example in this guide uses the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to change settings on the gateway proxy. To find other customization examples, see the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).

1. Create a {{< reuse "docs/snippets/gatewayparameters.md" >}} resource to add any custom settings to the gateway. The following example makes the following changes: 
   
   * The Envoy log level is set to `debug` (default value: `info`).
   * The Kubernetes service type is changed to NodePort (default value: `LoadBalancer`). 
   * The `gateway: custom` label is added to the gateway proxy service that exposes the proxy (default value: `gloo=kube-gateway`). 
   * The `externalTrafficPolicy` is set to `Local` to preserve the original client IP address.  
   * The `gateway: custom` label is added to the gateway proxy pod (default value: `gloo=kube-gateway` ). 
   * The security context of the gateway proxy is changed to use the 50000 as the supplemental group ID and user ID (default values: `10101` ). 
   
   For other settings, see the [API docs]({{< link-hextra path="/reference/api/#gatewayparametersspec" >}}) or check out the [Gateway customization guides]({{< link-hextra path="/setup/customize/" >}}).
   
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/gatewayparameters.md" >}}
   metadata:
     name: custom-gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube: 
       envoyContainer:
         bootstrap:
           logLevel: debug       
       service:
         type: NodePort
         extraLabels: 
           gateway: custom
         externalTrafficPolicy: Local
       podTemplate: 
         extraLabels:
           gateway: custom
         securityContext: 
           fsGroup: 50000
           runAsUser: 50000
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
         name: custom-gw-params
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

3. Verify that a pod is created for your gateway proxy and that it has the pod settings that you defined in the {{< reuse "docs/snippets/gatewayparameters.md" >}} resource. 
   
   ```sh
   kubectl get pods -l app.kubernetes.io/name=custom -n {{< reuse "docs/snippets/namespace.md" >}}   -o yaml
   ```
   
   {{< callout type="info" >}}
   If the pod does not come up, try running `kubectl get events -n kgateway-system` to see if the Kubernetes API server logged any failures. If no events are logged, ensure that the `kgateway` GatewayClass is present in your cluster and that the Gateway resource shows an `Accepted` status. 
   {{< /callout >}}
   
   Example output:
   
   ```yaml {linenos=table,hl_lines=[13,20,21,22],linenostart=1,filename="gateway-pod.yaml"}
   apiVersion: v1
   kind: Pod
   metadata:
     annotations:
       prometheus.io/path: /metrics
       prometheus.io/port: "9091"
       prometheus.io/scrape: "true"
     creationTimestamp: "2024-08-07T19:47:27Z"
     generateName: custom-7d9bf46f96-
     labels:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/name: custom
       gateway: custom
       gateway.networking.k8s.io/gateway-name: custom
       kgateway: kube-gateway
   ...
     priority: 0
     restartPolicy: Always
     schedulerName: default-scheduler
     securityContext:
       fsGroup: 50000
       runAsUser: 50000
   ...
   ```

4. Get the details of the service that exposes the gateway proxy. Verify that the service is of type NodePort and that the extra label was added to the service. 
   
   ```sh
   kubectl get service custom -n kgateway-system -o yaml
   ```
   
   Example output: 
   
   ```yaml {linenos=table,hl_lines=[10,36],linenostart=1,filename="gateway-service.yaml"}
   apiVersion: v1
   kind: Service
   metadata:
     creationTimestamp: "2024-08-07T19:47:27Z"
     labels:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/managed-by: Helm
       app.kubernetes.io/name: custom
       app.kubernetes.io/version: kgateway-proxy-v{{< reuse "docs/versions/n-patch.md" >}}
       gateway: custom
       gateway.networking.k8s.io/gateway-name: custom
       kgateway: kube-gateway
       helm.sh/chart: kgateway-proxy-v{{< reuse "docs/versions/n-patch.md" >}}
     name: custom
     namespace: kgateway-system
     ownerReferences:
     - apiVersion: gateway.networking.k8s.io/v1
       controller: true
       kind: Gateway
       name: custom
       uid: d29417ba-60f9-410c-a023-283b250f3d57
     resourceVersion: "7371789"
     uid: 67945b5f-e55f-42bb-b5f2-c35932659831
   spec:
     ports:
     - name: http
       nodePort: 30579
       port: 80
       protocol: TCP
       targetPort: 8080
     selector:
       app.kubernetes.io/instance: custom
       app.kubernetes.io/name: custom
       gateway.networking.k8s.io/gateway-name: custom
     sessionAffinity: None
     type: NodePort
   ```
   

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete gateway custom -n kgateway-system
kubectl delete {{< reuse "docs/snippets/gatewayparameters.md" >}} custom-gw-params -n kgateway-system
```
   
   