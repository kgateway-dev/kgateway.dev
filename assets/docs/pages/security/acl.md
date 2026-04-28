Use an IP-based access control list (ACL) to allow or deny HTTP requests based on the client's source IP address.

## About ACL

The HTTP ACL filter enforces IP-based allow/deny rules on every incoming HTTP request at Layer 7. The filter inspects the downstream client IP (`source.address`) and compares it against a configured rule set by using longest-prefix matching across separate IPv4 and IPv6 tries.

Key behaviors:

- **Allow**: The request proceeds down the filter chain.
- **Deny**: The filter returns an immediate response (default HTTP 403) and stops processing.
- **Fail-closed**: If the client IP cannot be determined, the request is denied.
- **Longest-prefix wins**: A more specific CIDR always wins over a less specific one, regardless of rule order. This lets you "punch holes" — for example, allow a specific subnet inside a broader denied range.
- **IPv4-mapped IPv6**: Addresses such as `::ffff:10.0.0.1` are unwrapped and evaluated against the IPv4 rules.
- **Bare IPs**: An IP without a prefix (`192.168.1.5`) is treated as `/32` (IPv4) or `/128` (IPv6).

On every denial, the filter emits Envoy dynamic metadata under namespace `dev.kgateway.http.acl`, key `blocked-by`, so access logs and other filters can correlate the block:

| Denial source | `blocked-by` value |
|---|---|
| Named rule matched | The rule's `name` |
| Unnamed rule matched | `"rule"` |
| Default action applied (no rule matched) | `"default"` |
| IP unparseable | `"unknown-ip"` |

Access log format string: `%DYNAMIC_METADATA(dev.kgateway.http.acl:blocked-by)%`

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Configure an ACL policy

Use a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource to define your ACL rules.

The following examples walk through common ACL configurations using the httpbin sample app.

### Default deny with an allowlist

Allow only a specific subnet and deny all other clients.

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that denies all traffic by default and allows only requests from the `10.0.0.0/8` subnet. The policy targets the `httpbin` HTTPRoute that you set up as part of the prerequisites.

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
   | `defaultAction` | Fallback action when no rule matches the client IP address. This example denies all traffic by default, unless it is explicitly allowed by one of the `rules`.  |
   | `rules[].cidrs` | Define the CIDR blocks, for which you want to define an action.  |
   | `rules[].action` | Define the action to take when the client IP address matches any CIDR block. This example allows requests from the specified CIDR range. |

2. Send a request to verify that traffic from outside the allowed subnet is denied with a 403 response.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vi http://$INGRESS_GW_ADDRESS:8080/status/200 -H "host: acl.example:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vi localhost:8080/status/200 -H "host: acl.example"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:
   ```console
   HTTP/1.1 403 Forbidden
   ...
   ```

### Default allow with a denylist

Block a set of CIDRs and allow everything else.

1. Update the {{< reuse "docs/snippets/trafficpolicy.md" >}} to allow all traffic by default and block RFC 1918 private ranges.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: acl-allowlist
     namespace: httpbin
   spec:
     acl:
       defaultAction: allow
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
   | `rules[].name` | Optional rule identifier. On denial this value appears as the `blocked-by` dynamic metadata and, if `denyResponse.blockedByHeaderName` is set, as the value of that response header. |
   | `rules[].cidrs` | Multiple CIDRs can share one rule entry when they have the same name and action. |

### Hole-punching with named rules

Use longest-prefix matching to allow a specific subnet within a broader denied range.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: acl-allowlist
  namespace: httpbin
spec:
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

With this configuration:
- `10.1.2.3` is denied (most specific prefix, `block-rogue-host`).
- `10.1.2.4` is allowed (matches `allow-trusted-subnet`).
- `10.2.0.1` is denied (matches `block-internal-range`).
- All other IPs are allowed by `defaultAction`.

### Custom deny response

Return a non-default HTTP status code and include extra headers in denial responses.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
metadata:
  name: acl-allowlist
  namespace: httpbin
spec:
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
| `denyResponse.statusCode` | HTTP status code returned on denial. Defaults to `403`. |
| `denyResponse.headers` | Extra headers added to every denial response. |
| `denyResponse.blockedByHeaderName` | When set, adds a response header whose value mirrors the `blocked-by` dynamic metadata (the matched rule name, `"rule"`, or `"default"`). |

## Monitor ACL blocks

The ACL filter increments the Envoy counter `dev.kgateway.http.acl.blocked` on every denied request.

1. Port-forward to the Envoy admin endpoint on the gateway proxy pod.
   ```sh
   kubectl port-forward deploy/http -n {{< reuse "docs/snippets/namespace.md" >}} 19000:19000 & sleep 1
   ```

2. Query the ACL counter.
   ```sh
   curl -s localhost:19000/stats | grep "dev.kgateway.http.acl"
   ```

   Example output:
   ```console
   dev.kgateway.http.acl.blocked: 3
   ```

3. Stop the port-forward.
   ```sh
   kill %1
   ```

## Cleanup

{{< reuse "docs/snippets/cleanup.md" >}}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} acl-allowlist -n httpbin
kubectl delete httproute httpbin-acl -n httpbin
```
