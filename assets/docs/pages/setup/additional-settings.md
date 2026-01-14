Annotate your Gateway listener to enable additional TLS settings, such as the minimum and maximum TLS version, cipher suites, or allowed certificate hashes. 

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: example-gateway
  namespace: default
spec:
  gatewayClassName: kgateway
  listeners:
  - name: https
    protocol: HTTPS
    port: 443
    tls:
      mode: Terminate
      certificateRefs:
        - name: https
          kind: Secret
  - name: https-mtls-strict-validation
    protocol: HTTPS
    port: 8443
    tls:
      mode: Terminate
      certificateRefs:
        - name: https
          kind: Secret
      options:
        kgateway.dev/alpn-protocols: "h2"
        kgateway.dev/cipher-suites: "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
        kgateway.dev/ecdh-curves: "X25519,P-256"
        kgateway.dev/min-tls-version: "1.2"
        kgateway.dev/max-tls-version: "1.3"
        kgateway.dev/verify-subject-alt-names: "example.com"
        kgateway.dev/verify-certificate-hash: "46:DB:0D:C2:E1:4F:0A:05:8C:4F:05:8D:77:B1:8D:7C:1A:BE:18:4F:AF:81:BF:E2:B1:CD:03:43:7F:D8:65:4B"
  - name: https-insecure-fallback
    protocol: HTTPS
    port: 9443
    tls:
      mode: Terminate
      certificateRefs:
        - name: https
          kind: Secret
```


The following settings are supported: 

| Setting | Description | 
| -- | -- | 
| `kgateway.dev/alpn-protocols` | A comma-delimited list of the application protocol that the Gateway can use during a TLS handshake. In this example, HTTP/2 is used.|
| `kgateway.dev/cipher-suites` | A comma-delimited list of the cipher suites that the Gateway can use during a TLS handshake. The example shows the TLSv1_2 and TLSv1_3 cipher suites.| 
| `kgateway.dev/ecdh-curves` | A comma-delimited list of key exchange protocols. If unset, the Envoy default of `X25519` and `P-256` are used. When adding a new protocol to this list, it’s important to ensure it is backwards compatible in the case that the client does not specifically support the new protocol. This example adds the Post-Quantum safe key exchange protocol X25519MLKEM768, but fall backs to the classic X25519 or P-256 protocols if the client does not support it. If you want to allow only the Post-Quantum safe protocol, remove the safe protocols and specify X25519MLKEM768 only. |
| `kgateway.dev/min-tls-version` | Enforce a minimum TLS version for the listener to use. In this example, TLS version 1.2 is used. |
| `kgateway.dev/max-tls-version` | Enforce a maximum TLS version for the Gateway to use. In this example, TLS version 1.3 is used. |
| `kgateway.dev/verify-certificate-hash` | A comma-delimited list of the certificate hash (fingerprint) that must be present in the peer certificate that is presented during the TLS handshake. Use this setting for [mTLS listeners]({{< link-hextra path="/setup/listeners/mtls/" >}}) only.   | 
| `kgateway.dev/verify-subject-alt-names` | A comma-delimited list of the Subject Alternative Names that must be present in the peer certificate that is presented during the TLS handshake. Use this setting for [mTLS listeners]({{< link-hextra path="/setup/listeners/mtls/" >}}) only.  |


