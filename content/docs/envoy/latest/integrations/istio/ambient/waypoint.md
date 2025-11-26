---
title: Waypoint proxy
weight: 20
---

{{< callout type="warning" >}}
The waypoint integration for Envoy-based gateway proxies is deprecated and is planned to be removed in version 2.2. If you want to use AI capabilities, use an [agentgateway proxy](../../agentgateway/) instead.
{{< /callout >}}

Enforce Layer 7 policies for the apps in your ambient mesh by using {{< reuse "/docs/snippets/kgateway.md" >}} as a waypoint proxy.


## About ambient mesh

Solo.io and Google collaborated to develop ambient mesh, a new “sidecarless” architecture for the Istio service mesh. Ambient mesh uses node-level ztunnels to route and secure Layer 4 traffic between pods with mutual TLS (mTLS). Waypoint proxies enforce Layer 7 traffic policies whenever needed. To onboard apps into the ambient mesh, you simply label the namespace the app belongs to. Because no sidecars need to be injected in to your apps, ambient mesh significantly reduces the complexity of adopting a service mesh. 

To learn more about ambient, see the [ambient mesh documentation](https://ambientmesh.io/docs/about/). 

## About this guide

In this guide, you learn how to set up {{< reuse "/docs/snippets/kgateway.md" >}} as a waypoint proxy for multiple apps in your ambient mesh. To demonstrate the Layer 7 capabilities of the waypoint proxy, you deploy the three sample apps `client`, `httpbin2`, and `httpbin3` to your cluster. The `client` app sends in-mesh traffic to `httpbin2` and `httpbin3`. To apply Layer 7 policies, you create HTTPRoute resources for the `httpbin2` and `httpbin3` apps that define the policies that you want to apply to each app. Because the HTTPRoute is scoped to a particular service, when the `client` app sends a request to that service, only the policies that are defined for that service are enforced by the waypoint proxy. 

{{< callout type="info" >}}
You can create an HTTPRoute and scope it to the waypoint proxy by referencing the waypoint proxy in the `parentRef` section. This way, the policies that are defined in the HTTPRoute are automatically applied to all services in the waypoint proxy namespace.
{{< /callout >}}

{{< reuse-image src="img/waypoint.svg" width="600px" caption="Waypoint proxy for Layer 7 policy application in an ambient mesh" >}}
{{< reuse-image-dark srcDark="img/waypoint.svg" width="600px" caption="Waypoint proxy for Layer 7 policy application in an ambient mesh" >}}

## Set up an ambient mesh

{{< reuse "docs/snippets/setup-ambient-mesh.md" >}}

## Deploy sample apps

Install the httpbin2, httpbin3, and curl client sample apps into the httpbin namespace. You use these sample apps to demonstrate the Layer 7 capabilities of the waypoint proxy. 

1. Create the httpbin namespace. 
   ```sh
   kubectl create ns httpbin
   ```
   
2. Deploy the httpbin2, httpbin3, and client sample apps. 
   {{< tabs tabTotal="3" items="httpbin2,httpbin3,client" >}}
   {{% tab tabName="httpbin2" %}}
   ```yaml
   kubectl apply -f - <<EOF                                                  
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: httpbin2
     namespace: httpbin
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: httpbin2
     namespace: httpbin
     labels:
       app: httpbin2
       service: httpbin2
   spec:
     ports:
     - name: http
       port: 8000
       targetPort: http
       protocol: TCP
       appProtocol: http
     selector:
       app: httpbin2
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: httpbin2
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: httpbin2
         version: v1
     template:
       metadata:
         labels:
           app: httpbin2
           version: v1
       spec:
         serviceAccountName: httpbin2
         containers:
         - name: httpbin
           image: mccutchen/go-httpbin:v2.14.0
           command: [ go-httpbin ]
           args:       
             - "-max-duration"
             - "600s" # override default 10s
             - -use-real-hostname
           ports:
             - name: http
               containerPort: 8080
               protocol: TCP
           livenessProbe:
             httpGet:
               path: /status/200
               port: http
           readinessProbe:
             httpGet:
               path: /status/200
               port: http
           env:
           - name: K8S_MEM_LIMIT
             valueFrom:
               resourceFieldRef:
                 divisor: "1"
                 resource: limits.memory
           - name: GOMAXPROCS
             valueFrom:
               resourceFieldRef:
                 divisor: "1"
                 resource: limits.cpu  
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="httpbin3" %}}
   ```yaml
   kubectl apply -f - <<EOF                                                  
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: httpbin3
     namespace: httpbin
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: httpbin3
     namespace: httpbin
     labels:
       app: httpbin3
       service: httpbin3
   spec:
     ports:
     - name: http
       port: 8000
       targetPort: http
       protocol: TCP
       appProtocol: http
     selector:
       app: httpbin3
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: httpbin3
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: httpbin3
         version: v1
     template:
       metadata:
         labels:
           app: httpbin3
           version: v1
       spec:
         serviceAccountName: httpbin3
         containers:
         - name: httpbin
           image: mccutchen/go-httpbin:v2.14.0
           command: [ go-httpbin ]
           args:       
             - "-max-duration"
             - "600s" # override default 10s
             - -use-real-hostname
           ports:
             - name: http
               containerPort: 8080
               protocol: TCP
           livenessProbe:
             httpGet:
               path: /status/200
               port: http
           readinessProbe:
             httpGet:
               path: /status/200
               port: http
           env:
           - name: K8S_MEM_LIMIT
             valueFrom:
               resourceFieldRef:
                 divisor: "1"
                 resource: limits.memory
           - name: GOMAXPROCS
             valueFrom:
               resourceFieldRef:
                 divisor: "1"
                 resource: limits.cpu  
   EOF
   ```
   {{% /tab %}}
   {{% tab tabName="client" %}}
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: client
     namespace: httpbin
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: client
     namespace: httpbin
     labels:
       app: client
       service: client
   spec:
     ports:
     - name: http
       port: 8000
       targetPort: 80
     selector:
       app: client
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: client
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: client
         version: v1
     template:
       metadata:
         labels:
           app: client
           version: v1
       spec:
         serviceAccountName: client
         containers:
         - image: nicolaka/netshoot:latest
           imagePullPolicy: IfNotPresent
           name: netshoot
           command: ["/bin/bash"]
           args: ["-c", "while true; do ping localhost; sleep 60;done"]
   EOF
   ```
   {{% /tab %}}
   {{< /tabs >}}

4. Verify that all apps are deployed successfully. 
   ```sh
   kubectl get pods -n httpbin
   ```
   
   Example output: 
   ```  
   NAME                                        READY   STATUS    RESTARTS   AGE
   client-87678cb44-dclfs                      1/1     Running   0          87m
   httpbin2-58dcc755ff-ngq2f                   1/1     Running   0          92m
   httpbin3-77bbdd9b6b-8d8hq                   1/1     Running   0          70m
   ```

5. Label the `httpbin` namespace to add the httpbin2, httpbin3, and client apps to the ambient mesh. 
   ```sh
   kubectl label ns httpbin istio.io/dataplane-mode=ambient
   ```

## Create a waypoint proxy

Use the `{{< reuse "/docs/snippets/waypoint-class.md" >}}` GatewayClass to deploy {{< reuse "/docs/snippets/kgateway.md" >}} as a waypoint proxy in your cluster. 

1. Enable the waypoint integration in your kgateway Helm chart. 
   ```sh
   helm get values {{< reuse "/docs/snippets/kgateway.md" >}} -n {{< reuse "/docs/snippets/namespace.md" >}} -o yaml > {{< reuse "/docs/snippets/kgateway.md" >}}.yaml
   
   helm upgrade -i --namespace kgateway-system --version v{{< reuse "docs/versions/patch-dev.md" >}} \
   kgateway oci://cr.kgateway.dev/kgateway-dev/charts/kgateway \
   --set controller.image.pullPolicy=Always \
   --set waypoint.enabled=true \
   --values {{< reuse "/docs/snippets/kgateway.md" >}}.yaml
   ```

2. Verify that you see the `{{< reuse "/docs/snippets/waypoint-class.md" >}}` GatewayClass in your cluster. 
   ```sh
   kubectl get gatewayclasses -A
   ```
   
   Example output: 
   ```
   NAME                CONTROLLER              ACCEPTED   AGE
   kgateway            kgateway.dev/kgateway   True       2d19h
   kgateway-waypoint   kgateway.dev/kgateway   True       1s
   ```
  
3. Create a waypoint proxy in the httpbin namespace. Note that creating a waypoint proxy does not automatically enforce Layer 7 policies for the apps in your cluster. To assign a waypoint, you must label your apps. You learn how to label your apps in a later step. 
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: {{< reuse "/docs/snippets/waypoint-class.md" >}}
     namespace: httpbin
   spec:
     gatewayClassName: {{< reuse "/docs/snippets/waypoint-class.md" >}}
     listeners:
     - name: proxy
       port: 15088
       protocol: istio.io/PROXY
   EOF
   ```

4. Wait for the waypoint proxy to deploy successfully.
   ```sh
   kubectl -n httpbin rollout status deploy {{< reuse "/docs/snippets/waypoint-class.md" >}}
   ```
   
   Example output: 
   ```
   deployment "{{< reuse "/docs/snippets/waypoint-class.md" >}}" successfully rolled out
   ```

5. Label the httpbin2 and httpbin3 apps to use the waypoint proxy that you created.
   ```sh
   kubectl -n httpbin label svc httpbin2 istio.io/use-waypoint={{< reuse "/docs/snippets/waypoint-class.md" >}}
   kubectl -n httpbin label svc httpbin3 istio.io/use-waypoint={{< reuse "/docs/snippets/waypoint-class.md" >}}
   ```

6. Send a request from the client app to httpbin2 and httpbin3. Verify that the request succeeds. 
   ```sh
    kubectl -n httpbin exec deploy/client -- curl -s http://httpbin2:8000/get
    kubectl -n httpbin exec deploy/client -- curl -s http://httpbin3:8000/get
    ```
    
    Example output for httpbin2: 
    ```
    {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "httpbin2:8000"
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
         "590a6a48-60f8-4ec0-92d1-fcb629b97e0d"
       ]
     },
     "method": "GET",
     "origin": "10.XX.X.XX:34059",
     "url": "http://httpbin2:8000/get"
    }
    ```

## Enforce L7 policies with the waypoint {#waypoint-policies}

In this step, you explore how to apply different types of Layer 7 policies to your sample apps. These policies are enforced by the {{< reuse "/docs/snippets/kgateway.md" >}} waypoint proxy that you created earlier. You can add other Layer 7 policies to the waypoint proxy. For more information, see the [traffic management](../../../../traffic-management), [security](../../../../security), and [resiliency](../../../../resiliency) guides. 

### Header control

Use the Kubernetes Gateway API to define header manipulation rules that you apply to the httpbin apps, including adding, setting, and removing request headers. 

1. Create an HTTPRoute resource for the httpbin2 app with the following request header modifications rules: 
   * Add the `App: httpbin2` header to all requests. 
   * Set the `User-Agent` header to `custom`. If the User-Agent header is not present, it is added to the request. 
   * Remove the `X-Remove` header from the request. 
   
   Note that the HTTPRoute specifies the httpbin2 service in the `parentRefs` section. This setting instructs the waypoint proxy to enforce these policies for the httpbin2 app only. 
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin2
     namespace: httpbin
   spec:
     parentRefs:
     - name: httpbin2
       kind: Service
       group: ""
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /
         backendRefs:
          - name: httpbin2
            port: 8000
         filters:
           - type: RequestHeaderModifier
             requestHeaderModifier:
               add:
                 - name: App
                   value: httpbin2
               set:
                 - name: User-Agent
                   value: custom
               remove:
                 - X-Remove
   EOF
   ```

