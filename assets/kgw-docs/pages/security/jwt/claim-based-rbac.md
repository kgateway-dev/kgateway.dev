Use an `rbac` policy with [Common Expression Language (CEL)](https://github.com/cel-expr/cel-spec) expressions to allow or deny requests based on the claims in a verified JWT. The JWT filter writes the verified token payload to Envoy dynamic metadata, and your CEL expressions read the claims from that metadata. Because the rules depend on a verified token, configure `rbac` together with `jwtAuth` in the same {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

4. Complete the [Basic JWT policy](../basic/) guide to set up JWT auth with an inline JWKS key. Save the sample JWT token in an environment variable.
   ```sh
   export TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbG8tcHVibGljLWtleS0wMDEifQ.eyJpc3MiOiJzb2xvLmlvIiwib3JnIjoic29sby5pbyIsInN1YiI6ImFsaWNlIiwidGVhbSI6ImRldiIsImV4cCI6MjA3NDI3NDg4NCwibGxtcyI6eyJvcGVuYWkiOlsiZ3B0LTMuNS10dXJibyJdfX0.il5Rjsad65jpQR_pyRzBdEKFSj-ERmBf4K2VksvGvswWVv4n79lYERslr4KCECuiz9y_T-xUiQ9IkhW3YHzl5zo1kajhhIg7Nhnl1AvAqODbnF6wYpLRk0Npna_2T6lK3Yj54qQGi6vXG3IMRpo1_o2DrbdlKx2k_WFegCoQyyYazb4z3ZXfWvTiWqQDJA5wWcM3-jKzAWfNM8zgZWa-1BeAHDvpLcfWtuXEGSjkdCW0FQJOTjgIEqACnnXb2Jio0tWgelh9hDPILI-tvanj3iKCjpf3uF6g8QWSBNoVFfu7F1jJgj5Aj1sX8AV-CQVu2aQx3EHRZ1mL_3w3qSRWPw
   ```

## Allow access based on a claim {#allow}

1. Create a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} that enforces JWT authentication and allows only requests with a valid JWT that contains the `team=dev` claim. If the JWT does not include this claim, the request is denied.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
   metadata:
     name: jwt-policy
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
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

2. Send a request with the sample token from the previous guide. Because the JWT has a `team` claim that equals `dev`, the request matches the policy and is allowed with a 200 HTTP response. A request with a token where the `team` claim does not equal `dev`, or that has no `team` claim, is denied with a 403 HTTP response.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $TOKEN"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik localhost:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $TOKEN"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Verify that you get a `200 OK` response.

3. Save a token that does not have the `team=dev` claim, then repeat the request. This example uses a token for a user named Bob, who has the `team=ops` claim. The token is signed by the same private key so that the JWT passes verification with the inline JWKS that you defined in your policy. Verify that the request is denied with a 403 HTTP response. 

   ```sh
   export BOB_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbG8tcHVibGljLWtleS0wMDEifQ.eyJpc3MiOiJzb2xvLmlvIiwib3JnIjoic29sby5pbyIsInN1YiI6ImJvYiIsInRlYW0iOiJvcHMiLCJleHAiOjIwNzQyNzQ5NTQsImxsbXMiOnsibWlzdHJhbGFpIjpbIm1pc3RyYWwtbGFyZ2UtbGF0ZXN0Il19fQ.GF_uyLpZSTT1DIvJeO_eish1WDjMaS4BQSifGQhqPRLjzu3nXtPkaBRjceAmJi9gKZYAzkT25MIrT42ZIe3bHilrd1yqittTPWrrM4sWDDeldnGsfU07DWJHyboNapYR-KZGImSmOYshJlzm1tT_Bjt3-RK3OBzYi90_wl0dyAl9D7wwDCzOD4MRGFpoMrws_OgVrcZQKcadvIsH8figPwN4mK1U_1mxuL08RWTu92xBcezEO4CdBaFTUbkYN66Y2vKSTyPCxg3fLtg1mvlzU1-Wgm2xZIiPiarQHt6Uq7v9ftgzwdUBQM1AYLvUVhCN6XkkR9OU3p0OXiqEDjAxcg
   ```

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $BOB_TOKEN"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik localhost:8080/headers \
     -H "host: www.example.com:8080" \
     --header "Authorization: Bearer $BOB_TOKEN"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Verify that the request is denied with a `403 Forbidden` response.

   ```
   HTTP/1.1 403 Forbidden
   RBAC: access denied
   ```

## Other configurations {#other}

The following examples show other ways to write the `rbac` policy. Each one replaces the `rbac` block in the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} from the previous section.

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

List multiple expressions to match on more than one condition. The policy matches when **any** expression evaluates to `true` (OR logic). The following policy allows requests if the JWT has a `team=dev` or `sub=alice` claim.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['team'] == 'dev'"
      - "metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['sub'] == 'alice'"
```
For nested claims extraction, see the [JWT claim extraction guide](../jwt-claim-extraction/#nested-claims).

### Match an OAuth scope {#scope}

You can authorize requests based on an OAuth scope, such as one that is issued by an identity provider. Unlike the single-value claims in the previous examples, the scope is conventionally a single string of space-delimited scopes, such as `read write admin`. To match one scope without accidentally matching a longer scope that contains it (for example, matching `admin` but not `superadmin`), split the string on spaces and test for membership in the resulting list. The following policy allows requests with a JWT where the `scope` includes `admin`.

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
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
