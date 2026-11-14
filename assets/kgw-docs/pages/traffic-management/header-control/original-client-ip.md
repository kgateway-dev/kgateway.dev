Configure how the gateway proxy determines the original client IP address when requests pass through load balancers, CDNs, or other proxies.

## About the client IP address {#about}

The gateway proxy uses the client IP address of a request in several places, such as to match the rules of an [ACL policy]({{< link-hextra path="/security/acl/" >}}), to apply [rate limits by remote address]({{< link-hextra path="/security/ratelimit/global/" >}}), to set the `X-Envoy-External-Address` header, and to log the `%DOWNSTREAM_REMOTE_ADDRESS%` value in [access logs]({{< link-hextra path="/security/access-logging/" >}}).

By default, the gateway proxy uses the source address of the downstream connection as the client IP address. The `X-Forwarded-For` (XFF) header that a client sends is not trusted to determine the client IP address. Before the gateway proxy forwards the request, it appends the source address of the connection to the XFF header.

When the gateway proxy runs behind a load balancer or proxy that terminates the client connection, the source address of the connection belongs to that proxy instead of the client. If the proxy works at the TCP level, such as a network load balancer, you can preserve the client address with the `externalTrafficPolicy: Local` setting on the gateway proxy Service or with [proxy protocol]({{< link-hextra path="/traffic-management/proxy-protocol/" >}}). If the proxy works at the HTTP level, such as an application load balancer or a CDN, it typically records the client address in the XFF header. In that case, configure the gateway proxy to trust the addresses that these proxies add to the XFF header.

You can use the following settings in the `spec.default.httpSettings` section of a ListenerPolicy to configure how the gateway proxy determines the client IP address.

| Setting | Description |
| -- | -- |
| `useRemoteAddress` | Defaults to `true`. When `true`, the gateway proxy uses the source address of the connection as the client IP address, unless you also set `xffNumTrustedHops`. When `false`, the gateway proxy takes the client IP address from the XFF header and stops appending to the XFF header, unless you set `skipXFFAppend` to `false`. When `false`, the gateway proxy also does not set the `X-Envoy-External-Address` header. |
| `xffNumTrustedHops` | The number of trusted proxies in front of the gateway proxy that append to the XFF header. If `useRemoteAddress` is `true` and you set this value to `N`, the client IP address is the `N`th address from the right of the XFF header that the gateway proxy receives. If `useRemoteAddress` is `false`, the client IP address is the `N+1`th address from the right, and a value of `0` uses the rightmost address. If the XFF header contains fewer addresses, the gateway proxy uses the source address of the connection. You cannot set this field together with `xffTrustedCIDRs`. |
| `xffTrustedCIDRs` | The CIDR ranges of your trusted proxies. If the source address of the connection is in one of these ranges, the gateway proxy reads the XFF header from right to left and uses the first address that is not in a trusted range as the client IP address. If all addresses in the XFF header are trusted, the leftmost address is used. If the source address of the connection is not in a trusted range, the gateway proxy uses the source address as the client IP address and appends it to the XFF header. You must set `useRemoteAddress` to `false` to use this field, and you cannot set this field together with `xffNumTrustedHops`. |
| `skipXFFAppend` | Set to `true` to forward the XFF header without appending the source address of the connection. If unset, the gateway proxy appends to the XFF header when `useRemoteAddress` is `true`, and does not append when `useRemoteAddress` is `false`. |

> [!WARNING]
> Trust the XFF header only for addresses that your own proxies add. If clients can reach the gateway proxy directly without passing through your trusted proxies, they can send a forged XFF header to set any client IP address, such as to bypass an ACL policy or a rate limit.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Default behavior {#default}

Review how the gateway proxy determines the client IP address without a ListenerPolicy.

1. Send a request to the httpbin app with an XFF header that sets the `203.0.113.10` client IP address.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output for a port-forward. The `X-Envoy-External-Address` header shows the client IP address that the gateway proxy determined. This address is the source address of the connection, `127.0.0.1`, and not the address in the XFF header that the client sent. If you use a LoadBalancer, the header shows the address of your load balancer or node instead. The XFF header that is forwarded to the httpbin app has another address appended to it. For connections from a loopback address, such as through a port-forward, the gateway proxy appends its own IP address, such as `10.244.0.7`. For other connections, the gateway proxy appends the source address of the connection.

   ```console {hl_lines=[15,16,18,19]}
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "127.0.0.1"
       ],
       "X-Forwarded-For": [
         "203.0.113.10,10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "b9e27a1c-3f6d-4a8e-9c52-7d1e0f4a6b38"
       ]
     }
   }
   ```

## Trust a number of proxy hops {#trusted-hops}

Use the `xffNumTrustedHops` setting when you know how many proxies that append to the XFF header are in front of the gateway proxy. For example, if all requests pass through one application load balancer, set `xffNumTrustedHops` to `1`.

1. Create a ListenerPolicy that trusts one proxy hop in the XFF header.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: client-ip
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         xffNumTrustedHops: 1
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}} For more information about the available fields, see the [API reference]({{< link-hextra path="/reference/api/#httpsettings" >}}).

   | Setting | Description |
   | -- | -- |
   | `spec.targetRefs` | The Gateway that this policy applies to. The policy applies to all HTTP and HTTPS listeners on the Gateway. |
   | `spec.default.httpSettings.xffNumTrustedHops` | The number of trusted proxies that append to the XFF header. Because `useRemoteAddress` is `true` by default, a value of `1` sets the client IP address to the rightmost address in the XFF header that the gateway proxy receives. |

