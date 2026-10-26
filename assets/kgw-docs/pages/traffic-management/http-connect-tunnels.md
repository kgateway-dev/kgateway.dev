## About HTTP CONNECT tunnels

If your environment requires egress traffic to leave through a forward proxy, you can tunnel connections from a Static {{< reuse "kgw-docs/snippets/backend.md" >}} through that proxy. The gateway proxy sends an HTTP `CONNECT` request to the forward proxy, and the forward proxy opens the connection to the destination. Without a tunnel, the gateway proxy connects to the destination directly.

You configure the tunnel by using the `spec.tunnel` field of a BackendConfigPolicy and reference the forward proxy. You can optionally add headers to the `CONNECT` request, such as `Proxy-Authorization`. The headers are sent to the forward proxy only, not to the destination.

Follow these rules when you configure a tunnel:

* The destination that you want to tunnel must be a Static {{< reuse "kgw-docs/snippets/backend.md" >}} that has exactly one host. Other destination types, and Static destinations with multiple hosts, are not supported.
* Do not set `healthCheck`, `tcpKeepalive`, or `upstreamProxyProtocol` in any BackendConfigPolicy that applies to the same {{< reuse "kgw-docs/snippets/backend.md" >}}.
* Reference a forward proxy that the gateway proxy can resolve. The forward proxy must be a Service or a Static {{< reuse "kgw-docs/snippets/backend.md" >}}.
* Do not tunnel the connection to the forward proxy itself.

