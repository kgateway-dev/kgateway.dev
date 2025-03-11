---
title: Shadowing
weight: 10
description: Copy live production traffic to a shadow environment or service so that you can try out, analyze, and monitor new software changes before deploying them to production. 
---

Copy live production traffic to a shadow environment or service so that you can try out, analyze, and monitor new software changes before deploying them to production.

## About traffic shadowing

When releasing changes to a service, you want to finely control how those changes get exposed to users. This [progressive delivery](https://redmonk.com/jgovernor/2018/08/06/towards-progressive-delivery/) approach to releasing software allows you to reduce the blast radius, especially when changes introduce unintended behaviors. Traffic shadowing, also referred to as traffic mirroring, is one way to observe the impact of new software releases and test out new changes before you roll them out to production. Other approaches to slowly introduce new software include canary releases, A/B testing, or blue-green deployments. 

When you turn on traffic shadowing for an app, {{< reuse "docs/snippets/product-name.md" >}} makes a copy of all incoming requests. {{< reuse "docs/snippets/product-name.md" >}} still proxies the request to the backing destination along the request path. It also sends a copy of the request asynchronously to another shadow destination. When a response or failure happens, copies are not generated. This way, you can test how traffic is handled by a new release or version of your app with zero production impact. You can also compare the shadowed results against the expected results. You can use this information to decide how to proceed with a canary release.

When a copy of the request is sent to the shadow app, {{< reuse "docs/snippets/product-name.md" >}} adds a `-shadow` postfix to the `Host` or `Authority` header. For example, if traffic is sent to `foo.bar.com`, the `Host` header value is set to `foo.bar.com-shadow`. This way, the app that receives the shadowed traffic can determine if the traffic is shadowed or not. This information might be valuable for stateful services, such as to roll back any stateful transactions that are associated with processing the request. To learn more about advanced traffic shadowing patterns, see [this blog](https://blog.christianposta.com/microservices/advanced-traffic-shadowing-patterns-for-microservices-with-istio-service-mesh/).

To observe and analyze shadowed traffic, you can use a tool like [Open Diffy](https://github.com/opendiffy/diffy). This tool create diff-compares on the responses. You can use this data to verify that the response is correct and to detect API forward/backward compatibility problems. 

{{% callout type="info" %}}
To enable traffic shadowing, you must set up an [Backend](/docs/traffic-management/destination-types/backends/) resource for the app that you want to shadow traffic for and for the app that receives the shadowed traffic.  
{{% /callout %}}


## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up traffic shadowing

1. Create a namespace for a second httpbin app that you use to receive shadowed traffic. 
   ```sh
   kubectl create ns shadow
   ```

2. Deploy the httpbin shadow app. 
   ```sh
   kubectl -n shadow apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
   ```

3. Verify that the httpbin shadow app is running.
   ```sh
   kubectl -n shadow get pods
   ```

4. Create a Backend resource for the httpbin shadow app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: shadow
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     kube:
       serviceName: httpbin
       serviceNamespace: shadow
       servicePort: 8000
   EOF
   ```

5. Create another Backend resource for the httpbin app that you deployed as part of the [Get started](/docs/quickstart/}) guide. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: httpbin
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   spec:
     kube:
       serviceName: httpbin
       serviceNamespace: httpbin
       servicePort: 8000
   EOF
   ```

5. Create a RouteOption resource to define your shadowing rules. The following example shadows 100% of the traffic to the `shadow` Backend resource that you just created. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: RouteOption
   metadata:
     name: shadowing
     namespace: httpbin
   spec:
     options:
       shadowing:
          backend:
            name: shadow
            namespace: {{< reuse "docs/snippets/ns-system.md" >}}
          percentage: 100
   EOF
   ```

6. Create an HTTPRoute resource for the httpbin app that you want to shadow traffic for and reference the RouteOption resource that you created. Note that shadowing requires you to route traffic to the httpbin Backend and not to the httpbin service directly. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin-shadow
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/ns-system.md" >}}
     hostnames:
       - shadowing.example
     rules:
       - filters:
           - type: ExtensionRef
             extensionRef:
               group: gateway.solo.io
               kind: RouteOption
               name: shadowing
         backendRefs:
           - name: httpbin
             kind: Backend
             group: gateway.kgateway.dev
             namespace: {{< reuse "docs/snippets/ns-system.md" >}}
   EOF
   ```

7. Create a reference grant to allow the HTTPRoute resource to access Backend resources in the `{{< reuse "docs/snippets/ns-system.md" >}}` namespace. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: ReferenceGrant
   metadata:
     name: shadow-rg
     namespace: {{< reuse "docs/snippets/ns-system.md" >}}   
   spec:
     from:
       - group: gateway.networking.k8s.io
         kind: HTTPRoute
         namespace: httpbin
     to:
       - group: "gateway.kgateway.dev"
         kind: Backend
   EOF
   ```

7. Send a request to the httpbin app on the `shadowing.example` domain. Verify that you get back a 200 HTTP response code. 
   {{< tabs items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab  %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: shadowing.example:8080"
   ```
   {{% /tab %}}
   {{% tab  %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: shadowing.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a successful response: 
   ```yaml
   ...
   {
    "headers": {
      "Accept": [
        "*/*"
      ],
      "Host": [
        "timeout.example:8080"
      ],
      "User-Agent": [
        "curl/7.77.0"
      ],
      "X-Envoy-Expected-Rq-Timeout-Ms": [
        "20000"
      ],
      "X-Forwarded-Proto": [
        "http"
      ],
      "X-Request-Id": [
        "0ae53bc3-2644-44f2-8603-158d2ccf9f78"
      ]
    }
   }
   ```

8. Get the logs for the shadow httpbin app and verify that you see a copy of that request. 
   ```sh
   kubectl logs $(kubectl get pod -l app=httpbin -o jsonpath='{.items[0].metadata.name}' -n shadow) -n shadow -c httpbin 
   ```

   Example output: 
   ```
   go-httpbin listening on http://0.0.0.0:8080
   time="2024-06-12T14:08:37.4174" status=200 method="GET" uri="/headers" size_bytes=442 duration_ms=0.17 user_agent="curl/7.77.0" client_ip=10.XX.X.XX
   ```
   
9. Get the logs for the httpbin app and verify that you see the same log entry for your requests. 
   ```sh
   kubectl logs $(kubectl get pod -l app=httpbin -o jsonpath='{.items[0].metadata.name}' -n httpbin) -n httpbin -c httpbin 
   ```

   Example output: 
   ```
   go-httpbin listening on http://0.0.0.0:8080
   time="2024-06-12T14:10:23.4605" status=200 method="GET" uri="/headers" size_bytes=338 duration_ms=0.09 user_agent="curl/7.77.0" client_ip=10.XX.X.XX:38808
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproutes httpbin-shadow -n httpbin 
kubectl delete routeoption shadowing -n httpbin
kubectl delete backend shadow -n {{< reuse "docs/snippets/ns-system.md" >}}
kubectl delete backend httpbin -n {{< reuse "docs/snippets/ns-system.md" >}} 
kubectl delete referencegrant shadow-rg -n {{< reuse "docs/snippets/ns-system.md" >}}
kubectl delete -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml -n shadow
kubectl delete ns shadow
```


