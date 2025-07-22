## Global flags

```yaml
--as string                      The username to impersonate for the operation. The userame can be a regular user or a service account in a namespace.
--as-group stringArray           The group to impersonate for the operation. This flag can be repeated to specify multiple groups.
--as-uid string                  The UID to impersonate for the operation.
--cache-dir string               The default cache directory. (default "/Users/[user]/.kube/cache")
--certificate-authority string   The path to a file that contains the certificate for the Certificate Authority. 
--client-certificate string      The path to a file that contains the client certificate file to use to authenticate with the Kubernetes API server. 
--client-key string              The path to a client key file to use for TLS connections to the Kubernetes API server. 
--cluster string                 The name of the cluster to use.
--context string                 The name of the kubeconfig context to use.
--disable-compression            If true, opt-out of response compression for all requests to the server.
--insecure-skip-tls-verify       If true, the server's certificate is not checked for validity.
--kubeconfig string              The path to the kubeconfig file to use for CLI requests.
-n, --namespace string           If present, the namespace scope for this CLI request.
--request-timeout string         The length of time to wait before a server request is considered failed. Non-zero values must contain a corresponding time unit, such as 1s, 2m, 3h, etc. If set to zero ("0"), no timeouts are applied to CLI requests. (default "0")
-s, --server string              The address and port of the Kubernetes API server.
--tls-server-name string         The server name to use for server certificate validation. If not provided, the hostname that is used to contact the Kubernetes API server is used.
--token string                   The bearer token for authentication to the API server.
--user string                    The name of the kubeconfig user to use.
-v, --v int                      The number for the log level verbosity. (defaults to 0)
```