2. Repeat the request with the `203.0.113.10` address in the XFF header. In this example, your curl request plays the role of the trusted load balancer that adds the client address to the XFF header. Verify that the `X-Envoy-External-Address` header now shows the `203.0.113.10` address from the XFF header.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[15,16]}
   {
     "headers": {
       "Accept": [
         "*/*"
       ],
       "Host": [
         "www.example.com"
       ],
       "User-Agent": [
         "curl/8.7.1"
       ],
       "X-Envoy-Expected-Rq-Timeout-Ms": [
         "15000"
       ],
       "X-Envoy-External-Address": [
         "203.0.113.10"
       ],
       "X-Forwarded-For": [
         "203.0.113.10,10.244.0.7"
       ],
       "X-Forwarded-Proto": [
         "http"
       ],
       "X-Request-Id": [
         "4c8d2e6f-1a7b-4f3e-8d95-2b6c0e9a7f14"
       ]
     }
   }
   ```

3. Send a request with two addresses in the XFF header. Verify that the gateway proxy uses only the rightmost address, `198.51.100.7`, as the client IP address. Because only one proxy hop is trusted, the gateway proxy ignores the `203.0.113.10` address that a client might have forged.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10, 198.51.100.7"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10, 198.51.100.7"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[2,3,5,6]}
   ...
       "X-Envoy-External-Address": [
         "198.51.100.7"
       ],
       "X-Forwarded-For": [
         "203.0.113.10, 198.51.100.7,10.244.0.7"
       ],
   ...
   ```

## Trust proxy CIDR ranges {#trusted-cidrs}

Use the `xffTrustedCIDRs` setting when you know the IP address ranges of your proxies, but the number of proxies that a request passes through can vary.

1. Create a ListenerPolicy that trusts the XFF header for connections from specific CIDR ranges. You must set `useRemoteAddress` to `false` to use trusted CIDR ranges.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: client-ip
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         useRemoteAddress: false
         xffTrustedCIDRs:
         - 10.0.0.0/8
         - 127.0.0.1/32
   EOF
   ```

   {{< reuse "kgw-docs/snippets/review-table.md" >}}

   | Setting | Description |
   | -- | -- |
   | `spec.default.httpSettings.useRemoteAddress` | Set to `false` to take the client IP address from the XFF header. This setting is required for `xffTrustedCIDRs`. |
   | `spec.default.httpSettings.xffTrustedCIDRs` | The CIDR ranges of your trusted proxies. Replace `10.0.0.0/8` with the address ranges of your load balancers or proxies. The `127.0.0.1/32` range trusts connections through a port-forward for local testing. Remove it in production setups. With this configuration, a request from a trusted address with an XFF header of `198.51.100.7, 203.0.113.10, 10.0.0.5` gets the client IP address `203.0.113.10`, because `10.0.0.5` is in a trusted range. The gateway proxy does not set the `X-Envoy-External-Address` header in this mode. |

2. Port-forward the gateway proxy on port 19000 to open the Envoy admin interface.

   ```sh
   kubectl port-forward deploy/http -n {{< reuse "kgw-docs/snippets/namespace.md" >}} 19000
   ```

3. In the Envoy configuration, verify that the original IP detection extension includes your trusted CIDR ranges. Alternatively, you can open the [Envoy admin interface](http://localhost:19000/config_dump) and look for the `original_ip_detection_extensions` setting in the config dump.

   ```sh
   curl -s localhost:19000/config_dump | jq '[.. | objects | select(has("original_ip_detection_extensions")) | {use_remote_address, original_ip_detection_extensions}]'
   ```

   Example output:

   ```console
   [
     {
       "use_remote_address": false,
       "original_ip_detection_extensions": [
         {
           "name": "envoy.http.original_ip_detection.xff",
           "typed_config": {
             "@type": "type.googleapis.com/envoy.extensions.http.original_ip_detection.xff.v3.XffConfig",
             "xff_trusted_cidrs": {
               "cidrs": [
                 {
                   "address_prefix": "10.0.0.0",
                   "prefix_len": 8
                 },
                 {
                   "address_prefix": "127.0.0.1",
                   "prefix_len": 32
                 }
               ]
             }
           }
         }
       ]
     }
   ]
   ```

## Stop appending to the XFF header {#skip-xff-append}

By default, the gateway proxy appends the source address of the connection to the XFF header. If your backends expect the XFF header exactly as your trusted proxies set it, you can turn off appending.

1. Create a ListenerPolicy that sets `skipXFFAppend` to `true`.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: ListenerPolicy
   metadata:
     name: client-ip
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: Gateway
       name: http
     default:
       httpSettings:
         skipXFFAppend: true
   EOF
   ```

2. Send a request with an XFF header. Verify that the XFF header that the httpbin app receives contains only the `203.0.113.10` address that you sent.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl localhost:8080/headers -H "host: www.example.com" \
     -H "X-Forwarded-For: 203.0.113.10"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```console {hl_lines=[5,6]}
   ...
       "X-Envoy-External-Address": [
         "127.0.0.1"
       ],
       "X-Forwarded-For": [
         "203.0.113.10"
       ],
   ...
   ```

## Cleanup

{{< reuse "kgw-docs/snippets/cleanup.md" >}}

```sh
kubectl delete listenerpolicy client-ip -n {{< reuse "kgw-docs/snippets/namespace.md" >}} --ignore-not-found
```
