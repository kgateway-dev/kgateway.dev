Use JWT authentication to verify that incoming requests carry a token issued by a trusted provider before allowing them to reach your upstream services. This configuration lets you protect your APIs from unauthenticated access without adding authentication logic to each service. Enforce JWT authentication by creating a GatewayExtension with a JWT provider and referencing it from a {{< reuse "docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Set up JWT authentication

1. Create a GatewayExtension resource with a `jwt` configuration. The GatewayExtension holds one or more JWT provider definitions, including the issuer and JWKS source that you want to use to validate incoming tokens. By keeping the provider configuration in a separate resource, the same GatewayExtension can be referenced from more than one {{< reuse "docs/snippets/trafficpolicy.md" >}}.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: selfminted
           issuer: solo.io
           jwks:
             local:
               inline: '{"keys":[{"kty":"RSA","kid":"solo-public-key-001","use":"sig","alg":"RS256","n":"AOfIaJMUm7564sWWNHaXt_hS8H0O1Ew59-nRqruMQosfQqa7tWne5lL3m9sMAkfa3Twx0LMN_7QqRDoztvV3Wa_JwbMzb9afWE-IfKIuDqkvog6s-xGIFNhtDGBTuL8YAQYtwCF7l49SMv-GqyLe-nO9yJW-6wIGoOqImZrCxjxXFzF6mTMOBpIODFj0LUZ54QQuDcD1Nue2LMLsUvGa7V1ZHsYuGvUqzvXFBXMmMS2OzGir9ckpUhrUeHDCGFpEM4IQnu-9U8TbAJxKE5Zp8Nikefr2ISIG2Hk1K2rBAc_HwoPeWAcAWUAR5tWHAxx-UXClSZQ9TMFK850gQGenUp8","e":"AQAB"}]}'
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `spec.jwt.providers` | A list of JWT providers. If multiple providers are listed, a token that validates against any one of them is accepted (OR logic). |
   | `name` | An arbitrary name for this provider entry. |
   | `issuer` | The expected value of the `iss` claim. Tokens with a different issuer are rejected. If omitted, the `iss` field is not checked. |
   | `jwks.local.inline` | An inline JSON Web Key Set (JWKS) used to verify token signatures. To fetch the keys from a remote JWKS server instead, see [Use a remote JWKS as a source](#remote-jwks). |

2. Create the {{< reuse "docs/snippets/trafficpolicy.md" >}} resource that points to the GatewayExtension that you created in the previous step. The following policy applies JWT authentication to all routes on the Gateway. Create the policy in the same namespace as the targeted resource.

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
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `targetRefs` | The resource to enforce the policy on. When targeting a Gateway, the policy must be in the same namespace as the Gateway. To restrict JWT enforcement to a single route instead, change the `kind` field to HTTPRoute and provide the name of the HTTPRoute resource that defines the routes that you want to route to. Make sure to create the policy in the same namespace as the HTTPRoute that you target. |
   | `jwtAuth.extensionRef` | The name of the GatewayExtension resource that holds the JWT provider configuration. The extension must be in the same namespace as the policy. |

3. Send a request without a JWT and verify that you get a `401 Unauthorized` response.

   {{< tabs tabTotal="2" items="Cloud Provider LoadBalancer,Port-forward for local testing" >}}
   {{% tab tabName="Cloud Provider LoadBalancer" %}}
   ```sh
   curl -vik http://$INGRESS_GW_ADDRESS:8080/headers -H "host: www.example.com:8080"
   ```
   {{% /tab %}}
   {{% tab tabName="Port-forward for local testing" %}}
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

   {{< callout type="warning" >}}
   **Got a `200 OK` instead?** The controller silently ignores {{< reuse "docs/snippets/trafficpolicy.md" >}} resources that target a resource in a different namespace. Verify that both resources were created in the correct namespace and that the controller accepted them.
   ```sh
   kubectl get {{< reuse "docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
   kubectl get gatewayextension selfminted-jwt -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
   ```
   Both resources must show an `Accepted` condition. If either has no status at all, the resource could be in the wrong namespace.
   {{< /callout >}}

4. Save a sample JWT token and send it in the `Authorization` header. The token is signed by the same issuer and key that you configured in the GatewayExtension resource and can be successfully validated by the gateway proxy.

   <!-- Example token from: https://github.com/kgateway-dev/kgateway/pull/12811 -->

   ```sh
   export TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbG8tcHVibGljLWtleS0wMDEifQ.eyJpc3MiOiJzb2xvLmlvIiwib3JnIjoic29sby5pbyIsInN1YiI6ImFsaWNlIiwidGVhbSI6ImRldiIsImV4cCI6MjA3NDI3NDg4NCwibGxtcyI6eyJvcGVuYWkiOlsiZ3B0LTMuNS10dXJibyJdfX0.il5Rjsad65jpQR_pyRzBdEKFSj-ERmBf4K2VksvGvswWVv4n79lYERslr4KCECuiz9y_T-xUiQ9IkhW3YHzl5zo1kajhhIg7Nhnl1AvAqODbnF6wYpLRk0Npna_2T6lK3Yj54qQGi6vXG3IMRpo1_o2DrbdlKx2k_WFegCoQyyYazb4z3ZXfWvTiWqQDJA5wWcM3-jKzAWfNM8zgZWa-1BeAHDvpLcfWtuXEGSjkdCW0FQJOTjgIEqACnnXb2Jio0tWgelh9hDPILI-tvanj3iKCjpf3uF6g8QWSBNoVFfu7F1jJgj5Aj1sX8AV-CQVu2aQx3EHRZ1mL_3w3qSRWPw
   ```

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

   Verify that you get a `200 OK` response.

## Forward JWT claims as request headers {#claims-to-headers}

You can extract claims from the verified JWT and forward them as headers to the upstream service by using the `claimsToHeaders` field in the GatewayExtension resource.

1. Update the GatewayExtension resource to define the claims that you want to add as headers to the request before it is forwarded upstream. The following example extracts the `team` and `org` claims from the verified JWT and forwards them to the upstream service as the `x-team` and `x-org` headers.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: selfminted
           issuer: solo.io
           claimsToHeaders:
             - name: team
               header: x-team
             - name: org
               header: x-org
           jwks:
             local:
               inline: '{"keys":[{"kty":"RSA","kid":"solo-public-key-001","use":"sig","alg":"RS256","n":"AOfIaJMUm7564sWWNHaXt_hS8H0O1Ew59-nRqruMQosfQqa7tWne5lL3m9sMAkfa3Twx0LMN_7QqRDoztvV3Wa_JwbMzb9afWE-IfKIuDqkvog6s-xGIFNhtDGBTuL8YAQYtwCF7l49SMv-GqyLe-nO9yJW-6wIGoOqImZrCxjxXFzF6mTMOBpIODFj0LUZ54QQuDcD1Nue2LMLsUvGa7V1ZHsYuGvUqzvXFBXMmMS2OzGir9ckpUhrUeHDCGFpEM4IQnu-9U8TbAJxKE5Zp8Nikefr2ISIG2Hk1K2rBAc_HwoPeWAcAWUAR5tWHAxx-UXClSZQ9TMFK850gQGenUp8","e":"AQAB"}]}'
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `claimsToHeaders` | A list of JWT claims to extract and forward as request headers to the upstream service. |
   | `name` | The name of the JWT claim to extract, for example `team`. |
   | `header` | The HTTP header name to set with the extracted claim value, for example `x-team`. |

2. Send the request again with the JWT. Verify that the response includes the `X-Team` and `X-Org` headers, which the gateway extracted from the token's `team` and `org` claims and forwarded to the upstream service.

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

   Example output:

   ```json
   {
     "headers": {
       ...
       "X-Org": [
         "solo.io"
       ],
       "X-Team": [
         "dev"
       ]
     }
   }
   ```

## Optional: Use a remote JWKS as a source {#remote-jwks}

Instead of embedding the keys inline, you can point the provider at a remote JWKS server, such as the JWKS endpoint of an external identity provider. The gateway fetches the keys from the server and caches them, which means you do not have to update the GatewayExtension when the provider rotates its keys. To reach the server, the GatewayExtension references a Backend resource that fronts the JWKS host.

1. Create a Backend resource for the remote JWKS server. The following example uses a static Backend that points to an external host. Set the `host` and `port` to match the JWKS server that you want to use.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: gateway.kgateway.dev/v1alpha1
   kind: Backend
   metadata:
     name: jwks-server
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     type: Static
     static:
       hosts:
         - host: example.com
           port: 443
   EOF
   ```

2. Update the GatewayExtension to use a `remote` JWKS source instead of `local`. Replace the entire `jwks` block with the `remote` configuration. The `url` is the full JWKS endpoint, and `backendRef` points to the Backend that you created in the previous step.

   ```yaml
   kubectl apply -f- <<EOF
   apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
   kind: GatewayExtension
   metadata:
     name: selfminted-jwt
     namespace: {{< reuse "docs/snippets/namespace.md" >}}
   spec:
     jwt:
       providers:
         - name: remote-provider
           issuer: https://example.com
           jwks:
             remote:
               url: https://example.com/.well-known/jwks.json
               backendRef:
                 name: jwks-server
                 kind: Backend
                 group: gateway.kgateway.dev
               cacheDuration: 10m
   EOF
   ```

   | Field | Description |
   | ----- | ----- |
   | `jwks.remote.url` | The URL of the remote JWKS server. It must be a full FQDN with protocol, host, and path, for example `https://example.com/.well-known/jwks.json`. |
   | `jwks.remote.backendRef` | A reference to the Backend (or other backend resource) that fronts the JWKS server. When you reference a kgateway Backend, set `kind` to `Backend` and `group` to `gateway.kgateway.dev`. |
   | `jwks.remote.cacheDuration` | How long the gateway caches the fetched keys before it refreshes them. If omitted, the keys are cached for 5 minutes. |

   {{< callout type="warning" >}}
   This example uses a placeholder JWKS server (`example.com`), so it does not validate the sample token from the earlier steps. To try it out, replace the host, URL, and `issuer` with the values for a JWKS server that you control, and use a token that is signed by that provider.
   {{< /callout >}}

   For more information, see the [API docs]({{< link-hextra path="/reference/api/#remotejwks" >}}).

## Optional: Customize how tokens are validated {#customize}

The `jwt` configuration in the GatewayExtension supports several optional fields that change how tokens are located, validated, and forwarded. To use any of them, add the field to the GatewayExtension that you created earlier and reapply it. Add only the fields that you need, and keep the `jwks` and other settings that you already configured.

| Field | Location | Description |
| ----- | ----- | ----- |
| `validationMode` | `spec.jwt` | Controls whether a JWT is required. `Strict` (the default) rejects requests that do not include a valid JWT. `AllowMissing` lets requests without a token through, but still rejects requests that present an invalid token. When you use `AllowMissing`, pair it with an RBAC policy to enforce authorization, because unauthenticated requests are allowed through. |
| `audiences` | `spec.jwt.providers[]` | A list of accepted audiences. An incoming token must include an `aud` claim that matches one of these values. If omitted, the `aud` claim is not checked. |
| `tokenSource` | `spec.jwt.providers[]` | Where to find the JWT. By default, the token is read from the `Authorization` header as a bearer token. Set `header.header` to read it from a different header (and optional `header.prefix` to strip a prefix), or `queryParameter` to read it from a URL query parameter. Exactly one of `header` or `queryParameter` can be set. |
| `forwardToken` | `spec.jwt.providers[]` | Whether to forward the token to the upstream service. If `false` or unset, the gateway removes the token's header before it forwards the request. Set to `true` to keep the token so that the upstream service can use it. |

The following GatewayExtension is a replacement for the one that you created earlier. You can apply it as-is: the request-changing fields (`audiences` and `tokenSource`) are commented out, so the example keeps working with the sample token and requests from the previous steps. Uncomment the fields that you want to use.

```yaml
kubectl apply -f- <<EOF
apiVersion: {{< reuse "docs/snippets/trafficpolicy-apiversion.md" >}}
kind: GatewayExtension
metadata:
  name: selfminted-jwt
  namespace: {{< reuse "docs/snippets/namespace.md" >}}
spec:
  jwt:
    validationMode: Strict            # Strict (default) requires a valid JWT; AllowMissing also lets requests with no token through
    providers:
      - name: selfminted
        issuer: solo.io
        forwardToken: true            # keep the token so that the upstream service can use it
        # audiences:                  # require a matching aud claim (the sample token has no aud claim)
        #   - my-api
        # tokenSource:                # read the token from a custom location instead of the Authorization header
        #   header:
        #     header: x-jwt
        #     prefix: "Bearer "
        jwks:
          local:
            inline: '{"keys":[{"kty":"RSA","kid":"solo-public-key-001","use":"sig","alg":"RS256","n":"AOfIaJMUm7564sWWNHaXt_hS8H0O1Ew59-nRqruMQosfQqa7tWne5lL3m9sMAkfa3Twx0LMN_7QqRDoztvV3Wa_JwbMzb9afWE-IfKIuDqkvog6s-xGIFNhtDGBTuL8YAQYtwCF7l49SMv-GqyLe-nO9yJW-6wIGoOqImZrCxjxXFzF6mTMOBpIODFj0LUZ54QQuDcD1Nue2LMLsUvGa7V1ZHsYuGvUqzvXFBXMmMS2OzGir9ckpUhrUeHDCGFpEM4IQnu-9U8TbAJxKE5Zp8Nikefr2ISIG2Hk1K2rBAc_HwoPeWAcAWUAR5tWHAxx-UXClSZQ9TMFK850gQGenUp8","e":"AQAB"}]}'
EOF
```

{{< callout type="warning" >}}
The `audiences` and `tokenSource` fields change how clients must send requests, so they are commented out above. If you uncomment `tokenSource`, send the token in the matching header or query parameter instead of the `Authorization` header. If you uncomment `audiences`, requests must use a token that includes a matching `aud` claim; the sample token in this guide has no `aud` claim.
{{< /callout >}}

For claim-based access control with a CEL `rbac` policy, see [Restrict access with claim-based rules](../claim-based-rbac/).

## Cleanup {#cleanup}

```sh
kubectl delete {{< reuse "docs/snippets/trafficpolicy.md" >}} jwt-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "docs/snippets/namespace.md" >}}
```

If you completed the [Use a remote JWKS as a source](#remote-jwks) section, also delete the Backend that you created for the JWKS server.

```sh
kubectl delete backend jwks-server -n {{< reuse "docs/snippets/namespace.md" >}}
```
