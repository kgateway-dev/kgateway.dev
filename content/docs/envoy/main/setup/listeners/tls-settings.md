---
title: Additional TLS settings
description: Tune TLS settings such as minimum version and cipher suites on a listener.
weight: 20
---

Annotate your Gateway listener to enable additional TLS settings, such as the minimum and maximum TLS version, cipher suites, signature algorithms, or allowed certificate hashes. 

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
  - name: https-tls-settings
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
        kgateway.dev/signature-algorithms: "ecdsa_secp256r1_sha256,rsa_pss_rsae_sha256"
```


The following settings are supported: 

| Setting | Description | 
| -- | -- | 
| `kgateway.dev/alpn-protocols` | A comma-delimited list of the application protocol that the Gateway can use during a TLS handshake. In this example, HTTP/2 is used.|
| `kgateway.dev/cipher-suites` | A comma-delimited list of the cipher suites that the Gateway can use during a TLS handshake. The example allows one TLS 1.2 cipher suite. TLS 1.3 cipher suites are not configurable through this setting.| 
| `kgateway.dev/ecdh-curves` | A comma-delimited list of key exchange protocols. If unset, the Envoy default of `X25519` and `P-256` are used. When adding a new protocol to this list, ensure it is backwards compatible in the case that the client does not specifically support the new protocol. The example sets the classic `X25519` and `P-256` protocols. To add the Post-Quantum safe key exchange protocol `X25519MLKEM768`, put it first in the list, such as `X25519MLKEM768,X25519,P-256`, so that clients that do not support it fall back to the classic protocols. To allow only the Post-Quantum safe protocol, specify `X25519MLKEM768` only. |
| `kgateway.dev/min-tls-version` | Enforce a minimum TLS version for the listener to use. In this example, TLS version 1.2 is used. |
| `kgateway.dev/max-tls-version` | Enforce a maximum TLS version for the Gateway to use. In this example, TLS version 1.3 is used. |
| `kgateway.dev/signature-algorithms` | A comma-delimited list of TLS signature algorithms that the gateway advertises during the TLS handshake with downstream clients. Use this setting to restrict which signature algorithms are accepted, for example to enforce ECDSA-only or exclude legacy RSA schemes. If unset, Envoy's defaults apply. |
| `kgateway.dev/verify-certificate-hash` | A comma-delimited list of the certificate hash (fingerprint) that must be present in the peer certificate that is presented during the TLS handshake. Use this setting for [mTLS listeners]({{< link-hextra path="/setup/listeners/mtls/" >}}) only, because the listener needs a CA to validate client certificates. | 
| `kgateway.dev/verify-subject-alt-names` | A comma-delimited list of the Subject Alternative Names that must be present in the peer certificate that is presented during the TLS handshake. Use this setting for [mTLS listeners]({{< link-hextra path="/setup/listeners/mtls/" >}}) only, because the listener needs a CA to validate client certificates. |


