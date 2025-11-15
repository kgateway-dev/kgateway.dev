---
title: Ingress
weight: 10
---

Use {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway for your ambient mesh. 

## About ambient mesh

Solo.io and Google collaborated to develop {{< gloss "Ambient mesh" >}}ambient mesh{{< /gloss >}}, a new “sidecarless” architecture for the Istio service mesh. Ambient mesh uses node-level ztunnels to route and secure Layer 4 traffic between pods with mutual TLS (mTLS). Waypoint proxies enforce Layer 7 traffic policies whenever needed. To onboard apps into the ambient mesh, you simply label the namespace the app belongs to. Because no sidecars need to be injected in to your apps, ambient mesh significantly reduces the complexity of adopting a service mesh.

To learn more about ambient, see the [ambient mesh documentation](https://ambientmesh.io/docs/about/). 

## About this guide

In this guide, you learn how to use {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway to route traffic to the httpbin app that is part of an ambient service mesh. 

This guide assumes that you run your ambient mesh in a single cluster and want to use {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway to protect your ambient mesh services. 

{{< reuse-image src="img/ambient-ingress.svg" width="600px" caption="Ingress gateway integration for an ambient mesh" >}}
{{< reuse-image-dark srcDark="img/ambient-ingress.svg" width="600px" caption="Ingress gateway integration for an ambient mesh" >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Set up an ambient mesh

{{< reuse "docs/snippets/setup-ambient-mesh.md" >}}

## Step 2: Set up the ingress gateway

To set up {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway for your ambient mesh, you simply add all the namespaces that you want to secure to your ambient mesh, including the namespace that your gateway proxy is deployed to.

1. Add the `httpbin` and optionally the `{{< reuse "docs/snippets/namespace.md" >}}` namespace to your ambient mesh. The label instructs istiod to configure a ztunnel socket on all the pods in that namespace so that traffic to these pods is secured via mutual TLS (mTLS). If you do not label the `{{< reuse "docs/snippets/namespace.md" >}}` namespace, the traffic from the gateway proxy to the app is not secured via mTLS.
   ```sh
   kubectl label ns {{< reuse "docs/snippets/namespace.md" >}} istio.io/dataplane-mode=ambient
   kubectl label ns httpbin istio.io/dataplane-mode=ambient
   ```
   
2. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. All traffic from the gateway is automatically intercepted by a ztunnel that is co-located on the same node as the gateway. The ztunnel collects Layer 4 metrics before it forwards the request to the ztunnel that is co-located on the same node as the httpbin app. The connection between ztunnels is secured via mutual TLS.
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```

   Example output: 
   ```console
   HTTP/1.1 200 OK
   ...
   {
    "headers": {
      "Accept": [
        "*/*"
       ],
       "Host": [
         "www.example.com:8080"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
      "X-Request-Id": [
         "929c334b-e611-4aba-9bc6-ad6b2450db26"
       ]
     }
   }
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   1. Port-forward the `http` pod on port 8080. 
      ```sh
      kubectl port-forward deployment/http -n {{< reuse "docs/snippets/namespace.md" >}} 8080:8080
      ```
   
   2. Send a request to the httpbin app and verify that you get back a 200 HTTP response code. 
      ```sh
      curl -i localhost:8080/headers -H "host: www.example.com"
      ```

      Example output: 
      ```
      HTTP/1.1 200 OK
      ...
      {
      "headers": {
         "Accept": [
         "*/*"
         ],
         "Host": [
            "www.example.com:8080"
         ],
         "User-Agent": [
            "curl/8.7.1"
         ],
         "X-Envoy-Expected-Rq-Timeout-Ms": [
            "15000"
         ],
         "X-Forwarded-Proto": [
            "http"
         ],
         "X-Request-Id": [
            "929c334b-e611-4aba-9bc6-ad6b2450db26"
         ]
       }
      }
      ```
   {{% /tab %}}
   {{< /tabs >}}

3. Verify that traffic between the gateway proxy and the httpbin app is secured via mutual TLS. Because traffic in an ambient mesh is intercepted by the ztunnels that are co-located on the same node as the sending and receiving service, you can check the logs of the ztunnels. 
   1. Find the `NODE` that the httpbin app runs on. 
      ```sh
      kubectl get pods -n httpbin -o wide
      ```
      
      Example output: 
      ```
      NAME                       READY   STATUS    RESTARTS   AGE   IP           NODE                                                  NOMINATED NODE   READINESS GATES
      httpbin-54cf575757-hdv8t   3/3     Running   0          22h   10.XX.X.XX   gke-ambient-default-pool-bb9a8da5-bdf4   <none>           <none>
      ```
   2. Find the ztunnel that runs on the same node as the httpbin app. 
      ```sh
      kubectl get pods -n istio-system -o wide | grep ztunnel
      ```
   3. Check the logs of that ztunnel instance and verify that the source and destination workloads have a SPIFFE ID. 
      ```sh
      kubectl logs <ztunnel-instance> -n istio-system
      ```
      
      Example output: 
      ```
      2025-03-19T17:32:42.762545Z	info	http access	request complete	src.addr=10.0.71.117:42468 src.workload="http-9db6c8995-l54dw" src.namespace="{{< reuse "docs/snippets/namespace.md" >}}" src.identity="spiffe://cluster.local/ns/{{< reuse "docs/snippets/namespace.md" >}}/sa/http" dst.addr=10.0.65.144:15008 dst.hbone_addr=10.0.65.144:8080 dst.service="httpbin.httpbin.svc.cluster.local" dst.workload="httpbin-577649ddb-7nc8p" dst.namespace="httpbin" dst.identity="spiffe://cluster.local/ns/httpbin/sa/httpbin" direction="inbound" method=GET path="/headers" protocol=HTTP1 response_code=200 host="www.example.com:8080" user_agent="curl/8.7.1" request_id="4c5fc679-c5cd-4721-8735-51bcdbea6e0f" duration="0ms"
      2025-03-19T17:32:46.810472Z	info	access	connection complete	src.addr=10.0.71.117:42468 src.workload="http-9db6c8995-l54dw" src.namespace="{{< reuse "docs/snippets/namespace.md" >}}" src.identity="spiffe://cluster.local/ns/{{< reuse "docs/snippets/namespace.md" >}}/sa/http" dst.addr=10.0.65.144:15008 dst.hbone_addr=10.0.65.144:8080 dst.service="httpbin.httpbin.svc.cluster.local" dst.workload="httpbin-577649ddb-7nc8p" dst.namespace="httpbin" dst.identity="spiffe://cluster.local/ns/httpbin/sa/httpbin" direction="inbound" bytes_sent=1290 bytes_recv=550 duration="6742ms"
      ```

## Next

Now that you set up {{< reuse "/docs/snippets/kgateway.md" >}} as the ingress gateway for your ambient mesh, you can further control and secure ingress traffic with [Policies](../../../../about/policies/).