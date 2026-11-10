Use an `rbac` policy with [Common Expression Language (CEL)](https://github.com/cel-expr/cel-spec) expressions to allow or deny requests based on the claims in a verified JWT. The JWT filter writes the verified token payload to Envoy dynamic metadata, and your CEL expressions read the claims from that metadata. Because the rules depend on a verified token, configure `rbac` together with `jwtAuth` in the same {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

4. Complete the [Set up JWT authentication](../basic/#set-up-jwt-authentication) steps in the Basic JWT policy guide to create the `selfminted-jwt` GatewayExtension. The `jwt-policy` {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} in this guide replaces the policy of the same name from that guide.
5. Save the sample JWT token from that guide in an environment variable. The token is for a user named Alice, who has the `team=dev` claim.
   ```sh
   export TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtnYXRld2F5LXB1YmxpYy1rZXktMDAxIn0.eyJpc3MiOiJrZ2F0ZXdheS5kZXYiLCJvcmciOiJrZ2F0ZXdheS5kZXYiLCJzdWIiOiJhbGljZSIsInRlYW0iOiJkZXYiLCJleHAiOjIwNzQyNzQ4ODQsImxsbXMiOnsib3BlbmFpIjpbImdwdC0zLjUtdHVyYm8iXX19.lTQr9PIyDeIQYn0c_qxaNb1sAJ3-rCMzZ0jR33v_P5ZWw9eiIHm9e_LDWaBZp2s6CCeqSubJvk7QT06SeKqiq84uQNUG6o5vKVolIfep6L7LCH9GFuTsJgTLxznJPc4oh5qIum0zBC2fy_IOOGeV_FzeFh1Jidi3onGS1fxV2EhY9btbM3br8oFwkhU4Gv1d-lUK1_j0cuP0Cuyx3EoaJkarmB_chJYqFe-EoUVbKXdsYdBLGCwK8u30FOBleRUWvuekQB7atlfYG0qptG0iOPVVv4tynL44cNQ_5GBt4QfIwBqAQyoJCcqbxNrZi_Ie6UP-IMWuejlXMDgTHJggqA
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

2. Send a request with Alice's token. Because the JWT has a `team` claim that equals `dev`, the request matches the policy and is allowed with a 200 HTTP response. A request with a token where the `team` claim does not equal `dev`, or that has no `team` claim, is denied with a 403 HTTP response.

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

3. Save a token that does not have the `team=dev` claim, then repeat the request. This example uses a token for a user named Bob, who has the `team=ops` claim. The token is signed by the same private key so that the JWT passes verification with the inline JWKS in the `selfminted-jwt` GatewayExtension. Verify that the request is denied with a 403 HTTP response. 

   ```sh
   export BOB_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtnYXRld2F5LXB1YmxpYy1rZXktMDAxIn0.eyJpc3MiOiJrZ2F0ZXdheS5kZXYiLCJvcmciOiJrZ2F0ZXdheS5kZXYiLCJzdWIiOiJib2IiLCJ0ZWFtIjoib3BzIiwiZXhwIjoyMDc0Mjc0OTU0LCJsbG1zIjp7Im1pc3RyYWxhaSI6WyJtaXN0cmFsLWxhcmdlLWxhdGVzdCJdfX0.pKtqiC1EZh1Rjz5B19DbtM_ixfeHc9UgyGeHa3sFxFZoqRne1p_sCNgnRK0GMFTv5-rVaneIfhgcCK2ytRPFMe-wQZ4eX_O_1Cm2Yz_9yKsJJ0VVgIcqGgWQvp0UQXsFBBONrsjIz2kEZBxR3t_phzXhbxe-5JeFKCRoC9zN6Bmyr_LzrJUNaqSIUsy3hmpsTE8zkI2besj88UtgHf1LZ9MAon76bJp45R34mf9ZZh58hFip5QyddYhKnOI3-OVSbwT3zRX39EDvxr8-jbNm5nZa2nquIWclpN497JtAfFHryONxtl3KO66YWGwkftxYUCe6q5oP26WeR9mtba_SnA
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

### Match an OAuth scope {#scope}

You can authorize requests based on an OAuth scope that your identity provider issues. The sample tokens in this guide do not have a `scope` claim, so to try these examples, use a token from your identity provider. Unlike the single-value claims in the previous examples, the scope is conventionally a single string of space-delimited scopes, such as `read write admin`. To match one scope, split the string on spaces and check whether the resulting list contains the scope. A match on `admin` then does not also match a longer scope that contains it, such as `superadmin`. The following policy allows requests with a JWT where the `scope` includes `admin`.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "'admin' in metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['scope'].split(' ')"
```

If your identity provider issues `scope` as a list instead of a space-delimited string, remove the `.split(' ')` and match the list directly.

```yaml
rbac:
  action: Allow
  policy:
    matchExpressions:
      - "'admin' in metadata.filter_metadata['envoy.filters.http.jwt_authn']['payload']['scope']"
```

## Cleanup {#cleanup}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
