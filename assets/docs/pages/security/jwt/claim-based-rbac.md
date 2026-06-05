Use an `rbac` policy with [Common Expression Language (CEL)](https://github.com/google/cel-spec) expressions to allow or deny requests based on the claims in a verified JWT. The JWT filter writes the verified token payload to Envoy dynamic metadata, and your CEL expressions read the claims from that metadata. Because the rules depend on a verified token, configure `rbac` together with `jwtAuth` in the same {{< reuse "docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

4. Complete the [Basic JWT policy](../basic/) guide to set up JWT auth with an inline JWKS key. Save a sample JWT token in an environment variable so that you can use it in this guide. 
    ```sh
    export TOKEN=...
    ```

## Allow access based on a claim {#allow}

1. Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that enforces JWT authentication and allows only requests with a valid JWT that contains the `team=dev` claim is `dev`. If the JWT does not include this claim, the request is denied.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: jwt-policy
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     targetRefs:
       - group: gateway.networking.k8s.io
         kind: Gateway
         name: http
     jwtAuth:
       extensionRef:
         name: selfminted-jwt
     rbac:
       action: Allow
       policy:
         matchExpressions:
           - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['team'] == 'dev'"
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `rbac.action` | The action to take when a request matches the policy, either `Allow` or `Deny`. Defaults to `Allow`, which permits only matching requests and denies all others. |
   | `rbac.policy.matchExpressions` | A list of CEL expressions. The policy matches when any one of the expressions evaluates to `true`. Reference verified JWT claims through the `envoy.filters.http.jwt_authn` filter metadata, in the form `metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['<claim>']`. |

2. Send a request with the sample token from the previous guide. Because JWT has a `team` claim that equals `dev`, the request matches the policy and is allowed with a 200 HTTP response. A request with a token where the `team` claim does not equal `dev`, or that has no `team` claim, is denied with a 403 HTTP response.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $TOKEN"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
   ```sh
   curl -vik localhost:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $TOKEN"
   ```
   {{% /tab %}}
   {{< /tabs >}}

## Other configurations {#other}

The following examples show other ways to write the `rbac` policy. Each one replaces the `rbac` block in the {{< reuse "docs/snippets/trafficpolicy.md" >}} from the previous section.

### Deny access based on a claim {#deny}

Set `action` to `Deny` to deny requests that match the expressions and allow everything else. The following policy denies requests with a JWT where the `team` claim equals `ops`.

```yaml
rbac:
  action: Deny
  policy:
    matchExpressions:
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['team'] == 'ops'"
```

### Match more than one claim {#multiple}

List multiple expressions to match on more than one condition. The policy matches when **any** expression evaluates to `true` (OR logic). The following policy allows requests from either the `dev` team or the user `alice`.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['team'] == 'dev'"
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['sub'] == 'alice'"
```

To require multiple conditions in a single rule instead (AND logic), combine them in one expression with `&&`. The following policy allows a request only when it is from the `dev` team **and** the `solo.io` org.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['team'] == 'dev' && metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['org'] == 'solo.io'"
```

### Match an OAuth scope {#scope}

You can authorize requests based on an OAuth `scope` claim, such as one issued by an identity provider. Unlike the single-value claims in the previous examples, the `scope` claim is conventionally a single string of space-delimited scopes, such as `read write admin`. To match one scope without accidentally matching a longer scope that contains it (for example, matching `admin` but not `superadmin`), split the string on spaces and test for membership in the resulting list. The following policy allows requests whose `scope` claim includes `admin`.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "'admin' in metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['scope'].split(' ')"
```

{{< callout type="info" >}}
The sample token in the [Basic JWT policy](../basic/) guide does not include a `scope` claim, so this example does not match that token. To try it out, use a token that carries a space-delimited `scope` claim. If your identity provider issues `scope` as a list instead of a string, drop the `.split(' ')` and match the list directly: `"'admin' in metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['scope']"`.
{{< /callout >}}

## Cleanup {#cleanup}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "docs/snippets/namespace.md" >}}
```
