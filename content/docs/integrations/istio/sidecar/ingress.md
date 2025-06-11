---
title: Ingress
weight: 10
description: Use your kgateway as the ingress gateway to control and secure traffic that enters your service mesh.
--- 

Use your kgateway as the ingress gateway to control and secure traffic that enters your service mesh.

A service mesh is a dedicated infrastructure layer that you add your apps to, which ensures secure service-to-service communication across cloud networks. With a service mesh, you can solve problems such as service identity, mutual TLS communication, consistent L7 network telemetry gathering, service resilience, secure traffic routing between services across clusters, and policy enforcement, such as to enforce quotas or rate limit requests. To learn more about the benefits of using a service mesh, see [What is Istio](https://istio.io/latest/docs/overview/what-is-istio/) in the Istio documentation. 

### About Istio

The open source project Istio is the leading service mesh implementation that offers powerful features to secure, control, connect, and monitor cloud-native, distributed applications. Istio is designed for workloads that run in one or more Kubernetes clusters, but you can also extend your service mesh to include virtual machines and other endpoints that are hosted outside your cluster. The key benefits of Istio include: 

* Automatic load balancing for HTTP, gRPC, WebSocket, MongoDB, and TCP traffic
* Secure TLS encryption for service-to-service communication with identity-based authentication and authorization
* Advanced routing and traffic management policies, such as retries, failovers, and fault injection
* Fine-grained access control and quotas
* Automatic logs, metrics, and traces for traffic in the service mesh

### About the kgateway Istio integration

Kgateway comes with an Istio integration that allows you to configure your gateway proxy with an Istio sidecar. The Istio sidecar uses mutual TLS (mTLS) to prove its identity and to secure the connection between your gateway and the services in your Istio service mesh. In addition, you can control and secure the traffic that enters the mesh by applying all the advanced routing, traffic management, security, resiliency, and AI capabilities that kgateway offers. 

## About this guide

In this guide, you learn how to use kgateway as an ingress gateway proxy for the workloads in your Istio service mesh. You explore how to enable the Istio sidecar mesh integration in kgateway, set up your ingress gateway proxy with a sidecar, and send secure mutual TLS traffic to the httpbin app as illustrated in the following image. 

{{< reuse-image src="img/sidecar-ingress.svg" width="800px" >}}
{{< reuse-image-dark srcDark="img/sidecar-ingress.svg" width="800px" >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Set up an Istio service mesh

1. Follow the [Istio documentation](https://istio.io/latest/docs/setup/getting-started/) to install Istio in sidecar mode. 
2. Deploy the [Bookinfo sample app](https://istio.io/latest/docs/examples/bookinfo/). 
3. Verify that your Bookinfo apps are up and running. 
   ```sh
   kubectl get pods -n bookinfo
   ```

## Step 2: Enable the Istio integration in kgateway

Upgrade your kgateway installation to enable the Istio integration. 

1. Get the Helm values for your current kgateway installation. 
   ```sh
   helm get values kgateway -n kgateway-system -o yaml > kgateway.yaml
   open kgateway.yaml
   ```
   
2. Add the following values to the Helm values file to enable the Istio integration in kgateway.
   ```yaml
   controller:
     extraEnv:
       KGW_ENABLE_ISTIO_AUTO_MTLS: true
   ```
   
3. Upgrade your kgateway installation. This upgrade automatically triggers a restart of any existing gateway proxies to inject `istio-proxy` and `sds` containers.
   
   ```sh
   helm upgrade -i --namespace kgateway-system --version v2.0.0-main kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway -f kgateway.yaml
   ```

4. Check that the gateway proxy automatically restarts with two additional containers, `istio-proxy` and `sds`. 
   ```sh
   kubectl get pods -n kgateway-system
   ```
   
   {{< callout type="warning" >}}
   The `istio-proxy` container in the gateway proxy looks for a service that is named `istiod` in the `istio-system` namespace to obtain a valid certificate. Depending on how you installed Istio, you might have a revisioned istiod deployment, such as `istiod-main`, or custom names for the Istio meta cluster ID and meta mesh ID. If this is the case, the `istio-proxy` container cannot deploy successfully. Continue with [Revisioned istiod and custom Istio meta mesh settings](#custom-istio-settings) to configure the `istio-proxy` container to use your custom values. 
   {{< /callout >}}
   

### Revisioned istiod and custom Istio meta mesh settings {#custom-istio-settings}

If you installed Istio with a revision, or you set up a custom Istio meta cluster ID and meta mesh, you must create a GatewayParameters resource to change the default Istio settings on your gateway proxy. 

{{< callout type="info" >}}
If you have a revisionless istiod setup and did not customize the Istio meta cluster ID or meta mesh ID, you can skip this step and continue with [Step 3: Verify the integration](#verify). 
{{< /callout >}}

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

3. Create a GatewayParameters resource to configure the revisioned istiod service address and any custom values for the Istio meta cluster ID and meta mesh ID.
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     name: custom-gw-params
     namespace: kgateway-system
   spec:
     kube: 
       istio:
         istioProxyContainer:
           istioDiscoveryAddress: <istiod-service-address> # such as istiod-main.istio-system.svc:15012
           istioMetaClusterId: <cluster-ID> ## such as the cluster name
           istioMetaMeshId: <meta-mesh-ID> ## such as the cluster name
   EOF
   ```
      
4. Change the `http` gateway from the getting started tutorial to apply the custom settings of the GatewayParameters resource. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: kgateway-system
   spec:
     gatewayClassName: kgateway
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
   
5. Verify that the gateway proxy is now successfully deployed. You might need to restart the proxy to apply the latest Gateway settings. 
   ```sh
   kubectl get pods -n kgateway-system
   ```

## Step 3: Verify the integration {#verify}

1. Create an HTTPRoute to route requests from the gateway proxy to the productpage app. 
   ```yaml
   kubectl apply -n bookinfo -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: bookinfo
   spec:
     parentRefs:
     - name: http
       namespace: kgateway-system
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
   ```sh
   curl -I http://$INGRESS_GW_ADDRESS:8080/productpage \
   -H "host: istio-sidecar.example:8080"
   ```
   
   Example output: 
   ```
   HTTP/1.1 200 OK
   content-type: text/html; charset=utf-8
   content-length: 4183
   server: envoy
   x-envoy-upstream-service-time: 29
   x-envoy-decorator-operation: productpage.bookinfo.svc.cluster.local:9080/*
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Delete the HTTPRoute and gateway-related resources. 
   ```sh
   kubectl delete httproute bookinfo -n bookinfo
   kubectl delete gatewayparameters custom-gw-params -n kgateway-system
   ```
  
2. Restore the http Gateway from the getting started tutorial. 
   ```yaml
   kubectl apply -f- <<EOF
   kind: Gateway
   apiVersion: gateway.networking.k8s.io/v1
   metadata:
     name: http
     namespace: kgateway-system
   spec:
     gatewayClassName: kgateway
     listeners:
     - protocol: HTTP
       port: 8080
       name: http
       allowedRoutes:
         namespaces:
           from: All
   EOF
   ```

3. Get the Helm values for your current kgateway installation and remove the values that you added in this guide.
   ```sh
   helm get values kgateway -n kgateway-system -o yaml > kgateway.yaml
   open kgateway.yaml
   ```
   
4. Upgrade your kgateway installation. 
   ```sh
   helm upgrade -i --namespace kgateway-system --version v2.0.0-main kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway -f kgateway.yaml
   ```

5. Follow the Istio documentation to [uninstall Istio](https://istio.io/latest/docs/setup/getting-started/#uninstall) and [remove the Bookinfo sample app](https://istio.io/latest/docs/examples/bookinfo/#cleanup).