2. Create an HTTPRoute for the httpbin3 app with the following request header modifications rules:
   * Add the `App: httpbin3` header to all requests.
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin3
     namespace: httpbin
   spec:
     parentRefs:
     - name: httpbin3
       kind: Service
       group: ""
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /
         backendRefs:
          - name: httpbin3
            port: 8000
         filters:
           - type: RequestHeaderModifier
             requestHeaderModifier:
               add:
                 - name: App
                   value: httpbin3
   EOF
   ```

3. Use the client sample app to send a request to the httpbin2 app. Verify that you see the `App: httpbin2` and `User-Agent: custom` headers, and that the `X-Remove` was not added to the respones. 
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -s http://httpbin2:8000/get \
    -H "X-Remove: this header"
   ```
   
   Example output: 
   ```console {hl_lines=[7,8,13,14]}
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "App": [
         "httpbin2"
       ],
       "Host": [
         "httpbin2:8000"
       ],
       "User-Agent": [
         "custom"
       ],
       "X-Client": [
         "curl"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "4ef6b82d-6388-4be9-bb2c-b3077beafee8"
       ]
     },
     "method": "GET",
     "origin": "10.XX.X.XX:33737",
     "url": "http://httpbin2:8000/get"
   }
   ```

4. Send the same request to the httpbin3 app. Verify that you see the `App: httpbin3` header and `X-Remove` headers, and that the `User-Agent` header is not changed to `custom`.
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -s http://httpbin3:8000/get \
    -H "X-Remove: this header"
   ```
   
   Example output: 
   ```console {hl_lines=[10,11,13,14,22,23]}
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "httpbin3:8000"
       ],
       "App": [
         "httpbin3"
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
       "X-Remove": [
         "this header"
       ],
       "X-Request-Id": [
         "8a32f44f-55ab-4ff7-8b77-16d18739ae02"
       ]
     },
     "method": "GET",
     "origin": "10.XX.X.XX:53569",
     "url": "http://httpbin3:8000/get"
   }
   ```

### Transformations

Use {{< reuse "/docs/snippets/kgateway.md" >}}'s {{< reuse "/docs/snippets/trafficpolicy.md" >}} to apply a transformation policy to the httpbin2 app. 

1. If you have not done so yet, create an HTTPRoute for the httpbin2 app. You use this HTTPRoute to apply your transformation policy in the next step. 
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin2
     namespace: httpbin
   spec:
     parentRefs:
     - name: httpbin2
       kind: Service
       group: ""
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /
         backendRefs:
          - name: httpbin2
            port: 8000 
   EOF
   ```

