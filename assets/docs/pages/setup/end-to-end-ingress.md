---
title: End-to-End Ingress Setup
description: Step-by-step guide to configuring ingress using KGateway.
sidebar_position: 5
---

This guide demonstrates a step-by-step ingress setup with {{< reuse "/docs/snippets/kgateway.md" >}}. You will deploy a sample application, configure a Gateway with both HTTP and HTTPS listeners, and manage traffic with path-based routing, all within a single namespace.

## Architecture overview

In {{< reuse "/docs/snippets/kgateway.md" >}}, traffic enters your cluster through a **Gateway**. The Gateway uses **HTTPRoute** resources to determine which **Service** should receive the request based on rules like hostnames and paths.

```mermaid
flowchart LR
    A[Client] -->|http://example.com| B(Gateway: 80/443)
    B -->|Path: /get| C[httpbin Service: 8000]
```

## Before you begin

Ensure that you have:
1.  A Kubernetes cluster (e.g., [Kind](https://kind.sigs.k8s.io/), [GKE](https://cloud.google.com/kubernetes-engine), or [EKS](https://aws.amazon.com/eks/)).
2.  `kubectl` and `helm` installed.
3.  {{< reuse "/docs/snippets/kgateway.md" >}} installed. If you haven't installed it yet, follow the [installation guide]({{< link-hextra path="/install" >}}).

## Step 1: Deploy a sample app {#deploy-app}

We will use the **httpbin** application as our backend.

1.  Create the `httpbin` namespace and deploy the application.
    ```shell
    kubectl create ns httpbin
    kubectl apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway/refs/heads/{{< reuse "docs/versions/github-branch.md" >}}/examples/httpbin.yaml -n httpbin
    ```

2.  Verify the pods are running:
    ```shell
    kubectl get pods -n httpbin
    ```

## Step 2: Create a Gateway {#create-gateway}

The **Gateway** resource defines the entry point for traffic. In this guide, we deploy the Gateway in the same namespace as the application.

1.  Apply the Gateway with an HTTP listener on port 8080:
    ```yaml
    kubectl apply -f- <<EOF
    kind: Gateway
    apiVersion: gateway.networking.k8s.io/v1
    metadata:
      name: my-gateway
      namespace: httpbin
    spec:
      gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
      listeners:
      - protocol: HTTP
        port: 8080
        name: http
        allowedRoutes:
          namespaces:
            from: Same
    EOF
    ```

2.  Verify the Gateway status and get its address:
    ```shell
    kubectl get gateway my-gateway -n httpbin
    ```

## Step 3: Create an HTTPRoute {#create-route}

The **HTTPRoute** defines how traffic from the Gateway is routed to the `httpbin` service.

1.  Expose httpbin on the `example.com` domain:
    ```yaml
    kubectl apply -f- <<EOF
    apiVersion: gateway.networking.k8s.io/v1
    kind: HTTPRoute
    metadata:
      name: httpbin-route
      namespace: httpbin
    spec:
      parentRefs:
        - name: my-gateway
          namespace: httpbin
      hostnames:
        - "example.com"
      rules:
        - backendRefs:
            - name: httpbin
              port: 8000
    EOF
    ```

## Step 4: Verify Ingress {#verify-ingress}

Test your ingress configuration using either a LoadBalancer IP or local port-forwarding.

{{< tabs items="Cloud Provider (LoadBalancer),Local Testing (Port-forward)" tabTotal="2" >}}
{{% tab tabName="Cloud Provider (LoadBalancer)" %}}
Get your Gateway IP and send a request:
```bash
export GATEWAY_IP=$(kubectl get svc -n httpbin -l gateway.networking.k8s.io/gateway-name=my-gateway -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
curl -H "Host: example.com" http://$GATEWAY_IP:8080/get
```
{{% /tab %}}
{{% tab tabName="Local Testing (Port-forward)" %}}
1. Identify the service created for your Gateway:
   ```bash
   kubectl get svc -n httpbin -l gateway.networking.k8s.io/gateway-name=my-gateway
   ```
2. Port-forward the service using the retrieved service name (replace `<gateway-service-name>`):
   ```bash
   kubectl port-forward svc/<gateway-service-name> 8080:8080 -n httpbin &
   ```
3. Send a test request:
   ```bash
   curl -H "Host: example.com" http://localhost:8080/get
   ```
{{% /tab %}}
{{< /tabs >}}

## Step 5: Path-based routing {#path-routing}

Update your route to handle different URL paths. For example, you can handle `/status` separately.

1.  Update the HTTPRoute with multiple rules:
    ```yaml
    kubectl apply -f- <<EOF
    apiVersion: gateway.networking.k8s.io/v1
    kind: HTTPRoute
    metadata:
      name: httpbin-route
      namespace: httpbin
    spec:
      parentRefs:
        - name: my-gateway
          namespace: httpbin
      hostnames:
        - "example.com"
      rules:
        - matches:
          - path:
              type: PathPrefix
              value: /status
          backendRefs:
            - name: httpbin
              port: 8000
        - matches:
          - path:
              type: PathPrefix
              value: /
          backendRefs:
            - name: httpbin
              port: 8000
    EOF
    ```

    {{< callout type="tip" >}}Path-based routing is flexible. You can use `Exact`, `PathPrefix`, or `RegularExpression` match types. For more details, see [Request Matching]({{< link-hextra path="/traffic-management/match" >}}).{{< /callout >}}

## Step 6: Secure with TLS {#secure-tls}

To terminate HTTPS traffic at the Gateway, provide a TLS certificate via a Kubernetes Secret.

1.  **Create a TLS Secret**: Generate a self-signed certificate for testing.
    ```bash
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout tls.key -out tls.crt -subj "/CN=example.com"
    kubectl create secret tls example-tls-secret -n httpbin \
      --cert=tls.crt --key=tls.key
    ```

2.  **Update the Gateway with an HTTPS listener**:
    ```yaml
    kubectl apply -f- <<EOF
    kind: Gateway
    apiVersion: gateway.networking.k8s.io/v1
    metadata:
      name: my-gateway
      namespace: httpbin
    spec:
      gatewayClassName: {{< reuse "docs/snippets/gatewayclass.md" >}}
      listeners:
      - protocol: HTTP
        port: 8080
        name: http
        allowedRoutes:
          namespaces:
            from: Same
      - protocol: HTTPS
        port: 8443
        name: https
        tls:
          mode: Terminate
          certificateRefs:
            - name: example-tls-secret
        allowedRoutes:
          namespaces:
            from: Same
    EOF
    ```

3.  **Test HTTPS access**:
    ```bash
    # Cloud Provider
    curl -k -H "Host: example.com" https://$GATEWAY_IP:8443/get

    # Port-forward if using local testing
    # kubectl port-forward svc/<gateway-service-name> 8443:8443 -n httpbin
    # curl -k -H "Host: example.com" https://localhost:8443/get
    ```

## Next steps {#next-steps}

Explore more advanced topics to enhance your ingress setup:
*   **Production TLS**: Automate certificate management with [ExternalDNS and cert-manager]({{< link-hextra path="/integrations/external-dns-cert-manager" >}}).
*   **Advanced Routing**: Learn about [redirects]({{< link-hextra path="/traffic-management/redirect" >}}), [rewrites]({{< link-hextra path="/traffic-management/rewrite" >}}), and [weighted routing]({{< link-hextra path="/traffic-management/weighted-routes" >}}).
*   **Security**: Add [Rate Limiting]({{< link-hextra path="/security/ratelimit" >}}) or [External Authentication]({{< link-hextra path="/security/external-auth" >}}) to your Gateway.

## Troubleshooting {#troubleshooting}

If you encounter issues, check the status of your resources:
*   **Gateway Status**: `kubectl describe gateway my-gateway -n httpbin`. Look for the `Programmed` and `Accepted` conditions.
*   **HTTPRoute Status**: `kubectl describe httproute httpbin-route -n httpbin`. Ensure the parent reference is accepted.
*   **Control Plane Logs**: Check the logs of the {{< reuse "/docs/snippets/kgateway.md" >}} controller:
    ```shell
    kubectl logs -n {{< reuse "docs/snippets/namespace.md" >}} deployment/{{< reuse "/docs/snippets/helm-kgateway.md" >}}
    ```

## Cleanup {#cleanup}

Clean up the resources and locally generated files:

```shell
# Remove the namespace and all its resources
kubectl delete ns httpbin

# Remove local TLS files generated during the TLS step
rm -f tls.key tls.crt
```
