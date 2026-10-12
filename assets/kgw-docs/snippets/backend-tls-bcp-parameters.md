```yaml
kubectl apply -f- <<EOF
apiVersion: gateway.kgateway.dev/v1alpha1
kind: BackendConfigPolicy
metadata:
  name: nginx-tls-policy
  namespace: kgateway-base
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: nginx
  tls:
    sni: "example.com"
    secretRef:
      name: ca
    parameters:
      ecdhCurves:
      - P-384
      - P-256
      cipherSuites:
      - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
      - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
      minVersion: "1.2"
      maxVersion: "1.3"
      signatureAlgorithms:
      - ecdsa_secp256r1_sha256
      - rsa_pss_rsae_sha256
    alpnProtocols:
    - http/1.1
    verifySubjectAltNames:
    - example.com
EOF
```

{{< reuse "kgw-docs/snippets/review-table.md" >}}

| Setting | Description |
|---------|-------------|
| `tls.parameters.ecdhCurves` | The key exchange curves for the upstream TLS handshake. If the backend uses a P-384 ECDSA certificate, include `P-384` in this list. |
| `tls.parameters.cipherSuites` | The cipher suites for the upstream TLS handshake. Cipher suites apply to TLS 1.2 and earlier. |
| `tls.parameters.minVersion` | The minimum TLS version for the upstream TLS handshake. |
| `tls.parameters.maxVersion` | The maximum TLS version for the upstream TLS handshake. |
| `tls.parameters.signatureAlgorithms` | The TLS signature algorithms that the gateway proxy advertises during the upstream TLS handshake. |
| `tls.alpnProtocols` | The Application-Layer Protocol Negotiation (ALPN) protocols that the gateway proxy offers to the backend. If you do not set this field, the proxy offers `h2` and `http/1.1`. |
| `tls.verifySubjectAltNames` | A list of Subject Alternative Names. The backend certificate must have one of these names. This setting requires a trusted CA certificate in `tls.secretRef`. |