2. Create a {{< reuse "/docs/snippets/trafficpolicy.md" >}} that applies a transformation policy to the httpbin2 app. In this example, the base64-encoded value from the `x-base64-encoded` header is decoded and added to the `x-base64-decoded` header, starting from the 11th character. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: transformation
     namespace: httpbin
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin2
     transformation:
       response:
         set:
         - name: x-base64-decoded
           value: '{{ substring(base64_decode(request_header("x-base64-encoded")), 11) }}'
   EOF
   ```
  
3. Use the client app to send a request to the httpbin2 app and include a base64-encoded value of `transformation test` in the request `x-base64-encoded` header. Verify that you get back a 200 HTTP response code, and that the decoded value is added to the `x-base64-decoded` response header, starting from the 11th character. 
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -vi http://httpbin2:8000/headers \
    -H "x-base64-encoded: dHJhbnNmb3JtYXRpb24gdGVzdA=="
   ```
   
   Example output: 
   ```console {hl_lines=[8,25,26]}
   < HTTP/1.1 200 OK
   ...
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; charset=utf-8
   content-length: 544
   x-envoy-upstream-service-time: 0
   x-base64-decoded: ion test
   server: envoy

   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "App": [
         "httpbin2"
       ],
       "Host": [
         "httpbin2:8000"
       ],
       "User-Agent": [
         "custom"
       ],
       "X-Base64-Encoded": [
         "dHJhbnNmb3JtYXRpb24gdGVzdA=="
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "10.0.74.217"
       ],
       "X-Forwarded-For": [
         "10.0.74.217"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "4b6444cc-b631-49c9-b2b4-f71ec479925f"
       ]
     }
   }
   ```

