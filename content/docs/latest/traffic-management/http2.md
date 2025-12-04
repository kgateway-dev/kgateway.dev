---
title: HTTP/2
weight: 20
description: Configure a service to use HTTP/2. 
---

You might have services in your Kubernetes cluster that use HTTP/2 for communication. Typically these are gRPC services, but it could apply to any service that uses HTTP/2 in its transport layer. To enable HTTP/2 communication, you simply set the app protocol on the service to HTTP/2. This setting instructs {{< reuse "docs/snippets/kgateway.md" >}} to use HTTP/2 for communication with the destination.

{{< callout >}}
{{< reuse "docs/snippets/proxy-kgateway.md" >}}
{{< /callout >}}

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Enable access logging

Enable access logging on the Gateway. You can use the access logs later to verify that the request used the HTTP/2 protocol. 

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: HTTPListenerPolicy
metadata:
  name: access-logs
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: http
  accessLog:
  - fileSink:
      path: /dev/stdout
      jsonFormat:
          start_time: "%START_TIME%"
          method: "%REQ(X-ENVOY-ORIGINAL-METHOD?:METHOD)%"
          path: "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%"
          protocol: "%PROTOCOL%"
          response_code: "%RESPONSE_CODE%"
          response_flags: "%RESPONSE_FLAGS%"
          bytes_received: "%BYTES_RECEIVED%"
          bytes_sent: "%BYTES_SENT%"
          total_duration: "%DURATION%"
          resp_backend_service_time: "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%"
          req_x_forwarded_for: "%REQ(X-FORWARDED-FOR)%"
          user_agent: "%REQ(USER-AGENT)%"
          request_id: "%REQ(X-REQUEST-ID)%"
          authority: "%REQ(:AUTHORITY)%"
          backendHost: "%UPSTREAM_HOST%"
          backendCluster: "%UPSTREAM_CLUSTER%"
EOF
```

## HTTP/2 for in-cluster services

To demonstrate the HTTP/2 routing capabilities, deploy a sample nginx server and configure it to only accept HTTP/2 connections. 

1. Deploy a simple nginx server that is configured to use the HTTP/2 protocol. Note that in this example, the `appProtocol` on the nginx service is set to `http2`. Other supported values to configure the HTTP/2 protocol include `grpc`, `grpc-web`, or `kubernetes.io/h2c`. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: nginx-conf
   data:
     nginx.conf: |
       user nginx;
       worker_processes  1;
       events {
         worker_connections  10240;
       }
       http {
         server {
             listen       80 http2;
             server_name  localhost;
             location / {
               root   /usr/share/nginx/html;
               index  index.html index.htm;
           }
         }
       }
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: nginx
   spec:
     selector:
       app.kubernetes.io/name: nginx
     ports:
       - protocol: TCP
         port: 8080
         targetPort: http-web-svc
         appProtocol: http2
   --- 
   apiVersion: v1
   kind: Pod
   metadata:
     name: nginx
     labels:
       app.kubernetes.io/name: nginx
   spec:
     containers:
       - name: nginx
         image: nginx:stable
         ports:
           - containerPort: 80
             name: http-web-svc
         volumeMounts:
           - name: nginx-conf
             mountPath: /etc/nginx/nginx.conf
             subPath: nginx.conf
             readOnly: true
     volumes:
     - name: nginx-conf
       configMap:
         name: nginx-conf
         items:
           - key: nginx.conf
             path: nginx.conf
   EOF
   ```

2. Verify that the nginx server is up and running. 
   ```sh
   kubectl get pods | grep nginx
   ```
   
   Example output: 
   ```console
   nginx      1/1     Running   0          15s
   ```

3. Create an HTTPRoute to expose the nginx server on the Gateway. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: nginx
     namespace: default
   spec:
     parentRefs:
       - name: http
         namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - http2.example.com
     rules:
       - backendRefs:
           - name: nginx
             port: 8080
   EOF
   ```

4. Send a request to the nginx server and include the `--http2-prior-knowledge` option to send an HTTP/2 request to the Gateway. Verify that the request succeeds and that you get back a 200 HTTP response code. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/ -H "host: http2.example.com:8080" --http2-prior-knowledge 
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/ -H "host: http2.example.com" --http2-prior-knowledge 
   ```
   
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[8,9]}
   ...
   > GET / HTTP/2
   > Host: http2.example.com:8080
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   HTTP/2 200 
   ...

   <!DOCTYPE html>
   <html>
   <head>
   <title>Welcome to nginx!</title>
   <style>
   html { color-scheme: light dark; }
   body { width: 35em; margin: 0 auto;
   font-family: Tahoma, Verdana, Arial, sans-serif; }
   </style>
   </head>
   <body>
   <h1>Welcome to nginx!</h1>
   <p>If you see this page, the nginx web server is successfully installed and
   working. Further configuration is required.</p>

   <p>For online documentation and support please refer to
   <a href="http://nginx.org/">nginx.org</a>.<br/>
   Commercial support is available at
   <a href="http://nginx.com/">nginx.com</a>.</p>

   <p><em>Thank you for using nginx.</em></p>
   </body>
   </html>
   ```

5. Get the access logs of your gateway proxy. 
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} logs deployments/http | tail -1 | jq --sort-keys
   ```
   
   Example output: 
   ```console {hl_lines=[9]}
   {
     "authority": "http2.example.com:8080",
     "backendCluster": "kube_default_nginx_8080",
     "backendHost": "10.0.2.26:80",
     "bytes_received": 0,
     "bytes_sent": 615,
     "method": "GET",
     "path": "/",
     "protocol": "HTTP/2",
     "req_x_forwarded_for": "10.0.15.215",
     "request_id": "c996b154-9299-4f00-b356-8cc66472e613",
     "resp_backend_service_time": "0",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2025-06-23T16:23:09.615Z",
     "total_duration": 0,
     "user_agent": "curl/8.7.1"
   }
   ```

   
