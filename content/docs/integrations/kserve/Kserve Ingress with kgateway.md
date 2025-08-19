---
title: Kserve Ingress with kgateway
weight: 20
---

Use as the ingress gateway to manage traffic for your KServe machine learning inference services. This integration provides advanced routing, security, and observability capabilities for production ML workloads.

### About kgateway with KServe
kgateway provides a high-performance ingress solution for KServe that delivers comprehensive traffic management capabilities for machine learning workloads. As an ingress controller, it enables model-specific traffic routing through intelligent request distribution based on path patterns, headers, or model versions. The solution includes automatic TLS termination with certificate management for secure inference endpoints and configurable rate limiting to protect ML models from excessive traffic. For enterprise-grade security, kgateway supports advanced authentication methods including JWT validation, OAuth2 integration, and API key authentication, coupled with role-based authorization controls. Teams gain full observability through detailed request metrics, distributed tracing, and comprehensive access logging.

### Before you begin

{{< reuse "docs/snippets/prereq.md" >}}

### Additional requirements

1. Verify KServe installation:
   ```sh
   kubectl get pods -n kserve-system
   ```

2. Install cert-manager for TLS certificates:
   ```sh
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
   ```

### Step 1: Configure basic ingress

Create a VirtualService to route traffic to your KServe predictors:

```yaml
apiVersion: networking.kgateway.io/v1
kind: VirtualService
metadata:
  name: kserve-ingress
  namespace: kserve-system
spec:
  virtualHost:
    domains:
      - "inference.example.com"
    routes:
      - matchers:
          - prefix: "/v1/models/"
        routeAction:
          single:
            upstream:
              name: kserve-predictor-default
              namespace: kserve-system
```
Apply the configuration:
```sh
kubectl apply -f kserve-ingress.yaml
```

### Step 2: Set up model-specific routing

Create a RouteTable for advanced routing rules:

```yaml
apiVersion: networking.kgateway.io/v1
kind: RouteTable
metadata:
  name: model-routes
  namespace: kserve-system
spec:
  routes:
    - matchers:
        - exact: "/v1/models/iris-classifier/predict"
      routeAction:
        single:
          upstream:
            name: iris-classifier-predictor-default
            namespace: ml-models
      options:
        prefixRewrite: "/predict"
```
### Step 3: Configure security
### Enable TLS termination
```yaml
spec:
  virtualHost:
    options:
      tls:
        secretRef:
          name: kserve-tls-cert
          namespace: kserve-system
```
### Set up CORS policies
```yaml
options:
  cors:
    allowOrigins: ["*.example.com"]
    allowMethods: ["GET", "POST"]
    allowHeaders: ["x-model-version"]
```
### Step 4: Verify the integration
1. Test the inference endpoint:
   ```sh
   curl -v https://inference.example.com/v1/models/iris-classifier/predict \
     -H "Host: inference.example.com" \
     -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
   ```
2. Check gateway status:
   ```sh
   kubectl get virtualservices -n kserve-system
   kubectl get routetables -n kserve-system
   ```

### Troubleshooting

### Common issues

| Symptom | Possible cause | Solution |
|---------|---------------|----------|
| 503 errors | KServe predictor not ready | Check pod status: `kubectl get pods -n ml-models` |
| 404 errors | Route misconfiguration | Verify routes: `kubectl get virtualservices -o yaml` |
| TLS handshake failures | Certificate issues | Check cert-manager logs |

### Diagnostic commands

```sh
# View proxy logs
kubectl logs -n kgateway-system -l app=kgateway-proxy

# Check applied configuration
kubectl get virtualservices, routetables -n kserve-system -o yaml
```

## Cleanup

1. Remove the VirtualService and RouteTable:
   ```sh
   kubectl delete virtualservice kserve-ingress -n kserve-system
   kubectl delete routetable model-routes -n kserve-system
   ```

2. Optional: Uninstall KServe components following the [KServe documentation](https://kserve.github.io/website/master/admin/serverless/install/).