4. Optional: Remove the {{< reuse "/docs/snippets/trafficpolicy.md" >}} and HTTPRoute that you created in this guide. 
   ```sh
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
   kubectl delete httproute httpbin2 -n httpbin
   ```

### Local rate limiting

1. If you have not done so yet, create an HTTPRoute for the httpbin2 app. You use this HTTPRoute to apply your local rate limiting policy in the next step. 
   ```yaml
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: httpbin2
     namespace: httpbin
   spec:
     parentRefs:
     - name: httpbin2
       kind: Service
       group: ""
     rules:
       - matches:
         - path:
             type: PathPrefix
             value: /
         backendRefs:
          - name: httpbin2
            port: 8000 
   EOF
   ```
   
2. Create a {{< reuse "/docs/snippets/trafficpolicy.md" >}} that applies a local rate limiting policy to the httpbin2 app. In this example, only one request is allowed within 30 seconds. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "/docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "/docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: ratelimit
     namespace: httpbin
   spec:
     targetRefs: 
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin2
     rateLimit:
       local:
         tokenBucket:
           maxTokens: 1
           tokensPerFill: 1
           fillInterval: 30s
   EOF
   ```
   
3. Use the client app to send three requests to the httpbin2 app. Verify that you get back a 200 HTTP response code for the first request, and that the second and third request are denied with a 429 HTTP response code. 
   ```sh
   for i in {1..3}; do kubectl -n httpbin exec deploy/client -- curl -vi http://httpbin2:8000/headers ; done
   ```
   
   Example output: 
   ```
   * Request completely sent off
   HTTP/1.1 200 OK
   < HTTP/1.1 200 OK
   ...
   * Request completely sent off
   HTTP/1.1 429 Too Many Requests
   content-length: 18
   content-type: text/plain
   server: envoy
   ...
   local_rate_limited
   ...
   * Request completely sent off
   < HTTP/1.1 429 Too Many Requests
   < content-length: 18
   < content-type: text/plain
   < server: envoy
   ...  
   local_rate_limited%    
   ```
   
4. Optional: Remove the {{< reuse "/docs/snippets/trafficpolicy.md" >}} and HTTPRoute. 
   ```sh
   kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} ratelimit -n httpbin
   kubectl delete httproute httpbin2 -n httpbin
   ```

### Istio AuthorizationPolicy

Apply an Istio AuthorizationPolicy to allow access from specific apps only. 

1. Send a `GET` request from the client to the httpbin2 app. Verify that your request succeeds. 
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -vi http://httpbin2:8000/headers 
   ```
   
   Example output: 
   ```console 
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; charset=utf-8
   content-length: 439
   x-envoy-upstream-service-time: 2
   server: envoy

   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "httpbin2:8000"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "10.0.74.45"
   ....
   ```

