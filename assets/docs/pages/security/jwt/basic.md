Use JWT authentication to verify that incoming requests carry a token issued by a trusted provider before allowing them to reach your upstream services. This configuration lets you protect your APIs from unauthenticated access without adding authentication logic to each service. Enforce JWT authentication by creating a `GatewayExtension` with a JWT provider and referencing it from a {{< reuse "docs/snippets/trafficpolicy.md" >}}.

## Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

## Step 1: Create a GatewayExtension for the JWT provider {#gateway-extension}

A `GatewayExtension` resource with a `jwt` configuration holds one or more JWT provider definitions, including the issuer and JWKS source that you want to use to validate incoming tokens. By keeping the provider configuration in a separate resource, the same `GatewayExtension` can be referenced from more than one {{< reuse "docs/snippets/trafficpolicy.md" >}}.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
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
| `jwks.local.inline` | An inline JSON Web Key Set (JWKS) used to verify token signatures. To use a remote JWKS server instead, replace `local` with `remote` and provide a `url` and `backendRef`. |

## Step 2: Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} that references the GatewayExtension {#traffic-policy}

Create a {{< reuse "docs/snippets/trafficpolicy.md" >}} with `jwtAuth.extensionRef` pointing to the `GatewayExtension`. This example applies JWT enforcement to all routes on the Gateway. Create the policy in the same namespace as the targeted resource.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: TrafficPolicy
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
| `targetRefs` | The resource to enforce the policy on. When targeting a `Gateway`, the policy must be in the same namespace as the Gateway. To restrict JWT enforcement to a single route instead, change `kind` to `HTTPRoute`, provide the route name, and create the policy in the same namespace as the HTTPRoute. |
| `jwtAuth.extensionRef` | The name of the `GatewayExtension` that holds the JWT provider configuration. The extension must be in the same namespace as the policy. |

## Step 3: Verify that requests without a JWT are denied {#verify-denied}

Send a request without a JWT. Verify that you get a `401 Unauthorized` response.

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
**Got a `200 OK` instead?** The controller silently ignores a `TrafficPolicy` that targets a resource in a different namespace. Verify that both resources were created in the correct namespace and that the controller accepted them.
```sh
kubectl get trafficpolicy jwt-policy -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
kubectl get gatewayextension selfminted-jwt -n {{< reuse "docs/snippets/namespace.md" >}} -o yaml | grep -A10 status
```
Both resources should show an `Accepted` condition. If either has no status at all, the resource is in the wrong namespace.
{{< /callout >}}

## Step 4: Send a request with a valid JWT {#verify-allowed}

Save a sample JWT token and send it in the `Authorization` header. The token is signed by the same issuer and key configured in the `GatewayExtension`, so the gateway allows the request through.

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

## (Optional) Forward JWT claims as request headers {#claims-to-headers}

You can extract claims from the verified JWT and forward them as headers to the upstream service. Update the `GatewayExtension` to add `claimsToHeaders`.

```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
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

Send the request again with the JWT. Verify that the response includes the `X-Team` and `X-Org` headers, which the gateway extracted from the token's `team` and `org` claims and forwarded to the upstream service.

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

## Cleanup {#cleanup}

```sh
kubectl delete trafficpolicy jwt-policy -n {{< reuse "docs/snippets/namespace.md" >}}
kubectl delete gatewayextension selfminted-jwt -n {{< reuse "docs/snippets/namespace.md" >}}
```