## HTTP/2 for external services

1. Create a Backend resource that represents your external service. In this example, you configure a Backend for the `https://nghttp2.org/httpbin/` domain. This domain requires requests to be sent with the HTTP/2 protocol. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: http2
   spec:
     type: Static
     static:
       hosts:
         - host: nghttp2.org
           port: 80
       appProtocol: http2
   EOF
   ```

2. Create an HTTPRoute that routes requests to your Backend. 
   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: http2
     namespace: default
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "docs/snippets/namespace.md" >}}
     hostnames:
       - static.example
     rules:
       - backendRefs:
         - name: http2
           kind: Backend
           group: gateway.kgateway.dev 
         filters:
         - type: URLRewrite
           urlRewrite:
             hostname: nghttp2.org
             path:
              type: ReplacePrefixMatch
              replacePrefixMatch: /httpbin/
   EOF
   ```

3. Send a request to the `static.example` domain. The request is forwarded to the `nghttp2.org/httpbin/` path, which only accepts HTTP/2 requests. Verify that the request succeeds and that you get back a 200 HTTP response code. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing"  >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/ -H "host: static.example:8080" --http2-prior-knowledge 
   ```

   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/ -H "host: static.example" --http2-prior-knowledge 
   ```
   
   {{% /tab %}}
   {{< /tabs >}}
   
   Example output: 
   ```console {hl_lines=[8,9]}
   ...
   > GET / HTTP/2
   > Host: static.example:8080
   > User-Agent: curl/8.7.1
   > Accept: */*
   > 
   * Request completely sent off
   < HTTP/2 200 
   HTTP/2 200 
   < content-type: text/html; charset=utf-8
   content-type: text/html; charset=utf-8
   < content-length: 9649
   content-length: 9649
   < access-control-allow-origin: *
   access-control-allow-origin: *
   < access-control-allow-credentials: true
   access-control-allow-credentials: true
   < x-backend-header-rtt: 6.191667
   x-backend-header-rtt: 6.191667
   < alt-svc: h3=":443"; ma=3600
   alt-svc: h3=":443"; ma=3600
   < server: envoy
   server: envoy
   < via: 1.1 nghttpx
   via: 1.1 nghttpx
   < x-frame-options: SAMEORIGIN
   x-frame-options: SAMEORIGIN
   < x-xss-protection: 1; mode=block
   x-xss-protection: 1; mode=block
   < x-content-type-options: nosniff
   x-content-type-options: nosniff
   < x-envoy-upstream-service-time: 6504
   x-envoy-upstream-service-time: 6504
   < 
   ...
   ```

4. Get the access logs of your gateway proxy. 
   ```sh
   kubectl -n {{< reuse "docs/snippets/namespace.md" >}} logs deployments/http | tail -1 | jq --sort-keys
   ```
   
   Example output: 
   ```console {hl_lines=[9]}
   {
     "authority": "nghttp2.org",
     "backendCluster": "backend_default_http2_0",
     "backendHost": "139.162.123.134:80",
     "bytes_received": 0,
     "bytes_sent": 9649,
     "method": "GET",
     "path": "/",
     "protocol": "HTTP/2",
     "req_x_forwarded_for": "10.0.9.76",
     "request_id": "6e8baf82-2c2b-40cc-b5c0-d2d2295d3abf",
     "resp_backend_service_time": "313",
     "response_code": 200,
     "response_flags": "-",
     "start_time": "2025-06-23T16:25:22.639Z",
     "total_duration": 314,
     "user_agent": "curl/8.7.1"
   }
   ```
   




## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute nginx
kubectl delete pod nginx
kubectl delete service nginx
kubectl delete configmap nginx-conf
kubectl delete backend http2
kubectl delete httproute http2
```