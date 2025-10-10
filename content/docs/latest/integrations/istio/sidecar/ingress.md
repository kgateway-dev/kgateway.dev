---
title: Ingress
weight: 10
--- 

Use {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway to control and secure traffic that enters your service mesh.

A service mesh is a dedicated infrastructure layer that you add your apps to, which ensures secure service-to-service communication across cloud networks. With a service mesh, you can solve problems such as service identity, mutual TLS communication, consistent L7 network telemetry gathering, service resilience, secure traffic routing between services across clusters, and policy enforcement, such as to enforce quotas or rate limit requests. To learn more about the benefits of using a service mesh, see [What is Istio](https://istio.io/latest/docs/overview/what-is-istio/) in the Istio documentation. 

### About Istio

The open source project Istio is the leading service mesh implementation that offers powerful features to secure, control, connect, and monitor cloud-native, distributed applications. Istio is designed for workloads that run in one or more Kubernetes clusters, but you can also extend your service mesh to include virtual machines and other endpoints that are hosted outside your cluster. The key benefits of Istio include: 

* Automatic load balancing for HTTP, gRPC, WebSocket, MongoDB, and TCP traffic
* Secure TLS encryption for service-to-service communication with identity-based authentication and authorization
* Advanced routing and traffic management policies, such as retries, failovers, and fault injection
* Fine-grained access control and quotas
* Automatic logs, metrics, and traces for traffic in the service mesh

### About the sidecar Istio integration

{{< reuse "/docs/snippets/kgateway-capital.md" >}} comes with an Istio integration that allows you to configure your gateway proxy with an Istio sidecar. The Istio sidecar uses mutual TLS (mTLS) to prove its identity and to secure the connection between your gateway and the services in your Istio service mesh. In addition, you can control and secure the traffic that enters the mesh by applying all the advanced routing, traffic management, security, resiliency, and AI capabilities that {{< reuse "/docs/snippets/kgateway.md" >}} offers. 

## About this guide

In this guide, you learn how to use {{< reuse "/docs/snippets/kgateway.md" >}} as an ingress gateway proxy for the workloads in your Istio service mesh. You explore how to enable the Istio sidecar mesh integration in {{< reuse "/docs/snippets/kgateway.md" >}}, set up your ingress gateway proxy with a sidecar, and send secure mutual TLS traffic to the Bookinfo app as illustrated in the following image. 

{{< reuse-image src="img/sidecar-ingress.svg" width="800px" >}}
{{< reuse-image-dark srcDark="img/sidecar-ingress-dark.svg" width="800px" >}}
<!-- source Excalidraw: https://app.excalidraw.com/s/AKnnsusvczX/1HkLXOmi9BF -->

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Set up an Istio service mesh {#istio}

1. Follow the [Istio documentation](https://istio.io/latest/docs/setup/getting-started/) to install Istio in sidecar mode. 
2. Deploy the [Bookinfo sample app](https://istio.io/latest/docs/examples/bookinfo/). 
3. Verify that your Bookinfo apps are up and running. 
   ```sh
   kubectl get pods
   ```

## Step 2: Enable the Istio integration {#istio-integration}

Upgrade your {{< reuse "/docs/snippets/kgateway.md" >}} installation to enable the Istio integration. 

1. Get the Helm values for your current Helm installation. 
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   open {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
2. Add the following values to the Helm values file to enable the Istio integration in {{< reuse "/docs/snippets/kgateway.md" >}}.
   ```yaml

   controller:
     extraEnv:
       KGW_ENABLE_ISTIO_AUTO_MTLS: true
   ```
   
3. Upgrade your Helm installation. This upgrade automatically triggers a restart of any existing gateway proxies to inject `istio-proxy` and `sds` containers.
   
   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "/docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -f {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
   {{< callout type="warning" >}}
   The `istio-proxy` container in the gateway proxy looks for a service that is named `istiod` in the `istio-system` namespace to obtain a valid certificate. Depending on how you installed Istio, you might have a revisioned istiod deployment, such as `istiod-main`, or custom names for the Istio meta cluster ID and meta mesh ID. If this is the case, the `istio-proxy` container cannot deploy successfully. Continue with [Revisioned istiod and custom Istio meta mesh settings](#custom-istio-settings) to configure the `istio-proxy` container to use your custom values. 
   {{< /callout >}}

## Step 3: Update the Istio proxy settings {#custom-istio-settings}

Create a GatewayParameters resource to configure the Istio SDS container to pull the image from the kgateway repository. The steps vary depending on the following scenarios:

* Revisioned istiod deployment, such as `istiod-main`; **or** custom cluster or mesh IDs.
* Revisionless Istio without custom cluster or mesh IDs.

{{< tabs tabTotal="2" items="Revisioned Istio or custom cluster and mesh IDs,Revisionless Istio without custom IDs" >}}
{{% tab tabName="Revisioned Istio or custom cluster and mesh IDs" %}}

Create a GatewayParameters resource to configure the revisioned istiod service address and any custom values for the Istio meta cluster ID and meta mesh ID.

1. Get the name of the istiod service. Depending on how you set up Istio, you might see a service name with a revision, such as `istiod-main`.
   ```sh
   kubectl get services -n istio-system
   ```
   
   Example output: 
   ```                          
   NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                 AGE
   istiod-main   ClusterIP   10.102.24.31   <none>        15010/TCP,15012/TCP,443/TCP,15014/TCP   3h49m
   ``` 

2. Derive the Kubernetes service address for your istiod deployment. The service address uses the format `<service-name>.<namespace>.svc:15012`. For example, if your service name is `istiod-main`, the full service address is `istiod-main.istio-system.svc:15012`.

3. Create a GatewayParameters resource to configure the revisioned istiod service address and any custom values for the Istio meta cluster ID and meta mesh ID. **Note**: If you do not set custom values for the cluster ID and mesh ID, you can omit these values. Then, the default values of `Kubernetes` for the cluster ID and `cluster.local` for the mesh ID are used.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: custom-gw-params
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     kube: 
       istio:
         istioProxyContainer:
           istioDiscoveryAddress: <istiod-service-address> # such as istiod-main.istio-system.svc:15012
           istioMetaClusterId: <cluster-ID> ## such as the cluster name
           istioMetaMeshId: <meta-mesh-ID> ## such as the cluster name
       sdsContainer:
         image:
           registry: cr.kgateway.dev/kgateway-dev
           repository: sds
           tag: v2.1.0-main
   EOF
   ```  
{{% /tab %}}
{{% tab tabName="Revisionless Istio without custom IDs" %}}
Create a GatewayParameters resource to configure the Istio SDS container to pull the image from the kgateway repository.
```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayParameters
metadata:
  name: custom-gw-params
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  kube:
    sdsContainer:
      image:
        registry: cr.kgateway.dev/kgateway-dev
        repository: sds
        tag: v2.1.0-main
EOF
```
{{% /tab %}}
{{< /tabs >}}

## Step 4: Create a gateway proxy {#create-gateway-proxy}

Create or update a Gateway that includes the Istio proxy.

1. Change the `http` gateway from the getting started tutorial to apply the custom settings of the GatewayParameters resource. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     infrastructure:
       parametersRef:
         name: custom-gw-params
         group: gateway.kgateway.dev
         kind: GatewayParameters
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```
   
2. Verify that the gateway proxy is now successfully deployed. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/namespace.md" >}} -l gateway.networking.k8s.io/gateway-name=http \
     -o jsonpath='{range .items[*]}Pod: {.metadata.name} | Status: {.status.phase}{"\n"}Containers:{"\n"}{range .spec.containers[*]}- {.name}{"\n"}{end}{"\n"}{end}'
   ```

   Example output: Note that pod is running and has three containers, including the `istio-proxy`.

   ```
   Pod: http-f7c7f4b78-pwgnt | Status: Running
   Containers:
   - kgateway-proxy
   - sds
   - istio-proxy
   ```

   If you do not see the three containers, try restarting the proxy to apply the latest Gateway settings.

## Step 5: Verify the integration {#verify}

1. Create an HTTPRoute to route requests from the gateway proxy to the productpage app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: bookinfo
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
     - istio-sidecar.example
     rules:
     - matches:
       - path:
           type: PathPrefix
           value: /productpage
       backendRefs:
         - name: productpage
           port: 9080
   EOF
   ```

2. Send a request to the productpage app through the gateway. Verify that you get back a 200 HTTP response code. This response code proves that the gateway proxy can establish a mutual TLS connection to the productpage app. 

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -I http://$INGRESS_GW_ADDRESS:8080/productpage \
   -H "host: istio-sidecar.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -I http://localhost:8080/productpage \
   -H "host: istio-sidecar.example:8080"
   ```   
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```
   HTTP/1.1 200 OK
   content-type: text/html; charset=utf-8
   content-length: 4183
   server: envoy
   x-envoy-upstream-service-time: 29
   x-envoy-decorator-operation: productpage.bookinfo.svc.cluster.local:9080/*
   ```

{{< callout type="info">}}
To exclude a service from using Istio mTLS or to configure your own TLS settings, you can create a static Backend resource for the service and add the `kgateway.dev/disable-istio-auto-mtls` annotation to the Backend. Then, you can apply custom TLS settings by using a BackendTLSPolicy or BackendConfigPolicy.   
{{< /callout >}}

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the HTTPRoute and gateway-related resources. 
   ```sh
   kubectl delete httproute bookinfo
   kubectl delete gatewayparameters custom-gw-params -n {{< reuse "docs/snippets/namespace.md" >}}
   ```
  
2. Restore the http Gateway from the getting started tutorial. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/gatewayclass.md" >}}
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Get the Helm values for your current Helm installation and remove the values that you added in this guide.
   ```sh
   helm get values {{< reuse "/docs/snippets/helm-kgateway.md" >}} -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   open {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```
   
4. Upgrade your Helm installation. 
   ```sh
   helm upgrade -i --namespace {{< reuse "docs/snippets/namespace.md" >}} --version {{< reuse "/docs/versions/helm-version-flag.md" >}} {{< reuse "/docs/snippets/helm-kgateway.md" >}} oci://{{< reuse "/docs/snippets/helm-path.md" >}}/charts/{{< reuse "/docs/snippets/helm-kgateway.md" >}} -f {{< reuse "/docs/snippets/helm-kgateway.md" >}}.yaml
   ```

5. Follow the Istio documentation to [uninstall Istio](https://istio.io/latest/docs/setup/getting-started/#uninstall) and [remove the Bookinfo sample app](https://istio.io/latest/docs/examples/bookinfo/#cleanup).
