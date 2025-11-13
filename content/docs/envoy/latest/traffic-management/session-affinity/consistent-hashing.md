---
title: Consistent hashing
weight: 20
---

Set up soft session affinity between a client and a backend service by using consistent hashing algorithms.

## About session affinity

Session affinity allows you to route requests for a particular session to the same backend service instance that served the initial request. This setup is particularly useful if you have a backend service that performs expensive operations and caches the output or data for subsequent requests. With session affinity, you make sure that the expensive operation is performed once and that subsequent requests can be served from the backend’s cache, which can significantly improve operational cost and response times for your clients.

## About consistent hashing

{{< reuse "docs/snippets/kgateway-capital.md" >}} allows you to set up soft session affinity between a client and a backend service by using the [Ringhash](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/load_balancing_policies/ring_hash/v3/ring_hash.proto.html) or [Maglev](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#maglev) consistent hashing algorithm. The hashing algorithm uses a property of the request, such as a cookie, header, or source IP address, and hashes this property with the address of a backend service instance that served the initial request. In subsequent requests, as long as the client sends the same request property, the request is routed to the same backend service instance.

Request properties are configured in the `loadBalancer.hashPolicies` section of a BackendConfigPolicy. The header, cookie, and sourceIP hash policies are mutually exclusive, in that a request can only have one property that the algorithm uses for hashing. However, you can define multiple different hash policies within one BackendConfigPolicy by using the `terminal` field for each hash policy. If a policy has the `terminal: true` setting and the policy is matched, any subsequent hash policies are skipped. This field is useful for defining fallback policies, and limiting the amount of time spent generating hash keys.

{{< callout type="info" >}}
Consistent hashing is less reliable than a "strong" or "sticky" session affinity implementation, such as session persistence, in which the backend service is encoded in a cookie or header and affinity can be maintained for as long as the backend service is available. With consistent hashing, affinity might be lost when an instance is added or removed from the backend service's pool, or if the gateway proxy restarts. To set up strong stickiness, see the [Session persistence](../session-persistence) docs.
{{< /callout >}}

## Before you begin 

{{< reuse "docs/snippets/prereq.md" >}}

## Set up consistent hashing 

See the following links to get started: 
* [Ringhash](#ringhash)
* [Maglev](#maglev)

### Ringhash

Ringhash allows you to tune the ring size to balance memory usage vs load distribution precision. This way, you get more fine-grained control over how traffic is distributed across endpoint. However, this configurability might come at a performance cost, depending on your setup. To learn more about Ringhash, see the [Envoy documentation](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/load_balancing_policies/ring_hash/v3/ring_hash.proto.html). 

1. Create a BackendConfigPolicy that uses the request property of your choice. 
   {{< tabs tabTotal="3" items="Headers,Cookies,Source IP address" >}}
   {{% tab tabName="Headers" %}}

   Create a consistent hash by using a specific request header.

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       ringHash:
         minimumRingSize: 1024
         maximumRingSize: 2048
         hashPolicies:
         - header:
             name: "x-user-id"
           terminal: true
         - header:
             name: "x-session-id"
           terminal: false
         useHostnameForHashing: true
       closeConnectionsOnHostSetChange: true
   EOF
   ``` 

   {{< reuse "/docs/snippets/review-table.md" >}}

   | Setting | Description | 
   | -- | -- | 
   | `ringHash.minimumRingSize` | The minimum ring size. The size of the ring determines the number of hashes that can be assigned for each host and placed on the ring. The ring number is divided by the number of hosts that serve the request. For example, if you have 2 hosts and the minimum ring size is 1000, each host gets approximately 500 hashes in the ring. When a request is received, the request is assigned a hash in the ring, and therefore assigned to a particular host. Generally speaking, the larger the ring size is, the better distribution between hosts can be achieved. If not set, the minimum ring size defaults to 1024. |
   | `ringHash.maximumRingSize` | The maximum ring size. If not set, the maximum ring size defaults to 8 million. | 
   | `useHostnameForHashing` | If set to true, the gateway proxy uses the hostname as the key to consistently hash to a backend host. If not set, defaults to using the resolved address of the hostname as the key. | 
   | `header.name` | The expected header name to create the hash with. |
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal` field to determine which policy is the priority. For example, in this policy, the `x-user-id` header has the `terminal: true` setting. This indicates that if the request has the `x-user-id` header, any subsequent policies (such as the `x-session-id` header in this example) are skipped. This field is useful for defining fallback policies, and limiting the amount of time spent generating hash keys. |
   | `closeConnectionsOnHostSetChange` | If set to true, the proxy drains all existing connections to a backend host whenever hosts are added or removed for a backend pool. | 


   {{% /tab %}}
   {{% tab tabName="Cookies" %}}

   Create a consistent hash by using a cookie. 

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       ringHash:
         minimumRingSize: 1024
         maximumRingSize: 2048
         hashPolicies:
         - cookie:
             name: "session-id"
             path: "/api"
             ttl: 30m
             httpOnly: true
             secure: true
             sameSite: "Strict"
           terminal: true
   EOF
   ```

   {{< reuse "/docs/snippets/review-table.md" >}}

   | Setting | Description | 
   | -- | -- | 
   | `ringHash.minimumRingSize` | The minimum ring size. The size of the ring determines the number of hashes that can be assigned for each host and placed on the ring. The ring number is divided by the number of hosts that serve the request. For example, if you have 2 hosts and the minimum ring size is 1000, each host gets approximately 500 hashes in the ring. When a request is received, the request is assigned a hash in the ring, and therefore assigned to a particular host. Generally speaking, the larger the ring size is, the better distribution between hosts can be achieved. If not set, the minimum ring size defaults to 1024. |
   | `ringHash.maximumRingSize` | The maximum ring size. If not set, the maximum ring size defaults to 8 million. | 
   | `cookie.name` | The expected cookie name to create the hash with. In this example, the cookie is named `session-id`. |
   | `cookie.path` | The name of the path for the cookie, such as `/api` in this example. |
   | `cookie.ttl` | If the cookie is not present, a cookie with this duration of time for validity is generated, such as 30 minutes in this example. |
   | `cookie.attributes` | Define additional attributes for an HTTP cookie. This example sets three additional attirbutes: `httpOnly: true`, `secure: true`, and `sameSite: Strict`. |
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal: true` setting to indicate the priority policy. |


   {{% /tab %}}
   {{% tab tabName="Source IP" %}}

   Create a consistent hash by using the source IP address. 

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       ringHash:
         minimumRingSize: 1024
         maximumRingSize: 2048
         hashPolicies:
         - sourceIP: {}
           terminal: true
   EOF
   ```

   | Setting | Description | 
   | -- | -- | 
   | `ringHash.minimumRingSize` | The minimum ring size. The size of the ring determines the number of hashes that can be assigned for each host and placed on the ring. The ring number is divided by the number of hosts that serve the request. For example, if you have 2 hosts and the minimum ring size is 1000, each host gets approximately 500 hashes in the ring. When a request is received, the request is assigned a hash in the ring, and therefore assigned to a particular host. Generally speaking, the larger the ring size is, the better distribution between hosts can be achieved. If not set, the minimum ring size defaults to 1024. |
   | `ringHash.maximumRingSize` | The maximum ring size. If not set, the maximum ring size defaults to 8 million. | 
   | `sourceIP` | Hash based on the source IP address of the request. No further configuration is required. |
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal: true` setting to indicate the priority policy. |


   {{% /tab %}}
   {{< /tabs >}}
   
2. Continue with [Verify consistent hashing](#verify). 


### Maglev

With Maglev, you use a fixed lookup table of 65,357 entries that is optimized for fast request routing with deterministic performance. This option is well-suited for general-purpose workloads that do not require custom tuning. For more information, see the [Envoy docs](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#maglev).

1. Create a BackendConfigPolicy that uses the request property of your choice. 
   {{< tabs items="Headers,Cookies,Source IP address" tabTotal="3" >}}
   {{% tab tabName="Headers"  %}}

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       maglev:
         hashPolicies:
         - header:
             name: "x-user-id"
           terminal: true
         - header:
             name: "x-session-id"
           terminal: false
         useHostnameForHashing: true
       closeConnectionsOnHostSetChange: true
   EOF
   ``` 

   {{< reuse "/docs/snippets/review-table.md" >}}

   | Setting | Description | 
   | -- | -- | 
   | `header.name` | The expected header name to create the hash with. |
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal` field to determine which policy is the priority. For example, in this policy, the `x-user-id` header has the `terminal: true` setting. This indicates that if the request has the `x-user-id` header, any subsequent policies (such as the `x-session-id` header in this example) are skipped. This field is useful for defining fallback policies, and limiting the amount of time spent generating hash keys. |
   | `useHostnameForHashing` | If set to true, the gateway proxy uses the hostname as the key to consistently hash to a backend host. If not set, defaults to using the resolved address of the hostname as the key. | 
   | `closeConnectionsOnHostSetChange` | If set to true, the proxy drains all existing connections to a backend host whenever hosts are added or removed for a backend pool. | 

   {{% /tab %}}
   {{% tab tabName="Cookies" %}}

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       maglev:
         hashPolicies:
         - cookie:
             name: "session-id"
             path: "/api"
             ttl: 30m
             httpOnly: true
             secure: true
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
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal: true` setting to indicate the priority policy. |

   {{% /tab %}}
   {{% tab tabName="Source IP" %}}

   ```yaml
   kubectl apply -f- <<EOF
   kind: BackendConfigPolicy
   apiVersion: gateway.kgateway.dev/v1alpha1
   metadata:
     name: httpbin-hash
     namespace: httpbin
   spec:
     targetRefs:
       - name: httpbin
         group: ""
         kind: Service
     loadBalancer:
       maglev:
         hashPolicies:
         - sourceIP: {}
           terminal: true
   EOF
   ```

   | Setting | Description | 
   | -- | -- | 
   | `sourceIP` | Hash based on the source IP address of the request. No further configuration is required. |
   | `terminal` | If you define multiple `hashPolicies` in one BackendConfigPolicy, you can use the `terminal: true` setting to indicate the priority policy. |

   {{% /tab %}}
   {{< /tabs >}}
   
2. Continue with [Verify consistent hashing](#verify). 


## Verify consistent hashing {#verify}

Send a few requests to the httpbin app and verify that the request is served by the same backend instance. 

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

3. Test consistent hashing by sending multiple requests to the httpbin app and verifying that all requests are served by the same backend instance. Note that the verification steps vary depending on the hashing policy that you defined. 
   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   
   * **Headers**: 
     ```sh
     for i in {1..10}; do curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
      -H "x-user-id: me" \
      -H "host: www.example.com"; done
     ```
     
   * **Source IP address**: 
     ```sh
     for i in {1..10}; do curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
      -H "host: www.example.com"; done
     ```
     
   * **Cookies**: 
     1. Send a request to the httpbin app and verify that you get back a `set-cookie` header with a `session-id`. 
        ```sh
        curl -i -c cookie-jar -k http://$INGRESS_GW_ADDRESS:8080/headers \
        -H "host: www.example.com"
        ```
        
        Example output: 
        ```console 
        set-cookie: session-id="76fe9617cf960748"; Max-Age=1800; Path=/api; Secure=true; HttpOnly=true; SameSite=Strict; HttpOnly
        ```
     
     2. Send a few more requests to the httpbin app and include the session ID from the previous step. 
        ```sh
        for i in {1..10}; do
        curl -i -b session-id="<sessionID>" -k http://$INGRESS_GW_ADDRESS:8080/headers \
        -H "host: www.example.com"; done
        ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
  
   * **Headers**
     ```sh
     for i in {1..10}; do curl -vik localhost:8080/headers \
      -H "x-user-id: me" \
      -H "host: www.example.com"; done
     ```
   
   * **Source IP address**
     ```sh
     for i in {1..10}; do curl -vik localhost:8080/headers \
      -H "host: www.example.com"; done
     ```
     
   * **Cookies**: 
     1. Send a request to the httpbin app and verify that you get back a `set-cookie` header with a `session-id`. 
        ```sh
        curl -i -c -k localhost:8080/headers \
        -H "host: www.example.com"
        ```
        
        Example output: 
        ```console 
        set-cookie: session-id="76fe9617cf960748"; Max-Age=1800; Path=/api; Secure=true; HttpOnly=true; SameSite=Strict; HttpOnly
        ```
     
     2. Send a few more requests to the httpbin app and include the session ID from the previous step. 
        ```sh
        for i in {1..10}; do
        curl -i -b session-id="<sessionID>" -k localhost:8080/headers \
        -H "host: www.example.com"; done
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
   kubectl delete BackendConfigPolicy httpbin-hash -n httpbin
   ```
  