> [!NOTE]
> Looking to accept `CONNECT` requests from clients at the gateway? See the [HTTP protocol upgrades]({{< link-hextra path="/traffic-management/http-upgrades/" >}}) guide instead.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Tunnel a Static backend through a forward proxy {#tunnel-static-backend}

Send connections for a Static {{< reuse "kgw-docs/snippets/backend.md" >}} through the forward proxy. In this example, the destination is the httpbin app. Only the `CONNECT` request includes the `Proxy-Authorization` header, and the header value comes from a Secret.

1. Deploy a forward proxy. In this guide, you use Squid as the forward proxy. The configuration allows `CONNECT` requests to port 8000 only, which is the port of the httpbin sample app, and logs the `Proxy-Authorization` header so that you can verify later that the tunnel was used.

   The following Squid configuration does not enforce authentication or check credentials. In a production environment, configure your forward proxy to authenticate requests.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: egress-proxy-config
     namespace: httpbin
   data:
     squid.conf: |
       max_filedescriptors 1024
       http_port 3128
       acl httpbin_port port 8000
       acl connect_method method CONNECT
       http_access allow connect_method httpbin_port
       http_access deny all
       logformat tunnel %>a %rm %ru %>Hs "Proxy-Authorization: %{Proxy-Authorization}>h"
       access_log stdio:/var/log/squid/access.log tunnel
       cache deny all
   ---
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: egress-proxy
     namespace: httpbin
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: egress-proxy
     template:
       metadata:
         labels:
           app: egress-proxy
       spec:
         containers:
         - name: squid
           image: ubuntu/squid:latest
           ports:
           - containerPort: 3128
           volumeMounts:
           - name: config
             mountPath: /etc/squid/squid.conf
             subPath: squid.conf
         volumes:
         - name: config
           configMap:
             name: egress-proxy-config
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: egress-proxy
     namespace: httpbin
   spec:
     selector:
       app: egress-proxy
     ports:
     - port: 3128
       targetPort: 3128
   EOF
   ```

2. Verify that the forward proxy is running.

   ```sh
   kubectl get pods -n httpbin -l app=egress-proxy
   ```

   Example output:

   ```console
   NAME                            READY   STATUS    RESTARTS   AGE
   egress-proxy-59c7db587b-4jzsq   1/1     Running   0          20s
   ```

3. Create a Static {{< reuse "kgw-docs/snippets/backend.md" >}} for the httpbin app.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
   metadata:
     name: httpbin-via-proxy
     namespace: httpbin
   spec:
     type: Static
     static:
       hosts:
       - host: httpbin.httpbin.svc.cluster.local
         port: 8000
   EOF
   ```

4. Create a Secret with a sample credential for the forward proxy. The Squid proxy in this guide does not check credentials, so the Secret is not required for the tunnel to work. You add it to show how to send a header, such as `Proxy-Authorization`, with the `CONNECT` request without putting the value in the policy.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: v1
   kind: Secret
   metadata:
     name: egress-proxy-credentials
     namespace: httpbin
   type: Opaque
   stringData:
     authorization: Basic dXNlcjpwYXNz
   EOF
   ```

5. Create a BackendConfigPolicy that tunnels connections to the {{< reuse "kgw-docs/snippets/backend.md" >}} through the forward proxy.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: BackendConfigPolicy
   metadata:
     name: httpbin-tunnel
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.kgateway.dev
       kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
       name: httpbin-via-proxy
     tunnel:
       proxy:
         backendRef:
           name: egress-proxy
           port: 3128
       headers:
       - name: Proxy-Authorization
         secretRef:
           name: egress-proxy-credentials
           key: authorization
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Field | Description |
   | -- | -- |
   | `targetRefs` | Targets the `httpbin-via-proxy` Static {{< reuse "kgw-docs/snippets/backend.md" >}}. |
   | `tunnel.proxy.backendRef` | The `egress-proxy` Service on port 3128, which exposes the Squid forward proxy that you deployed earlier. The gateway proxy sends the `CONNECT` request to this forward proxy. |
   | `tunnel.headers` | Adds the `Proxy-Authorization` header to the `CONNECT` request. The value comes from the `egress-proxy-credentials` Secret. Note that any headers in the `spec.tunnel.headers` field are part of the `CONNECT` request. They are not sent to the destination.|

6. Verify that the BackendConfigPolicy is accepted. If the status shows `Accepted=False`, check the message for the reason, such as an unsupported destination setting.

   ```sh
   kubectl get backendconfigpolicy httpbin-tunnel -n httpbin -o jsonpath='{.status.ancestors[0].conditions[?(@.type=="Accepted")]}'
   ```

   Example output:

   ```console
   {"message":"Policy accepted","reason":"Valid","status":"True","type":"Accepted", ...}
   ```

7. Create an HTTPRoute that routes requests for the `tunnel.example` hostname to the {{< reuse "kgw-docs/snippets/backend.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: HTTPRoute
   metadata:
     name: tunnel
     namespace: httpbin
   spec:
     parentRefs:
     - name: http
       namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
     hostnames:
     - tunnel.example
     rules:
     - backendRefs:
       - name: httpbin-via-proxy
         group: gateway.kgateway.dev
         kind: {{< reuse "kgw-docs/snippets/backend.md" >}}
   EOF
   ```

8. Send a request to the httpbin app through the gateway proxy. Verify that you get back a 200 HTTP response.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -i http://$INGRESS_GW_ADDRESS:8080/headers -H "host: tunnel.example"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -i localhost:8080/headers -H "host: tunnel.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console
   HTTP/1.1 200 OK
   ...
   ```

9. Check the access log of the forward proxy. Verify that the log contains a `CONNECT` request to the httpbin app and that you see the `Proxy-Authorization` header. This log entry confirms that the gateway proxy connected to httpbin through the forward proxy.

   ```sh
   kubectl exec -n httpbin deploy/egress-proxy -- cat /var/log/squid/access.log
   ```

   Example output:

   ```console
   10.244.0.32 CONNECT httpbin.httpbin.svc.cluster.local:8000 200 "Proxy-Authorization: Basic dXNlcjpwYXNz"
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete httproute tunnel -n httpbin --ignore-not-found
kubectl delete backendconfigpolicy httpbin-tunnel -n httpbin --ignore-not-found
kubectl delete {{< reuse "kgw-docs/snippets/backend.md" >}} httpbin-via-proxy -n httpbin --ignore-not-found
kubectl delete secret egress-proxy-credentials -n httpbin --ignore-not-found
kubectl delete deployment,service egress-proxy -n httpbin --ignore-not-found
kubectl delete configmap egress-proxy-config -n httpbin --ignore-not-found
```
