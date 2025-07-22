---
title: Consistent hashing
weight: 20
---

Set up soft session affinity between a client and a backend service by using consistent hashing algorithms.

## About session affinity

Session affinity allows you to route requests for a particular session to the same backend service instance that served the initial request. This setup is particularly useful if you have a backend service that performs expensive operations and caches the output or data for subsequent requests. With session affinity, you make sure that the expensive operation is performed once and that subsequent requests can be served from the backend’s cache, which can significantly improve operational cost and response times for your clients.

## About consistent hashing

{{< reuse "docs/snippets/kgateway-capital.md" >}} allows you to set up soft session affinity between a client and a backend service by using the [Ringhash](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/load_balancing_policies/ring_hash/v3/ring_hash.proto.html) or [Maglev](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#maglev) consistent hashing algorithm. The hashing algorithm uses a property of the request, such as a cookie or header, and hashes this property with the address of a backend service instance that served the initial request. In subsequent requests, as long as the client sends the same header, the request is routed to the same backend service instance.

{{< callout type="info" >}}
Consistent hashing is less reliable than a "strong" or "sticky" session affinity implementation, such as session persistence, in which the backend service is encoded in a cookie or header and affinity can be maintained for as long as the backend service is available. With consistent hashing, affinity might be lost when an instance is added or removed from the backend service's pool, or if the gateway proxy restarts. To set up strong stickiness, see the [Session persistence](../session-persistence) docs.
{{< /callout >}}

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Configure session affinity with consistent hashing

First, define the Ringhash or Maglev hashing algorithm that you want to use for your backend app in a `BackendConfigPolicy`. Then, define the request property to hash in a {{< reuse "docs/snippets/trafficpolicy.md" >}} that you apply to the backend app's HTTPRoute.

### Define Ringhash or Maglev hashing

In the `loadBalancer` section of a BackendConfigPolicy resource, specify settings for either the Ringhash or Maglev hashing algorithm. 

* **Ringhash**: You can tune the ring size to balance memory usage vs load distribution precision. This way, you get more fine-grained control over how traffic is distributed across endpoint. However, this configurability might come at a performance cost, depending on your setup.
* **Maglev**: You use a fixed lookup table of 65,357 entries that is optimized for fast request routing with deterministic performance. This option is well-suited for general-purpose workloads that do not require custom tuning.

{{< tabs tabTotal="2" items="Ringhash,Maglev" >}}
{{% tab tabName="Ringhash" %}}
```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: example-ringhash-policy
  namespace: default
spec:
  targetRefs:
    - name: example-app
      group: ""
      kind: Service
  loadBalancer:
    ringHash:
      minimumRingSize: 1024
      maximumRingSize: 2048
    useHostnameForHashing: true
    closeConnectionsOnHostSetChange: true
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description | 
| -- | -- | 
| `minimumRingSize` | The minimum ring size. The size of the ring determines the number of hashes that can be assigned for each host and placed on the ring. The ring number is divided by the number of hosts that serve the request. For example, if you have 2 hosts and the minimum ring size is 1000, each host gets approximately 500 hashes in the ring. When a request is received, the request is assigned a hash in the ring, and therefore assigned to a particular host. Generally speaking, the larger the ring size is, the better distribution between hosts can be achieved. If not set, the minimum ring size defaults to 1024. |
| `maximumRingSize` | The maximum ring size. If not set, the maximum ring size defaults to 8 million. | 
| `useHostnameForHashing` | If set to true, the gateway proxy uses the hostname as the key to consistently hash to a backend host. If not set, defaults to using the resolved address of the hostname as the key. | 
| `closeConnectionsOnHostSetChange` | If set to true, the proxy drains all existing connections to a backend host whenever hosts are added or removed for a backend pool. | 

{{% /tab %}}
{{% tab tabName="Maglev" %}}
Note that no further settings for Maglev are required because it uses a fixed table size.

```yaml
kind: BackendConfigPolicy
apiVersion: gateway.kgateway.dev/v1alpha1
metadata:
  name: example-maglev-policy
  namespace: default
spec:
  targetRefs:
    - name: example-app
      group: ""
      kind: Service
  loadBalancer:
    maglev: {}
```
{{% /tab %}}
{{< /tabs >}}

### Define request properties

Define the request property to use, such as a header, cookie, or source IP address, in the `hashPolicies` section of a {{< reuse "docs/snippets/trafficpolicy.md" >}}. The algorithm hashes this property with the address of a backend service instance that served the initial request. The {{< reuse "docs/snippets/trafficpolicy.md" >}} references the backend app's HTTPRoute to apply the hashing algorithm to requests for that backend app.

The `header`, `cookie`, and `sourceIP` hash policies are mutually exclusive, in that a request can only have one property that the algorithm uses for hashing. However, you can define multiple different hash policies within one {{< reuse "docs/snippets/trafficpolicy.md" >}} by using the `terminal` field for each hash policy. If a policy has the `terminal: true` setting and the policy is matched, any subsequent hash policies are skipped. This field is useful for defining fallback policies, and limiting the amount of time spent generating hash keys.

{{< tabs tabTotal="3" items="Header,Cookie,SourceIP" >}}
{{% tab tabName="Header" %}}
```yaml
kubectl apply -f- <<EOF
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
metadata:
  name: example-header-hash-policy
  namespace: default
spec:
  targetRefs:
    - name: example-route
      group: gateway.networking.k8s.io
      kind: HTTPRoute
  hashPolicies:
    - header:
        name: "x-user-id"
      terminal: true
    - header:
        name: "x-session-id"
      terminal: false
EOF
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description | 
| -- | -- | 
| `header.name` | The expected header name to create the hash with. |
| `terminal` | If you define multiple `hashPolicies` in one {{< reuse "docs/snippets/trafficpolicy.md" >}}, you can use the `terminal` field to determine which policy is the priority. For example, in this policy, the `x-user-id` header has the `terminal: true` setting. This indicates that if the request has the `x-user-id` header, any subsequent policies (such as the `x-session-id` header in this example) are skipped. This field is useful for defining fallback policies, and limiting the amount of time spent generating hash keys. |
{{% /tab %}}
{{% tab tabName="Cookie" %}}
```yaml
kubectl apply -f- <<EOF
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
metadata:
  name: example-cookie-hash-policy
  namespace: default
spec:
  targetRefs:
    - name: example-route
      group: gateway.networking.k8s.io
      kind: HTTPRoute
  hashPolicies:
    - cookie:
        name: "session-id"
        path: "/api"
        ttl: 30m
        attributes:
          httpOnly: "true"
          secure: "true"
          sameSite: "Strict"
      terminal: true
EOF
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description | 
| -- | -- | 
| `cookie.name` | The expected cookie name to create the hash with. In this example, the cookie is named `session-id`. |
| `cookie.path` | The name of the path for the cookie, such as `/api` in this example. |
| `cookie.ttl` | If the cookie is not present, a cookie with this duration of time for validity is generated, such as 30 minutes in this example. |
| `cookie.attributes` | Define additional attributes for an HTTP cookie. This example sets three additional attirbutes: `httpOnly: true`, `secure: true`, and `sameSite: Strict`. |
| `terminal` | If you define multiple `hashPolicies` in one {{< reuse "docs/snippets/trafficpolicy.md" >}}, you can use the `terminal: true` setting to indicate the priority policy. |
{{% /tab %}}
{{% tab tabName="SourceIP" %}}
```yaml
kubectl apply -f- <<EOF
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
metadata:
  name: example-sourceip-hash-policy
  namespace: default
spec:
  targetRefs:
    - name: example-route
      group: gateway.networking.k8s.io
      kind: HTTPRoute
  hashPolicies:
    - sourceIP: {}
      terminal: true
EOF
```

{{< reuse "/docs/snippets/review-table.md" >}}

| Setting | Description | 
| -- | -- | 
| `sourceIP` | Hash based on the source IP address of the request. No further configuration is required. |
| `terminal` | If you define multiple `hashPolicies` in one {{< reuse "docs/snippets/trafficpolicy.md" >}}, you can use the `terminal: true` setting to indicate the priority policy. |
{{% /tab %}}
{{< /tabs >}}

## Verify the session affinity configuration {#verify}

To try out session affinity with consistent hashing, you can follow these steps to first define a Ringhash hashing algorithm in a BackendConfigPolicy for the httpbin sample app. Then, you define cookie settings to hash in a {{< reuse "docs/snippets/trafficpolicy.md" >}} that you apply to httpbin's HTTPRoute.

1. Scale the httpbin app up to two instances.
   ```sh 
   kubectl scale deployment httpbin -n httpbin --replicas=2
   ```
   
2. Verify that another instance of the httpbin app is created.
   ```sh
   kubectl get pods -n httpbin
   ```
   
   Example output:
   ```
   NAME                      READY   STATUS        RESTARTS   AGE
   httpbin-8d557795f-86hzg   3/3     Running       0          54s
   httpbin-8d557795f-h8ks9   3/3     Running       0          26m
   ```

3. Create a BackendConfigPolicy to configure the following Maglev algorithm for the httpbin app.
   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-ringhash-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       maglev: {}
   EOF
   ```

4. Create the following {{< reuse "docs/snippets/trafficpolicy.md" >}}, which defines the `session-id` cookie as the request property to hash with the address of an httpbin backend instance, and applies to the `httpbin` HTTPRoute.
   ```yaml
   kubectl apply -f- <<EOF
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   metadata:
     name: httpbin-cookie-hash-policy
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: gateway.networking.k8s.io
         kind: HTTPRoute
     hashPolicies:
       - cookie:
           name: "session-id"
           path: "/api"
           ttl: 30m
           attributes:
             httpOnly: "true"
             secure: "true"
             sameSite: "Strict"
         terminal: true
   EOF
   ```

5. Send a request to the httpbin app and verify that you see the `session-id` cookie in the `set-cookie` header of your response. The `-c` option stores the cookie in a local file on your machine so that you can use it in subsequent requests.
   {{< tabs tabTotal="2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   curl -i -c cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -i -c cookie-jar -k localhost:8080/headers \
   -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}} 
   
   Example output: 
   ```console {hl_lines=[8]}
   HTTP/1.1 200 OK
   access-control-allow-credentials: true
   access-control-allow-origin: *
   content-type: application/json; encoding=utf-8
   date: Wed, 16 Jul 2025 17:20:40 GMT
   content-length: 445
   x-envoy-upstream-service-time: 0
   set-cookie: session-id="Cg8xMC4yNDQuMC42OjgwODA="; HttpOnly
   server: envoy
   ...
   ```

6. Repeat the request a few more times. Include the cookie that you stored in the local file by using the `-b` option. Make sure to send these requests within the 30 minute cookie validity period.
   {{< tabs tabTotal= "2" items="LoadBalancer IP address or hostname,Port-forward for local testing" >}}
   {{% tab tabName="LoadBalancer IP address or hostname" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   for i in {1..10}; do
   curl -i -b cookie-jar -k localhost:8080/headers \
   -H "host: www.example.com:8080"; done
   ```
   {{% /tab %}}
   {{< /tabs >}}

7. Check the logs of each httpbin instance. Verify that only one of the instances served all 10 of the subsequent requests that you made.
   ```sh
   kubectl logs -n httpbin <httpbin-pod>
   ```

   Example output for one pod, in which all 10 subsequent requests (timestamps at `17:20`) are served after the previous 1 request (timestamp at `17:17`):
   ```
   Defaulted container "httpbin" out of: httpbin, curl
   go-httpbin listening on http://0.0.0.0:8080
   time="2025-07-16T17:17:09.8479" status=200 method="GET" uri="/headers" size_bytes=440 duration_ms=0.10 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:32.1077" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:40.7017" status=200 method="GET" uri="/headers" size_bytes=445 duration_ms=0.05 user_agent="curl/8.7.1" client_ip=10.244.0.7
   time="2025-07-16T17:20:49.5744" status=200 method="GET" uri="/headers" size_bytes=515 duration_ms=0.04 user_agent="curl/8.7.1" client_ip=10.244.0.7
   ...
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

1. Scale the httpbin app back down.
   ```sh 
   kubectl scale deployment httpbin -n httpbin --replicas=1
   ```

2. Delete the resources that you created.
   ```sh
   kubectl delete BackendConfigPolicy httpbin-ringhash-policy -n httpbin
   kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} httpbin-cookie-hash-policy -n httpbin
   ```