2. Create an Istio AuthorizationPolicy that denies all `GET` requests to the httpbin2 app. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: security.istio.io/v1
   kind: AuthorizationPolicy
   metadata:
     name: httpbin-authz
     namespace: httpbin
   spec:
    action: DENY
    rules:
    - to:
      - operation:
          methods: ["GET"]
          ports: ["8000"]
    targetRefs:
    - group: ""
      kind: Service
      name: httpbin2
   EOF
   ```

3. Repeat the same request that previously succeeded. Verify that this time, you get back a 403 HTTP response code. 
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -vi http://httpbin2:8000/headers \
    -H "x-base64-encoded: dHJhbnNmb3JtYXRpb24gdGVzdA=="
   ```
   
   Example output: 
   ```console 
   * Request completely sent off
   < HTTP/1.1 403 Forbidden
   < content-length: 19
   < content-type: text/plain
   < server: envoy
   ```
   
4. Send a `POST` request to the httpbin2 app that is allowed with the AuthorizationPolicy. Verify that the request succeeds and that you get back a 200 HTTP response code. 
   ```sh
   kubectl -n httpbin exec deploy/client -- curl -vi -X POST http://httpbin2:8000/post \
    -H "x-base64-encoded: dHJhbnNmb3JtYXRpb24gdGVzdA=="
   ```
   
   Example output: 
   ```console
   * Request completely sent off
   < HTTP/1.1 200 OK
   < access-control-allow-credentials: true
   < access-control-allow-origin: *
   < content-type: application/json; charset=utf-8
   < content-length: 707
   < x-envoy-upstream-service-time: 2
   < server: envoy
   
   {
     "args": {},
     "headers": {
       "Accept": [
         "*/*"
       ],
      "Content-Length": [
         "0"
       ],
       "Host": [
         "httpbin2:8000"
       ],
       "User-Agent": [
         "curl/8.7.1"
   ...
   ```

5. Optional: Remove the Istio AuthoriationPolicy that you created in this guide. 
   ```sh
   kubectl delete authorizationpolicy httpbin-authz -n httpbin
   ```

## Cleanup

Delete the resources that you created in this guide. 

```sh
kubectl delete HTTPRoute httpbin3 -n httpbin
kubectl delete HTTPRoute httpbin2 -n httpbin
kubectl delete gateway {{< reuse "/docs/snippets/waypoint-class.md" >}} -n httpbin
kubectl delete serviceaccount httpbin2 -n httpbin
kubectl delete service httpbin2 -n httpbin
kubectl delete deployment httpbin2 -n httpbin
kubectl delete serviceaccount httpbin3 -n httpbin
kubectl delete service httpbin3 -n httpbin
kubectl delete deployment httpbin3 -n httpbin
kubectl delete serviceaccount client -n httpbin
kubectl delete service client -n httpbin
kubectl delete deployment client -n httpbin
kubectl delete {{< reuse "/docs/snippets/trafficpolicy.md" >}} transformation -n httpbin
kubectl delete authorizationpolicy httpbin-authz -n httpbin
```