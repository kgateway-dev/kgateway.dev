---
title: Istio service mesh
weight: 530
description: Use your kgateway proxy as the ingress gateway to control and secure traffic that enters your service mesh. 
---

Use your {{< reuse "docs/snippets/product-name.md" >}} proxy as the ingress gateway to control and secure traffic that enters your service mesh.

## About service mesh

A service mesh is a dedicated infrastructure layer that you add your apps to, which ensures secure service-to-service communication across cloud networks. With a service mesh, you can solve problems such as service identity, mutual TLS communication, consistent L7 network telemetry gathering, service resilience, secure traffic routing between services across clusters, and policy enforcement, such as to enforce quotas or rate limit requests. To learn more about the benefits of using a service mesh, see [What is a service mesh](https://docs.solo.io/gloo-mesh-enterprise/latest/concepts/istio/service-mesh-ov/) in Solo.io's Gloo Mesh Enterprise documentation. 

### About Istio

The open source project Istio is the leading service mesh implementation that offers powerful features to secure, control, connect, and monitor cloud-native, distributed applications. Istio is designed for workloads that run in one or more Kubernetes clusters, but you can also extend your service mesh to include virtual machines and other endpoints that are hosted outside your cluster. The key benefits of Istio include: 

* Automatic load balancing for HTTP, gRPC, WebSocket, MongoDB, and TCP traffic
* Secure TLS encryption for service-to-service communication with identity-based authentication and authorization
* Advanced routing and traffic management policies, such as retries, failovers, and fault injection
* Fine-grained access control and quotas
* Automatic logs, metrics, and traces for traffic in the service mesh

### About the Istio integration

{{< reuse "docs/snippets/product-name-caps.md" >}} comes with an Istio integration that allows you to configure your gateway proxy with an Istio sidecar. The Istio sidecar uses mutual TLS (mTLS) to prove its identity and to secure the connection between your gateway and the services in your Istio service mesh. In addition, you can control and secure the traffic that enters the mesh by applying all the advanced routing, traffic management, security, and resiliency capabilities that {{< reuse "docs/snippets/product-name.md" >}} offers.  

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up an Istio service mesh

Use Solo.io's Gloo Mesh Enterprise product to install a managed Istio version by using the built-in Istio lifecycle manager, or manually install and manage your own Istio installation. 

{{< tabs items="Managed Istio with Gloo Mesh Enterprise,Manual Istio installation" >}}
{{% tab  %}}

Gloo Mesh Enterprise is a service mesh management plane that is based on hardened, open-source projects like Envoy and Istio. With Gloo Mesh, you can unify the configuration, operation, and visibility of service-to-service connectivity across your distributed applications. These apps can run in different virtual machines (VMs) or Kubernetes clusters on premises or in various cloud providers, and even in different service meshes.

Follow the [Gloo Mesh Enterprise get started guide](https://docs.solo.io/gloo-mesh-enterprise/latest/getting_started/single/gs_single/) to quickly install a managed Solo distribution of Istio by using the built-in Istio lifecycle manager. 

{{% /tab %}}
{{% tab  %}}

Set up Istio. Choose between the following options to set up Istio: 
* [Manually install a Solo distribution of Istio](https://docs.solo.io/gloo-mesh-enterprise/latest/istio/manual/manual_deploy/). The Solo distribution of Istio is a hardened Istio enterprise image, which maintains `n-4` support for CVEs and other security fixes.
* Install an open source distribution of Istio by following the [Istio documentation](https://istio.io/latest/docs/setup/getting-started/). 

{{% /tab %}}
{{< /tabs >}}

## Enable the Istio integration

Upgrade your {{< reuse "docs/snippets/product-name.md" >}} installation to enable the Istio integration. 

1. Get the name of the istiod service. Depending on how you set up Istio, you might see a revisionless service name (`istiod`) or a service name with a revision, such as `istiod-1-21`. 
   ```sh
   kubectl get services -n istio-system
   ```
   
   Example output: 
   ```                          
   NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                 AGE
   istiod-1-21   ClusterIP   10.102.24.31   <none>        15010/TCP,15012/TCP,443/TCP,15014/TCP   3h49m
   ``` 

2. Derive the Kubernetes service address for your istiod deployment. The service address uses the format `<service-name>.<namespace>.svc:15012`. For example, if your service name is `istiod-1-21`, the full service address is `istiod-1-21.istio-system.svc:15012`.

3. Get the Helm values for your current {{< reuse "docs/snippets/product-name.md" >}} installation. 
   ```sh
   helm get values kgateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml > kgateway.yaml
   open kgateway.yaml
   ```
   
4. Add the following values to the Helm value file. Make sure that you change the `istioProxyContainer` values to the service address and cluster name of your Istio installation.
   ```yaml
   
   global:
     istioIntegration:
       enableAutoMtls: true
       enabled: true
     istioSDS:
       enabled: true
   kubeGateway:
     enabled: true
     gatewayParameters:
       glooGateway:
         istio:
           istioProxyContainer: 
             istioDiscoveryAddress: istiod-1-21.istio-system.svc:15012
             istioMetaClusterId: mycluster
             istioMetaMeshId: mycluster
   ```
   
   | Setting | Description |
   | -- | -- | 
   | `istioDiscoveryAddress` | The address of the istiod service. If omitted, `istiod.istio-system.svc:15012` is used. |
   | `istioMetaClusterId` </br> `istioMetaMeshId` | The name of the cluster where {{< reuse "docs/snippets/product-name.md" >}} is installed. |
   
5. Upgrade your {{< reuse "docs/snippets/product-name.md" >}} installation. 
   ```sh
   helm upgrade -n {{< reuse "docs/snippets/ns-system.md" >}} kgateway kgateway/kgateway \
      -f kgateway.yaml \
      --version={{< reuse "docs/versions/n-patch.md" >}}
   ```

6. Verify that your `http` pod is restarted with 3 containers now: `gateway-proxy`, `istio-proxy`, and `sds`. 
   ```sh
   kubectl get pods -n {{< reuse "docs/snippets/ns-system.md" >}} | grep http
   ```
   
   Example output: 
   ```
   http-f7cd596b7-tv5z7    3/3     Running            0              3h31m
   ```
   
7. Optional: Review the GatewayParameters resource and verify that the `istioDiscoveryAddress`, `istioMetaClusterId`, and `istioMetaMeshId` are set to the values from your Helm chart. 
   ```sh
   kubectl get gatewayparameters kgateway -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```
   
   Example output: 
   ```console {hl_lines=[20,21,22]}
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayParameters
   metadata:
     annotations:
       meta.helm.sh/release-name: kgateway
       meta.helm.sh/release-namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   ...
   spec:
     kube:
       deployment:
         replicas: 1
       ...
       istio:
         istioProxyContainer:
           image:
             pullPolicy: IfNotPresent
             registry: docker.io/istio
             repository: proxyv2
             tag: 1.22.0
           istioDiscoveryAddress: istiod-1-21.istio-system.svc:15012
           istioMetaClusterId: mycluster
           istioMetaMeshId: mycluster
           logLevel: warning
        podTemplate:
         extraLabels:
           kgateway: kube-gateway
   ...
   ```

8. Optional: Review the Settings resource and verify that `appendXForwardedHost`, `enableAutoMtls`, and `enableIntegration` are all set to `true`. 
   ```sh
   kubectl get settings default -n {{< reuse "docs/snippets/ns-system.md" >}} -o yaml
   ```
   
   Example output: 
   ```console {hl_lines=[17,18,19]}
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Settings
   metadata:
     annotations:
       meta.helm.sh/release-name: kgateway
       meta.helm.sh/release-namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     consoleOptions:
       apiExplorerEnabled: true
       readOnly: false
     discovery:
       fdsMode: WHITELIST
     discoveryNamespace: {{< reuse "docs/snippets/ns-system.md" >}}
     gloo:
       ...
       istioOptions:
         appendXForwardedHost: true
         enableAutoMtls: true
         enableIntegration: true
   ...
   ```

   
## Set up mTLS routing to httpbin

1. Label the httpbin namespace for Istio sidecar injection. 
   ```sh
   export REVISION=$(kubectl get pod -L app=istiod -n istio-system -o jsonpath='{.items[0].metadata.labels.istio\.io/rev}')      
   echo $REVISION
   kubectl label ns httpbin istio.io/rev=$REVISION --overwrite=true
   ```
  
2. Perform a rollout restart for the httpbin deployment so that an Istio sidecar is automatically added to the httpbin app. 
   ```sh
   kubectl rollout restart deployment httpbin -n httpbin
   ```
   
3. Verify that the httpbin app comes up with a fourth container. 
   ```sh
   kubectl get pods -n httpbin
   ```
   
   Example output: 
   ```
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-f46cc8b9b-f4wbm   4/4     Running   0          10s
   ```

4. Send a request to the httpbin app. Verify that you get back a 200 HTTP response and that an [`x-forwarded-client-cert`](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_conn_man/headers#x-forwarded-client-cert) header is returned. The presence of this header indicates that the connection from the gateway to the httpbin app is now encrypted with mutual TLS. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output: 
   ```console {hl_lines=[21,22]}
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-B3-Sampled": [
        "0"
      ],
      "X-B3-Spanid": [
        "92744e97e79d8f22"
      ],
      "X-B3-Traceid": [
        "8189f0a6c4e3582792744e97e79d8f22"
      ],
      "X-Forwarded-Client-Cert": [
        "By=spiffe://gloo-edge-docs-mgt/ns/httpbin/sa/httpbin;Hash=3a57f9d8fddea59614b4ade84fcc186edeffb47794c06608068a3553e811bdfe;Subject=\"\";URI=spiffe://gloo-edge-docs-mgt/ns/{{< reuse "docs/snippets/ns-system.md" >}}/sa/http"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "7f1d6e38-3bf7-44fd-8298-a77c34e5b865"
      ]
    }
   }
   ```
   
## Exclude a service from mTLS 

You can exclude a service from requiring to communicate with the gateway proxy via mTLS by adding the `disableIstioAutoMtls` option to the Backend that represents your service. 

1. Create a Backend resource that represents the httpbin app and add the `disableIstioAutoMtls: true` option to it. This option excludes the httpbin Backend from communicating with the gateway proxy via mTLS. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     disableIstioAutoMtls: true
     kube:
       serviceName: httpbin
       serviceNamespace: httpbin
       servicePort: 8000
   EOF
   ```
   
2. Create an HTTPRoute resource that routes traffic to the httpbin Backend that you created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: exclude-automtls
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - disable-automtls.example
     rules:
       - backendRefs:
         - name: httpbin
           kind: Backend
           group: gateway.kgateway.dev
   EOF
   ```

3. Send a request to the httpbin app on the `disable-automtls.example` domain. Verify that you do not get back the `x-forwarded-client-cert` header. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
    -H "host:disable-automtls.example:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/headers 
    -H "host: disable-automtls.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```
   {
     "headers": {
        "Accept": [
         "*/*"
       ],
       "Host": [
         "disable-automtls.example:8080"
       ],
        "User-Agent": [
          "curl/7.77.0"
        ],
        "X-Forwarded-Proto": [
         "http"
        ],
       "X-Request-Id": [
         "47c4dcc8-551b-4c93-8aa3-1cd1e15b137c"
       ]
     }
   }
   ```
   
4. Repeat the request to the httpbin app on the `www.example.com` domain that is enabled for mTLS. Verify that you continue to see the `x-forwarded-client-cert` header. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
    -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/headers 
    -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[12,13]}
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "www.example.com:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-Forwarded-Client-Cert": [
        "By=spiffe://gloo-edge-docs-mgt/ns/httpbin/sa/httpbin;Hash=3a57f9d8fddea59614b4ade84fcc186edeffb47794c06608068a3553e811bdfe;Subject=\"\";URI=spiffe://gloo-edge-docs-mgt/ns/{{< reuse "docs/snippets/ns-system.md" >}}/sa/http"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "7f1d6e38-3bf7-44fd-8298-a77c34e5b865"
      ]
    }
   }
   ```
   
   
## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Follow the [Uninstall guide in the Gloo Mesh Enterprise documentation](https://docs.solo.io/gloo-mesh-enterprise/main/setup/uninstall/) to remove Gloo Mesh Enterprise. 

2. Remove the Istio sidecar from the httpbin app. 
   1. Remove the Istio label from the httpbin namespace. 
      ```sh
      kubectl label ns httpbin istio.io/rev-
      ```
   2. Perform a rollout restart for the httpbin deployment. 
      ```sh
      kubectl rollout restart deployment httpbin -n httpbin
      ```
   3. Verify that the Istio sidecar container is removed. 
      ```sh
      kubectl get pods -n httpbin
      ```
      
      Example output: 
      ```
      NAME                       READY   STATUS        RESTARTS   AGE
      httpbin-7d4965fb6d-mslx2   3/3     Running       0          6s
      ```

3. Remove the Backend and HTTPRoute that you used to exclude a service from mTLS. 
   ```sh
   kubectl delete backend httpbin -n {{< reuse "docs/snippets/ns-system.md" >}}
   kubectl delete httproute exclude-automtls -n {{< reuse "docs/snippets/ns-system.md" >}} 
   ```

<!-- TODO: Upgrade guide   
2. Follow the [upgrade guide](/docs/operations/upgrade/) to upgrade your {{< reuse "docs/snippets/product-name.md" >}} Helm installation values. Remove the Helm values that you added as part of this guide.
-->


