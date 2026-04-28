Use an IP-based access control list (ACL) to allow or deny HTTP requests based on the client's source IP address.

## About ACL

The HTTP ACL filter evaluates every incoming HTTP request at Layer 7 against a set of IP-based rules and either allows or denies the request based on the client's source IP address (`source.address`). ACL rules are defined in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. 

The following ACL rules and configuration options apply: 

**Default fail closed**

If the source IP address cannot be determined, the request is denied by default (fail-closed).

**Defining rules with CIDR ranges and IP addresses**

Each rule contains one or more CIDR blocks (for example, `10.0.0.0/8` or `2001:db8::/32`) or bare IP addresses. A bare IP without a prefix is treated as a single host with a `/32` prefix for IPv4 and `/128` for IPv6. Multiple CIDRs that share the same action can be grouped into a single rule entry. Every rule requires a `defaultAction` (`allow` or `deny`) that applies when no rule matches the client IP. See [Default deny with an allowlist](#default-deny-with-an-allowlist) and [Default allow with a denylist](#default-allow-with-a-denylist) for more information.

**Mixing allow and deny rules with longest-prefix matching**

You can mix `allow` and `deny` actions within the same {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. When a client IP matches more than one rule, the most specific CIDR prefix always wins, regardless of the rule order that you specified in the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource. A `/32` single-host rule takes precedence over a `/16` subnet rule, which takes precedence over a `/8` range rule. With this capability, you can "punch holes" in to broader CIDR ranges. For example, you can deny an entire `10.0.0.0/8` range, while allowing a specific `10.1.0.0/16` subnet within that CIDR. For an example, see [Hole-punching with named rules](#hole-punching-with-named-rules).

**Custom deny responses and surfacing the block reason**

By default, request are denied with a 403 HTTP response. You can customize the HTTP response code and add extra headers to a response. For an example, see [Custom deny response](#custom-deny-response). 

You can also add the name of the rule that denied the request to your response header. For an example, see [Default allow with a denylist](#default-allow-with-a-denylist).

**Access logs and metrics**

On every denial, the Envoy filter writes Envoy dynamic metadata under the `dev.kgateway.http.acl` namespace with the `blocked-by` key. You can access this metadata by using the `%DYNAMIC_METADATA(dev.kgateway.http.acl:blocked-by)%` string in your access log configuration. 

The following table shows the values that you can expect in your access logs: 

| `blocked-by` value | Meaning |
|---|---|
| Rule's `name` | The name of the rule that matched the source IP address and denied the request.  |
| `"rule"` | If the rule that matched the IP address does not have a name, the access logs show `"rule"`. |
| `"default"` | If no rule matched the source IP address and the request was denied by the default action, the access logs show `defaultAction`.  |
| `"unknown-ip"` | If the source IP address could not be parsed, the access logs show `"unknown-ip"`.  |

The filter also increments the gateway proxy's `dev.kgateway.http.acl.blocked` metric on every denial. You can access the Envoy admin interface to monitor this metric. For more information, see [Monitor ACL blocks](#monitor-acl-blocks).

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up an ACL policy

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to define your ACL rules.

The following examples walk through common ACL configurations with the httpbin sample app.

### Default deny with an allowlist

Deny all requests by default, unless they come from an IP address that is part of a specific CIDR range. 

1. Create the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that denies all traffic by default and allows only requests from the `10.0.0.0/8` subnet. The policy targets the `httpbin` HTTPRoute that you set up as part of the prerequisites.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: acl-allowlist
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     acl:
       defaultAction: deny
       rules:
       - cidrs:
         - 10.0.0.0/8
         action: allow
   EOF
   ```

   {{< reuse "docs/snippets/review-table.md" >}} For more information, see the [API docs]({{< link-hextra path="/reference/api/#aclpolicy" >}}).

   | Field | Description |
   |---|---|
   | `targetRefs` | The policy targets the `httpbin` HTTPRoute resource that you created as part of the prerequisites. |
   | `defaultAction` | Fallback action when no rule matches the client IP address. This example denies all traffic by default, unless it is explicitly allowed by one of the IP addresses that are defined in the `rules` section.  |
   | `rules[].cidrs` | Define the CIDR blocks or IP addresses that you want to allow or deny.   |
   | `rules[].action` | Define the action to take when the client IP address matches any CIDR block. This example allows requests from the specified CIDR range. |

2. Send a request to the httpbin app from outside the cluster. Verify that your request is denied with a 403 response, because the request comes from a public IP address that is not in the `10.0.0.0/8` CIDR range.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com" | head -1
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com" | head -1
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 403 Forbidden
   ```

3. Log into the httpbin pod to run a curl request from within the cluster. By default, Kubernetes assigns pod IP addresses from the `10.0.0.0/8` range. Because this range matches the allow rule, you get back a 200 HTTP response.

   ```sh
   kubectl exec -n httpbin deploy/httpbin -c curl -- curl -vi \
     http://http.{{< reuse "docs/snippets/namespace.md" >}}.svc.cluster.local:8080/status/200 \
     -H "host: www.example.com" | head -1
   ```

   Example output:
   ```console
   HTTP/1.1 200 OK
   ```

### Default allow with a denylist

Allow all traffic by default, but block traffic from specific CIDR ranges. When a request is blocked, the name of the matched rule is added as a response header so that you can track which rule denied the request. 

1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to allow all traffic by default and block IP addresses from [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) private ranges. The `denyResponse.blockedByHeaderName` field adds a response header on every denial with the name of the matched rule.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: acl-allowlist
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     acl:
       defaultAction: allow
       denyResponse:
         blockedByHeaderName: X-Blocked-By
       rules:
       - name: block-rfc1918
         cidrs:
         - 10.0.0.0/8
         - 172.16.0.0/12
         - 192.168.0.0/16
         action: deny
   EOF
   ```

   | Field | Description |
   |---|---|
   | `rules[].name` | Optional rule identifier. On denial, the name is written to Envoy dynamic metadata under `dev.kgateway.http.acl/blocked-by`. You can reference it in access logs with `%DYNAMIC_METADATA(dev.kgateway.http.acl:blocked-by)%`. If you also define `denyResponse.blockedByHeaderName`, the rule name is added to the response header that you specify when a request is denied.   |
   | `rules[].cidrs` | Define the CIDR ranges that you want to deny.  |
   | `denyResponse.blockedByHeaderName` | Add a response header with this name on every denial. The header value is set to the matched rule's `name`. If no rule name was specified, the header is set to `"rule"` for all denied requests. If the denial was triggered due to the default action, the header value is set to `"default"`.  |

2. Send a request to the httpbin app. Verify that your request succeeds with a 200 response, because the request comes from a public IP address that is not in any of the denied RFC 1918 ranges.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com" | head -1
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com" | head -1
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   ```

3. Log into the httpbin pod to run a curl request from within the cluster.  By default, Kubernetes assigns pod IP addresses from the `10.0.0.0/8` range. Because this range matches the deny rule, you get back a 403 HTTP response with the `x-blocked-by: block-rfc1918` header.

   ```sh
   kubectl exec -n httpbin deploy/httpbin -c curl -- curl -vi \
     http://http.{{< reuse "docs/snippets/namespace.md" >}}.svc.cluster.local:8080/status/200 \
     -H "host: www.example.com"
   ```

   Example output:
   ```console
   HTTP/1.1 403 Forbidden
   x-blocked-by: block-rfc1918
   ...
   ```

### Hole-punching

Use longest-prefix matching to allow a specific subnet within a broader denied range. When a client IP address matches more than one rule, the most specific CIDR prefix wins, indepedent of the rule order that you defined in the {{< reuse "docs/snippets/trafficpolicy.md" >}}. 

1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to deny the entire `10.0.0.0/8` range, but punch a hole to allow requests from the `10.1.0.0/16` range without including the host `10.1.2.3`. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: acl-allowlist
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     acl:
       defaultAction: allow
       rules:
       - name: block-internal-range
         cidrs:
         - 10.0.0.0/8
         action: deny
       - name: allow-trusted-subnet
         cidrs:
         - 10.1.0.0/16
         action: allow
       - name: block-rogue-host
         cidrs:
         - 10.1.2.3
         action: deny
   EOF
   ```

   The following table shows how each example IP is evaluated by using longest-prefix matching. 

   | Client IP | Matching rule | Prefix length | Outcome |
   |---|---|---|---|
   | `10.1.2.3` | `block-rogue-host` | `/32` (most specific) | Denied |
   | `10.1.2.4` | `allow-trusted-subnet` | `/16` | Allowed |
   | `10.2.0.1` | `block-internal-range` | `/8` | Denied |
   | `8.8.8.8` | None | — | Allowed by `defaultAction` |

2. Send a request to the httpbin app. Verify that your request succeeds with a 200 response, because the request comes from a public IP address that falls through to `defaultAction: allow`.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 200 OK
   ...
   ```

3. Log into the httpbin pod to run a curl request from within the cluster. By default, Kubernetes assigns pod IP addresses from the `10.0.0.0/8` range. Because this range matches the `block-internal-range` deny rule, you get back a 403 HTTP response.

   ```sh
   kubectl exec -n httpbin deploy/httpbin -c curl -- curl -vi \
     http://http.{{< reuse "docs/snippets/namespace.md" >}}.svc.cluster.local:8080/status/200 \
     -H "host: www.example.com" | head -1
   ```

   Example output:
   ```console
   HTTP/1.1 403 Forbidden
   ```

### Custom deny response and headers

Return a non-default HTTP status code and include extra headers in the denial responses.

1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to deny all traffic by default with a custom HTTP 451 status code and a `X-Blocked-Reason` response header.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: acl-allowlist
     namespace: httpbin
   spec:
     targetRefs:
     - group: gateway.networking.k8s.io
       kind: HTTPRoute
       name: httpbin
     acl:
       defaultAction: deny
       denyResponse:
         statusCode: 451
         headers:
         - name: X-Blocked-Reason
           value: geo-policy
       rules:
       - cidrs:
         - 203.0.113.0/24
         action: allow
   EOF
   ```

   | Field | Description |
   |---|---|
   | `denyResponse.statusCode` | HTTP status code to return on denial. Defaults to `403`. |
   | `denyResponse.headers` | Add extra headers to every denial response. |

2. Send a request to the httpbin app. Verify that your request is denied with a 451 response and the `x-blocked-reason: geo-policy` header.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: www.example.com"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 451 Unavailable For Legal Reasons
   x-blocked-reason: geo-policy
   ...
   ```

## Monitor ACL denials

The ACL filter increments the gateway proxy's `dev.kgateway.http.acl.blocked` metric on every denied request. You can monitor this metric to observe the number of denied requests in your environment. 

1. Port-forward the gateway proxy to access the Envoy admin endpoint.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000:19000
   ```

2. Get the `dev.kgateway.http.acl.blocked` metric and verify that the number equals the number of requests that were denied by your ACL policy. 
   ```sh
   curl -s localhost:19000/stats | grep "dev.kgateway.http.acl"
   ```

   Example output:
   ```console
   dev.kgateway.http.acl.blocked: 3
   ```


## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} acl-allowlist -n httpbin
```
