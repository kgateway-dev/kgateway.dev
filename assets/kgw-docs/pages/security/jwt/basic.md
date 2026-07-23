Use JWT authentication to verify that incoming requests carry a token issued by a trusted provider before allowing them to reach your upstream services. This configuration lets you protect your APIs from unauthenticated access without adding authentication logic to each service. Enforce JWT authentication by creating a GatewayExtension with a JWT provider and referencing it from a {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "kgw-docs/snippets/prereq.md" >}}

## Set up JWT authentication

1. Create a GatewayExtension resource with a `jwt` configuration. The GatewayExtension holds one or more JWT provider definitions, including the issuer and JWKS source that you want to use to validate incoming tokens. By keeping the provider configuration in a separate resource, the same GatewayExtension can be referenced from more than one {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: selfminted
           issuer: kgateway.dev
           jwks:
             local:
               inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `spec.jwt.providers` | A list of JWT providers. If multiple providers are listed, a token that validates against any one of them is accepted (OR logic). |
   | `name` | An arbitrary name for this provider entry. |
   | `issuer` | The expected value of the `iss` claim. Tokens with a different issuer are rejected. If omitted, the `iss` field is not checked. |
   | `jwks.local.inline` | An inline JSON Web Key Set (JWKS) used to verify token signatures. To fetch the keys from a remote JWKS server instead, see [Remote JWKS](#remote-jwks). |

2. Create the {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resource that points to the GatewayExtension that you created in the previous step. The following policy applies JWT authentication to all routes on the Gateway. Create the policy in the same namespace as the targeted resource.

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
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `targetRefs` | The resource to enforce the policy on. When targeting a Gateway, the policy must be in the same namespace as the Gateway. To restrict JWT enforcement to a single route instead, change the `kind` field to HTTPRoute and provide the name of the HTTPRoute resource that defines the routes you want to protect. Make sure to create the policy in the same namespace as the HTTPRoute that you target. |
   | `jwtAuth.extensionRef` | The name of the GatewayExtension resource that holds the JWT provider configuration. The extension must be in the same namespace as the policy. |

3. Send a request without a JWT and verify that you get a `401 Unauthorized` response.

   {{< tabs >}}
   {{% tab name="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab name="Port-forward for local testing" %}}
   ```sh
   curl -vik localhost:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{< /tabs >}}

   Example output:

   ```
   < HTTP/1.1 401 Unauthorized
   Jwt is missing
   ```

   > [!WARNING]
   > **Got a `200 OK` instead?** The controller silently ignores {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} resources that target a resource in a different namespace. Verify that both resources were created in the correct namespace and that the controller accepted them.
   >
   > ```sh
   > kubectl get {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
   > kubectl get gatewayextension selfminted-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
   > ```
   >
   > Both resources must show an `Accepted` condition. If either has no status at all, the resource could be in the wrong namespace.

4. Save a sample JWT token and send it in the `Authorization` header. The token is signed by the same issuer and key that you configured in the GatewayExtension resource and can be successfully validated by the gateway proxy.

   <!-- Example token generated from https://jwt.io using RS256 with the following payload:
   {
     "iss": "kgateway.dev",
     "org": "kgateway.dev",
     "sub": "alice",
     "team": "dev",
     "exp": 2074274884,
     "llms": {
       "openai": [
         "gpt-3.5-turbo"
       ]
     }
   }
   To generate: Select RS256, use the header {"alg":"RS256","typ":"JWT","kid":"kgateway-public-key-001"}, paste the private key from private-key.pem, and encode.
   -->

   ```sh
   export TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtnYXRld2F5LXB1YmxpYy1rZXktMDAxIn0.eyJpc3MiOiJrZ2F0ZXdheS5kZXYiLCJvcmciOiJrZ2F0ZXdheS5kZXYiLCJzdWIiOiJhbGljZSIsInRlYW0iOiJkZXYiLCJleHAiOjIwNzQyNzQ4ODQsImxsbXMiOnsib3BlbmFpIjpbImdwdC0zLjUtdHVyYm8iXX19.YCxMm0TmecXsbcbNp6_GXlq5hCFGMD7KhLdOrp3EqzOKl_NX5vm6sNCMNSq5LjbCSKGThn66fnI4P6rlXke7w5kj8khIXQwDn7R0Dy5QOpLAFyE7pk8QGAjkgEGu37bxht5VjbsORdmrfxep1MTy3UEqef60Zwxwt3UtG5KmnsyyedmsCeodPNiNfuhA43r4KahpYg9cIMAnU_Wg-52ztwtqbrVRGxmoj6Efply4FE0xSKhKJZhulViriXR5K2y4zSdxenKvprO46u2ZSka7nq9ehpw_Oqhcwezw7So3lV_xpohiFz_-PGX97TXR1zi0ATjjp7VFxhkbggk8nEEFkQ
   ```

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

## Forward JWT claims as request headers {#claims-to-headers}

You can extract claims from the verified JWT and forward them as headers to the upstream service by using the `claimsToHeaders` field in the GatewayExtension resource.

1. Update the GatewayExtension resource to define the claims that you want to add as headers to the request before it is forwarded upstream. The following example extracts the `team` and `org` claims from the verified JWT and forwards them to the upstream service as the `x-team` and `x-org` headers.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: selfminted
           issuer: kgateway.dev
           claimsToHeaders:
             - name: team
               header: x-team
             - name: org
               header: x-org
           jwks:
             local:
               inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `claimsToHeaders` | A list of JWT claims to extract and forward as request headers to the upstream service. |
   | `name` | The name of the JWT claim to extract, for example `team`. |
   | `header` | The HTTP header name to set with the extracted claim value, for example `x-team`. |

2. Send the request again with the JWT. Verify that the response includes the `X-Team` and `X-Org` headers, which the gateway extracted from the token's `team` and `org` claims and forwarded to the upstream service.

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

   Example output:

   ```json
   {
     "headers": {
       ...
       "X-Org": [
         "kgateway.dev"
       ],
       "X-Team": [
         "dev"
       ]
     }
   }
   ```

## Other configurations {#other-configurations}

Review other common JWT configuration examples.

### Remote JWKS {#remote-jwks}

Instead of embedding the JWKS keys inline, you can point the provider at a remote JWKS server, such as the JWKS endpoint of an external identity provider. The gateway fetches the keys from the server and caches them, which means you do not have to update the GatewayExtension when the provider rotates its keys.

The following example uses Keycloak as the identity provider.

1. Set the following environment variables to match your Keycloak installation.

   ```sh
   export HOST_KEYCLOAK=<keycloak-host>    # hostname of your Keycloak server, for example keycloak.example.com
   export PORT_KEYCLOAK=443               # port that Keycloak listens on
   export KEYCLOAK_URL=https://$HOST_KEYCLOAK
   ```

2. Create a Backend resource that points to the Keycloak host.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: keycloak
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     type: Static
     static:
       hosts:
         - host: $HOST_KEYCLOAK
           port: $PORT_KEYCLOAK
   EOF
   ```

3. Update the GatewayExtension to use the Keycloak JWKS endpoint. Set the `issuer` to the Keycloak realm URL and the `url` to the realm's JWKS endpoint. The `backendRef` points to the Backend that you created in the previous step. The kgateway proxy uses this Backend to fetch the JWKS keys from Keycloak. 

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: keycloak
           issuer: $KEYCLOAK_URL/realms/master
           jwks:
             remote:
               url: $KEYCLOAK_URL/realms/master/protocol/openid-connect/certs
               backendRef:
                 name: keycloak
                 kind: Backend
                 group: gateway.kgateway.dev
               cacheDuration: 10m
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `jwks.remote.url` | The full URL of the JWKS endpoint, including protocol, host, and path. |
   | `jwks.remote.backendRef` | A reference to the Backend that fronts the JWKS server. The kgateway proxy uses this Backend to fetch the JWKS keys from Keycloak. Set `kind` to `Backend` and `group` to `gateway.kgateway.dev`. |
   | `jwks.remote.cacheDuration` | How long the gateway caches the fetched keys before it refreshes them. If omitted, the keys are cached for 5 minutes. |

   {{< version exclude-if="2.1.x" >}}For more information, see the [API docs]({{< link-hextra path="/reference/api/#remotejwks" >}}).{{< /version >}}

{{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}

#### Async JWKS fetch {#async-fetch}

By default, the gateway fetches the JWKS synchronously during request handling. If the JWKS server is slow or temporarily unavailable, JWT validation can fail. You can configure the gateway proxy to fetch and cache the JWKS asynchronously in the background instead by using the `asyncFetch` field.

```yaml
jwks:
  remote:
    url: $KEYCLOAK_URL/realms/master/protocol/openid-connect/certs
    backendRef:
      name: keycloak
      kind: Backend
      group: gateway.kgateway.dev
    asyncFetch:
      fastListener: true
      failedRefetchDuration: 10s
```

| Field | Description |
| ----- | ----- |
| `asyncFetch.fastListener` | If `true`, the listener starts serving traffic immediately without waiting for the first JWKS fetch to complete. If `false` or unset, the listener waits for the initial fetch before accepting requests, so tokens are never validated against an empty key set. |
| `asyncFetch.failedRefetchDuration` | How long to wait before retrying after a failed JWKS fetch. Accepts Go duration strings such as `500ms` or `10s`. If unset, Envoy defaults to `1s`. |


#### JWKS retry policy {#jwks-retry-policy}

You can configure exponential backoff retries when the JWKS server is unavailable by using the `retryPolicy` field.

```yaml
jwks:
  remote:
    url: $KEYCLOAK_URL/realms/master/protocol/openid-connect/certs
    backendRef:
      name: keycloak
      kind: Backend
      group: gateway.kgateway.dev
    retryPolicy:
      numRetries: 3
      backOff:
        baseInterval: 1s
        maxInterval: 30s
```

| Field | Description |
| ----- | ----- |
| `retryPolicy.numRetries` | Number of retry attempts when the JWKS fetch fails. Must be at least `1`. Defaults to `1` if unset. |
| `retryPolicy.backOff.baseInterval` | The initial backoff interval. Required. Accepts Go duration strings, such as `500ms` or `1s`. |
| `retryPolicy.backOff.maxInterval` | The maximum backoff interval. Optional. Must be greater than or equal to `baseInterval`. If unset, Envoy defaults to 10 times the `baseInterval`. |

{{< /version >}}


### JWT validation modes {#jwt-validation}

The `validationMode` field in `spec.jwt` controls whether requests without a JWT are allowed. To change the mode, reapply the GatewayExtension that you created earlier with the updated `validationMode` value.

**Strict** (default): Requests without a valid JWT are rejected with a `401 Unauthorized` response.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    validationMode: Strict
    providers:
      - name: selfminted
        issuer: kgateway.dev
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
EOF
```
Send a request without a token to verify the behavior:

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{< /tabs >}}

Example output:

```text
< HTTP/1.1 401 Unauthorized
Jwt is missing
```

**AllowMissing**: Requests without a token are allowed through. Requests that present an invalid token are still rejected. When you use `AllowMissing`, pair it with an RBAC policy to enforce authorization, because unauthenticated requests are allowed through. For an example, see [Restrict access based on claims](../claim-based-rbac/).

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    validationMode: AllowMissing
    providers:
      - name: selfminted
        issuer: kgateway.dev
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
EOF
```
Send a request without a token to verify the behavior:

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```sh
curl -vik localhost:8080/headers -H "host: www.example.com:8080"
```
{{% /tab %}}
{{< /tabs >}}

Example output:

```
< HTTP/1.1 200 OK
```

### Configure audiences {#audiences}

Restrict access to tokens that include a specific audience claim. An incoming token must include an `aud` claim that matches at least one of the listed values. The following example restricts access to tokens that include a `my-api` audience.

{{< callout type="warning" >}}
The sample token in this guide has no `aud` claim, so using this configuration requires a different token that carries a matching `aud` claim.
{{< /callout >}}

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        audiences:
          - my-api
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
EOF
```
Send a request with the sample token to verify audience enforcement:

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

Example output:

```
< HTTP/1.1 401 Unauthorized
Jwt validation failed: audience mismatch
```

### Customize token source {#token-source}

By default, the gateway reads the JWT from the `Authorization` header as a bearer token. Use `tokenSource` to read the token from a different header or from a URL query parameter. The following example reads the token from a custom `x-jwt` header with a `Bearer ` prefix.

{{< callout type="warning" >}}
Changing the `tokenSource` affects how clients must send requests. If you apply this example, send the token in the `x-jwt` header instead of the `Authorization` header.
{{< /callout >}}

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        tokenSource:
          header:
            header: x-jwt
            prefix: "Bearer "
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
EOF
```
Send a request with the token in the `x-jwt` header:

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}
```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers \
  -H "host: www.example.com:8080" \
  -H "x-jwt: Bearer $TOKEN"
```
{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}
```sh
curl -vik localhost:8080/headers \
  -H "host: www.example.com:8080" \
  -H "x-jwt: Bearer $TOKEN"
```
{{% /tab %}}
{{< /tabs >}}

Example output:

```
< HTTP/1.1 200 OK
```

### Forward tokens upstream {#forward-token}

By default, the gateway strips the JWT from the request before forwarding it to the upstream service. Set `forwardToken: true` to keep the token so the upstream service can read it.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        forwardToken: true
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"kgateway-public-key-001","use":"sig","alg":"RS256","n":"tNxnW0ZghyIUdfRc97EuZ6Hii0z4AucJrbOCT8MxKznlnV9Z-OrOYMf_hyjiD2Q_qyGrv-sRhinKOjokr-cbLKhHlAlEkEW1ah4wQ-zzO3DT0SdAKX_7RkMkl5Sba443vfDlDmuVSBeyHQr6cKZZGBIe8TlzcKR0xYlop13p1DYAHsIiX8A_q2CmsRlnV4CbneNMGZOmHuBiFG3DJ2lc1ZgvKc8SN1gt3oEujRqxy4yPLHVJ3wQ58ezYtgV2gzbyllzJdi1DSoPtnCFFGvfDqmAcDdmfVtHUHqagCF0ivEQsrxt7PYKqxuCbkaSY1_ef7ub01_5KF1GhlA9y5XSqJQ","e":"AQAB"}]}'
EOF
```
Send a request with the token to verify it is forwarded to the upstream:

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

Example output:

```json
{
  "headers": {
    ...
    "Authorization": [
      "Bearer eyJhbGciOiJSUzI1NiIs..."
    ]
  }
}
```

For claim-based access control with a CEL `rbac` policy, see [Restrict access with claim-based rules](../claim-based-rbac/).

### Disable JWT filter {#disable-jwt}

The `disable` field lets you turn off JWT authentication at a higher policy level. This is useful when you want to override a JWT policy applied at the Gateway level for a specific HTTPRoute.

**1. Send a request without a JWT to verify it's blocked:**

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{< /tabs >}}

Expected output:

```text
< HTTP/1.1 401 Unauthorized
Jwt is missing
```

**2. Disable JWT with the TrafficPolicy:**

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "kgw-docs/snippets/trafficpolicy-apiversion.md" >}}
kind: {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}}
metadata:
  name: jwt-disable
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  targetRefs:
    - group: gateway.networking.k8s.io
      kind: HTTPRoute
      name: httpbin
  jwtAuth:
    disable: {}
EOF
```

In this example, any JWT policy applied at the Gateway level is disabled for the httpbin HTTPRoute. Requests to this route can be made without a JWT.

**3. Repeat the request, now verifying it succeeds because JWT authentication is disabled:**

{{< tabs >}}
{{% tab name="Cloud Provider LoadBalancer" %}}

```sh
curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{% tab name="Port-forward for local testing" %}}

```sh
curl -vik localhost:8080/headers -H "host: www.example.com:8080"
```

{{% /tab %}}
{{< /tabs >}}

Expected output:

```text
< HTTP/1.1 200 OK
```

{{< version exclude-if="2.1.x,2.2.x,2.3.x" >}}

### asyncFetch {#asyncFetch}

When using a remote JWKS, you can configure `asyncFetch` to control how the gateway fetches and caches the JWKS. This is useful for improving performance and controlling startup behavior.

For detailed field descriptions, see the [API docs]({{< link-hextra path="/reference/api/#jwksasyncfetch" >}}).

{{< callout type="info" >}}
**Note:** `failedRefetchDuration` controls how long to wait before retrying a failed fetch, while `retryPolicy` controls how many times to retry and the backoff intervals. Use `failedRefetchDuration` for quick retries after transient failures, and `retryPolicy` for more robust retry handling with exponential backoff.
{{< /callout >}}

**Example:**

The following example allows the listener to start even if the JWKS endpoint is temporarily unavailable (`fastListener: true`). If the fetch fails, it retries after 5 seconds (`failedRefetchDuration: 5s`).

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        jwks:
          remote:
            url: https://auth.example.com/.well-known/jwks.json
            asyncFetch:
              fastListener: true   # Don't block startup on JWKS fetch
              failedRefetchDuration: 5s  # Retry after 5 seconds on failure
EOF
```
### retryPolicy {#retry-policy}

Configure how the gateway retries JWKS fetch when the remote server is unavailable. This ensures that temporary network issues do not cause authentication failures.

For detailed field descriptions, see the [API docs]({{< link-hextra path="/reference/api/#jwksretrypolicy" >}}).

**Example:**

The following example retries JWKS fetches up to three times (`numRetries: 3`) with exponential backoff starting at 2 seconds (`baseInterval: 2s`) and capping at 30 seconds (`maxInterval: 30s`). This is useful for handling transient network issues with an external JWKS endpoint.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "kgw-docs/snippets/namespace.md" >}}
spec:
  jwt:
    providers:
      - name: selfminted
        issuer: kgateway.dev
        jwks:
          remote:
            url: https://auth.example.com/.well-known/jwks.json
            retryPolicy:
              numRetries: 3  # Retry up to 3 times on failure
              backOff:
                baseInterval: 2s  # Start with 2-second delay
                maxInterval: 30s  # Cap at 30 seconds to avoid long waits
EOF
```

### When to use advanced settings {#recommendations}

In most cases, you do not need to configure `retryPolicy` or `asyncFetch`. The defaults are intended to work for typical JWKS endpoints.

Use the following guidelines to choose appropriate values:

| Scenario | Recommended Configuration |
| -------- | ------------------------- |
| **JWKS endpoint is external or occasionally slow** | Increase `numRetries` (e.g., 3-5) and use a larger `backOff.maxInterval` (e.g., 30s-60s) to handle intermittent failures |
| **Gateway startup should not be blocked by JWKS fetch failures** | Set `asyncFetch.fastListener: true` to allow traffic to flow while the JWKS fetch happens in the background |
| **Authentication must fail closed until JWKS is available** | Keep `fastListener: false` (default) to block traffic until the JWKS is successfully fetched |
| **Seeing frequent network failures** | Increase retries, but keep the max backoff bounded so failures surface quickly. Avoid setting very high retry counts or very long backoff intervals because that can make real JWKS endpoint outages harder to detect |

{{< callout type="warning" >}}
**Important:** Setting `fastListener: true` means that requests may be rejected if the JWKS fetch fails before it completes, because the gateway cannot validate tokens without the JWKS. Consider your application's availability requirements when choosing this setting.
{{< /callout >}}

{{< /version >}}

## Cleanup {#cleanup}

```sh
kubectl delete {{< reuse "kgw-docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```

If you completed the [Remote JWKS](#remote-jwks) section, also delete the Backend that you created for the Keycloak server.

```sh
kubectl delete backend keycloak -n {{< reuse "kgw-docs/snippets/namespace.md" >}}
```
